const API_URL = 'http://127.0.0.1:5000/chat';  //URL backend Flask

const chatBox = document.getElementById('chatBox')
const userInput = document.getElementById('userInput')
const sendBtn = document.getElementById('sendBtn')

userInput.addEventListener('keydown', (e) => {   //Permite enviar mensaje al presionar tecla Enter
    if (e.key === 'Enter' && !sendBtn.disabled) enviarMensaje();
});

function agregarMensaje(texto, tipo) {
    const div = document.createElement('div');
    div.className = `message ${tipo}`.trim();   //className: soporta varias clases separadas por espacio
    div.textContent = texto;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
    return div
}

async function enviarMensaje() {
    const texto = userInput.value.trim();
    if (!texto) return;

    agregarMensaje(texto, 'user-message');
    userInput.value = '';
    sendBtn.disabled = true;

    const indicador = agregarMensaje('Escribiendo....', 'bot-message');

    try{
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: texto })
        });

        if (!response.ok) {
            throw new Error(`El servidor respondió con estado ${response.status}`);
        }

        const data = await response.json();

        indicador.remove()
        const claseExtra = data.intencion === 'fallback' ? 'fallback' : '';
        const textoFinal = data.respuesta && data.respuesta.trim()
            ? data.respuesta
            : 'No entendí tu consulta. ¿Podés reformularla o intentarlo de nuevo?';
        agregarMensaje(textoFinal, `bot-message ${claseExtra}`.trim());

    } catch(error){
        indicador.remove()
        agregarMensaje(
            'No pude conectarme con el servidor. Verificá que el backend esté corriendo.', 
            'bot-message fallback'
        )
        console.error('Error al consultar la API:', error)

    } finally {
        sendBtn.disabled = false
        userInput.focus()
    }
}