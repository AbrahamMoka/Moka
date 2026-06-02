// ================================================================
//  recorder.js FINAL
//  Corrección absoluta del error "No se ha configurado recorder(url)"
// ================================================================

let blobs = [];
let stream = null;
let rec = null;

let recordUrl = null;               // <-- si esto no está configurado, NO hay grabación
let audioResponseHandler = null;

let voiceMode = false;
let audioPlayer = null;

// ================================================================
//  CONFIGURACIÓN DEL RECORDER
// ================================================================
function recorder(url, handler) {
    if (!url) {
        console.error("❌ recorder(url) fue llamado SIN url");
        return;
    }

    console.log("✔ recorder configurado con URL:", url);

    recordUrl = url;
    audioResponseHandler = handler || null;
}

// ================================================================
//  INICIAR GRABACIÓN
// ================================================================
async function record() {
    // Protección absoluta contra el error
    if (!recordUrl) {
        console.error("❌ No se ha configurado recorder(url). Evitando POST /undefined.");
        return;
    }

    try {
        document.getElementById("text").innerHTML = "<i>Grabando...</i>";
        document.getElementById("record").style.display = "none";
        document.getElementById("stop").style.display = "";
        document.getElementById("record-stop-label").style.display = "block";
        document.getElementById("record-stop-loading").style.display = "none";
        document.getElementById("stop").disabled = false;

        blobs = [];

        stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        rec = new MediaRecorder(stream);

        rec.ondataavailable = e => {
            if (e.data) blobs.push(e.data);
        };

        rec.onstop = doPreview;

        rec.start();
    } catch (e) {
        alert("No se pudo iniciar el micro. Revisa permisos o HTTPS.");
    }
}

// ================================================================
//  PROCESAR GRABACIÓN
// ================================================================
function doPreview() {
    resetRecorderUI();

    if (!blobs.length) {
        console.warn("No hay audio capturado.");

        if (voiceMode) record();
        return;
    }

    const blob = new Blob(blobs, { type: "audio/webm" });
    const fd = new FormData();
    fd.append("audio", blob, "audio");

    fetch(recordUrl, {
        method: "POST",
        body: fd
    })
    .then(res => res.json())
    .then(data => {
        if (audioResponseHandler) audioResponseHandler(data);

        if (data.file) {
            if (!audioPlayer) audioPlayer = document.getElementById("audio-response");

            audioPlayer.src = "/static/" + data.file + "?v=" + Date.now();
            audioPlayer.play();

            audioPlayer.onended = () => {
                if (voiceMode) startVoiceMode();
            };
        } else {
            if (voiceMode) startVoiceMode();
        }
    })
    .catch(err => {
        console.error("Error al enviar audio:", err);
        if (voiceMode) startVoiceMode();
    });
}

// ================================================================
//  DETENER GRABACIÓN
// ================================================================
function stop() {
    document.getElementById("record-stop-label").style.display = "none";
    document.getElementById("record-stop-loading").style.display = "block";
    document.getElementById("stop").disabled = true;

    if (rec && rec.state === "recording") rec.stop();
}

// ================================================================
//  RESET UI
// ================================================================
function resetRecorderUI() {
    document.getElementById("record").style.display = "";
    document.getElementById("stop").style.display = "none";
    document.getElementById("listening-indicator").style.display = "none";
}

// ================================================================
//  MODO DE VOZ
// ================================================================
window.addEventListener("voice-mode-change", e => {
    voiceMode = e.detail;
    if (voiceMode) startVoiceMode();
});

function startVoiceMode() {
    if (!recordUrl) {
        console.error("❌ No puedo iniciar voiceMode: recorder(url) no fue configurado.");
        return;
    }

    console.log("🎤 Moka escuchando...");
    document.getElementById("listening-indicator").style.display = "block";
    record();
}
