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

_Belum dimulai. Section ini diisi setelah merge._

## Phase 2 — config.py lazy singleton

_Belum dimulai. Section ini diisi setelah merge._

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
