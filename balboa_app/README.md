# Balboa mapping agent — PyQt6 rewrite

## Setup

```
pip install -r requirements.txt
python main.py
```

First run creates `config.json`, `data/mappings_database.db`, and `data/backups/`
next to wherever you placed these files. Open **Settings** in the app to point
each fund at its actual cashbook file, and to point the database at your
shared folder if you want it there.

If the database lives on OneDrive/SharePoint, right-click that folder and
choose "Always keep on this device" so it's never a cloud-only placeholder.

## Layout

```
config.py                   absolute path resolution, fund settings
db.py                       the only module that opens a SQLite connection
mapping_engine.py           rapidfuzz matching, fund-scoped corrections
import_export_service.py    bank import, cashbook GL write-back, ETL export, archiving
workers.py                  QThread wrappers so long operations never freeze the UI
ui/                         PyQt6 windows and dialogs — presentation only
main.py                     entry point
```

Each layer only calls the one below it. The UI never touches SQLite or
openpyxl directly.

## What changed from the original script, and why

**Cross-fund correction bleed (fixed).** Corrections were keyed by
description text alone, so a GL correction made on one fund could get
silently applied to an identical-looking transaction on a different fund.
`corrections` is now keyed on `(fund_name, description)`, and the mapping
engine's fuzzy corpus is filtered to the current fund as well. Verified with
a direct test: an identical description on Fund I and Fund III now resolves
to two different GL codes.

**Same-day, same-amount transactions silently dropped (fixed).** The
cashbook-level duplicate check only compared `(date, amount)`, so two
legitimate transactions — a recurring transfer, a duplicate wire fee — could
collide and the second one would vanish with no warning. The dedupe key is
now `(date, amount, description)`. Verified directly: two rows with the same
date and amount but different descriptions are now both kept.

**Auto-archive was described but never wired up (fixed).** The original
import panel computed the cashbook's date range and logged it, but nothing
in the code actually archived a prior month once new data arrived.
`MonthArchiver.archive_completed_months()` now runs automatically after
every bank import: any month strictly before the one just imported, whose
rows are *all* already GL-mapped, gets archived to the database. A month
with any unmapped row is left alone and reported in the log instead of
being partially archived.

**Fuzzy matching swapped from fuzzywuzzy to rapidfuzz.** `fuzzywuzzy`
silently falls back to pure-Python `difflib` unless `python-Levenshtein` is
installed alongside it — and that package is GPLv2, worth avoiding on the
same trip where PyQt6 licensing was already a consideration. `rapidfuzz` is
MIT-licensed, C-accelerated, and `process.extractOne` runs the whole
candidate list in one call instead of a manual Python loop.

**Training data now reads live from the database.** The original tool kept
fuzzy-match training data in memory, populated only when someone manually
picked a "master training Excel file" — a step that had to be repeated
every session, and which silently produced empty results if forgotten.
The mapping engine now queries `transaction_history` directly, so a
correction saved this session, or a month archived a minute ago, is part of
the corpus for the very next match — no reload step, ever.

**Database path is no longer inferred from the working directory (fixed).**
The original used a bare relative filename for the SQLite file, so launching
the packaged app from a different folder silently created a fresh, empty
database. The path now comes from `config.json`, resolved from either the
`BALBOA_HOME` environment variable or the folder containing the running
executable — set once, explicit from then on.

**SQLite is defensive about network/cloud-sync storage.** Every connection
explicitly sets `journal_mode=DELETE` (WAL is documented as unreliable on
network filesystems) and a `busy_timeout`, so a sync client briefly locking
the file causes a short wait instead of an unhandled exception. `Database.backup()`
snapshots the file to `data/backups/` before any archive or import.

**Cashbook writes take a backup first.** Both the raw bank import
(`_append_to_cashbook`) and the GL write-back (`CashbookGLWriter`) copy the
live cashbook to a `.bak` file before writing, so a bad write during a
crash or a file-lock collision has a same-day rollback point.

**No more hardcoded personal paths in source code.** All fund cashbook
paths and the database location are edited from the Settings dialog and
persisted to `config.json` — nothing needs a code change to point at a
different machine or folder.

## Performance, at the volume discussed

Training corpus today: ~2,500 rows. At 30–90 new transactions/month across
the three funds over the next 7 months, the corpus grows to roughly
2,700–3,100 rows. Matching a month's batch against that corpus is on the
order of 80,000–280,000 rapidfuzz comparisons, which runs in well under two
seconds — and it now runs on a background thread (`MappingWorker`) with a
progress bar regardless, so the window stays responsive even as that number
grows over the coming years.
