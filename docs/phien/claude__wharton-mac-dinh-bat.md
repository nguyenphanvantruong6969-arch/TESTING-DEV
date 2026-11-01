# Branch handoff: claude/wharton-mac-dinh-bat

> Read CLAUDE.md first, then this file. English, cap 150 lines. Rewrite "Current state"; only append to "Session log".

## Feature / goal
A13.13: school workspace default `rules.wharton = True` (commitment points on by default).
Truong approved breaking invariant 1 for this item (recorded in CHANGELOG + TIEN_DO). Invariants 2-8 hold.
Out of scope: "template header by vocabulary" (Direction A/B).

## Plan (Opus plan, ticked)
- [x] 1. Failing tests first (tests/test_wharton_mac_dinh_bat.py)
- [x] 2. Minimal fix: cau_hinh_ws (default True; auto-off in `_chuan_hoa` and `tron_len` when combo not allowed and `wharton` not explicit)
- [x] 3. Fix affected old tests (default -> new default, or explicit `wharton: false` via `tests/_wharton.py::tat_wharton`; no delete/skip)
- [x] 4. Scripts in du_lieu_test/ + soat-ma `kiem_nhanh.py` pass `wharton: false` explicitly
- [x] 5. Error text `wharton_ho_so_chua_hop_le` now names both fixes; docs wording
- [x] 6. ruff clean; soat-ma 7/7; CHANGELOG + TIEN_DO; commits pushed (no PR)
- [x] 7. Parent's acceptance suite: tests/test_a13_13_kiem_nhan.py (45) + tests/test_giao_dien_a13_13_kiem_nhan.py (2): all pass, no code change needed

## Current state
- Work complete and pushed (last commit 94d3e53). Truong APPROVED (01/11/2026) the HS024 data change in vi_du_day_du, the new hash in tests/test_ket_qua_khong_doi.py and the 4 adjusted tests; recorded in CHANGELOG.
- Parent session is watching CI (runs 41309555295, 41309617327) and will report if red. No PR from this branch's sessions; parent opens it when CI is green.
- ruff clean, soat-ma 7/7 at last check.

## Round 3 (after full CI: 241 red in 40 files) — classification
- Group A fixed (local `api` fixture -> `tat_wharton`; 27 files incl. 9 giao_dien; no assert loosened, none skipped): all pass.
- Group B (shipped sample/example/skill outputs under DEFAULT config; NOT masked; waiting for Truong): 50 red.
  test_vi_du_huong_dan(8), test_vi_du_day_du(6), test_csv_mau(2), test_bo_sach(10), test_skill_sinh_du_lieu(6),
  test_skill_tao_workspace(3), test_skill_xu_li_raw(1), test_mau_forms_thi_clb(1), test_kich_ban_nhap_tay(8: the doc'd
  scenario in du_lieu_test/NHAP_TAY.md), test_so_nhap(2: vi_du sổ must load with 0 warnings), test_diem_bat_thuong(1:
  published sets must be silent), test_rang_buoc_csdl::test_csdl_demo_that_duoc_nang_len (shipped demo DB, health n_high=1).
- Real bug found in own change: VI text of `wharton_ho_so_chua_hop_le` contained "workspace" -> fixed.
- Merged claude/sleepy-sagan-ly5fx0 (doc tests); CLAUDE_CHI_TIET `tests/` row updated to 167 files / 3.127 cases.

## Round 4 (Truong chose direction (c) for group B)
- Merged claude/demo-wharton-va-duong-dan. DQT added to vi_du_huong_dan, mau_csv/vi_du_day_du, vi_du_ca_tuan, 08 via `du_lieu_test/them_diem_quyet_tam_vao_mau.py` (fixed seeds 11202610x; SIMULATED data). `mau_csv/tao_so_nhap.py` now reads `wp` cols.
- vi_du_day_du: HS024 dropped `thu_2` pref `clb_bongro` in tao_bo_mau.py (otherwise 2 em trang tay with DQT, test needs exactly 1).
- bo_sach untouched; Wharton OFF explicit everywhere it runs. sinh-du-lieu-clb default = hop_le + `--khong-diem-quyet-tam`.
- tao-workspace-tu-raw writes `wharton:false` + message; xu-li-raw-forms / chuyen_forms only report (a sổ cannot hold config).
- NHAP_TAY.md: new step 3 (DQT table, seed 112026105).
- TODO later (not done on purpose): add DQT collection to the Google Form (tao-google-form-clb).

## Decisions and gotchas
- `rbda_priority_pipeline.LUAT_XEP_MAC_DINH["wharton"]` stays False: bare pipeline calls (rules=None, run_full_pipeline) keep old numbers; default ON lives only in cau_hinh_ws.
- Old stored config lacking the `wharton` key reads as ON (no migration, per Truong's original request).
- Data is blocked only when a fund has >=2 clubs and no points (single-club fund auto-fills 100, "cach A").
- soat-ma `kiem_trung_khit` would silently compare two "blocked" runs; fixed by writing wharton false in both.

## Next steps
1. Only act on parent/Truong feedback (CI red files). Classify: A = internal fixture -> local `api` fixture + `tat_wharton`; B = shipped sample/skill output -> ask parent, never mask.
2. Later (not now): Google Form (tao-google-form-clb) should collect commitment points.

## Files touched
- cau_hinh_ws.py, i18n_errors.py, i18n_loi.js, api_nhap.py/rbda_priority_pipeline.py (comments), docs: HUONG_DAN_SU_DUNG.md, TAI_LIEU_DU_LIEU.md, CHANGELOG.md, TIEN_DO.md, CLAUDE_CHI_TIET.md (tests row: 168 files / 3.138 cases), mau_csv/* (GIAI_THICH, wp cols, tao_so_nhap.py, tao_bo_mau.py HS024), du_lieu_test/* (them_diem_quyet_tam_vao_mau.py NEW, NHAP_TAY.md, vi_du_huong_dan/*, scripts with explicit wharton false).
- Skills: sinh-du-lieu-clb (default hop_le + --khong-diem-quyet-tam), tao-workspace-tu-raw (wharton:false + note), xu-li-raw-forms (note), soat-ma kiem_nhanh.py; mau_forms_thi_clb/chuyen_forms_sang_phan_mem.py (note).
- ~60 test files: local `api` fixture override with `tat_wharton` (group A), group-B tests keep asserts (data changed), new tests test_wharton_mac_dinh_bat.py, test_a13_13_kiem_nhan.py, test_giao_dien_a13_13_kiem_nhan.py.

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-01 | Sonnet | Branch + handoff created | |
| 2026-11-01 | Sonnet | Implemented A13.13, fixed tests/scripts, parent acceptance suite | see Current state |
| 2026-11-01 | Sonnet | Round 3 (group A after CI) + round 4 (group B, direction c, demo-branch merge, skills, NHAP_TAY) | handoff at ~400k tokens; final test run + ruff + soat-ma + report to parent pending |
| 2026-11-01 | Sonnet | Final handoff after round 4: 4 red tests fixed, ruff/soat-ma green, report sent to parent | context >400k; open a new session to continue |
| 2026-11-01 | Sonnet | Recorded Truong's approval in CHANGELOG; final handoff | context >400k; open a new session to continue |
