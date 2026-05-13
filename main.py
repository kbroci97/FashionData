from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import sqlite3

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


def get_db_connection():
    conn = sqlite3.connect("fashion.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/")
def home():
    return FileResponse("static/index.html")


@app.get("/api/dresses")
def get_dresses():

    conn = get_db_connection()

    dresses = conn.execute(
        '''
        SELECT
            rowid as id,
            product_name,
            brand,
            sale_price_usd,
            full_price_usd,
            image_url

        FROM dresses
        '''
    ).fetchall()

    conn.close()

    return [dict(row) for row in dresses]


@app.get("/api/dresses/{dress_id}")
def get_dress(dress_id: int):

    conn = get_db_connection()

    dress = conn.execute(
        '''
        SELECT
            dresses.rowid as id,
            dresses.product_name,
            dresses.brand,
            dresses.sale_price_usd,
            dresses.full_price_usd,

            designers.ceo,
            designers.creative_director,
            designers.founded_year,
            designers.country,
            designers.headquarters,
            designers.website

        FROM dresses

        LEFT JOIN designers
        ON LOWER(dresses.brand) = LOWER(designers.brand)

        WHERE dresses.rowid = ?
        ''',
        (dress_id,)
    ).fetchone()

    conn.close()

    if not dress:
        return {"error": "Dress not found"}

    return dict(dress)
