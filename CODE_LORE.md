# CODE_LORE.md

Catatan keputusan, pelajaran, dan perubahan per fase refactor `chatbot/`.
Di-update setelah setiap phase selesai di-merge ke `refractor`.

## Latar Belakang

Refactor Clean Code pada folder `chatbot/` (982 baris). Keputusan kunci dari klien:

- Nama publik yang sudah ada **dipertahankan** (tidak ada rename) — `Agregasi_agent`,
  `retrive`, `Process_data_tp_sql_and_qdrant.py`, `Vectore_database.py`, `model_llm`, dll.
- Refactor + perbaikan bug (ETL broken, path hardcoded, unused variables).
- `config.py` diubah jadi lazy singleton (import ringan, resource dimuat saat dipakai).
- Test dasar ditambahkan (pytest via `requirements-dev.txt`).
- Komentar/log tetap Bahasa Indonesia.
- Workflow: branch per phase → merge ke `refractor` → update file ini → graphify di akhir.

## Phase 1 — Test foundation + ekstraksi pure functions

**Status:** selesai, merge ke `refractor` (commit `24c0e63`).

**Keputusan:**
- Logika murni diekstrak verbatim dari agent/tool ke module side-effect-free (tanpa import config) supaya bisa di-unit-test tanpa env/network/db:
  - `chatbot/graph/routing.py` — `apply_guardrails()` (rantai 9 cabang if/elif dari `Data_agent`, lengkap dengan print `🚨 [Guardrail]`)
  - `chatbot/utils/sql_missing.py` — `detect_missing_sql()`
  - `chatbot/tools/markdown.py` — `format_rows_to_markdown()`
- `agent.py` & `tool.py` swap ke pemanggilan import (perilaku identik, tidak ada definisi duplikat).
- Test: `tests/test_routing.py` (11 kasus — semua cabang), `test_sql_missing.py` (7), `test_markdown.py` (4) → 23 passed.
- `tests/__init__.py` ditambah karena repo root tidak di sys.path (tanpa ini pytest gagal koleksi).

**Pelajaran / gotcha:**
- Ekstraksi "verbatim" harus benar-benar verbatim: reviewer memverifikasi byte-level (termasuk trailing space dan f-string `({sql_missing})` pada print guardrail).
- Module pure baru TIDAK BOLEH import `chatbot.config` — config punya side effects berat di import.
- Script `task-brief` SDD tidak bisa parse format plan (pakai `### Phase N`), jadi phase brief ditulis manual.

**File yang berubah:**
- `chatbot/graph/routing.py`, `chatbot/utils/sql_missing.py`, `chatbot/tools/markdown.py` (baru, murni)
- `chatbot/graph/agent.py`, `chatbot/tools/tool.py` (swap import)
- `tests/` (3 file test + `__init__.py`)

## Phase 2 — config.py lazy singleton + path fix

**Status:** selesai, merge ke `refractor` (commit `2fd16bd`).

**Keputusan:**
- `config.py` tidak lagi menjalankan side effects berat saat import. Resource dibuat lazy via
  `lru_cache`: `get_db()`, `get_embeddings()`, `get_rerank()`, `get_retrive()`; `model_llm`
  jadi lazy factory (per-temperature, `maxsize=8`).
- Nama publik lama tetap bisa di-import (`embedding`, `rerank`, `retrive`, `db`) via module
  `__getattr__` (PEP 562) — `from chatbot.config import X` memicu konstruksi hanya saat X
  pertama kali diakses.
- Path hardcoded `/home/hasyim/...` diganti konstanta `Path(__file__)` yang resolve ke lokasi
  yang sama (db, qdrant, model). `LLM_MODEL = "gpt-5.6-luna"` konstanta.
- `tool.py` beralih ke getter DI DALAM @tool function → import `tool.py` ringan (get_retrive/
  get_rerank/get_db hanya terpanggil saat tool di-invoke). Alias `retrive_rag`/`rerank_model` hilang.
- Import tak terpakai dibuang: `QdrantClient`, `SQLDatabase`, `import os` duplikat.

**Pelajaran / gotcha:**
- `import chatbot.config` masih ~12s = biaya import library (`sentence_transformers`, dsb.),
  BUKAN side effect config — konstruksi/download/koneksi resource sudah tidak terjadi di import.
- Module `__getattr__` membuat `from chatbot.config import embedding` tetap berfungsi untuk
  `Vectore_database.py` (ETL, belum difix) tanpa eager-load.
- QdrantClient mengeluarkan noise `ImportError: sys.meta_path is None` saat interpreter
  shutdown — harmless, pre-existing.

**File yang berubah:**
- `chatbot/config.py` — lazy rewrite + path relatif
- `chatbot/tools/tool.py` — getter di dalam tool, alias dibuang

## Phase 3 — agent.py: boilerplate via tracing helper

**Status:** selesai, merge ke `refractor` (commit `102bde0`).

**Keputusan:**
- Helper `chatbot/graph/tracing.py` → `llm_call(llm, messages, span_name)`: membungkus
  `llm.invoke` dalam span langfuse (`as_type="span"`) + `CallbackHandler` di config.
  Boilerplate langfuse × 7 agent (mulai ~40 baris/agent) dihilangkan.
- 7 agent function di-slim: hapus `session_id` (unused), docstring literal yang salah posisi
  (dead code) dipindah jadi docstring Bahasa Indonesia, import tak terpakai dibuang
  (`ToolMessage`, `propagate_attributes`, `CallbackHandler`, `get_client`, `load_dotenv`).
- `agent.py` 336 → **199 baris**. Semua temperatur, message, prompt `.format()`, cek `"N/A"`,
  pemanggilan tool, dict return, dan span name (termasuk typo `"RAG_agnet"`) dipertahankan
  VERBATIM. `apply_guardrails` di Data_agent tidak tersentuh.
- Konstanta magic string: `NO_DATA_MARKER = "N/A"`, `NOT_USED_RAG/SQL/OMDB = "Tidak pake ..."`.

**Pelajaran / gotcha:**
- Consequence desain `llm_call`: span langfuse kini hanya membungkus `llm.invoke`, tidak lagi
  membungkus tool call + pembentukan return (sebelumnya seluruh body node di dalam span).
  Observability-only drift — diterima, tercatat sebagai minor.
- `load_dotenv()` aman dihapus dari agent.py karena `config.py` sudah memanggilnya dan agent.py
  import config lebih dulu.
- Agent functions tetap signature `(state, config)` karena LangGraph memanggil node dengan 2 argumen.

**File yang berubah:**
- `chatbot/graph/tracing.py` (baru)
- `chatbot/graph/agent.py` (199 baris, boilerplate dihapus)

## Phase 4 — chatbot_result.py + tools/tool.py cleanup

**Status:** selesai, merge ke `refractor` (commit `2c1cc0f`).

**Keputusan:**
- `chatbot_result.py`: `run_chatbot()` dipecah jadi helpers privat `_split_history`,
  `_build_initial_state`, `_count_tokens`, `_extract_routing`. API & return dict
  `{response, routing, input_tokens, output_tokens}` TIDAK berubah; `main.py` tak tersentuh.
- langfuse client dibuat lazy via `_get_langfuse()` (`lru_cache`). `load_dotenv()` dihapus dari
  chatbot_result (config.py sudah memanggilnya & di-import transitif).
- Alias `langgraph_app = app` dibuang (tidak di-import pihak luar) → pakai `app` langsung.
- `tool.py`: dead code `tool_rag`/`tool_sql`/`tool_omdb` dihapus; annotation `RAG_tool ->
  list[str]`, `OMDB_tool -> dict | str` diperbaiki; indentasi `rerank.rank(...)` dirapikan;
  docstring OMDB_tool kutip berlebih `""""` → `"""` (konten deskripsi LLM TIDAK diubah).
- KUNCI: docstring @tool adalah deskripsi yang dilihat LLM — kontennya tidak boleh diubah,
  hanya perbaikan jumlah kutip.

**Pelajaran / gotcha:**
- Token counting kini dua panggilan `_count_tokens` independen (sebelumnya satu shared
  try/except) — identik untuk input str, divergence tepi dapat diabaikan.
- `import uuid` di chatbot_result unused — pre-existing, bisa dibuang di future cleanup.

**File yang berubah:**
- `chatbot/chatbot_result.py` — helpers + langfuse lazy
- `chatbot/tools/tool.py` — dead code + annotation

## Phase 5 — ETL fix

**Status:** selesai, merge ke `refractor` (commit `4c2cad4`).

**Keputusan:**
- Module baru `chatbot/utils/data_cleaning.py` (MURNI, tanpa import config): `prepare_movies_dataframe`
  (PG→NaN, Gross numeric, film_id UUID), `dataframe_for_sql` (drop Overview), `build_movies_documents`
  (Document RAG). Menghilangkan duplikasi cleaning yang ada di 2 file ETL.
- `Process_data_tp_sql_and_qdrant.py` FIXED: import `embedding_model` (bug, tak pernah ada) →
  `get_embeddings()`; path `sqlite:////chatbot/...` (root filesystem, bug) → `sqlite:///{DATABASE_PATH}`
  (resolve sama dengan config); `main()` + guard `if __name__ == "__main__"` → import AMAN
  (sebelumnya eksekusi module-level). main() = SQLite + `make_vectore` (Qdrant), sesuai nama file.
- `Vectore_database.py`: `return print(...)` → print + `return qdrant`; error tidak ditelan
  (try/except print dihapus); pakai `get_embeddings()` + `str(QDRANT_PATH)`.
- `tests/test_etl.py` (6 test, tmp_path fixture) — hanya data_cleaning, tanpa env/network.
- ETL penuh TIDAK dijalankan (drop DB + OpenAI embeddings 1000 baris = biaya). DB & qdrant intact.

**Pelajaran / gotcha:**
- `uuids = [str(uuid4()) ...]` di make_vectore dead code (tak di-pass ke `from_documents(ids=...)`) —
  pre-existing, dipertahankan (behavior-preserving). Qdrant auto-generate vector ids.
- Print `"sucesses"` typo dipertahankan (behavior drift tidak diizinkan di phase ini).

**File yang berubah:**
- `chatbot/utils/data_cleaning.py` (baru)
- `chatbot/utils/Process_data_tp_sql_and_qdrant.py`, `chatbot/utils/Vectore_database.py`
- `tests/test_etl.py` (baru)

## Phase 6 — Polish + docs + graphify

_Belum dimulai. Section ini diisi setelah merge._

---

## Template section (hapus setelah dipakai)

```markdown
## Phase N — <judul>

**Keputusan:**
- ...

**Pelajaran / gotcha:**
- ...

**File yang berubah:**
- `path/file.py` — apa yang diubah
```
