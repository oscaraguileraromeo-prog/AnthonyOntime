# Registro de Jornada de Conducción para Transportistas

Este proyecto es una aplicación web progresiva (PWA) diseñada para digitalizar las "Hojas de Registro y Control de Servicio Diario" de un chófer de camión de gran tonelaje. Está optimizada para su uso por parte de transportistas de mercancías como Antonio Becerra Ortega y conectada a una base de datos MySQL proporcionada por la empresa ONTIME.

## Características principales

- Registro diario de turnos laborales con kilometraje, horarios y trayectos.
- Subregistro de múltiples trayectos por turno.
- Consulta de jornadas anteriores.
- Generación de informes mensuales en PDF o CSV.
- Cálculo de horas ordinarias y horas extra.
- Diseño responsivo y uso como aplicación instalable desde el navegador.
- Preparada para incorporar asistente de voz en el futuro.

## Tecnología prevista

- Frontend: HTML, CSS, JavaScript
- Backend: Python (Flask) o Node.js (según elección del agente)
- Base de datos: MySQL
- Generación de documentos: wkhtmltopdf o equivalente

## Estado actual

Repositorio iniciado el 27/07/2025. Preparado para recibir los archivos generados automáticamente por el Agente GPT.

---

## Cómo ejecutar

1. Instalar dependencias:
   ```bash
   pip install flask mysql-connector-python fpdf2
   ```
2. Lanzar el servidor:
   ```bash
   python3 app/app.py
   ```
3. Acceder a `http://localhost:5000` desde el navegador para usar la aplicación.

La base de datos debe existir con las tablas definidas en `init.sql`. Importa el archivo en tu servidor MySQL antes de iniciar.
