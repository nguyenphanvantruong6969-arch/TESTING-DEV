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
