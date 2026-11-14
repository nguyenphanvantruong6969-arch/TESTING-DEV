# Branch handoff: claude/dreamy-johnson-cgw652

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English. Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".

## Feature / goal
Crisis and human-error scenarios for one real allocation round (students, club teachers, GVCN, IT): find what can go
wrong when people slip (e.g. a student takes the wrong club's test), how much harm it does, whether the system detects
it, and which fix keeps the 8 invariants. Research by Fable; brief `docs/fable/05_CRISIS_BRIEF.md`.
Registry: none yet. Proposed new item **FA-SC** (outside the registry) — awaiting Truong (D-SC1).

## Plan (written by Opus)
- [x] Step 0 (Opus): write Fable brief `docs/fable/05_CRISIS_BRIEF.md` and this file.
- [ ] Step 1 (Fable): failure catalogue (FMEA-style S×O×D), brief §4.1; STOP, top 5 to Truong.
- [ ] Step 2 (Fable): drills on fake data, scripts in `du_lieu_test/su_co/`, brief §4.3.
- [ ] Step 3 (Fable): remedy tables + FA-SC-n proposals with `kiem_nhan` → `docs/fable/06_CRISIS_MEMO.md`.
- [ ] Step 4 (Fable): runbook draft `docs/fable/06b_SO_TAY_SU_CO.md` (Vietnamese).
- [ ] Step 5 (Truong): decide D-SC1…D-SC4; Opus then turns approved FA-SC-n into a Sonnet plan.

## Current state (overwrite each handoff)
- Done so far: Step 0 (docs only, no code).
- In progress: none.
- Tests: none needed (docs only).
- Open problems: item code FA-SC not approved yet.

## Decisions and gotchas (keep short)
- Remedies must not reopen manipulation: post-result "I misclicked" claims are the key tension (brief S6, D-SC3).
- Reruns after a correction keep the locked STB (inv. 3) and append to `run_history` (inv. 4).

## Next steps (ordered)
1. Truong starts a Fable session with the prompt in brief §8.

## Files touched
- docs/fable/05_CRISIS_BRIEF.md: Fable brief for FA-SC.
- docs/phien/claude__dreamy-johnson-cgw652.md: this handoff.

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-14 | Opus | Wrote FA-SC Fable brief and handoff | docs only |
