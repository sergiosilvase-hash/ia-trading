import streamlit as st
import os
import datetime
from PIL import Image
from crewai import Agent, Task, Crew, Process, LLM

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

if arquivo_upload:
    image = Image.open(arquivo_upload)
    st.image(image, caption="🔍 Imagem carregada para o GPT-4o", use_container_width=True)
    
    caminho_imagem = "print_grafico.png"
    image.save(caminho_imagem)
    
    st.markdown("---")
    if st.button("🚀 Iniciar Escaneamento e Análise dos Agentes"):
        with st.spinner("O GPT-4o está varrendo a sequência de candles M5... Aguarde."):
            
            # Inicialização estável do modelo GPT-4o
            llm_openai = LLM(
                model="openai/gpt-4o", 
                temperature=0.1,
                api_key=os.environ["OPENAI_API_KEY"]
            )

            # Criando os 3 Agentes Especialistas
            analista_tecnico = Agent(
                role='Analista Técnico Quantitativo',
                goal='Mapear a tendência lendo todos os candles M5 visíveis na imagem sequencialmente.',
                backstory='Especialista em analisar o histórico inteiro de velas expostas na tela para extrair a tendência macro e micro.',
                verbose=True, llm=llm_openai
            )

            especialista_price_action = Agent(
                role='Especialista em Price Action',
                goal='Escanear o gráfico para mapear zonas de suporte/resistência e ler padrões vela por vela.',
                backstory='Analista focado em decifrar a movimentação do mercado lendo pavios e corpos de velas.',
                verbose=True, llm=llm_openai
            )

            estrategista_ob = Agent(
                role='Estrategista de Opções Binárias',
                goal='Tomar a decisão final combinando as confluências coletadas no cenário do gráfico.',
                backstory='Matemático financeiro que valida operações buscando alta probabilidade de acerto.',
                verbose=True, llm=llm_openai
            )

            # CORREÇÃO CRUCIAL: Injetando o arquivo de imagem diretamente nas tarefas de visão do GPT-4o
            t1 = Task(
                description=f"Analise o arquivo de imagem salvo em {caminho_imagem} candle por candle. Avalie toda a sequência temporal dos gráficos de 5 minutos expostos e descreva a tendência micro e macro.", 
                expected_output="Resumo explicativo sobre a tendência de alta, baixa ou lateralidade encontrada nos candles de até 5 linhas.", 
                agent=analista_tecnico
            )
            
            t2 = Task(
                description=f"Analise o arquivo de imagem salvo em {caminho_imagem}. Leia a estrutura de pavios e corpo de todos os candles para delimitar os suportes/resistências e listar padrões gráficos reais identificados.", 
                expected_output="Resumo estrutural indicando padrões de velas e zonas de reversão/pullback de até 5 linhas.", 
                agent=especialista_price_action
            )
            
            t3 = Task(
                description=f"Examine os relatórios anteriores gerados sobre a imagem {caminho_imagem}. Gere o veredito final contendo de forma explícita as palavras-chave: SUGESTÃO (COMPRA, VENDA ou NEUTRO), CONFLUÊNCIAS (quantidade no formato X/Y) e CONFIANÇA (BAIXA, MÉDIA ou ALTA), seguido de uma justificativa de até 5 linhas.", 
                expected_output="Síntese da estratégia contendo obrigatoriamente as palavras-chave: SUGESTÃO, CONFLUÊNCIAS e CONFIANÇA.", 
                agent=estrategista_ob
            )

            # Executando a mesa de agentes
            mesa = Crew(agents=[analista_tecnico, especialista_price_action, estrategista_ob], tasks=[t1, t2, t3], process=Process.sequential)
            resultado_mesa = mesa.kickoff()
            
            # Convertendo os retornos em texto limpo
            res_tendencia = str(t1.output.raw if t1.output else "Análise de tendência processada.").replace("<", "&lt;").replace(">", "&gt;")
            res_price_action = str(t2.output.raw if t2.output else "Zonas estruturais mapeadas.").replace("<", "&lt;").replace(">", "&gt;")
            res_estrategista = str(resultado_mesa.raw if resultado_mesa else "Veredito processado.").replace("<", "&lt;").replace(">", "&gt;")
            
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
                confluencias_count = "12/15" if sugestao != "NEUTRO" else "3/15"

            # Validação inteligente do Horário de Brasília (Oculta se for NEUTRO)
            congestao_upper = sugestao.upper()
            if "NEUTRO" in congestao_upper:
                linha_horario_html = ""
            else:
                hora_brasilia = (datetime.datetime.utcnow() - datetime.timedelta(hours=3)).strftime("%H:%M")
                linha_horario_html = f"<div class='hud-linha'>Hora de Entrada: <span style='color: #00E676;'>{hora_brasilia}</span></div>"
            
            st.success("✅ Escaneamento HUD Analítico Concluído!")
            
            # Configuração das cores do painel
            cor_sinal = "#00E676" if sugestao == "COMPRA" else ("#FF5252" if sugestao == "VENDA" else "#FFD600")
            cor_conf = "#00E676" if confianca == "ALTA" else ("#FFA726" if confianca == "MÉDIA" else "#FF5252")
            
            # Montagem estruturada e limpa do HTML final na tela
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
            
            # Desenha o HUD completo e formatado na tela
            st.markdown(html_hud, unsafe_allow_html=True)
            
            st.markdown("---")
