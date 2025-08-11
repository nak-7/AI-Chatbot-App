const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");
const fileInput = document.getElementById("file-input");
const fileBtn = document.getElementById("file-btn");

function getSessionId() {
  return localStorage.getItem("session_id");
}
function setSessionId(sid) {
  localStorage.setItem("session_id", sid);
}

// Load saved messages
document.addEventListener("DOMContentLoaded", () => {
  const savedMessages = JSON.parse(localStorage.getItem("chat_messages") || "[]");
  savedMessages.forEach(msg => appendMessage(msg.sender, msg.text, false));
});

function saveMessage(sender, text) {
  let messages = JSON.parse(localStorage.getItem("chat_messages") || "[]");
  messages.push({ sender, text });
  localStorage.setItem("chat_messages", JSON.stringify(messages));
}

async function sendMessage() {
  const message = userInput.value.trim();
  if (!message) return;

  appendMessage("user", message);
  saveMessage("user", message);
  userInput.value = "";

  const typingId = appendTypingIndicator();
  const payload = { message, session_id: getSessionId() || undefined };

  try {
    const res = await fetch("http://localhost:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (data.session_id) setSessionId(data.session_id);

    updateMessage(typingId, data.response || "Sorry, something went wrong.", true);
    saveMessage("bot", data.response || "Sorry, something went wrong.");
  } catch (err) {
    console.error("Network error:", err);
    updateMessage(typingId, "Server unreachable. Please check your connection.", true);
    saveMessage("bot", "Server unreachable. Please check your connection.");
  }
}

function appendMessage(sender, text, isTemporary = false) {
  const messageDiv = document.createElement("div");
  messageDiv.classList.add("message", sender);

  const bubble = document.createElement("div");
  bubble.classList.add("bubble");
  bubble.innerText = text;
  messageDiv.appendChild(bubble);

  if (sender === "bot" && !isTemporary) addReactions(messageDiv, text);

  chatBox.appendChild(messageDiv);
  chatBox.scrollTop = chatBox.scrollHeight;

  if (isTemporary) {
    const tempId = "temp-" + Date.now();
    messageDiv.setAttribute("data-id", tempId);
    return tempId;
  }
}

function appendTypingIndicator() {
  const messageDiv = document.createElement("div");
  messageDiv.classList.add("message", "bot");

  const bubble = document.createElement("div");
  bubble.classList.add("bubble", "typing");
  bubble.innerHTML = `<span></span><span></span><span></span>`;

  messageDiv.appendChild(bubble);
  chatBox.appendChild(messageDiv);
  chatBox.scrollTop = chatBox.scrollHeight;

  const tempId = "temp-" + Date.now();
  messageDiv.setAttribute("data-id", tempId);
  return tempId;
}

function updateMessage(tempId, newText, isBot = false) {
  const messageDiv = chatBox.querySelector(`[data-id="${tempId}"]`);
  if (messageDiv) {
    const bubble = messageDiv.querySelector(".bubble");
    if (bubble) {
      bubble.classList.remove("typing");
      bubble.innerText = newText;
    }
    if (isBot) addReactions(messageDiv, newText);
  }
}

function addReactions(messageDiv, text) {
  const reactionContainer = document.createElement("div");
  reactionContainer.classList.add("reaction-container");

  const emojis = ["👍"]; // Only first two emojis
  emojis.forEach(emoji => {
    const emojiSpan = document.createElement("span");
    emojiSpan.textContent = emoji;
    emojiSpan.addEventListener("click", () => {
      reactionContainer.querySelectorAll("span").forEach(e => e.style.opacity = "0.5");
      emojiSpan.style.opacity = "1";
      console.log(`Reaction: ${emoji} for "${text}"`);
    });
    reactionContainer.appendChild(emojiSpan);
  });

  messageDiv.appendChild(reactionContainer);
}

// File upload
fileBtn.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", () => {
  if (fileInput.files.length > 0) {
    const fileName = fileInput.files[0].name;
    appendMessage("user", `📎 Uploaded: ${fileName}`);
    saveMessage("user", `📎 Uploaded: ${fileName}`);
  }
});

userInput.addEventListener("keypress", e => {
  if (e.key === "Enter") sendMessage();
});
