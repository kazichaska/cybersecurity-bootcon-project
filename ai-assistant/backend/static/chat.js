const statusEl = document.getElementById("status");
const modesEl = document.getElementById("modes");
const transcriptEl = document.getElementById("transcript");
const formEl = document.getElementById("chat-form");
const messageEl = document.getElementById("message");
const contextControls = document.getElementById("context-controls");
const containerField = document.getElementById("container-field");
const containerSelect = document.getElementById("container-select");
const trackField = document.getElementById("track-field");
const trackSelect = document.getElementById("track-select");

let mode = "freeform";
const history = [];

function setStatus(text, cls) {
  statusEl.textContent = text;
  statusEl.className = `status ${cls || ""}`.trim();
}

async function checkHealth() {
  try {
    const res = await fetch("/api/health");
    const data = await res.json();
    if (data.ok) {
      setStatus(`connected (${data.provider})`, "ok");
    } else {
      setStatus(data.error || "backend unavailable", "error");
    }
  } catch {
    setStatus("backend unreachable", "error");
  }
}

async function loadContainers() {
  try {
    const res = await fetch("/api/containers");
    const data = await res.json();
    containerSelect.innerHTML = "";
    for (const name of data.containers || []) {
      const opt = document.createElement("option");
      opt.value = name;
      opt.textContent = name;
      containerSelect.appendChild(opt);
    }
  } catch {
    /* leave empty; chat call will surface the error */
  }
}

async function loadTracks() {
  try {
    const res = await fetch("/api/tracks");
    const data = await res.json();
    trackSelect.innerHTML = "";
    for (const name of data.tracks || []) {
      const opt = document.createElement("option");
      opt.value = name;
      opt.textContent = name;
      trackSelect.appendChild(opt);
    }
  } catch {
    /* leave empty */
  }
}

function updateModeUI() {
  for (const btn of modesEl.querySelectorAll("button")) {
    btn.classList.toggle("active", btn.dataset.mode === mode);
  }
  containerField.classList.toggle("hidden", mode !== "log_analyst");
  trackField.classList.toggle("hidden", mode !== "tutor");
  contextControls.classList.toggle("hidden", mode !== "log_analyst" && mode !== "tutor");
}

modesEl.addEventListener("click", (e) => {
  const btn = e.target.closest("button[data-mode]");
  if (!btn) return;
  mode = btn.dataset.mode;
  updateModeUI();
});

function appendBubble(role, text) {
  const div = document.createElement("div");
  div.className = `bubble ${role}`;
  div.textContent = text;
  transcriptEl.appendChild(div);
  transcriptEl.scrollTop = transcriptEl.scrollHeight;
}

formEl.addEventListener("submit", async (e) => {
  e.preventDefault();
  const message = messageEl.value.trim();
  if (!message) return;

  appendBubble("user", message);
  messageEl.value = "";
  messageEl.disabled = true;
  formEl.querySelector("button").disabled = true;

  const body = { mode, message, history };
  if (mode === "log_analyst") body.container = containerSelect.value;
  if (mode === "tutor") body.track = trackSelect.value;

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    if (!res.ok) {
      appendBubble("error", data.error || "Request failed");
    } else {
      appendBubble("assistant", data.reply);
      history.push({ role: "user", content: message });
      history.push({ role: "assistant", content: data.reply });
    }
  } catch (err) {
    appendBubble("error", `Request failed: ${err}`);
  } finally {
    messageEl.disabled = false;
    formEl.querySelector("button").disabled = false;
    messageEl.focus();
  }
});

updateModeUI();
checkHealth();
loadContainers();
loadTracks();
