document.getElementById("sendBtn").disabled = true;

// Seleccionar deporte y obtener la primera pregunta
function selectSport(sport) {
    // Ocultar botones de selección
    document.getElementById("sportButtons").style.display = "none";
    document.getElementById("soccerBtn").style.display = "none";
    document.getElementById("basketBtn").style.display = "none";

    document.getElementById("sendBtn").disabled = false;
    addMessage("user", sport === 'soccer' ? "Quiero apostar en fútbol" : "Quiero apostar en basketball");

    fetch("/bot/select_sport", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sport: sport })
    })
    .then(response => response.json())
    .then(data => {
        addMessage("bot", data.message);
        if (data.next_message) {
            addMessage("bot", data.next_message)
        }
    });
}

document.getElementById("userInput").focus();

// Enviar respuesta del usuario al sistema experto
function sendMessage() {
    const input = document.getElementById("userInput");
    const message = input.value.trim();
    if (message === "") return;

    addMessage("user", message);
    input.value = "";

    // Mostrar mensaje de carga
    const loadingMsg = addMessage("bot", "Procesando información...", true);

    fetch("/bot/get_response", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: message })
    })
    .then(response => response.json())
    .then(data => {
        // Reemplazar el mensaje de carga con la respuesta real
        loadingMsg.textContent = data.message;

        if (data.finished) {
            document.getElementById("sendBtn").disabled = true;
            document.getElementById("restartBtn").style.display = "inline-block";
            if (data.next_message) {
                addMessage("bot", data.next_message);
            }
        }
    });
}

// Enviar mensaje rápido desde botones
function sendQuickMessage(text) {
    document.getElementById("userInput").value = text;
    sendMessage();
}

// Agregar mensajes al chat
function addMessage(sender, text, isLoading = false) {
    const chat = document.getElementById("chat");
    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${sender}`;

    if (isLoading) {
        msgDiv.innerHTML = '<span class="spinner"></span> ' + text;
    } else {
        msgDiv.innerHTML = text.replace(/\n/g, "<br>");
    }

    chat.appendChild(msgDiv);
    chat.scrollTop = chat.scrollHeight;
    return msgDiv; 
}

// Focus input and allow Enter key to submit
window.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("userInput");
    input.focus();
    input.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            sendMessage();
        }
    });
});


function restartConversation() {
    // Limpiar el chat
    const chat = document.getElementById("chat");
    chat.innerHTML = '<div class="message bot">Hola ¿Sobre qué deporte quieres apostar hoy?</div>';

    // Restaurar botones y entrada
    document.getElementById("sportButtons").style.display = "flex";
    document.getElementById("soccerBtn").style.display = "inline-block";
    document.getElementById("basketBtn").style.display = "inline-block";
    document.getElementById("restartBtn").style.display = "none";

    // Limpiar campos
    document.getElementById("userInput").value = "";
}


