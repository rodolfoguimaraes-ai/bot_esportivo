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

print("📌 Bot Pré-Live Iniciado com Correção de Sintaxe da OpenAI!")

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

def processar_foto(chat_id, file_id):
    try:
        enviar_mensagem(chat_id, "📸 Print recebido! Analisando profundamente as equipes e buscando melhores mercados alternativos...")

        url_file = f"{URL_BASE}/getFile?file_id={file_id}"
        res_file = requests.get(url_file, timeout=10).json()

        if res_file.get("ok"):
            prompt_sistema = (
"Você é um analista estatístico e tipster esportivo profissional sênior especializado em análises pré-live.\n"
"Sua função é identificar os confrontos e formular VÁRIAS ENTRADAS (Simples, Duplas e Triplas) de altíssimo valor estatístico.\n\n"
"REGRAS DA ANÁLISE PROFISSIONAL:\n"
"1. Formule entradas em múltiplos formatos: Apostas Individuais (Simples), Combinações Duplas e Combinações Triplas.\n"
"2. Para cada jogo, analise e escolha os melhores mercados alternativos de alto valor estatístico:\n"
"   - Mercado Asiático (Handicap Asiático de Gols ou Linhas de proteção como AH 0.0 / DNB).\n"
"   - Escanteios / Cantos (Cantos Asiáticos de valor ou Over Cantos HT/FT).\n"
"   - Gols / Ambas Marcam (BTTS) explorando fragilidades defensivas e força nos ataques.\n"
"   - Cartões / Disciplinar (Over/Under de cartões por equipe ou partida).\n"
"3. Não se limite ao mercado tradicional de vitória (1X2).\n"
"4. Crie uma estrutura clara separando as sugestões em: ENTRADAS SIMPLES, DUPLAS RECOMENDADAS e TRIPLAS DE VALOR.\n"
"5. Estruture uma Justificativa técnica e estatística detalhada para cada seleção realizada.\n"
"6. Indique uma Gestão de Banca rigorosa (1% a 2% de stake por bilhete/simples) baseada no risco da operação.\n\n"
"Você deve ANALISAR OS MERCADOS POR CONTA PRÓPRIA buscando na internet e escolher aqueles que apresentarem maior consistência estatística.\n"
"NÃO espere que o usuário indique qual mercado deseja apostar.\n"
"NÃO espere que o print mostre os mercados.\n"
"Para cada confronto, analise possibilidades como:\n"
"   - Vitória do mandante.\n"
"   - Empate.\n"
"   - Vitória do visitante.\n"
"   - Dupla chance.\n"
"   - Draw No Bet.\n"
"   - Handicap Asiático.\n"
"   - Handicap Europeu.\n"
"   - Over/Under de gols.\n"
"   - Gols por equipe.\n"
"   - Ambas Marcam — BTTS.\n"
"   - Over/Under de escanteios.\n"
"   - Escanteios por equipe.\n"
"   - Handicap de escanteios.\n"
"   - Over/Under de cartões.\n"
"   - Cartões por equipe.\n"
"   - Outros mercados disponíveis que apresentem vantagem estatística.\n"
"Escolha o MELHOR MERCADO para cada jogo com base nos dados encontrados, mesmo que esse mercado não apareça no print.\n\n"
                "FORMATO OBRIGATÓRIO DA RESPOSTA:\n"
"A resposta DEVE COMEÇAR pelo CARD DE APOSTAS.\n"
"Não comece com explicações.\n"
"Não comece com estatísticas.\n"
"Não peça outro print.\n"
"Não diga que o print precisa conter mercados.\n"
"Primeiro apresente o resultado da pesquisa em formato de card.\n"
"Somente depois apresente as justificativas detalhadas.\n\n"

"🏆 CARD DE APOSTAS\n\n"

"🏆 MELHORES SIMPLES\n"
"[Jogo] — [Melhor mercado encontrado] — [Seleção] — Odd: [odd] — Confiança: [nível]\n"
"[Jogo] — [Melhor mercado encontrado] — [Seleção] — Odd: [odd] — Confiança: [nível]\n"
"[Jogo] — [Melhor mercado encontrado] — [Seleção] — Odd: [odd] — Confiança: [nível]\n"
"[Jogo] — [Melhor mercado encontrado] — [Seleção] — Odd: [odd] — Confiança: [nível]\n\n"

"🔥 MELHORES DUPLAS\n"
"DUPLA 01 — [Seleção] + [Seleção] — Odd combinada: [odd] — Confiança: [nível]\n"
"DUPLA 02 — [Seleção] + [Seleção] — Odd combinada: [odd] — Confiança: [nível]\n"
"DUPLA 03 — [Seleção] + [Seleção] — Odd combinada: [odd] — Confiança: [nível]\n"
"DUPLA 04 — [Seleção] + [Seleção] — Odd combinada: [odd] — Confiança: [nível]\n\n"

"🚀 MELHORES TRIPLAS\n"
"TRIPLA 01 — [Seleção] + [Seleção] + [Seleção] — Odd combinada: [odd] — Confiança: [nível]\n"
"TRIPLA 02 — [Seleção] + [Seleção] + [Seleção] — Odd combinada: [odd] — Confiança: [nível]\n"
"TRIPLA 03 — [Seleção] + [Seleção] + [Seleção] — Odd combinada: [odd] — Confiança: [nível]\n\n"

"🥇 TOP OPORTUNIDADES\n"
"Mostre as melhores oportunidades encontradas em todos os jogos analisados, independentemente do mercado.\n"
"Para cada uma, informe jogo, mercado, seleção, odd, confiança e principal motivo da escolha.\n\n"
                "Formate a sua resposta final de forma impecável usando emojis marcantes, tópicos limpos e negritos organizados para publicação em canal VIP."
            )

            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt_sistema},
                    {"role": "user", "content": "Gere imediatamente a análise pré-live especializada completa aplicando os filtros de valor (Asiáticos/Escanteios/Gols) conforme as regras operacionais."}
                ]
            )

            # CORREÇÃO CRUCIAL AQUI: Adicionado [0] para extrair corretamente da lista da OpenAI
            analise_final = response.choices[0].message.content
            
            enviar_mensagem(CHANNEL_ID, analise_final)
            enviar_mensagem(chat_id, "✅ Palpite de alto valor publicado no canal privado com sucesso!")
        else:
            enviar_mensagem(chat_id, "❌ Erro ao obter link do arquivo.")

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
                        file_id = message["photo"][-1]["file_id"]
                        processar_foto(chat_id, file_id)
        time.sleep(1)

if __name__ == '__main__':
    limpar_fila_telegram()
    
    t = threading.Thread(target=iniciar_servidor_web, daemon=True)
    t.start()
    
    executar_bot()
