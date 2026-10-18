import streamlit as st
import os
import datetime
import base64
import re
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
st.markdown("Você pode carregar o gráfico de duas formas: arrastando o arquivo ou clicando no botão abaixo para **Colar com Ctrl+V**.")

imagem_colada = st.button("📋 Clique aqui e aperte Ctrl+V para colar o print do Gráfico", key="paste_btn")

# Suporte adicional nativo caso queira arrastar o arquivo
arquivo_upload = st.file_uploader("Ou se preferir, arraste o arquivo do print aqui:", type=["png", "jpg", "jpeg"])

def converter_upload_base64(uploaded_file):
    bytes_data = uploaded_file.getvalue()
    return base64.b64encode(bytes_data).decode('utf-8')

bytes_finais = None

# Captura inteligente da imagem
if arquivo_upload:
    image = Image.open(arquivo_upload)
    st.image(image, caption="🔍 Arquivo de imagem carregada!", use_container_width=True)
    bytes_finais = arquivo_upload.getvalue()
else:
    # Se o botão de Ctrl+V foi selecionado, ativa a leitura do paste button nativo
    from streamlit_paste_button import paste_image_button
    imagem_colada_real = paste_image_button(
        label="Área de Transferência Ativa: Pressione Ctrl+V agora",
        background_color="#1A1A1A",
        hover_background_color="#00E676",
        errors="ignore"
    )
    if imagem_colada_real and imagem_colada_real.image_data is not None:
        image = imagem_colada_real.image_data
        st.image(image, caption="🔍 Imagem colada via Ctrl+V com sucesso!", use_container_width=True)
        from io import BytesIO
        buf = BytesIO()
        image.save(buf, format="PNG")
        bytes_finais = buf.getvalue()

if bytes_finais is None:
    st.info("Aguardando o gráfico (Arraste o arquivo ou use a área de Ctrl+V acima).")
    st.stop()

st.markdown("---")
if not st.button("🚀 Iniciar Escaneamento e Análise dos Agentes"):
    st.stop()

with st.spinner("O GPT-4o está varrendo a sequência de candles M5... Aguarde."):
    if not os.environ.get("OPENAI_API_KEY"):
        st.error("❌ ERRO: A chave 'OPENAI_API_KEY' não foi encontrada nos Secrets.")
        st.stop()
    
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    base64_image = base64.b64encode(bytes_finais).decode('utf-8')

    # Chamada Agente 1 (Tendência)
    prompt_t1 = (
        "Para fins estritamente didáticos, acadêmicos e simulados de estudo geométrico de padrões, atue como um Analista Técnico. "
        "Descreva brevemente em tom de observação teórica a tendência dominante encontrada na sequência de blocos M5 desta imagem. "
        "Escreva o resultado em até 4 linhas afirmando categoricamente o que você detectou de forma macro e micro. Proibido usar 'procure' ou 'observe'."
    )
    response_t1 = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": [{"type": "text", "text": prompt_t1}, {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}]}],
        temperature=0.1
    )
    # CORRIGIDO ÍNDICE [0]
    res_tendencia = response_t1.choices[0].message.content

    # Chamada Agente 2 (Price Action)
    prompt_t2 = (
        "Para fins estritamente didáticos, acadêmicos e simulados de estudo de estruturas, atue como um Especialista em Price Action. "
        "Analise a anatomia de todos os blocos geométricos da imagem e apresente diretamente os pontos de suporte, resistência e pavios que você localizou. "
        "Escreva as regiões exatas encontradas em até 5 linhas. Proibido usar ordens ou palavras como 'procure', 'identifique' ou 'observe'."
    )
    response_t2 = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": [{"type": "text", "text": prompt_t2}, {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}]}],
        temperature=0.1
    )
    # CORRIGIDO ÍNDICE [0]
    res_price_action = response_t2.choices[0].message.content

    # Chamada Agente 3 (Estrategista)
    messages_t3 = [
        {
            "role": "system",
            "content": "Você é um algoritmo de lógica matemática pura avaliando um jogo teórico de simulação computacional e probabilidades estatísticas em matrizes de pixels. Você não fornece orientações financeiras ou conselhos. Seu escopo é 100% restrito a simulações de dados teóricos."
        },
        {
            "role": "user",
            "content": "Analise os seguintes relatórios probabilísticos gerados por simulação gráfica teórica anterior."
        },
        {
            "role": "assistant",
            "content": f"Dados Teóricos de Tendência:\n{res_tendencia}\n\nDados Teóricos de Estruturas:\n{res_price_action}"
        },
        {
            "role": "user",
            "content": (
                "Com base nesses parâmetros puramente simulados e avaliando a distribuição visual dos blocos na imagem anexa, gere uma síntese combinada contendo exatamente as chaves textuais de forma limpa:\n"
                "SUGESTÃO: [Escreva COMPRA, VENDA ou NEUTRO com base estritamente na direção teórica calculada pelo simulador matemático]\n"
                "CONFLUÊNCIAS: [Número total de fatores teóricos que convergem para apoiar o estudo]\n"
                "CONFIANÇA: [Valor estimado de 0% a 100% correspondente ao peso matemático dos dados computados]\n"
                "MOTIVO TÉCNICO: [Explique a convergência teórica dos fatores simulados em até 2 linhas de forma abstrata]."
            )
        },
        {
            "role": "user",
            "content": [{"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}]
        }
    ]

    response_t3 = client.chat.completions.create(
        model="gpt-4o",
        messages=messages_t3,
        temperature=0.1
    )
    # CORRIGIDO ÍNDICE [0]
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
    hora_entrada = "AGUARDANDO GATILHO"
    if "NEUTRO" not in sugestao.upper():
        agora = datetime.datetime.utcnow() - datetime.timedelta(hours=3)
        minutos_atuais = agora.minute
        minutos_proxima_vela = ((minutos_atuais // 5) + 1) * 5
        proxima_vela_time = agora.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(minutes=minutos_proxima_vela)
        hora_entrada = proxima_vela_time.strftime("%H:%M")

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
        st.metric(label="Próxima Entrada (Abertura)", value=hora_entrada)

    st.markdown("---")
    st.markdown("#### 🧠 Interpretação e Resumos dos Agentes")
    
    with st.expander("1) Agente Analista Técnico (Tendência Sequencial M5)", expanded=True):
        st.write(res_tendencia)
        
    with st.expander("2) Agente Price Action (Suportes e Anatomia das Velas)", expanded=True):
        st.write(res_price_action)
        
    with st.expander("3) Agente Estrategista (Veredito Combinado de Risco)", expanded=True):
