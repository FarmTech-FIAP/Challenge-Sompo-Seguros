# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href= "https://www.fiap.com.br/"><img src="assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Admnistração Paulista" border="0" width=40% height=40%></a>
</p>

<br>

# Challenge-Sompo-Seguros

## Nome do grupo

## 👨‍🎓 Integrantes: 
- <a href="https://www.linkedin.com/company/inova-fusca">Arthur Prudêncio Soares — RM569295</a>
- <a href="https://www.linkedin.com/company/inova-fusca">Caroline Coelho Mendes — RM570370</a>
- <a href="https://www.linkedin.com/company/inova-fusca">Leandro Paiva — RM572159</a> 
- <a href="https://www.linkedin.com/company/inova-fusca">Lucas Viana de Lima — RM571835</a> 
- <a href="https://www.linkedin.com/company/inova-fusca">Matheus Tavares Lima — RM572808</a>

## 👩‍🏫 Professores:
### Tutor(a) 
- <a href="https://www.linkedin.com/company/inova-fusca">Nome do Tutor</a>
### Coordenador(a)
- <a href="https://www.linkedin.com/company/inova-fusca">Nome do Coordenador</a>

## 1. Entendimento do Problema
No agronegócio, maquinários pesados (tratores, colheitadeiras) operam em terrenos hostis. Chuvas recentes e solos instáveis causam atolamentos e tombamentos, gerando altos custos de manutenção, tempo de máquina parada e sinistros caros para seguradoras como a Sompo. Atualmente, a decisão de operar ou não é baseada na intuição do operador (reativa).

## 2. Definição da Solução
Nossa solução é um sistema preditivo baseado em **IoT e Machine Learning**. Utilizaremos um módulo embarcado no trator (simulado via ESP32) para coletar dados locais de inclinação e umidade, cruzando com dados meteorológicos via API (chuva acumulada). Um modelo de IA rodando localmente analisará esses fatores e emitirá um **Score de Risco**, gerando alertas preventivos (visuais/sonoros) antes que o acidente aconteça.

## 3. Personas e User Stories
* **Operador da Máquina:** "Como operador, quero receber um alerta imediato no painel (LED/Buzzer) quando o terreno apresentar alto risco de atolamento, para que eu possa desviar a rota com segurança."
* **Gestor da Fazenda:** "Como gestor, quero visualizar o score de risco das operações em um dashboard (Python) local, para decidir se autorizo o trabalho nas frentes de colheita após dias chuvosos."
* **Seguradora (Sompo):** "Como seguradora, quero saber que o cliente possui um sistema ativo de prevenção de tombamentos/atolamentos para oferecer apólices com prêmios otimizados."

## 4. Estruturação dos Dados (Dataset Simulado)
Criamos um dataset inicial simulando as condições de operação para treinar nosso futuro modelo preditivo.

| ID | Umidade Solo (%) | Chuva 48h (mm) | Inclinação Graus | Peso Máquina (Ton) | Risco Acidente (Alvo) |
|:---|:---|:---|:---|:---|:---|
| 1 | 30 | 5.0 | 5 | 12 | Baixo |
| 2 | 85 | 45.0 | 12 | 15 | Alto (Alerta) |
| 3 | 90 | 60.0 | 25 | 15 | Crítico (Parada) |
| 4 | 40 | 0.0 | 18 | 10 | Médio |

* **Umidade_Solo e Inclinacao:** Serão coletadas pelo ESP32 (simulado).
* **Chuva_48h:** Coletada via API de Clima (ex: OpenWeather) pelo Python.
* **Peso_Maquina:** Dado fixo no sistema.

## 5. Arquitetura da Solução
O sistema roda em uma arquitetura local para garantir baixa latência e dependência mínima de internet:
1.  **Coleta (Wokwi/ESP32):** O ESP32 simula a leitura de sensores (potenciômetros simulando umidade/inclinação).
2.  **Comunicação:** Os dados do ESP32 são enviados via porta Serial (ou Wi-Fi local) para o computador.
3.  **Processamento e IA (VS Code / Python):** Um script Python recebe os dados, consulta a API de clima e processa o modelo preditivo.
4.  **Saída:** O Python devolve um comando para o ESP32 (ex: acender LED Vermelho) e exibe o risco na tela.

## 6. Proposta Inicial do Modelo Preditivo
Utilizaremos um modelo de **Classificação** (ex: Árvore de Decisão ou Random Forest usando a biblioteca *scikit-learn* em Python).
* **Entradas:** Umidade do solo, chuva acumulada, inclinação e peso.
* **Saída:** Uma categoria de risco (Baixo, Médio, Alto, Crítico).
* **Justificativa:** Modelos baseados em árvores criam regras claras (ex: "Se inclinação > 15 e chuva > 40mm = Risco Crítico").

## 7. Planejamento (Próximas Etapas)
- [ ] **Sprint 2:** Criar o circuito no Wokwi com sensores e o código C++ para o ESP32.
- [ ] **Sprint 3:** Criar o script Python no VS Code para ler a Serial e puxar a API.
- [ ] **Sprint 4:** Treinar o modelo de IA com o dataset simulado completo e integrar o fluxo.
