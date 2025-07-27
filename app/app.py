import os
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
import mysql.connector
from fpdf import FPDF
import csv
from io import BytesIO, StringIO
import requests

app = Flask(__name__)

DB_CONFIG = {
    'host': 'srv1789.hstgr.io',
    'user': 'u643065128_ontime',
    'password': 'Time1On2',
    'database': 'u643065128_ontime'
}


def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# Devuelve los 7 últimos turnos para dar contexto al asistente
def ultimos_turnos():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT fecha, hora_inicio, hora_fin, matricula, kms_inicio, kms_fin FROM jornadas ORDER BY fecha DESC, hora_inicio DESC LIMIT 7")
    datos = cur.fetchall()
    conn.close()
    return datos

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT matricula, kms_fin FROM jornadas ORDER BY id DESC LIMIT 1")
    last = cur.fetchone()
    conn.close()
    return render_template('index.html', last=last)

@app.route('/guardar', methods=['POST'])
def guardar():
    data = request.form
    conn = get_db_connection()
    cur = conn.cursor()
    sql = (
        "INSERT INTO jornadas (fecha, hora_inicio, hora_fin, matricula, remolque, kms_inicio, kms_fin, observaciones)"
        " VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
    )
    cur.execute(sql, (
        data['fecha'], data['hora_inicio'], data['hora_fin'], data['matricula'],
        data.get('remolque'), data['kms_inicio'], data['kms_fin'], data.get('observaciones')
    ))
    jornada_id = cur.lastrowid
    trayectos = []
    ts = data.getlist('t_hora_salida')
    for i in range(len(ts)):
        trayectos.append((
            jornada_id,
            ts[i],
            data.getlist('t_origen')[i],
            data.getlist('t_hora_llegada')[i],
            data.getlist('t_destino')[i]
        ))
    cur.executemany(
        "INSERT INTO trayectos (jornada_id, hora_salida, origen, hora_llegada, destino) VALUES (%s,%s,%s,%s,%s)",
        trayectos
    )
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/jornadas')
def jornadas():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM jornadas ORDER BY fecha DESC, hora_inicio DESC")
    jorn = cur.fetchall()
    conn.close()
    return render_template('jornadas.html', jornadas=jorn)

# Editar una jornada existente
@app.route('/jornadas/<int:id>/editar', methods=['GET', 'POST'])
def editar_jornada(id):
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    if request.method == 'POST':
        data = request.form
        cur.execute(
            "UPDATE jornadas SET fecha=%s, hora_inicio=%s, hora_fin=%s, matricula=%s, remolque=%s, kms_inicio=%s, kms_fin=%s, observaciones=%s WHERE id=%s",
            (data['fecha'], data['hora_inicio'], data['hora_fin'], data['matricula'], data.get('remolque'), data['kms_inicio'], data['kms_fin'], data.get('observaciones'), id)
        )
        cur.execute("DELETE FROM trayectos WHERE jornada_id=%s", (id,))
        trayectos = []
        ts = data.getlist('t_hora_salida')
        for i in range(len(ts)):
            trayectos.append((id, ts[i], data.getlist('t_origen')[i], data.getlist('t_hora_llegada')[i], data.getlist('t_destino')[i]))
        if trayectos:
            cur.executemany("INSERT INTO trayectos (jornada_id, hora_salida, origen, hora_llegada, destino) VALUES (%s,%s,%s,%s,%s)", trayectos)
        conn.commit()
        conn.close()
        return redirect(url_for('jornadas'))
    else:
        cur.execute("SELECT * FROM jornadas WHERE id=%s", (id,))
        jornada = cur.fetchone()
        cur.execute("SELECT * FROM trayectos WHERE jornada_id=%s", (id,))
        trayectos = cur.fetchall()
        conn.close()
        return render_template('editar.html', jornada=jornada, trayectos=trayectos)

@app.route('/jornadas/<int:id>/eliminar', methods=['POST'])
def eliminar_jornada(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM jornadas WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('jornadas'))

# Consulta de jornadas por rango de fechas
@app.route('/consulta')
def consulta():
    inicio = request.args.get('inicio')
    fin = request.args.get('fin')
    datos = []
    total = extra = 0
    if inicio and fin:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM jornadas WHERE fecha BETWEEN %s AND %s ORDER BY fecha", (inicio, fin))
        datos = cur.fetchall()
        cur.execute("SELECT SUM(horas_turno) as total, SUM(GREATEST(horas_turno-8,0)) as extra FROM jornadas WHERE fecha BETWEEN %s AND %s", (inicio, fin))
        res = cur.fetchone()
        total = res['total'] or 0
        extra = res['extra'] or 0
        conn.close()
    return render_template('consulta.html', datos=datos, total=total, extra=extra, inicio=inicio, fin=fin)

@app.route('/reporte')
def reporte():
    inicio = request.args.get('inicio')
    fin = request.args.get('fin')
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM jornadas WHERE fecha BETWEEN %s AND %s ORDER BY fecha", (inicio, fin))
    datos = cur.fetchall()
    cur.execute("SELECT SUM(horas_turno) as total, SUM(GREATEST(horas_turno-8,0)) as extra FROM jornadas WHERE fecha BETWEEN %s AND %s", (inicio, fin))
    totales = cur.fetchone()
    conn.close()

    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, f'Antonio Becerra Ortega - ONTIME', 0, 1, 'C')
            self.cell(0, 10, f'Del {inicio} al {fin}', 0, 1, 'C')
            self.ln(5)
        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Arial', size=10)
    for j in datos:
        extra = max(float(j['horas_turno']) - 8.0, 0)
        linea = f"{j['fecha']} {j['hora_inicio']}-{j['hora_fin']} Matricula: {j['matricula']} Kms: {j['kms_inicio']}-{j['kms_fin']} Horas: {j['horas_turno']} Extra: {extra:.2f}"
        pdf.cell(0, 8, linea, 0, 1)
    pdf.ln(4)
    pdf.cell(0, 8, f'Horas totales: {totales["total"] or 0} - Horas extra: {totales["extra"] or 0}', 0, 1)
    output = BytesIO()
    pdf.output(output)
    output.seek(0)
    return send_file(output, download_name='reporte.pdf', as_attachment=True)

@app.route('/csv')
def export_csv():
    inicio = request.args.get('inicio')
    fin = request.args.get('fin')
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM jornadas WHERE fecha BETWEEN %s AND %s ORDER BY fecha", (inicio, fin))
    datos = cur.fetchall()
    conn.close()
    si = StringIO()
    if datos:
        writer = csv.DictWriter(si, fieldnames=datos[0].keys())
        writer.writeheader()
        writer.writerows(datos)
    output = BytesIO()
    output.write(si.getvalue().encode('utf-8'))
    output.seek(0)
    return send_file(output, download_name='reporte.csv', as_attachment=True)

@app.route('/api/ultimas_jornadas')
def ultimas_jornadas():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM jornadas ORDER BY fecha DESC, hora_inicio DESC LIMIT 7")
    datos = cur.fetchall()
    conn.close()
    return jsonify(datos)

# Endpoint para interactuar con la API de OpenRouter
@app.route('/assistant', methods=['POST'])
def assistant():
    data = request.get_json()
    key = data.get('key')
    model = data.get('model')
    messages = data.get('messages', [])
    # Instrucciones del sistema en archivo separado
    with open(os.path.join(app.root_path, 'assistant', 'system.txt'), encoding='utf-8') as f:
        system = f.read().strip()
    contexto = json.dumps(ultimos_turnos(), ensure_ascii=False)
    mensajes = [{'role': 'system', 'content': f"{system}\nUltimos turnos: {contexto}"}] + messages
    resp = requests.post(
        'https://openrouter.ai/api/v1/chat/completions',
        headers={'Authorization': f'Bearer {key}'},
        json={'model': model, 'messages': mensajes}
    )
    return jsonify(resp.json())

if __name__ == '__main__':
    app.run(debug=True)
