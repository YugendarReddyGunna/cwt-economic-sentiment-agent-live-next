import sqlite3
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "macro_economics.db"


def import_csv(connection, csv_path, table_name):
    """Import a CSV file into SQLite when the file exists."""

    if not csv_path.exists():
        print(f"Skipping missing file: {csv_path}")
        return

    df = pd.read_csv(csv_path)

    if df.empty:
        print(f"Skipping empty file: {csv_path}")
        return

    df.to_sql(
        table_name,
        connection,
        if_exists="replace",
        index=False,
    )

    print(f"Imported {len(df)} rows into {table_name}")


def create_joined_dataset(connection):
    """Join daily news and macro features by date."""

    query = """
        SELECT
            f.date AS date,
            f.news_count,
            f.sentiment_mean,
            f.event_count,
            f.event_surprise_mean,
            m.news_article_count,
            m.average_news_sentiment
        FROM daily_features AS f
        LEFT JOIN daily_macro_features AS m
            ON date(f.date) = date(m.date)

        UNION ALL

        SELECT
            m.date AS date,
            NULL AS news_count,
            NULL AS sentiment_mean,
            NULL AS event_count,
            NULL AS event_surprise_mean,
            m.news_article_count,
            m.average_news_sentiment
        FROM daily_macro_features AS m
        WHERE NOT EXISTS (
            SELECT 1
            FROM daily_features AS f
            WHERE date(f.date) = date(m.date)
        )

        ORDER BY date
    """

    df = pd.read_sql_query(query, connection)

    df.to_sql(
        "joined_macro_dataset",
        connection,
        if_exists="replace",
        index=False,
    )

    print(
        f"Created joined_macro_dataset "
        f"with {len(df)} rows"
    )


def verify_database(connection):
    """Display database tables and their row counts."""

    cursor = connection.cursor()

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name
    """)

    tables = cursor.fetchall()

    print("\n===== DATABASE VERIFICATION =====")

    for (table_name,) in tables:
        cursor.execute(
            f'SELECT COUNT(*) FROM "{table_name}"'
        )
        row_count = cursor.fetchone()[0]

        print(f"{table_name}: {row_count} rows")


def main():
    """Import source datasets and create the joined dataset."""

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # CSV sources imported into SQLite.
    sources = {
        "economic_calendar": (
            DATA_DIR / "raw" / "economic_calendar.csv"
        ),
        "apify_economic_calendar": (
            DATA_DIR / "raw" / "apify_economic_calendar.csv"
        ),
        "economic_news": (
            DATA_DIR / "raw" / "tavily_economic_news.csv"
        ),
        "market_prices": (
            DATA_DIR / "raw" / "market_prices.csv"
        ),
        "daily_features": (
            DATA_DIR / "processed" / "daily_features.csv"
        ),
        "daily_macro_features": (
            DATA_DIR / "processed" / "daily_macro_features.csv"
        ),
        "aligned_model_dataset": (
            DATA_DIR / "processed" / "aligned_model_dataset.csv"
        ),
    }

    with sqlite3.connect(DB_PATH) as connection:

        # Step 1: Import all available CSV datasets.
        for table_name, csv_path in sources.items():
            import_csv(
                connection,
                csv_path,
                table_name,
            )

        # Step 2: Create the combined macro dataset.
        create_joined_dataset(connection)

        # Step 3: Verify all tables.
        verify_database(connection)

    print(f"\nSQLite database saved to:\n{DB_PATH}")


if __name__ == "__main__":
    main()