from chatbot.tools.markdown import format_rows_to_markdown


def test_format_columns_dan_beberapa_rows():
    columns = ["judul", "director"]
    rows = [
        ["Inception", "Christopher Nolan"],
        ["Memento", "Christopher Nolan"],
    ]
    expected = (
        "| judul | director |\n"
        "| --- | --- |\n"
        "| Inception | Christopher Nolan |\n"
        "| Memento | Christopher Nolan |"
    )
    assert format_rows_to_markdown(columns, rows) == expected


def test_nilai_none_jadi_sel_kosong():
    columns = ["judul", "director"]
    rows = [["Inception", None]]
    expected = (
        "| judul | director |\n"
        "| --- | --- |\n"
        "| Inception |  |"
    )
    assert format_rows_to_markdown(columns, rows) == expected


def test_pipe_di_escape_dan_newline_diganti_spasi():
    columns = ["judul", "sinopsis"]
    rows = [["Film | Keren", "baris 1\nbaris 2"]]
    expected = (
        "| judul | sinopsis |\n"
        "| --- | --- |\n"
        "| Film \\| Keren | baris 1 baris 2 |"
    )
    assert format_rows_to_markdown(columns, rows) == expected


def test_satu_baris_data():
    columns = ["judul"]
    rows = [["Inception"]]
    expected = (
        "| judul |\n"
        "| --- |\n"
        "| Inception |"
    )
    assert format_rows_to_markdown(columns, rows) == expected
