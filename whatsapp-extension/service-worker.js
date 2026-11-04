const TRANSCRIBE_ENDPOINTS = [
  "http://127.0.0.1:5000/api/transcrever",
  "https://transcreve-zap.vercel.app/api/transcrever"
];
const MAX_AUDIO_BYTES = 100 * 1024 * 1024;

function extensionForMime(mimeType) {
  const normalized = (mimeType || "").split(";")[0].toLowerCase();
  return ({
    "audio/aac": "aac",
    "audio/flac": "flac",
    "audio/mp4": "m4a",
    "audio/mpeg": "mp3",
    "audio/ogg": "ogg",
    "audio/wav": "wav",
    "audio/webm": "webm"
  })[normalized] || "ogg";
}

function fileFromBase64(base64, mimeType, filename) {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let index = 0; index < binary.length; index += 1) {
    bytes[index] = binary.charCodeAt(index);
  }
  const normalizedMime = (mimeType || "audio/ogg").split(";")[0];
  const safeName = filename || `whatsapp-audio.${extensionForMime(normalizedMime)}`;
  return new File([bytes], safeName, { type: normalizedMime });
}

function installWhatsAppAudioHook() {
  const hookFlag = "__transcrevezapAudioHookV1";
  if (window[hookFlag]) return;
  Object.defineProperty(window, hookFlag, { value: true, configurable: false });

  let requestId = null;
  let expireTimer = null;
  const pageOrigin = window.location.origin;

  function mimeFromBuffer(buffer) {
    const bytes = new Uint8Array(buffer);
    if (bytes.length >= 4 && bytes[0] === 0x4f && bytes[1] === 0x67 && bytes[2] === 0x67 && bytes[3] === 0x53) return "audio/ogg";
    if (bytes.length >= 4 && bytes[0] === 0x1a && bytes[1] === 0x45 && bytes[2] === 0xdf && bytes[3] === 0xa3) return "audio/webm";
    if (bytes.length >= 8 && String.fromCharCode(...bytes.slice(4, 8)) === "ftyp") return "audio/mp4";
    if (bytes.length >= 4 && String.fromCharCode(...bytes.slice(0, 4)) === "RIFF") return "audio/wav";
    if (bytes.length >= 3 && String.fromCharCode(...bytes.slice(0, 3)) === "ID3") return "audio/mpeg";
    if (bytes.length >= 2 && bytes[0] === 0xff && (bytes[1] & 0xe0) === 0xe0) return "audio/mpeg";
    return "";
  }

  function sendCapturedBlob(blob, mimeType) {
    if (!requestId || !blob || blob.size < 4096 || blob.size > 100 * 1024 * 1024) return;
    const activeRequest = requestId;
    requestId = null;
    clearTimeout(expireTimer);
    window.postMessage({
      source: "transcrevezap-page",
      type: "captured-audio",
      requestId: activeRequest,
      mimeType,
      blob
    }, pageOrigin);
  }

  window.addEventListener("message", (event) => {
    if (event.source !== window || event.origin !== pageOrigin) return;
    const message = event.data;
    if (message?.source !== "transcrevezap-content" || message.type !== "capture-audio" || typeof message.requestId !== "string") return;
    requestId = message.requestId;
    clearTimeout(expireTimer);
    expireTimer = setTimeout(() => { requestId = null; }, 15000);
  });

  const originalCreateObjectURL = URL.createObjectURL.bind(URL);
  URL.createObjectURL = function (object) {
    const url = originalCreateObjectURL(object);
    if (requestId && object instanceof Blob && object.type.toLowerCase().startsWith("audio/")) {
      sendCapturedBlob(object, object.type.split(";")[0].toLowerCase());
    }
    return url;
  };

  if (window.HTMLMediaElement?.prototype?.play) {
    const originalMediaPlay = HTMLMediaElement.prototype.play;
    HTMLMediaElement.prototype.play = function (...args) {
      const source = this.currentSrc || this.src || "";
      if (requestId && source.startsWith("blob:")) {
        const activeRequest = requestId;
        fetch(source).then((response) => response.blob()).then((blob) => {
          if (requestId === activeRequest && blob.type.toLowerCase().startsWith("audio/")) {
            sendCapturedBlob(blob, blob.type.split(";")[0].toLowerCase());
          }
        }).catch(() => {});
      }
      return originalMediaPlay.apply(this, args);
    };
  }

  if (window.AudioContext?.prototype?.decodeAudioData) {
    const originalDecodeAudioData = AudioContext.prototype.decodeAudioData;
    AudioContext.prototype.decodeAudioData = function (audioData, ...args) {
      if (requestId && audioData instanceof ArrayBuffer && audioData.byteLength <= 100 * 1024 * 1024) {
        const mimeType = mimeFromBuffer(audioData);
        if (mimeType) sendCapturedBlob(new Blob([audioData.slice(0)], { type: mimeType }), mimeType);
      }
      return originalDecodeAudioData.call(this, audioData, ...args);
    };
  }

}

function isAllowedWhatsAppMediaUrl(value) {
  try {
    const url = new URL(value);
    if (url.protocol !== "https:") return false;
    const host = url.hostname.toLowerCase();
    return host === "web.whatsapp.com" ||
      host.endsWith(".whatsapp.net") ||
      host.endsWith(".fbcdn.net") ||
      host === "lookaside.fbsbx.com";
  } catch {
    return false;
  }
}

async function transcribe(file) {
  if (!file || file.size === 0) throw new Error("O áudio está vazio ou não foi carregado.");
  if (file.size > MAX_AUDIO_BYTES) throw new Error("O áudio ultrapassa o limite de 100 MB.");

  let lastError = null;
  for (const endpoint of TRANSCRIBE_ENDPOINTS) {
    try {
      const form = new FormData();
      form.append("audio", file, file.name);
      const response = await fetch(endpoint, { method: "POST", body: form });
      const payload = await response.json().catch(() => ({}));
      if (response.ok) {
        return payload.text || "";
      }
      lastError = new Error(payload.error || "O TranscreveZap não conseguiu transcrever o áudio.");
    } catch (err) {
      lastError = err;
    }
  }
  throw lastError || new Error("Falha ao comunicar com o servidor do TranscreveZap.");
}

async function ensureOffscreenRecorder() {
  if (await chrome.offscreen.hasDocument()) return;
  await chrome.offscreen.createDocument({
    url: "recorder.html",
    reasons: ["USER_MEDIA"],
    justification: "Capture o áudio reproduzido na aba do WhatsApp Web para transcrevê-lo."
  });
}

chrome.action.onClicked.addListener(async (tab) => {
  if (!tab.id || !tab.url?.startsWith("https://web.whatsapp.com/")) return;
  try {
    await ensureOffscreenRecorder();
    const streamId = await chrome.tabCapture.getMediaStreamId({ targetTabId: tab.id });
    const armed = await chrome.runtime.sendMessage({
      target: "transcrevezap-offscreen",
      type: "arm-tab-capture",
      streamId,
      tabId: tab.id
    });
    if (!armed?.ok) throw new Error(armed?.error || "O Chrome não liberou a captura desta aba.");
    await chrome.tabs.sendMessage(tab.id, { type: "transcrevezap-capture-ready" });
    await chrome.action.setBadgeText({ tabId: tab.id, text: "ON" });
    await chrome.action.setBadgeBackgroundColor({ tabId: tab.id, color: "#168451" });
  } catch (error) {
    console.error("TranscreveZap tab capture:", error);
    await chrome.action.setBadgeText({ tabId: tab.id, text: "!" });
    await chrome.action.setBadgeBackgroundColor({ tabId: tab.id, color: "#b73531" });
  }
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (!sender.url?.startsWith("https://web.whatsapp.com/")) return false;

  if (message?.type === "transcrevezap-start-tab-audio" || message?.type === "transcrevezap-stop-tab-audio") {
    if (typeof sender.tab?.id !== "number") {
      sendResponse({ ok: false, error: "Não encontrei a aba do WhatsApp Web." });
      return false;
    }
    const type = message.type === "transcrevezap-start-tab-audio" ? "start-recording" : "stop-recording";
    chrome.runtime.sendMessage({ target: "transcrevezap-offscreen", type, tabId: sender.tab.id })
      .then(sendResponse)
      .catch((error) => sendResponse({ ok: false, error: error?.message || "Não consegui acessar o gravador da extensão." }));
    return true;
  }

  if (message?.type === "transcrevezap-install-audio-hook") {
    if (typeof sender.tab?.id !== "number") {
      sendResponse({ ok: false, error: "Não encontrei a aba do WhatsApp Web." });
      return false;
    }
    chrome.scripting.executeScript({
      target: { tabId: sender.tab.id },
      world: "MAIN",
      func: installWhatsAppAudioHook
    }).then(() => sendResponse({ ok: true })).catch((error) => {
      sendResponse({ ok: false, error: error?.message || "Não consegui ativar a captura do player." });
    });
    return true;
  }

  if (!message || message.type !== "transcrevezap-transcribe") return false;

  (async () => {
    let file;
    if (message.audioBlob instanceof Blob) {
      const mimeType = message.audioBlob.type.startsWith("audio/")
        ? message.audioBlob.type.split(";")[0]
        : (message.mimeType || "audio/ogg").split(";")[0];
      file = new File([message.audioBlob], message.filename || `whatsapp-audio.${extensionForMime(mimeType)}`, { type: mimeType });
    } else if (message.audioBase64) {
      file = fileFromBase64(message.audioBase64, message.mimeType, message.filename);
    } else if (message.mediaUrl && isAllowedWhatsAppMediaUrl(message.mediaUrl)) {
      const mediaResponse = await fetch(message.mediaUrl, { credentials: "include" });
      if (!mediaResponse.ok) throw new Error("Não consegui baixar o áudio do WhatsApp. Tente reproduzi-lo e tente de novo.");
      const blob = await mediaResponse.blob();
      if (!blob.size) throw new Error("O WhatsApp ainda não carregou o áudio. Reproduza-o e tente novamente.");
      const mimeType = blob.type.startsWith("audio/") ? blob.type.split(";")[0] : "audio/ogg";
      file = new File([blob], message.filename || `whatsapp-audio.${extensionForMime(mimeType)}`, { type: mimeType });
    } else {
      throw new Error("A captura não chegou à extensão. Recarregue a extensão e feche e reabra a aba do WhatsApp Web.");
    }

    const text = await transcribe(file);
    return { ok: true, text };
  })().then(sendResponse).catch((error) => {
    sendResponse({ ok: false, error: error?.message || "Falha ao comunicar com o TranscreveZap." });
  });

  return true;
});
