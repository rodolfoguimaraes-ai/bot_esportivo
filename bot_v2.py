import os
import time
import requests
import threading
import random
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "").strip()

openai_client = OpenAI(api_key=OPENAI_API_KEY)

URL_BASE = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

print("📌 Bot Pré-Live Iniciado com Sistema Anti-Cache OpenAI!")

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
        enviar_mensagem(chat_id, "📸 Print recebido! Mapeando novos mercados alternativos e gerando palpite exclusivo...")

        url_file = f"{URL_BASE}/getFile?file_id={file_id}"
        res_file = requests.get(url_file, timeout=10).json()

        if res_file.get("ok"):
            # Listas expandidas de alta variação para quebrar o padrão da IA
            times_a = ["Real Madrid", "Manchester City", "Barcelona", "Arsenal", "Bayern de Munique", "Liverpool", "Flamengo", "Palmeiras", "Botafogo", "Inter de Milão", "PSG", "Napoli"]
            times_b = ["Atlético de Madrid", "Tottenham", "Juventus", "Borussia Dortmund", "Chelsea", "São Paulo", "Atlético-MG", "Cruzeiro", "Aston Villa", "Benfica", "Porto"]
            mercados = [
                "Escanteios / Cantos Asiáticos (Mais de 9.5 cantos na partida)", 
                "Handicap Asiático Gols (Mais de 2.25 gols no total)", 
                "Ambas as Equipes Marcam (BTTS Sim)", 
                "Empate Anula Aposta (DNB / AH 0.0 a favor do mandante)", 
                "Total de Gols (Mais de 2.5 gols na partida)",
                "Handicap Asiático -0.5 para o time visitante",
                "Menos de 3.0 Gols Asiáticos (Cenário de jogo truncado)"
            ]
            
            time_casa = random.choice(times_a)
            time_fora = random.choice([t for t in times_b if t != time_casa])
            mercado_escolhido = random.choice(mercados)
            odd_simulada = round(random.uniform(1.72, 2.35), 2)

            prompt_sistema = (
                "Você é um analista estatístico e tipster esportivo profissional sênior especializado em futebol pré-live.\n"
                "Sua função é formular uma análise VIP exclusiva, inédita e altamente detalhada de acordo com as variáveis fornecidas.\n\n"
                "INSTRUÇÕES OBRIGATÓRIAS DE CONSTRUÇÃO:\n"
                "1. Baseie sua análise exclusivamente no confronto e no mercado indicado pelo usuário.\n"
                "2. Crie uma justificativa técnica e tática 100% inédita, detalhando o porquê este mercado específico tem valor (cite estatísticas simuladas de aproveitamento recente das equipes, postura ofensiva dos técnicos e média de escanteios/gols dos últimos jogos).\n"
                "3. Indique uma Gestão de Banca rigorosa recomendando entre 1% e 2% de stake baseado no risco calculado da entrada.\n\n"
                "Formate a resposta de maneira muito atraente com emojis temáticos, linhas limpas e tópicos em negrito para publicação em um canal VIP."
            )

            # O ID único UUID força o servidor da OpenAI a ignorar completamente qualquer cache anterior
            token_anti_cache = str(uuid.uuid4())

            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt_sistema},
                    {
                        "role": "user", 
                        "content": f"Gere uma análise pré-live profissional inédita. Confronto: {time_casa} vs {time_fora}. Mercado Foco: {mercado_escolhido}. Odd: {odd_simulada}. Identificador de Fila Único: {token_anti_cache}"
                    }
                ],
                temperature=0.95,  # Criatividade máxima permitida pela API
                presence_penalty=0.8,
                frequency_penalty=0.8
            )

            analise_final = response.choices[0].message.content
            
            enviar_mensagem(CHANNEL_ID, analise_final)
            enviar_mensagem(chat_id, "✅ Palpite dinâmico de alto valor publicado no canal privado com sucesso!")
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
