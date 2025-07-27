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

// Cálculo de horas totales del turno
function calcularHoras(){
    const hi=document.querySelector('[name=hora_inicio]').value;
    const hf=document.querySelector('[name=hora_fin]').value;
    if(hi && hf){
        const d1=new Date('1970-01-01T'+hi+':00');
        const d2=new Date('1970-01-01T'+hf+':00');
        let diff=(d2-d1)/3600000;
        if(diff<0) diff+=24;
        document.getElementById('horasTotales').textContent=diff.toFixed(2);
    }
}

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

// Integración básica de asistente por voz
let history=[];
const voiceBtn=document.getElementById('voiceBtn');
if(voiceBtn){
    voiceBtn.addEventListener('click', iniciarAsistente);
}

function iniciarAsistente(){
    history=[];
    hablar('Hola Antonio, ¿en qué puedo ayudarte?');
    escuchar();
}

function escuchar(){
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if(!SpeechRecognition){
        const texto=prompt('Escribe tu consulta:');
        if(texto) enviar(texto);
        return;
    }
    const rec=new SpeechRecognition();
    rec.lang='es-ES';
    rec.onresult=e=>{const txt=e.results[0][0].transcript; enviar(txt);};
    rec.start();
}

function hablar(texto){
    const u=new SpeechSynthesisUtterance(texto);u.lang='es-ES';speechSynthesis.speak(u);
}

function enviar(texto){
    history.push({role:'user', content:texto});
    fetch('/assistant',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({messages:history,key:localStorage.getItem('apiKey'),model:localStorage.getItem('model')})})
      .then(r=>r.json()).then(data=>{
        const resp=data.choices[0].message.content;
        history.push({role:'assistant',content:resp});
        hablar(resp);
        // escucha de nuevo tras respuesta
        setTimeout(escuchar,500);
      });
}
