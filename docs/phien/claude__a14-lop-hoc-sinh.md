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
- DONE (part A): base + CSV/So nhap import + So mau/export co_lop + APIs (list_students_admin, set_student_class,
  list_classes, create_student_if_missing, submit_test_selection/submit_preferences class_id, get_student_entry_state,
  get_match_results) + i18n errors + skill + docs/registry/CHANGELOG/TIEN_DO.
- Coordinator contract: class_id is 3rd optional positional arg; must exist in list_classes else
  `lop_khong_co_trong_danh_sach`, nothing written. api_bao_cao.py now owned by session B (do not edit).
- Tests: tests/test_a14_*.py (51+2 cases) green; related (non-UI) run: 2022 pass, 8 old failures all fixed
  (see CHANGELOG). soat-ma kiem_nhanh 7/7 PASS. UI/browser tests NOT run here (session B).
- Post-review fixes A1-A6 done (tests/test_a14_sua_sau_soat.py, 26 cases); see CHANGELOG.
- C1 (saved duplicate labels can be re-saved/cloned) and C2 (static sample workbooks/CSVs have simulated Lop; script du_lieu_test/them_lop_vao_mau.py) done.
- Next steps / not done: skill sinh-du-lieu-clb has no simulated-class option yet.

## Decisions and gotchas
- Wharton default is ON: allocation tests without determination points need a LOCAL `api` fixture calling tests/_wharton.py::tat_wharton (no autouse).
- JS mirrors of the noun list (i18n.js nounText, js/075_workspace.js WS_DANH_TU) belong to session B.

## Status
- PR #6 opened, waiting for CI (claude/a14-giao-dien -> main, includes this branch up to c3cd884). Coordinator asked A to PAUSE: no more pushes to this branch unless told.

## Next steps
1. Step 2 as in Plan.

## Files touched
- rbda_priority_pipeline.py, nhan_ws.py, cau_hinh_ws.py, tests (see git log), skill tao-workspace-tu-raw

## Session log (append only)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-02 | Sonnet | Step 1 base | |
| 2026-11-02 | Sonnet | Step 2 import/API/docs, old-test fixes, soat-ma | final |
| 2026-11-03 | Sonnet | C1 label re-save, C2 sample files with simulated classes | |
| 2026-11-02 | Sonnet | Cross-review fixes A1-A6 | one commit per item (A2-A4 together) |
