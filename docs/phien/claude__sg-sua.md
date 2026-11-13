# Branch handoff: claude/sg-sua

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English. Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".

## Feature / goal
Fix the 19 findings of Fable's whole-kiosk UI audit ("Soát giao diện kiosk RB-DA", 2026-11-13), most severe first.
Spec: `docs/ke_hoach/SOAT_GIAO_DIEN_KE_HOACH.md` (follow exactly; items SG-1 … SG-12). Run by three people in parallel
(A `claude/sg-a` Opus + integrator, B `claude/sg-b`, C `claude/sg-c` Sonnet): `docs/ke_hoach/SG_SONG_SONG.md`;
per-person state in `docs/phien/sg_song_song/STATUS_<X>.md`, overall `docs/phien/SG_STATUS.md` after integration. Base = `claude/forms-gop` (already holds FG-1…FG-9). All numbers SIMULATED.

## Plan (written by Opus; ticked by Sonnet)
- [x] Step 0: BASE = forms-gop with FG + marker blocks (commit 'SG-KH: parallel split'); L2, L3 fixed by FG-9 (Fable appendix A)
- [ ] SG-1 selective club with no scores blocks the run (C3)
- [ ] SG-2 default workspace no longer traps a new user (C1)
- [ ] SG-3 FA rank from the original list + flag earlier FA numbers (C2)
- [ ] SG-4 one student-ID matching rule (M3)
- [ ] SG-5 medal questions explained; swap question only when possible (H3) — wording copied to "For Truong"
- [ ] SG-6 club time and room (H1) — D1 = A
- [ ] SG-7 grouped warnings everywhere (H4, M1)
- [ ] SG-8 step-1 strings into i18n (M5)
- [ ] SG-9 busy state + .catch wrapper for new JS (FG-4 pattern)
- [ ] SG-10 free clubs: no fill percentage (M2)
- [ ] SG-11 UI hygiene (M4, M6, M7, L1, L4, L5)
- [ ] SG-12 plain titles in student forms (H2) — D2 = b
- [ ] Finish: kiem_nhanh 20 seeds, snapshots, soat-ma, re-run Fable's four walkthroughs

## Current state (overwrite each handoff)
- Plan written; Truong approved D1 = A, D2 = b, D3 = NULL (2026-11-13). Nothing implemented yet.

## Decisions and gotchas (keep short)
- Order puts C3 before C1 (silent harm to students beats a loud block); see spec §2.
- Default `wharton: true` stays (invariant 1); SG-2 adds an exit instead.

## Next steps (ordered)
1. Persons A, B, C start in parallel (`SG_SONG_SONG.md` §1).
2. Person A integrates when B and C are DONE, gate, PR.

## Files touched
- docs/ke_hoach/SOAT_GIAO_DIEN_KE_HOACH.md: spec
- docs/ke_hoach/SG_VONG_LAP.md: three-role loop runbook (fallback)
- docs/ke_hoach/SG_SONG_SONG.md: parallel split runbook (A/B/C)
- i18n_errors.py, i18n.js, tests/test_ws_nhan.py, style.css: empty SG-A/B/C marker blocks (comments only)

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-13 | Opus (forms-gop session) | Read Fable report, re-checked C1/C2/C3/H1 in code, wrote spec + this handoff | plan only |
| 2026-11-13 | Opus (forms-gop session) | Truong approved D1–D3; wrote three-role runbook SG_VONG_LAP.md | plan only |
| 2026-11-13 | Opus (forms-gop session) | Truong chose a 3-way parallel split; wrote SG_SONG_SONG.md, added marker blocks | no behaviour change |
