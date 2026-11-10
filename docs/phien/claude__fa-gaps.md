# Branch handoff: claude/fa-gaps

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English (cheaper in tokens). Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".
> File name = branch name with "/" replaced by "__" (see `.claude/hooks/handoff_khi_day_ngu_canh.py`).
> Written by the session when context passes ~400k tokens (after finishing its current prompt).

## Feature / goal
Fill every remaining FA-DAA vision gap (GAP-0 … GAP-14) per `INSTRUCTION_FILL_GAPS.md`: post-allocation changes
(adjustment table + replay, attendance, waitlist invites, appeals, round 2), feedback/surveys, next-term capacity,
admin dashboard, two-grader deviation, reminders, Power Apps kit, simulation, improvement cycles (measurement mode),
D1 memo. Every behaviour behind a new `rules` key defaulting to False; default output byte-identical (invariant 1).
Status: `docs/phien/FA_GAPS_STATUS.md`; specs: `docs/ke_hoach/FA_GAPS_KE_HOACH.md`. Run mode: SOLO (START_HERE §2.2b).

## Plan (written by Opus; ticked by Sonnet)
- [ ] GAP-0 fa_dieu_chinh + vi_tri_hien_tai (w1)  - [ ] GAP-1 attendance (w1)  - [ ] GAP-2 waitlist invites (w1)
- [ ] GAP-3 appeals (w2)  - [ ] GAP-4 round 2 (w2)  - [ ] GAP-5 feedback (w2)  - [ ] GAP-6 week-3 survey (w2)
- [ ] GAP-7 next-term capacity (w3)  - [ ] GAP-8 admin dashboard (w3)  - [ ] GAP-9 two-grader deviation (w3)
- [ ] GAP-10 reminders (w3)  - [ ] GAP-11 Power Apps kit (w4)  - [ ] GAP-12 simulation (w4)
- [ ] GAP-13 improvement cycles (w4)  - [ ] GAP-14 D1 memo (w4)

## Current state (overwrite each handoff)
- F1 setup done; wave 1 spec next.

## Decisions and gotchas (keep short)
- SOLO mode: technical choice = safest option keeping default byte-identical; recorded in status "Review notes".

## Next steps (ordered)
1. F2 wave 1 spec.

## Files touched
- docs/phien/FA_GAPS_STATUS.md, docs/ke_hoach/FA_GAPS_KE_HOACH.md, this file

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-10 | Opus (SOLO) | F1 setup: branch claude/fa-gaps from keen-ride 60f75a5 | phase 1 done 7/7 |
