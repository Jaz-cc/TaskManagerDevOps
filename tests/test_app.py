import pytest
import app as taskmanager


# ==========================================
# CONFIGURACION DEL ENTORNO DE PRUEBAS
# ==========================================
@pytest.fixture
def cliente(tmp_path, monkeypatch):

    # Crear una base de datos temporal
    base_datos = tmp_path / "test_taskmanager.db"

    # Sustituir temporalmente la base de datos original
    monkeypatch.setattr(
        taskmanager,
        "DATABASE",
        str(base_datos)
    )

    monkeypatch.setitem(
        taskmanager.app.config,
        "TESTING",
        True
    )

    # Crear la tabla en la base de datos temporal
    taskmanager.crear_tabla()

    # Crear el cliente de pruebas de Flask
    with taskmanager.app.test_client() as cliente:
        yield cliente


# ==========================================
# FUNCIONES AUXILIARES
# ==========================================

def obtener_tareas():
    conexion = taskmanager.conectar_bd()

    tareas = conexion.execute(
        "SELECT * FROM tareas ORDER BY id"
    ).fetchall()

    conexion.close()

    return tareas


def registrar_tarea_prueba(cliente):

    respuesta = cliente.post(
        "/registrar",
        data={
            "nombre": "Actividad DevOps",
            "descripcion": "Tarea para pruebas",
            "prioridad": "Alta"
        }
    )

    assert respuesta.status_code == 302

    tareas = obtener_tareas()

    assert len(tareas) == 1

    return tareas[0]["id"]


# ==========================================
# PU01 - REGISTRAR TAREA
# ==========================================

def test_registro_tarea(cliente):

    respuesta = cliente.post(
        "/registrar",
        data={
            "nombre": "Realizar actividad DevOps",
            "descripcion": "Implementar CI",
            "prioridad": "Alta"
        }
    )

    assert respuesta.status_code == 302

    tareas = obtener_tareas()

    assert len(tareas) == 1

    assert tareas[0]["nombre"] == "Realizar actividad DevOps"
    assert tareas[0]["descripcion"] == "Implementar CI"
    assert tareas[0]["prioridad"] == "Alta"
    assert tareas[0]["estado"] == "Pendiente"


# ==========================================
# PU02 - CONSULTAR TAREAS
# ==========================================

def test_consultar_tareas(cliente):

    registrar_tarea_prueba(cliente)

    respuesta = cliente.get("/")

    assert respuesta.status_code == 200

    contenido = respuesta.get_data(as_text=True)

    assert "Actividad DevOps" in contenido


# ==========================================
# PU03 - EDITAR TAREA
# ==========================================

def test_editar_tarea(cliente):

    id_tarea = registrar_tarea_prueba(cliente)

    respuesta = cliente.post(
        f"/editar/{id_tarea}",
        data={
            "nombre": "Actividad actualizada",
            "descripcion": "Descripcion modificada",
            "prioridad": "Media"
        }
    )

    assert respuesta.status_code == 302

    tareas = obtener_tareas()

    assert len(tareas) == 1
    assert tareas[0]["id"] == id_tarea
    assert tareas[0]["nombre"] == "Actividad actualizada"
    assert tareas[0]["descripcion"] == "Descripcion modificada"
    assert tareas[0]["prioridad"] == "Media"
    assert tareas[0]["estado"] == "Pendiente"


# ==========================================
# PU04 - ELIMINAR TAREA
# ==========================================

def test_eliminar_tarea(cliente):

    id_tarea = registrar_tarea_prueba(cliente)

    respuesta = cliente.post(
        f"/eliminar/{id_tarea}"
    )

    assert respuesta.status_code == 302

    tareas = obtener_tareas()

    assert len(tareas) == 0


# ==========================================
# PU05 - CAMBIAR ESTADO
# ==========================================

def test_cambiar_estado(cliente):

    id_tarea = registrar_tarea_prueba(cliente)

    estados = [
        "En proceso",
        "Terminada",
        "Pendiente"
    ]

    for estado in estados:

        respuesta = cliente.post(
            f"/cambiar-estado/{id_tarea}",
            data={
                "estado": estado
            }
        )

        assert respuesta.status_code == 302

        tareas = obtener_tareas()

        assert tareas[0]["estado"] == estado


# ==========================================
# PU06 - ASIGNAR PRIORIDAD
# ==========================================

def test_asignar_prioridad(cliente):

    id_tarea = registrar_tarea_prueba(cliente)

    prioridades = [
        "Media",
        "Baja",
        "Alta"
    ]

    for prioridad in prioridades:

        respuesta = cliente.post(
            f"/cambiar-prioridad/{id_tarea}",
            data={
                "prioridad": prioridad
            }
        )

        assert respuesta.status_code == 302

        tareas = obtener_tareas()

        assert tareas[0]["prioridad"] == prioridad


# ==========================================
# PU07 - REGISTRAR TAREA SIN NOMBRE
# ==========================================

def test_registro_sin_nombre(cliente):

    respuesta = cliente.post(
        "/registrar",
        data={
            "nombre": "",
            "descripcion": "Tarea sin nombre",
            "prioridad": "Alta"
        }
    )

    assert respuesta.status_code == 302

    tareas = obtener_tareas()

    # La tarea no debe guardarse
    assert len(tareas) == 0

    # Verificar el mensaje de validacion
    with cliente.session_transaction() as sesion:

        mensajes = sesion.get("_flashes", [])

        assert any(
            "Ingresa un nombre y una prioridad válida." in mensaje
            for categoria, mensaje in mensajes
        )
