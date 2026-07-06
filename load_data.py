"""
Day 1: Load football-data.co.uk Championship CSVs into SQLite.

Usage:
    python load_data.py

Expects CSV files in ./data/ named like E1_2024-25.csv
Creates (or recreates) championship.db in the project folder.
"""

import sqlite3
from pathlib import Path

import pandas as pd

DATA_DIR = Path("data")
DB_PATH = Path("championship.db")

# The raw CSV columns we care about, mapped to our own column names.
# Everything else (referee, betting odds, etc.) gets dropped.
COLUMN_MAP = {
    "Date": "match_date",
    "HomeTeam": "home_team",
    "AwayTeam": "away_team",
    "FTHG": "home_goals",
    "FTAG": "away_goals",
    "FTR": "result",
    "HTHG": "ht_home_goals",
    "HTAG": "ht_away_goals",
    "HS": "home_shots",
    "AS": "away_shots",
    "HST": "home_shots_ot",
    "AST": "away_shots_ot",
    "HC": "home_corners",
    "AC": "away_corners",
    "HY": "home_yellows",
    "AY": "away_yellows",
    "HR": "home_reds",
    "AR": "away_reds",
}

SCHEMA = """
DROP TABLE IF EXISTS matches;
DROP TABLE IF EXISTS teams;
DROP TABLE IF EXISTS seasons;

CREATE TABLE seasons (
    season_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    label       TEXT NOT NULL UNIQUE
);

CREATE TABLE teams (
    team_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    team_name   TEXT NOT NULL UNIQUE
);

CREATE TABLE matches (
    match_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    season_id       INTEGER NOT NULL REFERENCES seasons(season_id),
    match_date      DATE NOT NULL,
    home_team_id    INTEGER NOT NULL REFERENCES teams(team_id),
    away_team_id    INTEGER NOT NULL REFERENCES teams(team_id),
    home_goals      INTEGER,
    away_goals      INTEGER,
    result          TEXT CHECK (result IN ('H', 'D', 'A')),
    ht_home_goals   INTEGER,
    ht_away_goals   INTEGER,
    home_shots      INTEGER,
    away_shots      INTEGER,
    home_shots_ot   INTEGER,
    away_shots_ot   INTEGER,
    home_corners    INTEGER,
    away_corners    INTEGER,
    home_yellows    INTEGER,
    away_yellows    INTEGER,
    home_reds       INTEGER,
    away_reds       INTEGER
);
"""


def read_season_csv(csv_path: Path) -> pd.DataFrame:
    """Read one raw CSV, keep only the columns we need, clean it up."""
    df = pd.read_csv(csv_path)

    # Some files have extra columns or missing ones — only keep what exists
    cols_present = [c for c in COLUMN_MAP if c in df.columns]
    df = df[cols_present].rename(columns=COLUMN_MAP)

    # Dates on football-data.co.uk are UK format (dd/mm/yyyy)
    df["match_date"] = pd.to_datetime(
        df["match_date"], dayfirst=True
    ).dt.strftime("%Y-%m-%d")

    # Drop rows with no result (abandoned/blank trailing rows)
    df = df.dropna(subset=["home_team", "away_team", "result"])

    # Season label comes from the filename: E1_2024-25.csv -> 2024-25
    df["season_label"] = csv_path.stem.split("_")[1]

    return df


def get_or_create_id(cur, table, id_col, name_col, value):
    """Return the id for a value, inserting it first if it's new."""
    cur.execute(f"SELECT {id_col} FROM {table} WHERE {name_col} = ?", (value,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(f"INSERT INTO {table} ({name_col}) VALUES (?)", (value,))
    return cur.lastrowid


def main():
    csv_files = sorted(DATA_DIR.glob("E1_*.csv"))
    if not csv_files:
        raise SystemExit(f"No E1_*.csv files found in {DATA_DIR.resolve()}")

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.executescript(SCHEMA)

    total = 0
    for csv_path in csv_files:
        df = read_season_csv(csv_path)
        season_label = df["season_label"].iloc[0]
        season_id = get_or_create_id(
            cur, "seasons", "season_id", "label", season_label
        )

        for row in df.itertuples(index=False):
            home_id = get_or_create_id(
                cur, "teams", "team_id", "team_name", row.home_team
            )
            away_id = get_or_create_id(
                cur, "teams", "team_id", "team_name", row.away_team
            )
            cur.execute(
                """
                INSERT INTO matches (
                    season_id, match_date, home_team_id, away_team_id,
                    home_goals, away_goals, result,
                    ht_home_goals, ht_away_goals,
                    home_shots, away_shots, home_shots_ot, away_shots_ot,
                    home_corners, away_corners,
                    home_yellows, away_yellows, home_reds, away_reds
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    season_id, row.match_date, home_id, away_id,
                    row.home_goals, row.away_goals, row.result,
                    row.ht_home_goals, row.ht_away_goals,
                    row.home_shots, row.away_shots,
                    row.home_shots_ot, row.away_shots_ot,
                    row.home_corners, row.away_corners,
                    row.home_yellows, row.away_yellows,
                    row.home_reds, row.away_reds,
                ),
            )
        print(f"{csv_path.name}: loaded {len(df)} matches ({season_label})")
        total += len(df)

    con.commit()

    # Sanity check
    for table in ("seasons", "teams", "matches"):
        count = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"{table}: {count} rows")

    con.close()
    print(f"\nDone. {total} matches loaded into {DB_PATH}")


if __name__ == "__main__":
    main()