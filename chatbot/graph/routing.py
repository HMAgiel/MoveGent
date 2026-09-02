def apply_guardrails(
    data_route: str,
    sql_results: str,
    omdb_results: str,
    rag_results: str,
    butuh_rag: bool,
    sql_missing: str,
) -> str:
    if data_route == "OMDB_agent" and sql_results == "":
        print("🚨 [Guardrail] OMDB dipilih tapi SQL belum jalan. Memaksa ke SQL_agent dulu.")
        data_route = "SQL_agent"

    elif sql_results != "" and data_route == "SQL_agent":
        if "No results returned." in sql_results or "EMPTY_RESULT" in sql_results: 
            print("🚨 [Guardrail] Data kosong di SQL. Memaksa pindah ke Agregasi_agent.")
            data_route = "Agregasi_agent"
        else:
            if butuh_rag == True and rag_results == "":
                print("🚨 [Guardrail] SQL selesai. Memaksa lanjut ke RAG_agent untuk overview.")
                data_route = "RAG_agent"
            elif omdb_results == "" and sql_missing != "":
                print(f"🚨 [Guardrail] SQL selesai tapi ada data NULL ({sql_missing}). Lanjut ke OMDB_agent.")
                data_route = "OMDB_agent"
            else:
                print("🚨 [Guardrail] SQL selesai dan data lengkap. Memaksa pindah ke Agregasi_agent.")
                data_route = "Agregasi_agent"

    elif data_route == "OMDB_agent" and sql_missing == "":
        print("🚨 [Guardrail] OMDB dipilih tapi data SQL lengkap. Memaksa pindah ke Agregasi_agent.")
        data_route = "Agregasi_agent"

    elif butuh_rag == True and rag_results == "" and data_route in ["Agregasi_agent", "OMDB_agent"]:
        print("🚨 [Guardrail] Tunggu! User butuh overview, RAG belum jalan. Memaksa pindah ke RAG_agent.")
        data_route = "RAG_agent"

    elif omdb_results != "" and data_route in ["OMDB_agent", "SQL_agent"]:
        print("🚨 [Guardrail] OMDB sudah dicoba. Memaksa pindah ke Agregasi_agent.")
        data_route = "Agregasi_agent"
        
    elif rag_results != "" and data_route in ["RAG_agent", "SQL_agent", "OMDB_agent"]:
        print("🚨 [Guardrail] RAG sudah dicoba. Memaksa pindah ke Agregasi_agent.")
        data_route = "Agregasi_agent"

    return data_route
