# Branch handoff: claude/keen-ride-72sa7t

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English (cheaper in tokens). Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".
> File name = branch name with "/" replaced by "__" (see `.claude/hooks/handoff_khi_day_ngu_canh.py`).
> Night-run protocol: `docs/phien/CHAY_DEM_FA_DAA.md`. Spec: `docs/ke_hoach/FA_DAA_KE_HOACH.md`.

## Feature / goal
Implement Truong's FA-DAA vision (`docs/ke_hoach/FA_DAA_VISION.md`, 2026-11-08) for real use THIS term at a school of
500-1000 students on the Microsoft ecosystem: club types FREE / LIMITED / SELECTIVE, three medals per day (60/30/10,
one fund) replacing the two-fund determination points, pass mark for SELECTIVE, reserved seats, minimum members,
fallback to FREE clubs, a reason for every result, demand table for teachers, public lottery seed. Kiosk first
(no change to the DA core: wrapper `fa_daa.py`), then Microsoft Forms / Power Apps (T4M-NC track).
Parent registry items: A13 (FA-DAA), A5, A6, C3, Z6, A2; Microsoft part under T4M-NC.

## Plan (written by Opus; ticked by Sonnet)
Night 1 — kiosk backend (order fixed; dependencies in CHAY_DEM_FA_DAA.md C.5):
- [x] FA-0 baseline: venv, invariant-1 tests, ruff; record counts here
- [x] FA-1 data model: `rules.fa_daa`, club columns loai/diem_san/so_toi_thieu/suc_chua_phong, table `giu_cho`, Sổ nhập/CSV optional columns
- [x] FA-2 precheck `kiem_truoc_fa`
- [x] FA-3 medals one fund: `kiem_ho_so_huy_chuong`, `diem_huy_chuong_hieu_luc`
- [x] FA-4 wrapper `chay_fa_daa`: FREE unbounded, SELECTIVE filter, reserved via soft reserve, fallback, groups (`fa_nhom`)
- [x] FA-5 minimum members closure loop (one club per iteration, D3)
- [x] FA-6 reasons/cut-offs/waitlist (`fa_ly_do`, `ket_qua_ly_do.csv`, `fa_ly_do.py` templates)
- [x] FA-7 demand table + `so_sanh_suc_chua.py`
- [x] FA-8 property tests V§13 (`tests/test_fa_tinh_chat.py`)
Later (NOT night 1):
- [x] FA-9 witnessed lottery record (D5)  - [x] FA-10 simulation compare (+ D1 two-term incentive behaviour)
- [x] FA-M3 part: `dat_huy_chuong_duong_b` + `tests/test_fa_m3_huy_chuong_b.py` (Opus, Truong asked 08/11; not yet wired)
Night 2 — Microsoft (released by Opus 2026-11-09; order and dependencies in CHAY_DEM_FA_DAA.md C.5; all TH):
- [x] FA-M1 club setup form guide + converter `chuyen_phieu_clb.py`
- [x] FA-M2 path B registration Forms (`--fa-daa` in `tao_mau_forms.py` / `bieu_mau.py`)
- [x] FA-M3 converter FA mode (`--fa-daa`), wires `dat_huy_chuong_duong_b` (needs FA-M1, FA-M2)
- [x] FA-M4 quiz variants + item analysis + D11 equating `phan_tich_cau_hoi.py` (needs FA-M3)
- [x] FA-M5 Power Apps spec v2 (path A) + `bo_dung_t4m` columns (needs FA-M3)
- [x] FA-M6 after-allocation docs `FA_SAU_XEP.md` (needs FA-M5)
- [x] Opus review night 1 (2026-11-09: GO; report bao_cao_dem/2026-11-09_soat_dem1.md)
- [x] Opus review night 2 (2026-11-09: GO with fix list; report bao_cao_dem/2026-11-09_soat_dem2.md; nothing fixed, Truong's instruction)
Night 3 — fixes then kiosk screens (released by Opus 2026-11-09; spec plan §6; order in CHAY_DEM_FA_DAA.md C.5):
- [x] FA-S7 export reasons of the latest run only   - [x] FA-S8 CSV import keeps row when FA off   - [x] FA-S9 rollback test fa_nhom/fa_ly_do
- [x] FA-S3 D11 small comparison group -> no shift   - [x] FA-S1 retake counts only when flagged + retake variant
- [x] FA-S2 --bo-cau per variant   - [x] FA-S4 warn on unreadable quiz times   - [x] FA-S5 warn on wrong variant
- [x] FA-S6 generator reads Loại (--so-nhap-clb)   - [x] FA-S11 email <-> student_id join for KetQua   - [x] FA-S10 plan §4 D8 row
- [x] FA-UI-1 FA switch   - [x] FA-UI-2 club columns   - [x] FA-UI-3 medal step   - [x] FA-UI-4 reasons + exports   - [x] FA-UI-5 user guide
- [x] Opus review night 3 (2026-11-09: GO; 2 new bugs + 2 small items listed as FA-N1..N4, not fixed; report bao_cao_dem/2026-11-09_soat_dem3.md)
Night 4 — review fixes, lottery record, simulation (released by Opus 2026-11-09; spec plan §7, FA-9/FA-10 in §2):
- [x] FA-N1 reasons per day after a partial run   - [x] FA-N2 on-site lazy medals saved + follow re-rank
- [x] FA-N3 clear error FA on / points off   - [x] FA-N4 warn: single-variant club, no retake
- [x] FA-9 witnessed lottery record   - [x] FA-10 simulation compare (+ D1 two-term behaviour, tables only)
- [x] Opus review night 4 (2026-11-10: GO; 1 bug FA-O1 + 1 test gap listed, not fixed; report bao_cao_dem/2026-11-10_soat_dem4.md)
Night 5 — fix list + Excel lottery record (released 2026-11-10; spec plan §8; protocol CHAY_DEM_FA_DAA.md, night-5 version):
- [ ] FA-O1 reasons sorted by day order (THU_TU_BUOI, chu_nhat last)   - [ ] FA-9b Excel version of the lottery record (Truong approved)
- [ ] Opus review night 5
- [ ] DEFERRED to term 2: D1 compensation credit — needs FA-10 incentive measurement + Truong's exception to invariant 2

## Current state (overwrite each handoff)
- RUNNING: 2026-11-10 02:55Z sonnet-night-5 (manual, Truong asked)
- 2026-11-10 night 4 REVIEWED (Sonnet session run by hand, not Opus; Truong asked): GO. 1 bug FA-O1 (reasons sorted as plain strings, `chu_nhat` before `thu_2`) rated `trung` by judgement + test gap FA-O2. Night 5 released = FA-O1 + FA-9b.
- Tests: 2276 passed / 1 skipped / 0 failed (related, non-UI); Chromium 7 passed; kiem_nhanh 7/7; ruff clean. No code changed in this review.
- The two scheduled tasks ("FA-DAA vong soat" Opus, "FA-DAA vong sua" Sonnet) fired but their fresh sessions had NO repo (empty /home/user) and stopped without writing. They need the repo + branch attached as source in the routines UI (create_trigger has no source field). Until then night 5 must be started by hand.
- Next: Sonnet night 5 per `docs/phien/CHAY_DEM_FA_DAA.md`; then Opus review night 5. PR to main only after night 5 (Truong). D8 waits for GĐ2.

## Decisions and gotchas (keep short)
- D1..D12: table in plan §1 (revised by the council 08/11); night run uses the Default column.
- Truong 08/11: invariant-2 EXCEPTION approved for D2 (default medals from rank, only with override; in CLAUDE.md). D11 never blocks: sample-size threshold + mean equating, admin confirms. D1 stays deferred; FA-10 two-term simulation required before term 2.
- D1 compensation deferred: NOT a stability problem; the issue is the cross-term incentive (lose NV1 on purpose), which invariant 2 guards. Simulate before term 2.
- D3 close the club with the largest shortfall first. D4 waitlist SELECTIVE score>medal>STB, LIMITED medal>STB, only students ranking it above their club.
- D2 default medals from rank only at the registration layer (Power Apps, converter, kiosk on-site entry screen) and only with an override; the priority key never reads rank (CLAUDE.md invariant-2 exception).
- D5 no public seed (24/10 decision stands); FA-9 = witnessed lottery record. D9 Forms time limit + flag < 1/3 median. D11 never blocks (sample-size threshold + mean equating, admin confirms). D12 path B: 3 choice questions, no Ranking, medals by order + gold and silver/bronze-swap questions (all 6 placements).
- Registry A13 already titled "FA-DAA": medals reuse `wharton_bids` and the `diem_wharton` input of `run_rbda`.
- Gotchas: test-file count in CLAUDE_CHI_TIET.md; False rule keys omitted from fingerprint; sanity needs augmented lists.

## Next steps (ordered)
1. Night 5 implementer (Sonnet): `docs/phien/CHAY_DEM_FA_DAA.md` (night-5 version; night 4 is done). Truong was given a scheduled-task prompt "FA-DAA chay dem 4" (CRON_TZ=Asia/Ho_Chi_Minh 13 23,1,3 * * *, fresh Sonnet session per firing, self-disables when done) for his collaborator; this session created no task.
2. Truong: OK to open a PR to main for the full CI suite + Windows build? GĐ2 -> D8. Night-3 questions: defaults in the night-3 review.
3. Opus: review night 4 (auto task "FA-DAA soat dem 4" may do it): only when night 4 is finished (no RUNNING < 3 h, every night-4 item ticked or BLOCKED). Same method as bao_cao_dem/2026-11-09_soat_dem3.md: list bugs, do NOT fix; write bao_cao_dem/<date>_soat_dem4.md; plan §8 'Night 5' = that fix list only (no new features without Truong); turn CHAY_DEM_FA_DAA.md into the night-5 version; add Night 5 items to this Plan (or 'Night 5: nothing to do'); tick 'Opus review night 4'.
4. Sonnet night 5 (auto task "FA-DAA chay dem 5"): runs only after step 3 released night 5.
5. LOOP (supersedes the two tasks above if the collaborator creates it): "FA-DAA vong soat" (Opus, CRON_TZ=Asia/Ho_Chi_Minh 43 */2 * * *) reviews the latest finished night N and releases night N+1 = fix list only; "FA-DAA vong sua" (Sonnet, 13 1-23/2 * * *) runs the released night. Stops with "LOOP DONE: <reason>" in Current state when no trung/cao bug, N+1 > 8, or a fixed bug returns twice; then both tasks are disabled. Fixes only: no new features, invariants, D-decisions or scope changes without Truong. Prompt text was given to Truong in chat; no task created by this session.

## Files touched
- docs/ke_hoach/FA_DAA_VISION.md: Truong's vision, copied verbatim into the repo
- docs/ke_hoach/FA_DAA_KE_HOACH.md: implementation plan and item specs
- docs/phien/CHAY_DEM_FA_DAA.md: single entry file for the night run
- docs/phien/claude__keen-ride-72sa7t.md: this handoff
- CHANGELOG.md, docs/ke_hoach/TIEN_DO.md: FA-KH planning entry + FA-1..FA-8 entries
- Code (night 1): fa_daa.py, fa_ly_do.py, mau_forms_thi_clb/so_sanh_suc_chua.py; edits in api.py, api_nhap.py, api_quan_ly.py, api_xuat.py, cau_hinh_ws.py, rbda_priority_pipeline.py, so_nhap.py, i18n_errors.py (+ i18n_loi.js); tests/test_fa_*.py and tests/_fa.py

- docs/phien/bao_cao_dem/2026-11-09_soat_dem2.md, 2026-11-09_soat_dem3.md: Opus reviews of nights 2 and 3 (fix lists)
- docs/ke_hoach/FA_DAA_KE_HOACH.md §6, §7: night-3 and night-4 specs

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-08 | Opus | Read vision + code (priority, wharton, STB, registry A5/A6/A13/C3, T4M); wrote plan, night-run file, handoff | No code changed; D1 blocked; D8 waits for GĐ2 |
| 2026-11-08 | Opus | Council review applied: D1 reason, D3, D4, D5->FA-9 record, D9, D11, D12 | Docs only |
| 2026-11-08 | Opus | Truong decisions: D2 invariant-2 exception (CLAUDE.md), path B gold-override question, D11 no-block equating, D1 deferred | Docs + CLAUDE.md only |
| 2026-11-08 | Opus | Truong: path B second medal question (swap silver/bronze); built `dat_huy_chuong_duong_b`, tests first (19 red -> green), mutation caught 8/19 | Converter only; not wired; no kiosk/schema/CSV change |
| 2026-11-09 | Sonnet | FA-0: venv OK; baseline TestTrungKhit 7 passed, test_wharton_pipeline 29 passed, ruff clean | night 1 start |
| 2026-11-09 | Sonnet | FA-1: rules.fa_daa, 4 club cols, giu_cho, So nhap/CSV optional cols; tests/test_fa_du_lieu.py (43), related 1673 passed, kiem_nhanh 7/7, mutation caught | di_tru ALTER runs after the rebuild step (single backup) |
| 2026-11-09 | Sonnet | FA-2: kiem_truoc_fa + hooks (pipeline, health); tests/test_fa_kiem_truoc.py (15); related 1823 passed (+1 expected count test, fixed); mutation caught | kiểu CLB helpers moved into so_nhap.py (standalone skill) |
| 2026-11-09 | Sonnet | FA-3: huy chuong one fund + submit_huy_chuong + pipeline validation; tests/test_fa_huy_chuong.py (20); related 1992 passed; mutation caught (after adding invalid-value cases) | pipeline passes huy chuong as diem_wharton until FA-4 wrapper |
| 2026-11-09 | Sonnet | FA-4..FA-8 (one commit, overlapping files): chay_fa_daa, minimum-members loop, fa_ly_do, demand table + so_sanh_suc_chua.py, property tests; related 4077 passed (+2 fixed: doc code map, COLLATE THU_TU_BUOI); mutations caught for every item | tests/test_fa_{chay,toi_thieu,ly_do,nhu_cau,tinh_chat}.py |
| 2026-11-09 | Sonnet | Night report 2026-11-09: 9/9 done, 0 blocked; report in docs/phien/bao_cao_dem/2026-11-09.md | RUNNING line removed |
| 2026-11-09 | Opus | Review night 1: GO. Non-UI tests 4981/1 fail/4 skip; fixed `test_van_phong_tu_nhien` (DAA acronym, f9b9031); invariant 1 3x20x2 identical; mutations 5/5; released night 2 in CHAY_DEM_FA_DAA.md | report bao_cao_dem/2026-11-09_soat_dem1.md; RUNNING line removed |
| 2026-11-09 | Sonnet | FA-M1: chuyen_phieu_clb.py + PHIEU_THIET_LAP_CLB.md; tests/test_fa_m1_phieu_clb.py 17; related 201 passed; mutation caught; kiem_nhanh 7/7 | night 2 |
| 2026-11-09 | Sonnet | FA-M2: bieu_mau.cac_phan_fa + tao_mau_forms --fa-daa; tests/test_fa_m2_forms_dang_ky.py 10 (mutation caught after adding the >3-clubs case); related 263 passed; old modes byte-identical (diff -r); mutation caught; kiem_nhanh 7/7 | night 2 |
| 2026-11-09 | Sonnet | FA-M3: chuyen_fa_daa (+doc_lists fa, doc_dang_ky_fa_forms, quy_diem_10, co_nhanh_qua); tests/test_fa_m3_chuyen.py 25; related 266 passed; default-mode cells identical; 3 mutations caught; kiem_nhanh 7/7 | night 2 |
| 2026-11-09 | Sonnet | FA-M4: phan_tich_cau_hoi.py + tao_mau_forms --bien-the + converter gate (D11); tests/test_fa_m4_phan_tich.py 24; related 330 passed; old modes identical; 5 mutations caught; kiem_nhanh 7/7 | night 2 |
| 2026-11-09 | Sonnet | FA-M5: T4M_DAC_TA_SUA_APP §12 (R39-R54) + bo_dung_t4m ECA_FA + tao_bo_dung_t4m --fa-daa; tests/test_fa_m5_bo_dung.py 10; related 208 passed (after scoping old R1..R38 test); default kit byte-identical; 2 mutations caught; kiem_nhanh 7/7 | night 2 |
| 2026-11-09 | Sonnet | FA-M6: docs/he_sinh_thai/FA_SAU_XEP.md (docs only) + tests/test_fa_m6_tai_lieu.py 6; related passed; 2 mutations caught; kiem_nhanh 7/7 | night 2 |
| 2026-11-09 | Sonnet | Night 2 report 2026-11-09: 6/6 done, 0 blocked; report in docs/phien/bao_cao_dem/2026-11-09_dem2.md | RUNNING line removed |
| 2026-11-09 | Opus | Reviewed night 2: GO; 6 new bugs + 4 open night-1 findings + 1 email gap listed as FA-S1..S11 (not fixed, Truong's instruction); wrote plan §6 and night-3 protocol | Repro: FA-S3, FA-S4; 197 related tests pass |
| 2026-11-09 | Opus (night 3, Truong asked) | FA-S8: CSV club import keeps the row when FA is off; red first, mutation caught | related tests 2304 passed |
| 2026-11-09 | Opus (night 3) | FA-S7 export latest run only + FA-S9 rollback test; red first; mutations caught (S9: commit before lock -> red) | kiem_nhanh 7/7 |
| 2026-11-09 | Opus (night 3) | FA-S3: N_NHO when either side small; 1 old expectation changed per spec | test_fa_m4 25 passed |
| 2026-11-09 | Opus (night 3) | FA-S1 retake rule; red first; 2 mutations caught; converter/T4M tests 252 passed | default mode path unchanged (fa=False branch identical) |
| 2026-11-09 | Opus (night 3) | FA-S5 wrong-variant warning; red first; mutation caught (2 tests) | converter tests green |
| 2026-11-09 | Opus (night 3) | FA-S2 --bo-cau per variant; red first; mutation caught | 91 passed (fa_m2/m3/m4, mau_forms) |
| 2026-11-09 | Opus (night 3) | FA-S4 unreadable quiz times warning; red first; mutation caught | test_fa_m3/m4 green |
| 2026-11-09 | Opus (night 3) | FA-S6 generator reads club type; red first; mutation caught; without flag diff -r identical | tao_mau_forms tests 241 passed |
| 2026-11-09 | Opus (night 3) | FA-S11 email join script + EMAIL_MA_HS.csv; red first; mutation caught; new test file (count 217) | kiem_nhanh 7/7 |
| 2026-11-09 | Opus (night 3) | FA-S10 plan §4 D8 path-B row fixed | docs only |
| 2026-11-09 | Opus (night 3) | FA-UI-1 FA switch in workspace wizard; red first (5/5); mutation caught; ws/wharton UI tests 341 passed after fixing 'em' wording | Chromium really ran |
| 2026-11-09 | Opus (night 3) | FA-UI-2 club table FA columns; red first; mutation caught; related 2334 passed / 1 skipped | Chromium really ran |
| 2026-11-09 | Opus (night 3) | FA-UI-3 medal step; red first (4/5); swap mutation caught; related 2704 passed / 1 skipped after wording fix | Chromium really ran |
| 2026-11-09 | Opus (night 3) | FA-UI-4 reasons column + 2 export buttons; red first; mutation caught; related 2526 passed / 1 skipped | Chromium really ran |
| 2026-11-09 | Opus (night 3) | FA-UI-5 user guide section 15; doc test red first | guide tests 92 passed, kiem_nhanh 7/7 |
| 2026-11-09 | Opus (night 3) | Night 3 report 2026-11-09: 16/16 done, 0 blocked; report in docs/phien/bao_cao_dem/2026-11-09_dem3.md | RUNNING line removed |
| 2026-11-09 | Opus | Reviewed night 3: GO; repro FA-N1 (partial run drops other days' reasons) and FA-N2 (on-site lazy path saves no medals); kiem_nhanh 7/7; wrote plan §7 and night-4 protocol | UI tests not rerun (playwright install did not finish) |
| 2026-11-09 | Opus | Handoff at ~400k context (Stop hook): rewrote Current state; night 4 released, not started | Next session: Read CLAUDE.md + this file |
| 2026-11-09 | Opus | Gave Truong a night-4 schedule prompt (23:13/01:13/03:13 VN); no new work (context over limit) | Report may be named 2026-11-09_dem4.md or 2026-11-10_dem4.md |
| 2026-11-09 | Opus | Night 4 running on collaborator side; wrote chained auto plan (Opus review night 4 -> Sonnet night 5) in Next steps | No task created by this session |
| 2026-11-09 | Opus | Gave Truong a self-review/self-fix loop prompt (two recurring tasks, stop rules in Next steps 5); no new work | Context over limit |
| 2026-11-09 | Opus | Answered vision coverage (projected after night 5: P1 ~90 %, P2 ~95 %, P3 ~30-40 %, overall ~75-80 %; gaps: real Microsoft test/D8, full CI + Windows build, P3 features, admin dashboard §11). No night-4 commits on this branch yet at 2026-11-09 ~23:00 | No new work |
| 2026-11-09 | Opus | Answered: Forms yes (setup form, quizzes, surveys); Power Apps vs Forms-only registration = D8 open; NOT everything in M365 (kiosk + converters run offline on the IT Windows PC, files moved by Excel/CSV) | No new work |
| 2026-11-09 | Sonnet (night 4) | FA-N1: per-day latest run reasons + warning; tests/test_fa_n1_ly_do_mot_phan.py 3 (red first); related 1955 passed/1 skipped; mutation caught; kiem_nhanh 7/7 | night 4 |
| 2026-11-09 | Sonnet (night 4) | FA-N2: on-site lazy medals saved + follow re-rank (js hcTheoNguyenVong); tests/test_giao_dien_fa_n2_luu_mac_dinh.py 3 Chromium red first; related UI 63 passed; mutation caught; kiem_nhanh 7/7 | night 4 |
| 2026-11-09 | Sonnet (night 4) | FA-N3: fa_can_diem_quyet_tam error code; tests/test_fa_n3_loi_diem_quyet_tam.py 5 red first; related fa+ws 2423 passed (1 count test fixed); mutation caught; kiem_nhanh 7/7 | night 4 |
| 2026-11-09 | Sonnet (night 4) | FA-N4: single-variant club retake warning + guide line; tests/test_fa_n4_mot_de_khong_thi_lai.py 3 red first; converter/forms tests 129 passed; mutation caught; kiem_nhanh 7/7 | night 4 |
| 2026-11-09 | Sonnet (night 4) | FA-9: fa_bien_ban.py + export_bien_ban_boc_tham + button; tests/test_fa_bien_ban.py 9 + 1 Chromium; related 112 passed; 2 mutations caught; kiem_nhanh 7/7; pure module written before its tests, API/UI tests red first | night 4 |
| 2026-11-09 | Sonnet (night 4) | FA-10: du_lieu_test/mo_phong_fa_daa.py tables only; tests/test_mo_phong_fa_daa.py 9; 3 mutations caught after adding 2 tests; module written before tests | night 4 |
| 2026-11-09 | Sonnet (night 4) | Night 4 report 2026-11-09: 6/6 done, 0 blocked; report in docs/phien/bao_cao_dem/2026-11-09_dem4.md | RUNNING line removed |
| 2026-11-10 | Opus | Status check; recorded Truong decisions (auto review, PR after night 5, D8 waits, Excel lottery record approved); ticked FA-9/FA-10 in Plan | Docs only |
| 2026-11-10 | Sonnet (review, by hand) | Reviewed night 4: GO; repro FA-O1 (reason rows sort `chu_nhat` before `thu_2`); biên bản after partial run OK; related 2276 passed, Chromium 7, kiem_nhanh 7/7; wrote plan §8 and night-5 protocol; scheduled tasks found sourceless | Docs only; report bao_cao_dem/2026-11-10_soat_dem4.md |
