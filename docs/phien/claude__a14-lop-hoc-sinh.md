# Branch handoff: claude/a14-lop-hoc-sinh

## Feature / goal
A14 "Lớp của học sinh" (part A, backend; part B = branch claude/a14-giao-dien does export + UI).
Each student may have a class (e.g. 10H1A) used ONLY for display, sorting, filtering and export for
homeroom teachers. The allocation algorithm NEVER reads it. DB: `students.class_id` TEXT, NULL = none.
New vocabulary noun `cohort` (vi "Lớp", en "Class"). One shared normaliser
`rbda_priority_pipeline.chuan_hoa_lop(raw) -> str | None` (strip, collapse whitespace, UPPER; empty -> None).
Conflict rule: last write wins; a Sổ/CSV without the column or with an empty cell keeps the old class.
Approved invariant-7 exception (Truong, 02/11/2026): OPTIONAL CSV column `class_id` right after `reserve_group`.

## Plan
- [x] Step 1 base: DEFAULT_SCHEMA + di_tru_schema (backup) + chuan_hoa_lop + `cohort` noun + skill
- [x] Step 2: CSV import (preferences / test selection), so_nhap (read/write/warn), api_quan_ly
      (list_students_admin, set_student_class, list_classes, create_student_if_missing, kiosk Save),
      api_bao_cao.get_match_results, i18n_errors, registry rows, CHANGELOG, TIEN_DO, docs
- [x] Invariant tests: match_results identical with/without class; no class_id in core; fingerprint unchanged; run_history untouched

## Current state
- MERGED via PR #6 (b044c4c, 03/11/2026; head branch claude/a14-giao-dien, which contains this branch up to c3cd884). CI green on Linux + Windows + ruff at 353d1c4.
- Part A delivered: students.class_id + chuan_hoa_lop + `cohort` noun, CSV/So nhap import, class APIs, post-review fixes A1-A6 and C1/C2 (duplicate labels re-save/clone; static sample workbooks/CSVs with simulated classes via du_lieu_test/them_lop_vao_mau.py).
- Nothing left on this branch; do not push to it. Doc closing is on branch claude/a14-chot-tai-lieu.

## Decisions and gotchas
- Wharton default is ON: allocation tests without determination points need a LOCAL `api` fixture calling tests/_wharton.py::tat_wharton (no autouse).
- JS mirrors of the noun list (i18n.js nounText, js/075_workspace.js WS_DANH_TU) belong to session B.

## Next steps (deferred work)
1. Google Form that asks for the class.
2. xu-li-raw-forms carries the Lop column through.
3. Skill sinh-du-lieu-clb: simulated-class option.
4. Two tests still use `DROP COLUMN` (tests/test_a14_sua_sau_soat.py `_csdl_cu_co_du_lieu`; tests/test_a14_tu_vung_cohort.py): risky on old SQLite; build the old schema with CREATE TABLE instead (as done for test A5 in 353d1c4).

## Files touched
- rbda_priority_pipeline.py, nhan_ws.py, cau_hinh_ws.py, tests (see git log), skill tao-workspace-tu-raw

## Session log (append only)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-02 | Sonnet | Step 1 base | |
| 2026-11-02 | Sonnet | Step 2 import/API/docs, old-test fixes, soat-ma | final |
| 2026-11-03 | Sonnet | C1 label re-save, C2 sample files with simulated classes | |
| 2026-11-02 | Sonnet | Cross-review fixes A1-A6 | one commit per item (A2-A4 together) |
| 2026-11-04 | Sonnet | Closed docs after PR #6 merge | branch claude/a14-chot-tai-lieu |
