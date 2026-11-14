# Branch handoff: claude/fable-fa-sc

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English. Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".

## Feature / goal
FA-SC (new item, outside the registry, approved D-SC1 2026-11-14): human-error and crisis scenarios for one real
allocation round. Research only (Fable). Brief: `docs/fable/05_CRISIS_BRIEF.md`. Parent branch:
`claude/dreamy-johnson-cgw652` (its handoff holds the Opus plan).

## Plan (from the Opus plan, brief §4)
- [x] Step 1: failure catalogue (FMEA-style S×O×D) → `docs/fable/06_CRISIS_MEMO.md`; top 5 sent to Truong.
- [x] Step 3 (brief §4.3): 16 drills on fake data, `du_lieu_test/su_co/` (memo §6).
- [x] Step 4 (brief §4.4): remedy tables (memo §7), FA-SC-1..9 with `kiem_nhan` sketches (memo §8).
- [x] Step 5 (brief §4.5): runbook draft `docs/fable/06b_SO_TAY_SU_CO.md` (Vietnamese).
- [ ] Truong: decide D-SC2..7, approve FA-SC-n one by one. Then Opus plans, Sonnet codes.

## Current state (overwrite each handoff)
- Done: all research deliverables of brief §6. Docs and drill scripts only; no production code, no new tests.
- In progress: none.
- Open problems: S/O/D scores are AI assumptions. Not drilled: S31, S34, S35, S43, I8, T1, all of path A (Power Apps
  is not in the repo). Sample data has only 3 clubs per day.

## Decisions and gotchas (keep short)
- Facts F1–F14 in memo §2 were read in code by function name; reuse them, do not re-derive.
- Drill findings: a never-registered student is absent from the kiosk (no fallback); a missed day is silently filled
  with a FREE club; a typed ID collision refuses the whole workbook; path B has no class, so `export_theo_lop` writes
  only `_chua_co_lop.xlsx`; one attendance slip releases the seat and invites the next student, correcting the cell
  does not restore it (`fa_sau_xep.KIND` has no reversal kind); one invalid medal blocks the whole run.
- **Largest finding (F15, D-SC7):** `sinh_stb_theo_buoi` (`stb_ngay`) re-derives every day's order when the head-count
  changes; drill d16: one late student who takes no contested seat moves 18 / 38 / 30 earlier students (seeds 42 / 7 /
  11, 120 fake students). Base lottery order is kept, per-day order on 0 of 5 days. Not fixed; needs Truong (inv. 1, 3).
- No problem found: double import is idempotent; a failure inside the run leaves `match_results`/`run_history` intact.
- Drill harness: `du_lieu_test/su_co/chung.py` builds a path-B FA round (5 days × SELECTIVE/LIMITED/FREE) and runs
  the real converter and `PipelineAPI`; ~4 s per run, all drills ~100 s.
- `kiem_nhanh.py` item `trung_khit` cannot run in this clone (no `origin/main`); this branch changes no product code.

## Next steps (ordered)
1. Truong answers D-SC2..7 (memo §9); D-SC7 first and picks which FA-SC-n to build.
2. Cheapest first: FA-SC-1 (wording), FA-SC-7 (checklists, already drafted in the runbook §4), then FA-SC-4 / FA-SC-2
   (converter only), then FA-SC-5 (kiosk, `fa_sau_xep`).
3. Try memo §10 list on real Microsoft Forms (TH).

## Files touched
- docs/fable/06_CRISIS_MEMO.md: step 1 catalogue.
- docs/fable/06b_SO_TAY_SU_CO.md: runbook draft.
- du_lieu_test/su_co/: drill harness and 16 drills.
- CHANGELOG.md, docs/ke_hoach/TIEN_DO.md: one entry each.
- docs/phien/claude__fable-fa-sc.md: this handoff.

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-14 | Fable | Step 1 catalogue memo, handoff | docs only; stopped at STOP |
| 2026-11-14 | Fable | Drills d01–d15, remedy tables, runbook, CHANGELOG/TIEN_DO | docs + du_lieu_test/su_co only |
