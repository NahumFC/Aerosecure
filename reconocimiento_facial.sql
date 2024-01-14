drop database if exists reconocimiento_facial;

CREATE DATABASE reconocimiento_facial;

USE reconocimiento_facial;

CREATE TABLE usuarios (
    nombre VARCHAR(100),
    encoding BLOB,
	password VARBINARY(255),
	numero_trabajador VARCHAR(250) PRIMARY KEY
);

CREATE TABLE delincuentes(
	nombre VARCHAR(100),
    apellido VARCHAR(100),
    nacionalidad VARCHAR(100),
    cargos VARCHAR(1000),
    encoding BLOB
);

SELECT * FROM `usuarios`;
SELECT * FROM `delincuentes`;