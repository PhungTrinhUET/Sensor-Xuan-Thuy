# Sensor-Xuan-Thuy
DHT11 to ThingsBoard and getData from ThingsBoard to Database

#CREATE DATABASE 
CREATE TABLE IF NOT EXISTS "weatherData" (
    id SERIAL PRIMARY KEY,
    "dateTime" TIMESTAMP,
    "outsideHumidity" FLOAT,
    "outsideTemp" FLOAT
);

SELECT * FROM "weatherData"


