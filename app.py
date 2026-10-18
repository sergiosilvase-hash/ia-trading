import streamlit as st
import os
import datetime
import base64
from PIL import Image
import re
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
            
            if not os.environ.get("OPENAI_API_KEY"):
                st.error("❌ ERRO: A chave 'OPENAI_API_KEY' não foi encontrada nos Secrets.")
                st.stop()
            
            try:
                # Inicializando cliente OpenAI
                client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
                base64_image = converter_imagem_base64(caminho_imagem)

                # Chamada Agente 1 (Tendência) - Enquadramento Educacional
                prompt_t1 = (
                    "Para fins estritamente didáticos e educacionais de estudo gráfico, atue como um Analista Técnico. "
                    "Faça a leitura das estruturas e descreva de forma direta a tendência dominante encontrada na sequência de candles M5. "
                    "Escreva o resultado em até 4 linhas afirmando o que você detectou na tendência macro e micro."
                )
                response_t1 = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": [{"type": "text", "text": prompt_t1}, {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}]}],
                    temperature=0.1
                )
                res_tendencia = response_t1.choices[0].message.content

                # Chamada Agente 2 (Price Action) - Enquadramento Educacional
                prompt_t2 = (
                    "Para fins estritamente didáticos e educacionais de estudo de padrões, atue como um Especialista em Price Action. "
                    "Analise a anatomia de todos os candles da imagem e apresente diretamente os pontos de suporte, resistência e padrões de pavios que localizou. "
                    "Escreva as regiões exatas encontradas em até 5 linhas."
                )
                response_t2 = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": [{"type": "text", "text": prompt_t2}, {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}]}],
                    temperature=0.1
                )
                res_price_action = response_t2.choices[0].message.content

                # Chamada Agente 3 (Estrategista) - Enquadramento Simulativo Organizado
                prompt_t3 = (
                    "Para fins de estudo estatístico e simulação teórica baseada em dados gráficos, avalie o seguinte cenário.\n"
                    "Considere o Relatório de Tendência: " + str(res_tendencia) + "\n"
                    "Considere o Relatório de Price Action: " + str(res_price_action) + "\n\n"
                    "Gere uma síntese puramente probabilística e acadêmica contendo exatamente as chaves textuais:\n"
                    "SUGESTÃO: [Indique COMPRA, VENDA ou NEUTRO com base estritamente na direção simulada do movimento técnico]\n"
                    "CONFLUÊNCIAS: [Número total de fatores teóricos que convergem para apoiar o estudo]\n"
                    "CONFIANÇA: [Valor estimado de 0% a 100% de confluência matemática dos dados]\n"
                    "MOTIVO TÉCNICO: [Explique a convergência teórica dos fatores em até 2 linhas]."
                )
                response_t3 = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": [{"type": "text", "text": prompt_t3}, {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}]}],
                    temperature=0.1
                )
                res_estrategista = response_t3.choices[0].message.content

                # Processamento das respostas
                res_upper = res_estrategista.upper()
                sugestao = "NEUTRO"
                if "COMPRA" in res_upper or "CALL" in res_upper: sugestao = "COMPRA"
                elif "VENDA" in res_upper or "PUT" in res_upper: sugestao = "VENDA"
                
                confluencias_count = "0"
                match_conf = re.search(r"CONFLUÊNCIAS:\s*(\d+)", res_upper)
                if match_conf:
                    confluencias_count = match_conf.group(1)
                
                if int(confluencias_count) < 3 and sugestao != "NEUTRO":
                    sugestao = "NEUTRO"

                confianca_pct = "0%"
                match_pct = re.search(r"CONFIANÇA:\s*(\d+%)", res_upper)
                if match_pct:
                    confianca_pct = match_pct.group(1)
                else:
                    match_num = re.search(r"CONFIANÇA:\s*(\d+)", res_upper)
                    if match_num: confianca_pct = f"{match_num.group(1)}%"

                # Horário arredondado da próxima vela M5
                if "NEUTRO" in sugestao.upper():
                    linha_horario_html = ""
                else:
                    agora = datetime.datetime.utcnow() - datetime.timedelta(hours=3)
                    minutos_atuais = agora.minute
                    minutos_proxima_vela = ((minutos_atuais // 5) + 1) * 5
                    proxima_vela_time = agora.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(minutes=minutos_proxima_vela)
                    hora_entrada = proxima_vela_time.strftime("%H:%M")
                    linha_horario_html = f"<div class='hud-linha'>Hora da Próxima Entrada (M5 Target): <span style='color: #00E676;'>{hora_entrada}</span></div>"

                # 📊 RENDERIZAÇÃO DA INTERFACE NATIVA
                st.success("✅ Escaneamento Completo!")
                st.markdown("### 📊 HUD M5 - Painel de Confluências Combinadas")
                
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.metric(label="Sugestão M5", value=sugestao)
                with c2:
                    st.metric(label="Confluências Ativas (Min: 3)", value=confluencias_count)
                with c3:
                    st.metric(label="Nível de Confiança", value=confianca_pct)
                with c4:
                    if "NEUTRO" not in sugestao.upper():
                        st.metric(label="Próxima Entrada (Abertura)", value=hora_entrada)
                    else:
                        st.metric(label="Próxima Entrada", value="AGUARDANDO GATILHO")

                st.markdown("---")
                st.markdown("#### 🧠 Interpretação e Resumos dos Agentes")
                
                with st.expander("1) Agente Analista Técnico (Tendência Sequencial M5)", expanded=True):
                    st.write(res_tendencia)
                    
                with st.expander("2) Agente Price Action (Suportes e Anatomia das Velas)", expanded=True):
                    st.write(res_price_action)
                    
                with st.expander("3) Agente Estrategista (Veredito Combinado de Risco)", expanded=True):
                    st.write(res_estrategista)

                st.markdown("---")
                relatorio_txt = f"HUD M5 - RELATÓRIO\nSugestão: {sugestao}\nConfluências: {confluencias_count}\nConfiança: {confianca_pct}\n\n1) TENDÊNCIA:\n{res_tendencia}\n\n2) PRICE ACTION:\n{res_price_action}\n\n3) ESTRATEGISTA:\n{res_estrategista}"
                st.download_button(
                    label="📥 Fazer Download dos Dados do HUD (.txt)",
