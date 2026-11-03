(() => {
  let captureArmed = false;
  chrome.runtime.onMessage.addListener((message) => {
    if (message?.type === "transcrevezap-capture-ready") captureArmed = true;
  });

  async function captureAndTranscribeMessage(message) {
    if (!captureArmed) {
      throw new Error("Antes de transcrever, clique no ícone da extensão TranscreveZap para ativar a captura desta aba.");
    }
    const playSelector = [
      'span[data-icon="audio-play"]',
      '[data-testid*="audio-play"]',
      '[aria-label*="play voice message" i]',
      '[aria-label*="reproduzir mensagem de voz" i]',
      '[aria-label*="reproducir mensaje de voz" i]',
      '[aria-label*="voice message" i]'
    ].join(",");
    const pauseSelector = [
      'span[data-icon="audio-pause"]',
      '[data-testid*="audio-pause"]',
      '[aria-label*="pause voice message" i]',
      '[aria-label*="pausar mensagem de voz" i]'
    ].join(",");

    let playIcon = message.querySelector(playSelector);
    const pauseIcon = message.querySelector(pauseSelector);
    if (!playIcon && pauseIcon) {
      const pauseButton = pauseIcon.closest("button,[role='button']") || pauseIcon;
      pauseButton.click();
      await new Promise((resolve) => requestAnimationFrame(resolve));
      const progress = message.querySelector('input[type="range"]');
      if (progress) {
        const valueSetter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value")?.set;
        if (valueSetter) valueSetter.call(progress, "0");
        progress.dispatchEvent(new Event("input", { bubbles: true }));
        progress.dispatchEvent(new Event("change", { bubbles: true }));
      }
      playIcon = message.querySelector(playSelector);
    }

    const playButton = playIcon?.closest("button,[role='button']") || playIcon;
    if (!playButton) throw new Error("Não encontrei o botão de reprodução desta mensagem de voz.");

    const started = await chrome.runtime.sendMessage({ type: "transcrevezap-start-tab-audio" });
    if (!started?.ok) throw new Error(started?.error || "Não foi possível iniciar a captura do som da aba.");
    playButton.click();
    const playback = await new Promise((resolve, reject) => {
      let hasPlayed = false;
      let quietSince = 0;
      const deadline = Date.now() + 10 * 60 * 1000;
      const pauseSelector = 'span[data-icon="audio-pause"], [data-testid*="audio-pause"], [aria-label*="pause voice message" i], [aria-label*="pausar mensagem de voz" i]';
      const timer = setInterval(() => {
        const playing = Boolean(message.querySelector(pauseSelector));
        if (playing) {
          hasPlayed = true;
          quietSince = 0;
        } else if (hasPlayed) {
          if (!quietSince) quietSince = Date.now();
          if (Date.now() - quietSince > 1200) {
            clearInterval(timer);
            resolve(true);
          }
        }
        if (Date.now() > deadline) {
          clearInterval(timer);
          reject(new Error("A reprodução não terminou dentro do limite de 10 minutos."));
        }
      }, 250);
      setTimeout(() => {
        if (!hasPlayed) {
          clearInterval(timer);
          reject(new Error("Não detectei a reprodução. Deixe esta mensagem de voz terminar e tente novamente."));
        }
      }, 30000);
    });
    if (!playback) throw new Error("Não foi possível capturar o áudio da aba.");
    const stopped = await chrome.runtime.sendMessage({ type: "transcrevezap-stop-tab-audio" });
    if (!stopped?.ok) throw new Error(stopped?.error || "A captura terminou, mas não consegui enviar o áudio para transcrição.");
    return stopped.text || "Nenhuma fala foi reconhecida neste áudio.";
  }

  const VOICE_SIGNAL_SELECTOR = [
    '[data-icon="ptt-status"]',
    '[aria-label*="voice message" i]',
    '[aria-label*="mensagem de voz" i]',
    '[aria-label*="mensaje de voz" i]',
    '[aria-label*="message vocal" i]'
  ].join(",");

  function removeOldControls() {
    document.querySelectorAll(
      "[data-transcrevezap-control], [data-transcrevezap-floating], [data-transcrevezap-message-control]"
    ).forEach((control) => control.remove());
  }

  function locateMessage(signal) {
    const container = signal.closest('[data-testid="msg-container"]');
    if (container) return container;
    const conversationMessage = signal.closest('[data-testid^="conv-msg-"]');
    if (conversationMessage) return conversationMessage.querySelector('[data-testid="msg-container"]') || conversationMessage;
    return signal.closest(".focusable-list-item") ||
      signal.closest(".message-in, .message-out") ||
      signal.closest('[role="row"]') ||
      signal.closest("[data-id]") ||
      signal.parentElement?.parentElement?.parentElement ||
      signal.parentElement;
  }

  function makeMessageControl(message) {
    if (!message || message.querySelector("[data-transcrevezap-message-control]")) return;
    const host = document.createElement("div");
    host.setAttribute("data-transcrevezap-message-control", "true");
    host.style.cssText = "display:block;clear:both;margin:6px 0 2px;position:relative;z-index:2;";
    const shadow = host.attachShadow({ mode: "open" });
    shadow.innerHTML = `
      <style>
        :host{display:block;font:12px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif;color:#26352b}
        .controls{display:flex;flex-direction:column;align-items:flex-start;gap:6px;max-width:min(360px,78vw)}
        button{border:1px solid #168451;border-radius:999px;background:#fff;color:#126b40;padding:6px 12px;font:650 12px system-ui,-apple-system,"Segoe UI",sans-serif;cursor:pointer;box-shadow:0 1px 3px #00000012}
        button:hover{background:#eff9f2}button:disabled{opacity:.65;cursor:wait}
        .hint{color:#758078;font-size:11px}.output{display:none;max-height:220px;overflow:auto;white-space:pre-wrap;overflow-wrap:anywhere;padding:9px 11px;border:1px solid #dce9df;border-radius:10px;background:#fff;color:#26352b}
        .output.visible{display:block}.output.error{color:#a73531;border-color:#edcfcc}input{display:none}
      </style>
      <div class="controls">
        <button type="button">Transcrever</button>
        <span class="hint"></span>
        <span class="output" role="status" aria-live="polite"></span>
      </div>
    `;
    const button = shadow.querySelector("button");
    const hint = shadow.querySelector(".hint");
    const output = shadow.querySelector(".output");

    button.addEventListener("click", async () => {
      button.disabled = true;
      button.textContent = "Lendo áudio do WhatsApp…";
      hint.textContent = "Capturando o som desta aba enquanto a mensagem toca. Ela pode ser marcada como ouvida.";
      output.className = "output visible";
      output.textContent = "Reproduza o áudio até o fim para capturá-lo…";
      try {
        output.textContent = await captureAndTranscribeMessage(message);
        output.className = "output visible";
        button.textContent = "Transcrito ✓";
        button.disabled = false;
        hint.textContent = "";
      } catch (error) {
        chrome.runtime.sendMessage({ type: "transcrevezap-stop-tab-audio" }).catch(() => {});
        output.className = "output visible error";
        output.textContent = error?.message || "Não foi possível capturar o áudio da aba.";
        button.textContent = "Tentar novamente";
        button.disabled = false;
      }
    });
    message.append(host);
  }

  function scanForVoiceMessages() {
    for (const signal of document.querySelectorAll(VOICE_SIGNAL_SELECTOR)) {
      const message = locateMessage(signal);
      if (message) makeMessageControl(message);
    }
  }

  let scanTimer;
  const observer = new MutationObserver(() => {
    clearTimeout(scanTimer);
    scanTimer = setTimeout(() => {
      scanForVoiceMessages();
    }, 250);
  });

  function start() {
    removeOldControls();
    scanForVoiceMessages();
    observer.observe(document.body, { childList: true, subtree: true });
  }

  if (document.body) start();
  else document.addEventListener("DOMContentLoaded", start, { once: true });
})();
