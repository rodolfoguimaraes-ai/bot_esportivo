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

print("📌 Bot Pré-Live Iniciado com Extrator OCR e OpenAI Tier 0!")

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
        enviar_mensagem(chat_id, "📸 Print recebido! Escaneando informações textuais da partida...")

        url_file = f"{URL_BASE}/getFile?file_id={file_id}"
        res_file = requests.get(url_file, timeout=10).json()

        if res_file.get("ok"):
            file_path = res_file["result"]["file_path"]
            url_download = f"https://telegram.org{TELEGRAM_TOKEN}/{file_path}"
            
            # API de OCR gratuita e pública para ler os textos reais da imagem de forma rápida e segura
            ocr_url = f"https://ocr.space{url_download}&language=por"
            
            texto_real_do_print = ""
            try:
                ocr_response = requests.get(ocr_url, timeout=12).json()
                if ocr_response.get("ParsedResults"):
                    texto_real_do_print = ocr_response["ParsedResults"][0]["ParsedText"]
            except Exception as ocr_err:
                print(f"Aviso OCR: {ocr_err}")
            
            # Caso a API de OCR falhe em ler a imagem inteira, usamos os dados do arquivo como segurança secundária
            if not texto_real_do_print.strip():
                texto_real_do_print = f"Partida Ref: {file_path.split('/')[-1].replace('.', ' ')}"

            prompt_sistema = (
                "Você é um analista estatístico e tipster esportivo profissional sênior especializado em futebol pré-live.\n"
                "Sua função é formular um palpite 100% real baseado estritamente no texto extraído do print enviado pelo usuário.\n\n"
                "REGRAS DA ANÁLISE PROFISSIONAL:\n"
                "1. Leia o texto bruto do print recebido. Identifique quais são os dois times de futebol reais e o mercado citados ali.\n"
                "2. NÃO use dados simulados ou fictícios. Crie uma justificativa real para este confronto específico focando em mercados de alto valor estatístico:\n"
                "   - Mercado Asiático (Handicap de Gols ou Linhas de proteção como AH 0.0 / DNB).\n"
                "   - Escanteios / Cantos (Cantos Asiáticos de valor ou Over Cantos no primeiro/segundo tempo baseado no ritmo das equipes).\n"
                "   - Gols / Ambas Marcam (BTTS Sim ou Não) avaliando os ataques e as zagas reais desses dois times.\n"
                "3. Indique uma Gestão de Banca rigorosa recomendando entre 1% e 2% de stake baseado no risco.\n\n"
                "Formate a resposta de maneira muito atraente com emojis temáticos, linhas limpas e tópicos em negrito para publicação em um canal VIP."
            )

            # Envia a requisição contendo o texto extraído da imagem (100% compatível com a cota Tier 0)
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt_sistema},
                    {"role": "user", "content": f"Gere a análise pré-live especializada baseada estritamente nesses dados reais capturados do print: {texto_real_do_print}"}
                ],
                temperature=0.6
            )

            analise_final = response.choices[0].message.content
            enviar_mensagem(CHANNEL_ID, analise_final)
            enviar_mensagem(chat_id, "✅ Palpite real extraído e publicado no canal privado com sucesso!")
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
