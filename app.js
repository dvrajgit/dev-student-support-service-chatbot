const chatMessages = document.getElementById('chatMessages');
const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');
const apiKeyInput = document.getElementById('apiKeyInput');
const saveKeyBtn = document.getElementById('saveKeyBtn');
const clearKeyBtn = document.getElementById('clearKeyBtn');
const keyStatus = document.getElementById('keyStatus');

let conversation = [];
let currentMode = 'general';

// Mode selection logic
const modeButtons = document.querySelectorAll('.mode-btn');
modeButtons.forEach(btn => {
  btn.addEventListener('click', () => {
    modeButtons.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentMode = btn.dataset.mode;
  });
});

function addMessage(text, role = 'bot') {
  const messageEl = document.createElement('div');
  messageEl.className = `message ${role}`;
  messageEl.textContent = text;
  chatMessages.appendChild(messageEl);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addTypingIndicator() {
  const typingEl = document.createElement('div');
  typingEl.className = 'message bot typing';
  typingEl.textContent = 'Thinking...';
  typingEl.id = 'typing-indicator';
  chatMessages.appendChild(typingEl);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeTypingIndicator() {
  const typingIndicator = document.getElementById('typing-indicator');
  if (typingIndicator) {
    typingIndicator.remove();
  }
}

async function sendToServer(userMessage) {
  const headers = { 'Content-Type': 'application/json' };

  // Extract API key from localStorage if present
  const apiKey = localStorage.getItem('gemini_api_key');
  if (apiKey) {
    headers['X-Gemini-API-Key'] = apiKey;
  }

  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: headers,
    body: JSON.stringify({ message: userMessage, mode: currentMode }),
  });

  if (!response.ok) {
    const err = await response.text();
    throw new Error(`Server request failed: ${response.status} ${err}`);
  }

  const data = await response.json();
  return data.reply;
}

chatForm.addEventListener('submit', async (event) => {
  event.preventDefault();

  const userMessage = messageInput.value.trim();
  if (!userMessage) return;

  addMessage(userMessage, 'user');
  conversation.push({ role: 'user', text: userMessage });
  messageInput.value = '';
  addTypingIndicator();

  try {
    const reply = await sendToServer(userMessage);
    removeTypingIndicator();
    addMessage(reply, 'bot');
    conversation.push({ role: 'bot', text: reply });
  } catch (error) {
    removeTypingIndicator();
    addMessage(error.message || 'Something went wrong.', 'bot');
  }
});

// ── API Key Management ──────────────────────────────────────────────
function showKeyStatus(msg, type) {
  keyStatus.textContent = msg;
  keyStatus.className = `key-status ${type}`;
  setTimeout(() => { keyStatus.textContent = ''; keyStatus.className = 'key-status'; }, 3000);
}

// Auto-load saved key on page start
const savedKey = localStorage.getItem('gemini_api_key');
if (savedKey) {
  apiKeyInput.value = savedKey;
  showKeyStatus('✓ Key loaded from storage', 'saved');
}

saveKeyBtn.addEventListener('click', () => {
  const key = apiKeyInput.value.trim();
  if (!key) {
    showKeyStatus('⚠ Please enter an API key first.', 'cleared');
    return;
  }
  localStorage.setItem('gemini_api_key', key);
  showKeyStatus('✓ API key saved!', 'saved');
});

clearKeyBtn.addEventListener('click', () => {
  localStorage.removeItem('gemini_api_key');
  apiKeyInput.value = '';
  showKeyStatus('Key cleared.', 'cleared');
});

// ── Greeting ─────────────────────────────────────────────────────────
addMessage('Hello! I am your AI assistant. Select a mode and ask me anything.', 'bot');
