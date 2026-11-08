# CLAUDE.md — RB-DA allocation kiosk (club allocation)

> Loaded every session; kept short on purpose. Details: `docs/ke_hoach/CLAUDE_CHI_TIET.md`. Read only the doc parts relevant to the current item.
> **Reply to the user (Truong) in Vietnamese.** Keep function and variable names exactly as in the code.

## Project
- Offline Windows kiosk allocating ~800 students to ~20 clubs at a high school; a student's science-research project.
- Algorithm **RB-DA**: student-proposing Deferred Acceptance (Gale–Shapley) + two-pass soft reserves (Kominers & Sönmez 2016) + single tie-breaking (STB) + two-tier priority (Tier 1 tested: −score then STB; Tier 2: STB).
- Stack: Python 3.11 + SQLite (`app.db`); HTML/JS UI in pywebview (WebView2), browser fallback `browser_host.py`. PyInstaller build via GitHub Actions (*Build Windows executable (rbda-kiosk)*; manual: `build_windows.bat`).
- Owner's goal: generalise to 12 other sectors and handle changes over time (late arrivals, withdrawals). Business model later.

## Code map
`docs/ke_hoach/CLAUDE_CHI_TIET.md` § "Bản đồ mã". Locate by FUNCTION NAME, never line numbers (`grep -n "^def <name>" <file>`).

## Commands
- Tests: only related ones, `python -m pytest -q <file or -k ...>` in the project venv (`./.venv/bin/python`; Windows `.venv\Scripts\python`). Full suite ~22 min (with Chromium UI tests): run only if Truong asks; CI runs it. Lint `ruff check .`; CI needs coverage ≥ 85 %.
- After editing `i18n_errors.py`: `python tao_i18n_js.py`.
- Quick-verify reference scripts: `CLAUDE_CHI_TIET.md` § "Kiểm verify nhanh".

## Invariants — NEVER break
1. Default config gives results BYTE-IDENTICAL to before the change (same data, same seed): compare every `match_results` row, 3 datasets × 20 seeds. Every new parameter defaults to the old behaviour.
2. `compute_club_priority` never receives preference rank or a previous session's outcome (anti-endogeneity); new criteria may not read them either.
   **Exception (Truong, 2026-11-08, FA-DAA D2):** DEFAULT medals may be derived from rank order, at the registration layer only, and ONLY if every student can override medal placement (path A swap UI; path B optional Forms question for gold). Reason: CADA-style separate signal (Abdulkadiroğlu, Che & Yasuda 2015) keeps rank reporting truthful given the medals the student keeps. The priority key still reads stored medals, never rank.
3. STB lottery: locked after the first run, a locked seed gives the same numbers, generated with crc32 (never `hash()`), late arrivals inserted uniformly at random while keeping existing students' relative order.
4. `run_history` is never overwritten or deleted; every run appends a row.
5. Pipeline order: backup → validate → lock seed/STB → solve → sanity/verify → write in ONE transaction → export; rollback on error.
6. UI↔backend contract `{ok, data, errors}`, `errors = [{code, params}]`; error messages have one source (`i18n_errors.py` → `tao_i18n_js.py`).
7. CSV column contract (`club_id, student_id, test_club_k, score_k, pref_k, <buoi>_pref_k`) changes only when the item says so; `di_tru_schema` must be idempotent and back up first.
8. A new choice function must pass substitutability and the law of aggregate demand before registration; otherwise label it "không bảo đảm ổn định" and use measurement mode (item A12).

## Working rules (numbers are referenced elsewhere; keep them)
1. Every change maps to **one item code** in the registry (Z1…G5); ask before working outside it.
2. **Test first**: failing test from the item's `kiem_nhan`, minimal fix, then related tests only.
3. New parameters: see invariant 1.
4. Keep control modes (`stb_tuan`, `stb_co_bu`, A1/A3 in TN7): `du_lieu_test/` scripts need them to reproduce numbers.
5. New choice functions: see invariant 8.
6. After each item: `CHANGELOG.md` (item code, files, new tests) and progress in `docs/ke_hoach/TIEN_DO.md`.
7. Stop and ask when: an invariant conflicts with the item; registry line numbers/state clearly differ from the repo; a new library is needed; the CSV contract or schema must change beyond the item.
8. Trước khi push: chạy skill `soat-ma` (`.claude/skills/soat-ma/`): `kiem_nhanh.py`, then the four tiers in `SKILL.md`; report only unless asked to fix.
9. **Branch handoff**: `docs/phien/<branch, "/"→"__">.md` (from `docs/phien/_TEMPLATE.md`, English, ≤150 lines). Past ~400k tokens of context, finish the current turn, write state there, stop (Stop hook `.claude/hooks/handoff_khi_day_ngu_canh.py` reminds).
10. **No subagents / Agent tool** unless Truong says so explicitly; use Read/Grep/Bash directly.
11. **Model roles** (one session each, bridged by the handoff file): Opus plans (Plan section; first Opus session of a new branch creates the handoff file with Goal + Plan), Sonnet codes and ticks the Plan, Haiku only reads/searches/summarises, never edits.

## Academic integrity (student project)
- All verification numbers are SIMULATED data; never present them as a real survey.
- Commentary, interpretation and conclusions in the project report are written by the student; never draft them. Operational docs, code and tests are fine.
- Log significant AI help in the project's AI log. Correct name: **Gale–Shapley** (not "Sharpley").

## Sectors and order
12 target sectors and the shared chain Z6 → … → G5: `CLAUDE_CHI_TIET.md`. Per-sector order: `nganh[].ke_hoach` in `ke_hoach_thay_doi.json`; follow it, never reorder.

## Read order
0. `docs/phien/<branch>.md` first if it exists (unfinished work, next steps, decisions).
1. `docs/ke_hoach/BOI_CANH_DU_AN.md` — full context: history, findings, measurements, theory, open questions.
2. `docs/ke_hoach/SO_DANG_KY_33_MUC.md` — the 33 items: state, change, risk, acceptance, sectors.
3. `docs/ke_hoach/ke_hoach_thay_doi.json` — same data, machine-readable.
4. Only if needed: document list at the end of `CLAUDE_CHI_TIET.md`.
