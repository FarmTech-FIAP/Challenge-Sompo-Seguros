-- =========================================================
-- AGRORISK TRACKER — CHALLENGE SOMPO SEGUROS (FIAP)
-- Arquivo de Consultas SQL (SQLite)
-- =========================================================
-- Banco:   sql/agrorisk.db
-- Tabela:  operacoes_risco
--
-- Estrutura da tabela (gerada pelo main.py via pandas.to_sql):
--   id_equipamento          TEXT     -- Ex.: TRATOR-I, COLHEITADEIRA-II
--   chuva_acumulada_mm      REAL     -- Chuva acumulada em 48h (mm)
--   umidade_solo_pct        REAL     -- Umidade do solo (%)
--   inclinacao_graus        REAL     -- Inclinação lateral do terreno (graus)
--   peso_maquina_ton        REAL     -- Peso estimado de carga (toneladas)
--   distancia_corpo_agua_m  REAL     -- Distância de corpos d'água (metros)
--   ocorreu_acidente        INTEGER  -- 0 = não, 1 = sim (sinistro)
--   score_risco             REAL     -- Score de risco da IA (0 a 100)
--   nivel_risco             TEXT     -- BAIXO, MÉDIO, ALTO, CRÍTICO
--
-- Como executar via terminal:
--   sqlite3 sql/agrorisk.db < sql/queries.sql
-- =========================================================


-- =========================================================
-- 1. LISTAR OPERAÇÕES
-- =========================================================

-- 1.1 Listar todas as operações registradas
SELECT *
FROM operacoes_risco;

-- 1.2 Listar as operações mais recentes (colunas principais)
SELECT id_equipamento,
       score_risco,
       nivel_risco,
       ocorreu_acidente
FROM operacoes_risco
LIMIT 20;

-- 1.3 Listar operações de um equipamento específico
SELECT *
FROM operacoes_risco
WHERE id_equipamento = 'TRATOR-I';

-- 1.4 Listar operações ordenadas pelo maior risco
SELECT id_equipamento,
       score_risco,
       nivel_risco
FROM operacoes_risco
ORDER BY score_risco DESC;


-- =========================================================
-- 2. CONTAR NÍVEIS DE RISCO
-- =========================================================

-- 2.1 Quantidade de operações por nível de risco
SELECT nivel_risco,
       COUNT(*) AS total_operacoes
FROM operacoes_risco
GROUP BY nivel_risco
ORDER BY total_operacoes DESC;

-- 2.2 Contagem de níveis na ordem lógica de severidade
SELECT nivel_risco,
       COUNT(*) AS total_operacoes
FROM operacoes_risco
GROUP BY nivel_risco
ORDER BY CASE nivel_risco
            WHEN 'BAIXO'   THEN 1
            WHEN 'MÉDIO'   THEN 2
            WHEN 'ALTO'    THEN 3
            WHEN 'CRÍTICO' THEN 4
         END;

-- 2.3 Distribuição percentual de cada nível de risco
SELECT nivel_risco,
       COUNT(*) AS total_operacoes,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM operacoes_risco), 2) AS percentual
FROM operacoes_risco
GROUP BY nivel_risco
ORDER BY total_operacoes DESC;

-- 2.4 Total de operações em risco crítico (gestão por exceção)
SELECT COUNT(*) AS total_criticas
FROM operacoes_risco
WHERE nivel_risco = 'CRÍTICO';


-- =========================================================
-- 3. MÉDIA DE SCORE DE RISCO
-- =========================================================

-- 3.1 Média geral do score de risco
SELECT ROUND(AVG(score_risco), 2) AS media_score_geral
FROM operacoes_risco;

-- 3.2 Média de score de risco por equipamento
SELECT id_equipamento,
       ROUND(AVG(score_risco), 2) AS media_score,
       COUNT(*) AS total_operacoes
FROM operacoes_risco
GROUP BY id_equipamento
ORDER BY media_score DESC;

-- 3.3 Estatísticas do score por nível de risco (mín, média, máx)
SELECT nivel_risco,
       ROUND(MIN(score_risco), 2) AS score_minimo,
       ROUND(AVG(score_risco), 2) AS score_medio,
       ROUND(MAX(score_risco), 2) AS score_maximo
FROM operacoes_risco
GROUP BY nivel_risco
ORDER BY score_medio;


-- =========================================================
-- 4. CONSULTAS PARA O DASHBOARD
-- =========================================================

-- 4.1 KPIs principais da "Visão do Gestor"
--     (total de operações, sinistros, taxa de sinistralidade,
--      média de score e alertas críticos)
SELECT COUNT(*)                                                   AS total_operacoes,
       SUM(ocorreu_acidente)                                      AS total_acidentes,
       ROUND(SUM(ocorreu_acidente) * 100.0 / COUNT(*), 2)         AS taxa_sinistralidade_pct,
       ROUND(AVG(score_risco), 1)                                 AS media_score_risco,
       SUM(CASE WHEN nivel_risco = 'CRÍTICO' THEN 1 ELSE 0 END)   AS alertas_criticos
FROM operacoes_risco;

-- 4.2 Operações em risco crítico (tabela de atenção imediata)
SELECT id_equipamento,
       score_risco,
       nivel_risco,
       inclinacao_graus,
       umidade_solo_pct,
       distancia_corpo_agua_m,
       peso_maquina_ton
FROM operacoes_risco
WHERE nivel_risco = 'CRÍTICO'
ORDER BY score_risco DESC
LIMIT 20;

-- 4.3 Distribuição de riscos por categoria (gráfico de barras)
SELECT nivel_risco,
       COUNT(*) AS quantidade
FROM operacoes_risco
GROUP BY nivel_risco;

-- 4.4 Taxa de sinistralidade por equipamento (ranking de frota)
SELECT id_equipamento,
       COUNT(*)                                            AS total_operacoes,
       SUM(ocorreu_acidente)                               AS acidentes,
       ROUND(SUM(ocorreu_acidente) * 100.0 / COUNT(*), 2)  AS taxa_sinistralidade_pct,
       ROUND(AVG(score_risco), 2)                          AS media_score
FROM operacoes_risco
GROUP BY id_equipamento
ORDER BY taxa_sinistralidade_pct DESC;

-- 4.5 Telemetria mais recente de um equipamento (Painel do Operador)
SELECT id_equipamento,
       score_risco,
       nivel_risco,
       inclinacao_graus,
       umidade_solo_pct,
       distancia_corpo_agua_m,
       peso_maquina_ton
FROM operacoes_risco
WHERE id_equipamento = 'COLHEITADEIRA-I'
ORDER BY rowid DESC
LIMIT 1;

-- 4.6 Influência da proximidade de corpos d'água no risco
--     (operações próximas a rios/canais tendem a ter score maior)
SELECT CASE
           WHEN distancia_corpo_agua_m < 50  THEN '0-50m (crítico)'
           WHEN distancia_corpo_agua_m < 200 THEN '50-200m (alto)'
           WHEN distancia_corpo_agua_m < 500 THEN '200-500m (moderado)'
           ELSE '500m+ (seguro)'
       END AS faixa_distancia_agua,
       COUNT(*)                   AS total_operacoes,
       ROUND(AVG(score_risco), 2) AS media_score,
       SUM(ocorreu_acidente)      AS acidentes
FROM operacoes_risco
GROUP BY faixa_distancia_agua
ORDER BY media_score DESC;

-- 4.7 Médias das variáveis dos sensores por nível de risco
--     (validação estatística das correlações de risco)
SELECT nivel_risco,
       ROUND(AVG(chuva_acumulada_mm), 2)     AS media_chuva_mm,
       ROUND(AVG(umidade_solo_pct), 2)       AS media_umidade_pct,
       ROUND(AVG(inclinacao_graus), 2)       AS media_inclinacao_graus,
       ROUND(AVG(peso_maquina_ton), 2)       AS media_peso_ton,
       ROUND(AVG(distancia_corpo_agua_m), 2) AS media_dist_agua_m
FROM operacoes_risco
GROUP BY nivel_risco
ORDER BY CASE nivel_risco
            WHEN 'BAIXO'   THEN 1
            WHEN 'MÉDIO'   THEN 2
            WHEN 'ALTO'    THEN 3
            WHEN 'CRÍTICO' THEN 4
         END;
