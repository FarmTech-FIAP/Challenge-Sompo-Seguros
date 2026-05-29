import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================
st.set_page_config(
    page_title="AgroRisk Dashboard",
    layout="wide",
    page_icon="🌾"
)

# Estilização básica para o topo do aplicativo
st.markdown("""
    <style>
    .reportview-container .main .block-container{ padding-top: 1rem; }
    </style>
""", unsafe_allow_html=True)

st.title("🌾 AgroRisk Tracker")
st.caption("Challenge Sompo Seguros — Integração Inteligente de Dados (Sprint 2)")

# =====================================================
# CONEXÃO SQL
# =====================================================
try:
    conn = sqlite3.connect('sql/agrorisk.db')
    df = pd.read_sql("SELECT * FROM operacoes_risco", conn)
    conn.close()
except Exception as e:
    st.error(f"Erro ao conectar ao banco de dados: {e}. Certifique-se de rodar o script do modelo de IA primeiro para gerar o arquivo 'sql/agrorisk.db'.")
    st.stop()

# =====================================================
# SEPARAÇÃO POR PERSONAS (Exigência Estratégica da FIAP)
# =====================================================
aba_gestor, aba_operador = st.tabs(["📊 Visão do Gestor (Frota & Estatísticas)", "🚜 Visão do Operador (Painel de Campo)"])

# =====================================================
# 1. ABA DO GESTOR DE FROTA
# =====================================================
with aba_gestor:
    st.subheader("📋 Monitoramento Gerencial e Análise de Sinistros")
    
    # KPIs Principais
    total_operacoes = len(df)
    total_acidentes = int(df['ocorreu_acidente'].sum())
    taxa_acidente = (total_acidentes / total_operacoes) * 100
    media_score = df['score_risco'].mean()
    
    # Novo KPI sugerido: Operações classificadas como CRÍTICAS pela IA
    total_criticas_ia = len(df[df['nivel_risco'] == 'CRÍTICO'])

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total de Operações", total_operacoes)
    col2.metric("Sinistros / Acidentes", total_acidentes)
    col3.metric("Taxa de Sinistralidade", f"{taxa_acidente:.2f}%")
    col4.metric("Média Score de Risco", f"{media_score:.1f}/100")
    col5.metric("Alertas Críticos (IA)", total_criticas_ia)

    st.divider()

    # Nova Tabela: Foco total no risco crítico (Gestão por Exceção)
    st.subheader("🚨 Operações em Risco Crítico (Atenção Imediata)")
    st.markdown("Lista prioritária contendo as operações que exigem intervenção ou paralisação de atividades.")
    df_criticas = df[df['nivel_risco'] == 'CRÍTICO'].head(20)
    
    if not df_criticas.empty:
        st.dataframe(df_criticas, use_container_width=True)
    else:
        st.success("Excelente! Nenhum maquinário operando em nível crítico no momento.")

    st.divider()

    # Filtro Interativo para o Gestor
    st.markdown("### 🔍 Filtrar Base de Dados por Equipamento")
    lista_equipamentos = ["TODOS"] + list(df['id_equipamento'].unique())
    equip_selecionado = st.selectbox("Selecione o Maquinário:", lista_equipamentos)
    
    df_filtrado = df if equip_selecionado == "TODOS" else df[df['id_equipamento'] == equip_selecionado]
    st.dataframe(df_filtrado.head(15), use_container_width=True)

    st.divider()
    
    # Gráficos Analíticos (Computação Estatística exigida pela FIAP)
    st.markdown("### 📊 Validação Estatística & Correlações de Risco")
    
    g1, g2 = st.columns(2)
    
    with g1:
        st.markdown("**Matriz de Distribuição de Riscos por Categoria**")
        fig_riscos, ax_riscos = plt.subplots(figsize=(6, 3.8))
        ordem_risco = [r for r in ["BAIXO", "MÉDIO", "ALTO", "CRÍTICO"] if r in df['nivel_risco'].unique()]
        sns.countplot(x='nivel_risco', data=df, order=ordem_risco, palette='coolwarm', ax=ax_riscos)
        ax_riscos.set_xlabel("Nível de Risco Atribuído pela IA")
        ax_riscos.set_ylabel("Quantidade de Registros")
        st.pyplot(fig_riscos)
        
    with g2:
        st.markdown("**🔥 Heatmap de Correlação das Variáveis Críticas**")
        fig_corr, ax_corr = plt.subplots(figsize=(6, 3.8))
        sns.heatmap(df.corr(numeric_only=True), annot=True, cmap='YlOrRd', fmt=".2f", ax=ax_corr, annot_kws={"size": 8})
        st.pyplot(fig_corr)

    g3, g4 = st.columns(2)
    
    with g3:
        st.markdown("**🌊 Influência da Distância da Água no Risco**")
        fig_scatter, ax_scatter = plt.subplots(figsize=(6, 3.8))
        sns.scatterplot(x='distancia_corpo_agua_m', y='score_risco', hue='nivel_risco', data=df, palette='coolwarm', ax=ax_scatter)
        ax_scatter.set_xlabel("Distância de Corpos d'Água (m)")
        ax_scatter.set_ylabel("Score de Risco (0-100)")
        st.pyplot(fig_scatter)
        
    with g4:
        st.markdown("**🌧️ Relação Acúmulo de Chuva x Umidade do Solo**")
        fig_chuva, ax_chuva = plt.subplots(figsize=(6, 3.8))
        sns.regplot(x='chuva_acumulada_mm', y='umidade_solo_pct', data=df, scatter_kws={'alpha':0.3}, line_kws={'color':'red'}, ax=ax_chuva)
        ax_chuva.set_xlabel("Chuva Acumulada 48h (mm)")
        ax_chuva.set_ylabel("Umidade do Solo (%)")
        st.pyplot(fig_chuva)

# =====================================================
# 2. ABA DO OPERADOR DA MÁQUINA
# =====================================================
with aba_operador:
    st.subheader("🚜 Painel de Alertas em Tempo Real (Simulação de Cabine)")
    st.markdown("Esta interface simula as informações críticas enviadas pelo módulo embarcado e processadas pelo motor de IA local.")
    
    # Filtro para o Operador focar estritamente na máquina dele
    maquina_operador = st.radio(
        "Selecione o seu Equipamento para simular o Monitoramento de Bordo:",
        df['id_equipamento'].unique(),
        horizontal=True
    )
    
    # Pega o registro simulado mais recente para aquela máquina específica
    dados_maquina = df[df['id_equipamento'] == maquina_operador].iloc[-1]
    
    st.markdown("---")
    
    # Interface de Alerta Dinâmica baseada nos Scores da nossa IA
    st.markdown("### 🚨 Painel de Segurança")
    
    score_atual = dados_maquina['score_risco']
    status_atual = dados_maquina['nivel_risco']
    
    col_status, col_score = st.columns([2, 1])
    
    with col_score:
        st.metric(label="SCORE DE RISCO ATUAL", value=f"{score_atual} / 100")
        
    with col_status:
        if status_atual == "CRÍTICO":
            st.error(f"🛑 ALERTA CRÍTICO: Risco de atolamento/tombamento iminente! PARALISE as operações na frente de colheita imediatamente.")
        elif status_atual == "ALTO":
            st.warning(f"⚠️ ATENÇÃO: Terreno instável. Reduza a velocidade do equipamento e evite rotas declivosas ou próximas a corpos d'água.")
        elif status_atual == "MÉDIO":
            st.info(f"🔄 AVISO: Condições operacionais moderadas. Prossiga com atenção redobrada nos sensores de inclinação.")
        else:
            st.success(f"✅ OPERAÇÃO SEGURA: Solo e condições climáticas dentro dos parâmetros ideais de estabilidade.")

    st.markdown("### 🎛️ Telemetria Atual dos Sensores")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Inclinação Lateral", f"{dados_maquina['inclinacao_graus']}°")
    c2.metric("Umidade do Solo (Sensores)", f"{dados_maquina['umidade_solo_pct']}%")
    c3.metric("Distância do Rio/Canal", f"{dados_maquina['distancia_corpo_agua_m']} m")
    c4.metric("Peso Estimado de Carga", f"{dados_maquina['peso_maquina_ton']} Ton")

# =====================================================
# RODAPÉ
# =====================================================
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        <b>AgroRisk Tracker v2.0</b> — Desenvolvido para o Challenge Sompo Seguros (FIAP)<br>
        <i>Arquitetura Local e Preditiva: IoT (ESP32) → Ingestão SQL → Motor Random Forest (Scikit-Learn) → Dashboards Funcionais</i>
    </div>
    """, 
    unsafe_allow_html=True
)