import datetime
import os
import psycopg2
import time
from flask import Flask, request, send_from_directory, Response

application = Flask(__name__)

conn_string = "host='postgres' dbname='bge' user='bge' password='ribszijngoed'"


def get_conn():
    retries = 5
    while True:
        retries -= 1
        try:
            _conn = psycopg2.connect(conn_string)
            _conn.autocommit = True
            return _conn
        except psycopg2.OperationalError:
            time.sleep(1)
            if retries <= 0:
                raise


conn = get_conn()
root_dir = os.getcwd()


@application.route('/')
def index():
    path = os.path.join(root_dir, 'static')
    return send_from_directory(path, 'index.html')


@application.route('/hist')
def get_histogram():
    result = []
    intercept = 0
    slope = 0
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

        cur.execute("""
            SELECT 
                regr_intercept(temperature, extract(epoch FROM created)) AS intercept, 
                regr_slope(temperature, extract(epoch FROM created)) AS slope
            FROM temperature
            WHERE created >= NOW() - INTERVAL '1 HOUR'
            HAVING COUNT(*) > 1
        """)
        for row in cur:
            if row[0]:
                intercept = float(row[0])
                slope = float(row[1])

    return Response(response="{{\"hist\":[{}], \"intercept\":{}, \"slope\":{}}}".format(
        ", ".join(result),
        intercept,
        slope
    ),
        status=200,
        mimetype="application/javascript"
    )


@application.route('/static/<path:filename>')
def download_file(filename):
    path = os.path.join(root_dir, 'static')
    return send_from_directory(path, filename)


@application.route('/temp')
def post_temperature():
    temp = request.args.get('temp')
    date = request.args.get('date')

    if not date:
        date = datetime.datetime.now()

    with conn.cursor() as cur:
        cur.execute("""
        INSERT INTO temperature(created, temperature) 
        VALUES(%s, %s);
        """, (date, float(temp)))
    return "OK"


if __name__ == '__main__':
    application.run(host='0.0.0.0')
