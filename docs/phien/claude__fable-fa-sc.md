# Branch handoff: claude/fable-fa-sc

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English. Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".

## Feature / goal
FA-SC (new item, outside the registry, approved D-SC1 2026-11-14): human-error and crisis scenarios for one real
allocation round. Research only (Fable). Brief: `docs/fable/05_CRISIS_BRIEF.md`. Parent branch:
`claude/dreamy-johnson-cgw652` (its handoff holds the Opus plan).

## Plan (from the Opus plan, brief §4)
- [x] Step 1: failure catalogue (FMEA-style S×O×D) → `docs/fable/06_CRISIS_MEMO.md`; STOP, top 5 sent to Truong.
- [ ] Step 2 (brief §4.3): drills on fake data, scripts under `du_lieu_test/su_co/`. WAIT for Truong.
- [ ] Step 3 (brief §4.4): remedy tables, FA-SC-n with `kiem_nhan`.
- [ ] Step 4 (brief §4.5): runbook `docs/fable/06b_SO_TAY_SU_CO.md` (Vietnamese).

## Current state (overwrite each handoff)
- Done: memo step 1: 48 student rows (S1–S29 + S30–S48 new), 13 teacher/IT rows, top-10 ranking, 9 proposed
  sub-items FA-SC-1..9, decisions D-SC2..6. Docs only; no production code, no tests needed.
- In progress: none. Stopped at the brief's STOP point.
- Open problems: all S/O/D scores are AI assumptions; no drill run; [hyp] rows unverified (S43 medals after club
  closing, S45 class source on path B, I6 off-machine backup).

## Decisions and gotchas (keep short)
- Facts F1–F14 in memo §2 were read in code by function name; reuse them, do not re-derive.
- S2 / S9 (valid but mistaken choices) top the RPN but are indistinguishable from intent: prevention only.
- Attendance (`luu_diem_danh`) releases and re-invites in one click; `fa_sau_xep.KIND` has no reversal kind.
- Path B: student ID is typed free text; duplicate ID blocks the whole workbook import (`so_nhap_hs_trung`).
- Citations (DeRosier 2002, Reason 2000, Chen & Sönmez 2006, Hassidim et al. 2017) checked on Crossref.

## Next steps (ordered)
1. Truong answers: which of ranks 1–10 to drill; decisions D-SC2..6; approve FA-SC-n one by one.
2. Then step 3 drills with `python du_lieu_test/demo_t4m.py --ra <scratch> --day-du`.

## Files touched
- docs/fable/06_CRISIS_MEMO.md: step 1 catalogue.
- docs/phien/claude__fable-fa-sc.md: this handoff.

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-14 | Fable | Step 1 catalogue memo, handoff | docs only; stopped at STOP |
