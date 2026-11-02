# Branch handoff: claude/a14-giao-dien

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English (cheaper in tokens). Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".
> File name = branch name with "/" replaced by "__" (see `.claude/hooks/handoff_khi_day_ngu_canh.py`).
> Written by the session when context passes ~400k tokens (after finishing its current prompt).

## Feature / goal
A14 part B (export + UI for the student class). Part A (branch claude/a14-lop-hoc-sinh) owns DB column
students.class_id, chuan_hoa_lop, `cohort` noun and all class APIs. Part B: Excel sheet "Theo lớp" (always),
API export_theo_lop (folder, one .xlsx per class), "Lớp" column after "Họ tên" in several tables, and UI
(Manager filter/sort/edit, Results filter/sort/export button, kiosk required class dropdown, workspace 6th noun).
Algorithm, match_results, run_history untouched.

## Plan (written by Opus; ticked by Sonnet)
- [x] api_xuat.py: sheet Theo lớp, export_theo_lop, Lớp column (tests/test_a14_lop_xuat.py, 12 green)
- [x] JS/HTML/i18n written to the contract (js/03,04,05,075, index.html, i18n.js)
- [x] tests/test_giao_dien_a14_lop.py written (only the i18n-text test can run before A's APIs land)
- [x] Merged A (ddd6035); arg order matched; Chromium tests green (10 + 12)
- [x] ruff, soat-ma (kiem_nhanh 7/7), CHANGELOG "A14 — phần B", TIEN_DO, HUONG_DAN_SU_DUNG, push (no PR)

## Current state (overwrite each handoff)
- Done: export + UI + docs; merged A; 22 new tests green; 283 related old tests green; kiem_nhanh 7/7.
- Open: tests/test_ws_nhan.py::test_moi_ma_loi_mac_dinh_giong_het_anh_chup is red because A's 4 new error codes are missing from MA_MOI_SAU_ANH_CHUP (A's gap, reported to coordinator; B did not edit).
- soat-ma notes (report only): language switch does not re-render the class dropdown texts until the next load; export_theo_lop leaves a partial folder if a mid-way write fails.

## Decisions and gotchas (keep short)
- Name clash: api_xuat._khoa_lop_xuat (was _khoa_lop_tu_nhien, shadowed A's method on PipelineAPI).
- Export tests set class via SQL, so they do not depend on A's API.
- export_theo_lop: absolute existing dir -> "x (2)" (own logic, _duong_xuat would reject an existing dir).
- tkb_xlsx (Excel only) carries the Lớp column; du["tkb"] (CSV) unchanged.

## Next steps (ordered)
1. After A fixes MA_MOI_SAU_ANH_CHUP, merge again and rerun test_ws_nhan.py.

## Files touched
- api_xuat.py, index.html, i18n.js, js/02,03,04,05,075, tests/test_a14_lop_xuat.py, tests/test_giao_dien_a14_lop.py, tests/test_so_excel_de_dung.py + test_ws_nhan.py (sheet list)

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-02 | Sonnet | export + UI + tests written | waiting on A's APIs |
| 2026-11-02 | Sonnet | merged A, fixed name clash + filter bug, soat-ma | final report sent |
