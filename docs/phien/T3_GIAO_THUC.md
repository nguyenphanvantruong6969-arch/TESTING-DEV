# T3 automation protocol (coordinator + implementer + tester)

> Shared by every session of branch `claude/gallant-mendel-uki8j2`. English (cheap). Read once at session start.
> Truong's decisions (2026-11-04) are in `docs/phien/claude__gallant-mendel-uki8j2.md` ("Decisions"). Do not re-ask them.

## Roles
| Role | Model | Owns | Never |
|---|---|---|---|
| coord | Opus (this chat with Truong) | plan, briefs, PR, CI watch, notifications, successor creation | reads big diffs, writes product code |
| impl | Sonnet | tests first, code, related tests, `soat-ma`, CHANGELOG/TIEN_DO, commit+push | reviews own lot as "passed" |
| tester | Opus for L0, Sonnet for L1-L3 | reviews ONE lot diff, runs related tests, screenshots, writes verdict | edits product code (only screenshots + its handoff file) |

## Session start (every child)
1. Write `.claude/phien_vai.json` (gitignored): `{"vai":"impl"|"tester","coord_id":"<coord id from brief>","nguong":400000}`.
   Coord writes `{"vai":"coord","nguong":700000}`.
2. Read `CLAUDE.md`, this file, the branch file, and your own `docs/phien/claude__gallant-mendel-uki8j2__<vai>.md` if it exists.
3. Test env: `python3 -m venv .venv && .venv/bin/pip install -q -r requirements-dev.txt`; UI tests need
   `.venv/bin/pip install -q playwright==1.63.0` and `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`.

## Token rules (all roles)
- Find T3 findings by id: `grep -n "^| T3-26 " docs/nghien_cuu/T3_DEBLOAT_GIAO_DIEN.md`. Never read the whole 68 KB study.
- Locate code by function name with grep; read only the needed range.
- Run only related tests (`-k`, single files). Full suite = CI only.
- New test file -> update the `tests/` row in `docs/ke_hoach/CLAUDE_CHI_TIET.md` (file count + `pytest --collect-only -q` count);
  always include `tests/test_a13_12_tai_lieu.py` and `tests/test_giao_dien_tieng_viet_sach.py` in related tests.
- Messages between sessions use the fixed formats below, <= 15 lines, no pasted diffs or logs (give file:line or sha).
- Coord reads child transcripts only with `list_events(kinds=["assistant","result"], limit<=20)` when a message is missing.

## Work loop per lot (L0 -> L1 -> L2 -> L3)
1. coord -> impl: `GO L<n>` (lot spec = branch file section "Lot L<n>").
2. impl: per item: failing test -> minimal fix -> related tests -> next item. Then `soat-ma` (`kiem_nhanh.py` + 4 tiers),
   CHANGELOG entry, TIEN_DO row `T3-L<n>`, commit(s) `T3-L<n>: ...`, `git pull --rebase && git push -u origin <branch>`.
   L0 only: also prove invariant 1 (default config identical `match_results`, 3 datasets x 20 seeds) and report how.
3. impl -> coord: `IMPL DONE L<n>` report.
4. coord -> tester: `REVIEW L<n> <base_sha>..<head_sha>`.
5. tester: read diff, run related tests, check invariants list, take <= 6 screenshots (Playwright via `browser_host.py`,
   1280x800, deviceScaleFactor 1) of changed screens into `docs/nghien_cuu/anh_t3/sau_L<n>/`, commit+push them.
6. tester -> coord: `TESTER REPORT L<n>` with `NO BUGS` or numbered bugs (file:line, repro, expected).
7. bugs -> coord forwards list to impl (`FIX L<n>`) -> impl fixes -> `IMPL DONE L<n> fix<k>` -> tester re-checks only the fix.
   Max 3 rounds, then coord asks Truong.
8. NO BUGS -> coord opens/updates PR (one open PR per branch; if the previous lot's PR is still open, update its title/body
   to cover both lots). PR body: lots, items, tests added, screenshot links, items skipped "needs Truong".
   coord: `subscribe_pr_activity`, PushNotification "PR ready ...". Then `GO L<n+1>` immediately (stacking allowed).
9. CI red or review comment: coord sends `FIX CI L<n>` (job + failing test name) to impl; same 3-round cap.
10. PR merged by Truong: before the next push, impl rebases unmerged commits onto `origin/main`
    (`git fetch origin main && git rebase origin/main`, force-with-lease only if history was already merged).

## Blocked items (CLAUDE.md rule 7)
Invariant conflict, new library, CSV/schema contract change, or spec unclear after reading the study row:
skip the item, add a line under "Needs Truong" in the branch file, mention it in the report, continue with the next item.

## Message formats
```
IMPL DONE L<n>[ fix<k>] | base <sha> head <sha>
items: T3-xx ok; T3-yy skipped (needs Truong: reason)
tests: <files> -> <N passed>; soat-ma: <DAT/KHONG DAT + 1 line>
invariants: 1 <how proven or n/a>, 3, 4, 5, 6 <ok/n/a>
notes: <=3 lines
```
```
TESTER REPORT L<n> | reviewed <base>..<head>
verdict: NO BUGS | <k> BUGS
1. <file:line> <what> | repro: <steps> | expected: <...>
screenshots: docs/nghien_cuu/anh_t3/sau_L<n>/<files>
```
```
HANDOFF <vai> <file> <sha>
```

## Child handoff (at 400k, triggered by the Stop hook)
Child: write its `__<vai>.md` file, push, `send_message` coord `HANDOFF ...`, stop.
Coord on receipt: `create_session` (same repo, `source_revision` = branch, same model as the role, `permission_mode` auto)
with prompt: `You are <ROLE> for T3 on branch claude/gallant-mendel-uki8j2. Coordinator id: <coord id>. Read CLAUDE.md,
docs/phien/T3_GIAO_THUC.md, docs/phien/claude__gallant-mendel-uki8j2.md and docs/phien/claude__gallant-mendel-uki8j2__<vai>.md,
then continue from "Next steps".` Update the Sessions table, `archive_session` the old child, PushNotification "handoff <vai>".

## Coordinator handoff (at 700k)
1. Update the branch file (Sessions table, Current state, Next steps), push.
2. `create_session` (Opus, same repo/branch) with prompt: `You are COORD for T3 on branch claude/gallant-mendel-uki8j2.
   Previous coordinator: <old id>. Read CLAUDE.md, docs/phien/T3_GIAO_THUC.md, docs/phien/claude__gallant-mendel-uki8j2.md,
   then write .claude/phien_vai.json and continue. Re-subscribe to the open PR.`
3. `send_message` every live child: `NEW COORD <new id>` (they update `coord_id` in `.claude/phien_vai.json`).
4. PushNotification "coordinator handed off to <new id>". Stop.

## Silence fallback
Coord schedules `send_later` 90 min after each `GO`/`REVIEW`. On wake with no report: `get_session` + `list_events`
(kinds assistant/result, limit 20); if the child is idle without reporting, `send_message` "report status in protocol format".
