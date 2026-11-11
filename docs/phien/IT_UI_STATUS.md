Mode: CHU_TRI (parallel worker A, PROMPT_A.md; Phase 3 integration)
RUNNING CHU_TRI-A session_01TGThn5vxmXkqyACZzBpJCq 2026-11-11T22:40Z
STATUS: IT-UI RUNNING (Phase 3: INTEGRATE A alone)

# IT-UI status (FA-M7 … FA-M10, kiosk tab "Chuẩn bị đợt")

> English, ≤ 150 lines. Spec: `docs/ke_hoach/it_ui_song_song/PROMPT_A.md` + `docs/ke_hoach/IT_GIAO_DIEN_KE_HOACH.md`.
> All numbers SIMULATED; all Forms work TH (not tried on real Microsoft). BASE = fe37349.

## Current step
- INTEGRATE: merge `origin/claude/it-ui-a` into `claude/forms-gop`, fold `MANH_A.md`, then green loop here, report.

## Workers
| Worker | Branch | Items | State |
|---|---|---|---|
| A | `claude/it-ui-a` | G0, FA-M7 | GREEN (CI run 43047307624, Windows build 43035758322) |
| B | `claude/it-ui-b` | FA-M9, FA-M10 | BLOCKED: waited too long (branch never pushed; 12 checks 18:33–22:36 UTC) |
| C | `claude/it-ui-c` | FA-M8 | BLOCKED: waited too long (branch never pushed; 12 checks 18:33–22:36 UTC) |

## Decisions
- B and C not merged (AUTO rule: RED/BLOCKED branches are not merged; their items count as not done).
- CI Linux job hit a GitHub runner apt DNS outage 5 times ("Cai Chromium cho Playwright"); only reran, no workflow change.
- The Windows build workflow uploads to the shared release `ban-moi-nhat` whatever branch it runs on.

## Waiting for Truong
- Workers B and C never started (no branch pushed). Re-run PROMPT_B / PROMPT_C (they branch from `claude/forms-gop`,
  which will then already contain G0 + FA-M7), or run TU_DONG SOLO for FA-M9 → FA-M8 → FA-M10?

## Log (append only)
- 2026-11-11 11:52 A started; G0 c7b5d1d, FA-M7 d5a303e + 414a94c, FIX-1 db76ea9; it-ui-a GREEN 18:12.
- 2026-11-11 22:36 wait for B/C ended; INTEGRATE A alone.
