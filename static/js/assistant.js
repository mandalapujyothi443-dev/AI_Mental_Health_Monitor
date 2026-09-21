const chat = document.getElementById("chat");
const input = document.getElementById("message");
const send = document.getElementById("send");
const mic = document.getElementById("mic");
const speak = document.getElementById("speak");
const clear = document.getElementById("clear");
const language = document.getElementById("language");
const voiceStatus = document.getElementById("voiceStatus");

let history = [];
let lastAnswer = "";
let recorder = null;
let chunks = [];
let recording = false;

function addBubble(text, who) {
    const div = document.createElement("div");
    div.className = `bubble ${who === "user" ? "user-bubble" : "assistant-bubble"}`;
    div.textContent = text;
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
}

async function ask(message) {
    message = message.trim();
    if (!message) return;

    addBubble(message, "user");
    input.value = "";
    send.disabled = true;
    voiceStatus.textContent = "AI is thinking...";

    try {
        const res = await fetch("/assistant/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({message, history})
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || "Unable to get AI response.");

        lastAnswer = data.answer || "I could not generate a response.";
        addBubble(lastAnswer, "assistant");
        history.push({role: "user", content: message});
        history.push({role: "assistant", content: lastAnswer});
        history = history.slice(-10);
        speak.disabled = !lastAnswer;
        voiceStatus.textContent = "Ready";
    } catch (err) {
        addBubble("Sorry, I could not connect to the AI assistant. Please try again.", "assistant");
        voiceStatus.textContent = err.message;
    } finally {
        send.disabled = false;
        input.focus();
    }
}

send.addEventListener("click", () => ask(input.value));
input.addEventListener("keydown", e => {
    if (e.key === "Enter") ask(input.value);
});

speak.addEventListener("click", () => {
    if (!lastAnswer || !("speechSynthesis" in window)) return;
    speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(lastAnswer);
    const selected = language.value || "en";
    utterance.lang = selected === "te" ? "te-IN" :
                     selected === "hi" ? "hi-IN" :
                     selected === "ta" ? "ta-IN" :
                     selected === "kn" ? "kn-IN" :
                     selected === "ml" ? "ml-IN" : "en-IN";
    speechSynthesis.speak(utterance);
});

clear.addEventListener("click", () => {
    history = [];
    lastAnswer = "";
    chat.innerHTML = '<div class="bubble assistant-bubble">Chat cleared. How can I support you?</div>';
    speak.disabled = true;
});

async function startRecording() {
    if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) {
        voiceStatus.textContent = "Your browser does not support microphone recording.";
        return;
    }

    try {
        const stream = await navigator.mediaDevices.getUserMedia({audio: true});
        chunks = [];
        const types = ["audio/webm;codecs=opus", "audio/webm", "audio/ogg;codecs=opus"];
        const mime = types.find(t => MediaRecorder.isTypeSupported(t));
        recorder = mime ? new MediaRecorder(stream, {mimeType: mime}) : new MediaRecorder(stream);

        recorder.ondataavailable = e => {
            if (e.data.size) chunks.push(e.data);
        };
        recorder.onstop = async () => {
            stream.getTracks().forEach(t => t.stop());
            const blob = new Blob(chunks, {type: recorder.mimeType || "audio/webm"});
            await transcribe(blob);
        };

        recorder.start();
        recording = true;
        mic.classList.add("recording");
        mic.textContent = "⏹️";
        voiceStatus.textContent = "Listening... click again to stop";
    } catch {
        voiceStatus.textContent = "Microphone permission was denied.";
    }
}

function stopRecording() {
    if (!recorder || recorder.state === "inactive") return;
    recorder.stop();
    recording = false;
    mic.classList.remove("recording");
    mic.textContent = "🎤";
    voiceStatus.textContent = "Converting speech to text...";
}

mic.addEventListener("click", () => recording ? stopRecording() : startRecording());

async function transcribe(blob) {
    const fd = new FormData();
    fd.append("audio", blob, blob.type.includes("ogg") ? "voice.ogg" : "voice.webm");
    if (language.value) fd.append("language", language.value);

    try {
        const res = await fetch("/assistant/transcribe", {method: "POST", body: fd});
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || "Speech recognition failed.");
        if (!data.text) throw new Error("No speech was detected. Please try again.");
        input.value = data.text;
        voiceStatus.textContent = "Speech recognized.";
        await ask(data.text);
    } catch (err) {
        voiceStatus.textContent = err.message;
    }
}
