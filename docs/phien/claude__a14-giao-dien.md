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
- Done: export + UI + docs; merged A (latest); two read-only view tabs 06 (club members) and 07 (by class) in js/09_the_xem.js; language switch re-renders class dropdowns; export_theo_lop removes the half-made folder on failure.
- Tests: new 14 + 7 + 17 green; 435 related old+new green (incl. test_ws_nhan after A added its 4 codes); kiem_nhanh 7/7.
- Open: nothing known. Screenshots of both tabs are in the session scratchpad (not committed).

## Decisions and gotchas (keep short)
- Name clash: api_xuat._khoa_lop_xuat (was _khoa_lop_tu_nhien, shadowed A's method on PipelineAPI).
- Export tests set class via SQL, so they do not depend on A's API.
- export_theo_lop: absolute existing dir -> "x (2)" (own logic, _duong_xuat would reject an existing dir).
- tkb_xlsx (Excel only) carries the Lớp column; du["tkb"] (CSV) unchanged.

## Next steps (ordered)
1. Wait for coordinator review; merge A again only if A pushes more.

## Files touched
- api_xuat.py: Theo lớp sheet, export_theo_lop (ket_qua_cu, dọn thư mục dở, cắt tên tệp), cột Lớp
- api_bao_cao.py: get_thoi_khoa_bieu(class_id), get_danh_sach_clb.class_id
- index.html, style.css, i18n.js: UI lớp, thẻ 06/07, chữ vi+en
- js/01_khung.js (TAB_LOADERS), js/02_van_hanh.js, js/03_ket_qua.js, js/04_nhap_tai_cho.js (kiosk lớp, chưa lưu), js/05_quan_ly.js, js/07_ngon_ngu.js, js/075_workspace.js, js/08_khoi_dong.js, js/09_the_xem.js (mới), js/_danh_sach.txt
- tests/_trinh_duyet.py (+ test_trinh_duyet_tim.py), test_a14_lop_xuat.py, test_a14_the_xem.py, test_giao_dien_a14_lop.py; test_so_excel_de_dung.py, test_ws_nhan.py (kỳ vọng trang Theo lớp)
- CHANGELOG.md, docs/ke_hoach/SO_DANG_KY_33_MUC.md, TIEN_DO.md, HUONG_DAN_SU_DUNG.md

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-02 | Sonnet | export + UI + tests written | waiting on A's APIs |
| 2026-11-02 | Sonnet | merged A, fixed name clash + filter bug, soat-ma | final report sent |
| 2026-11-02 | Sonnet | tabs 06/07, lang re-render, export cleanup, tests, soat-ma | final report sent |
| 2026-11-02 | Sonnet | cross-review fixes B1-B7 (A merged last) | see CHANGELOG |
