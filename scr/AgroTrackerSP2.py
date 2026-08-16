# Arquivo: AgroTrackerSP3.py
import streamlit as st
import pandas as pd
import joblib
import oracledb
import logging
import os

# ==========================================
# 1. SEGURANÇA: LOGS DE AUDITORIA
# ==========================================
logging.basicConfig(filename='auditoria_sistema.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# ==========================================
# 2. SEGURANÇA: CONTROLE DE ACESSO (LOGIN)
# ==========================================
def check_password():
    """Retorna True se a senha estiver correta."""
    def password_entered():
        if st.session_state["password"] == "sompo2026" and st.session_state["username"] == "admin":
            st.session_state["password_correct"] = True
            del st.session_state["password"] 
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state or not st.session_state["password_correct"]:
        
        # Exibe a logo se o arquivo existir na pasta do projeto
        logo_path = "logo_agrorisk.jpeg"
        if os.path.exists(logo_path):
            st.image(logo_path, width=550)

        st.title("🔒 Acesso Restrito - Sompo Seguros")
        st.text_input("Usuário", key="username")
        st.text_input("Senha", type="password", on_change=password_entered, key="password")
        
        if st.session_state.get("password_correct") == False:
            st.error("Usuário ou senha incorretos.")
        return False
        
    return True

# Função para sair do sistema
def logout():
    # Limpa a sessão e recarrega a página
    st.session_state.clear()
    st.rerun()

# Trava o app na tela de login
if not check_password():
    st.stop() 

logging.info("Acesso concedido ao dashboard.")

# ==========================================
# 3. CARREGAMENTO DO MODELO DE IA
# ==========================================
@st.cache_resource
def load_model():
    try:
        return joblib.load('modelo_agrorisk.pkl')
    except Exception as e:
        st.error(f"Erro ao carregar modelo: {e}")
        return None

modelo = load_model()

# ==========================================
# 4. INTERFACE E DASHBOARD
# ==========================================
st.title("🚜 AgroRisk Tracker - Sprint 3")
st.write("Integração: Telemetria ➔ Inteligência Artificial ➔ Banco de Dados Oracle")

# Botão de Logout no Menu Lateral
st.sidebar.button("🚪 Sair do Sistema", on_click=logout, use_container_width=True)
st.sidebar.markdown("---")

st.sidebar.header("📡 Entrada de Telemetria (Simulador)")
# Usando as mesmas nomenclaturas do seu código da Sprint 2
equipamentos = ['TRATOR-I', 'TRATOR-II', 'COLHEITADEIRA-I', 'COLHEITADEIRA-II', 'PULVERIZADOR-I']
id_equip = st.sidebar.selectbox("Equipamento", equipamentos)

chuva = st.sidebar.number_input("Chuva 48h (mm)", min_value=0.0, max_value=200.0, value=50.0)
umidade = st.sidebar.number_input("Umidade do Solo (%)", min_value=0.0, max_value=100.0, value=60.0)
inclinacao = st.sidebar.number_input("Inclinação (Graus)", min_value=0.0, max_value=45.0, value=15.0)
peso = st.sidebar.number_input("Peso da Máquina (Ton)", min_value=10.0, max_value=30.0, value=15.0)

if st.sidebar.button("Analisar Risco e Salvar no Banco"):
    if modelo:
        try:
            # 5. PREDIÇÃO (O MOTOR DA IA)
            # Organizando os dados de entrada na mesma ordem que a IA foi treinada
            input_data = pd.DataFrame([[chuva, umidade, inclinacao, peso]], 
                                    columns=['chuva_acumulada_mm', 'umidade_solo_pct', 'inclinacao_graus', 'peso_maquina_ton'])
            
            # Pegamos a probabilidade de acidente (classe 1) e multiplicamos por 100
            probabilidade = modelo.predict_proba(input_data)[0][1]
            score_risco = int(probabilidade * 100)

            # Classificando o Alerta
            if score_risco < 40:
                alerta, cor = "Seguro", "green"
            elif score_risco < 75:
                alerta, cor = "Atenção", "orange"
            else:
                alerta, cor = "Crítico", "red"

            # Exibindo resultado no Dashboard
            st.subheader(f"Análise: {id_equip}")
            st.markdown(f"<h1 style='text-align: center; color: {cor};'>{score_risco} / 100</h1>", unsafe_allow_html=True)
            st.markdown(f"<h3 style='text-align: center; color: {cor};'>Status: {alerta}</h3>", unsafe_allow_html=True)
            
            logging.info(f"Processado: {id_equip} | Score: {score_risco} | Status: {alerta}")

            # ==========================================
            # 6. ENGENHARIA DE DADOS (ORACLE DB)
            # ==========================================
            # Substitua com seus dados reais da FIAP (SQL Developer)
            ORACLE_USER = "rm572159"
            ORACLE_PASS = "050682"
            
            # Montando a string de conexão especificamente para Host, Port e SID
            ORACLE_DSN = oracledb.makedsn("oracle.fiap.com.br", 1521, sid="ORCL")

            try:
                # Conexão com o Oracle
                conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASS, dsn=ORACLE_DSN)
                cursor = conn.cursor()
                
                # Query de Inserção (A tabela tb_historico_risco deve estar criada no seu banco)
                sql = """INSERT INTO tb_historico_risco 
                         (id_equipamento, chuva_acumulada_mm, umidade_solo_pct, inclinacao_graus, peso_maquina_ton, score_risco, classificacao_alerta) 
                         VALUES (:1, :2, :3, :4, :5, :6, :7)"""
                
                # Inserindo os dados gerados
                cursor.execute(sql, [id_equip, chuva, umidade, inclinacao, peso, score_risco, alerta])
                conn.commit()
                
                cursor.close()
                conn.close()
                
                st.success("✅ Ocorrência registrada no Banco de Dados Oracle com sucesso!")
                logging.info(f"Registro inserido no Oracle DB para {id_equip}.")
                
            #except Exception as db_error:
                #st.warning("⚠️ Risco calculado, mas falhou ao salvar no Banco de Dados. Verifique as credenciais no código.")
                #logging.error(f"Erro BD: {db_error}")

            except Exception as db_error:
                st.warning("⚠️ Falha ao salvar no Banco de Dados.")
                st.error(f"Detalhe técnico do erro: {db_error}") # <--- ESSA LINHA VAI NOS DAR A RESPOSTA
                logging.error(f"Erro BD: {db_error}")

        except Exception as pred_error:
            st.error("Ocorreu um erro ao processar a IA.")
            logging.error(f"Erro IA: {pred_error}")

            # ==========================================
            # 7. EXIBIÇÃO DO HISTÓRICO (DASHBOARD)
            # ==========================================
            st.markdown("---")
            st.subheader("📋 Histórico de Análises (Auditoria da Seguradora)")

if st.button("Atualizar Histórico"):
    try:
        # Mesmas credenciais que você já configurou
        ORACLE_USER = "rm572159"
        ORACLE_PASS = "050682"
        ORACLE_DSN = oracledb.makedsn("oracle.fiap.com.br", 1521, sid="ORCL")
        
        conn = oracledb.connect(user=ORACLE_USER, password=ORACLE_PASS, dsn=ORACLE_DSN)
        cursor = conn.cursor()
        
        # Busca os últimos 10 registros
        query = """
            SELECT id_equipamento, score_risco, classificacao_alerta, data_hora 
            FROM tb_historico_risco 
            ORDER BY data_hora DESC 
            FETCH FIRST 10 ROWS ONLY
        """
        cursor.execute(query)
        linhas = cursor.fetchall()
        
        if linhas:
            # Transforma os dados em uma tabela Pandas para exibir no Streamlit
            df_historico = pd.DataFrame(linhas, columns=['Equipamento', 'Score de Risco', 'Status', 'Data/Hora'])
            st.dataframe(df_historico, use_container_width=True)
        else:
            st.info("Nenhum registro encontrado no banco de dados.")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        st.error(f"Erro ao buscar histórico no banco: {e}")
