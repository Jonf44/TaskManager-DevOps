import pytest
import app as sistema


@pytest.fixture
def cliente(tmp_path, monkeypatch):
    monkeypatch.setattr(
        sistema, "DATABASE", tmp_path / "pruebas.db"
    )

    sistema.inicializar_bd()
    sistema.app.config["TESTING"] = True

    return sistema.app.test_client()


def registrar_tarea(cliente, prioridad="Alta"):
    return cliente.post("/registrar", data={
        "nombre": "Realizar actividad DevOps",
        "descripcion": "Actividad de prueba",
        "prioridad": prioridad
    }, follow_redirects=True)


def consultar_tareas():
    conexion = sistema.conectar_bd()

    tareas = conexion.execute(
        "SELECT * FROM tareas"
    ).fetchall()

    conexion.close()

    return tareas


def test_registro_tarea(cliente):
    respuesta = registrar_tarea(cliente)

    assert respuesta.status_code == 200

    tareas = consultar_tareas()

    assert len(tareas) == 1
    assert tareas[0]["nombre"] == "Realizar actividad DevOps"
    assert tareas[0]["estado"] == "Pendiente"


def test_registro_sin_nombre(cliente):
    respuesta = cliente.post("/registrar", data={
        "nombre": "",
        "descripcion": "Actividad de prueba",
        "prioridad": "Alta"
    }, follow_redirects=True)

    assert "El nombre es obligatorio" in respuesta.get_data(as_text=True)
    assert len(consultar_tareas()) == 0


def test_consultar_tareas(cliente):
    registrar_tarea(cliente)

    respuesta = cliente.get("/")

    assert respuesta.status_code == 200
    assert "Realizar actividad DevOps" in respuesta.get_data(as_text=True)


def test_editar_tarea(cliente):
    registrar_tarea(cliente)
    tarea = consultar_tareas()[0]

    cliente.post(f"/editar/{tarea['id']}", data={
        "nombre": "Actividad actualizada",
        "descripcion": "Descripcion actualizada",
        "prioridad": "Media",
        "estado": "Pendiente"
    }, follow_redirects=True)

    tarea = consultar_tareas()[0]

    assert tarea["nombre"] == "Actividad actualizada"
    assert tarea["descripcion"] == "Descripcion actualizada"
    assert tarea["prioridad"] == "Media"


def test_eliminar_tarea(cliente):
    registrar_tarea(cliente)
    tarea = consultar_tareas()[0]

    cliente.post(
        f"/eliminar/{tarea['id']}",
        follow_redirects=True
    )

    assert len(consultar_tareas()) == 0


def test_cambiar_estado(cliente):
    registrar_tarea(cliente)
    tarea = consultar_tareas()[0]

    for estado in ["En proceso", "Terminada", "Pendiente"]:
        cliente.post(f"/editar/{tarea['id']}", data={
            "nombre": tarea["nombre"],
            "descripcion": tarea["descripcion"],
            "prioridad": tarea["prioridad"],
            "estado": estado
        }, follow_redirects=True)

        assert consultar_tareas()[0]["estado"] == estado


def test_asignar_prioridad(cliente):
    for prioridad in ["Alta", "Media", "Baja"]:
        registrar_tarea(cliente, prioridad)

    prioridades = [
        tarea["prioridad"]
        for tarea in consultar_tareas()
    ]

    assert prioridades == ["Alta", "Media", "Baja"]
