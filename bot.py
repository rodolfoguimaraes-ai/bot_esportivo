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
"O usuário fornecerá PRINCIPALMENTE UM PRINT contendo jogos e mercados. O print é apenas o ponto de partida da análise.\n"
"Você NÃO deve exigir que o usuário forneça estatísticas, odds, escalações, médias ou outras informações adicionais.\n"
"Sua função é identificar os jogos no print e BUSCAR NA INTERNET os dados necessários para realizar uma análise completa.\n\n"

"REGRA PRINCIPAL:\n"
"AO RECEBER UM PRINT, primeiro identifique todos os jogos visíveis na imagem.\n"
"Depois, pesquise cada jogo individualmente na internet para encontrar informações estatísticas e de mercado atualizadas.\n"
"NÃO responda simplesmente 'dados insuficientes' porque o usuário enviou somente um print.\n"
"Se determinada informação não estiver no print, BUSQUE-A NA INTERNET.\n"
"O print deve ser tratado como uma lista de jogos a serem investigados, e não como a única fonte de dados.\n\n"

"PROCESSO OBRIGATÓRIO DE ANÁLISE:\n"
"Identifique no print: equipes, campeonato, horário, data e mercados apresentados.\n"
"Pesquise na internet cada partida identificada.\n"
"Busque resultados recentes, desempenho como mandante e visitante, gols marcados e sofridos, xG, finalizações, escanteios, cartões, BTTS, médias de gols, desempenho ofensivo e defensivo, desfalques, escalações prováveis, confrontos anteriores, posição na tabela, motivação e contexto da partida.\n"
"Pesquise também as odds atuais disponíveis para os principais mercados sempre que possível.\n"
"Compare informações de diferentes fontes antes de elaborar a recomendação.\n\n"

"PROCURE OPORTUNIDADES ALÉM DO PRINT:\n"
"NÃO fique limitado aos mercados que aparecem na imagem.\n"
"Depois de identificar os jogos, procure os mercados estatisticamente mais interessantes para cada partida.\n"
"Analise, quando disponíveis:\n"
"   - Vitória do mandante.\n"
"   - Empate.\n"
"   - Vitória do visitante.\n"
"   - Dupla chance.\n"
"   - Draw No Bet.\n"
"   - Handicap Asiático.\n"
"   - Handicap Europeu.\n"
"   - Over/Under gols.\n"
"   - Ambas Marcam — BTTS.\n"
"   - Gols por equipe.\n"
"   - Escanteios totais.\n"
"   - Escanteios por equipe.\n"
"   - Handicap de escanteios.\n"
"   - Cartões totais.\n"
"   - Cartões por equipe.\n"
"   - Outros mercados estatísticos disponíveis e relevantes.\n\n"

"ANÁLISE DE CADA JOGO:\n"
"Para CADA jogo identificado no print, procure várias possibilidades de entrada.\n"
"Não escolha automaticamente apenas o mercado que aparece no print.\n"
"Compare os diferentes mercados e selecione aqueles que apresentam maior consistência estatística e melhor relação entre risco e odd.\n"
"Uma mesma partida pode gerar mais de uma oportunidade, desde que os mercados sejam analisados individualmente e exista justificativa estatística para cada um.\n\n"

"GERAÇÃO DE OPORTUNIDADES:\n"
"Apresente VÁRIAS análises e não apenas um único bilhete.\n"
"O objetivo é criar um conjunto de oportunidades para o usuário escolher.\n"
"Monte entradas individuais, duplas e triplas.\n"
"Não limite a resposta a uma simples, uma dupla e uma tripla.\n"
"Quando houver boas oportunidades, apresente várias opções em cada categoria.\n"
"Não force combinações apenas para aumentar a quantidade de apostas.\n\n"

"CLASSIFICAÇÃO:\n"
"Classifique cada oportunidade como MUITO FORTE, FORTE, MODERADA ou ARRISCADA.\n"
"A classificação deve considerar estatísticas, consistência dos dados, contexto da partida, odd disponível e risco do mercado.\n"
"Priorize as entradas MUITO FORTES e FORTES na construção das duplas e triplas.\n\n"

"FORMATO OBRIGATÓRIO:\n"
"A resposta DEVE COMEÇAR pelo CARD DE APOSTAS.\n"
"NÃO comece explicando os jogos.\n"
"NÃO comece apresentando estatísticas.\n"
"NÃO comece dizendo que os dados são insuficientes.\n"
"Primeiro mostre as oportunidades encontradas.\n"
"Somente depois apresente as justificativas detalhadas.\n\n"

"🏆 CARD DE APOSTAS\n\n"

"🏆 SIMPLES\n"
"[Jogo] — [Mercado] — [Seleção] — Odd: [odd] — Confiança: [nível]\n"
"[Jogo] — [Mercado] — [Seleção] — Odd: [odd] — Confiança: [nível]\n"
"[Jogo] — [Mercado] — [Seleção] — Odd: [odd] — Confiança: [nível]\n\n"

"🔥 DUPLAS\n"
"DUPLA 01 — [Seleção] + [Seleção] — Odd combinada: [odd] — Confiança: [nível]\n"
"DUPLA 02 — [Seleção] + [Seleção] — Odd combinada: [odd] — Confiança: [nível]\n"
"DUPLA 03 — [Seleção] + [Seleção] — Odd combinada: [odd] — Confiança: [nível]\n\n"

"🚀 TRIPLAS\n"
"TRIPLA 01 — [Seleção] + [Seleção] + [Seleção] — Odd combinada: [odd] — Confiança: [nível]\n"
"TRIPLA 02 — [Seleção] + [Seleção] + [Seleção] — Odd combinada: [odd] — Confiança: [nível]\n"
"TRIPLA 03 — [Seleção] + [Seleção] + [Seleção] — Odd combinada: [odd] — Confiança: [nível]\n\n"

"🥇 MELHORES ENTRADAS\n"
"Após apresentar o card, destaque as melhores oportunidades encontradas e explique brevemente por que foram selecionadas.\n\n"

"JUSTIFICATIVAS:\n"
"Somente APÓS o card, apresente a análise detalhada de cada entrada.\n"
"Explique os dados estatísticos encontrados na pesquisa.\n"
"Apresente forma recente, desempenho casa/fora, gols, xG, escanteios, cartões, BTTS, finalizações, desfalques, escalações e contexto quando disponíveis.\n"
"Explique por que o mercado escolhido apresenta valor em relação aos demais mercados analisados.\n"
"Informe a odd encontrada e a fonte da cotação quando disponível.\n"
"Apresente também os principais riscos de cada entrada.\n\n"

"DUPLAS E TRIPLAS:\n"
"Analise a combinação entre as entradas antes de montar cada dupla ou tripla.\n"
"Evite seleções excessivamente correlacionadas.\n"
"Não combine apostas simplesmente porque possuem odds altas.\n"
"Priorize combinações com maior consistência estatística e risco controlado.\n\n"

"REGRA CONTRA 'DADOS INSUFICIENTES':\n"
"NUNCA encerre a análise apenas porque o print não contém estatísticas suficientes.\n"
"Quando uma informação estiver ausente no print, PESQUISE NA INTERNET.\n"
"Somente utilize 'dados insuficientes' quando o jogo não puder ser identificado corretamente ou quando, após realizar a pesquisa, não houver informações confiáveis suficientes para analisar aquela partida.\n"
"Mesmo nesse caso, continue analisando os demais jogos do print que possam ser identificados e pesquisados.\n"
"Se uma partida não puder ser analisada, informe apenas aquela partida como 'SEM ENTRADA', sem interromper a análise dos outros jogos.\n\n"

"REGRA FINAL:\n"
"O usuário envia o PRINT.\n"
"Você identifica os jogos.\n"
"Você pesquisa os dados na internet.\n"
"Você encontra os melhores mercados.\n"
"Você cria VÁRIAS oportunidades.\n"
"Você monta SIMPLES, DUPLAS e TRIPLAS.\n"
"Você apresenta primeiro o CARD.\n"
"Depois apresenta as JUSTIFICATIVAS.\n"
"Por último apresenta as FONTES utilizadas.\n"
"Nunca transforme a análise em apenas um único bilhete quando houver vários jogos disponíveis no print.\n"
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
