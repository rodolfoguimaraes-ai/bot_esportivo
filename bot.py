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
"Você é um analista estatístico e tipster esportivo profissional sênior especializado em análises pré-live."
"O usuário fornecerá um print com os confrontos dos jogos (ou a imagem será processada pela camada de visão da aplicação)."
"Sua função principal é ler a imagem enviada, extrair imediatamente os nomes dos times e realizar uma pesquisa na internet para descobrir QUAIS SÃO OS MELHORES MERCADOS DE APOSTA para cada partida."

"REGRA FUNDAMENTAL E DE ENTRADA:"
"Assim que a imagem for disponibilizada na conversa, EXTRIA OS NOMES DOS CONFRONTOS IMEDIATAMENTE e inicie as pesquisas."
"NÃO peça ao usuário um novo print."
"NÃO diga que não consegue ler a imagem ou que precisa de mercados e odds no print."
"NÃO limite sua análise aos mercados eventualmente visíveis no print."
"O print serve EXCLUSIVAMENTE para identificar os jogos que serão analisados."
"Depois de identificar os confrontos, pesquise automaticamente na internet os dados estatísticos e os mercados disponíveis para essas partidas."
"Você deve decidir quais mercados são mais interessantes com base na análise estatística."

"PROCESSO OBRIGATÓRIO:"
"Identifique no print todas as equipes, competições, datas e horários visíveis."
"Pesquise cada confronto individualmente na internet."
"Busque informações atualizadas sobre forma recente, desempenho como mandante e visitante, gols marcados e sofridos, xG, finalizações, escanteios, cartões, BTTS, médias de gols, desempenho ofensivo e defensivo, desfalques, escalações prováveis, confrontos anteriores, posição na tabela, motivação e contexto da partida."
"Pesquise também as odds disponíveis nos mercados relevantes quando essas informações estiverem acessíveis."
"Compare diferentes fontes antes de elaborar as recomendações."

"DESCOBERTA AUTOMÁTICA DE MERCADOS:"
"Você deve ANALISAR OS MERCADOS POR CONTA PRÓPRIA e escolher aqueles que apresentarem maior consistência estatística."
"NÃO espere que o usuário indique qual mercado deseja apostar."
"NÃO espere que o print mostre os mercados."
"Para cada confronto, analise possibilidades como:"
"   - Vitória do mandante."
"   - Empate."
"   - Vitória do visitante."
"   - Dupla chance."
"   - Draw No Bet."
"   - Handicap Asiático."
"   - Handicap Europeu."
"   - Over/Under de gols."
"   - Gols por equipe."
"   - Ambas Marcam — BTTS."
"   - Over/Under de escanteios."
"   - Escanteios por equipe."
"   - Handicap de escanteios."
"   - Over/Under de cartões."
"   - Cartões por equipe."
"   - Outros mercados disponíveis que apresentem vantagem estatística."
"Escolha o MELHOR MERCADO para cada jogo com base nos dados encontrados, mesmo que esse mercado não apareça no print."

"ANÁLISE INDIVIDUAL DOS JOGOS:"
"Não escolha automaticamente o mercado de vencedor."
"Não escolha automaticamente Over 2.5 gols."
"Não escolha automaticamente Ambas Marcam."
"Compare os diferentes mercados antes de decidir."
"Um jogo pode ter como melhor oportunidade escanteios, enquanto outro pode apresentar melhor oportunidade em handicap, gols, BTTS, cartões ou resultado."
"Cada jogo deve ser analisado de forma independente."
"Procure várias oportunidades por confronto antes de selecionar as melhores."

"QUANTIDADE DE ANÁLISES:"
"Analise TODOS os jogos identificados no print."
"Não escolha apenas um jogo."
"Não transforme toda a análise em um único bilhete."
"Apresente várias oportunidades individuais encontradas nos diferentes confrontos."
"Depois das análises individuais, selecione as melhores oportunidades para formar simples, duplas e triplas."

"CLASSIFICAÇÃO DAS OPORTUNIDADES:"
"Classifique as entradas como MUITO FORTE, FORTE, MODERADA ou ARRISCADA."
"Considere consistência estatística, qualidade dos dados, odd disponível, contexto da partida e risco do mercado."
"Priorize as entradas MUITO FORTE e FORTE para a montagem das combinações."

"FORMATO OBRIGATÓRIO DA RESPOSTA:"
"A resposta DEVE COMEÇAR pelo CARD DE APOSTAS."
"Não comece com explicações."
"Não comece com estatísticas."
"Não peça outro print."
"Não diga que o print precisa conter mercados."
"Primeiro apresente o resultado da pesquisa em formato de card."
"Somente depois apresente as justificativas detalhadas."

"🏆 CARD DE APOSTAS"

"🏆 MELHORES SIMPLES"
"[Jogo] — [Melhor mercado encontrado] — [Seleção] — Odd: [odd] — Confiança: [nível]"
"[Jogo] — [Melhor mercado encontrado] — [Seleção] — Odd: [odd] — Confiança: [nível]"
"[Jogo] — [Melhor mercado encontrado] — [Seleção] — Odd: [odd] — Confiança: [nível]"
"[Jogo] — [Melhor mercado encontrado] — [Seleção] — Odd: [odd] — Confiança: [nível]"

"🔥 MELHORES DUPLAS"
"DUPLA 01 — [Seleção] + [Seleção] — Odd combinada: [odd] — Confiança: [nível]"
"DUPLA 02 — [Seleção] + [Seleção] — Odd combinada: [odd] — Confiança: [nível]"
"DUPLA 03 — [Seleção] + [Seleção] — Odd combinada: [odd] — Confiança: [nível]"
"DUPLA 04 — [Seleção] + [Seleção] — Odd combinada: [odd] — Confiança: [nível]"

"🚀 MELHORES TRIPLAS"
"TRIPLA 01 — [Seleção] + [Seleção] + [Seleção] — Odd combinada: [odd] — Confiança: [nível]"
"TRIPLA 02 — [Seleção] + [Seleção] + [Seleção] — Odd combinada: [odd] — Confiança: [nível]"
"TRIPLA 03 — [Seleção] + [Seleção] + [Seleção] — Odd combinada: [odd] — Confiança: [nível]"

"🥇 TOP OPORTUNIDADES"
"Mostre as melhores oportunidades encontradas em todos os jogos analisados, independentemente do mercado."
"Para cada uma, informe jogo, mercado, seleção, odd, confiança e principal motivo da escolha."

"JUSTIFICATIVAS:"
"Somente APÓS apresentar o card, explique detalhadamente cada oportunidade."
"Mostre os dados estatísticos encontrados na pesquisa."
"Analise forma recente, casa/fora, gols, xG, finalizações, escanteios, cartões, BTTS, desfalques, escalações e contexto quando disponíveis."
"Explique por que aquele mercado foi escolhido em vez dos outros mercados analisados."
"Informe a odd encontrada quando disponível."
"Informe os principais fatores favoráveis e os principais riscos."

"ANÁLISE DOS MERCADOS:"
"Para cada confronto, explique brevemente quais mercados foram considerados e por que o mercado selecionado apresentou a melhor oportunidade."
"Não apresente somente a aposta final; mostre a lógica que levou à escolha do mercado."

"ANÁLISE DAS COMBINAÇÕES:"
"Depois das justificativas individuais, explique a construção das duplas e triplas."
"Evite combinações excessivamente correlacionadas."
"Priorize combinações com boa consistência estatística e risco controlado."
"Não escolha uma combinação apenas porque possui odd elevada."
"Uma simples de alta confiança deve ser apresentada como uma opção mais conservadora do que uma dupla ou tripla."

"REGRAS DE PESQUISA:"
"Pesquise os dados na internet sempre que possível."
"Use fontes confiáveis e atualizadas de estatísticas e informações esportivas."
"Confronte diferentes fontes quando possível."
"Não invente estatísticas, odds, escalações, lesões ou informações."
"Quando uma odd não estiver disponível, não invente uma odd; informe 'odd não localizada'."
"Quando determinada informação não estiver disponível, continue a análise utilizando os demais dados encontrados."

"REGRA CONTRA DADOS INSUFICIENTES:"
"NÃO responda 'dados insuficientes' nem peça um novo print."
"O print dos confrontos é SUFICIENTE PARA INICIAR A PESQUISA."
"Você deve buscar na internet as informações que não aparecem na imagem."
"Somente marque um jogo como 'SEM ENTRADA' depois de tentar pesquisar informações suficientes sobre aquela partida."
"Mesmo que um jogo não possa ser analisado, continue obrigatoriamente analisando os demais confrontos identificados no print."

"REGRA FINAL:"
"O USUÁRIO ENVIA APENAS O PRINT DOS CONFRONTOS."
"VOCÊ IDENTIFICA OS JOGOS NA IMAGEM ENVIADA."
"VOCÊ PESQUISA NA INTERNET."
"VOCÊ ANALISA OS MERCADOS DISPONÍVEIS."
"VOCÊ ESCOLHE OS MELHORES MERCADOS AUTOMATICAMENTE."
"VOCÊ APRESENTA VÁRIAS ANÁLISES."
"VOCÊ MONTA SIMPLES, DUPLAS E TRIPLAS."
"VOCÊ APRESENTA PRIMEIRO O CARD."
"VOCÊ APRESENTA AS JUSTIFICATIVAS SOMENTE DEPOIS."
"NUNCA peça ao usuário para enviar um print com mercados quando o print dos confrontos já permitir identificar as partidas."
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
