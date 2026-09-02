"""Pipeline pembersihan data film — dipakai ETL SQLite & Qdrant (tanpa side effects)."""
import pandas as pd
from uuid import uuid4
from langchain_core.documents import Document


def prepare_movies_dataframe(path) -> pd.DataFrame:
    """Baca CSV film dan bersihkan (Released_Year 'PG'→NaN, Gross numeric, film_id UUID)."""
    df = pd.read_csv(path)
    df = df.replace({"Released_Year": "PG"}, None)
    df["Gross"] = df["Gross"].str.replace(",", "", regex=True)
    df[["Released_Year", "Gross"]] = df[["Released_Year", "Gross"]].apply(pd.to_numeric)
    df["film_id"] = [str(uuid4()) for _ in range(len(df["Series_Title"]))]
    return df


def dataframe_for_sql(df: pd.DataFrame) -> pd.DataFrame:
    """Kembalikan dataframe tanpa kolom Overview (Overview hanya untuk Qdrant)."""
    return df.drop(columns="Overview")


def build_movies_documents(df: pd.DataFrame) -> list:
    """Buat daftar Document RAG dari baris film untuk koleksi Qdrant."""
    documents = []
    for i in range(len(df)):
        judul_film = df["Series_Title"][i]
        overview_film = df["Overview"][i]
        input_rag = f"Series_Title: {judul_film}, Overview: {overview_film}"
        doc = Document(
            page_content=input_rag,
            metadata={"film_id": df["film_id"][i], "Series_Title": judul_film},
        )
        documents.append(doc)
    return documents
