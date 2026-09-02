def format_rows_to_markdown(columns: list, rows: list) -> str:
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join(["---"] * len(columns)) + " |"

    body_lines = []
    for row in rows:
        formatted_row = []
        for val in row:
            if val is None:
                formatted_row.append("")
            else:
                clean_val = str(val).replace("|", "\\|").replace("\n", " ")
                formatted_row.append(clean_val)
        body_lines.append("| " + " | ".join(formatted_row) + " |")

    body = "\n".join(body_lines)
    return f"{header}\n{separator}\n{body}"
