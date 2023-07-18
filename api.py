# api is not currently in use. it's just meant to be a blueprint for possible future endavours.
from fastapi import FastAPI
import sqlite3

app = FastAPI()

# Assuming you have a SQLite database with a table named "shipping_costs"
DB_NAME = 'shipping_costs.db'

def get_shipping_costs():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM shipping_costs')
    rows = cursor.fetchall()

    # Fetch the column names from the database
    columns = [description[0] for description in cursor.description]

    conn.close()

    return columns, rows

@app.get("/shipping_costs", response_model=dict)
def shipping_costs():
    columns, rows = get_shipping_costs()

    response_data = {}
    for idx, row in enumerate(rows):
        row_data = {}
        for col_idx, col_name in enumerate(columns):
            row_data[col_name] = row[col_idx]
        response_data[str(idx)] = row_data

    return response_data
