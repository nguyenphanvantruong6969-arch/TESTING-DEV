# FA-SC automation protocol (lead + writer + checker)

> Written 2026-11-14 (Opus, branch `claude/dreamy-johnson-cgw652`) at Truong's request: "delegate to 3 sessions that
> run automatically without any input". English (cheap). Every session reads this once at start.
> Modelled on `docs/phien/T3_GIAO_THUC.md` (proven pattern); where they differ, THIS file wins.

## 0. Source plan and scope
- Plan: `docs/fable/07_FA_SC_FIX_PLAN.md`; evidence: `docs/fable/06_CRISIS_MEMO.md`; drills: `du_lieu_test/su_co/`
  (all on branch `claude/fable-fa-sc`). Item code FA-SC approved by Truong 2026-11-14 (D-SC1).
- **Work branch:** `claude/fa-sc-sua`, created by the lead from `origin/claude/fable-fa-sc`, then
  `git checkout origin/claude/dreamy-johnson-cgw652 -- docs/phien/FA_SC_GIAO_THUC.md`. Push only there. Never touch
  `main` or other branches. Never force-push. **No PR** (not asked).
- **Automatic scope = Phase 1 only** (converter and scripts under `mau_forms_thi_clb/`, kiosk untouched). Truong's
  "run without input" covers these lots and nothing else:

| Lot | Package (plan §2) | Sub-item | Done when (plan `kiem_nhan` + drill flips) |
|---|---|---|---|
| L1 | P1-1 roster input | FA-SC-6 | d03a, d03b, d14, d01, d02 flip; without the roster option, output byte-identical |
| L2 | P1-2 sheet "Cần xử lý" | FA-SC-4 | d06, d04, d07 flip (d05 only if no form change needed); old warning list unchanged |
| L3 | P1-4 per-club dropped-response report | FA-SC-4b | one file per club, injected cases listed, no other data |
| L4 | P1-3 per-class confirmation sheet | FA-SC-2 | one block per student; dropped test shown "not counted + reason"; no other student's data, no scores of others, no lottery numbers |

- **Out of scope → "Needs Truong" list, never build:** all of Phase 0 (wording, checklists, decisions D-SC2…D-SC7),
  P2-1 per-day lottery (schema change), P2-2 attendance, P2-3 capacity warning, P2-4, P2-5, the S37 name check that
  needs a form-generator change, wiring the new options into the kiosk "Chuẩn bị đợt" tab.
- Undecided policy inside a lot: take the plan's "recommended" option ONLY if it is report-only (no effect on
  placement); otherwise skip that part and list it under "Needs Truong".

## 1. Roles
| Role | Model | Owns | Never |
|---|---|---|---|
| lead | Opus (`claude-opus-5-5`) | branch setup, lot specs, creating/steering children, final summary | writes product code, reads big diffs |
| writer | Sonnet (`claude-sonnet-5-5`) | tests first, code, related tests, `soat-ma`, CHANGELOG/TIEN_DO, commit+push | reviews own lot as passed |
| checker | Sonnet (`claude-sonnet-5-5`) | reviews ONE lot diff, runs related tests and drills, writes verdict | edits product code or tests (only its verdict file) |

## 2. Rules for all three (from CLAUDE.md; do not ask Truong about these)
- Invariants 1–8 and rules 1–11 of `CLAUDE.md`. Truong explicitly asked for these 3 sessions (rule 10 satisfied); no
  other subagents or Agent tool.
- Invariant 1: every new option defaults OFF; without it the converter output is byte-identical. Prove it: before L1,
  run the converter on the `demo_t4m.py` fake data into a scratch folder (`--day-du`, and plain); after each lot,
  rerun and compare (`.xlsx`: compare cell values sheet by sheet with openpyxl, `.csv`: `cmp`). Kiosk untouched, so
  also run `kiem_nhanh.py --co-so origin/main --so-seed 20` once per lot (expect 7/7, 60/60 identical).
- Invariant 2: new sheets are reports; nothing they compute feeds `compute_club_priority` or the Sổ nhập.
- Invariant 7: Sổ nhập columns unchanged (the class column already exists). No schema change, no new library.
- Privacy: fake data only; per-class / per-club files contain only that class's / club's students.
- New user-facing text: plain Vietnamese, no internal codes (FA-SC, P1-1, S30) in text a teacher reads.
- Tests quiet: `.venv/bin/python -m pytest -q -p no:cacheprovider --no-header -rf --tb=no <files> 2>&1 | grep -E '^(FAILED|ERROR)|passed|failed' | tail -25`.
  Related tests = the lot's new tests + every `tests/` file that greps for an identifier you changed (start with
  `tests/test_mau_forms_thi_clb.py`, `tests/test_fa_m3_chuyen.py`, `tests/test_fa_m2_forms_dang_ky.py`,
  `tests/test_fa_m9_nap_tep_forms.py`) + `tests/test_a13_12_tai_lieu.py`. Full suite = CI only.
- New test file → update the `tests/` row in `docs/ke_hoach/CLAUDE_CHI_TIET.md` (file count + collect count).
- Env: `python3 -m venv .venv && .venv/bin/pip install -q -r requirements-dev.txt`.
- Locate code by function name (`grep -n "def <name>"`), never line numbers.
- Blocked (invariant conflict, new library, schema/CSV change, unclear spec): skip that part, add a line under
  "Needs Truong" in `docs/phien/claude__fa-sc-sua.md`, continue. Never stop to ask.

## 3. Session start
1. Write `.claude/phien_vai.json` (gitignored): lead `{"vai":"coord","nguong":700000}`; children
   `{"vai":"impl"|"tester","coord_id":"<lead id>","nguong":200000}` (hook vocabulary: writer = impl, checker = tester).
2. Read `CLAUDE.md`, this file, `docs/phien/claude__fa-sc-sua.md`, own `docs/phien/claude__fa-sc-sua__<vai>.md` if any,
   then only the plan/memo sections for the current lot.

## 4. Work loop per lot (L1 → L2 → L3 → L4)
1. lead → writer: `GO L<n>` (spec = section "Lot L<n>" of the branch file, written by the lead).
2. writer: failing test from `kiem_nhan` → minimal code → related tests → drill(s) of the lot
   (`python du_lieu_test/su_co/<drill>.py`) → invariant-1 comparison → `soat-ma` (`kiem_nhanh.py` + 4 tiers, report
   only) → `CHANGELOG.md`, `TIEN_DO.md` row `FA-SC-L<n>` → commit `FA-SC-L<n>: ...` → `git pull --rebase && git push`.
3. writer → lead: `WRITER DONE L<n>`.
4. lead → checker: `REVIEW L<n> <base>..<head>`.
5. checker: read the diff, run related tests and the lot's drills, check invariants 1, 2, 6, 7 and privacy, try 2–3
   edge cases of its own on fake data (empty roster, duplicate rows, Vietnamese diacritics, missing column). Write
   `docs/phien/claude__fa-sc-sua__tester.md` (verdict section per lot), commit+push that file only.
6. checker → lead: `CHECKER REPORT L<n>`.
7. Bugs → lead sends `FIX L<n>` with the list → writer fixes → `WRITER DONE L<n> fix<k>` → checker re-checks the fix.
   Max 3 rounds; then the lead records the lot as "Needs Truong" and moves on.
8. NO BUGS → lead ticks the lot in the branch file, pushes, sends `GO L<n+1>`.
9. After L4 (or all remaining lots blocked): lead writes the final summary (§7), archives both children, stops.

## 5. Message formats (≤ 15 lines; no pasted diffs/logs, give file:function or sha)
```
WRITER DONE L<n>[ fix<k>] | base <sha> head <sha>
done: <what>; skipped: <part> (needs Truong: reason)
tests: <files> -> <N passed>; drills flipped: <ids>; soat-ma: <DAT/KHONG DAT + 1 line>
invariants: 1 <how proven>, 2, 7 <ok/n/a>
```
```
CHECKER REPORT L<n> | reviewed <base>..<head>
verdict: NO BUGS | <k> BUGS
1. <file:function> <what> | repro: <steps> | expected: <...>
```
```
HANDOFF <vai> <file> <sha>
```

## 6. Messaging, silence, handoff
- Children send reports with `send_message` to the lead id. If a child has no `send_message` tool, it writes the same
  report at the top of its `__<vai>.md` file, pushes, and ends its turn; the lead detects it by `git fetch`.
- Lead: after each `GO`/`REVIEW`/`FIX`, schedule `send_later` 60 min. On wake without a report: `get_session` +
  `list_events(kinds=["assistant","result"], limit=20)` + `git fetch`; if the child is idle without reporting,
  `send_message` "report status in protocol format". Ignore wakes whose report already arrived.
- Child at 200k tokens (Stop hook): write `__<vai>.md`, push, send `HANDOFF ...`, stop. Lead creates a fresh child
  (same model, same prompt as §8 plus "continue from Next steps of docs/phien/claude__fa-sc-sua__<vai>.md"), archives
  the old one. Lead at 700k: update branch file, create a new lead with §8 lead prompt plus "previous lead: <id>",
  send `NEW LEAD <id>` to children, stop.

## 7. Final summary (lead, Vietnamese, in the branch file and as its last message)
Lots done / skipped, new tests, drills flipped, the "Needs Truong" list (with plan §4 recommendations), what to try on
real Forms (TH), and a 3–5 line AI-log note. No report conclusions (academic integrity).

## 8. Prompts (the lead uses the writer/checker prompts verbatim in `create_session`)
**Lead** (created by the planning session):
```
You are LEAD for FA-SC on branch claude/fa-sc-sua. Read CLAUDE.md, then docs/phien/FA_SC_GIAO_THUC.md (on
origin/claude/dreamy-johnson-cgw652 until you copy it) and follow it exactly. Set up the branch (§0), write
docs/phien/claude__fa-sc-sua.md from docs/phien/_TEMPLATE.md with the four lot specs, a Sessions table and a
"Needs Truong" list, push, then create the WRITER and CHECKER sessions with the §8 prompts (repo
https://github.com/nguyenphanvantruong6969-arch/TESTING-DEV, source_revision claude/fa-sc-sua, models from §1,
permission_mode auto) and run the §4 loop to the end. Never wait for Truong; anything that needs him goes on the list.
```
**Writer:**
```
You are WRITER for FA-SC on branch claude/fa-sc-sua. Lead session id: <LEAD_ID>. Read CLAUDE.md,
docs/phien/FA_SC_GIAO_THUC.md and docs/phien/claude__fa-sc-sua.md, write .claude/phien_vai.json (§3), set up the venv,
then wait for "GO L<n>" from the lead and follow §4 steps 2-3. Do not ask Truong anything; blocked parts go on the
"Needs Truong" list. Report only in the §5 formats.
```
**Checker:**
```
You are CHECKER for FA-SC on branch claude/fa-sc-sua. Lead session id: <LEAD_ID>. Read CLAUDE.md,
docs/phien/FA_SC_GIAO_THUC.md and docs/phien/claude__fa-sc-sua.md, write .claude/phien_vai.json (§3), set up the venv,
then wait for "REVIEW L<n> <base>..<head>" and follow §4 steps 5-6. Never edit product code or tests; only your
verdict file. Report only in the §5 formats.
```
