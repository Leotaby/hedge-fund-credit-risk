#!/usr/bin/env python3
"""
create_database.py

This script constructs a simple SQLite database to support a demonstration
of counterparty credit‐risk analysis for hedge funds and asset managers.
It reads several CSV files containing factor returns and equity price
histories, then populates the appropriate tables.  It also seeds the
database with a small number of hypothetical hedge funds and their
positions in the underlying assets.  Running this script is idempotent –
if the database already exists it will be overwritten.
"""

import sqlite3
import pandas as pd
from pathlib import Path

def load_factors(csv_path: Path) -> pd.DataFrame:
    """Read the Fama‐French five factor data.

    The raw file contains daily data starting in 1963.  We strip any
    whitespace from the headers and ensure the Date column is treated as
    a string so it can serve as a primary key in SQLite.  Missing
    entries (represented by blank cells) will be interpreted as NaN.

    Parameters
    ----------
    csv_path : Path
        Path to the factor CSV file.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: date, mkt_rf, smb, hml, rmw, cma, rf.
    """
    df = pd.read_csv(csv_path, skipinitialspace=True)
    # Rename columns to lower case and remove spaces around names
    df.columns = [c.strip().lower() for c in df.columns]
    # Factor file uses 'date' for the first column already
    df.rename(columns={'mkt-rf': 'mkt_rf'}, inplace=True)
    # Ensure date is a string for SQLite insertion
    df['date'] = df['date'].astype(str)
    return df[['date', 'mkt_rf', 'smb', 'hml', 'rmw', 'cma', 'rf']]


def load_prices(csv_path: Path, asset_name: str) -> pd.DataFrame:
    """Read equity price history from CSV and attach asset name.

    Parameters
    ----------
    csv_path : Path
        Path to the CSV file containing OHLCV data for a single asset.
    asset_name : str
        Ticker or name of the asset.  This will be stored in the
        resulting table.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: date, asset, open, high, low, close,
        adj_close, volume.  Dates are strings.
    """
    df = pd.read_csv(csv_path)
    # Some files have extra blank lines; drop rows where date is NaN
    df = df.dropna(subset=['Date'])
    df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
    df['date'] = df['date'].astype(str)
    df['asset'] = asset_name
    # Ensure numeric columns are floats
    numeric_cols = ['open', 'high', 'low', 'close', 'adj_close', 'volume']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df[['date', 'asset', 'open', 'high', 'low', 'close', 'adj_close', 'volume']]


def main():
    project_dir = Path(__file__).resolve().parent.parent
    data_dir = project_dir / 'data'
    db_path = project_dir / 'risk_management.db'
    # Remove existing database to start fresh
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Create tables
    cur.execute("""
        CREATE TABLE factor_returns (
            date TEXT PRIMARY KEY,
            mkt_rf REAL,
            smb REAL,
            hml REAL,
            rmw REAL,
            cma REAL,
            rf REAL
        )
    """)

    cur.execute("""
        CREATE TABLE asset_prices (
            date TEXT,
            asset TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            adj_close REAL,
            volume REAL,
            PRIMARY KEY (date, asset)
        )
    """)

    cur.execute("""
        CREATE TABLE funds (
            fund_id INTEGER PRIMARY KEY,
            fund_name TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE positions (
            fund_id INTEGER,
            asset TEXT,
            quantity REAL,
            FOREIGN KEY(fund_id) REFERENCES funds(fund_id)
        )
    """)

    # Load and insert factor data
    factor_csv = data_dir / 'fama_french_5factors.csv'
    factors_df = load_factors(factor_csv)
    factors_df.to_sql('factor_returns', conn, if_exists='append', index=False)

    # Load and insert price data for each asset
    assets = {
        'AAPL': 'aapl.csv',
        'AMZN': 'amzn.csv',
        'SPX': 'spx.csv',
    }
    for asset, filename in assets.items():
        df = load_prices(data_dir / filename, asset)
        df.to_sql('asset_prices', conn, if_exists='append', index=False)

    # Seed funds and positions
    funds = [
        (1, 'Equity Hedge Fund'),
        (2, 'Long/Short Fund'),
        (3, 'Tech Focused Fund'),
    ]
    cur.executemany('INSERT INTO funds (fund_id, fund_name) VALUES (?, ?)', funds)

    positions = [
        # fund 1 positions
        (1, 'AAPL', 300),
        (1, 'AMZN', 100),
        (1, 'SPX', 250),
        # fund 2 positions
        (2, 'AAPL', 150),
        (2, 'AMZN', 200),
        (2, 'SPX', 300),
        # fund 3 positions
        (3, 'AAPL', 500),
        (3, 'AMZN', 0),
        (3, 'SPX', 100),
    ]
    cur.executemany('INSERT INTO positions (fund_id, asset, quantity) VALUES (?, ?, ?)', positions)

    conn.commit()
    conn.close()
    print(f"Database created at {db_path}")


if __name__ == '__main__':
    main()