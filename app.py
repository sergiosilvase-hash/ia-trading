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

                # Chamada Agente 1 (Tendência) - CORRIGIDO ÍNDICE [0]
                prompt_t1 = "Você é o Agente Analista Técnico. Descreva de 3 a 5 linhas a tendência dominante encontrada na sequência de candles M5 desta imagem."
                response_t1 = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": [{"type": "text", "text": prompt_t1}, {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}]}],
                    temperature=0.1
                )
                res_tendencia = response_t1.choices[0].message.content

                # Chamada Agente 2 (Price Action) - CORRIGIDO ÍNDICE [0]
                prompt_t2 = "Você é o Agente Especialista em Price Action. Identifique de 3 a 5 linhas as zonas de suporte, resistência e anatomia dos pavios visíveis na imagem."
                response_t2 = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": [{"type": "text", "text": prompt_t2}, {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}]}],
                    temperature=0.1
                )
                res_price_action = response_t2.choices[0].message.content

                # Chamada Agente 3 (Estrategista) - CORRIGIDO ÍNDICE [0]
                prompt_t3 = f"Com base nas análises de Tendência ({res_tendencia}) e Price Action ({res_price_action}), defina o veredito em formato de texto contendo as palavras exatas: SUGESTÃO: [COMPRA, VENDA ou NEUTRO], CONFLUÊNCIAS: [X/Y], CONFIANÇA: [BAIXA, MÉDIA ou ALTA]."
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
                
                confianca = "BAIXA"
                if "ALTA" in res_upper: confianca = "ALTA"
                elif "MÉDIA" in res_upper or "MEDIA" in res_upper: confianca = "MÉDIA"
                
                confluencias_count = "3/15"
                import re
                match = re.search(r"CONFLUÊNCIAS:\s*(\d+/\d+)", res_upper)
                if match:
                    confluencias_count = match.group(1)
                elif sugestao != "NEUTRO":
                    confluencias_count = "12/15"

                # 📊 RENDERIZAÇÃO DA INTERFACE NATIVA
                st.success("✅ Escaneamento Completo!")
                
                st.markdown("### 📊 HUD M5 - Painel de Confluências Combinadas")
                
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.metric(label="Sugestão M5", value=sugestao)
                with c2:
                    st.metric(label="Confluências Totais", value=confluencias_count)
                with c3:
                    st.metric(label="Confiança das Análises", value=confianca)
                with c4:
                    if congestao_upper := sugestao.upper() != "NEUTRO":
                        hora_brasilia = (datetime.datetime.utcnow() - datetime.timedelta(hours=3)).strftime("%H:%M")
                        st.metric(label="Horário de Entrada", value=hora_brasilia)
                    else:
                        st.metric(label="Horário de Entrada", value="FORA DE MERCADO")

                # Exibe as caixas de texto estruturadas com os resumos de cada um dos agentes
                st.markdown("---")
                st.markdown("#### 🧠 Interpretação e Resumos dos Agentes")
                
                with st.expander("1) Agente Analista Técnico (Tendência Sequencial M5)", expanded=True):
                    st.write(res_tendencia)
                    
                with st.expander("2) Agente Price Action (Suportes e Anatomia das Velas)", expanded=True):
                    st.write(res_price_action)
                    
                with st.expander("3) Agente Estrategista (Veredito Combinado de Risco)", expanded=True):
                    st.write(res_estrategista)

                # Relatório consolidado para download (.txt)
                st.markdown("---")
                relatorio_txt = f"HUD M5 - RELATÓRIO\nSugestão: {sugestao}\nConfluências: {confluencias_count}\nConfiança: {confianca}\n\n1) TENDÊNCIA:\n{res_tendencia}\n\n2) PRICE ACTION:\n{res_price_action}\n\n3) ESTRATEGISTA:\n{res_estrategista}"
                st.download_button(
                    label="📥 Fazer Download dos Dados do HUD (.txt)",
                    data=relatorio_txt,
                    file_name="hud_m5_combinado.txt",
                    mime="text/plain"
                )

            except Exception as e:
                st.error("Ocorreu um erro na execução dos agentes da OpenAI.")
                st.exception(e)
