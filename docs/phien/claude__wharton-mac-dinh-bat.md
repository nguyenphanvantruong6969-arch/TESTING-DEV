# Branch handoff: claude/wharton-mac-dinh-bat

> Read CLAUDE.md first, then this file. English, cap 150 lines. Rewrite "Current state"; only append to "Session log".

## Feature / goal
A13.13: the school workspace default `rules.wharton = True` (commitment points / "Wharton" ON by default). Truong approved breaking invariant 1 for this item (recorded in CHANGELOG + TIEN_DO under A13.13). Invariants 2-8 hold. Out of scope: "template header by vocabulary" (Direction A/B).

## Plan (all ticked)
- [x] Failing tests first (tests/test_wharton_mac_dinh_bat.py, 16 cases)
- [x] cau_hinh_ws: default True; auto-off in `_chuan_hoa` and `tron_len` when priority=tier / score_scope=per_person and `wharton` not explicit (explicit true + bad combo still raises)
- [x] Fix old tests (group A) and independent acceptance suite from parent (tests/test_a13_13_kiem_nhan.py 45 + tests/test_giao_dien_a13_13_kiem_nhan.py 2: all pass, no code change needed)
- [x] Scripts in du_lieu_test/ + soat-ma kiem_nhanh.py pass `wharton: false` explicitly
- [x] Error text `wharton_ho_so_chua_hop_le` names both fixes (VI uses "khong gian lam viec", no English word)
- [x] Group B (shipped samples / skills), direction (c); demo-branch merge; docs; CHANGELOG/TIEN_DO; ruff; soat-ma

## Current state (rewritten)
- (a) LAST CODE COMMIT: 94d3e53 (Truong's approval recorded in CHANGELOG); handoff commits after it. Branch is pushed to origin/claude/wharton-mac-dinh-bat. MERGED INTO IT (merge commits): origin/claude/sleepy-sagan-ly5fx0 (doc-test fixes, CLAUDE_CHI_TIET map) and origin/claude/demo-wharton-va-duong-dan (demo DB with Wharton on). 79c8946's `_nap_nhieu_buoi` change was redone by hand, not cherry-picked.
- (d) CI: GitHub runs 41309555295 and 41309617327 are running; result UNKNOWN. Parent session (session_01YVAyu1fhG9nmCdTfR1eikv) reads CI and will report. Local status: ruff clean, soat-ma 7/7, targeted runs green after fixes (last: 27 passed on the 2 re-fixed files; before that 1414 passed). The whole suite was never run locally (rule 2; CI does).
- No PR yet: the PR into the default branch is opened by the PARENT session when CI is green.

## Decisions (Truong, via parent)
- (b) Default ON for the school workspace; exception to invariant 1 approved. `rbda_priority_pipeline.LUAT_XEP_MAC_DINH["wharton"]` stays False (bare pipeline calls keep old numbers; default ON lives only in cau_hinh_ws). Old stored configs without the `wharton` key read as ON (no migration).
- Group B = direction (c): example sets in user docs get SIMULATED valid commitment points via fixed-seed script `du_lieu_test/them_diem_quyet_tam_vao_mau.py` (vi_du_huong_dan, mau_csv/vi_du_day_du, vi_du_ca_tuan, 08_nguyen_vong_nhieu_buoi); CSV column contract unchanged (`wp_k` / `<buoi>_wp_k`); `mau_csv/tao_so_nhap.py` reads `wp` cols.
- `bo_sach` (thesis data): data untouched; every place that runs it sets Wharton OFF explicitly. No published number changed.
- Skill sinh-du-lieu-clb: default `--diem-quyet-tam hop_le`, flag `--khong-diem-quyet-tam`. Skill tao-workspace-tu-raw (REAL data, never invent points): writes `wharton: false` + one-line notice when the spec doesn't set it. Skill xu-li-raw-forms and mau_forms_thi_clb converter ONLY remind to turn the feature off (a sổ cannot hold config; output file list is test-locked).
- du_lieu_test/NHAP_TAY.md: new Step 3 "commitment points" (table from `random.Random(112026105)`); expected result table unchanged.
- vi_du_day_du: HS024's `thu_2` pref `clb_bongro` removed (tao_bo_mau.py) so exactly one em stays trang tay; hash in tests/test_ket_qua_khong_doi.py updated; 3 more tests adjusted (csv_wp_bo_qua warning when feature OFF; clear all W cells before setting one). Truong APPROVED 01/11/2026.
- Google Form (tao-google-form-clb): NOT changed now.

## (c) Helper rule
- `tests/_wharton.py::tat_wharton(api_or_db)` writes `rules.wharton=false`. Use it per file via a LOCAL fixture `api(api)` override (or at the build point). NEVER autouse/global: tests about the new default must see the real default. Group B tests keep their asserts (data changed instead).

## (e) Traps hit
- A grep-chosen test list misses many files that run the pipeline on data without points: first "0 red" report was wrong (241 red in CI). Classify red files: A internal fixture (mask with tat_wharton) vs B shipped sample/skill output (do NOT mask; ask parent).
- soat-ma `chu_cam` does not catch English words inside Vietnamese text ("workspace"); test_giao_dien_tieng_viet_sach did. Also no "you" in EN text.
- soat-ma `kiem_nhanh.py` trung_khit must turn Wharton off in BOTH trees, else it silently compares two "blocked" runs.
- With Wharton on, only funds with >=2 clubs and no points block a run (single-club fund auto-fills 100). A student with 2 untested clubs per session (<=75 pts) loses to students with 1 club (100 pts).
- Env: pip install pytest ruff openpyxl "playwright>=1.40,<2" into system python; chromium via RBDA_TEST_CHROMIUM=/opt/pw-browsers/chromium-1243/chrome-linux64/chrome; never `playwright install`.

## Next steps
1. (f) Wait for CI (runs above) -> fix red files if any (only on parent/Truong feedback; don't loosen asserts) -> parent opens the PR.
2. (g) Later: Google Form should collect commitment points.

## Files touched (summary)
- cau_hinh_ws.py, i18n_errors.py/i18n_loi.js, comments in api_nhap.py + rbda_priority_pipeline.py; docs (HUONG_DAN_SU_DUNG, TAI_LIEU_DU_LIEU, CHANGELOG, TIEN_DO, CLAUDE_CHI_TIET tests row 168 files/3.138 cases, mau_csv + vi_du docs).
- Data/scripts: mau_csv/*, du_lieu_test/* (new them_diem_quyet_tam_vao_mau.py, NHAP_TAY.md, explicit wharton false in scripts); skills sinh-du-lieu-clb, tao-workspace-tu-raw, xu-li-raw-forms, soat-ma; mau_forms_thi_clb converter.
- ~60 test files (local `api` fixture + tat_wharton) + new tests: test_wharton_mac_dinh_bat.py, test_a13_13_kiem_nhan.py, test_giao_dien_a13_13_kiem_nhan.py.

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-01 | Sonnet | Branch + handoff created | |
| 2026-11-01 | Sonnet | Implemented A13.13, fixed tests/scripts, parent acceptance suite | see Current state |
| 2026-11-01 | Sonnet | Round 3 (group A after CI) + round 4 (group B, direction c, demo-branch merge, skills, NHAP_TAY) | handoff at ~400k tokens; final test run + ruff + soat-ma + report to parent pending |
| 2026-11-01 | Sonnet | Final handoff after round 4: 4 red tests fixed, ruff/soat-ma green, report sent to parent | context >400k; open a new session to continue |
| 2026-11-01 | Sonnet | Recorded Truong's approval in CHANGELOG; final handoff | context >400k; open a new session to continue |
| 2026-11-01 | Sonnet | Full handoff rewrite requested by parent (rule 9, context ~538k) | stop; new session continues from this file |
| 2026-11-01 | Sonnet | Handoff re-confirmed (hook fired again); nothing new done | open a new session from this file |
