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
            "Você é um analista estatístico e tipster esportivo profissional sênior especializado em futebol pré-live.\n"
            "Sua única tarefa é ler o texto do confronto enviado pelo usuário e criar uma tip avançada de alto valor.\n\n"
            "REGRAS DE ANÁLISE COMPUTAÇÃO:\n"
            "1. Baseie-se estritamente nas informações ou times digitados pelo usuário na legenda.\n"
            "2. Varie obrigatoriamente os palpites sugeridos entre: Cantos Asiáticos (ex: Over 9.5 cantos), Handicap de Gols (ex: Over 2.25 gols), Ambas Marcam (BTTS Sim) ou Empate Anula Aposta (DNB).\n"
            "3. Desenvolva uma justificativa técnica e tática de 2 a 3 linhas simulando dados analíticos baseados especificamente no estilo de jogo real dos dois times citados.\n"
            "4. Indique uma Gestão de Banca estrita recomendando 1% ou 2% de stake.\n\n"
            "Formate a resposta com emojis temáticos fortes e tópicos organizados em negrito para publicação direta em um canal VIP."
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
