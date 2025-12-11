const chatBox = document.getElementById("chat-box");
const typing = document.getElementById("typing");
const micBtn = document.getElementById("mic-btn");
const micStatus = document.getElementById("mic-status");
const fileListDiv = document.getElementById("file-list");

let recognition = null;
let micOn = false;
let uploadedFiles = []; // track uploaded files metadata

// Initialize SpeechRecognition if available
function initSpeech(){
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        micBtn.disabled = true;
        micStatus.innerText = "SpeechRecognition not supported in this browser.";
        return;
    }
    recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.onstart = () => { micStatus.innerText = "Listening..."; micBtn.innerText = "⏸ Stop Mic"; };
    recognition.onend = () => { micStatus.innerText = "Mic off"; micBtn.innerText = "🎙 Start Mic"; micOn = false; };
    recognition.onresult = (ev) => {
        const text = Array.from(ev.results).map(r=>r[0].transcript).join('');
        document.getElementById("user-input").value += (document.getElementById("user-input").value ? " " : "") + text;
    };
}

initSpeech();

function toggleMic(){
    if (!recognition) return alert("Browser does not support SpeechRecognition.");
    if (!micOn) {
        micOn = true;
        recognition.start();
    } else {
        recognition.stop();
        micOn = false;
    }
}

// File upload handler: send file to backend /upload_file
async function uploadFile(){
    const input = document.getElementById("file-input");
    if (!input.files.length) return;
    const file = input.files[0];

    const form = new FormData();
    form.append('file', file);

    const res = await fetch('/upload_file', {
        method: 'POST',
        body: form
    });

    const data = await res.json();
    if (data.success) {
        uploadedFiles.push(data.meta);
        renderFileList();
        addMessage(`File uploaded: ${data.meta.filename}`, 'bot-message');
    } else {
        addMessage(`Upload failed: ${data.error}`, 'bot-message');
    }

    input.value = '';
}

function renderFileList(){
    fileListDiv.innerHTML = '';
    uploadedFiles.forEach((f, i) => {
        const div = document.createElement('div');
        div.className = 'file-item';
        div.innerHTML = `<strong>${f.filename}</strong> <small>${f.type}</small>
            <div style="margin-top:6px;">
                <button onclick="viewFileText(${i})">View text</button>
                <button onclick="removeFile(${i})">Remove</button>
            </div>`;
        fileListDiv.appendChild(div);
    });
}

async function viewFileText(i){
    const f = uploadedFiles[i];
    const res = await fetch(`/download_file_text?path=${encodeURIComponent(f.server_path)}`);
    const data = await res.json();
    if (data.success) {
        addMessage(`Contents of ${f.filename}:\n\n${data.text.slice(0,4000)}${data.text.length>4000 ? "\n\n... (truncated)" : ""}`, 'bot-message');
    } else {
        addMessage("Could not read file text.", 'bot-message');
    }
}

async function removeFile(i){
    const f = uploadedFiles[i];
    await fetch('/remove_file', {
        method:'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ path: f.server_path })
    });
    uploadedFiles.splice(i,1);
    renderFileList();
    addMessage(`Removed ${f.filename}`, 'bot-message');
}

// send user message
async function sendMessage() {
    const input = document.getElementById("user-input");
    const message = input.value.trim();
    if (!message) return;

    addMessage(message, "user-message");
    input.value = "";

    typing.classList.remove("hidden");

    // include uploaded files metadata to allow backend to consider them
    const response = await fetch("/ask", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            query: message,
            files: uploadedFiles
        })
    });

    const data = await response.json();

    typing.classList.add("hidden");

    typeText(data.answer);
}

// message helpers
function getTime(){
    const d = new Date();
    return d.getHours() + ":" + String(d.getMinutes()).padStart(2,"0");
}

function addMessage(text, className) {
    const div = document.createElement("div");
    div.className = className;
    // preserve newlines
    const html = text.split('\n').map(line => `<div>${escapeHtml(line)}</div>`).join('');
    div.innerHTML = html + `<div class="time">${getTime()}</div>`;
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function escapeHtml(unsafe) {
    return unsafe.replace(/[&<"'>]/g, function(m){ return ({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;' })[m]; });
}

// typing animation that types out assistant text
function typeText(text){
    const div = document.createElement("div");
    div.className = "bot-message";
    chatBox.appendChild(div);

    let i = 0;
    const speed = 14;
    const interval = setInterval(() => {
        div.innerHTML = escapeHtml(text.slice(0, i)) + `<div class="time">${getTime()}</div>`;
        i++;
        chatBox.scrollTop = chatBox.scrollHeight;
        if (i > text.length) {
            clearInterval(interval);
        }
    }, speed);
}

// Reset Chat
async function resetChat(){
    await fetch("/reset", {method:"POST"});
    chatBox.innerHTML = "";
    uploadedFiles = [];
    renderFileList();
    addMessage("New chat started. Ask anything.", "bot-message");
}

// Export chat text
function exportChat(){
    const text = chatBox.innerText;
    const blob = new Blob([text], {type:"text/plain"});
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "chat.txt";
    a.click();
}

// Dark/Light
function toggleMode(){
    document.body.classList.toggle("light");
}

// Enter key -> send
document.getElementById("user-input").addEventListener("keydown", function(e){
    if(e.key === "Enter" && !e.shiftKey){
        e.preventDefault();
        sendMessage();
    }
});
async function sendMessage() {
    const input = document.getElementById("user-input");
    const message = input.value;

    if (!message) return;

    const res = await fetch("/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: message })
    });

    const data = await res.json();
    
    document.getElementById("chat-box").innerHTML += `
        <div class="user-msg">${message}</div>
        <div class="bot-msg">${data.answer}</div>
    `;

    input.value = "";
}
fetch("/ask", {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify({ message: userMessage })
})
