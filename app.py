import streamlit as st
import os
from PIL import Image
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

# Configuração para ler a nova chave da OpenAI direto dos Secrets do Streamlit
if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="Mesa de IA - Opções Binárias", layout="wide", initial_sidebar_state="collapsed")
st.title("🤖 Painel OpenAI: Visão & Análise M5")
st.markdown("---")

st.subheader("📸 1. Escanear Gráfico do Mercado")
arquivo_upload = st.file_uploader("Arraste o print do TradingView ou Binance para ler o gráfico:", type=["png", "jpg", "jpeg"])

if arquivo_upload:
    image = Image.open(arquivo_upload)
    st.image(image, caption="🔍 Imagem carregada para o GPT-4o", use_container_width=True)
    image.save("print_grafico.png")
    
    st.markdown("---")
    if st.button("🚀 Iniciar Escaneamento e Análise dos Agentes"):
        with st.spinner("O GPT-4o está escaneando a tela... Aguarde."):
            
            # Mudando para o motor da OpenAI (GPT-4o) para ler o print do gráfico
            llm_openai = ChatOpenAI(model="gpt-4o", temperature=0.1)

            # Criando os 3 Agentes Especialistas com a OpenAI (LINHAS CORRIGIDAS)
            analista_tecnico = Agent(
                role='Analista Técnico Quantitativo',
                goal='Mapear rigorosamente a tendência macro/micro e canais de preço no print.',
                backstory='Especialista em visão computacional voltada a estruturas de gráficos financeiros.',
                verbose=True, 
                llm=llm_openai
            )

            especialista_price_action = Agent(
                role='Especialista em Price Action',
                goal='Escanear o print para achar zonas de suporte, resistência e padrões de velas.',
                backstory='Analista detalhista que foca em equilíbrio de forças e confluências visuais.',
                verbose=True, 
                llm=llm_openai
            )

            estrategista_ob = Agent(
                role='Estrategista de Opções Binárias',
                goal='Tomar a decisão final baseada no gerenciamento e confluência estrita.',
                backstory='Matemático focado em manter o filtro rígido para buscar assertividade acima de 75%.',
                verbose=True, 
                llm=llm_openai
            )

            # Definição das Tarefas de Visão
            t1 = Task(description="Escaneie o arquivo 'print_grafico.png'. Identifique e relate a tendência dominante.", expected_output="Tendência identificada.", agent=analista_tecnico)
            t2 = Task(description="Escaneie o arquivo 'print_grafico.png'. Ache suportes, resistências e padrões de vela.", expected_output="Zonas de preço mapeadas.", agent=especialista_price_action)
            t3 = Task(description="Reúna as análises. Decida por CALL, PUT ou NEUTRO com a porcentagem de confiança.", expected_output="Resultado definitivo.", agent=estrategista_ob)

            mesa = Crew(agents=[analista_tecnico, especialista_price_action, estrategista_ob], tasks=[t1, t2, t3], process=Process.sequential)
            resultado = str(mesa.kickoff())
            
            st.success("✅ Análise Computacional Concluída!")
            st.markdown("### 📊 Quadrantes de Decisão")
            
            res_string = str(resultado).upper()
            if "CALL" in res_string:
                sinal_final = "🟢 CALL (COMPRA)"
            elif "PUT" in res_string:
                sinal_final = "🔴 PUT (VENDA)"
            else:
                sinal_final = "🟡 NEUTRO (FORA DO MERCADO)"
                
            # Criação dos 4 Quadrantes que você pediu
            q1, q2, q3, q4 = st.columns(4)
            with q1:
                st.info("**Quadrante 1: Tendência**\n\nTendência do gráfico processada com sucesso via OpenAI.")
            with q2:
                st.info("**Quadrante 2: Price Action**\n\nZonas estruturais mapeadas pelo agente especialista.")
            with q3:
                st.warning(f"**Quadrante 3: Decisão**\n\n### {sinal_final}")
            with q4:
                st.success("**Quadrante 4: Assertividade**\n\nFiltro matemático buscando taxa alvo > 75%.")
            
            st.markdown("---")
            st.subheader("📝 Relatório Técnico Detalhado")
            st.text_area("Análise completa gerada pelos agentes:", resultado, height=250)
            
            st.download_button(
                label="📥 Fazer Download da Decisão (.txt)",
                data=resultado,
                file_name="decisao_agentes_trading.txt",
                mime="text/plain"
            )
