import pandas as pd
import sqlite3

# Connect to database
conn = sqlite3.connect("fashion.db")

# Load dresses table
df = pd.read_sql("SELECT * FROM dresses", conn)

# Remove sale price column if it exists
if "sale_price_usd" in df.columns:
    df = df.drop(columns=["sale_price_usd"])

# Replace dresses table
df.to_sql(
    "dresses",
    conn,
    if_exists="replace",
    index=False
)

conn.close()

print("Sale price removed successfully!")