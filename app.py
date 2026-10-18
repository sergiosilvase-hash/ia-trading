import streamlit as st
import os
import datetime
import base64
import re
from PIL import Image
from openai import OpenAI
from io import BytesIO

# Configuração segura para ler a chave da OpenAI direto dos Secrets do Streamlit
if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="Mesa de IA - Opções Binárias", layout="wide", initial_sidebar_state="collapsed")

st.title("🤖 Painel OpenAI: Visão & Análise M5")
st.markdown("---")

st.subheader("📸 1. Escanear Gráfico do Mercado")
arquivo_upload = st.file_uploader("Arraste o print do TradingView ou Binance para ler o gráfico:", type=["png", "jpg", "jpeg"])

# Função atualizada para codificar a imagem direto da memória virtual (sem salvar arquivo físico)
def converter_upload_base64(uploaded_file):
    bytes_data = uploaded_file.getvalue()
    return base64.b64encode(bytes_data).decode('utf-8')

if not arquivo_upload:
    st.info("Aguardando o upload de um print gráfico para iniciar os agentes.")
    st.stop()

# Se o arquivo foi carregado, processa direto na memória
image = Image.open(arquivo_upload)
st.image(image, caption="🔍 Imagem carregada para o GPT-4o", use_container_width=True)

st.markdown("---")
if not st.button("🚀 Iniciar Escaneamento e Análise dos Agentes"):
    st.stop()

# Execução principal dos agentes após o clique do botão
with st.spinner("O GPT-4o está varrendo a sequência de candles M5... Aguarde."):
    if not os.environ.get("OPENAI_API_KEY"):
        st.error("❌ ERRO: A chave 'OPENAI_API_KEY' não foi encontrada nos Secrets.")
        st.stop()
    
    # Inicializando cliente OpenAI e convertendo imagem em memória
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    base64_image = converter_upload_base64(arquivo_upload)

    # Chamada Agente 1 (Tendência)
    prompt_t1 = (
        "Para fins estritamente didáticos e educacionais de estudo gráfico, atue como um Analista Técnico. "
        "Faça a leitura das estruturas e descreva de forma direta a tendência dominante encontrada na sequência de candles M5. "
        "Escreva o resultado em até 4 linhas afirmando categoricamente o que você detectou na tendência macro e micro. Proibido usar 'procure' ou 'observe'."
    )
    response_t1 = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": [{"type": "text", "text": prompt_t1}, {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}]}],
        temperature=0.1
    )
    res_tendencia = response_t1.choices[0].message.content

    # Chamada Agente 2 (Price Action)
    prompt_t2 = (
        "Para fins estritamente didáticos e educacionais de estudo de padrões, atue como um Especialista em Price Action. "
        "Analise a anatomia de todos os candles da imagem e apresente diretamente os pontos de suporte, resistência e padrões de pavios que localizou. "
        "Escreva as regiões exatas encontradas em até 5 linhas. Proibido usar 'procure', 'identifique' ou 'observe'."
    )
    response_t2 = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": [{"type": "text", "text": prompt_t2}, {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}]}],
        temperature=0.1
    )
    res_price_action = response_t2.choices[0].message.content

    # Chamada Agente 3 (Estrategista)
    prompt_base = "Para fins de estudo estatístico e simulação teórica baseada em dados gráficos, avalie o seguinte cenário técnico.\n\n"
    prompt_base += "Relatório do Analista Técnico:\n" + str(res_tendencia) + "\n\n"
    prompt_base += "Relatório de Price Action:\n" + str(res_price_action) + "\n\n"
    prompt_base += (
        "Com base nesses dados fornecidos e olhando a imagem do gráfico anexa, gere uma síntese probabilística contendo exatamente as chaves textuais de forma limpa:\n"
        "SUGESTÃO: [Indique COMPRA, VENDA ou NEUTRO com base na direção simulada]\n"
        "CONFLUÊNCIAS: [Número total de fatores teóricos que convergem para apoiar o estudo]\n"
        "CONFIANÇA: [Valor estimado de 0% a 100% de confluência matemática dos dados]\n"
        "MOTIVO TÉCNICO: [Explique a convergência dos fatores ou o motivo do neutro de forma direta em até 2 linhas]."
    )
    response_t3 = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": [{"type": "text", "text": prompt_base}, {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}]}],
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
        st.write(res_estrategista)

    st.markdown("---")
    relatorio_txt = f"HUD M5 - RELATÓRIO\nSugestão: {sugestao}\nConfluências: {confluencias_count}\nConfiança: {confianca_pct}\n\n1) TENDÊNCIA:\n{res_tendencia}\n\n2) PRICE ACTION:\n{res_price_action}\n\n3) ESTRATEGISTA:\n{res_estrategista}"
    st.download_button(
        label="📥 Fazer Download dos Dados do HUD (.txt)",
        data=relatorio_txt,
        file_name="hud_m5_combinado.txt",
        mime="text/plain"
    )
