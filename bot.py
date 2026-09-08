import os
import time
import requests
import base64
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

print("📌 Bot Pré-Live Iniciado com Análise Avançada de Mercados!")

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
            file_path = res_file["result"]["file_path"]
            url_download = f"https://telegram.org{TELEGRAM_TOKEN}/{file_path}"
            response_foto = requests.get(url_download, timeout=15)

            if response_foto.status_code == 200:
                # Converte o print real para processamento visual da IA
                foto_base64 = base64.b64encode(response_foto.content).decode("utf-8")

                # PROMPT AVANÇADO: Força a busca por escanteios, asiáticos e valor real
                prompt_sistema = (
                    "Você é um analista estatístico e tipster esportivo profissional sênior.\n"
                    "Sua função é identificar os times presentes no print enviado e estruturar um palpite de alto valor.\n\n"
                    "REGRAS DA ANÁLISE:\n"
                    "1. Identifique o Evento (Times/Campeonato).\n"
                    "2. Não se limite ao mercado simples de vitória (1X2) mostrado na imagem se as odds estiverem esmagadas. Busque sempre sugerir cenários de maior valor estatístico, PRIORIZANDO:\n"
                    "   - Mercados Asiáticos (Handicaps Asiáticos de Gols ou Linhas de proteção como AH 0.0 / DNB).\n"
                    "   - Escanteios (Cantos Totais ou Cantos Asiáticos com base na postura ofensiva esperada).\n"
                    "   - Gols / Ambas Marcam (BTTS) se houver forte tendência ofensiva/defensiva.\n"
                    "3. Indique uma Gestão de Banca estrita (Recomende 1% ou 2% de stake baseado no risco).\n\n"
                    "Formate a sua resposta final de forma muito elegante usando emojis, negritos e tópicos organizados para publicação em um canal VIP."
                )

                # Requisição multimídia completa enviando a imagem real do usuário
                response = openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": prompt_sistema},
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Analise os times e mercados deste print de aposta e gere o palpite avançado focado em valor (Asiáticos/Escanteios/Gols):"},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{foto_base64}"
                                    }
                                }
                            ]
                        }
                    ]
                )

                analise_final = response.choices[0].message.content
                
                # Envia o palpite estruturado para o canal privado
                enviar_mensagem(CHANNEL_ID, analise_final)
                enviar_mensagem(chat_id, "✅ Palpite de alto valor publicado no canal privado com sucesso!")
            else:
                enviar_mensagem(chat_id, f"❌ Erro ao baixar foto do Telegram (Status: {response_foto.status_code})")
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
