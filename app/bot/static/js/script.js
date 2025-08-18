// Estado global
let CURRENT_SESSION_ID = null;

// Deshabilitar enviar hasta que el usuario elija deporte
document.getElementById("sendBtn").disabled = true;

// Seleccionar deporte y obtener la primera pregunta
async function selectSport(sport) {
  try {
    // Ocultar botones de selección
    const sportButtons = document.getElementById("sportButtons");
    const soccerBtn = document.getElementById("soccerBtn");
    const basketBtn = document.getElementById("basketBtn");

    sportButtons.style.display = "none";
    soccerBtn.style.display = "none";
    basketBtn.style.display = "none";

    document.getElementById("sendBtn").disabled = false;

    addMessage("user", sport === 'soccer' ? "Quiero apostar en fútbol" : "Quiero apostar en basketball");

    const resp = await fetch("/bot/select_sport", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sport })
    });
    const data = await resp.json();

    if (!resp.ok) {
      addMessage("bot", data.error || "No se pudo iniciar la conversación.");
      return;
    }

    // Guardamos el session_id que crea el backend
    CURRENT_SESSION_ID = data.session_id || null;

    addMessage("bot", data.message);
    if (data.next_message) {
      addMessage("bot", data.next_message);
    }

    // Refresca historial
    await refreshHistory();
  } catch (err) {
    console.error(err);
    addMessage("bot", "Ocurrió un error al iniciar la sesión.");
  }
}

document.getElementById("userInput").focus();

// Enviar respuesta del usuario al sistema experto
async function sendMessage() {
  const input = document.getElementById("userInput");
  const message = input.value.trim();
  if (message === "") return;

  addMessage("user", message);
  input.value = "";

  // Mostrar mensaje de carga
  const loadingMsg = addMessage("bot", "Procesando información...", true);

  try {
    const resp = await fetch("/bot/get_response", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: message,
        session_id: CURRENT_SESSION_ID // MUY IMPORTANTE
      })
    });

    const data = await resp.json();

    if (!resp.ok) {
      loadingMsg.textContent = data.error || "No se pudo obtener respuesta.";
      return;
    }

    // Reemplazar el mensaje de carga con la respuesta real
    loadingMsg.textContent = data.message;

    if (data.finished) {
      document.getElementById("sendBtn").disabled = true;
      document.getElementById("restartBtn").style.display = "inline-block";
      if (data.next_message) {
        addMessage("bot", data.next_message);
      }
    }

    // Actualiza session_id si el backend lo envía (por compat)
    if (data.session_id) {
      CURRENT_SESSION_ID = data.session_id;
    }

    // Refresca historial (por la actualización de updated_at)
    await refreshHistory();
  } catch (err) {
    console.error(err);
    loadingMsg.textContent = "Error procesando la respuesta.";
  }
}

// Enviar mensaje rápido desde botones (si más adelante agregas quick replies)
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

// Cargar historial de sesiones
async function refreshHistory() {
  try {
    const resp = await fetch("/bot/history");
    if (!resp.ok) return;
    const sessions = await resp.json();

    const ul = document.getElementById("historyList");
    ul.innerHTML = "";

    if (!Array.isArray(sessions) || sessions.length === 0) {
      const li = document.createElement("li");
      li.className = "list-group-item";
      li.textContent = "No hay conversaciones aún.";
      ul.appendChild(li);
      return;
    }

    sessions.forEach(s => {
      const li = document.createElement("li");
      li.className = "list-group-item list-group-item-action d-flex justify-content-between align-items-center";
      const title = s.title || "Conversación";
      const time = s.updated_at ? new Date(s.updated_at).toLocaleString() : "";
      li.innerHTML = `
        <span>
          <strong>${escapeHTML(title)}</strong>
          <small class="text-muted d-block">${s.sport ? escapeHTML(s.sport) : "-"}</small>
        </span>
        <span class="badge bg-secondary">${time}</span>
      `;
      li.style.cursor = "pointer";
      li.onclick = () => loadSession(s.id);
      ul.appendChild(li);
    });
  } catch (e) {
    console.error("Error cargando historial:", e);
  }
}

// Cargar una sesión (reemplaza la conversación en pantalla)
async function loadSession(sessionId) {
  try {
    const resp = await fetch(`/bot/history/${sessionId}`);
    const data = await resp.json();
    if (!resp.ok) {
      alert(data.error || "No se pudo cargar la sesión");
      return;
    }

    CURRENT_SESSION_ID = data.session.id;

    // Reemplaza contenido del chat por el historial de esa sesión
    clearChat();

    const messages = data.messages || [];
    messages.forEach(m => {
      if (m.role === "user") addMessage("user", m.content);
      else addMessage("bot", m.content);
    });

    // Al cargar una sesión, ocultamos los botones de deporte y permitimos enviar
    document.getElementById("sportButtons").style.display = "none";
    document.getElementById("soccerBtn").style.display = "none";
    document.getElementById("basketBtn").style.display = "none";
    document.getElementById("sendBtn").disabled = false;
    document.getElementById("restartBtn").style.display = "inline-block";

    // Cierra el drawer si estaba abierto
    const offcanvasEl = document.getElementById('historyDrawer');
    const oc = bootstrap.Offcanvas.getInstance(offcanvasEl);
    if (oc) oc.hide();
  } catch (e) {
    console.error("Error cargando sesión:", e);
  }
}

function clearChat() {
  const chat = document.getElementById("chat");
  chat.innerHTML = '';
}

// Utilidad simple para evitar XSS en títulos/sports
function escapeHTML(str) {
  return (str || "").replace(/[&<>"']/g, s => (
    { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[s]
  ));
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

  // Carga historial al iniciar
  refreshHistory();
});

function restartConversation() {
  // Limpiar el chat
  const chat = document.getElementById("chat");
  chat.innerHTML = `
    <div class="message bot">
      <i class="fas fa-robot me-2 icon-custom"></i>
      Hola. ¿Sobre qué deporte quieres apostar hoy?
    </div>
  `;

  // Restaurar botones y entrada
  document.getElementById("sportButtons").style.display = "flex";
  document.getElementById("soccerBtn").style.display = "inline-block";
  document.getElementById("basketBtn").style.display = "inline-block";
  document.getElementById("restartBtn").style.display = "none";

  // Deshabilitar enviar hasta que elijan deporte
  document.getElementById("sendBtn").disabled = true;

  // Limpiar input y sesión actual
  document.getElementById("userInput").value = "";
  CURRENT_SESSION_ID = null;
}
