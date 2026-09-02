def detect_missing_sql(result: str) -> str:
    """Deteksi kolom dengan nilai kosong/NULL/NaN pada hasil tabel markdown sql_tool."""
    if not result or "No results returned." in result:
        return ""
    lines = [line for line in result.splitlines() if line.startswith("|")]
    if len(lines) < 2:
        return ""
    headers = [h.strip() for h in lines[0].strip("|").split("|")]
    missing = set()
    for line in lines[2:]:
        cells = [c.strip() for c in line.strip("|").split("|")]
        for header, value in zip(headers, cells):
            if value in ("", "None", "NULL", "NaN", "nan"):
                missing.add(header)
    return ", ".join(sorted(missing)) if missing else ""
