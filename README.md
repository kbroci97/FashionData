# FashionData

This project loads a dresses CSV into a SQLite database and serves it with FastAPI.

## Designer metadata table

You can create a new `designers` table in the same database.

- Seed it from the unique brands already in `dresses.csv`:

```bash
python load_dresses_db.py --csv dresses.csv --db dresses.db --create-designers-table
```

- Load designer metadata from a separate CSV file:

```bash
python load_dresses_db.py --csv dresses.csv --db dresses.db --designers-csv designers.csv
```

Designer CSV columns should include `brand` and can also include:

- `founded_year`
- `creative_director`
- `ceo`
- `city`
- `country`
- `headquarters`
- `website`
- `notes`

The FastAPI app now also exposes designer data at `/api/designers`.
