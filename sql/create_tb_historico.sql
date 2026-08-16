CREATE TABLE tb_historico_risco (
    id_leitura          NUMBER GENERATED ALWAYS AS IDENTITY,
    id_equipamento      VARCHAR2(50) NOT NULL,
    data_hora           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    chuva_acumulada_mm  NUMBER(5,2) NOT NULL,
    umidade_solo_pct    NUMBER(5,2) NOT NULL,
    inclinacao_graus    NUMBER(5,2) NOT NULL,
    peso_maquina_ton    NUMBER(5,2) NOT NULL,
    score_risco         NUMBER(3) NOT NULL,
    classificacao_alerta VARCHAR2(20) NOT NULL,
    
    CONSTRAINT pk_historico_risco PRIMARY KEY (id_leitura)
);
