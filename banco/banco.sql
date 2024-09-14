CREATE TABLE IF NOT EXISTS users (
  id integer PRIMARY KEY autoincrement,
  nome varchar(45) NOT NULL,
  created timestamp NULL DEFAULT NULL,
  modified timestamp NULL DEFAULT NULL
);

INSERT INTO users (id, nome, created, modified) VALUES
(1, 'Mano Lima', '2019-10-18 16:28:53', '2019-10-18 16:28:53')