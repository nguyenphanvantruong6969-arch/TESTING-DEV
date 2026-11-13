# Branch handoff: claude/sg-sua

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English. Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".

## Feature / goal
Fix the 19 findings of Fable's whole-kiosk UI audit ("Soát giao diện kiosk RB-DA", 2026-11-13), most severe first.
Spec: `docs/ke_hoach/SOAT_GIAO_DIEN_KE_HOACH.md` (follow exactly; items SG-1 … SG-12). Branch from `main` only AFTER
`claude/fg-sua` is merged into `main`. All numbers SIMULATED.

## Plan (written by Opus; ticked by Sonnet)
- [ ] Step 0: `claude/fg-sua` merged into `main` (Truong); branch `claude/sg-sua` from it
- [ ] SG-1 selective club with no scores blocks the run (C3)
- [ ] SG-2 default workspace no longer traps a new user (C1)
- [ ] SG-3 FA rank from the original list + flag earlier FA numbers (C2) — needs D3
- [ ] SG-4 one student-ID matching rule (M3)
- [ ] SG-5 medal questions explained; swap question only when possible (H3) — Truong approves wording
- [ ] SG-6 club time and room (H1) — needs D1
- [ ] SG-7 grouped warnings everywhere (H4, M1)
- [ ] SG-8 step-1 strings into i18n (M5)
- [ ] SG-9 busy state + .catch wrapper for new JS (FG-4 pattern)
- [ ] SG-10 free clubs: no fill percentage (M2)
- [ ] SG-11 UI hygiene (M4, M6, M7, L1, L4, L5)
- [ ] SG-12 plain titles in student forms (H2) — only if D2 = b, separate approval
- [ ] Finish: kiem_nhanh 20 seeds, snapshots, soat-ma, re-run Fable's four walkthroughs

## Current state (overwrite each handoff)
- Plan written; nothing implemented. Waiting for Truong: Step 0 merge, D1, D2, D3 (spec §1).

## Decisions and gotchas (keep short)
- Order puts C3 before C1 (silent harm to students beats a loud block); see spec §2.
- Default `wharton: true` stays (invariant 1); SG-2 adds an exit instead.

## Next steps (ordered)
1. Truong: merge fg-sua; answer D1–D3.
2. Sonnet: SG-1.

## Files touched
- docs/ke_hoach/SOAT_GIAO_DIEN_KE_HOACH.md: spec

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-13 | Opus (forms-gop session) | Read Fable report, re-checked C1/C2/C3/H1 in code, wrote spec + this handoff | plan only |
