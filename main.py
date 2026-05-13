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
            dresses.id,
            dresses."Product Name" as product_name,
            dresses.Brand as brand,
            dresses."Sale Price (USD)" as sale_price,
            dresses."Full Price (USD)" as full_price,
            dresses."Image URL" as image_url
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
            dresses.id,
            dresses."Product Name" as product_name,
            dresses.Brand as brand,
            dresses."Sale Price (USD)" as sale_price,
            dresses."Full Price (USD)" as full_price,
            dresses."Image URL" as image_url,

            designers.*

        FROM dresses

        LEFT JOIN designers
        ON dresses.designer_id = designers.id

        WHERE dresses.id = ?
        ''',
        (dress_id,)
    ).fetchone()

    conn.close()

    if not dress:
        return {"error": "Dress not found"}

    return dict(dress)
