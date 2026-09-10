import os
import time
import requests
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "").strip()

openai_client = OpenAI(api_key=OPENAI_API_KEY)
URL_BASE = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

print("📌 Bot Pré-Live Ativo com Motor de Legenda Direta Telegram!")

class WebServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Bot is running successfully!")
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

def iniciar_servidor_web():
    port = int(os.getenv("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), WebServerHandler)
    print(f"🌍 Servidor Web de suporte ativo na porta {port}")
    server.serve_forever()

def limpar_fila_telegram():
    print("🧹 Limpando mensagens antigas travadas na fila do Telegram...")
    try:
        url = f"{URL_BASE}/getUpdates?offset=-1"
        requests.get(url, timeout=10)
        print("✅ Fila do Telegram limpa com sucesso!")
    except Exception as e:
        print(f"Erro ao limpar fila: {e}")

def buscar_atualizacoes(offset=None):
    url = f"{URL_BASE}/getUpdates?timeout=30"
    if offset:
        url += f"&offset={offset}"
    try:
        response = requests.get(url, timeout=35)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Erro ao buscar atualizações: {e}")
    return None

def enviar_mensagem(chat_id, texto):
    url = f"{URL_BASE}/sendMessage"
    payload = {"chat_id": chat_id, "text": texto, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

def processar_foto(chat_id, legenda_texto):
    try:
        enviar_mensagem(chat_id, "📸 Print recebido! Processando dados fornecidos na legenda e gerando palpite estruturado de valor...")

        # Caso o usuário envie o print totalmente sem legenda, o bot cria um jogo dinâmico para não falhar
        if not legenda_texto or len(legenda_texto.strip()) < 3:
            legenda_texto = "Confronto importante do dia na Série A"

        prompt_sistema = (
            Você é um analista estatístico e tipster profissional sênior especializado nas modalidades de Futebol, Basquete e Tênis pré-live.
Sua tarefa é analisar TODOS os confrontos enviados pelo usuário (sejam 1 ou 20+ jogos), gerar as análises técnicas individuais e estruturar uma matriz completa de Bilhetes (Simples, Duplas e Triplas) sem repetição de confrontos nos bilhetes combinados.

REGRAS DE PROCESSAMENTO E ANÁLISE COMPUTAÇÃO:

1. PROCESSAMENTO COMPLETO DE LOTE:
   - Analise 100% dos jogos enviados pelo usuário na legenda, sem ignorar nenhum confronto relevante.
   - Para cada jogo, aplique os mercados de valor específicos da modalidade:
     * Futebol: Cantos Asiáticos, Handicap Asiático de Gols, Ambas Marcam (BTTS) ou DNB.
     * Basquete: Handicaps de Pontos, Totais Over/Under (Geral/Quartos) ou PRA (Pontos/Rebotes/Assistências).
     * Tênis: Handicap de Games, Total de Games Over/Under, Handicap de Sets ou Vencedor do 1º Set.

2. METODOLOGIA ESTATÍSTICA E TÁTICA DA ANÁLISE PRINCIPAL:
   - Para cada partida do lote, gere uma justificativa densa de 2 a 3 linhas simulando dados avançados reais (Futebol: xG, Pressionamento; Basquete: Pace, OffRtg/DefRtg; Tênis: 1º Serviço, Break Points e Piso).

3. REGRA ESTRITA DE MONTAGEM DOS BILHETES COMBINADOS:
   - REGRA DE OURO: É ESTRITAMENTE PROIBIDO repetir o mesmo time/atleta dentro de um mesmo bilhete duplo ou triplo.
   - Distribua os jogos fornecidos criando o máximo possível de Bilhetes Simples, Bilhetes Duplos e Bilhetes Triplos distintos.
   - Se o usuário enviar muitos jogos (ex: 10 jogos), monte MÚLTIPLAS Duplas e MÚLTIPLAS Triplas utilizando combinatórias com times diferentes para diversificar a banca.

4. FORMATO DE SAÍDA (Publicação Direta no Canal VIP):
   - Utilize a estrutura exata abaixo, sem saudações, introduções ou conversas paralelas.

--- ESTRUTURA DA SAÍDA ---

🚨 **ANÁLISES TÉCNICAS DA RODADA** 🚨

[REPETIR O BLOCO ABAIXO PARA CADA JOGO ENVIADO]
🏆 **Evento:** [Campeonato] | ⚔️ **Confronto:** [Time A vs Time B]
📌 **Mercado:** [Mercado Selecionado] ➔ **Palpite:** [Entrada Exata] (@[Odd Mínima])
📊 **Análise Técnica:** [2 a 3 linhas com dados de xG/Pace/Serviço e leitura tática]
💰 **Stake:** [1% ou 2%] | **Confiança:** [Ex: 8/10]
--------------------------------------------------

🎫 **CARDS DE ENTRADAS VIP (PRONTO PARA COPIAR)** 🎫

📌 **ENTRADAS SIMPLES**
[Listar cada jogo com entrada direta e odd]
⚽/🏀/🎾 [Time A] vs [Time B] ➔ [Entrada Exata] | Odd Mínima: @[Odd]
⚽/🏀/🎾 [Time C] vs [Time D] ➔ [Entrada Exata] | Odd Mínima: @[Odd]
(...)

---

🧩 **BILHETES DUPLOS DA RODADA (SEM REPETIÇÃO DE TIMES)**

🔹 **DUPLA 1**
1️⃣ [Time A] vs [Time B] ➔ [Entrada Exata]
2️⃣ [Time C] vs [Time D] ➔ [Entrada Exata]
🔥 **Odd Total Estimada:** @[ Odd ] | **Stake:** 1%

🔹 **DUPLA 2**
1️⃣ [Time E] vs [Time F] ➔ [Entrada Exata]
2️⃣ [Time G] vs [Time H] ➔ [Entrada Exata]
🔥 **Odd Total Estimada:** @[ Odd ] | **Stake:** 1%
(...) [Criar mais duplas se houver jogos suficientes]

---

🚀 **BILHETES TRIPLOS ALTO VALOR (+EV) (SEM REPETIÇÃO DE TIMES)**

🔥 **TRIPLA 1**
1️⃣ [Time A] vs [Time B] ➔ [Entrada Exata]
2️⃣ [Time E] vs [Time F] ➔ [Entrada Exata]
3️⃣ [Time I] vs [Time J] ➔ [Entrada Exata]
🚀 **Odd Total Estimada:** @[ Odd ] | **Stake:** 0.5% a 1%

🔥 **TRIPLA 2**
1️⃣ [Time C] vs [Time D] ➔ [Entrada Exata]
2️⃣ [Time G] vs [Time H] ➔ [Entrada Exata]
3️⃣ [Time K] vs [Time L] ➔ [Entrada Exata]
🚀 **Odd Total Estimada:** @[ Odd ] | **Stake:** 0.5% a 1%
(...) [Criar mais triplas utilizando combinações limpas sem repetir confrontos na mesma aposta]
        )

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": f"Formule o palpite profissional avançado focado em mercados alternativos para este confronto: {legenda_texto}"}
            ],
            temperature=0.8
        )

        # CORREÇÃO CRUCIAL DA API AQUI: Adicionado [0] para extrair corretamente da lista
        analise_final = response.choices[0].message.content
        
        enviar_mensagem(CHANNEL_ID, analise_final)
        enviar_mensagem(chat_id, "✅ Palpite gerado dinamicamente e publicado no canal com sucesso!")

    except Exception as e:
        print(f"Erro na OpenAI: {str(e)}")
        enviar_mensagem(chat_id, f"❌ Erro de processamento na API: {str(e)}")

def executar_bot():
    last_update_id = None
    while True:
        updates = buscar_atualizacoes(last_update_id)
        if updates and updates.get("ok"):
            for update in updates["result"]:
                last_update_id = update["update_id"] + 1

                if "message" in update and update["message"]["chat"]["type"] == "private":
                    message = update["message"]
                    chat_id = message["chat"]["id"]

                    if "photo" in message:
                        # Resgata o texto digitado na legenda da foto pelo usuário
                        legenda = message.get("caption", "")
                        processar_foto(chat_id, legenda)
        time.sleep(1)

if __name__ == '__main__':
    limpar_fila_telegram()
    t = threading.Thread(target=iniciar_servidor_web, daemon=True)
    t.start()
    executar_bot()
