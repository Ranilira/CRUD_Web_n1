DROP TABLE IF EXISTS users;

CREATE TABLE IF NOT EXISTS users (
  id integer PRIMARY KEY autoincrement,
  nome varchar(45) NOT NULL,
  login varchar(45) NOT NULL,
  password  VARCHAR(255),  -- Adicionando a coluna para armazenar senhas
  created timestamp NULL DEFAULT NULL,
  modified timestamp NULL DEFAULT NULL,
  status INTEGER DEFAULT 1
);
