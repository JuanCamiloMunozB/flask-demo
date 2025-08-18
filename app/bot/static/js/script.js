// =========================
// Estado global
// =========================
let CURRENT_SESSION_ID = null;

// Deshabilitar enviar hasta que el usuario elija deporte
const sendBtn = document.getElementById("sendBtn");
const userInput = document.getElementById("userInput");
sendBtn.disabled = true;

// =========================
// Seleccionar deporte
// =========================
async function selectSport(sport) {
  try {
    // Ocultar botones de selección
    const sportButtons = document.getElementById("sportButtons");
    const soccerBtn = document.getElementById("soccerBtn");
    const basketBtn = document.getElementById("basketBtn");

    sportButtons.style.display = "none";
    soccerBtn.style.display = "none";
    basketBtn.style.display = "none";

    sendBtn.disabled = false;

    addMessage("user", sport === "soccer" ? "Quiero apostar en fútbol" : "Quiero apostar en basketball");

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

    // Guardar session_id creado en el backend
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

// =========================
// Enviar mensaje
// =========================
async function sendMessage() {
  const message = userInput.value.trim();
  if (message === "") return;

  addMessage("user", message);
  userInput.value = "";

  // Mostrar mensaje de carga
  const loadingMsg = addMessage("bot", "Procesando información...", true);

  try {
    const resp = await fetch("/bot/get_response", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message,
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
      sendBtn.disabled = true;
      document.getElementById("restartBtn").style.display = "inline-block";
      if (data.next_message) {
        addMessage("bot", data.next_message);
      }
    }

    // Por compatibilidad: si backend devuelve session_id, lo actualizamos
    if (data.session_id) {
      CURRENT_SESSION_ID = data.session_id;
    }

    // Refresca historial (updated_at cambió)
    await refreshHistory();
  } catch (err) {
    console.error(err);
    loadingMsg.textContent = "Error procesando la respuesta.";
  }
}

// Enviar mensaje con Enter
window.addEventListener("DOMContentLoaded", () => {
  userInput.focus();
  userInput.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
      event.preventDefault();
      sendMessage();
    }
  });

  // Carga historial al iniciar
  refreshHistory();
});

// =========================
// Historial
// =========================
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

    sessions.forEach((s) => {
      const li = document.createElement("li");
      li.className = "list-group-item list-group-item-action d-flex justify-content-between align-items-center";
      const title = s.title || "Conversación";
      const time = s.updated_at ? new Date(s.updated_at).toLocaleString() : "";

      li.innerHTML = `
        <span>
          <strong>${escapeHTML(title)}</strong>
          <small class="text-muted d-block">${s.sport ? escapeHTML(s.sport) : "-"}</small>
        </span>
        <span class="badge">${time}</span>
      `;
      li.style.cursor = "pointer";
      li.onclick = () => loadSession(s.id);
      ul.appendChild(li);
    });
  } catch (e) {
    console.error("Error cargando historial:", e);
  }
}

async function loadSession(sessionId) {
  try {
    const resp = await fetch(`/bot/history/${sessionId}`);
    const data = await resp.json();
    if (!resp.ok) {
      alert(data.error || "No se pudo cargar la sesión");
      return;
    }

    CURRENT_SESSION_ID = data.session.id;

    // Reemplazar contenido del chat por el historial de esa sesión
    clearChat();

    const messages = data.messages || [];
    messages.forEach((m) => {
      if (m.role === "user") addMessage("user", m.content);
      else addMessage("bot", m.content);
    });

    // Al cargar una sesión, ocultamos los botones de deporte y permitimos enviar
    document.getElementById("sportButtons").style.display = "none";
    document.getElementById("soccerBtn").style.display = "none";
    document.getElementById("basketBtn").style.display = "none";
    sendBtn.disabled = false;
    document.getElementById("restartBtn").style.display = "inline-block";

    // Cierra el drawer si estaba abierto
    const offcanvasEl = document.getElementById("historyDrawer");
    const oc = bootstrap.Offcanvas.getInstance(offcanvasEl);
    if (oc) oc.hide();
  } catch (e) {
    console.error("Error cargando sesión:", e);
  }
}

// =========================
/* Utilidades de UI */
// =========================
function addMessage(sender, text, isLoading = false) {
  const chat = document.getElementById("chat");
  const msgDiv = document.createElement("div");
  msgDiv.className = `message ${sender}`;

  if (isLoading) {
    msgDiv.innerHTML = '<span class="spinner"></span> ' + text;
  } else {
    msgDiv.innerHTML = (text || "").replace(/\n/g, "<br>");
  }

  chat.appendChild(msgDiv);
  chat.scrollTop = chat.scrollHeight;
  return msgDiv;
}

function clearChat() {
  const chat = document.getElementById("chat");
  chat.innerHTML = `
    <div class="message bot">
      <i class="fas fa-robot me-2 icon-custom"></i>
      Hola. ¿Sobre qué deporte quieres apostar hoy?
    </div>
  `;
}

function escapeHTML(str) {
  return (str || "").replace(/[&<>"']/g, (s) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[s]));
}

// =========================
// Nueva conversación
// =========================
function restartConversation() {
  // Limpiar el chat
  clearChat();

  // Restaurar botones y entrada
  document.getElementById("sportButtons").style.display = "flex";
  document.getElementById("soccerBtn").style.display = "inline-block";
  document.getElementById("basketBtn").style.display = "inline-block";
  document.getElementById("restartBtn").style.display = "none";

  // Deshabilitar enviar hasta que elijan deporte
  sendBtn.disabled = true;

  // Limpiar input y sesión actual
  userInput.value = "";
  CURRENT_SESSION_ID = null;
}
