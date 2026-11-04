# Branch handoff: claude/gallant-mendel-uki8j2 (impl, session 1)

> Role: impl (Sonnet). Coordinator: session_01YVAyu1tdPE9AURCeJXaN5S. Protocol: `docs/phien/T3_GIAO_THUC.md`.
> Language: English. Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".
> Fresh impl per lot from now on (coord's decision): the next impl starts at L2 from this file.

## Feature / goal
Implement T3 lots L0..L3 on this branch (spec = "Lot L<n>" in `docs/phien/claude__gallant-mendel-uki8j2.md`;
study rows by id: `grep -n "^| T3-26 " docs/nghien_cuu/T3_DEBLOAT_GIAO_DIEN.md`).

## Plan
- [x] L0 (+ fix1, fixci1), tester NO BUGS
- [x] L1 implemented, pushed (`0fd4981`), tester L1 reviewing
- [x] L2  - [x] L3 implemented (tester pending)

## Current state (L3 DONE, impl session 4)
- L3 implemented on top of 7ac6beb: tab 03/05 names, T3-16/17/18 (hide "Theo lớp" without classes, sort by column headers, no "Thứ tự"),
  T3-19 (`export_bang_dang_xem` + `#btnKqTaiBang`), T3-22 (card removed from tab 03), T3-31 (one table + "Xem chi tiết"),
  T3-27 (Chỉ tiêu / Suất ưu tiên / Nhóm ưu tiên in i18n.js, index.html, i18n_errors.py; Excel headers in api_xuat.py left as they were),
  T3-11 (wizard: "Tạo" on step 1, `#wzTuyChinh` opens steps 2-4). CHANGELOG + TIEN_DO row T3-L3 written; tests row = 192 files / 3.433 cases.
- NOT YET VERIFIED: the last related-UI batch (ui5) showed ~7 failures (F at positions 9,12,14-16,22,23 of: test_giao_dien_a14_lop, danh_sach_clb,
  ux_xuat, tom_tat_ket_qua, t3_l0, t3_l1, t3_l2_van_hanh, a13_8_quan_ly, a13_13_kiem_nhan, ws_nhan_giao_dien, loi_chan_gon, sua_loi_p1, a13_12_tai_lieu, tieng_viet_sach).
  Output file was in the old scratchpad; RE-RUN that file list (background + Monitor), fix pinned-text/old-id failures (likely tab labels "Dữ liệu khác", "Theo ngày trong tuần",
  Tổng chỗ, #dcChonClb, #kqTang2, wizard #wzTiep at step 1), then push and send `IMPL DONE L3` (base 7ac6beb) to coord.
- Already green: test_giao_dien_t3_l3, test_t3_l3_backend, wizard tests (ws_giao_dien, a13_12_ws, a13_13, ws_wharton, t3_l1_ws), Điểm chuẩn tests, t2_ket_qua, test_ws_nhan*, non-UI batch, soat-ma 7/7.
- L3 gotchas: wizard tests now press `#wzTuyChinh` instead of the first `#wzTiep`; `tests/test_ws_nhan.py` has T3-27 text pairs in `THAY_CHU_T3`
  plus 3 exact keys in `chu_ui_doi_co_y_t3.json` (tier_reserve vi/en, th_tong_cho en). Run `pytest` via the uv tool; first `uv pip install --python
  /root/.local/share/uv/tools/pytest/bin/python openpyxl pillow python-docx ruff pytest-cov playwright==1.63.0` if modules are missing.

## Test environment (read before running anything)
- `python3 -m venv .venv && pip install` HANGS on the proxy here. Use the uv tool pytest: `pytest` (= /root/.local/bin/pytest,
  python at `/root/.local/share/uv/tools/pytest/bin/python`). Already installed there: playwright 1.63, openpyxl, pillow, python-docx, ruff, pytest-cov.
  If a package is missing: `uv pip install --python /root/.local/share/uv/tools/pytest/bin/python <pkg>`.
- UI tests: `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers pytest -q -p no:cacheprovider <files>`. A tool call is killed at 120 s:
  run long sets in the background and wait with Monitor (until-loop on the output file).
- Run a second test set in a `git worktree` if you need to edit while tests run (tests read the working tree).
- Machine check: `python3 .claude/skills/soat-ma/scripts/kiem_nhanh.py --co-so origin/main` (7 items; `git fetch origin main` first).
  Invariant 1 with 20 seeds: call `kiem_nhanh.kiem_trung_khit(new_dir, old_dir, tuple(range(1,21)), 3)` on a `git archive origin/main` dir.

## Gotchas that cost time
- **Pinned-text tests.** Changing displayed text breaks many old tests. Before editing, grep tests for the old string. Typical victims:
  `test_ws_nhan.py`, `test_ws_nhan_giao_dien.py`, `test_giao_dien_tieng_viet_sach.py`, `test_van_phong_tu_nhien.py`, `test_i18n_*`,
  `test_giao_dien_quan_ly_tab_con.py`, `test_giao_dien_a13_10_diem_chuan.py`, `test_a13_13_kiem_nhan.py`, `test_wharton_mac_dinh_bat.py`.
  `test_giao_dien_tieng_viet_sach.py` bans English technical words and "zip"/ALL-CAPS in vi and en UI text, and "tab" in vi.
- **Frozen snapshot `tests/test_ws_nhan.py`** compares every default string with `tests/du_lieu_ws/chuoi_truoc_khi_co_nhan.json`.
  Intentional changes: add a removed key to `KHOA_UI_DA_BO`; a text rename to `THAY_CHU_T3`; a rewritten UI string to
  `tests/du_lieu_ws/chu_ui_doi_co_y_t3.json` (value = NEW filled default text, both languages). Regenerate that JSON with a script that
  runs `_chay_js({"khoa": ...})` (node) against the snapshot after applying `THAY_CHU_T3`, then drops removed keys. New error codes go
  to `MA_MOI_SAU_ANH_CHUP`. Company-vocabulary expectations are hard-coded in `test_giao_dien_cong_ty` and `test_ws_nhan_giao_dien.py`.
- **Fallback text in `index.html` must equal the catalog** (`tests/test_t3_l1_chu_du_phong.py`, filled with default labels).
  After editing `i18n.js` run it; it lists mismatches. `{person}` = "Học sinh" (capital), `{person_l}` lowercase: sentence starts need `{person}`.
- **Excel texts** (`api_xuat.py`) go through `dien_nhan` / `t.n(...)`; a `%d {person_l}` string not wrapped in `t.n` leaks braces into the file.
- **Test file count row**: every added `tests/test_*.py` must update the `tests/` row of `docs/ke_hoach/CLAUDE_CHI_TIET.md`
  (files + `pytest --collect-only -q` cases; now 188 files / 3.396 cases) and `tests/test_a13_12_tai_lieu.py` must be in the related set.
- Seed input lives in `<details id="nangCao">`; UI tests must open it (`page.evaluate("document.getElementById('nangCao').open = true")`).
- `stb_lock` always has one seeded row; assert on `is_locked`, not row count. `ruff`: tests that import a fixture and also take it as a
  parameter need `# noqa: F811`.
- Regenerate `i18n_loi.js` with `python3 tao_i18n_js.py` after every `i18n_errors.py` edit.
- Each stop-hook nag about unpushed commits: do not push unverified work; commit locally, push after related tests are green.

## Next steps (ordered)
1. If `FIX L2` round 2 arrives: fix, related tests by grep (+ `test_a13_12_tai_lieu.py`, `test_giao_dien_tieng_viet_sach.py`, `test_ws_nhan.py`), push, reply `IMPL DONE L2 fix2`.
2. Otherwise nothing; L3 belongs to a fresh impl.

## Files touched (L0 + L1)
- Backend: api.py (empty-run guard), api_quan_ly.py (`create_or_update_club` None = keep), api_xuat.py (Excel text), main.py (window title)
- Text: i18n.js, i18n_errors.py, i18n_loi.js (generated), index.html, HUONG_DAN_SU_DUNG.md
- UI: style.css, js/00_nen.js (`dinhDangGio`), js/01_khung.js, js/02_van_hanh.js, js/04_nhap_tai_cho.js, js/05_quan_ly.js, js/06_cham_diem.js, js/075_workspace.js
- Tests: test_t3_l0_backend.py, test_giao_dien_t3_l0.py, test_t3_l1_chu.py, test_t3_l1_chu_du_phong.py, test_giao_dien_t3_l1.py,
  test_giao_dien_t3_l1_ws.py, du_lieu_ws/chu_ui_doi_co_y_t3.json, and ~14 old test files adjusted (see CHANGELOG T3-L0 fixci1, T3-L1)

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-04 | Sonnet (impl 1) | L0 implemented, fix1, fixci1 | tester NO BUGS on L0 |
| 2026-11-04 | Sonnet (impl 1) | L1 implemented (`0fd4981`), handoff written | tester L1 pending |
| 2026-11-04 | Sonnet (impl 3) | L2 finished (T3-23, T3-28, T3-21, docs, soat-ma) | tester L2 pending |
| 2026-11-04 | Sonnet (impl 3) | L2 fix1 (6 tester items, 5 done, T3-32 collapse skipped) | head a1258c3; handoff at 200k |
| 2026-11-04 | Sonnet (impl 4) | L3 implemented (T3-11/16/17/18/19/22/27/31 + tab names) | tester L3 pending |
