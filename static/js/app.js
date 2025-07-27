// Funciones de UI para añadir trayectos
const trayectosDiv = document.getElementById('trayectos');
document.getElementById('add-trayecto').addEventListener('click', () => {
    const div = document.createElement('div');
    div.className = 'trayecto';
    div.innerHTML = `
        <label>Salida: <input type="time" name="hora_salida[]" required></label>
        <label>Origen: <input type="text" name="origen[]" required></label>
        <label>Llegada: <input type="time" name="hora_llegada[]" required></label>
        <label>Destino: <input type="text" name="destino[]" required></label>
        <button type="button" class="del">Eliminar</button>
    `;
    div.querySelector('.del').addEventListener('click', () => div.remove());
    trayectosDiv.appendChild(div);
});

// Envío de formulario
const form = document.getElementById('jornada-form');
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const datos = new FormData(form);
    const res = await fetch('/api/jornadas', {
        method: 'POST',
        body: datos
    });
    if(res.ok) {
        alert('Guardado');
        form.reset();
        trayectosDiv.innerHTML = '';
    } else {
        alert('Error al guardar');
    }
});

if('serviceWorker' in navigator){
    navigator.serviceWorker.register('/sw.js');
}
