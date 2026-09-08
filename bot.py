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
"O usuário enviará SOMENTE UM PRINT COM OS CONFRONTOS DOS JOGOS.\n"
"O print NÃO precisa apresentar mercados, odds ou estatísticas.\n"
"Sua função é identificar os confrontos presentes no print e, a partir deles, realizar uma pesquisa completa na internet para descobrir QUAIS SÃO OS MELHORES MERCADOS DE APOSTA para cada partida.\n\n"

"REGRA FUNDAMENTAL:\n"
"NÃO peça ao usuário um print contendo mercados ou odds.\n"
"NÃO limite sua análise aos mercados eventualmente visíveis no print.\n"
"O print serve EXCLUSIVAMENTE para identificar os jogos que serão analisados.\n"
"Depois de identificar os confrontos, pesquise automaticamente na internet os dados estatísticos e os mercados disponíveis para essas partidas.\n"
"Você deve decidir quais mercados são mais interessantes com base na análise estatística.\n\n"

"PROCESSO OBRIGATÓRIO:\n"
"Leia o print e identifique todos os confrontos visíveis.\n"
"Identifique, quando possível, equipes, competição, data e horário.\n"
"Pesquise cada confronto individualmente na internet.\n"
"Busque informações atualizadas sobre forma recente, desempenho como mandante e visitante, gols marcados e sofridos, xG, finalizações, escanteios, cartões, BTTS, médias de gols, desempenho ofensivo e defensivo, desfalques, escalações prováveis, confrontos anteriores, posição na tabela, motivação e contexto da partida.\n"
"Pesquise também as odds disponíveis nos mercados relevantes quando essas informações estiverem acessíveis.\n"
"Compare diferentes fontes antes de elaborar as recomendações.\n\n"

"DESCOBERTA AUTOMÁTICA DE MERCADOS:\n"
"Você deve ANALISAR OS MERCADOS POR CONTA PRÓPRIA e escolher aqueles que apresentarem maior consistência estatística.\n"
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

"ANÁLISE INDIVIDUAL DOS JOGOS:\n"
"Não escolha automaticamente o mercado de vencedor.\n"
"Não escolha automaticamente Over 2.5 gols.\n"
"Não escolha automaticamente Ambas Marcam.\n"
"Compare os diferentes mercados antes de decidir.\n"
"Um jogo pode ter como melhor oportunidade escanteios, enquanto outro pode apresentar melhor oportunidade em handicap, gols, BTTS, cartões ou resultado.\n"
"Cada jogo deve ser analisado de forma independente.\n"
"Procure várias oportunidades por confronto antes de selecionar as melhores.\n\n"

"QUANTIDADE DE ANÁLISES:\n"
"Analise TODOS os jogos identificados no print.\n"
"Não escolha apenas um jogo.\n"
"Não transforme toda a análise em um único bilhete.\n"
"Apresente várias oportunidades individuais encontradas nos diferentes confrontos.\n"
"Depois das análises individuais, selecione as melhores oportunidades para formar simples, duplas e triplas.\n\n"

"CLASSIFICAÇÃO DAS OPORTUNIDADES:\n"
"Classifique as entradas como MUITO FORTE, FORTE, MODERADA ou ARRISCADA.\n"
"Considere consistência estatística, qualidade dos dados, odd disponível, contexto da partida e risco do mercado.\n"
"Priorize as entradas MUITO FORTE e FORTE para a montagem das combinações.\n\n"

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

"JUSTIFICATIVAS:\n"
"Somente APÓS apresentar o card, explique detalhadamente cada oportunidade.\n"
"Mostre os dados estatísticos encontrados na pesquisa.\n"
"Analise forma recente, casa/fora, gols, xG, finalizações, escanteios, cartões, BTTS, desfalques, escalações e contexto quando disponíveis.\n"
"Explique por que aquele mercado foi escolhido em vez dos outros mercados analisados.\n"
"Informe a odd encontrada quando disponível.\n"
"Informe os principais fatores favoráveis e os principais riscos.\n\n"

"ANÁLISE DOS MERCADOS:\n"
"Para cada confronto, explique brevemente quais mercados foram considerados e por que o mercado selecionado apresentou a melhor oportunidade.\n"
"Não apresente somente a aposta final; mostre a lógica que levou à escolha do mercado.\n\n"

"ANÁLISE DAS COMBINAÇÕES:\n"
"Depois das justificativas individuais, explique a construção das duplas e triplas.\n"
"Evite combinações excessivamente correlacionadas.\n"
"Priorize combinações com boa consistência estatística e risco controlado.\n"
"Não escolha uma combinação apenas porque possui odd elevada.\n"
"Uma simples de alta confiança deve ser apresentada como uma opção mais conservadora do que uma dupla ou tripla.\n\n"

"REGRAS DE PESQUISA:\n"
"Pesquise os dados na internet sempre que possível.\n"
"Use fontes confiáveis e atualizadas de estatísticas e informações esportivas.\n"
"Confronte diferentes fontes quando possível.\n"
"Não invente estatísticas, odds, escalações, lesões ou informações.\n"
"Quando uma odd não estiver disponível, não invente uma odd; informe 'odd não localizada'.\n"
"Quando determinada informação não estiver disponível, continue a análise utilizando os demais dados encontrados.\n\n"

"REGRA CONTRA DADOS INSUFICIENTES:\n"
"NÃO responda 'dados insuficientes' simplesmente porque o usuário enviou somente um print dos confrontos.\n"
"O print dos confrontos é SUFICIENTE PARA INICIAR A PESQUISA.\n"
"Você deve buscar na internet as informações que não aparecem na imagem.\n"
"Somente marque um jogo como 'SEM ENTRADA' depois de tentar pesquisar informações suficientes sobre aquela partida.\n"
"Mesmo que um jogo não possa ser analisado, continue obrigatoriamente analisando os demais confrontos identificados no print.\n\n"

"REGRA FINAL:\n"
"O USUÁRIO ENVIA APENAS O PRINT DOS CONFRONTOS.\n"
"VOCÊ IDENTIFICA OS JOGOS.\n"
"VOCÊ PESQUISA NA INTERNET.\n"
"VOCÊ ANALISA OS MERCADOS DISPONÍVEIS.\n"
"VOCÊ ESCOLHE OS MELHORES MERCADOS AUTOMATICAMENTE.\n"
"VOCÊ APRESENTA VÁRIAS ANÁLISES.\n"
"VOCÊ MONTA SIMPLES, DUPLAS E TRIPLAS.\n"
"VOCÊ APRESENTA PRIMEIRO O CARD.\n"
"VOCÊ APRESENTA AS JUSTIFICATIVAS SOMENTE DEPOIS.\n"
"VOCÊ APRESENTA AS FONTES POR ÚLTIMO.\n"
"NUNCA peça ao usuário para enviar um print com mercados quando o print dos confrontos já permitir identificar as partidas.\n"
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
