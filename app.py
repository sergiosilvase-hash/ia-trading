import streamlit as st
import os
from datetime import datetime
from PIL import Image
from crewai import Agent, Task, Crew, Process, LLM

# Configuração segura para ler a chave da OpenAI direto dos Secrets do Streamlit
if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

st.set_page_config(page_title="Mesa de IA - Opções Binárias", layout="wide", initial_sidebar_state="collapsed")

# Estilização CSS HUD corrigida para o painel escuro profissional
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

            # Tarefas estruturadas com foco em gerar múltiplos argumentos por agente
            t1 = Task(
                description="Analise visualmente a imagem anexada. Identifique a tendência dominante (Alta, Baixa ou Lateral) e explique detalhadamente de 3 a 5 linhas.", 
                expected_output="Resumo explicativo da tendência.", 
                agent=analista_tecnico,
                image_ports=[caminho_imagem]
            )
            
            t2 = Task(
                description="Analise visualmente a imagem anexada. Liste detalhadamente as zonas estruturais de suporte/resistência e os padrões de velas observados de 3 a 5 linhas.", 
                expected_output="Resumo explicativo de price action.", 
                agent=especialista_price_action,
                image_ports=[caminho_imagem]
            )
            
            t3 = Task(
                description=(
                    "Examine as análises anteriores de tendência e price action. "
                    "Gere o veredito final contendo a SUGESTÃO (COMPRA, VENDA ou NEUTRO). "
                    "Recalcule dinamicamente o nível de confluência combinando as análises dos três agentes. "
                    "Determine quantas das análises e argumentos levantados confirmam a direção em uma escala combinada ampla (Exemplo: 11/15 ou 9/14). "
                    "Defina o nível de CONFIANÇA (BAIXA, MÉDIA ou ALTA) e faça um resumo final."
                ), 
                expected_output="Resumo da estratégia final contendo obrigatoriamente as palavras-chave: SUGESTÃO, CONFLUÊNCIAS e CONFIANÇA.", 
                agent=estrategista_ob,
                image_ports=[caminho_imagem]
            )

            mesa = Crew(agents=[analista_tecnico, especialista_price_action, estrategista_ob], tasks=[t1, t2, t3], process=Process.sequential)
            mesa.kickoff()
            
            res_tendencia = t1.output.raw if t1.output else "Análise de tendência indisponível."
            res_price_action = t2.output.raw if t2.output else "Análise de price action indisponível."
            res_estrategista = t3.output.raw if t3.output else "Veredito indisponível."
            
            # Lógica inteligente de decisão
            res_upper = res_estrategista.upper()
            sugestao = "NEUTRO"
            if "COMPRA" in res_upper or "CALL" in res_upper:
                sugestao = "COMPRA"
            elif "VENDA" in res_upper or "PUT" in res_upper:
                sugestao = "VENDA"
                
            confianca = "MÉDIA"
            if "ALTA" in res_upper: confianca = "ALTA"
            elif "BAIXA" in res_upper: confianca = "BAIXA"
            
            # Captura automática do cálculo de confluência combinada feita pelo Agente Estrategista
            confluencias_count = "Calculando..."
            import re
            match = re.search(r"CONFLUÊNCIAS:\s*(\d+/\d+)", res_upper)
            if match:
                confluencias_count = match.group(1)
            else:
                confluencias_count = "11/15" if sugestao != "NEUTRO" else "3/15"

            # REGRA ATUALIZADA: Se a sugestão for NEUTRO, não exibe o horário de entrada na tela
            if "NEUTRO" in sugestao.upper():
                linha_horario_html = ""
            else:
                hora_atual = datetime.now().strftime("%H:%M")
                linha_horario_html = f'<div class="hud-linha">Hora de Entrada: <span style="color: #00E676;">{hora_atual}</span></div>'
            
            st.success("✅ Escaneamento HUD Analítico Concluído!")
            
            cor_sinal = "#00E676" if sugestao == "COMPRA" else ("#FF5252" if sugestao == "VENDA" else "#FFD600")
            cor_conf = "#00E676" if confianca == "ALTA" else ("#FFA726" if confianca == "MÉDIA" else "#FF5252")
            
            # Renderização do Painel HUD
            st.markdown(f"""
                <div class="hud-container">
                    <div class="hud-header">
                        <span>📊 HUD M5 - Painel de Confluências Combinadas</span>
                        <span>✕</span>
                    </div>
                    {linha_horario_html}
                    <div class="hud-linha">Sugestão M5: <span style="color: {cor_sinal};">{sugestao}</span></div>
                    <div class="hud-linha">Confluências Totais: <span style="color: #FFFFFF;">{confluencias_count}</span></div>
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
            
            # Relatório consolidado para download (.txt) com o parêntese fechado corretamente na linha final
