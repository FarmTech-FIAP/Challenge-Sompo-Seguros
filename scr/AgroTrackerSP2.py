import pandas as pd
import numpy as np

# Definindo uma semente para que os dados sejam os mesmos toda vez que rodar o script
np.random.seed(42)

# Quantidade de registros simulados (1500 operações/leituras)
n_samples = 1500

print("Gerando dados das variáveis independentes...")

# 1. Equipamentos
equipamentos = ['TRATOR-I', 'TRATOR-II', 'COLHEITADEIRA-I', 'COLHEITADEIRA-II', 'PULVERIZADOR-I']
id_equipamento = np.random.choice(equipamentos, n_samples)

# 2. Chuva acumulada nas últimas 48h (De 0 a 120 mm)
chuva_acumulada_mm = np.random.uniform(0, 120, n_samples)

# 3. Umidade do Solo (%)
# Umidade não é aleatória; ela aumenta logicamente se a chuva acumulada for alta.
# Fator aleatório base (10 a 40%) + impacto da chuva
umidade_solo_pct = (chuva_acumulada_mm * 0.6) + np.random.uniform(10, 40, n_samples)
# Garantindo que a umidade não passe de 100%
umidade_solo_pct = np.clip(umidade_solo_pct, 0, 100)

# 4. Inclinação do terreno (De 0 a 35 graus)
inclinacao_graus = np.random.uniform(0, 35, n_samples)

# 5. Peso do Equipamento (De 10 a 25 Toneladas)
peso_maquina_ton = np.random.uniform(10, 25, n_samples)

print("Calculando a regra de negócio para acidentes...")

# 6. Variável Alvo (Ocorreu Acidente? 0 = Não, 1 = Sim)
# Criamos uma "fórmula secreta" de risco.
# Inclinação e umidade altas, combinadas com peso alto, elevam o fator de risco.
fator_risco_oculto = (umidade_solo_pct * 0.4) + (inclinacao_graus * 1.5) + (peso_maquina_ton * 0.5)

# Adicionamos um pouco de "ruído" (aleatoriedade) para simular o mundo real,
# assim o nosso modelo de IA não acerta 100% sempre e a matriz de confusão fica realista.
fator_risco_oculto += np.random.normal(0, 8, n_samples)

# Definimos que se o fator de risco oculto ultrapassar o limiar de 75, ocorreu um acidente/atolamento.
limiar_acidente = 75
ocorreu_acidente = np.where(fator_risco_oculto > limiar_acidente, 1, 0)

# DataFrame (Tabela)
df_agrorisk = pd.DataFrame({
    'id_equipamento': id_equipamento,
    'chuva_acumulada_mm': np.round(chuva_acumulada_mm, 2),
    'umidade_solo_pct': np.round(umidade_solo_pct, 2),
    'inclinacao_graus': np.round(inclinacao_graus, 2),
    'peso_maquina_ton': np.round(peso_maquina_ton, 2),
    'ocorreu_acidente': ocorreu_acidente
})

# Salvando em um arquivo CSV para ser usado no treinamento do Machine Learning
nome_arquivo = 'dataset_agrorisk_simulado.csv'
df_agrorisk.to_csv(nome_arquivo, index=False)

# Exibindo os primeiros registros e informações no terminal
print("\n--- Primeiros 5 registros gerados ---")
print(df_agrorisk.head())

print("\n--- Distribuição da Variável Alvo (Acidentes) ---")
print(df_agrorisk['ocorreu_acidente'].value_counts(normalize=True) * 100)
print(f"\nArquivo '{nome_arquivo}' criado com sucesso!")
