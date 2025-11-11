// ============================================
// NEBULA AGENT v6.0 - Professional Chat Interface
// ============================================

// Configuração da API
const API_BASE_URL = window.location.origin;

// Elementos da interface
const messagesEl = document.getElementById("messages");
const typingEl = document.getElementById("typing");
const inputEl = document.getElementById("inputMsg");
const formEl = document.getElementById("chatForm");
const creditsEl = document.getElementById("credits");
const creditsValueEl = document.getElementById("creditsValue");
const clearLocalBtn = document.getElementById("clearLocal");

let history = [];
let isProcessing = false;

// ============================================
// UTILITIES
// ============================================

function saveHistory() {
  try {
    localStorage.setItem("nebula_history_v1", JSON.stringify(history));
  } catch (e) {
    console.warn("localStorage error:", e);
  }
}

function loadHistory() {
  try {
    const data = localStorage.getItem("nebula_history_v1");
    history = data ? JSON.parse(data) : [];
  } catch (e) {
    history = [];
  }
}

function formatTime(ts) {
  const d = new Date(ts || Date.now());
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// ============================================
// MARKDOWN PARSER
// ============================================

function parseMarkdown(text) {
  if (!text) return '';
  
  let html = text;
  
  // Code blocks
  html = html.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
  
  // Inline code
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
  
  // Bold
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/__([^_]+)__/g, '<strong>$1</strong>');
  
  // Italic
  html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');
  html = html.replace(/_([^_]+)_/g, '<em>$1</em>');
  
  // Links
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
  
  // Line breaks
  html = html.replace(/\n/g, '<br>');
  
  return html;
}

// ============================================
// RENDER MESSAGES
// ============================================

function appendMessage({ role = 'assistant', text = '', ts = Date.now(), temp = false }) {
  const tpl = document.getElementById("msg-template");
  const node = tpl.content.cloneNode(true);
  const group = node.querySelector(".message-group");
  const avatar = node.querySelector(".avatar");
  const bubbleInner = node.querySelector(".bubble-inner");
  
  // Parse markdown for bot messages
  if (role === 'assistant') {
    bubbleInner.innerHTML = parseMarkdown(text);
  } else {
    bubbleInner.textContent = text;
  }
  
  avatar.textContent = role === 'user' ? 'U' : 'N';
  
  if (role === 'user') {
    group.classList.add("user");
  } else {
    group.classList.add("bot");
  }
  
  messagesEl.appendChild(node);
  scrollToBottom();
  
  return group;
}

function setTyping(on = true) {
  typingEl.style.display = on ? 'flex' : 'none';
  if (on) {
    scrollToBottom();
  }
}

function scrollToBottom() {
  messagesEl.scrollTop = messagesEl.scrollHeight - messagesEl.clientHeight + 100;
}

// ============================================
// API FUNCTIONS
// ============================================

async function fetchCredits() {
  try {
    const res = await fetch(`${API_BASE_URL}/billing/status`);
    if (res.ok) {
      const data = await res.json();
      const credits = data.credits ?? 0;
      creditsValueEl.textContent = credits;
      return credits;
    } else {
      creditsValueEl.textContent = '--';
      return null;
    }
  } catch (e) {
    console.error("Error fetching credits:", e);
    creditsValueEl.textContent = '--';
    return null;
  }
}

async function sendToAPI(message) {
  try {
    const res = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message })
    });
    
    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }
    
    const data = await res.json();
    return {
      reply: data.reply || data.response || "Sem resposta no momento.",
      credits: data.credits_remaining
    };
  } catch (e) {
    console.error("Error sending message:", e);
    throw e;
  }
}

// ============================================
// CHAT HANDLING
// ============================================

async function handleSend(raw) {
  if (isProcessing) return;
  
  const text = (raw || inputEl.value || "").trim();
  if (!text) return;
  
  isProcessing = true;
  inputEl.disabled = true;
  
  // Push user message
  const userMsg = { role: "user", text, ts: Date.now() };
  history.push(userMsg);
  saveHistory();
  appendMessage(userMsg);
  
  // Clear input
  inputEl.value = "";
  
  // Show typing
  setTyping(true);
  
  // Small delay for better UX
  await new Promise(r => setTimeout(r, 300));
  
  try {
    // Call API
    const response = await sendToAPI(text);
    
    // Hide typing
    setTyping(false);
    
    // Add bot message
    const botMsg = { role: "assistant", text: response.reply, ts: Date.now() };
    history.push(botMsg);
    saveHistory();
    appendMessage(botMsg);
    
    // Update credits
    if (response.credits !== undefined) {
      creditsValueEl.textContent = response.credits;
    } else {
      fetchCredits();
    }
    
  } catch (error) {
    setTyping(false);
    
    const errorMsg = {
      role: "assistant",
      text: "⚠️ **Erro de Conexão**\n\nNão consegui conectar ao servidor Nebula. Verifique se o backend está rodando corretamente.\n\n**Detalhes:** " + error.message,
      ts: Date.now()
    };
    
    history.push(errorMsg);
    saveHistory();
    appendMessage(errorMsg);
    
    console.error("❌ Erro:", error);
  } finally {
    isProcessing = false;
    inputEl.disabled = false;
    inputEl.focus();
  }
}

// ============================================
// INITIALIZATION
// ============================================

function ensureWelcome() {
  const hasSeen = history && history.length > 0;
  if (!hasSeen) {
    const welcome = {
      role: "assistant",
      text: "👋 **Olá! Eu sou a Nebula Agent v6.0**\n\nSou sua assistente inteligente especializada em:\n\n• 📝 **Geração de cenários Gherkin** para testes BDD\n• 🔍 **Análise de telas** e identificação de elementos\n• 🧪 **Sugestão de casos de teste** e estratégias\n• 📊 **Validação de funcionalidades** com BDD\n• 💡 **Consultoria** sobre testes e qualidade\n\n**Como posso ajudar você hoje?**\n\nTente pedir:\n- \"Gerar um cenário Gherkin para login\"\n- \"Analisar a tela de checkout\"\n- \"Que casos de teste devo criar?\"",
      ts: Date.now()
    };
    history.push(welcome);
    saveHistory();
  }
}

function renderHistory() {
  messagesEl.innerHTML = "";
  for (const m of history) {
    appendMessage(m);
  }
  scrollToBottom();
}

// ============================================
// EVENT LISTENERS
// ============================================

formEl.addEventListener("submit", async (e) => {
  e.preventDefault();
  await handleSend();
});

inputEl.addEventListener("keypress", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    handleSend();
  }
});

clearLocalBtn.addEventListener("click", async () => {
  if (confirm("Tem certeza que deseja limpar o histórico de conversa?")) {
    // Clear local history
    history = [];
    saveHistory();
    renderHistory();
    
    // Clear server history
    try {
      await fetch(`${API_BASE_URL}/clear-history`, {
        method: "POST",
        headers: { "Content-Type": "application/json" }
      });
    } catch (e) {
      console.error("Error clearing server history:", e);
    }
    
    // Show welcome message again
    ensureWelcome();
    renderHistory();
  }
});

// Navigation buttons
document.querySelectorAll(".nav-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".nav-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    // Future: implement view switching
  });
});

// ============================================
// INITIALIZE
// ============================================

document.addEventListener("DOMContentLoaded", () => {
  loadHistory();
  ensureWelcome();
  renderHistory();
  fetchCredits();
  
  // Focus input
  inputEl.focus();
  
  console.log("✅ Nebula Agent v6.0 initialized");
});
