CREATE DATABASE IF NOT EXISTS dasm DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_general_ci;

USE dasm;

-- topic v3/espm/devices/passage01/up
-- topic v3/espm/devices/passage02/up
-- { "end_device_ids": { "device_id": "passage01" }, "uplink_message": { "rx_metadata": [{ "timestamp": 2040934975 }], "decoded_payload": { "battery": 0, "period_in": 0, "period_out": 0 } } }
CREATE TABLE passagem (
  id bigint NOT NULL AUTO_INCREMENT,
  data datetime NOT NULL,
  id_sensor tinyint NOT NULL,
  delta int NOT NULL,
  bateria tinyint NOT NULL,
  entrada int NOT NULL,
  saida int NOT NULL,
  PRIMARY KEY (id),
  KEY passagem_data_id_sensor (data, id_sensor),
  KEY passagem_id_sensor (id_sensor)
);

-- tabela pessoa
CREATE TABLE IF NOT EXISTS pessoa (
  id BIGINT NOT NULL AUTO_INCREMENT,
  nome VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY pessoa_email (email)
);

-- Query de consolidação por dia da semana (1 = domingo, 2 = segunda...) e por hora, para o heatmap com 7 colunas e 24 linhas
select dayofweek(data) dia_semana, extract(hour from data) hora, sum(entrada + saida) total
from passagem
where data between '2025-03-03 00:00:00' and '2025-03-14 23:59:59'
and id_sensor = 2
group by dia_semana, hora;

-- Query de consolidação por dia do mês e por hora, para o heatmap de visão explodida por dia da semana com N colunas e 24 linhas
select date_format(date(data), '%d/%m/%Y') dia, extract(hour from data) hora, sum(entrada + saida) total
from passagem
where data between '2025-03-03 00:00:00' and '2025-03-14 23:59:59'
and dayofweek(data) = 2
and id_sensor = 2
group by dia, hora;

-- Query de consolidação de pessoas presentes no espaço por dia do mês e por hora, para o heatmap de visão explodida por presença com N colunas e 24 linhas
-- A presença é dada por uma coluna virtual, gerada via código, onde:
-- presenca[i] = max(0, presenca[i - 1] + total_entrada[i] - total_saida[i])
-- exceto presenca[0], que vale 0
-- (Consolidado i deve ser reiniciado para 0 na mudança de dia)
select date_format(date(data), '%d/%m/%Y') dia, extract(hour from data) hora, sum(entrada) total_entrada, sum(saida) total_saida
from passagem
where data between '2025-03-03 00:00:00' and '2025-03-14 23:59:59'
and id_sensor = 2
group by dia, hora
order by dia, hora;

-- tabela contratante
CREATE TABLE IF NOT EXISTS contratante(
  id INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL,
  empresa VARCHAR(100) NOT NULL,
  senha VARCHAR(255) NOT NULL
);

-- tabela de evento
CREATE TABLE IF NOT EXISTS evento(
  id INT AUTO_INCREMENT PRIMARY KEY,
  titulo VARCHAR(100) NOT NULL,
  descricao TEXT,
  data_evento DATETIME NOT NULL,
  id_responsavel INT,
  FOREIGN KEY (id_responsavel) REFERENCES contratante(id)
);

-- table manutenção
CREATE TABLE IF NOT EXISTS manutencao (
  id INT AUTO_INCREMENT PRIMARY KEY,
  descricao TEXT,
  data_manutencao DATETIME NOT NULL,
  responsavel VARCHAR(100) NOT NULL,
  relacao_evento ENUM('antes', 'depois'),
  nivel ENUM('basica', 'limpeza', 'preventiva', 'pesada'),
  id_evento INT,
  FOREIGN KEY (id_evento) REFERENCES evento(id)
);