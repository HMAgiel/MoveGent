# Todo: OMDB Fallback — Call OMDB Only When SQL Data Is Missing

Branch: `fix/omdb-invalid-url`

## Phase 1: State foundation

- [ ] Task 1: Add `SQL_missing` to state + initializers
      - `chatbot/graph/state.py`: add `SQL_missing: str` to `AgentState`
      - `chatbot/chatbot_result.py`: add `"SQL_missing": ""` to invoke input
      - `chatbot/graph/agent.py` `supervisor_agent` return: add `"SQL_missing": ""`
      Acceptance: state schema imports; app still boots unchanged (no behavior change yet)
      Verification: `python -m py_compile` on the 3 files; app loads in Streamlit
      Deps: None
      Scope: S (3 files, trivial)

### Checkpoint: Phase 1
- [ ] `python -m py_compile chatbot/graph/state.py chatbot/chatbot_result.py chatbot/graph/agent.py` passes
- [ ] App loads in Streamlit unchanged
- [ ] Human reviews before proceeding

## Phase 2: Real SQL execution + missing detection (core)

- [ ] Task 2: `SQL_agent` executes SQL via `sql_tool`
      - Replace `RAG_tool.invoke({"query": responses.content})` with `sql_tool.invoke({"query": responses.content})`
      - N/A fallback becomes `"Tidak pake SQL"`
      - Add helper `detect_missing_sql(result)` → comma-joined missing column names or `""`
      - Return `{"SQL_result": result, "SQL_missing": sql_missing}`
      Acceptance: `SQL_result` contains real DB rows (markdown table); `SQL_missing` lists columns with empty/NULL cells
      Verification: stub test calling `sql_tool` against the SQLite db; `python -m py_compile`
      Deps: Task 1
      Scope: M (1 file + helper)

- [ ] Task 3: `Data_agent` guardrails — OMDB only on missing data
      - Reordered deterministic block:
        1. `OMDB_agent` chosen but SQL not run yet → force `SQL_agent`
        2. SQL done, `SQL_agent` re-chosen: empty result → `Agregasi`; RAG pending → `RAG`; OMDB only if `omdb_results == ""` AND `SQL_missing != ""`; else `Agregasi`
        3. `OMDB_agent` chosen but `SQL_missing == ""` → force `Agregasi`
        4–6. existing RAG/OMDB anti-loop rules unchanged
      Acceptance: complete-data query ("sci-fi movie with highest rating") never calls OMDB; a film with NULL `Gross`/`Certificate` does
      Verification: full `streamlit run main.py` chat test against both query types
      Deps: Task 2
      Scope: M (1 file)

### Checkpoint: Phase 2
- [ ] `python -m py_compile chatbot/graph/agent.py` passes
- [ ] Chat test: complete-data query → SQL(+RAG) → Agregasi, zero OMDB calls
- [ ] Chat test: missing-field query → SQL → OMDB → Agregasi
- [ ] No infinite loop (guardrail termination intact)
- [ ] Human reviews before proceeding

## Phase 3: Alignment + cleanup

- [ ] Task 4: Prompt alignment + import cleanup
      - `chatbot/prompt/agent_prompt.py` `Data_prompt` rule 2: tighten to "call OMDB only when the specific field (e.g. Released Year) is NULL/missing in SQL"
      - Remove now-unused `db` import from `chatbot/graph/agent.py` (keep `model_llm`)
      Acceptance: no unused imports; prompt wording matches the deterministic gate
      Verification: `python -m py_compile`; grep confirms `sql_tool` invoked and `db` unused in agent.py
      Deps: Task 3
      Scope: S (2 files)

### Checkpoint: Complete
- [ ] All acceptance criteria met
- [ ] Human reviews; commit per phase (stage only intended files — never `git add -A`)
