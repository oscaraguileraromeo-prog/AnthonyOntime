// Configuración guardada en LocalStorage
function getConfig(){
    return JSON.parse(localStorage.getItem('vozConf')||'{}');
}
function setConfig(cfg){
    localStorage.setItem('vozConf', JSON.stringify(cfg));
}

// Cargar modelos de openrouter (solo gratuitos)
async function cargarModelos(select){
    const cfg = getConfig();
    if(!cfg.api) return;
    try{
        const res = await fetch('https://openrouter.ai/api/v1/models', {
            headers:{'Authorization':'Bearer '+cfg.api}
        });
        const data = await res.json();
        select.innerHTML = '';
        data.data.filter(m=>m.id && m.id.includes('free')).forEach(m=>{
            const opt=document.createElement('option');
            opt.value=m.id; opt.textContent=m.id;
            select.appendChild(opt);
        });
    }catch(e){console.error(e);}
}

// Modal de configuración
function showConfig(){
    const modal=document.createElement('div');
    modal.className='modal';
    modal.innerHTML=`
        <div class="modal-content">
            <label>API Key:<input type="text" id="apiKey"></label>
            <p><a href="https://openrouter.ai" target="_blank">Obtener API gratuita</a></p>
            <label>Modelo:<select id="modelo"></select></label>
            <button id="guardar">Guardar</button>
        </div>`;
    document.body.appendChild(modal);
    const cfg=getConfig();
    document.getElementById('apiKey').value=cfg.api||'';
    cargarModelos(document.getElementById('modelo')).then(()=>{
        document.getElementById('modelo').value=cfg.modelo||'';
    });
    document.getElementById('guardar').onclick=()=>{
        setConfig({api:document.getElementById('apiKey').value, modelo:document.getElementById('modelo').value});
        modal.remove();
    };
}

document.getElementById('btn-config').addEventListener('click', showConfig);

function checkConfig(){
    const cfg=getConfig();
    if(cfg.api && cfg.modelo){
        document.getElementById('btn-voice').style.display='block';
    }
}

checkConfig();

let recognizer, synthesis;
if('webkitSpeechRecognition' in window){
    recognizer = new webkitSpeechRecognition();
    recognizer.lang='es-ES';
}
if('speechSynthesis' in window){
    synthesis = window.speechSynthesis;
}

async function preguntar(text){
    const cfg=getConfig();
    if(!cfg.api||!cfg.modelo)return;
    const res=await fetch('https://openrouter.ai/api/v1/chat/completions',{
        method:'POST',
        headers:{'Content-Type':'application/json','Authorization':'Bearer '+cfg.api},
        body:JSON.stringify({model:cfg.modelo,messages:[{role:'system',content:'Eres un asistente para Antonio Becerra Ortega.'},{role:'user',content:text}]})
    });
    const data=await res.json();
    const respuesta=data.choices[0].message.content;
    if(synthesis){
        const utter=new SpeechSynthesisUtterance(respuesta);
        synthesis.speak(utter);
    }
}

document.getElementById('btn-voice').onclick=()=>{
    if(!recognizer){alert('Reconocimiento de voz no disponible');return;}
    recognizer.start();
};

if(recognizer){
    recognizer.onresult=(e)=>{
        const text=e.results[0][0].transcript;
        preguntar(text);
    };
}
