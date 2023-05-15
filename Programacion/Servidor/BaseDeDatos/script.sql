CREATE DATABASE tiempo;
USE tiempo;

CREATE TABLE mediciones (
  id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
  fecha DATETIME,
  temperatura FLOAT(5,2),
  humedad FLOAT(5,2),
  presion FLOAT(6,2),
  precipitaciones FLOAT(5,2),
  velocidad FLOAT(5,2),
  direccion FLOAT(5,2),
  uvi FLOAT(4,2),
  lux FLOAT(8,2),
  ppm FLOAT(6,2)
);