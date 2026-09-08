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
URL_BASE = f"https://telegram.org{TELEGRAM_TOKEN}"

print("📌 Bot Pré-Live Iniciado com Visão Computacional Corrigida!")

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
        enviar_mensagem(chat_id, "📸 Print recebido! Analisando visualmente os dados reais do confronto...")

        url_file = f"{URL_BASE}/getFile?file_id={file_id}"
        res_file = requests.get(url_file, timeout=10).json()

        if res_file.get("ok"):
            file_path = res_file["result"]["file_path"]
            url_download = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/{file_path}"
            response_foto = requests.get(url_download, timeout=15)

            if response_foto.status_code == 200:
                # Converte o print real para código Base64 para envio de imagem à OpenAI
                foto_base64 = base64.b64encode(response_foto.content).decode("utf-8")

                prompt_sistema = (
                    "Você é um analista estatístico e tipster esportivo profissional sênior.\n"
                    "Sua única tarefa é ler o print real enviado pelo usuário e identificar os times e dados corretos.\n\n"
                    "REGRAS DE LEITURA E ANÁLISE:\n"
                    "1. Identifique com precisão absoluta o Evento real (quais são os dois times jogando na imagem).\n"
                    "2. Leia o mercado e a odd sugerida no print. Com base estritamente nesses times reais da foto, sugira um palpite inteligente focado em mercados alternativos de alto valor:\n"
                    "   - Mercado Asiático (Handicaps de Gols ou Linhas de proteção como AH 0.0 / DNB).\n"
                    "   - Escanteios / Cantos (Cantos Asiáticos de valor ou Over Cantos no primeiro/segundo tempo).\n"
                    "   - Gols / Ambas Marcam (BTTS Sim ou Não) justificando com base no estilo de jogo real dos dois times.\n"
                    "3. Forneça uma breve Justificativa tática coerente baseada especificamente nas duas equipes da imagem.\n"
                    "4. Indique uma Gestão de Banca de 1% a 2% de stake baseado no risco da entrada.\n\n"
                    "Formate a resposta de maneira organizada com emojis, tópicos limpos e negritos para publicação em um canal VIP."
                )

                # Requisição multimodal legítima: envia a foto convertida em tempo real
                response = openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": prompt_sistema},
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Extraia os times reais e os dados contidos neste print e monte a análise:"},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{foto_base64}"
                                    }
                                }
                            ]
                        }
                    ],
                    temperature=0.4 # Temperatura mais baixa diminui a chance de a IA inventar dados ou misturar confrontos
                )

                analise_final = response.choices[0].message.content
                enviar_mensagem(CHANNEL_ID, analise_final)
                enviar_mensagem(chat_id, "✅ Palpite real publicado no canal privado com sucesso!")
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
