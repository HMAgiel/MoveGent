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

## Phase 3 — agent.py boilerplate

_Belum dimulai. Section ini diisi setelah merge._

## Phase 4 — chatbot_result.py + tools/tool.py

_Belum dimulai. Section ini diisi setelah merge._

## Phase 5 — ETL fix

_Belum dimulai. Section ini diisi setelah merge._

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
