import os
import time
import requests
import base64
from openai import OpenAI
from dotenv import load_dotenv

# Carrega as variáveis do .env
load_dotenv("/home/Rsguimaraes/bot_esportivo/.env")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "").strip()

# Inicialização da OpenAI
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Proxy Manual Forçado para Contas Gratuitas do PythonAnywhere
proxies = {
    'http': 'http://proxy.server:3128',
    'https': 'http://proxy.server:3128'
}

URL_BASE = f"https://telegram.org{TELEGRAM_TOKEN}"

print("📌 Bot Pré-Live Corrigido Iniciado via Proxy Manual Resistente!")

def buscar_atualizacoes(offset=None):
    url = f"{URL_BASE}/getUpdates?timeout=30"
    if offset:
        url += f"&offset={offset}"
    try:
        # Usa o proxy manual e reduz o timeout para não travar o loop se o servidor cair
        response = requests.get(url, proxies=proxies, timeout=15)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"⏳ Servidor do PythonAnywhere oscilou (Proxy 503/Timeout). Tentando novamente em 3s...")
        time.sleep(3)
    return None

def enviar_mensagem(chat_id, texto):
    url = f"{URL_BASE}/sendMessage"
    payload = {"chat_id": chat_id, "text": texto, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, proxies=proxies, timeout=10)
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

def processar_foto(chat_id, file_id):
    try:
        enviar_mensagem(chat_id, "📸 Print recebido! Analisando mercado e buscando dados. O resultado sairá no canal...")

        # Pega as informações do arquivo de foto no Telegram
        url_file = f"{URL_BASE}/getFile?file_id={file_id}"
        res_file = requests.get(url_file, proxies=proxies, timeout=10).json()

        if res_file.get("ok"):
            file_path = res_file["result"]["file_path"]

            # URL oficial de download
            url_download = f"https://telegram.org{TELEGRAM_TOKEN}/{file_path}"
            response_foto = requests.get(url_download, proxies=proxies, timeout=15)

            if response_foto.status_code == 200:
                # Converte para Base64 de forma segura
                foto_base64 = base64.b64encode(response_foto.content).decode("utf-8")

                prompt_sistema = (
                    "Você é um analista esportivo profissional. Extraia o evento, mercado e odd e faça uma breve análise."
                )

                response = openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": prompt_sistema},
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Analise este print:"},
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

                analise_final = response.choices.message.content
                enviar_mensagem(CHANNEL_ID, analise_final)
                enviar_mensagem(chat_id, "✅ Publicado com sucesso no canal!")
            else:
                enviar_mensagem(chat_id, f"❌ Erro ao baixar foto (Status: {response_foto.status_code})")
        else:
            enviar_mensagem(chat_id, "❌ Erro ao obter link do arquivo.")

    except Exception as e:
        enviar_mensagem(chat_id, f"❌ Erro de processamento: {str(e)}")

def ejecutar_bot():
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
    ejecutar_bot()
