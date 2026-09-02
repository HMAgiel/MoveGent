from sqlalchemy import Column, Float, Integer, MetaData, String, Table, create_engine, text
from uuid import uuid4

from chatbot.config import DATABASE_PATH
from chatbot.utils.Vectore_database import make_vectore
from chatbot.utils.data_cleaning import dataframe_for_sql, prepare_movies_dataframe

RAW_CSV_PATH = "chatbot/data/raw/imdb_top_1000.csv"


def build_movies_table(metadata_obj):
    """Definisikan tabel FILM_TABEL sesuai skema asli."""
    return Table(
        "FILM_TABEL",
        metadata_obj,
        Column("film_id", String, primary_key=True, default=lambda: str(uuid4())),
        Column("Series_Title", String, nullable=False),
        Column("Released_Year", Float),
        Column("Certificate", String),
        Column("Runtime", String),
        Column("Genre", String),
        Column("IMDB_Rating", Float),
        Column("Meta_score", Float),
        Column("Director", String),
        Column("Star1", String),
        Column("Star2", String),
        Column("Star3", String),
        Column("Star4", String),
        Column("No_of_Votes", Integer),
        Column("Gross", Float),
        Column("Poster_Link", String),
        extend_existing=True,
    )


def create_sqlite_database(csv_path: str = RAW_CSV_PATH):
    """Bangun database SQLite FILM_TABEL dari CSV film (drop table lama dulu)."""
    df = prepare_movies_dataframe(csv_path)
    df_clean = dataframe_for_sql(df)
    engine = create_engine(f"sqlite:///{DATABASE_PATH}")

    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS FILM_TABEL"))

    metadata_obj = MetaData()
    build_movies_table(metadata_obj)

    df_clean.to_sql(
        name="FILM_TABEL",
        con=engine,
        if_exists="append",
        index=False,
    )

    return engine


def main():
    """ETL penuh: CSV -> SQLite (FILM_TABEL) + Qdrant (Data_IMDB)."""
    create_sqlite_database()
    make_vectore(RAW_CSV_PATH)
    print("Create sql sucesses ✅")


if __name__ == "__main__":
    main()
