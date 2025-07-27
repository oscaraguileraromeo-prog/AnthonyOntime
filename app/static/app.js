function addTrayecto() {
    const div = document.createElement('div');
    div.className = 'trayecto';
    div.innerHTML = `
        <label>Hora salida</label><input type="time" name="t_hora_salida" required>
        <label>Origen</label><input type="text" name="t_origen" required>
        <label>Hora llegada</label><input type="time" name="t_hora_llegada" required>
        <label>Destino</label><input type="text" name="t_destino" required>
        <button type="button" onclick="this.parentNode.remove()">Eliminar</button>
        <hr>`;
    document.getElementById('trayectos').appendChild(div);
}
addTrayecto();

// Modal configuración
const modal = document.getElementById('configModal');
function openModal(){modal.style.display='block'; loadModels();}
function closeModal(){modal.style.display='none';}

function saveConfig(){
    localStorage.setItem('apiKey', document.getElementById('apiKey').value);
    localStorage.setItem('model', document.getElementById('modelSelect').value);
    checkAssistant();
    closeModal();
}

function loadModels(){
    const key = localStorage.getItem('apiKey');
    fetch('https://openrouter.ai/api/v1/models', {headers:{'Authorization': 'Bearer ' + key}})
      .then(r=>r.json())
      .then(data=>{
        const select = document.getElementById('modelSelect');
        select.innerHTML='';
        data.data.filter(m=>!m.id.includes('paid')).forEach(m=>{
            const opt=document.createElement('option');
            opt.value=m.id; opt.textContent=m.id; select.appendChild(opt);});
        select.value=localStorage.getItem('model')||'';
        document.getElementById('apiKey').value=key||'';
      });
}

function checkAssistant(){
    const key=localStorage.getItem('apiKey');
    const model=localStorage.getItem('model');
    document.getElementById('voiceBtn').style.display = key&&model ? 'block':'none';
}

checkAssistant();

// Placeholder para integración de voz (reconocimiento/síntesis del navegador)
