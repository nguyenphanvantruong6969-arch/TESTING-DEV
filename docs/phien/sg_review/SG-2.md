# SG-2 review (CHECKER, Sonnet) — round 0 → verdict PASS

Diff `5c8ee63..d9da2c5` (claude/sg-b) vs `SOAT_GIAO_DIEN_KE_HOACH.md` §3 SG-2 / finding C1. Checker session_01YVAyu3aEQRoHtkKoFwqkCc.
Fable's report was not re-read; the spec text and the coder's repro tests were used.

## Checklist (2.10)
1. **Scope — holds.** (1) `js/075_workspace.js` `wsMoTinhNang`: switch "Dùng điểm quyết tâm" (`rules.wharton`), locked + checked + reason under `fa_daa`;
   without FA only `wharton` is sent, FA boxes stay locked. (2) `api_nhap._canh_bao_wharton_trong_xem_truoc`: one grouped warning with count + example id,
   skipped under FA / wharton off, per day/fund like `tu_dien_wharton_mot_clb`, no block on import. (3) `so_nhap._huong_dan_co_dau`: "ô trống tính là 0" replaced
   by "mỗi quỹ cộng đúng 100; quỹ một CLB để trống tự điền 100; quỹ ≥ 2 CLB để trống cả quỹ thì bị chặn". (4) `showLog` hint line + button
   `#btnMoTinhNangTuLoi` → `wsMoTinhNangDangMo` opens the dialog. Nothing else changed (no `cau_hinh_ws.py` edit).
2. **Red-first — holds.** Scratch worktree at 5c8ee63 + the two new test files: 6 failed / 5 passed (the 5 are regression guards). At d9da2c5: all pass (68 passed incl. fg2, ws_nhan).
3. **Mutation — holds.** `len(ds) >= 2` → `>= 99`: 2 tests red. `hopW.disabled = coFa` → `true`: UI switch test red. Worktree restored, clean.
4. **Tests ran for real — holds.** `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`, `-rs`: no SKIPPED. Subset `-k "wharton or so_nhap or xem_truoc or workspace or ws_"`: 1311 passed.
   Plus `test_db_demo_wharton`, `test_du_lieu_mau_diem_quyet_tam`, `test_fg2_xem_truoc_fa`, `test_ws_nhan`, `test_i18n*`: all green. Only red anywhere:
   `test_a13_12_tai_lieu.py::test_ban_do_ma_so_tep_test_la_so_that` ('275' vs 277) = known expected, unrelated.
5. **Invariants — hold.** `kiem_nhanh --so-seed 20`: 7/7 (60 runs byte-identical, ruff, chu_cam, ma_loi_js, i18n_loi_khop, i18n_khoa, no UPDATE/DELETE on run_history).
   No change in `compute_club_priority`, pipeline, schema, CSV contract. New code reads the workbook/DB read-only; error contract `{code, params}`, message source `i18n_errors.py` → `i18n_loi.js` (regenerated, matches).
6. **Strings — hold.** vi + en for all 6 new keys; no internal codes; `i18n.js`, `i18n_errors.py`, `style.css` additions inside the SG-B marker blocks (`i18n_loi.js` is the generated file).
7. **UI — holds (partly limited).** Browser (Chromium) at 1366×768, vi: dialog shows the switch checked with the hint, no horizontal overflow (page and dialog), Lưu/Huy visible, spacing sane.
   1920×1080 overflow check passed, but my attempt to switch the UI to English did not take effect, so the English dialog was NOT looked at; en strings were read in the diff only.
8. **soat-ma** (diff read per tier): tier 1 untouched; tier 2 `_canh_bao_wharton_trong_xem_truoc` is read-only, `la_dat_diem` rejects bool/negative/blank, `\d`-safe regex; tier 3 guard `typeof wsMoTinhNangDangMo === "function"`, button is `type=button`, Escape handling unchanged;
   tier 4 test names/docstrings fine, ruff clean, MANH_B.md present.
9. **Special:** none for SG-2.

## Lead points
- **(a) Four sub-points — all done.** Sub-point 4 is realised as a hint row plus a button in the blocked-run log (headline `wharton_ho_so_chua_hop_le` deliberately unchanged, justified in STATUS_B Decisions; I confirmed old tests forbid changing it). Covered by `test_khung_loi_chay_bi_chan_co_nut_mo_hop_thoai`.
- **(b) `js/02_van_hanh.js` — minimal and needed.** +10 lines, only inside `showLog` (one `them(t("wh_goi_y_tat"))` + one guarded button); the button needs the dialog opener that lives in 075; declared in `MANH_B.md` ("Note for A").
- **(c) Six `SO_NHAP_DQT_*.xlsx` — legitimate and reproducible.** Re-ran `du_lieu_test/sinh_du_lieu_diem_quyet_tam.py --ra` at d9da2c5: all 6 xlsx are byte-identical (excluding docProps/core.xml) to the committed ones, and `DQT_BANG_LOI.json` / `DQT_KIEU_CHIA.json` are identical. Versus 5c8ee63 only `xl/worksheets/sheet3.xml` (= sheet "Hướng dẫn") differs in each file; CLB and học sinh sheets unchanged. Dependent tests (`test_db_demo_wharton`, `test_du_lieu_mau_diem_quyet_tam`) pass with identical numbers.
- **(d) `test_fg2_xem_truoc_fa.py` — no assertion weakened.** Diff = one comment + the sha256 constant of the default sample dump; the hash must change because the generated guide sentence changed (item 3). The test still compares an exact hash; all other assertions untouched.
- **(e) `Trường học` default `wharton: true` — unchanged** (`cau_hinh_ws.py` not in the diff; UI test confirms switch checked by default).
- **(f) Chromium tests really ran** (see 4); `-rs` shows no skips; mutation of the UI line turned a Playwright test red.

## Optional (do not block)
- `wh_goi_y_tat` ("turn off in After-allocation features…") is shown for every wharton-blocked run, also under FA where the switch is locked; the dialog then explains why. Could be hidden under FA.
- English dialog not visually verified by me (see 7).

**Verdict: PASS.**

---

# Round 3 (FIX-2) — verdict PASS

Diff `6aa59c0..690322f` (claude/sg-b), checker session_01YVAyu2yBkGgxzL1aNxajw8. Trigger: lead's full suite had `tests/test_giao_dien_loi_chan_gon.py` 2 red since d9da2c5 (hint added as a second `.log-tom-tat` line).

1. **Old test unchanged and green — holds.** `git diff 5c8ee63..690322f -- tests/test_giao_dien_loi_chan_gon.py` is empty. At 690322f/HEAD: 6 passed. At 6aa59c0 (scratch worktree, removed): 2 failed (`test_chay_bi_chan_chi_hien_tom_tat_nam_em_va_con_lai`, `test_tieng_anh_loi_chan_gon_doi_theo`; strict-mode violation: `#logBox .log-tom-tat` resolved to 2 elements), 4 passed.
2. **SG-2 sub-point 4 — holds, vi and en, 1366×768 and 1920×1080 (Chromium, scratch script, 26 blocked students).** Row `.log-hang-cuoi` = "and 21 more" label, "Open the list to fix", hint, `#btnMoTinhNangTuLoi` ("Mở Tính năng sau khi xếp…" / "Open After-allocation features…"); the hint is `flex: 1 1 100%` so it sits on its own line between the two buttons. No overflow (`documentElement.scrollWidth` = viewport, `#logBox` scrollWidth = clientWidth in all 4 cases); hint 14px, dark text on the page background, readable (screenshot viewed). Tab from "Open the list" lands on `#btnMoTinhNangTuLoi`; click opens the dialog without page errors. English really viewed this time (the round-1 gap is closed).
3. **Mutation — holds.** Put `them(t("wh_goi_y_tat"), "log-tom-tat")` back after the headline → `loi_chan_gon` 2 red; restored, `git status` clean.
4. **Related tests ran for real** (`PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`): every `tests/` file grepping showLog / logBox / log-tom-tat / log-dong / btnMoTinhNangTuLoi / wh_… = `test_giao_dien_chay`, `fg6_danh_sach_loi`, `loi_chan_gon`, `sg2_diem_quyet_tam`, plus `test_sg2_wharton_trong`, `test_ws_nhan`: 91 passed, 0 skipped. `ruff check .` clean. `kiem_nhanh --so-seed 20`: 7/7 (60 runs byte-identical).
5. **Scope — holds.** Diff = `js/02_van_hanh.js` (−1/+4, inside `showLog` only, guarded by the existing `typeof wsMoTinhNangDangMo` check), `style.css` (+1 rule inside the SG-B block), `MANH_B.md` (declares the `02_van_hanh.js` change as "SG-2 FIX-2"). No i18n/string change (`wh_goi_y_tat` reused).

Optional (does not block): the new test for sub-point 4 (`test_khung_loi_chay_bi_chan_co_nut_mo_hop_thoai`) still asserts only the vi word "tắt" in `#logBox`, so it would not notice the hint moving back into a `.log-tom-tat` line or disappearing in en; the mutation in 3 is caught by the old test only. No test pins the hint to the button row.

**Verdict: PASS.**
