from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel, Session, create_engine, select
import sqlite3

app = FastAPI()

engine = create_engine("sqlite:///fashion.db")

class Dress(SQLModel, table=False):
    brand: str | None = None
    product_name: str | None = None
    full_price_usd: str | None = None
    image_url: str | None = None

class Designer(SQLModel, table=False):
    id: int | None = None
    brand: str | None = None
    founded_year: str | None = None
    creative_director: str | None = None
    ceo: str | None = None
    country: str | None = None
    headquarters: str | None = None
    website: str | None = None

with Session(engine) as session:
    print("SQLModel session initialized")

def get_db_connection():
    conn = sqlite3.connect("fashion.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/")
def home():
    return FileResponse("static/index.html")


@app.get("/api/dresses")
def get_dresses():

    conn = sqlite3.connect("fashion.db")
    conn.row_factory = sqlite3.Row

    dresses = conn.execute("""

        SELECT
            rowid as id,
            brand,
            product_name,
            full_price_usd,
            image_url

        FROM dresses

    """).fetchall()

    conn.close()

    return [dict(dress) for dress in dresses]


@app.get("/api/dresses/{dress_id}")
def get_dress(dress_id: int):

    conn = sqlite3.connect("fashion.db")
    conn.row_factory = sqlite3.Row

    dress = conn.execute("""

        SELECT
            dresses.rowid as id,
            dresses.brand,
            dresses.product_name,
            dresses.full_price_usd,
            dresses.image_url,

            designers.creative_director,
            designers.ceo,
            designers.country,
            designers.headquarters,
            designers.founded_year

        FROM dresses

        LEFT JOIN designers
        ON dresses.brand = designers.brand

        WHERE dresses.rowid = ?

    """, (dress_id,)).fetchone()

    conn.close()

    if dress is None:
        return {"error": "Dress not found"}

    return dict(dress)

app.mount("/static", StaticFiles(directory="static"), name="static")