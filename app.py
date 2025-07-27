import os
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import mysql.connector
from io import BytesIO
from datetime import datetime

app = Flask(__name__)
CORS(app)

def get_db():
    return mysql.connector.connect(
        host='srv1789.hstgr.io',
        user='u643065128_ontime',
        password='Time1On2',
        database='u643065128_ontime'
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/consultar')
def consultar():
    return render_template('consultar.html')

@app.route('/api/jornadas', methods=['GET', 'POST'])
def jornadas():
    db = get_db()
    cur = db.cursor(dictionary=True)
    if request.method == 'POST':
        datos = request.form
        cur.execute("""
            INSERT INTO jornadas (fecha, hora_inicio, hora_fin, matricula, remolque, kms_inicio, kms_fin, observaciones)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            datos['inicio'][:10], datos['inicio'][11:], datos['fin'][11:], datos['matricula'], datos.get('remolque'), datos['kms_inicio'], datos['kms_fin'], datos.get('observaciones')
        ))
        jornada_id = cur.lastrowid
        trayectos = zip(datos.getlist('hora_salida[]'), datos.getlist('origen[]'), datos.getlist('hora_llegada[]'), datos.getlist('destino[]'))
        for hs, o, hl, d in trayectos:
            cur.execute("""
                INSERT INTO trayectos (jornada_id, hora_salida, origen, hora_llegada, destino)
                VALUES (%s,%s,%s,%s,%s)
            """, (jornada_id, hs, o, hl, d))
        db.commit()
        db.close()
        return '', 201
    else:
        desde = request.args.get('desde')
        hasta = request.args.get('hasta')
        sql = 'SELECT * FROM jornadas'
        params = []
        if desde and hasta:
            sql += ' WHERE fecha BETWEEN %s AND %s'
            params = [desde, hasta]
        cur.execute(sql, params)
        datos = cur.fetchall()
        db.close()
        return jsonify(datos)

@app.route('/api/jornadas/<int:jid>/pdf')
def jornada_pdf(jid):
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute('SELECT * FROM jornadas WHERE id=%s', (jid,))
    j = cur.fetchone()
    cur.execute('SELECT * FROM trayectos WHERE jornada_id=%s', (jid,))
    t = cur.fetchall()
    db.close()
    html = render_template('reporte.html', j=j, trayectos=t)
    try:
        import pdfkit
        pdf = pdfkit.from_string(html, False)
        return send_file(BytesIO(pdf), download_name='reporte.pdf', mimetype='application/pdf')
    except Exception as e:
        return html

if __name__ == '__main__':
    app.run(debug=True)
