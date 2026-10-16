import os
import streamlit as st
from PIL import Image
import google.generativeai as genai

# Configuração da chave oficial ativa do Gemini
CHAVE_GEMINI = "AQ.Ab8RN6KbT084eC7xHcVDtmNZM0eHYZTxmumZOO3Wr8m_gaXYpA"
genai.configure(api_key=CHAVE_GEMINI)

# CONFIGURAÇÃO DA INTERFACE RESPONSIVA DO SCANNER
st.set_page_config(page_title="Scanner IA - Inteligência M5", layout="wide", initial_sidebar_state="collapsed")

# Estilização em CSS moderno (Dark Mode focado em Trading)
st.markdown("""
    <style>
    .main { background-color: #060913; color: #ffffff; }
    .card { background-color: #111827; padding: 18px; border-radius: 10px; border: 1px solid #1f2937; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    .title-app { font-size: 26px; font-weight: bold; color: #6366f1; text-align: center; margin-bottom: 5px; }
    .subtitle-app { font-size: 14px; color: #9ca3af; text-align: center; margin-bottom: 25px; }
    .metric-val { font-size: 22px; font-weight: bold; margin-top: 8px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='title-app'>🔍 SCANNER DE SINAIS MULTIFUNCIONAL IA (M5)</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle-app'>Cole, envie ou fotografe o gráfico para análise instantânea</div>", unsafe_allow_html=True)

# Abas interativas para selecionar a forma de envio do gráfico
aba_upload, aba_camera = st.tabs(["📁 Colar Print ou Enviar Arquivo", "📸 Escanear com a Câmera"])

arquivo_imagem = None

with aba_upload:
    st.markdown("### 💻 Desktop / Mobile")
    upload_print = st.file_uploader(
        "Clique aqui e dê Ctrl + V para colar o print, ou arraste o arquivo do gráfico:", 
        type=["png", "jpg", "jpeg"]
    )
    if upload_print:
        arquivo_imagem = upload_print

with aba_camera:
    st.markdown("### 📱 Celular / Tablet / Webcam")
    captura_foto = st.camera_input("Aponte para o gráfico da corretora e tire a foto para escanear:")
    if captura_foto:
        arquivo_imagem = captura_foto

# Se houver imagem capturada, inicia o processamento direto pela API do Google
if arquivo_imagem is not None:
    imagem = Image.open(arquivo_imagem)
    st.image(imagem, caption="Gráfico Carregado no Sistema", use_container_width=True)
    
    with st.spinner("⚡ Mesa de Operações Ativa: Agentes debatendo as confluências em M5..."):
        try:
            prompt_agentes = """
            Você é um sistema de Inteligência Artificial operando como uma Mesa de Operações com 3 Agentes Especialistas:
            1. Agente Analista Técnico: Avalia tendências macro/micro e localiza o horário exato impresso nos eixos do print ou no relógio regressivo da vela para projetar a próxima entrada em gráficos de M5.
            2. Agente Price Action: Mapeia suportes, resistências e conta rigorosamente a quantidade de confluências presentes (gatilhos técnicos).
            3. Agente Estrategista: Valida os dados de risco e consolida o veredito final focando em assertividade acima de 75%.

            Analise minuciosamente a imagem do gráfico fornecida e retorne a resposta ESTREITAMENTE no formato de chaves abaixo para preencher o layout da interface gráfica. Não escreva introduções ou textos explicativos fora do padrão:

            HORARIO_ENTRADA: [Insira o horário exato projetado para a entrada em formato HH:MM]
            DIRECAO: [CALL, PUT ou NEUTRO]
            CONFLUENCIAS: [Insira apenas o número inteiro de confluências encontradas, ex: 3]
            CONFIANCA: [Insira a porcentagem estimada de acerto de 0% a 100%]
            RESUMO: [Escreva um resumo didático, curto e condensado explicando os motivos técnicos dos 3 analistas]
            """
            
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content([prompt_agentes, imagem])
            resultado = response.text
            
            # CONVERSÃO DOS DADOS EM VARIÁVEIS VISUAIS
            linhas = resultado.split('\n')
            dados = {"HORARIO_ENTRADA": "N/A", "DIRECAO": "NEUTRO", "CONFLUENCIAS": "0", "CONFIANCA": "0%", "RESUMO": "Sem dados."}
            for linha in linhas:
                for chave in dados.keys():
                    if linha.strip().startswith(f"{chave}:"):
                        dados[chave] = linha.replace(f"{chave}:", "").strip()

            # LAYOUT DAS 4 COLUNAS INTERATIVAS
            st.markdown("### 📊 PAINEL DE VEREDITO DO SCANNER")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"<div class='card'>⏰ <b>HORÁRIO DE ENTRADA</b><div class='metric-val' style='color:#f39c12;'>{dados['HORARIO_ENTRADA']}</div></div>", unsafe_allow_html=True)
            
            with col2:
                cor_sinal = "#2ecc71" if "CALL" in dados["DIRECAO"] else "#e74c3c" if "PUT" in dados["DIRECAO"] else "#9ca3af"
                st.markdown(f"<div class='card'>📈 <b>SUGESTÃO</b><div class='metric-val' style='color:{cor_sinal};'>{dados['DIRECAO']}</div></div>", unsafe_allow_html=True)
                
            with col3:
                st.markdown(f"<div class='card'>🎯 <b>CONFLUÊNCIAS</b><div class='metric-val' style='color:#3498db;'>{dados['CONFLUENCIAS']} Gatilhos</div></div>", unsafe_allow_html=True)
                
            with col4:
                st.markdown(f"<div class='card'>🛡️ <b>CONFIANÇA</b><div class='metric-val' style='color:#a855f7;'>{dados['CONFIANCA']}</div></div>", unsafe_allow_html=True)

            st.markdown("---")
            st.markdown("*📝 Justificativa de Estudo dos 3 Analistas:*")
            st.info(dados["RESUMO"])

            # RECURSO DE DOWNLOAD PARA ESTUDOS
            relatorio_texto = f"=== RELATÓRIO DE ESTUDO IA ===\nEntrada: {dados['HORARIO_ENTRADA']}\nOperação: {dados['DIRECAO']}\nGatilhos: {dados['CONFLUENCIAS']}\nConfiança: {dados['CONFIANCA']}\n\nMotivo:\n{dados['RESUMO']}"
            st.download_button(label="💾 Baixar Relatório Técnico para Estudo", data=relatorio_texto, file_name="estudo_m5.txt", mime="text/plain")
            
        except Exception as e:
            st.error(f"Erro de processamento da API: {e}")
