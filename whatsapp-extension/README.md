# Extensão do TranscreveZap para WhatsApp Web

A extensão adiciona **um botão Transcrever somente às mensagens de voz** gravadas no WhatsApp Web. Para contornar o bloqueio do arquivo interno pelo WhatsApp, a extensão grava o som reproduzido na aba, durante a reprodução da mensagem, e envia a gravação ao TranscreveZap em `http://127.0.0.1:5000`.

## Instalar no Chrome ou Edge

1. Deixe o Docker do TranscreveZap ligado neste mesmo computador.
2. Abra `chrome://extensions` (Chrome) ou `edge://extensions` (Edge).
3. Ative **Modo do desenvolvedor**.
4. Clique em **Carregar sem compactação** e selecione esta pasta `whatsapp-extension`.
5. Abra ou atualize `https://web.whatsapp.com`.
6. Depois de recarregar a extensão, feche todas as abas do WhatsApp Web e abra `https://web.whatsapp.com` novamente.
7. Se o ícone não estiver visível, fixe o TranscreveZap no menu de extensões do Chrome/Edge.
8. Clique no ícone da extensão com o WhatsApp Web aberto. O selo verde **ON** confirma que a captura da aba foi ativada.
9. Clique em **Transcrever** abaixo da mensagem de voz e deixe a reprodução terminar. Arquivos de áudio enviados como anexo não recebem o botão.

## Observações

- Esta extensão funciona no WhatsApp Web em navegadores Chromium (Chrome e Edge), no mesmo computador onde o TranscreveZap está rodando.
- A gravação captura o som da aba durante a reprodução; o áudio continua audível. Evite reproduzir outros sons na aba durante esse período.
- A integração é para o WhatsApp Web no navegador; ela não aparece no aplicativo nativo do WhatsApp para Windows.
- Limite: 100 MB por áudio, igual ao app.
- Para usar com uma versão hospedada na nuvem ou em outro computador, será preciso trocar o endereço do servidor e permitir a origem dessa extensão com HTTPS.

## Privacidade e LGPD na Extensão

A extensão opera sob o princípio da menor invasividade:
- Não lê mensagens de texto, contatos, fotos de perfil ou status da sua conta de WhatsApp.
- A captura de áudio da aba só acontece quando você clica deliberadamente no botão de transcrição de uma mensagem.
- O áudio capturado é processado exclusivamente para a conversão de voz em texto, sem identificação biométrica ou armazenamento permanente no servidor.
- Em conformidade integral com a LGPD (Lei nº 13.709/2018). Veja a [Política de Privacidade](../POLITICA_DE_PRIVACIDADE.md).
