# =========================================================
# AGRORISK - SPRINT 2
# MODELO PREDITIVO DE RISCO OPERACIONAL
# =========================================================

import os
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# =========================================================
# CRIAR PASTAS
# =========================================================
os.makedirs('data', exist_ok=True)
os.makedirs('images', exist_ok=True)
os.makedirs('sql', exist_ok=True)

csv_path = 'data/dataset_agrorisk_simulado.csv'
recriar_dataset = False

if not os.path.exists(csv_path):
    recriar_dataset = True
else:
    df_existente = pd.read_csv(csv_path)
    if 'distancia_corpo_agua_m' not in df_existente.columns:
        print("Nova variável detectada. Recriando dataset...")
        recriar_dataset = True

if recriar_dataset:
    print("Gerando dataset AgroRisk...")
    np.random.seed(42)
    n_samples = 1500

    equipamentos = ['TRATOR-I', 'TRATOR-II', 'COLHEITADEIRA-I', 'COLHEITADEIRA-II', 'PULVERIZADOR-I']
    id_equipamento = np.random.choice(equipamentos, n_samples)
    chuva_acumulada_mm = np.random.uniform(0, 120, n_samples)
    
    umidade_solo_pct = (chuva_acumulada_mm * 0.6) + np.random.uniform(10, 40, n_samples)
    umidade_solo_pct = np.clip(umidade_solo_pct, 0, 100)
    
    inclinacao_graus = np.random.uniform(0, 35, n_samples)
    peso_maquina_ton = np.random.uniform(10, 25, n_samples)
    distancia_corpo_agua_m = np.random.uniform(0, 1000, n_samples)

    # Lógica de Risco Oculto baseada nos critérios da faculdade
    fator_risco_oculto = (umidade_solo_pct * 0.4) + (inclinacao_graus * 1.5) + (peso_maquina_ton * 0.5)
    fator_risco_oculto += np.random.normal(0, 8, n_samples)

    # Restrição de proximidade de corpos d'água solicitado na Sprint 2
    risco_proximidade_agua = np.where(distancia_corpo_agua_m < 50, 25,
                             np.where(distancia_corpo_agua_m < 200, 15,
                             np.where(distancia_corpo_agua_m < 500, 5, 0)))
    fator_risco_oculto += risco_proximidade_agua

    limiar_acidente = 75
    ocorreu_acidente = np.where(fator_risco_oculto > limiar_acidente, 1, 0)

    df_agrorisk = pd.DataFrame({
        'id_equipamento': id_equipamento,
        'chuva_acumulada_mm': np.round(chuva_acumulada_mm, 2),
        'umidade_solo_pct': np.round(umidade_solo_pct, 2),
        'inclinacao_graus': np.round(inclinacao_graus, 2),
        'peso_maquina_ton': np.round(peso_maquina_ton, 2),
        'distancia_corpo_agua_m': np.round(distancia_corpo_agua_m, 2),
        'ocorreu_acidente': ocorreu_acidente
    })

    df_agrorisk.to_csv(csv_path, index=False)
    print("Dataset criado com sucesso!")
else:
    print("CSV já existe. Carregando dataset...")
    df_agrorisk = pd.read_csv(csv_path)

# =========================================================
# VISUALIZAÇÃO E ESTATÍSTICA (VALIDAÇÃO)
# =========================================================
plt.figure(figsize=(6,4))
sns.countplot(x='ocorreu_acidente', data=df_agrorisk)
plt.title("Distribuição de Acidentes")
plt.savefig('images/distribuicao_acidentes.png')
plt.show()
plt.close()

plt.figure(figsize=(10,6))
sns.heatmap(df_agrorisk.corr(numeric_only=True), annot=True, cmap='coolwarm')
plt.title("Correlação Entre Variáveis")
plt.savefig('images/heatmap.png')
plt.show()
plt.close() 

# =========================================================
# MACHINE LEARNING - MODELAGEM
# =========================================================
features_cols = ['chuva_acumulada_mm', 'umidade_solo_pct', 'inclinacao_graus', 'peso_maquina_ton', 'distancia_corpo_agua_m']
X = df_agrorisk[features_cols]
y = df_agrorisk['ocorreu_acidente']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

modelo = RandomForestClassifier(n_estimators=100, random_state=42)
modelo.fit(X_train, y_train)

# Validação do Modelo com dados de Teste
y_pred = modelo.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"\nAcurácia de Validação do modelo: {accuracy:.2f}")

print("\n--- Relatório de Classificação ---")
print(classification_report(y_test, y_pred))

# Matriz de Confusão para o Relatório Técnico
matriz = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(6,4))
sns.heatmap(matriz, annot=True, fmt='d', cmap='Blues')
plt.title("Matriz de Confusão")
plt.xlabel("Previsto")
plt.ylabel("Real")
plt.savefig('images/matriz_confusao.png')
plt.show()
plt.close()

# =========================================================
# IMPORTÂNCIA DAS VARIÁVEIS
# =========================================================
importancias = modelo.feature_importances_
df_importancia = pd.DataFrame({
    'Variavel': features_cols,
    'Importancia': importancias
}).sort_values(by='Importancia', ascending=False)

print("\n--- Importância das Variáveis ---")
print(df_importancia)

plt.figure(figsize=(8,5))
sns.barplot(
    x='Importancia',
    y='Variavel',
    data=df_importancia)
plt.title("Importância das Variáveis")
plt.savefig('images/importancia_variaveis.png')
plt.show()
plt.close()
# =========================================================
# GERAÇÃO DE SCORES PARA O ECOSSISTEMA ÍNTEGRO
# =========================================================
todas_probabilidades = modelo.predict_proba(X)
df_agrorisk['score_risco'] = np.round(todas_probabilidades[:, 1] * 100, 2)

def classificar_risco(score):
    if score <= 25: return "BAIXO"
    elif score <= 50: return "MÉDIO"
    elif score <= 75: return "ALTO"
    else: return "CRÍTICO"

df_agrorisk['nivel_risco'] = df_agrorisk['score_risco'].apply(classificar_risco)

# =========================================================
# CONEXÃO COM SQL
# =========================================================
db_path = 'sql/agrorisk.db'
conn = sqlite3.connect(db_path)

df_agrorisk.to_sql('operacoes_risco', conn, if_exists='replace', index=False)
print("\n[SUCESSO] Dados preditivos estruturados enviados para o SQLite!")

consulta = pd.read_sql("SELECT id_equipamento, score_risco, nivel_risco, ocorreu_acidente FROM operacoes_risco LIMIT 5", conn)
print("\n--- Validação da Tabela SQL (Métricas de Risco Incluídas) ---")
print(consulta)

conn.close()
print("\nParte 1 Finalizada com Sucesso!")