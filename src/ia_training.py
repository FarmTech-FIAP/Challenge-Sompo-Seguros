import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

print("Iniciando o treinamento da IA...")

# 1. Carregar os dados do dataset Sprint2
df = pd.read_csv('dataset_agrorisk_simulado.csv')

# 2. Separar as variáveis de entrada (Features) e o alvo (Target)
X = df[['chuva_acumulada_mm', 'umidade_solo_pct', 'inclinacao_graus', 'peso_maquina_ton']]
y = df['ocorreu_acidente']

# 3. Dividir os dados em treino (80%) e teste (20%)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 4. Criar e treinar o modelo Random Forest
modelo = RandomForestClassifier(n_estimators=100, random_state=42)
modelo.fit(X_train, y_train)

# 5. Avaliar a Acurácia (apenas para documentação)
previsoes = modelo.predict(X_test)
acuracia = accuracy_score(y_test, previsoes)
print(f"Treinamento concluído! Acurácia do modelo: {acuracia * 100:.2f}%")

# 6. Salvar o modelo treinado (Salvando o arquivo .pkl é gerado!)
joblib.dump(modelo, 'modelo_agrorisk.pkl')
print("Arquivo 'modelo_agrorisk.pkl' criado com sucesso na pasta atual!")
