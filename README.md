# TranscreveZap

Aplicativo local para enviar áudios do WhatsApp e receber a transcrição em texto usando IA. É necessária uma chave de API. A chave fica no servidor, não no navegador.

## Como iniciar no Windows

1. Instale Python 3.10 ou mais recente.
2. Abra o PowerShell nesta pasta e execute:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:API_KEY="sua-chave-da-api"
python app.py
```

3. Acesse http://127.0.0.1:5000.
4. No WhatsApp, salve/compartilhe o áudio para o computador e selecione o arquivo no app. Formatos `.opus`, `.ogg`, `.m4a`, `.mp3`, `.wav` e outros formatos comuns são aceitos; limite de 100 MB.

Para encerrar, pressione Ctrl+C no PowerShell. A chave é mantida apenas na variável de ambiente daquela janela. Gere uma chave no [Google AI Studio](https://aistudio.google.com/apikey).

## Como iniciar com Docker

Com o Docker Desktop aberto, execute nesta pasta:

```powershell
docker compose up -d --build
```

O Compose lê a chave do arquivo `../.ev/API.txt` e monta esse arquivo como segredo dentro do contêiner; a chave não entra na imagem. As transcrições ficam no volume persistente `transcrevezap_data`, junto com nome do áudio e data, sem guardar o áudio. Acesse http://127.0.0.1:5000. Para parar o app, execute `docker compose down`. O volume persiste após reiniciar o contêiner; não use `docker compose down -v` se quiser conservar o histórico.

O contêiner usa a variável `PORT` para aceitar a porta fornecida pelo provedor ao hospedar em nuvem.

## Extensão para WhatsApp Web

Para adicionar os controles de transcrição ao WhatsApp Web, carregue sem compactação a pasta `whatsapp-extension` em `chrome://extensions` ou `edge://extensions`. O Docker do TranscreveZap precisa estar ligado no mesmo computador. Consulte o [guia da extensão](whatsapp-extension/README.md) para os passos e limitações.

## Privacidade e Conformidade LGPD

O TranscreveZap foi desenvolvido com arquitetura de **Privacidade por Design e Retenção Zero**:
- **Zero Retenção de Áudio:** Nenhum áudio enviado é mantido em banco de dados permanente no servidor. O processamento é estritamente volátil (memória RAM / arquivos temporários destruídos imediatamente após o envio).
- **Sem Biometria Vocal:** Apenas conversão acústico-fonética de voz para texto (speech-to-text). Não há reconhecimento facial, geração de *voiceprints* ou identificação biométrica de falantes.
- **Histórico 100% Local:** As transcrições residem com exclusividade no `localStorage` do navegador do usuário, com exclusão sob demanda a qualquer momento.
- **Conformidade Legal:** Total alinhamento aos Artigos 6º, 7º, 9º, 11, 18, 33, 41, 43 e 46 da **LGPD (Lei nº 13.709/2018)**.
- Consulte a documentação completa em [POLITICA_DE_PRIVACIDADE.md](POLITICA_DE_PRIVACIDADE.md) ou pela rota `/privacidade` no navegador.
