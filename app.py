import os
import psycopg2
import time
from datetime import datetime
from flask import Flask, request, send_from_directory, Response

app = Flask(__name__)

conn_string = "host='localhost' dbname='bge' user='bge' password='ribszijngoed'"


def get_conn():
    retries = 5
    while True:
        retries -= 1
        try:
            return psycopg2.connect(conn_string)
        except psycopg2.OperationalError:
            time.sleep(1)
            if retries <= 0:
                raise


conn = get_conn()
root_dir = os.getcwd()


@app.route('/')
def index():
    path = os.path.join(root_dir, 'static')
    return send_from_directory(path, 'index.html')


@app.route('/hist')
def get_histogram():
    result = []
    with conn.cursor() as cur:
        cur.execute("""
        SELECT 
            EXTRACT(year from created) AS year,
            EXTRACT(month from created) AS month,
            EXTRACT(day from created) AS day,
            EXTRACT(hour from created) AS hour,
            EXTRACT(minute from created) AS minute,
            MIN(temperature) min,
            AVG(temperature) avg,
            MAX(temperature) max
        FROM temperature 
        GROUP BY year, month, day, hour, minute 
        ORDER BY year, month, day, hour, minute ASC""")
        for row in cur:
            print(row)
            result.append("""{{"date": "{}-{:02d}-{:02d}T{:02d}:{:02d}", "min":{}, "avg":{}, "max":{}}}""".format(
                int(row[0]),
                int(row[1]),
                int(row[2]),
                int(row[3]),
                int(row[4]),
                row[5],
                row[6],
                row[7]
            ))

    return Response(response="[{}]".format(", ".join(result)),
                    status=200,
                    mimetype="application/javascript")


@app.route('/static/<path:filename>')
def download_file(filename):
    path = os.path.join(root_dir, 'static')
    return send_from_directory(path, filename)


@app.route('/temp')
def post_temperature():
    temp = request.args.get('temp')
    with conn.cursor() as cur:
        print(temp)
        cur.execute("""
        INSERT INTO temperature(created, temperature) 
        VALUES('{}', {:f});
        """.format(datetime.now(), float(temp)))
    return "OK"


if __name__ == '__main__':
    app.run(host='0.0.0.0')
