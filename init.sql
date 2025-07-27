
CREATE TABLE IF NOT EXISTS jornadas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    matricula VARCHAR(20) NOT NULL,
    remolque VARCHAR(50),
    kms_inicio INT NOT NULL,
    kms_fin INT NOT NULL,
    horas_turno DECIMAL(5,2) GENERATED ALWAYS AS (TIMESTAMPDIFF(MINUTE, hora_inicio, hora_fin)/60) STORED,
    observaciones TEXT
);

CREATE TABLE IF NOT EXISTS trayectos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    jornada_id INT NOT NULL,
    hora_salida TIME NOT NULL,
    origen VARCHAR(100) NOT NULL,
    hora_llegada TIME NOT NULL,
    destino VARCHAR(100) NOT NULL,
    FOREIGN KEY (jornada_id) REFERENCES jornadas(id) ON DELETE CASCADE
);
