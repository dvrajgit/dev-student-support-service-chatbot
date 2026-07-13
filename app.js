const chatMessages = document.getElementById('chatMessages');
const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');
const apiKeyInput = document.getElementById('apiKey');
const saveKeyBtn = document.getElementById('saveKeyBtn');

const STORAGE_KEY = 'gemini_api_key';
let conversation = [];

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

function getStoredApiKey() {
  return localStorage.getItem(STORAGE_KEY) || '';
}

function saveApiKey() {
  const key = apiKeyInput.value.trim();
  if (!key) {
    alert('Please enter a Gemini API key.');
    return;
  }

  localStorage.setItem(STORAGE_KEY, key);
  apiKeyInput.value = '';
  addMessage('API key saved locally for this browser.', 'bot');
}

async function sendToGemini(userMessage) {
  const apiKey = getStoredApiKey();
  if (!apiKey) {
    throw new Error('Please enter your Gemini API key first.');
  }

  const payload = {
    contents: conversation.concat([{ role: 'user', parts: [{ text: userMessage }] }]).map((entry) => ({
      role: entry.role === 'user' ? 'user' : 'model',
      parts: [{ text: entry.text }],
    })),
  };

  const response = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    }
  );

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`Request failed: ${response.status} ${errorBody}`);
  }

  const data = await response.json();
  const reply = data?.candidates?.[0]?.content?.parts?.[0]?.text || 'Sorry, I could not generate a reply.';
  return reply;
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
    const reply = await sendToGemini(userMessage);
    removeTypingIndicator();
    addMessage(reply, 'bot');
    conversation.push({ role: 'bot', text: reply });
  } catch (error) {
    removeTypingIndicator();
    addMessage(error.message || 'Something went wrong.', 'bot');
  }
});

saveKeyBtn.addEventListener('click', saveApiKey);

apiKeyInput.value = getStoredApiKey();

addMessage('Hello! I am your simple AI assistant. Ask me anything.', 'bot');
