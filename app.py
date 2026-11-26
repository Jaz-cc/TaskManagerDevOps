
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "taskmanager_clave_local"

DATABASE = "taskmanager.db"


def conectar_bd():
    conexion = sqlite3.connect(DATABASE)
    conexion.row_factory = sqlite3.Row
    return conexion


def crear_tabla():
    conexion = conectar_bd()

    conexion.execute("""
        CREATE TABLE IF NOT EXISTS tareas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            prioridad TEXT NOT NULL,
            estado TEXT NOT NULL DEFAULT 'Pendiente'
        )
    """)

    conexion.commit()
    conexion.close()



@app.route("/")
def inicio():
    conexion = conectar_bd()
    tareas = conexion.execute(
        "SELECT * FROM tareas ORDER BY id DESC"
    ).fetchall()
    conexion.close()

    return render_template("index.html", tareas=tareas)



@app.route("/registrar", methods=["POST"])
def registrar():
    nombre = request.form.get("nombre", "").strip()
    descripcion = request.form.get("descripcion", "").strip()
    prioridad = request.form.get("prioridad", "")

    if not nombre or prioridad not in ["Alta", "Media", "Baja"]:
        flash("Ingresa un nombre y una prioridad válida.")
        return redirect(url_for("inicio"))

    conexion = conectar_bd()

    conexion.execute("""
        INSERT INTO tareas (nombre, descripcion, prioridad)
        VALUES (?, ?, ?)
    """, (nombre, descripcion, prioridad))

    conexion.commit()
    conexion.close()

    flash("¡Tarea registrada correctamente!")
    return redirect(url_for("inicio"))


if __name__ == "__main__":
    crear_tabla()
    app.run(debug=True)
