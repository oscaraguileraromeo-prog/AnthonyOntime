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

## Puesta en marcha

Instala las dependencias en un entorno Python y ejecuta `app.py`:

```bash
pip install flask flask-cors mysql-connector-python pdfkit
python app.py
```

Para la generación de PDF es necesario tener instalado `wkhtmltopdf` en el sistema.

El asistente por voz usa la API de OpenRouter configurada desde el botón de ajustes (⚙️). Si no se introduce una API válida, el botón de voz permanecerá oculto.

## Estado actual

Aplicación mínima funcional con registro y consulta de jornadas, generación de PDFs y configuración básica del asistente por voz. Algunas funciones avanzadas pueden requerir ajustes adicionales.

---
