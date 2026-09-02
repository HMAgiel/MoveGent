# Implementation Plan: OMDB Fallback — Call OMDB Only When SQL Data Is Missing

## Overview

Fix the data pipeline so OMDb is only queried as a fallback when the SQL result actually contains NULL/missing fields (e.g. `Released_Year`, `Certificate`, `Gross`). Requires repairing `SQL_agent` (it currently generates SQL but never executes it — it calls `RAG_tool` instead), adding a deterministic missing-field detector, and re-gating the `Data_agent` guardrails so OMDB only fires on real data gaps. All work on branch `fix/omdb-invalid-url` (already created).

## Architecture Decisions

- **Deterministic gating, not LLM trust**: OMDB routing is decided by a completeness check on real SQL rows (`SQL_missing`), not by the LLM's route choice. The existing anti-loop guardrail philosophy in `agent.py` (the only termination guarantee) is preserved.
- **Missing-field detector**: parse the markdown table produced by `sql_tool` (NULL renders as empty cell). Any empty/`None`/`NaN` cell → record the column name(s) in `SQL_missing`.
- **SQL always runs before OMDB**: `OMDB_agent` is unreachable until SQL has executed, per `Data_prompt` rule.
- **"No results returned."** from `sql_tool` → straight to `Agregasi` (no title exists to look up in OMDb); no OMDB call.
- New state field `SQL_missing: str` threaded through `AgentState`, `supervisor_agent`, and the `run_chatbot` invoke input.
- Comments/log copy stay Indonesian per `AGENTS.md`.

## Task List

### Phase 1: State foundation
- [ ] Task 1: Add `SQL_missing` to state + initializers
      Acceptance: state schema imports; app still boots unchanged (no behavior change yet)
      Deps: None

### Checkpoint: Phase 1
- [ ] `python -m py_compile` passes on the 3 touched files
- [ ] App loads in Streamlit unchanged

### Phase 2: Real SQL execution + missing detection (core)
- [ ] Task 2: `SQL_agent` executes SQL via `sql_tool`
      Acceptance: `SQL_result` contains real DB rows (markdown table); `SQL_missing` lists columns with empty/NULL cells
      Deps: Task 1
- [ ] Task 3: `Data_agent` guardrails — OMDB only on missing data
      Acceptance: complete-data query never calls OMDB; a film with NULL `Gross`/`Certificate` does
      Deps: Task 2

### Checkpoint: Phase 2
- [ ] `python -m py_compile` passes
- [ ] Chat test: "sci-fi movie with highest rating" → SQL(+RAG) → Agregasi, zero OMDB calls
- [ ] Chat test: missing-field query → SQL → OMDB → Agregasi
- [ ] No infinite loop (guardrail termination intact)

### Phase 3: Alignment + cleanup
- [ ] Task 4: Prompt alignment + import cleanup
      Acceptance: no unused imports; prompt wording matches the deterministic gate
      Deps: Task 3

### Checkpoint: Complete
- [ ] All acceptance criteria met
- [ ] Human review, then commit per phase (stage only intended files — working tree has unrelated changes)

## Verification

No test suite, linter, or typecheck in this repo (`AGENTS.md`). Per task:
1. `python -m py_compile <touched files>`
2. Stub-based tool checks (guardrail/detector logic without the full stack)
3. Full chat verification needs the stack (env, SQLite, Qdrant): kill the running Streamlit (PID 17468) first — it holds the Qdrant lock

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Working tree has unrelated uncommitted changes (`.gitignore`, `agent.py`/`agent_prompt.py`/`tool.py` diffs, untracked `.claude/`, `skills-lock.json`) | Med | Stage only files belonging to each task; never `git add -A` |
| SQL generation is LLM-driven — malformed SQL possible | Med | `sql_tool` error propagates as result text; guardrail still terminates; prompt enforces SELECT-only |
| Streamlit instance (PID 17468) holds Qdrant lock | Low | Kill before verification runs |
| `SQL_missing` empty when SQL never ran | Low | Guardrail rule 1 forces SQL before OMDB, so gating stays sound |
| Old `EMPTY_RESULT` string no longer produced | Low | Keep check for backward compat; "No results returned." also handled |

## Open Questions

- None — both design decisions (real SQL execution; any-NULL triggers OMDB) confirmed with human.
