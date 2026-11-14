# Integration checker — sg-a + sg-b + sg-c (`git diff 98709f1..cb50a38`, branch claude/sg-sua)
Checker: session_01TGThn6G7hMNDrmLhcpe5Hg (Sonnet). Focus: checklist 9 "no behaviour lost in conflicts" + global invariants. All numbers SIMULATED.
**Verdict: PASS** (one Optional doc nit, non-blocking).

## 1. Merge commits vs both parents (8733855 sg-c, 35111d5 sg-b)
Method: for each merge M, base = merge-base(P1,P2) = 98709f1; for each of the 16 listed shared files, every line ADDED by P1 or P2
relative to base was searched in M's version of the file.
- 8733855 and 35111d5: **0 added lines missing** in all 16 files except `js/09_the_xem.js` (3 lines, see below).
- `js/09_the_xem.js` `veKqTheoClb` (SG-10 × SG-6): the 3 "missing" lines are the two sides' edits of the same expression; merged form
  (line ~276-279) is `(d.tu_do ? t("clb_tu_do_theo_clb[_nhieu]") : t("members_dem",…)) + (chuGioDiaDiem(d) ? " · " + chuGioDiaDiem(d) : "")`
  → both SG-10 (free club text) and SG-6 (time/room suffix) kept.
- `api_xuat.py`: SG-10 ("Đã xếp N · không giới hạn chỗ", blank % for free clubs, "Tổng sức chứa" numeric-only sum) and SG-6
  (`Giờ:`/`Địa điểm:` header parts, `_o_clb_kem_gio`, `o_xlsx` for xlsx only) both present in final diff.
- `api_sau_xep.py`: SG-4 `gui_khieu_nai` uses `sx.khop_ma_hoc_sinh` + two codes (`khieu_nai_hs_khong_co`, `khieu_nai_chua_co_ket_qua`);
  SG-12 `_ban_do_forms`, `_canh_bao_cot_la` and the Forms readers (`doc_tep_forms_phan_hoi(hang, ban_do, cot_la)`, `doc_tep_forms_khieu_nai(..., ban_do)`,
  `ThieuBanDo`) present; line ~630 still matches ids with `khop_ma_hoc_sinh`. No loss either way.
- `tests/test_sg_tich_hop_tu_do_gio.py` (3 cases: stats, export, Chromium Theo CLB) pass; proves SG-6 × SG-10 together.

## 2. i18n
- `python tao_i18n_js.py` → `git diff i18n_loi.js` empty (file equals generator output); kiem_nhanh `i18n_loi_khop`, `i18n_khoa` ĐẠT.
- Marker blocks SG-A/SG-B/SG-C intact and closed in `i18n_errors.py`, `i18n.js` (vi AND en, key sets identical per block: 7/7, 7/7, 3/3), `tests/test_ws_nhan.py`, `style.css` (B, C).
- `MA_MOI_SAU_ANH_CHUP`: all 23 codes added in `i18n_errors.py` by the diff appear in the list (script check, 0 missing).

## 3. Tests (real run)
`PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers pytest` on 46 files = every test file added/changed in the diff + files named in the item reviews + `test_sg_tich_hop_tu_do_gio.py`, `test_a13_12_tai_lieu.py` (incl. the count test), `test_ws_nhan.py`, `test_van_phong_tu_nhien.py`: **674 passed, 0 failed, 0 skipped** (`-rs`; Chromium ran). Full suite not run (lead).

## 4. Invariants
- `kiem_nhanh --co-so origin/main --so-seed 20` → **7/7** (60 cases byte-identical). `ruff check .` clean.
- `rbda_priority_pipeline.py` diff: only DDL (`clubs.gio`, `clubs.dia_diem`, nullable) and `di_tru_schema`/`_them_cot_fa_cho_clb` (+2 columns). No hunk in `run_rbda`, `run_rbda_nhieu_buoi`, `club_choice_function`, `compute_club_priority`, `verify_stability`.
- Schema change only SG-6, via idempotent `di_tru_schema` (backup first; migration-twice verified in SG-6 review + tests pass). No other CREATE/ALTER in the diff (the only DROP COLUMN is inside a test).

## 5. Docs
- CHANGELOG entry, TIEN_DO rows, CLAUDE_CHI_TIET line: claims checked against code (`chayNut/chayTai/noiTiep/veCanhBaoGom` in `js/00_nen.js`, `--giu-ma` in `tao_mau_forms.py`, `color-scheme: light` in style.css, SG-1/3/4/5/8/11a/11b/integration case counts 9/5/4/6/9/15/9/3 match `--collect-only`).
- Test count line "293 tệp, 6.224 ca": `ls tests/test_*.py` = 293, `pytest --collect-only` = 6224 → correct.
- Optional (non-blocking): TIEN_DO row SG-12 says "44 ca" but `tests/test_sg12_tieu_de_thuan.py` collects **47**.

## 6. Browser walkthrough (Chromium, 1366×768, vi, scratch harness reusing the repo fixtures, data outside repo)
FA workspace, free club T with "Thứ 4, 15:00" / "Phòng B2" and 12 students: Quản lý row shows "Thứ 4, 15:00 · Phòng B2", "không giới hạn chỗ", no %; Kết quả → Theo CLB line "12 học sinh · không giới hạn chỗ · Thứ 4, 15:00 · Phòng B2"; export of the same workspace asserted by the integration test; no horizontal overflow (scrollWidth 1366 = innerWidth); **0 page errors**. Workspace chooser (SG-11b): `tests/test_giao_dien_sg11b_focus_man_chon.py` (9 Chromium cases: focus trap, Esc, focus return) passed.
