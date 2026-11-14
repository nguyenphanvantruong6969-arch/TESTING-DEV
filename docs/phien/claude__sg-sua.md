# Branch handoff: claude/sg-sua

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English. Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".

## Feature / goal
Fix the 19 findings of Fable's whole-kiosk UI audit ("Soát giao diện kiosk RB-DA", 2026-11-13), most severe first.
Spec: `docs/ke_hoach/SOAT_GIAO_DIEN_KE_HOACH.md` (follow exactly; items SG-1 … SG-12). Run by three people in parallel
(A `claude/sg-a` + integrator, B `claude/sg-b`, C `claude/sg-c`; each person = one Opus lead + Sonnet coder + Sonnet checker): `docs/ke_hoach/SG_SONG_SONG.md`;
per-person state in `docs/phien/sg_song_song/STATUS_<X>.md`, overall `docs/phien/SG_STATUS.md` after integration. Base = `claude/forms-gop` (already holds FG-1…FG-9). All numbers SIMULATED.

## Plan (written by Opus; ticked by Sonnet)
- [x] Step 0: BASE = forms-gop with FG + marker blocks (commit 'SG-KH: parallel split'); L2, L3 fixed by FG-9 (Fable appendix A)
- [x] SG-1 selective club with no scores blocks the run (C3)
- [x] SG-2 default workspace no longer traps a new user (C1)
- [x] SG-3 FA rank from the original list + flag earlier FA numbers (C2)
- [x] SG-4 one student-ID matching rule (M3)
- [x] SG-5 medal questions explained; swap question only when possible (H3) — wording copied to "For Truong"
- [x] SG-6 club time and room (H1) — D1 = A
- [x] SG-7 grouped warnings everywhere (H4, M1)
- [x] SG-8 step-1 strings into i18n (M5)
- [x] SG-9 busy state + .catch wrapper for new JS (FG-4 pattern)
- [x] SG-10 free clubs: no fill percentage (M2)
- [x] SG-11 UI hygiene (M4, M6, M7, L1, L4, L5)
- [x] SG-12 plain titles in student forms (H2) — D2 = b
- [ ] Finish: kiem_nhanh 20 seeds, snapshots, soat-ma, re-run Fable's four walkthroughs

## Current state (overwrite each handoff)
- All 12 items DONE on claude/sg-a|b|c and merged into `claude/sg-sua` (HEAD d46ccc7). SG-11 split: SG-11a (A) + SG-11b (B).
- Gate results (lead A, 2026-11-14 01:10–01:55Z), all PASS except CI not yet read:
  - full suite `pytest -q -rs --cov` on code identical to d46ccc7: **6220 passed, 4 skipped** (numpy missing ×2, POSIX user, deferred V§13.12; no UI skips), coverage **93.82 %** (≥ 85), 44 min.
  - `ruff` clean; `kiem_nhanh --co-so origin/main --so-seed 20` 7/7 (60 cases identical).
  - integration checker session_01TGThn6G7hMNDrmLhcpe5Hg: PASS (`docs/phien/sg_review/INTEGRATION.md`; 674 targeted tests, browser walk SG-6+SG-10, 0 page errors).
  - walkthroughs on merged tree (script: lead's scratchpad, data outside repo): C3 run blocked with `fa_clb_tuyen_chon_chua_co_diem` {S, 8, 4} + health report; C2 HS001 rank 2 (original list), fallback HS004 NULL; C1 preview warns, run blocked with wharton on, succeeds after turning it off; H1 gio/dia_diem stored and shown. None reproduces.
  - generator diff vs BASE 98709f1 (8 modes + `--bien-the` with a variant exam; docProps/core.xml dropped): `--giu-ma` == BASE except m2/m3 (SG-5) and one sentence in `CAI_DAT_FORMS_BIEN_THE.md`; default adds MAP_*.json and plain titles in code-carrying forms (SG-12). Allowed.
  - CI *Tests (rbda-kiosk)* on d46ccc7: runs 741 (push) and 742 (pull_request of PR 17) were IN PROGRESS at 01:55Z — not read yet.
- **PR 17** (https://github.com/nguyenphanvantruong6969-arch/TESTING-DEV/pull/17) exists: DRAFT, head claude/sg-sua, base **claude/forms-gop** (wrong base), opened by another session (footer session_01YVAyu2b6DPKD2FkUm3cb7V), not by lead A. Lead A must not close/merge/edit it.
- NOT yet done: report section 4/6 filled, `docs/phien/SG_STATUS.md` gate table + line 3 `STATUS: SG GREEN`, the ONE PR claude/sg-sua → main.

## Decisions and gotchas (keep short)
- Order puts C3 before C1 (silent harm to students beats a loud block); see spec §2.
- Default `wharton: true` stays (invariant 1); SG-2 adds an exit instead.
- Fable's report artifact unreadable from this account → tests/walkthroughs from spec text.
- Merge conflicts SG-6 × SG-10 (`get_club_fill_stats`, `api_xuat` "Theo CLB" header, `js/09_the_xem.js` `veKqTheoClb`) kept both; proven by `tests/test_sg_tich_hop_tu_do_gio.py` (+ JS mutation check red→green).
- Pushing to claude/sg-sua re-triggers CI and cancels the previous push run: bundle the remaining docs into ONE final push.
- PR 17 has the wrong base; open a NEW PR to main (authorised) and list PR 17 under "Chờ Truong" for Truong to close.

## Next steps (ordered)
1. Read CI result of d46ccc7 (`mcp__github__actions_list` list_workflow_runs, workflow tests.yml, branch claude/sg-sua). Red → fix loop per SG_SONG_SONG.md 2.6 step 4 (coder session, max 3) else `SG RED`.
2. Fill `docs/phien/bao_cao_dem/2026-11-14_sg_sua.md` §4/§6 with the gate results above + CI line; add item 9 under §5: "PR 17 (draft, base claude/forms-gop, other session) — please close".
3. `docs/phien/SG_STATUS.md`: fill the Gate table from "Current state", line 3 → `STATUS: SG GREEN`, append Log line. Tick Plan "Finish" here.
4. ONE commit + push (git pull --rebase first).
5. Open ONE PR claude/sg-sua → main (body: FG-1…FG-9 + SG-1…SG-12, test counts 293 files / 6224 cases / 178 new, "SIMULATED data", "run the Windows build only after merge", PR 17 note; footer per system rules). Never merge it.
6. Last message: report link + PR link.

## Files touched
- docs/ke_hoach/SOAT_GIAO_DIEN_KE_HOACH.md, SG_VONG_LAP.md, SG_SONG_SONG.md: spec + runbooks
- Items: see CHANGELOG.md top entry (2026-11-14 SG-1 … SG-12) and docs/ke_hoach/sg_song_song/MANH_*.md
- Integration: api_bao_cao.py, api_xuat.py, js/09_the_xem.js, i18n_loi.js (regenerated), tests/test_sg_tich_hop_tu_do_gio.py
- Docs: CHANGELOG.md, docs/ke_hoach/TIEN_DO.md, docs/ke_hoach/CLAUDE_CHI_TIET.md (293 test files), docs/phien/SG_STATUS.md, docs/phien/bao_cao_dem/2026-11-14_sg_sua.md (draft)

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-13 | Opus (forms-gop session) | Read Fable report, re-checked C1/C2/C3/H1 in code, wrote spec + this handoff | plan only |
| 2026-11-13 | Opus (forms-gop session) | Truong approved D1–D3; wrote three-role runbook SG_VONG_LAP.md | plan only |
| 2026-11-13 | Opus (forms-gop session) | Truong chose a 3-way parallel split; wrote SG_SONG_SONG.md, added marker blocks | no behaviour change |
| 2026-11-13 | Opus (forms-gop session) | Truong: each person = 1 Opus lead managing a Sonnet coder + a Sonnet checker; SG_SONG_SONG.md rewritten | plan only |
| 2026-11-14 | Opus (lead A) | Persons A, B, C done; merged sg-c and sg-b into claude/sg-sua; folded MANH_* into CHANGELOG/TIEN_DO; test count 293 | gate next |
| 2026-11-14 | Opus (lead A) | Gate run: full suite 6220 passed / 93.82 % cov, ruff, kiem_nhanh 7/7, integration checker PASS, walkthroughs, generator diff; found PR 17 (wrong base, other session). Handoff at ~400k context | next: CI read, docs, PR to main |
