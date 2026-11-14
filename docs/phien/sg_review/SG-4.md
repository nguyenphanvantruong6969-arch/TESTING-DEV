# SG-4 review (M3) — checker session_01TGThn68N7shbENa7GNKWsZ, round 0
Diff a959972..53025b1 (branch claude/sg-a). Verdict: **FIX-1** (one cosmetic en-wording defect; everything else passes).

## Checked and OK
- Same rule on both paths: `api_sau_xep.gui_khieu_nai` calls `fa_sau_xep.khop_ma_hoc_sinh` (exact wins, else `strip().casefold()` if exactly ONE match, else None). Forms path uses the same function. Ambiguous -> None -> `khieu_nai_hs_khong_co` (test `test_ma_mo_ho_bi_tu_choi_nhu_duong_forms`). Stored ID unchanged (tested).
- Two codes distinct and correct: unknown student -> `khieu_nai_hs_khong_co`; known student, no result that day (or unknown buoi) -> `khieu_nai_chua_co_ket_qua`. Old `khieu_nai_khong_hop_le` kept: still used by `_them_khieu_nai` (Forms path, `nhap_sau_ket_qua_forms`) and its test in `test_fa_m6b_sau_ket_qua.py`.
- JS: `10_theo_doi.js` uses generic `showErrorToast(res.errors)`; both codes render. Browser look (1366x768 vi, 1920x1080 en): both codes appear as error toasts, layout fine, no page errors.
- Strings vi+en only inside SG-A marker blocks (`i18n_errors.py`, `i18n_loi.js`, `test_ws_nhan.py`); `tao_i18n_js.py` leaves no diff.
- Tests run: `test_sg4_khop_ma`, `test_fa_gap3_khieu_nai`, `test_fa_m6b_sau_ket_qua`, `test_ws_nhan`, `test_giao_dien_fa_gap3_khieu_nai` (really run, not skipped), `test_giao_dien_fg8_cau_chu`: all pass. ruff clean. `kiem_nhanh --co-so a959972 --so-seed 20`: 7/7, 60 cases identical.
- Note: the existing UI test only covers the unknown-student code (vi, 1400 wide); the "no result" code has backend test only. Not blocking.

## Fix list
1. **FIX-1 (low, visible en text).** `i18n_errors.py` (+ regenerated `i18n_loi.js`), SG-A block: both new `en` strings use `{person}` where the rest of the file uses `{person_l}` mid-sentence. Result in the UI: "Appeal not accepted: no **Student** with ID khong_co was found." and "...: **Student** s1 has no result...". Change `{person}` -> `{person_l}` in both `en` strings, run `python tao_i18n_js.py`, re-run `test_sg4_khop_ma.py` and `kiem_nhanh`. (vi strings already correct.)

---
# Round 1 — checker session_01TGThn6utYnaicoK4Ce6A5K
Diff a959972..17eaf11 (whole item incl. FIX-1 commit 17eaf11). Verdict: **PASS**. Fable's report unreadable (D-A1) → spec text.

## FIX-1 confirmed
- `i18n_errors.py` SG-A block: both `en` strings now use `{person_l}` (diff 53025b1..17eaf11 touches only those 2 lines + `i18n_loi.js`). `format_message(..., "en")` → "Appeal not accepted: no student with ID x was found. …" (lower-case, natural).
- `python tao_i18n_js.py` leaves no diff; `kiem_nhanh` `i18n_loi_khop` ĐẠT.

## 2.10 checklist (whole diff)
1. **Scope:** `gui_khieu_nai` uses `fa_sau_xep.khop_ma_hoc_sinh` (same rule as Forms path); two distinct codes (`khieu_nai_hs_khong_co`, `khieu_nai_chua_co_ket_qua`); old code kept for Forms path. Nothing else changed (production files in diff: `api_sau_xep.py`, `i18n_errors.py`, `i18n_loi.js` only).
2. **Red-first (rerun):** scratch worktree at a959972 + only `tests/test_sg4_khop_ma.py` → 4 failed; at 17eaf11 → 4 passed.
3. **Mutation (rerun):** at 17eaf11 replaced `khop_ma_hoc_sinh(...)` by exact-only match → `test_ma_go_tay_khac_hoa_thuong_va_khoang_trang_duoc_nhan` fails (1 failed, 3 passed). Worktree removed.
4. **Tests run for real** (`PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`, `-rs`): `test_sg4_khop_ma`, `test_fa_gap3_khieu_nai`, `test_fa_m6b_sau_ket_qua`, `test_ws_nhan`, `test_van_phong_tu_nhien`, `test_giao_dien_fa_gap3_khieu_nai` (appeal tab, Chromium), `test_giao_dien_fg8_cau_chu` → 102 passed, 0 skipped. `ruff check .` clean.
5. **Invariants:** `kiem_nhanh --co-so a959972 --so-seed 20` → 7/7, 60 cases (3 sets × 20 seeds) identical. Diff does not touch `rbda_priority_pipeline.py` (inv. 2 / forbidden core); no rank or past outcome read; no schema/CSV change; no write to `run_history`; appeal write still inside `_ket_noi_ghi` + `_them_khieu_nai`; `{ok,data,errors}` contract kept, messages only in `i18n_errors.py`.
6. **Strings:** vi + en for both codes, natural, no internal codes, inside SG-A marker blocks (`i18n_errors.py`, `i18n_loi.js`, `test_ws_nhan.py`).
7. **UI:** round-0 browser check (1366×768 vi, 1920×1080 en: both codes as error toasts, no overflow) reused — the JS (`10_theo_doi.js`, `style.css`) is unchanged since; only the en wording differs, which is text-only. The Chromium appeal-tab test reran and passed.
8. **soat-ma:** `kiem_nhanh` 7/7 (ruff, chu_cam, ma_loi_js, i18n_loi_khop, i18n_khoa, trung_khit, khong_sua_nhat_ky). Tiers 1–4 on the diff: no core change; backend change small and in the pipeline-free appeal path; no JS change; test/fragment (`MANH_A.md`) present, CHANGELOG/TIEN_DO not edited (correct per 2.3).
9. **Special:** none for SG-4.

## Optional (non-blocking)
- UI test covers only the unknown-student code; "no result" code has backend test only (from round 0).
