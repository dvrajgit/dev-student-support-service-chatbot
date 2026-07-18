const loginPanel = document.getElementById('loginPanel');
const chatPanel = document.getElementById('chatPanel');
const loginForm = document.getElementById('loginForm');
const usernameInput = document.getElementById('usernameInput');
const passwordInput = document.getElementById('passwordInput');
const loginStatus = document.getElementById('loginStatus');
const logoutBtn = document.getElementById('logoutBtn');

const chatMessages = document.getElementById('chatMessages');
const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');
const apiKeyInput = document.getElementById('apiKeyInput');
const saveKeyBtn = document.getElementById('saveKeyBtn');
const clearKeyBtn = document.getElementById('clearKeyBtn');
const keyStatus = document.getElementById('keyStatus');

let conversation = [];
let currentMode = 'general';

function setLoggedIn(loggedIn) {
  loginPanel.classList.toggle('hidden', loggedIn);
  chatPanel.classList.toggle('hidden', !loggedIn);

  if (loggedIn) {
    messageInput.focus();
  } else {
    usernameInput.focus();
  }
}

function showLoginStatus(message, type = 'error') {
  loginStatus.textContent = message;
  loginStatus.className = `login-status ${type}`;
}

async function checkSession() {
  try {
    const response = await fetch('/api/session');
    const data = await response.json();
    setLoggedIn(Boolean(data.logged_in));
  } catch (error) {
    showLoginStatus('Unable to connect to the server.');
    setLoggedIn(false);
  }
}

loginForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  showLoginStatus('');

  try {
    const response = await fetch('/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: usernameInput.value.trim(),
        password: passwordInput.value,
      }),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.message || 'Login failed.');
    }

    passwordInput.value = '';
    showLoginStatus(data.message, 'success');
    setLoggedIn(true);
  } catch (error) {
    showLoginStatus(error.message || 'Login failed.');
  }
});

logoutBtn.addEventListener('click', async () => {
  await fetch('/api/logout', { method: 'POST' });
  conversation = [];
  chatMessages.innerHTML = '';
  addMessage('Hello! I am your AI assistant. Select a mode and ask me anything.', 'bot');
  setLoggedIn(false);
});

const modeButtons = document.querySelectorAll('.mode-btn');
modeButtons.forEach((btn) => {
  btn.addEventListener('click', () => {
    modeButtons.forEach((button) => button.classList.remove('active'));
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

  const apiKey = localStorage.getItem('gemini_api_key');
  if (apiKey) {
    headers['X-Gemini-API-Key'] = apiKey;
  }

  const response = await fetch('/api/chat', {
    method: 'POST',
    headers,
    body: JSON.stringify({ message: userMessage, mode: currentMode }),
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.reply || data.message || `Server request failed: ${response.status}`);
  }

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

function showKeyStatus(message, type) {
  keyStatus.textContent = message;
  keyStatus.className = `key-status ${type}`;
  setTimeout(() => {
    keyStatus.textContent = '';
    keyStatus.className = 'key-status';
  }, 3000);
}

const savedKey = localStorage.getItem('gemini_api_key');
if (savedKey) {
  apiKeyInput.value = savedKey;
  showKeyStatus('Key loaded from storage', 'saved');
}

saveKeyBtn.addEventListener('click', () => {
  const key = apiKeyInput.value.trim();
  if (!key) {
    showKeyStatus('Please enter an API key first.', 'cleared');
    return;
  }
  localStorage.setItem('gemini_api_key', key);
  showKeyStatus('API key saved.', 'saved');
});

clearKeyBtn.addEventListener('click', () => {
  localStorage.removeItem('gemini_api_key');
  apiKeyInput.value = '';
  showKeyStatus('Key cleared.', 'cleared');
});

addMessage('Hello! I am your AI assistant. Select a mode and ask me anything.', 'bot');
checkSession();
