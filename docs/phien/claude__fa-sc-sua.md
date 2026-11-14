# Branch handoff: claude/fa-sc-sua

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English. Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".
> Protocol: `docs/phien/FA_SC_GIAO_THUC.md` (lead + writer + checker). Checker verdicts: `claude__fa-sc-sua__tester.md`.

## Feature / goal
FA-SC Phase 1 (approved by Truong 2026-11-14, D-SC1): converter-only fixes from `docs/fable/07_FA_SC_FIX_PLAN.md` §2
(evidence `docs/fable/06_CRISIS_MEMO.md`, drills `du_lieu_test/su_co/`). Code lives under `mau_forms_thi_clb/`
(entry `chuyen_fa_daa` in `chuyen_forms_sang_phan_mem.py`, CLI `main`). Kiosk untouched. Every new option defaults
OFF; without it the converter output is byte-identical (invariant 1). New sheets/files are reports only (invariant 2).

## Plan (written by Opus; ticked by lead after CHECKER NO BUGS)
- [ ] L0 baseline: converter on `du_lieu_test/demo_t4m.py` fake data (`--day-du` and plain) into scratch; keep outputs
- [ ] L1 FA-SC-6 roster input (P1-1)
- [ ] L2 FA-SC-4 sheet "Cần xử lý" (P1-2)
- [ ] L3 FA-SC-4b per-club dropped-response report (P1-4)
- [ ] L4 FA-SC-2 per-class confirmation sheet (P1-3)

### Lot L1 — roster input (FA-SC-6)
- New optional arg on `chuyen_fa_daa` + CLI flag (e.g. `danh_sach_truong=None` / `--danh-sach-truong CSV`): the roster
  format `danh_sach_chua_dang_ky.py` already reads (`student_id`, `class_id`, optional `email`). Reuse its reader if
  possible; no new library.
- With roster: (a) typed ID not on roster → one warning line naming ID + email; (b) one ID used by two emails → one
  line with both emails, listed BEFORE the workbook is written (non-blocking unless today's code already blocks; d03a
  must no longer be refused: if roster has `email`, replace typed ID by roster ID and report the difference);
  (c) `class_id` from roster fills the existing class column; (d) sheet "Chưa đăng ký" grouped by class, plus
  "missing day" rows per student (registered some days, not all).
- `kiem_nhan` test (new file, e.g. `tests/test_fa_sc_l1_danh_sach.py`): fake roster + export with one collision, one
  unknown ID, one unregistered, one missing day → exactly one line each; clean data → none; no roster → byte-identical.
- Drills must flip: d03a, d03b, d14 (0/120 without class), d01, d02 (student named in a report). Drills may need a
  roster arg passed through `du_lieu_test/su_co/chung.py`; add it with default OFF so old drill numbers reproduce.
- Sổ nhập columns unchanged (invariant 7).

### Lot L2 — sheet "Cần xử lý" in BANG_DIEM.xlsx (FA-SC-4)
- Only when a new option is on (default OFF → workbook byte-identical). One row per student per issue, built ONLY from
  warnings that already exist: wrong-test pair (test without rank + NOT_ATTEMPTED → one merged row), response dropped
  for unknown email, choices changed after test time, FREE club ranked above a tested SELECTIVE club, unused
  reservation (addressed to club teacher). Columns: student, issue (plain Vietnamese), who acts, what to do.
- Typed-name ≠ roster-name check (S37/d05): only if the data already exists without a form change; else skip →
  Needs Truong.
- Existing "Cảnh báo" sheet unchanged. Test: each injected case gives one row. Drills flip: d06, d04, d07 (d05 only
  if no form change).

### Lot L3 — per-club dropped-response report (FA-SC-4b)
- From L2 data, behind the same or a sibling option: one small file per club (folder in output dir): emails whose
  response for that club was dropped, and students who ranked that club but have no test. Only that club's rows; no
  scores, no lottery numbers, no other club's data. Test: one file per club, injected cases listed, nothing else.

### Lot L4 — per-class confirmation sheet (FA-SC-2)
- Behind an option; needs the L1 roster for the class. One file per class; one block per student: per day the stored
  choices, the three medals, tests received and whether each counts; dropped/not-counted tests shown "không tính + lý
  do". No other student's data in a class file, no scores of other students, no lottery numbers (STB). Own score:
  include only if the plan says so as report-only; otherwise omit and put "show own score?" on Needs Truong.
- Test: one block per student; dropped test shows reason; privacy assertions (no other class's IDs, no STB column).

## Current state (overwrite each handoff)
- Done so far: branch created from `origin/claude/fable-fa-sc` + protocol file copied (lead).
- In progress: L1 (writer).
- Tests: per lot, see protocol §2.
- Open problems: none.

## Sessions
| Role | Session id | Model | Status |
|---|---|---|---|
| lead | session_01YVAyu4EAC3N6CVfiJpThan | Opus | active |
| writer | session_01YVAyu37AUCc9XrJPLLF9Ru | Sonnet | active |
| checker | session_01YVAyu2yY5cZLrAT3px9584 | Sonnet | active |

## Needs Truong (never built automatically)
- Phase 0 (P0-1…P0-7): wording, checklists, decisions D-SC2…D-SC7 (plan §4 has a recommendation for each).
- P2-1 per-day lottery lock (schema change), P2-2 attendance, P2-3 capacity warning, P2-4, P2-5.
- S37 typed-name check that needs a "class and full name" question in the test form (form generator change).
- Wiring the new converter options into the kiosk "Chuẩn bị đợt" tab.

## Decisions and gotchas
- Undecided policy inside a lot: take the plan's "recommended" option only if report-only; else Needs Truong.
- No user-facing internal codes (FA-SC, P1-1, S30) in teacher-facing text.

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-14 | Opus (lead) | branch setup, lot specs | |
