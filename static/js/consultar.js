async function cargar(desde='', hasta=''){
    const params = new URLSearchParams();
    if(desde) params.append('desde', desde);
    if(hasta) params.append('hasta', hasta);
    const res = await fetch('/api/jornadas?'+params.toString());
    const data = await res.json();
    const tbody = document.querySelector('#tabla-jornadas tbody');
    tbody.innerHTML = '';
    data.forEach(j => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${j.fecha}</td><td>${j.hora_inicio}</td><td>${j.hora_fin}</td><td>${j.matricula}</td><td><a href="/api/jornadas/${j.id}/pdf" target="_blank">PDF</a></td>`;
        tbody.appendChild(tr);
    });
}

document.getElementById('filtro').addEventListener('submit', e => {
    e.preventDefault();
    const desde = e.target.desde.value;
    const hasta = e.target.hasta.value;
    cargar(desde, hasta);
});

cargar();
