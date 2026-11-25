const nombre = document.getElementById("nombre");

nombre.addEventListener("input", function () {
    if (nombre.value.trim() === "") {
        nombre.setCustomValidity("Ingresa el nombre de la tarea");
    } else {
        nombre.setCustomValidity("");
    }
});
