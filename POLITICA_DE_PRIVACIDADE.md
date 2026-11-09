# Política de Privacidade e Proteção de Dados Pessoais (LGPD)
**TranscreveZap — Transcrição Inteligente de Áudios**

*Última atualização: Novembro de 2026*  
*Em total conformidade com a Lei Geral de Proteção de Dados Pessoais (Lei Federal nº 13.709/2018 — LGPD), com o Marco Civil da Internet (Lei nº 12.965/2014) e com os regulamentos da Autoridade Nacional de Proteção de Dados (ANPD).*

---

## 1. APRESENTAÇÃO E COMPROMISSO COM A PRIVACIDADE

O **TranscreveZap** foi concebido sob os postulados mais rigorosos de **Privacidade por Design e por Padrão (*Privacy by Design and by Default*)**. A nossa prioridade absoluta é garantir a integridade, a confidencialidade e a autodeterminação informativa dos titulares de dados, eliminando riscos de vazamento e assegurando conformidade integral com a **Lei Geral de Proteção de Dados (Lei nº 13.709/2018 — LGPD)**.

Esta Política de Privacidade tem por objetivo esclarecer de forma transparente, clara, acessível e ostensiva (em observância ao **Art. 9º da LGPD**) como os dados são tratados no âmbito do sistema TranscreveZap (incluindo a aplicação web, API e a extensão de navegador para WhatsApp Web).

---

## 2. IDENTIFICAÇÃO DO CONTROLADOR E DISPENSA LEGAL DE DPO (RESOLUÇÃO CD/ANPD Nº 2/2022)

Nos termos do **Art. 5º, VI da LGPD** e do **Art. 11 da Resolução CD/ANPD nº 2/2022**:

- **Controlador do Projeto / Desenvolvedor:** Brayan Fortes (Mantenedor do TranscreveZap).
- **Dispensa Legal de Indicação de Encarregado (DPO):** Por se enquadrar como pessoa natural / desenvolvedor independente e agente de tratamento de pequeno porte (Art. 2º, I da Resolução CD/ANPD nº 2/2022), o responsável está **legalmente dispensado da obrigatoriedade de indicar um Encarregado pelo Tratamento de Dados Pessoais (DPO)** (Art. 11 da Resolução c/c Art. 41 da LGPD).
- **Canal Direto de Comunicação com os Titulares (Art. 11, § 1º da Resolução):**
  - Repositório oficial e suporte no GitHub: [github.com/BrayanFortes/TranscreveZap/issues](https://github.com/BrayanFortes/TranscreveZap/issues)
- **Prazos em Dobro para Agentes de Pequeno Porte:** Conforme o **Art. 14 da Resolução CD/ANPD nº 2/2022**, os prazos de resposta a solicitações dos titulares de dados e envio de declarações são computados em dobro (em até 30 dias para declaração completa).

> **Nota para implantações locais/auto-hospedadas (Self-Hosted):** Quando o usuário executa o TranscreveZap em seu próprio computador ou servidor local (via Python/Docker) utilizando sua própria chave de API privada, o próprio usuário atua como o único e exclusivo Controlador e Operador do seu ambiente local, não havendo qualquer envio de dados para servidores centrais do TranscreveZap.

---

## 3. ARQUITETURA DE RETENÇÃO ZERO (PRIVACY BY DESIGN)

A proteção de dados no TranscreveZap baseia-se na **minimização extrema e na retenção transitória**:

1. **Zero Retenção de Áudio no Servidor:** Os arquivos de áudio enviados para transcrição **NÃO são armazenados de forma permanente em nenhum banco de dados**.
2. **Processamento em Memória e Descarte Imediato:**
   - Áudios de tamanho reduzido são processados diretamente na memória volátil (RAM) e descartados imediatamente após a geração do texto.
   - Arquivos maiores que exigem criação de arquivo temporário utilizam áreas temporárias isoladas do sistema operacional e são **destruídos e desvinculados do disco imediatamente** após o envio ao motor de inteligência artificial.
3. **Histórico 100% sob Controle do Usuário (*Client-Side Storage*):** O histórico de transcrições anteriores não fica salvo em servidores do TranscreveZap. Ele é armazenado com exclusividade no armazenamento local do navegador do próprio usuário (`localStorage`). O usuário tem a faculdade de consultar, exportar ou apagar esse histórico instantaneamente a qualquer momento, sem necessidade de intervenção de terceiros.

---

## 4. INVENTÁRIO DE DADOS TRATADOS E NÃO TRATADOS

Para dar total transparência aos titulares de dados (**Art. 6º, VI da LGPD**):

### 4.1. Dados que Tratamos
| Dado Pessoal | Categoria | Finalidade | Base Legal (LGPD) | Período de Retenção |
| :--- | :--- | :--- | :--- | :--- |
| **Arquivo de Voz / Áudio** (.opus, .ogg, .mp3, etc.) | Dado Transitório de Comunicação | Conversão fonética em texto (transcrição do conteúdo audível a pedido do titular) | Execução de Contrato / Prestação de Serviço (Art. 7º, V) e Consentimento (Art. 7º, I) | **Tempo estrito da requisição** (segundos). Nenhum áudio é mantido após a resposta. |
| **Endereço IP e Cabeçalhos Técnicos** | Dado de Conexão / Rede | Aplicação de controle de taxa (*rate limiting*), mitigação de ataques DDoS, prevenção a fraudes e garantia da estabilidade do serviço | Cumprimento de Obrigação Legal (Marco Civil da Internet, Art. 15) e Legítimo Interesse (LGPD, Art. 7º, IX) | Retido apenas em memória volátil (*sliding window* de 60 segundos). Descarte contínuo. |
| **Texto da Transcrição** | Conteúdo Resultante | Exibição na tela para o usuário e gravação no dispositivo local | Execução de Contrato / Prestação de Serviço (Art. 7º, V) | Salvo exclusivamente no `localStorage` do dispositivo do usuário. Retido até que o próprio usuário decida limpar. |

### 4.2. Dados que NÃO Coletamos e NÃO Tratamos
- **NÃO coletamos dados cadastrais intrusivos:** Não solicitamos CPF, RG, endereço residencial, profissão ou dados de cartão de crédito para a transcrição básica.
- **NÃO realizamos perfilamento comportamental (*profiling*):** Não traçamos perfis psicológicos, hábitos de consumo ou rastreamento entre sites (*cross-site tracking*).
- **NÃO utilizamos cookies de terceiros para publicidade:** O TranscreveZap não emprega *tracking pixels*, cookies de marketing ou redes de anunciantes.

---

## 5. DISTINÇÃO FUNDAMENTAL: TRANSCRIÇÃO FONÉTICA vs. BIOMETRIA VOCAL (ART. 5º, II E ART. 11 DA LGPD)

Em atendimento estrito às diretrizes da ANPD e da doutrina de proteção de dados:

- **Não há Identificação Biométrica:** A transcrição executada pelo TranscreveZap é um procedimento acústico-fonético estrito (*speech-to-text*). O algoritmo analisa a frequência e a amplitude das ondas sonoras exclusivamente para decodificar palavras faladas no idioma português e convertê-las em caracteres ortográficos.
- **Ausência de *Voiceprints*:** Não são criadas assinaturas vocais biométricas, mapas faciais ou laríngeos, nem é feita qualquer tentativa de identificar quem é o indivíduo titular da voz.
- **Dados Sensíveis Incidentais:** Caso o emissor do áudio fale sobre temas protegidos pelo **Art. 11 da LGPD** (tais como saúde, convicção religiosa ou filiação partidária), o processamento ocorre por solicitação direta e expressa do próprio usuário destinatário da comunicação, com fundamento na estrita execução do serviço de transcrição (Art. 7º, V e Art. 11, II, "g" da LGPD).

---

## 6. COMPARTILHAMENTO DE DADOS COM TERCEIROS E OPERADORES

Em observância ao **Art. 9º, V e Art. 39 da LGPD**, declaramos expressamente que os dados são compartilhados exclusivamente com os seguintes agentes de tratamento essenciais para a operacionalização do serviço:

1. **Google LLC (Google Cloud / Google AI Studio — API Gemini):**
   - **Papel:** Operador de Processamento de Inteligência Artificial.
   - **Finalidade:** Processamento dos pacotes de áudio para geração do texto da transcrição.
   - **Compromisso de Segurança:** A Google adquire os pacotes sob conexões cifradas (TLS 1.3/HTTPS). Conforme os termos corporativos da API, os áudios trafegados via API não são utilizados para treinamento de modelos públicos e são descartados conforme os padrões de privacidade corporativa da provedora.
2. **Provedores de Nuvem e CDN (ex.: Vercel Inc. / Provedores de Hospedagem):**
   - **Papel:** Operadores de Infraestrutura e Redes.
   - **Finalidade:** Hospedagem da aplicação, distribuição segura de conteúdo estático e aplicação de filtros de proteção perimetral (Web Application Firewall).

> **Garantia de Não Comercialização:** O TranscreveZap **JAMAIS vende, aluga, licencia ou cede dados pessoais, arquivos de voz ou transcrições** para corretores de dados (*data brokers*), birôs de crédito ou agências de publicidade.

---

## 7. TRANSFERÊNCIA INTERNACIONAL DE DADOS (ART. 33 DA LGPD)

Considerando que as empresas de tecnologia parceiras (como Google LLC e Vercel Inc.) possuem data centers e infraestruturas distribuídas globalmente (inclusive nos Estados Unidos da América):

- O tratamento pode envolver a **transferência internacional de dados pessoais**, estritamente necessária para a execução do processamento de inteligência artificial.
- Tal transferência está devidamente amparada pelo **Art. 33, II e IX da LGPD** e pela **Resolução CD/ANPD nº 19/2024**, ocorrendo sob compromisso de salvaguardas contratuais robustas, certificações de segurança internacionais (como ISO/IEC 27001 e SOC 2/3) e criptografia em trânsito de ponta a ponta.

---

## 8. MEDIDAS DE SEGURANÇA TÉCNICAS E ADMINISTRATIVAS (ART. 46 E 47 DA LGPD)

Para proteger os dados contra acessos não autorizados, incidentes de segurança, destruição ou alteração ilícita, o TranscreveZap implementa salvaguardas técnicas em múltiplas camadas (*defense-in-depth*):

1. **Criptografia em Trânsito:** Todo o tráfego de dados entre o navegador do usuário, o servidor e a API de IA ocorre sob canais criptográficos seguros via protocolo HTTPS com cifras TLS modernas.
2. **Rate Limiting em Camada de Aplicação:** Mecanismo ativo de limitação de requisições por janela deslizante (*Sliding Window Rate Limiter*) que previne ataques automatizados, abusos e negações de serviço (DDoS).
3. **Cabeçalhos de Segurança HTTP Rígidos:**
   - `Content-Security-Policy (CSP)` restrito, bloqueando injeção de scripts e recursos maliciosos.
   - `X-Content-Type-Options: nosniff` para impedir ataques de MIME-sniffing.
   - `X-Frame-Options: DENY` para mitigar ataques de clickjacking.
   - `Referrer-Policy: strict-origin-when-cross-origin` para proteção de metadados de navegação.
   - `Permissions-Policy: microphone=(self)` para impedir o uso clandestino de microfones por terceiros.
4. **Isolamento de Origem (CORS Restrito):** Acesso às rotas de transcrição estritamente delimitado a origens confiáveis e validadas por expressão regular (incluindo o cliente web e a extensão oficial).
5. **Defesa contra Injeção de Prompt (*Anti-Prompt Injection*):** Instruções de sistema fonéticas blindadas para impedir que comandos contidos em áudios fraudulentos manipulem o comportamento do sistema.

---

## 9. DIREITOS DOS TITULARES DE DADOS E COMO EXERCÊ-LOS (ART. 18 DA LGPD)

O titular dos dados pessoais tem direito a obter do TranscreveZap, a qualquer momento e mediante requisição facilitada e gratuita:

1. **Confirmação da existência de tratamento** (Art. 18, I);
2. **Acesso aos dados tratados** (Art. 18, II);
3. **Correção de dados incompletos, inexatos ou desatualizados** (Art. 18, III);
4. **Anonimização, bloqueio ou eliminação de dados desnecessários, excessivos ou tratados em desconformidade** (Art. 18, IV);
5. **Portabilidade dos dados** (Art. 18, V) — garantida pela possibilidade de exportar suas transcrições em formato `.txt` direto na interface;
6. **Eliminação dos dados pessoais tratados com o consentimento** (Art. 18, VI) — garantida imediatamente pelo botão **"Limpar Histórico"** disponível no aplicativo, que remove instantaneamente todos os registros da memória do navegador;
7. **Informação sobre entidades públicas e privadas com as quais se realizou uso compartilhado** (Art. 18, VII);
8. **Informação sobre a possibilidade de não fornecer consentimento e sobre as consequências da negativa** (Art. 18, VIII);
9. **Revogação do consentimento** (Art. 18, IX).

### Como Exercer os seus Direitos:
- **Exclusão de Registros Locais:** Clique no botão de lixeira individual ou no botão *"Limpar Histórico"* no painel do TranscreveZap. Essa ação expurga de forma irreversível os textos gravados no seu dispositivo.
- **Canal Direto de Atendimento ao Titular:** Abra uma manifestação diretamente no repositório oficial no GitHub ([Aba Issues](https://github.com/BrayanFortes/TranscreveZap/issues)). A resposta será providenciada nos prazos regulamentares da ANPD.

---

## 10. RESPONSABILIDADE DO USUÁRIO SOBRE ÁUDIOS DE TERCEIROS E EXCLUDENTES DE RESPONSABILIDADE (ART. 43 DA LGPD)

### 10.1. Garantia de Licitude pelo Usuário
Ao submeter arquivos de áudio (sejam gravações próprias ou mensagens encaminhadas do aplicativo WhatsApp), **o Usuário declara e garante expressamente que:**
1. É o legítimo destinatário ou emissor da mensagem de voz, possuindo autorização legal, consentimento tácito ou interesse legítimo para transcrever a conversa para leitura própria;
2. O áudio não foi obtido por meios ilícitos, tais como grampo ilegal, interceptação não autorizada, furto de dispositivo ou quebra de segredo de justiça e sigilo profissional;
3. Não utilizará a transcrição gerada para fins ilícitos, difamatórios, fraudulentos ou discriminatórios.

### 10.2. Excludentes de Ilicitude e Responsabilidade do Controlador
Nos exatos termos do **Art. 43 da Lei nº 13.709/2018**, o TranscreveZap **não será responsabilizado quando demonstrar que:**
- Não realizou o tratamento de dados pessoais alegado;
- Não houve qualquer violação à legislação de proteção de dados na operação de seus sistemas;
- **O dano ou eventual infração for decorrente de culpa exclusiva do titular dos dados ou de terceiro (Art. 43, III da LGPD)**, incluindo o compartilhamento indevido de áudios alheios sem justa causa por parte do usuário, ou a falta de zelo na proteção de senhas e dispositivos pessoais por parte do usuário.

---

## 11. REGRAS ESPECÍFICAS DA EXTENSÃO PARA WHATSAPP WEB

A extensão de navegador oficial do TranscreveZap foi desenvolvida para operar sob o princípio do menor privilégio:

1. **Permissões Mínimas (`manifest.json`):**
   - `tabCapture`: Utilizada única e exclusivamente para capturar o fluxo de áudio quando o usuário clica expressamente no botão de transcrição de uma mensagem de voz.
   - `offscreen`: Utilizada para processar a codificação de áudio em segundo plano no navegador sem travar a interface.
   - `scripting`: Utilizada para injetar os controles de interface diretamente ao lado das mensagens de áudio na página do WhatsApp Web.
2. **Não Invasão da Privacidade do WhatsApp:**
   - A extensão **NÃO lê, não armazena e não transmite textos de conversas, lista de contatos, fotos de perfil ou status do WhatsApp**.
   - O áudio só é interceptado após **ação voluntária e explícita do usuário** ao acionar a funcionalidade de transcrição.

---

## 12. NOTIFICAÇÃO DE INCIDENTES DE SEGURANÇA (ART. 48 DA LGPD)

Em consonância com o **Art. 48 da LGPD** e com a **Resolução CD/ANPD nº 15/2024**, caso ocorra qualquer incidente de segurança com dados pessoais que possa acarretar risco ou dano relevante aos titulares:
1. O TranscreveZap comunicará a ocorrência à **Autoridade Nacional de Proteção de Dados (ANPD)** e aos titulares afetados em prazo razoável;
2. A comunicação conterá a descrição da natureza dos dados afetados, as medidas técnicas de proteção empregadas, os riscos identificados e as medidas corretivas adotadas para reverter ou mitigar os efeitos do evento.

---

## 13. CONFORMIDADE COM RESOLUÇÕES DA ANPD E PREVENÇÃO DE MULTAS (ART. 52 DA LGPD)

Este documento e as práticas de engenharia de software do TranscreveZap foram elaborados para neutralizar integralmente as hipóteses geradoras de sanções administrativas e multas pecuniárias (Art. 52 da LGPD e **Resolução CD/ANPD nº 4/2023 - Regulamento de Dosimetria**):

1. **Inexistência de Reincidência e Boa-Fé Comprovada:** O sistema adota medidas transparentes e pró-ativas desde a sua concepção.
2. **Minimização Total de Riscos:** Como não mantemos repositório central de áudios nem banco de dados de mensagens, o vetor de exposição a vazamentos massivos de dados é tecnicamente mitigado na raiz da arquitetura.
3. **Agentes de Tratamento de Pequeno Porte (Resolução CD/ANPD nº 2/2022):** Para instâncias qualificadas como startups ou agentes de pequeno porte, são aplicados os critérios de simplificação regulatória e mitigação de ônus administrativos previstos pela autoridade fiscalizatória, sem prejuízo da proteção irrestrita dos direitos dos titulares.

---

## 14. ALTERAÇÕES DESTA POLÍTICA DE PRIVACIDADE

O TranscreveZap reserva-se o direito de atualizar esta Política de Privacidade a qualquer tempo, visando refletir melhorias no sistema, novas funcionalidades ou atualizações regulatórias da ANPD.
- Qualquer alteração substancial será informada com destaque na página inicial da aplicação web.
- A continuidade do uso do serviço após a publicação das alterações constituirá concordância com os novos termos.

---

## 15. LEGISLAÇÃO APLICÁVEL E FORO DE ELEIÇÃO

Esta Política de Privacidade é regida, interpretada e executada de acordo com as Leis da República Federativa do Brasil, em especial a **Lei nº 13.709/2018 (LGPD)** e a **Lei nº 12.965/2014 (Marco Civil da Internet)**.

Fica eleito o foro da comarca de domicílio do usuário no território nacional para dirimir quaisquer controvérsias decorrentes deste documento, ressalvadas as prerrogativas de competência da Autoridade Nacional de Proteção de Dados (ANPD).

---

*TranscreveZap — Tecnologia ética, rápida e que respeita a sua privacidade.*
