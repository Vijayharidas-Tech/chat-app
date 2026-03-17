(() => {
  const cfg = window.CHAT_CONFIG;
  if (!cfg) return;

  const chatLog = document.getElementById("chat-log");
  const typingEl = document.getElementById("typing-indicator");
  const messageInput = document.getElementById("chat-message-input");
  const form = document.getElementById("chat-form");
  const sendBtn = document.getElementById("chat-message-submit");

  function scrollToBottom() {
    if (chatLog) {
      chatLog.scrollTop = chatLog.scrollHeight;
    }
  }

  scrollToBottom();

  const wsUrl =
    cfg.wsScheme +
    "://" +
    window.location.host +
    cfg.wsPath.replace(/^http(s?):/, "");

  const socket = new WebSocket(wsUrl);

  let typingTimeoutId = null;

  socket.onmessage = function (e) {
    const data = JSON.parse(e.data);

    // Typing indicator events
    if (data.type === "typing") {
      if (data.sender === cfg.otherUsername && typingEl) {
        typingEl.style.display = "block";
        if (typingTimeoutId) {
          clearTimeout(typingTimeoutId);
        }
        typingTimeoutId = setTimeout(() => {
          typingEl.style.display = "none";
        }, 1500);
      }
      return;
    }
    const isOwn = data.sender === cfg.currentUsername;

    const row = document.createElement("div");
    row.className = "message-row " + (isOwn ? "sent" : "received");

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";

    const text = document.createElement("div");
    text.className = "message-text";
    text.textContent = data.message;

    const meta = document.createElement("div");
    meta.className = "message-meta";
    const time = document.createElement("small");
    time.textContent = new Date(data.timestamp).toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
    meta.appendChild(time);

    if (isOwn) {
      const status = document.createElement("small");
      status.className = "ms-1";
      status.textContent = data.is_read ? "✓✓" : "✓";
      meta.appendChild(status);
    }

    bubble.appendChild(text);
    bubble.appendChild(meta);
    row.appendChild(bubble);
    chatLog.appendChild(row);
    scrollToBottom();
  };

  socket.onclose = function () {
    console.warn("WebSocket closed.");
  };

  function sendCurrentMessage() {
    const message = (messageInput.value || "").trim();
    if (!message) return;
    if (socket.readyState !== WebSocket.OPEN) return;

    socket.send(
      JSON.stringify({
        kind: "message",
        message: message,
        receiver: cfg.otherUsername,
      })
    );
    messageInput.value = "";
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    sendCurrentMessage();
  });

  if (sendBtn) {
    sendBtn.addEventListener("click", function () {
      sendCurrentMessage();
    });
  }

  if (messageInput) {
    let lastTypingSent = 0;
    messageInput.addEventListener("keydown", function (e) {
      const now = Date.now();
      if (socket.readyState === WebSocket.OPEN && now - lastTypingSent > 500) {
        socket.send(
          JSON.stringify({
            kind: "typing",
            receiver: cfg.otherUsername,
          })
        );
        lastTypingSent = now;
      }

      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendCurrentMessage();
      }
    });
  }
})();

