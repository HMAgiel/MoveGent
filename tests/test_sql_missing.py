from chatbot.utils.sql_missing import detect_missing_sql


def test_empty_string():
    assert detect_missing_sql("") == ""


def test_no_results_returned():
    assert detect_missing_sql("No results returned.") == ""


def test_markdown_tanpa_baris_data():
    # hanya header + separator, tidak ada baris data
    result = "| judul | director |\n| --- | --- |"
    assert detect_missing_sql(result) == ""


def test_markdown_tanpa_baris_meja():
    # teks biasa tanpa baris tabel
    assert detect_missing_sql("Tidak pake SQL") == ""


def test_sel_kosong_dideteksi():
    result = (
        "| judul | director |\n"
        "| --- | --- |\n"
        "| A |  |\n"
        "| B | Nolan |"
    )
    assert detect_missing_sql(result) == "director"


def test_sel_none_null_nan_dideteksi_sorted():
    result = (
        "| judul | director | tahun |\n"
        "| --- | --- | --- |\n"
        "| A |  | 2000 |\n"
        "| B | None | NULL |\n"
        "| C | NaN | 2002 |\n"
        "| D | nan | 2003 |"
    )
    # missing = director (kosong, None, NaN, nan), tahun (NULL) -> sorted, comma-joined
    assert detect_missing_sql(result) == "director, tahun"


def test_markdown_tanpa_nilai_kosong():
    result = (
        "| judul | director |\n"
        "| --- | --- |\n"
        "| A | Nolan |\n"
        "| B | Nolan |"
    )
    assert detect_missing_sql(result) == ""


def test_sel_tidak_kosong_tidak_ikut():
    result = (
        "| judul | director |\n"
        "| --- | --- |\n"
        "| A | Nolan |\n"
        "| B | Nonexistent |"
    )
    assert detect_missing_sql(result) == ""
