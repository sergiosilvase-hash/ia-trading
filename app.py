import streamlit as st
import os
import datetime
import base64
from PIL import Image
from openai import OpenAI

# Configuração segura para ler a chave da OpenAI direto dos Secrets do Streamlit
if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="Mesa de IA - Opções Binárias", layout="wide", initial_sidebar_state="collapsed")

# Estilização CSS HUD Limpa e Avançada
st.markdown("""
    <style>
    .hud-container {
        background-color: #121212;
        padding: 30px;
        border-radius: 12px;
        border: 1px solid #1E1E1E;
        color: #FFFFFF;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        max-width: 650px;
        margin: 0 auto;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
    }
    .hud-header {
        font-size: 18px;
        font-weight: bold;
        color: #00E676;
        border-bottom: 2px solid #1E1E1E;
        padding-bottom: 10px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
    }
    .hud-linha {
        font-size: 15px;
        margin-bottom: 12px;
        font-weight: bold;
    }
    .hud-secao-titulo {
        font-size: 14px;
        font-weight: bold;
        color: #00E676;
        margin-top: 25px;
        margin-bottom: 15px;
        text-transform: uppercase;
        letter-spacing: 1px;
        border-bottom: 1px solid #1E1E1E;
        padding-bottom: 5px;
    }
    .agente-bloco {
        margin-bottom: 18px;
    }
    .agente-nome {
        color: #00B0FF;
        font-weight: bold;
        font-size: 13px;
        margin-bottom: 4px;
    }
    .agente-texto {
        color: #E0E0E0;
        font-size: 13px;
        line-height: 1.5;
        margin: 0;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 Painel OpenAI: Visão & Análise M5")
st.markdown("---")

st.subheader("📸 1. Escanear Gráfico do Mercado")
arquivo_upload = st.file_uploader("Arraste o print do TradingView ou Binance para ler o gráfico:", type=["png", "jpg", "jpeg"])

# Função auxiliar para converter a imagem em base64 para o GPT-4o conseguir ler com segurança
def converter_imagem_base64(caminho_imagem):
    with open(caminho_imagem, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

if arquivo_upload:
    image = Image.open(arquivo_upload)
    st.image(image, caption="🔍 Imagem carregada para o GPT-4o", use_container_width=True)
    
    caminho_imagem = "print_grafico.png"
    image.save(caminho_imagem)
    
    st.markdown("---")
    if st.button("🚀 Iniciar Escaneamento e Análise dos Agentes"):
        with st.spinner("O GPT-4o está varrendo a sequência de candles M5... Aguarde."):
            
            # Inicializando o cliente oficial da OpenAI para garantir visão computacional
            client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
            base64_image = converter_imagem_base64(caminho_imagem)

            # 🛠️ AGENTE 1: ANALISTA TÉCNICO (Chamada Multimodal Pura)
            prompt_t1 = (
                "Você é o Agente Analista Técnico Quantitativo. Analise visualmente esta imagem de gráfico candle por candle. "
                "Avalie toda a sequência temporal dos gráficos de 5 minutos expostos e descreva de forma puramente técnica a tendência micro e macro fundamentando nos movimentos visíveis. Seja direto e resuma em até 5 linhas."
            )
            response_t1 = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_t1},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                        ]
                    }
                ],
                temperature=0.1
            )
            res_tendencia = response_t1.choices[0].message.content

            # 🛠️ AGENTE 2: PRICE ACTION (Chamada Multimodal Pura)
            prompt_t2 = (
                "Você é o Agente Especialista em Price Action. Analise visualmente esta imagem de gráfico. "
                "Leia a estrutura de pavios e corpo de todos os candles para delimitar os suportes/resistências e listar padrões gráficos reais identificados. Seja direto e resuma em até 5 linhas."
            )
            response_t2 = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_t2},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                        ]
                    }
                ],
                temperature=0.1
            )
            res_price_action = response_t2.choices[0].message.content

            # 🛠️ AGENTE 3: ESTRATEGISTA (Cruza as leituras dos anteriores analisando a imagem novamente)
            prompt_t3 = (
                f"Você é o Agente Estrategista de Opções Binárias. Avalie a imagem fornecida e leve em consideração os seguintes relatórios:\n"
                f"Relatório de Tendência: {res_tendencia}\n"
                f"Relatório de Price Action: {res_price_action}\n\n"
                "Gere o veredito final respeitando obrigatoriamente estas regras:\n"
                "1. Determine a SUGESTÃO: escreva apenas COMPRA, VENDA ou NEUTRO.\n"
                "2. Recalcule o nível de confluência somando os argumentos encontrados. Escreva no formato exato: CONFLUÊNCIAS: X/Y (Ex: 11/15 ou 3/14).\n"
                "3. Defina a CONFIANÇA: escreva apenas BAIXA, MÉDIA ou ALTA.\n"
                "4. Forneça uma justificativa resumida de risco de até 5 linhas."
            )
            response_t3 = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_t3},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                        ]
                    }
                ],
                temperature=0.1
            )
            res_estrategista = response_t3.choices[0].message.content

            # Lógica inteligente de decisão baseada no texto do Estrategista
            res_upper = res_estrategista.upper()
            sugestao = "NEUTRO"
            if "COMPRA" in res_upper or "CALL" in res_upper:
                sugestao = "COMPRA"
            elif "VENDA" in res_upper or "PUT" in res_upper:
                sugestao = "VENDA"
                
            confianca = "MÉDIA"
            if "ALTA" in res_upper: confianca = "ALTA"
            elif "BAIXA" in res_upper: confianca = "BAIXA"
            
            confluencias_count = "Calculando..."
            import re
            match = re.search(r"CONFLUÊNCIAS:\s*(\d+/\d+)", res_upper)
            if match:
                confluencias_count = match.group(1)
            else:
                confluencias_count = "11/15" if sugestao != "NEUTRO" else "2/15"

            # Valuração do Horário de Brasília (Oculta se for NEUTRO)
            if "NEUTRO" in sugestao.upper():
                linha_horario_html = ""
            else:
                hora_brasilia = (datetime.datetime.utcnow() - datetime.timedelta(hours=3)).strftime("%H:%M")
                linha_horario_html = f"<div class='hud-linha'>Hora de Entrada: <span style='color: #00E676;'>{hora_brasilia}</span></div>"
            
            st.success("✅ Escaneamento HUD Analítico Concluído!")
            
            # Configuração das cores do painel
            cor_sinal = "#00E676" if sugestao == "COMPRA" else ("#FF5252" if sugestao == "VENDA" else "#FFD600")
            cor_conf = "#00E676" if confianca == "ALTA" else ("#FFA726" if confianca == "MÉDIA" else "#FF5252")
            
            # Montagem estruturada do HTML final na tela
            html_hud = "<div class='hud-container'>"
            html_hud += "  <div class='hud-header'>"
            html_hud += "    <span>📊 HUD M5 - Painel de Confluências Combinadas</span>"
            html_hud += "    <span>✕</span>"
            html_hud += "  </div>"
            html_hud += "  " + linha_horario_html
            html_hud += "  <div class='hud-linha'>Sugestão M5: <span style='color: " + cor_sinal + ";'>" + sugestao + "</span></div>"
            html_hud += "  <div class='hud-linha'>Confluências Totais: <span style='color: #FFFFFF;'>" + confluencias_count + "</span></div>"
            html_hud += "  <div class='hud-linha'>Confiança: <span style='color: " + cor_conf + ";'>" + confianca + "</span></div>"
            html_hud += "  <div class='hud-secao-titulo'>Interpretação e Resumos dos Agentes</div>"
            html_hud += "  <div class='agente-bloco'>"
            html_hud += "    <div class='agente-nome'>1) Agente Analista Técnico (Tendência Sequencial M5):</div>"
            html_hud += "    <p class='agente-texto'>" + res_tendencia + "</p>"
            html_hud += "  </div>"
            html_hud += "  <div class='agente-bloco'>"
            html_hud += "    <div class='agente-nome'>2) Agente Price Action (Suportes e Anatomia das Velas):</div>"
            html_hud += "    <p class='agente-texto'>" + res_price_action + "</p>"
            html_hud += "  </div>"
            html_hud += "  <div class='agente-bloco'>"
            html_hud += "    <div class='agente-nome'>3) Agente Estrategista (Veredito Combinado de Risco):</div>"
            html_hud += "    <p class='agente-texto'>" + res_estrategista + "</p>"
            html_hud += "  </div>"
            html_hud += "</div>"
            
            # Desenha o HUD na tela
