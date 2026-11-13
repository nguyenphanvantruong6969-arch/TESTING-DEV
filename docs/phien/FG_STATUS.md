Mode: CHU_TRI_FG
RUNNING CHU_TRI_FG session_01VfPzNt8wLhNQyk5sYejKse 2026-11-13T01:14Z
STATUS: RUNNING

# FG status (FG-1 … FG-9, after user test of forms-gop)

> English, ≤ 150 lines. Spec: `docs/ke_hoach/FORMS_GOP_SUA_KE_HOACH.md`; mechanics: `docs/ke_hoach/FG_TU_DONG.md`.
> All numbers SIMULATED; all Forms work TH.

BASE = f5e8a41 (origin/claude/forms-gop at start)

## Current step
- STEP0 (spec §1b): delegate to a Sonnet worker.

## Item table
| Item | State | Commit | Tests |
|---|---|---|---|
| STEP0 | TODO | | |
| FG-1 | TODO | | |
| FG-3 | TODO | | |
| FG-4 | TODO | | |
| FG-5 | TODO | | |
| FG-6 | TODO | | |
| FG-2 | TODO | | |
| FG-7 | TODO | | |
| FG-8 | TODO | | |
| FG-9 | TODO | | |

## Snapshots
- Rebuild from BASE: `git worktree add <scratch>/base f5e8a41`, then in it run
  `mau_forms_thi_clb/tao_mau_forms.py <mode> --ra <scratch>/snap/<name>` for `--fa-daa`, `--fa-daa --mot-bieu-mau`,
  `--phan-hoi`, `--tuan-3` (and `--sau-ket-qua` for reference). Output verified deterministic (two runs, `diff -r` clean).
- Lead copy: `<scratchpad of session_01VfPzNt8wLhNQyk5sYejKse>/snap/{fa-daa,fa-daa_mot,phan-hoi,tuan-3,sau-ket-qua}`.

## Decisions
- D1–D4 as spec §1 (final).
- STEP0 commits the red tests it writes (they are each item's acceptance tests, rule 2); the item worker turns them
  green and may extend them. The branch is expected red between STEP0 and FG-9; the green loop runs at FINISH.
  A test already green on HEAD → item GONE-ON-HEAD; keep that test only if it adds coverage.

## Waiting for Truong
- (none yet)

## Workers
| Task | Session | State |
|---|---|---|
| STEP0 | (creating) | |

## Log
- 2026-11-13T01:14Z lead: branch claude/fg-sua created from BASE f5e8a41; lead model claude-opus-5-5; snapshots taken.
