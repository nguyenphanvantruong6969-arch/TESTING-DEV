# Branch handoff: claude/epic-knuth-801pkw

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English (cheaper in tokens). Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".
> File name = branch name with "/" replaced by "__" (see `.claude/hooks/handoff_khi_day_ngu_canh.py`).
> Written by the session when context passes ~400k tokens (after finishing its current prompt).

## Feature / goal
Follow-up to A14 (student class). Branch starts from `claude/a14-giao-dien` (fast-forwarded, includes
A14 part A + B). Truong's task file (2026-11-03), explicitly overriding the registry rule (rule 1):
- T1a: static sample `mau_csv/SO_NHAP_CLB.xlsx` has no "Lớp" column (software-generated sample has it).
  Add it and make that file the main sample.
- T1b: an old workspace whose saved config already has two nouns with the same label opens fine, but
  ANY later save (rename workspace, change a rule) is rejected with `nhan_trung_danh_tu` until labels
  are fixed. Fix that. No over-engineering.
- T2: merge sidebar tabs 02 (Kết quả), 06 (Thành viên CLB), 07 (Theo lớp) into TWO tabs:
  "Kết quả" (per-student timetable, members per club, members per class) and "Dữ liệu khác"
  (everything else that was in 02). Kết quả has two tiers (see Plan T2).
- T3 (later loop): UI debloat research, output one .md. T4 (later loop): data-collection ecosystem
  model (flowcharts/architecture images) for Truong to approve BEFORE any implementation.
Algorithm, match_results, run_history, CSV column contract: untouched.

## Plan (written by Opus; ticked by Sonnet)
T1a
- [x] Find how `mau_csv/SO_NHAP_CLB.xlsx` is built (`mau_csv/tao_so_nhap.py`) vs the generated sample
      (A14 adds "Lớp" after "Họ tên"). Give every student a SIMULATED class (fixed seed, plausible
      names like 10A1, 11A2...), regenerate the xlsx, keep everything else byte-for-byte equal in meaning.
- [x] Docs: `mau_csv/HUONG_DAN_SO_NHAP.md` (+ HUONG_DAN_SU_DUNG if it names a sample) say this file is
      THE main sample. Fix tests that pin the old header/hash.
T1b
- [x] `cau_hinh_ws` / `api_workspace`: a save is rejected only when it introduces a duplicate pair
      that the currently STORED config does not already have. Old duplicates pass (keep the existing
      warning path). New duplicates still get `nhan_trung_danh_tu`. Test both directions.
T2
- [x] Sidebar: 01 Vận hành, 02 Kết quả, 03 Dữ liệu khác, then Nhập tại chỗ, Quản lý, Nhập điểm
      (renumber). Remove tabs `members` and `theolop` as separate nav items.
- [x] Kết quả tier 1 (segmented control): Theo lớp | Theo CLB | Theo mã học sinh.
      Tier 2 (sort control): Theo ngày trong tuần | Theo mã học sinh | Theo lớp (the last one ONLY
      when tier 1 = Theo mã học sinh). One picker (class / club) or search box per tier-1 view.
      Remember last tier-1/tier-2 choice per machine (localStorage, try/catch). No scores, no lottery
      numbers in Kết quả (it is for BGH, club heads, homeroom teachers).
- [x] Dữ liệu khác = every remaining 02 section (summary, export, fill stats, coverage, preference
      distribution, unplaced, reserve, cutoffs, lottery numbers, full match list...).
- [x] i18n vi+en, text rules (no em dash, no "em/tôi/tớ" in UI descriptions), language switch re-render.
- [x] Update/replace Chromium UI tests that click the old tabs; new tests for tiers.
Both
- [x] Related tests green, ruff, soat-ma, CHANGELOG, TIEN_DO, push. Opus runs the FULL suite at the end.

## Current state (overwrite each handoff)
- Done: T1a, T1b (dcf5011), T2 (6a070da). 291 related tests pass; ruff clean; soat-ma machine part 7/7.
- Waiting: Opus runs the full suite and the tester loop.

## Decisions and gotchas (keep short)
- Truong's task file overrides rule 1 (registry) and asks for son sessions (rule 10 waived for this).
- Test/bug loop: Opus designs test prompts, a Sonnet tester session reports bugs (read-only),
  Opus plans fixes, implementer session fixes; repeat until no bug.

## Next steps (ordered)
1. Opus: full suite, tester loop, fix plans.

## Files touched
- docs/phien/claude__epic-knuth-801pkw.md: this file

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-03 | Opus | ff to a14-giao-dien, wrote plan for T1/T2 | coordinator session |
| 2026-11-03 | Sonnet | T1a, T1b, T2 implemented, tests green, pushed | static sample is a blank template (only Lớp column added); day sort = earliest session with a club |
| 2026-11-03 | Sonnet | Fix round 1 (F1-F8) from Opus plan | see CHANGELOG "T1/T2 sửa vòng 1" |
