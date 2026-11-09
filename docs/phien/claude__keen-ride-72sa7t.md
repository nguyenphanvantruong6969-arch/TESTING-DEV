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
- [ ] FA-9 witnessed lottery record (D5)  - [ ] FA-10 simulation compare (+ D1 two-term incentive behaviour)
- [x] FA-M3 part: `dat_huy_chuong_duong_b` + `tests/test_fa_m3_huy_chuong_b.py` (Opus, Truong asked 08/11; not yet wired)
Night 2 — Microsoft (released by Opus 2026-11-09; order and dependencies in CHAY_DEM_FA_DAA.md C.5; all TH):
- [x] FA-M1 club setup form guide + converter `chuyen_phieu_clb.py`
- [x] FA-M2 path B registration Forms (`--fa-daa` in `tao_mau_forms.py` / `bieu_mau.py`)
- [x] FA-M3 converter FA mode (`--fa-daa`), wires `dat_huy_chuong_duong_b` (needs FA-M1, FA-M2)
- [x] FA-M4 quiz variants + item analysis + D11 equating `phan_tich_cau_hoi.py` (needs FA-M3)
- [x] FA-M5 Power Apps spec v2 (path A) + `bo_dung_t4m` columns (needs FA-M3)
- [x] FA-M6 after-allocation docs `FA_SAU_XEP.md` (needs FA-M5)
- [ ] Night 3: FA-UI kiosk screens (Chromium tests)
- [x] Opus review night 1 (2026-11-09: GO; report bao_cao_dem/2026-11-09_soat_dem1.md)
- [ ] Opus review night 2, night 3 before the next night starts
- [ ] DEFERRED to term 2: D1 compensation credit — needs FA-10 incentive measurement + Truong's exception to invariant 2

## Current state (overwrite each handoff)
- 2026-11-09 night 2 (Sonnet): FA-M1..FA-M6 all DONE, 0 BLOCKED, all Microsoft parts TH (untested on real Microsoft). RUNNING lock removed. D8 still OPEN.
- Commits: FA-M1 bfdc371; FA-M2 1efa8d1 + cde4384; FA-M3 7c48eae; FA-M4 a61d703; FA-M5 cd1fe46; FA-M6 58bc370. Report: bao_cao_dem/2026-11-09_dem2.md.
- Tests: 6 new files (17+10+25+24+10+6 = 92 cases), each red first. Final run (all test_fa_*, mau forms, test_t4m_*, test_so_nhap, 2 doc tests): 2204 passed, 1 skipped. ruff clean, kiem_nhanh 7/7. UI/Chromium and full suite NOT run (CI).
- Old modes unchanged: --chi-thi/--moi-clb output and T4M kit byte-identical (diff -r); default converter cell contents identical. One old test edited (R1..R38 count). No kiosk code touched.
- Design notes: converter FA = `chuyen_forms_sang_phan_mem.py --fa-daa --so-nhap-clb <FA-M1 sheet> (--dang-ky FORMS.. | --lists CSV) [quiz..] [--bien-the-tep F=B] [--ap-dung-dieu-chinh|--giu-diem-goc] [--bo-cau club-k]`; D11 gap without a flag -> report + exit 3, never blocks. DRAFT rows dropped (flag --nhan-ban-nhap). Variants: `de_thi_bien_the` in de_thi.json; guide in CAI_DAT_FORMS_BIEN_THE.md (separate file, deviates from the plan row).
- Open for Truong: D8; DRAFT default; KetQua list read access; whether night 3 adds attendance/appeal/round-2 to the kiosk; the 2 night-1 review findings (see report).

## Decisions and gotchas (keep short)
- D1..D12: table in plan §1 (revised by the council 08/11); night run uses the Default column.
- Truong 08/11: invariant-2 EXCEPTION approved for D2 (default medals from rank, only with override; in CLAUDE.md). D11 never blocks: sample-size threshold + mean equating, admin confirms. D1 stays deferred; FA-10 two-term simulation required before term 2.
- D1 compensation deferred: NOT a stability problem; the issue is the cross-term incentive (lose NV1 on purpose), which invariant 2 guards. Simulate before term 2.
- D3 close the club with the largest shortfall first. D4 waitlist SELECTIVE score>medal>STB, LIMITED medal>STB, only students ranking it above their club.
- D2 default medals only at the registration layer (Power Apps / converter), never inside the kiosk.
- D5 no public seed (24/10 decision stands); FA-9 = witnessed lottery record. D9 Forms time limit + flag < 1/3 median. D11 variant mean gap > 1 blocks. D12 path B: 3 choice questions, no Ranking, medals by order.
- Registry A13 already titled "FA-DAA": medals reuse `wharton_bids` and the `diem_wharton` input of `run_rbda`.
- Gotchas: test-file count in CLAUDE_CHI_TIET.md; False rule keys omitted from fingerprint; sanity needs augmented lists.

## Next steps (ordered)
1. Opus: review night 2 (esp. FA-M3/FA-M4 converter wiring), then release night 3 (FA-UI, Chromium tests).
2. Sonnet night 3: FA-UI after the Opus release.
3. Truong: GĐ2 meeting -> decide D8; answer night-1 questions; decide whether to fix review findings 1-2.

## Files touched
- docs/ke_hoach/FA_DAA_VISION.md: Truong's vision, copied verbatim into the repo
- docs/ke_hoach/FA_DAA_KE_HOACH.md: implementation plan and item specs
- docs/phien/CHAY_DEM_FA_DAA.md: single entry file for the night run
- docs/phien/claude__keen-ride-72sa7t.md: this handoff
- CHANGELOG.md, docs/ke_hoach/TIEN_DO.md: FA-KH planning entry + FA-1..FA-8 entries
- Code (night 1): fa_daa.py, fa_ly_do.py, mau_forms_thi_clb/so_sanh_suc_chua.py; edits in api.py, api_nhap.py, api_quan_ly.py, api_xuat.py, cau_hinh_ws.py, rbda_priority_pipeline.py, so_nhap.py, i18n_errors.py (+ i18n_loi.js); tests/test_fa_*.py and tests/_fa.py

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
