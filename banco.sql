-- Banco de dados do formulário de contato da A Tupi Barber
-- Rodar na instância do MySQL:  sudo mysql < banco.sql

CREATE DATABASE IF NOT EXISTS tupibarber CHARACTER SET utf8mb4;
USE tupibarber;

CREATE TABLE IF NOT EXISTS mensagens (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  nome          VARCHAR(100) NOT NULL,
  telefone      VARCHAR(20),
  servico       VARCHAR(30),
  dia_preferido DATE NULL,
  mensagem      TEXT,
  criado_em     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
