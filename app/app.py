import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
import mysql.connector
from fpdf import FPDF
import csv
from io import BytesIO, StringIO

app = Flask(__name__)

DB_CONFIG = {
    'host': 'srv1789.hstgr.io',
    'user': 'u643065128_ontime',
    'password': 'Time1On2',
    'database': 'u643065128_ontime'
}


def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

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

@app.route('/jornadas/<int:id>/eliminar', methods=['POST'])
def eliminar_jornada(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM jornadas WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('jornadas'))

@app.route('/reporte')
def reporte():
    inicio = request.args.get('inicio')
    fin = request.args.get('fin')
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM jornadas WHERE fecha BETWEEN %s AND %s ORDER BY fecha", (inicio, fin))
    datos = cur.fetchall()
    cur.execute("SELECT SUM(horas_turno) as total FROM jornadas WHERE fecha BETWEEN %s AND %s", (inicio, fin))
    total_horas = cur.fetchone()['total'] or 0
    conn.close()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, f'Informe {inicio} a {fin}', 0, 1, 'C')
    pdf.set_font('Arial', size=10)
    for j in datos:
        pdf.cell(0, 8, f"{j['fecha']} {j['hora_inicio']}-{j['hora_fin']} Matricula: {j['matricula']} Kms: {j['kms_inicio']}-{j['kms_fin']}", 0, 1)
    pdf.ln(4)
    pdf.cell(0, 8, f'Horas totales: {total_horas}', 0, 1)
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

if __name__ == '__main__':
    app.run(debug=True)
