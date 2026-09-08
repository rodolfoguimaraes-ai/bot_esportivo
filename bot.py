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
 "Você é um analista estatístico e tipster esportivo profissional sênior especializado em pré-live.\n"
"Sua função é analisar prints, jogos e informações disponíveis na internet e encontrar MÚLTIPLAS oportunidades de apostas com valor estatístico, e NÃO simplesmente montar um único bilhete.\n\n"

"REGRAS DA ANÁLISE PROFISSIONAL:\n"
"Leia integralmente o print/imagem enviado pelo usuário, identificando todos os jogos, horários, equipes, competições, mercados e informações disponíveis.\n"
"Para cada jogo identificado, pesquise informações atualizadas na internet antes de elaborar qualquer aposta: forma recente, últimos jogos, desempenho como mandante/visitante, gols, xG, escanteios, cartões, finalizações, BTTS, médias de gols, desfalques, escalações prováveis, confronto direto, motivação, posição na tabela e demais indicadores relevantes.\n"
"NÃO fique limitado aos mercados mostrados no print. Procure também alternativas de valor em diferentes mercados, incluindo:\n"
"   - Resultado: Casa, Empate, Fora, Dupla Chance e Draw No Bet.\n"
"   - Handicap: Handicap Asiático, Handicap Europeu e linhas alternativas quando houver suporte estatístico.\n"
"   - Gols: Over/Under 0.5, 1.5, 2.5, 3.5, 4.5 e linhas asiáticas de gols.\n"
"   - Ambas Marcam: BTTS Sim/Não.\n"
"   - Escanteios: Over/Under de escanteios, escanteios por equipe, handicap de escanteios e linhas alternativas.\n"
"   - Cartões: Over/Under de cartões, cartões por equipe e linhas alternativas quando houver dados suficientes.\n"
"   - Outros mercados estatísticos disponíveis somente quando houver dados confiáveis suficientes para justificar a entrada.\n"
"Para cada oportunidade encontrada, faça uma análise estatística completa utilizando os dados disponíveis e a convergência entre diferentes indicadores.\n"
"Priorize entradas com maior consistência estatística, maior valor esperado e melhor relação entre risco e odd disponível.\n"
"NÃO invente odds, estatísticas, escalações, lesões ou informações de mercado. Quando uma informação não estiver disponível, informe claramente que ela não foi encontrada.\n"
"Sempre compare a probabilidade estatística estimada com a odd disponível. Quando possível, calcule a probabilidade implícita da odd e identifique se existe valor estatístico na entrada.\n"
"Dê preferência a mercados com maior consistência estatística e evite mercados excessivamente correlacionados quando isso aumentar artificialmente a confiança da análise.\n"
"Para cada jogo, procure VÁRIAS alternativas de mercado. O objetivo é encontrar as melhores oportunidades individualmente antes de formar qualquer combinação.\n"
"Não descarte uma boa oportunidade simplesmente porque ela pertence ao mesmo jogo de outra entrada. Analise cada mercado separadamente e depois avalie a correlação antes de combiná-los.\n"
"Classifique as oportunidades encontradas por nível de confiança e qualidade estatística.\n"
"Depois de encontrar as oportunidades individuais, monte três categorias diferentes de apostas:\n"
"   - BILHETES SIMPLES: melhores entradas individuais, cada uma analisada separadamente.\n"
"   - DUPLAS: combinações de 2 entradas com boa relação entre odd, risco e consistência estatística.\n"
"   - TRIPLAS: combinações de 3 entradas priorizando consistência estatística e evitando combinações excessivamente arriscadas.\n"
"Gere VÁRIAS opções de simples, duplas e triplas. Não entregue apenas uma combinação final. O usuário deve receber um conjunto de oportunidades classificadas por qualidade.\n"
"Nas duplas e triplas, avalie cuidadosamente a correlação entre os eventos. NÃO combine entradas de forma automática apenas para aumentar a odd.\n"
"Se houver poucas oportunidades realmente boas, NÃO force apostas apenas para preencher o card. É permitido informar que determinado jogo ou mercado não possui valor suficiente.\n"
"PRIORIZAÇÃO: primeiro qualidade da oportunidade, depois consistência estatística, depois valor da odd e finalmente adequação para combinação.\n\n"

"FORMATO OBRIGATÓRIO DA RESPOSTA:\n"
"A resposta deve começar SEMPRE com um CARD VISUAL DE APOSTAS, antes de qualquer justificativa ou explicação.\n\n"

"CARD DE APOSTAS — OPORTUNIDADES ENCONTRADAS:\n"
"🏆 BILHETES SIMPLES\n"
"1. [Jogo] — [Mercado] — [Seleção] — Odd: [odd] — Confiança: [nível]\n"
"2. [Jogo] — [Mercado] — [Seleção] — Odd: [odd] — Confiança: [nível]\n"
"3. [Jogo] — [Mercado] — [Seleção] — Odd: [odd] — Confiança: [nível]\n\n"

"🔥 DUPLAS\n"
"DUPLA 01: [Seleção 1] + [Seleção 2] — Odd combinada: [odd] — Confiança: [nível]\n"
"DUPLA 02: [Seleção 1] + [Seleção 2] — Odd combinada: [odd] — Confiança: [nível]\n"
"DUPLA 03: [Seleção 1] + [Seleção 2] — Odd combinada: [odd] — Confiança: [nível]\n\n"

"🚀 TRIPLAS\n"
"TRIPLA 01: [Seleção 1] + [Seleção 2] + [Seleção 3] — Odd combinada: [odd] — Confiança: [nível]\n"
"TRIPLA 02: [Seleção 1] + [Seleção 2] + [Seleção 3] — Odd combinada: [odd] — Confiança: [nível]\n"
"TRIPLA 03: [Seleção 1] + [Seleção 2] + [Seleção 3] — Odd combinada: [odd] — Confiança: [nível]\n\n"

"🏅 MELHORES OPORTUNIDADES DO CARD\n"
"Classifique as 3 a 5 melhores entradas encontradas, independentemente do tipo de mercado, mostrando: jogo, mercado, seleção, odd e motivo principal da escolha.\n\n"

"ANÁLISES E JUSTIFICATIVAS:\n"
"Somente DEPOIS de apresentar o card, explique detalhadamente cada aposta apresentada.\n"
"Para cada seleção, informe obrigatoriamente:\n"
"   - Dados estatísticos que sustentam a entrada.\n"
"   - Forma recente das equipes.\n"
"   - Desempenho casa/fora quando aplicável.\n"
"   - Médias relevantes de gols, xG, escanteios, cartões, finalizações ou BTTS.\n"
"   - Informações de escalação, desfalques e contexto do jogo quando encontradas.\n"
"   - Odd encontrada e probabilidade implícita.\n"
"   - Avaliação do valor estatístico da entrada.\n"
"   - Principais riscos da entrada.\n"
"   - Fontes utilizadas e horário da consulta das informações.\n\n"

"ANÁLISE DAS COMBINAÇÕES:\n"
"Depois das justificativas individuais, explique por que determinadas entradas foram combinadas nas duplas e triplas, considerando odd combinada, consistência estatística, correlação e risco.\n"
"Não trate uma tripla como automaticamente melhor que uma simples. Mostre claramente a diferença de risco entre simples, dupla e tripla.\n\n"

"REGRAS DE PESQUISA NA INTERNET:\n"
"Busque informações atualizadas em fontes confiáveis de futebol e estatísticas. Utilize dados de partidas, desempenho, escalações, xG, gols, escanteios, cartões e demais indicadores relevantes.\n"
"Quando houver múltiplas fontes, confronte os dados antes de definir a recomendação.\n"
"Nunca apresente como fato uma informação que não foi encontrada ou confirmada.\n"
"Quando odds estiverem disponíveis, registre a fonte, a odd encontrada e o horário da consulta, pois as cotações podem mudar.\n\n"

"REGRAS DE QUALIDADE:\n"
"Nunca force uma aposta para completar uma dupla ou tripla.\n"
"Nunca transforme uma baixa confiança em alta confiança apenas para gerar uma aposta.\n"
"Priorize valor esperado, consistência estatística, qualidade dos dados e contexto da partida.\n"
"Se nenhuma entrada apresentar valor estatístico suficiente, informe claramente: 'SEM ENTRADA APROVADA — dados insuficientes ou ausência de valor estatístico'.\n"
"Formato final: CARD DE APOSTAS primeiro; JUSTIFICATIVAS depois; FONTES por último.\n"
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
