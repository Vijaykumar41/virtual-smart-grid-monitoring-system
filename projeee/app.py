from flask import Flask, render_template, request
import mysql.connector
from datetime import date

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Vijay#2004",
        database="electricity_db"
    )

@app.route("/", methods=["GET", "POST"])
def index():
    report = None

    if request.method == "POST":
        voltage = float(request.form["voltage"])
        tariff = float(request.form["tariff"])
        units = float(request.form["units"])

        current = (units * 1000) / voltage
        power = voltage * current
        price = units * tariff

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO daily_consumption
            (entry_date, voltage, tariff, units, current, power, price)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (date.today(), voltage, tariff, units, current, power, price))

        conn.commit()

        cur.execute("""
            SELECT 
                COUNT(*),
                AVG(units), MIN(units), MAX(units),
                AVG(current), MIN(current), MAX(current),
                AVG(power), AVG(price),
                GROUP_CONCAT(entry_date),
                GROUP_CONCAT(units),
                GROUP_CONCAT(price)
            FROM daily_consumption
        """)

        row = cur.fetchone()
        conn.close()

        dates = row[9].split(",")
        units_list = list(map(float, row[10].split(",")))
        price_list = list(map(float, row[11].split(",")))

        report = {
            "total_days": row[0],
            "avg_units": row[1],
            "min_units": row[2],
            "max_units": row[3],
            "avg_current": row[4],
            "min_current": row[5],
            "max_current": row[6],
            "avg_power": row[7],
            "avg_price": row[8],
            "monthly_bill": row[8] * 30,
            "yearly_bill": row[8] * 365,
            "dates": dates,
            "units_list": units_list,
            "price_list": price_list
        }

    return render_template("index.html", report=report)

if __name__ == "__main__":
    app.run(debug=True)
