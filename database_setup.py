"""
database_setup.py
-----------------
Loads the four CSV files from ./data into a SQLite database (food.db),
creating properly typed tables with primary/foreign keys.

Run this once after you have the CSVs (real or sample):
    python database_setup.py

It is safe to re-run; it rebuilds the tables from the CSVs each time.
"""

import os
import sqlite3

import pandas as pd

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(BASE_DIR, "food.db")

SCHEMA = """
DROP TABLE IF EXISTS claims;
DROP TABLE IF EXISTS food_listings;
DROP TABLE IF EXISTS receivers;
DROP TABLE IF EXISTS providers;

CREATE TABLE providers (
    Provider_ID INTEGER PRIMARY KEY,
    Name        TEXT,
    Type        TEXT,
    Address     TEXT,
    City        TEXT,
    Contact     TEXT
);

CREATE TABLE receivers (
    Receiver_ID INTEGER PRIMARY KEY,
    Name        TEXT,
    Type        TEXT,
    City        TEXT,
    Contact     TEXT
);

CREATE TABLE food_listings (
    Food_ID       INTEGER PRIMARY KEY,
    Food_Name     TEXT,
    Quantity      INTEGER,
    Expiry_Date   TEXT,
    Provider_ID   INTEGER,
    Provider_Type TEXT,
    Location      TEXT,
    Food_Type     TEXT,
    Meal_Type     TEXT,
    FOREIGN KEY (Provider_ID) REFERENCES providers(Provider_ID)
);

CREATE TABLE claims (
    Claim_ID    INTEGER PRIMARY KEY,
    Food_ID     INTEGER,
    Receiver_ID INTEGER,
    Status      TEXT,
    Timestamp   TEXT,
    FOREIGN KEY (Food_ID)     REFERENCES food_listings(Food_ID),
    FOREIGN KEY (Receiver_ID) REFERENCES receivers(Receiver_ID)
);
"""

CSV_TO_TABLE = {
    "providers_data.csv": "providers",
    "receivers_data.csv": "receivers",
    "food_listings_data.csv": "food_listings",
    "claims_data.csv": "claims",
}

# Date columns to normalise to ISO so SQLite DATE()/DATETIME() work regardless
# of the source format (the real data uses M/D/YYYY and M/D/YYYY H:MM).
DATE_COLUMNS = {
    "food_listings": {"Expiry_Date": "%Y-%m-%d"},
    "claims": {"Timestamp": "%Y-%m-%d %H:%M:%S"},
}


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Light cleaning: strip whitespace, drop fully-empty rows, dedupe."""
    df = df.dropna(how="all").drop_duplicates()
    for col in df.columns:
        if df[col].dtype == object or str(df[col].dtype).startswith("string"):
            df[col] = df[col].astype(str).str.strip()
    return df


def normalise_dates(df: pd.DataFrame, table: str) -> pd.DataFrame:
    """Convert any known date/datetime columns to ISO strings."""
    for col, fmt in DATE_COLUMNS.get(table, {}).items():
        if col in df.columns:
            parsed = pd.to_datetime(df[col], errors="coerce")
            df[col] = parsed.dt.strftime(fmt)
    return df


def build():
    missing = [f for f in CSV_TO_TABLE if not os.path.exists(os.path.join(DATA_DIR, f))]
    if missing:
        raise FileNotFoundError(
            "Missing CSV files in ./data: " + ", ".join(missing) +
            "\nRun generate_sample_data.py first, or add the real CSVs."
        )

    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)

    for csv_name, table in CSV_TO_TABLE.items():
        df = clean(pd.read_csv(os.path.join(DATA_DIR, csv_name)))
        df = normalise_dates(df, table)
        df.to_sql(table, conn, if_exists="append", index=False)
        print(f"Loaded {len(df):>4} rows into '{table}'")

    conn.commit()
    conn.close()
    print(f"\nDatabase ready: {DB_PATH}")


if __name__ == "__main__":
    build()
