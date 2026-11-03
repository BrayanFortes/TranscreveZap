const TRANSCRIBE_ENDPOINT = "http://127.0.0.1:5000/api/transcrever";
let tabStream = null;
let audioContext = null;
let armedTabId = null;
let recorder = null;
let chunks = [];

async function armCapture(streamId, tabId) {
  if (tabStream) tabStream.getTracks().forEach((track) => track.stop());
  tabStream = await navigator.mediaDevices.getUserMedia({
    audio: { mandatory: { chromeMediaSource: "tab", chromeMediaSourceId: streamId } },
    video: { mandatory: { chromeMediaSource: "tab", chromeMediaSourceId: streamId } }
  });
  const audioOnly = new MediaStream(tabStream.getAudioTracks());
  audioContext = new AudioContext();
  audioContext.createMediaStreamSource(audioOnly).connect(audioContext.destination);
  if (audioContext.state === "suspended") await audioContext.resume();
  armedTabId = tabId;
  return { ok: true };
}

function startRecording(tabId) {
  if (!tabStream || tabId !== armedTabId) return { ok: false, error: "Clique no ícone da extensão com o WhatsApp Web aberto para ativar a captura." };
  if (recorder?.state === "recording") return { ok: false, error: "Já existe uma captura em andamento." };
  chunks = [];
  const audioOnly = new MediaStream(tabStream.getAudioTracks());
  const preferredType = MediaRecorder.isTypeSupported("audio/webm;codecs=opus") ? "audio/webm;codecs=opus" : "audio/webm";
  recorder = new MediaRecorder(audioOnly, MediaRecorder.isTypeSupported(preferredType) ? { mimeType: preferredType } : undefined);
  recorder.addEventListener("dataavailable", (event) => {
    if (event.data?.size) chunks.push(event.data);
  });
  recorder.start(300);
  return { ok: true };
}

function stopAndTranscribe(tabId) {
  if (tabId !== armedTabId) return Promise.resolve({ ok: false, error: "A captura está armada para outra aba. Clique no ícone da extensão nesta aba." });
  if (!recorder || recorder.state !== "recording") return Promise.resolve({ ok: false, error: "A gravação da aba não está ativa." });

  return new Promise((resolve) => {
    recorder.addEventListener("stop", async () => {
      try {
        const mimeType = recorder.mimeType || "audio/webm";
        const blob = new Blob(chunks, { type: mimeType });
        chunks = [];
        if (blob.size < 2048) throw new Error("Não capturei som suficiente. Ative a captura e reproduza a mensagem novamente.");
        if (blob.size > 25 * 1024 * 1024) throw new Error("O áudio capturado ultrapassa o limite de 25 MB.");
        const form = new FormData();
        form.append("audio", blob, `whatsapp-voz-${Date.now()}.webm`);
        const response = await fetch(TRANSCRIBE_ENDPOINT, { method: "POST", body: form });
        const payload = await response.json().catch(() => ({}));
        if (!response.ok) throw new Error(payload.error || "O TranscreveZap não conseguiu transcrever o áudio.");
        resolve({ ok: true, text: payload.text || "Nenhuma fala foi reconhecida neste áudio." });
      } catch (error) {
        resolve({ ok: false, error: error?.message || "Falha ao transcrever o áudio capturado." });
      }
    }, { once: true });
    recorder.stop();
  });
}

chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message?.target !== "transcrevezap-offscreen") return false;
  if (message.type === "arm-tab-capture") {
    armCapture(message.streamId, message.tabId).then(sendResponse).catch((error) => sendResponse({ ok: false, error: error?.message || "O Chrome bloqueou a captura de áudio desta aba." }));
    return true;
  }
  if (message.type === "start-recording") {
    sendResponse(startRecording(message.tabId));
    return false;
  }
  if (message.type === "stop-recording") {
    stopAndTranscribe(message.tabId).then(sendResponse);
    return true;
  }
  return false;
});
