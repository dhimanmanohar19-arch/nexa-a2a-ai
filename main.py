Python

import os
from flask import Flask, request, jsonify, render_template_string
from openai import OpenAI

app = Flask(__name__)

API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

client = OpenAI(api_key=API_KEY) if API_KEY else None

SYSTEM_PROMPT = """
You are NEXA A2A, a helpful and intelligent AI assistant.
Understand the user's language, including Hindi and Urdu.
Answer clearly, accurately and politely.
Help with questions, coding, learning and daily tasks.
Never pretend to perform actions you cannot perform.
"""

PAGE = """
<!DOCTYPE html>
<html lang="hi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>NEXA A2A AI</title>
<style>
*{box-sizing:border-box}
body{
 margin:0;background:#101827;color:white;
 font-family:Arial,sans-serif;
}
.container{
 max-width:750px;margin:25px auto;padding:18px;
}
h1{text-align:center;color:#55d6ff}
#status{text-align:center;color:#9ca3af}
#chat{
 height:58vh;overflow-y:auto;
 background:#192638;border-radius:14px;
 padding:15px;margin:18px 0;
}
.msg{
 padding:12px 15px;margin:10px 0;
 border-radius:12px;white-space:pre-wrap;
 line-height:1.5;overflow-wrap:anywhere;
}
.user{background:#075985;margin-left:35px}
.bot{background:#29384c;margin-right:35px}
.controls{display:flex;gap:8px}
input{
 flex:1;min-width:0;padding:14px;
 border:0;border-radius:10px;font-size:16px;
}
button{
 border:0;border-radius:10px;padding:12px 16px;
 background:#06b6d4;color:#00131b;
 font-weight:bold;cursor:pointer;
}
button:disabled{opacity:.5}
.small{text-align:center;color:#9ca3af;font-size:13px}
</style>
</head>
<body>
<div class="container">
<h1>🤖 NEXA A2A</h1>
<p id="status">AI Robot Ready</p>
<div id="chat">
 <div class="msg bot">नमस्ते! मैं NEXA A2A हूँ। बताइए, मैं आपकी क्या मदद करूँ?</div>
</div>
<div class="controls">
<input id="message" placeholder="अपना सवाल लिखें..." autocomplete="off">
<button id="send" onclick="sendMessage()">भेजें</button>
<button onclick="voiceInput()">🎤</button>
</div>
<p class="small">NEXA A2A • AI Assistant</p>
</div>
<script>
const chat = document.getElementById("chat");
const input = document.getElementById("message");
const statusText = document.getElementById("status");
const sendButton = document.getElementById("send");
let history = [];

function addMessage(text, who) {
 const div = document.createElement("div");
 div.className = "msg " + who;
 div.textContent = text;
 chat.appendChild(div);
 chat.scrollTop = chat.scrollHeight;
 return div;
}

async function sendMessage() {
 const message = input.value.trim();
 if (!message || sendButton.disabled) return;

 input.value = "";
 addMessage(message, "user");
 const loading = addMessage("NEXA सोच रहा है...", "bot");

 sendButton.disabled = true;
 statusText.textContent = "AI से संपर्क हो रहा है...";

 try {
   const response = await fetch("/api/chat", {
     method: "POST",
     headers: {"Content-Type": "application/json"},
     body: JSON.stringify({
       message: message,
       history: history.slice(-10)
     })
   });

   const data = await response.json();
   loading.textContent = data.reply || data.error || "कोई जवाब नहीं मिला।";

   if (response.ok && data.reply) {
     history.push({role:"user", content:message});
     history.push({role:"assistant", content:data.reply});
     history = history.slice(-10);
   }

   statusText.textContent = response.ok ? "AI Robot Online" : "जवाब में समस्या";
 } catch (error) {
   loading.textContent = "सर्वर से संपर्क नहीं हो पाया। कृपया दोबारा कोशिश करें।";
   statusText.textContent = "Connection Error";
 } finally {
   sendButton.disabled = false;
   input.focus();
 }
}

input.addEventListener("keydown", function(event) {
 if (event.key === "Enter") sendMessage();
});

function voiceInput() {
 const Speech = window.SpeechRecognition || window.webkitSpeechRecognition;
 if (!Speech) {
   addMessage("आपके ब्राउज़र में Voice Recognition उपलब्ध नहीं है।", "bot");
   return;
 }
 const recognition = new Speech();
 recognition.lang = "hi-IN";
 recognition.onresult = function(event) {
   input.value = event.results[0][0].transcript;
   sendMessage();
 };
 recognition.onerror = function() {
   statusText.textContent = "माइक्रोफोन की अनुमति जाँचें";
 };
 recognition.start();
}
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(PAGE)

@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "app": "NEXA A2A",
        "ai_configured": client is not None
    })

@app.route("/api/chat", methods=["POST"])
def chat():
    if client is None:
        return jsonify({
            "error": "OPENAI_API_KEY Render Environment में सेट नहीं है।"
        }), 503

    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()

    if not message:
        return jsonify({"error": "कृपया अपना सवाल लिखें।"}), 400

    if len(message) > 4000:
        return jsonify({"error": "सवाल 4000 अक्षरों से छोटा रखें।"}), 400

    history = data.get("history", [])
    if not isinstance(history, list):
        history = []

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for item in history[-10:]:
        if not isinstance(item, dict):
            continue
        role = item.get("role")
        content = item.get("content")
        if role in ("user", "assistant") and isinstance(content, str):
            messages.append({
                "role": role,
                "content": content[:4000]
            })

    messages.append({"role": "user", "content": message})

    try:
        result = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )

        answer = result.choices[0].message.content or ""
        return jsonify({"reply": answer})

    except Exception as error:
        app.logger.exception("AI request failed")
        return jsonify({
            "error": "AI से जवाब लेने में समस्या हुई। API Key, मॉडल और बिलिंग जाँचें।"
        }), 502

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

