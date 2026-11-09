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
- [ ] FA-2 precheck `kiem_truoc_fa`
- [ ] FA-3 medals one fund: `kiem_ho_so_huy_chuong`, `diem_huy_chuong_hieu_luc`
- [ ] FA-4 wrapper `chay_fa_daa`: FREE unbounded, SELECTIVE filter, reserved via soft reserve, fallback, groups (`fa_nhom`)
- [ ] FA-5 minimum members closure loop (one club per iteration, D3)
- [ ] FA-6 reasons/cut-offs/waitlist (`fa_ly_do`, `ket_qua_ly_do.csv`, `fa_ly_do.py` templates)
- [ ] FA-7 demand table + `so_sanh_suc_chua.py`
- [ ] FA-8 property tests V§13 (`tests/test_fa_tinh_chat.py`)
Later (NOT night 1):
- [ ] FA-9 witnessed lottery record (D5)  - [ ] FA-10 simulation compare (+ D1 two-term incentive behaviour)
- [x] FA-M3 part: `dat_huy_chuong_duong_b` + `tests/test_fa_m3_huy_chuong_b.py` (Opus, Truong asked 08/11; not yet wired)
- [ ] Night 2 Microsoft: FA-M1 setup form, FA-M2 Forms registration (path B), FA-M3 converter, FA-M4 quiz variants + item analysis, FA-M5 Power Apps spec v2 (path A), FA-M6 after-allocation docs
- [ ] Night 3: FA-UI kiosk screens (Chromium tests)
- [ ] Opus review of each night before the next night starts
- [ ] DEFERRED to term 2: D1 compensation credit — needs FA-10 incentive measurement + Truong's exception to invariant 2

## Current state (overwrite each handoff)
- 2026-11-08 Opus: plan written and pushed; no product code changed yet. Nothing running.
- RUNNING: 2026-11-09T02:08Z session_01VfPzNuHreMmsU2dsJPAz6x (night 1)
- Tests: not run on this branch yet (container had no .venv). Baseline is FA-0.
- Open problems: D8 (Power Apps vs Forms registration) waits for Truong's GĐ2 meeting with IT (before 15/11).

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
1. Night 1 implementer (Sonnet): follow `docs/phien/CHAY_DEM_FA_DAA.md`.
2. Opus: review night 1 diff (related tests, ruff, kiem_nhanh, invariant-1 byte identity), then release night 2.
3. Truong: GĐ2 meeting -> decide D8; confirm or change D1..D10.

## Files touched
- docs/ke_hoach/FA_DAA_VISION.md: Truong's vision, copied verbatim into the repo
- docs/ke_hoach/FA_DAA_KE_HOACH.md: implementation plan and item specs
- docs/phien/CHAY_DEM_FA_DAA.md: single entry file for the night run
- docs/phien/claude__keen-ride-72sa7t.md: this handoff
- CHANGELOG.md, docs/ke_hoach/TIEN_DO.md: FA-KH planning entry

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-08 | Opus | Read vision + code (priority, wharton, STB, registry A5/A6/A13/C3, T4M); wrote plan, night-run file, handoff | No code changed; D1 blocked; D8 waits for GĐ2 |
| 2026-11-08 | Opus | Council review applied: D1 reason, D3, D4, D5->FA-9 record, D9, D11, D12 | Docs only |
| 2026-11-08 | Opus | Truong decisions: D2 invariant-2 exception (CLAUDE.md), path B gold-override question, D11 no-block equating, D1 deferred | Docs + CLAUDE.md only |
| 2026-11-08 | Opus | Truong: path B second medal question (swap silver/bronze); built `dat_huy_chuong_duong_b`, tests first (19 red -> green), mutation caught 8/19 | Converter only; not wired; no kiosk/schema/CSV change |
| 2026-11-09 | Sonnet | FA-0: venv OK; baseline TestTrungKhit 7 passed, test_wharton_pipeline 29 passed, ruff clean | night 1 start |
| 2026-11-09 | Sonnet | FA-1: rules.fa_daa, 4 club cols, giu_cho, So nhap/CSV optional cols; tests/test_fa_du_lieu.py (43), related 1673 passed, kiem_nhanh 7/7, mutation caught | di_tru ALTER runs after the rebuild step (single backup) |
