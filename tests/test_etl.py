import pandas as pd

from chatbot.utils.data_cleaning import (
    build_movies_documents,
    dataframe_for_sql,
    prepare_movies_dataframe,
)


def tulis_csv_fixture(path, baris):
    """Tulis CSV kecil berisi header + baris untuk dipakai prepare_movies_dataframe."""
    header = "Series_Title,Released_Year,Gross,Overview"
    with open(path, "w") as f:
        f.write(header + "\n")
        for b in baris:
            f.write(b + "\n")


def test_prepare_movies_dataframe_ubah_pg_menjadi_nan(tmp_path):
    # Released_Year="PG" harus jadi NaN setelah pembersihan
    path = tmp_path / "film.csv"
    tulis_csv_fixture(path, ["The Godfather,PG,\"100,000,000\",Mafia"])

    df = prepare_movies_dataframe(path)

    assert pd.isna(df["Released_Year"].iloc[0])


def test_prepare_movies_dataframe_tahun_normal_bertahan(tmp_path):
    # Released_Year numerik biasa tidak berubah (tetap 1994.0)
    path = tmp_path / "film.csv"
    tulis_csv_fixture(path, ["Shawshank,1994,\"28,341,469\",Penjara"])

    df = prepare_movies_dataframe(path)

    assert df["Released_Year"].iloc[0] == 1994.0


def test_prepare_movies_dataframe_gross_hilangkan_koma(tmp_path):
    # Gross "100,000,000" -> 100000000.0 (koma dibuang, jadi numerik)
    path = tmp_path / "film.csv"
    tulis_csv_fixture(path, ["The Godfather,1972,\"100,000,000\",Mafia"])

    df = prepare_movies_dataframe(path)

    assert df["Gross"].iloc[0] == 100000000.0


def test_prepare_movies_dataframe_buat_film_id_unik(tmp_path):
    # film_id harus ada, sejumlah baris, semua string, dan unik
    path = tmp_path / "film.csv"
    tulis_csv_fixture(
        path,
        ["Shawshank,1994,\"28,341,469\",Penjara",
         "The Godfather,1972,\"100,000,000\",Mafia"],
    )

    df = prepare_movies_dataframe(path)

    assert "film_id" in df.columns
    assert len(df["film_id"]) == 2
    assert all(isinstance(f, str) for f in df["film_id"])
    assert df["film_id"].is_unique


def test_dataframe_for_sql_buang_kolom_overview():
    # dataframe_for_sql membuang Overview, kolom lain tetap dipertahankan
    df = pd.DataFrame(
        {"Series_Title": ["Shawshank"], "Overview": ["Penjara"], "Gross": [28341469.0]}
    )

    hasil = dataframe_for_sql(df)

    assert "Overview" not in hasil.columns
    assert "Series_Title" in hasil.columns
    assert "Gross" in hasil.columns
    assert len(hasil) == 1


def test_build_movies_documents_jumlah_dan_konten(tmp_path):
    # Jumlah Document = jumlah baris; page_content dan metadata harus benar
    df = pd.DataFrame(
        {
            "Series_Title": ["Shawshank", "The Godfather"],
            "Overview": ["Penjara", "Mafia"],
            "film_id": ["uuid-1", "uuid-2"],
        }
    )

    documents = build_movies_documents(df)

    assert len(documents) == 2
    assert documents[0].page_content == "Series_Title: Shawshank, Overview: Penjara"
    assert documents[1].page_content == "Series_Title: The Godfather, Overview: Mafia"
    assert documents[0].metadata["film_id"] == "uuid-1"
    assert documents[0].metadata["Series_Title"] == "Shawshank"
    assert documents[1].metadata["film_id"] == "uuid-2"
    assert documents[1].metadata["Series_Title"] == "The Godfather"
