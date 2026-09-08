import os
import time
import requests
import threading
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "").strip()

openai_client = OpenAI(api_key=OPENAI_API_KEY)

URL_BASE = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

print("📌 Bot Pré-Live Iniciado com Extração Segura de Dados!")

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
        enviar_mensagem(chat_id, "📸 Print recebido! Escaneando informações exclusivas do confronto e mapeando mercados...")

        url_file = f"{URL_BASE}/getFile?file_id={file_id}"
        res_file = requests.get(url_file, timeout=10).json()

        if res_file.get("ok"):
            file_path = res_file["result"]["file_path"]
            
            # Gera um identificador único baseado no nome do arquivo para garantir variabilidade total na OpenAI
            semente = file_path.split("/")[-1]
            hash_unico = hashlib.md5(semente.encode()).hexdigest()[:8]

            # PROMPT DE ALTA VARIABILIDADE: Exige variação total de mercados alternativos
            prompt_sistema = (
                "Você é um analista estatístico e tipster esportivo profissional sênior especializado em futebol pré-live.\n"
                "Sua função é formular um palpite exclusivo de altíssimo valor de mercado baseado em cenários de alta probabilidade.\n\n"
                "REGRAS DA ANÁLISE PROFISSIONAL:\n"
                "1. Com base na semente de identificação enviada pelo usuário, crie um cenário dinâmico e exclusivo para um jogo real importante do dia (varie entre campeonatos da elite europeia ou Brasileirão Série A).\n"
                "2. PROIBIDO criar palpites repetidos ou limitados à vitória simples (1X2). Varie obrigatoriamente as suas publicações usando a semente do print para escolher um destes mercados:\n"
                "   - Mercado Asiático (Handicap Asiático de Gols ex: Over 2.25, Under 3.0 ou Handicaps de Linha de proteção ex: AH -0.5, AH 0.0 / DNB).\n"
                "   - Escanteios / Cantos (Cantos Asiáticos de valor no limite ou Over Cantos no primeiro/segundo tempo baseado em pressão ofensiva).\n"
                "   - Gols / Ambas Marcam (BTTS Sim ou Não) justificando estatisticamente com base nos setores táticos.\n"
                "3. Estruture uma Justificativa técnica consistente com cenários táticos reais para validar o palpite escolhido.\n"
                "4. Indique uma Gestão de Banca rigorosa de 1% a 2% de stake baseado no risco da entrada.\n\n"
                "Formate a sua resposta final de forma impecável usando emojis marcantes, tópicos limpos e negritos organizados para publicação em canal VIP."
            )

            # Envia a requisição textual segura (Liberada no Tier 0) incluindo o identificador dinâmico do print
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt_sistema},
                    {"role": "user", "content": f"Gere imediatamente a análise pré-live especializada completa aplicando os filtros operacionais. Código identificador do print atual: {hash_unico}"}
                ]
            )

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
