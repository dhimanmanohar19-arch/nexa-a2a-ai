JavaScript

const input = document.getElementById("question");
const chat = document.getElementById("chat");
const statusBox = document.getElementById("status");

function addMessage(text, type) {
  const div = document.createElement("div");
  div.className = type + "-message";
  div.textContent = text;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
}

async function askRobot() {
  const question = input.value.trim();
  if (!question) return;

  addMessage(question, "user");
  input.value = "";

  statusBox.textContent = "रोबोट सोच रहा है...";

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ message: question })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Server error");
    }

    addMessage(
      data.reply || data.answer || "कोई जवाब नहीं मिला।",
      "bot"
    );

    statusBox.textContent = "रोबोट ऑनलाइन है";
  } catch (error) {
    addMessage(
      "सर्वर से जवाब नहीं मिला। Backend और API चेक करें।",
      "bot"
    );
    statusBox.textContent = "कनेक्शन में समस्या";
  }
}

document.getElementById("send")
  .addEventListener("click", askRobot);

input.addEventListener("keydown", event => {
  if (event.key === "Enter") askRobot();
});

document.getElementById("mic")
  .addEventListener("click", () => {
    const SpeechRecognition =
      window.SpeechRecognition ||
      window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert("इस ब्राउज़र में Voice Recognition उपलब्ध नहीं है।");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "hi-IN";
    recognition.onresult = event => {
      input.value = event.results[0][0].transcript;
      askRobot();
    };
    recognition.start();
  });SpeechRecognition();
    recognition.lang = "hi-IN";
    recognition.start();

    recognition.onresult = function(event) {
      messageInput.value = event.results[0][0].transcript;
      sendMessage();
    };
  });
}

console.log("NEXA A2A AI loaded successfully!");


