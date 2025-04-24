import requests
import datetime
import sqlite3

DB_FILE = "spot_prices.db"

url = 'https://www.ote-cr.cz/cs/kratkodobe-trhy/elektrina/denni-trh/@@chart-data?report_date='

def data_exists_check(date):
    store_date = date.date().isoformat()

    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM prices WHERE date = ?", (store_date,))
        count = c.fetchone()[0]
        return count == 24

def store_data(date):
    store_date = date.date().isoformat()
    data_url = url + store_date

    try:
        response = requests.get(data_url)
        response.raise_for_status()
        data = response.json()
        points = data["data"]["dataLine"][1]["point"]

        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            for hour, point in enumerate(points):
                price = point["y"]
                c.execute('''INSERT OR REPLACE INTO prices (date, hour, price) VALUES (?, ?, ?)''', (store_date, hour, price))
            conn.commit()

        print(f"Data for {store_date} stored successfully.")

    except Exception as e:
        print(f"Error storing data for {store_date}: {e}")

def main():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS prices (
            date TEXT,
            hour INTEGER,
            price REAL,
            PRIMARY KEY (date, hour))''')

    todays_date = datetime.datetime.now()
    tommorrows_date = todays_date + datetime.timedelta(days=1)

    if not data_exists_check(todays_date):
        store_data(todays_date)

    if not data_exists_check(tommorrows_date):
        store_data(tommorrows_date)

main()
