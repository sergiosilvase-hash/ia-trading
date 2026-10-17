import streamlit as st
import os
from datetime import datetime
from PIL import Image
from crewai import Agent, Task, Crew, Process, LLM

# Configuração para ler a nova chave da OpenAI direto dos Secrets do Streamlit
if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="Mesa de IA - Opções Binárias", layout="wide", initial_sidebar_state="collapsed")

# Estilização CSS HUD customizada conforme as novas exigências de layout
st.markdown("""
    <style>
    .hud-container {
        background-color: #121212;
        padding: 25px;
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
        margin-bottom: 10px;
        font-weight: bold;
    }
    .hud-sub-box {
        background-color: #1A1A1A;
        border-radius: 8px;
        padding: 15px;
        margin-top: 20px;
        border: 1px solid #262626;
    }
    .hud-sub-titulo {
        font-size: 14px;
        font-weight: bold;
        color: #00E676;
        margin-bottom: 12px;
        border-bottom: 1px solid #333;
        padding-bottom: 5px;
    }
    .agente-bloco {
        margin-bottom: 15px;
    }
    .agente-nome {
        color: #00B0FF;
        font-weight: bold;
        font-size: 13px;
    }
    .agente-texto {
        color: #D3D3D3;
        font-size: 13px;
        line-height: 1.4;
        margin: 4px 0 0 0;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 Painel OpenAI: Visão & Análise M5")
st.markdown("---")

st.subheader("📸 1. Escanear Gráfico do Mercado")
arquivo_upload = st.file_uploader("Arraste o print do TradingView ou Binance para ler o gráfico:", type=["png", "jpg", "jpeg"])

if arquivo_upload:
    image = Image.open(arquivo_upload)
    st.image(image, caption="🔍 Imagem carregada para o GPT-4o", use_container_width=True)
    
    caminho_imagem = "print_grafico.png"
    image.save(caminho_imagem)
    
    st.markdown("---")
    if st.button("🚀 Iniciar Escaneamento e Análise dos Agentes"):
        with st.spinner("O GPT-4o está gerando o seu Painel HUD Analítico... Aguarde."):
            
            # Inicialização do Modelo Multimodal
            llm_openai = LLM(
                model="openai/gpt-4o", 
                temperature=0.1,
                api_key=os.environ["OPENAI_API_KEY"]
            )

            # Criando os 3 Agentes Especialistas
            analista_tecnico = Agent(
                role='Analista Técnico Quantitativo',
                goal='Mapear rigorosamente a tendência macro/micro e canais de preço no print.',
                backstory='Especialista em visão computacional voltada a estruturas de gráficos financeiros.',
                verbose=True, llm=llm_openai
            )

            especialista_price_action = Agent(
                role='Especialista em Price Action',
                goal='Escanear o print para achar zonas de suporte, resistência e padrões de velas.',
                backstory='Analista detalhista que foca em equilíbrio de forças e confluências visuais.',
                verbose=True, llm=llm_openai
            )

            estrategista_ob = Agent(
                role='Estrategista de Opções Binárias',
                goal='Tomar a decisão final baseada no gerenciamento e confluência estrita.',
                backstory='Matemático focado em manter o filtro rígido para buscar assertividade acima de 75%.',
                verbose=True, llm=llm_openai
            )

            # Tarefas estruturadas para alimentar os resumos de 3 a 5 linhas de cada agente
            t1 = Task(
                description="Analise visualmente a imagem anexada. Identifique a tendência dominante (Alta, Baixa ou Lateral) e explique o porquê de forma resumida.", 
                expected_output="Resumo explicativo da tendência de até 5 linhas.", 
                agent=analista_tecnico,
                image_ports=[caminho_imagem]
            )
            
            t2 = Task(
                description="Analise visualmente a imagem anexada. Liste as zonas de suporte, resistência e os padrões de velas mais marcantes observados.", 
                expected_output="Resumo explicativo de price action de até 5 lines.", 
                agent=especialista_price_action,
                image_ports=[caminho_imagem]
            )
            
            t3 = Task(
                description=(
                    "Com base nas análises anteriores, tome a decisão final. "
                    "Determine a sugestão (COMPRA, VENDA ou NEUTRO), avalie a confluência (ex: 3/5 ou 4/5 fatores) "
                    "e o nível de confiança (BAIXA, MÉDIA ou ALTA). Faça uma síntese de raciocínio de até 5 linhas."
                ), 
                expected_output="Resumo explicativo da estratégia de até 5 linhas contendo chaves: SUGESTÃO, CONFLUÊNCIA, CONFIANÇA.", 
                agent=estrategista_ob,
                image_ports=[caminho_imagem]
            )

            # CORRIGIDO: Agora usando o nome correto 'estrategista_ob'
            mesa = Crew(agents=[analista_tecnico, especialista_price_action, estrategista_ob], tasks=[t1, t2, t3], process=Process.sequential)
            mesa.kickoff()
            
            # Capturando as respostas reais e factuais geradas por cada agente no processamento da imagem
            res_tendencia = t1.output.raw if t1.output else "Análise de tendência indisponível."
            res_price_action = t2.output.raw if t2.output else "Análise estrutural de candles indisponível."
            res_estrategista = t3.output.raw if t3.output else "Análise de gerenciamento indisponível."
            
            # Lógica de decisão para pintura do sinal
            res_upper = res_estrategista.upper()
            sugestao = "NEUTRO"
            if "COMPRA" in res_upper or "CALL" in res_upper:
                sugestao = "COMPRA"
            elif "VENDA" in res_upper or "PUT" in res_upper:
                sugestao = "VENDA"
                
            confianca = "MÉDIA"
            if "ALTA" in res_upper:
                confianca = "ALTA"
            elif "BAIXA" in res_upper:
                confianca = "BAIXA"
                
            # Lógica dinâmica para calcular a quantidade de confluências
            confluencias_count = "3/5"
            if "4/5" in res_upper: confluencias_count = "4/5"
            elif "5/5" in res_upper: confluencias_count = "5/5"
            elif "2/5" in res_upper: confluencias_count = "2/5"
            
            hora_atual = datetime.now().strftime("%H:%M")
            
            st.success("✅ Escaneamento HUD Analítico Concluído!")
            
            # Cores dinâmicas para o visual HUD
            cor_sinal = "#00E676" if sugestao == "COMPRA" else ("#FF5252" if sugestao == "VENDA" else "#FFD600")
            cor_conf = "#00E676" if confianca == "ALTA" else ("#FFA726" if confianca == "MÉDIA" else "#FF5252")
            
            # 🧩 RENDERIZAÇÃO DO QUADRANTE HUD SOLICITADO COM RESUMO REAL DE CADA AGENTE
            st.markdown(f"""
                <div class="hud-container">
                    <div class="hud-header">
                        <span>📊 HUD M5 - Painel de Confluências</span>
                        <span>✕</span>
                    </div>
                    <div class="hud-linha">Hora de Entrada: <span style="color: #00E676;">{hora_atual}</span></div>
                    <div class="hud-linha">Sugestão M5: <span style="color: {cor_sinal};">{sugestao}</span></div>
                    <div class="hud-linha">Confluências: <span style="color: #FFFFFF;">{confluencias_count}</span></div>
                    <div class="hud-linha">Confiança: <span style="color: {cor_conf};">{confianca}</span></div>
                    
                    <div class="hud-sub-box">
                        <div class="hud-sub-titulo">Interpretação e Resumos dos Agentes:</div>
                        
                        <div class="agente-bloco">
                            <div class="agente-nome">1) Agente Analista Técnico (Tendência):</div>
                            <p class="agente-texto">{res_tendencia}</p>
                        </div>
                        
                        <div class="agente-bloco">
                            <div class="agente-nome">2) Agente Price Action (Suportes e Velas):</div>
                            <p class="agente-texto">{res_price_action}</p>
                        </div>
                        
                        <div class="agente-bloco">
                            <div class="agente-nome">3) Agente Estrategista (Veredito e Risco):</div>
                            <p class="agente-texto">{res_estrategista}</p>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Botão de download consolidando o relatório do HUD
            relatorio_txt = f"HUD M5 - RELATÓRIO\nHora: {hora_atual}\nSugestão: {sugestao}\nConfluências: {confluencias_count}\nConfiança: {confianca}\n\n1) TENDÊNCIA:\n{res_tendencia}\n\n2) PRICE ACTION:\n{res_price_action}\n\n3) ESTRATEGISTA:\n{res_estrategista}"
            st.download_button(
                label="📥 Fazer Download dos Dados do HUD (.txt)",
                data=relatorio_txt,
                file_name="hud_m5_analitico.txt",
                mime="text/plain"
            )
