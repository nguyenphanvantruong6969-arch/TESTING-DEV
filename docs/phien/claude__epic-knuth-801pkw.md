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
- Done: T1a, T1b, T2, fix rounds 1, 2, 3 (HEAD cebfa2c plus this handoff commit). Round 3 verified: tests/test_ws_so_nhap.py
  and tests/test_so_nhap.py 115 passed, ruff clean; "CON-1 FIXED round 3" was SENT to Opus session_01VfPzNvdGizkwxJ8cd64rmp.
- In progress: nothing. Waiting for Opus: full-suite result and any further fix plan.

## Decisions and gotchas (keep short)
- Static sample mau_csv/SO_NHAP_CLB.xlsx is a blank template: only the Lớp column was added (all sheets equal the
  software-generated sample). vi_du_* workbooks and other du_lieu_test sổ keep the old guide wording (no test pins them).
- Guide sheet text rule: no em dash, no word em/tôi/tớ (so_nhap.py); six du_lieu_test/SO_NHAP_DQT_*.xlsx regenerated
  with sinh_du_lieu_diem_quyet_tam.py.
- test_ws_nhan.py snapshot test tolerates exactly the intended string changes (KHOA_UI_DA_BO, SUA_CO_Y).
- Do not run git stash while background tests run. Fixture `mo` (test_giao_dien_a14_lop.py) has an explicit browser
  context and a `them` parameter.

## Next steps (ordered)
1. Wait for / read Opus fix plans (cross-session messages). Fix test-first, related tests only, ruff, kiem_nhanh, CHANGELOG, commit, push.
2. Report to Opus with "CON-1 FIXED round N" (hashes, per-bug status, test counts).

## Files touched
- Round 3: tests/du_lieu_ws/so_nhap_truoc_khi_co_cfg.json, tests/test_ws_so_nhap.py, CHANGELOG.md, this file.
- Earlier rounds: see CHANGELOG sections "T1a, T1b", "T2", "T2 sửa vòng 1/2".

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-03 | Opus | ff to a14-giao-dien, wrote plan for T1/T2 | coordinator session |
| 2026-11-03 | Sonnet | T1a, T1b, T2 implemented, tests green, pushed | static sample is a blank template (only Lớp column added); day sort = earliest session with a club |
| 2026-11-03 | Sonnet | Fix round 1 (F1-F8) from Opus plan | see CHANGELOG "T1/T2 sửa vòng 1" |
| 2026-11-03 | Sonnet | Fix round 2 (G1-G3) from Opus plan | see CHANGELOG "T2 sửa vòng 2" |
| 2026-11-03 | Sonnet | Fix round 3 (snapshot of Sổ guide text) | only Hướng dẫn A1,A16,A18,A23,A33 differed |
| 2026-11-03 | Sonnet | Handoff at context limit, round 3 committed | tests still pending, report to Opus not sent |
| 2026-11-03 | Sonnet | Final handoff: rounds 1-3 done and reported | nothing pending on this side |
