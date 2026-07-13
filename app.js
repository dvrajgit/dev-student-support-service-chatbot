const chatMessages = document.getElementById('chatMessages');
const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');

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

async function sendToServer(userMessage) {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: userMessage }),
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

// API key UI removed; keys can still be provided via `localStorage` under
// the `gemini_api_key` key if desired.

addMessage('Hello! I am your simple AI assistant. Ask me anything.', 'bot');
