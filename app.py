from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from pathlib import Path

app = Flask(__name__)

DATABASE = Path(__file__).with_name("tareas.db")


def conectar_bd():
    conexion = sqlite3.connect(DATABASE)
    conexion.row_factory = sqlite3.Row
    return conexion


def inicializar_bd():
    conexion = conectar_bd()

    conexion.execute("""
        CREATE TABLE IF NOT EXISTS tareas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            estado TEXT NOT NULL DEFAULT 'Pendiente',
            prioridad TEXT NOT NULL
        )
    """)

    conexion.commit()
    conexion.close()


@app.route("/")
def index():
    conexion = conectar_bd()

    tareas = conexion.execute(
        "SELECT * FROM tareas ORDER BY id DESC"
    ).fetchall()

    conexion.close()

    return render_template(
        "index.html",
        tareas=tareas,
        mensaje=request.args.get("mensaje", "")
    )


@app.route("/registrar", methods=["POST"])
def registrar():
    nombre = request.form.get("nombre", "").strip()
    descripcion = request.form.get("descripcion", "").strip()
    prioridad = request.form.get("prioridad", "")

    if not nombre:
        return redirect(url_for(
            "index", mensaje="El nombre es obligatorio"
        ))

    if prioridad not in ["Alta", "Media", "Baja"]:
        return redirect(url_for(
            "index", mensaje="Prioridad no válida"
        ))

    conexion = conectar_bd()

    conexion.execute("""
        INSERT INTO tareas (nombre, descripcion, estado, prioridad)
        VALUES (?, ?, ?, ?)
    """, (nombre, descripcion, "Pendiente", prioridad))

    conexion.commit()
    conexion.close()

    return redirect(url_for(
        "index", mensaje="Tarea registrada correctamente"
    ))


inicializar_bd()

if __name__ == "__main__":
    app.run()
