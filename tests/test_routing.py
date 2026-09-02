from chatbot.graph.routing import apply_guardrails


def test_omdb_dipilih_tapi_sql_belum_jalan_ke_sql_agent():
    # data_route="OMDB_agent", sql_results="" -> cabang 1
    assert apply_guardrails(
        "OMDB_agent",
        sql_results="",
        omdb_results="",
        rag_results="",
        butuh_rag=False,
        sql_missing="Director",
    ) == "SQL_agent"


def test_sql_kosong_no_results_ke_agregasi():
    # data_route="SQL_agent", sql_results="No results returned." -> cabang 2.a
    assert apply_guardrails(
        "SQL_agent",
        sql_results="No results returned.",
        omdb_results="",
        rag_results="",
        butuh_rag=False,
        sql_missing="",
    ) == "Agregasi_agent"


def test_sql_kosong_emply_result_ke_agregasi():
    # data_route="SQL_agent", sql_results mengandung "EMPTY_RESULT" -> cabang 2.a
    assert apply_guardrails(
        "SQL_agent",
        sql_results="EMPTY_RESULT",
        omdb_results="",
        rag_results="",
        butuh_rag=False,
        sql_missing="",
    ) == "Agregasi_agent"


def test_sql_selesai_butuh_rag_ke_rag_agent():
    # data_route="SQL_agent", sql_results ada data, butuh_rag=True, rag_results="" -> cabang 2.b.i
    assert apply_guardrails(
        "SQL_agent",
        sql_results="ada data",
        omdb_results="",
        rag_results="",
        butuh_rag=True,
        sql_missing="Director",
    ) == "RAG_agent"


def test_sql_selesai_ada_data_null_ke_omdb_agent():
    # data_route="SQL_agent", sql_results ada data, omdb_results="", sql_missing="Director" -> cabang 2.b.ii
    assert apply_guardrails(
        "SQL_agent",
        sql_results="ada data",
        omdb_results="",
        rag_results="ada rag",
        butuh_rag=False,
        sql_missing="Director",
    ) == "OMDB_agent"


def test_sql_selesai_data_lengkap_ke_agregasi():
    # data_route="SQL_agent", sql_results ada data, else -> cabang 2.b.iii
    assert apply_guardrails(
        "SQL_agent",
        sql_results="ada data",
        omdb_results="ada omdb",
        rag_results="ada rag",
        butuh_rag=False,
        sql_missing="Director",
    ) == "Agregasi_agent"


def test_omdb_dipilih_tapi_data_lengkap_ke_agregasi():
    # data_route="OMDB_agent", sql_results ada data, sql_missing="" -> cabang 3
    assert apply_guardrails(
        "OMDB_agent",
        sql_results="ada data",
        omdb_results="",
        rag_results="",
        butuh_rag=False,
        sql_missing="",
    ) == "Agregasi_agent"


def test_butuh_rag_menang_sebelum_cabang_omdb():
    # data_route="OMDB_agent", butuh_rag=True, rag_results="", sql_results ada data, sql_missing="Director" -> cabang 4
    assert apply_guardrails(
        "OMDB_agent",
        sql_results="ada data",
        omdb_results="",
        rag_results="",
        butuh_rag=True,
        sql_missing="Director",
    ) == "RAG_agent"


def test_omdb_sudah_dicoba_ke_agregasi():
    # data_route="SQL_agent", omdb_results ada -> cabang 5
    assert apply_guardrails(
        "SQL_agent",
        sql_results="",
        omdb_results="ada omdb",
        rag_results="",
        butuh_rag=False,
        sql_missing="",
    ) == "Agregasi_agent"


def test_rag_sudah_dicoba_ke_agregasi():
    # data_route="RAG_agent", rag_results ada -> cabang 6
    assert apply_guardrails(
        "RAG_agent",
        sql_results="",
        omdb_results="",
        rag_results="ada rag",
        butuh_rag=False,
        sql_missing="",
    ) == "Agregasi_agent"


def test_tidak_ada_cabang_terpancing_route_bertahan():
    # data_route di luar daftar guardrail -> return data_route apa adanya
    assert apply_guardrails(
        "basic_agent",
        sql_results="",
        omdb_results="",
        rag_results="",
        butuh_rag=False,
        sql_missing="",
    ) == "basic_agent"
