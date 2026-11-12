Mode: CHU_TRI (parallel worker A, PROMPT_A.md; Phase 3 integration)
PAUSED by Truong 2026-11-12T00:00Z (no lock; any session may continue)
STATUS: IT-UI PAUSED (green loop round 1 on claude/forms-gop not finished)

# IT-UI status (FA-M7 … FA-M10, kiosk tab "Chuẩn bị đợt")

> English, ≤ 150 lines. Spec: `docs/ke_hoach/it_ui_song_song/PROMPT_A.md` + `docs/ke_hoach/IT_GIAO_DIEN_KE_HOACH.md`.
> All numbers SIMULATED; all Forms work TH (not tried on real Microsoft). BASE = fe37349.

## Current step
- PAUSED on Truong's request (2026-11-12 ~00:00 UTC). INTEGRATE done and reviewed (merge 47ab08b, fold 739736e,
  INTEGRATE-FIX1 9ac0998: user guide §16 path A/B meaning). Report: `docs/phien/bao_cao_dem/2026-11-11_it_giao_dien.md`.
- Green loop round 1 on `claude/forms-gop` @ 1c52030 was IN PROGRESS when paused:
  - generator snapshot vs BASE fe37349: identical (only default-mode xlsx `docProps/core.xml` timestamp differs);
  - local full suite: stopped at ~52 % (no failure so far) — rerun needed;
  - CI Tests run 43116400695 on 1c52030 (lint green; Linux + Windows test jobs were running) and Windows build run
    43118248858: may be cancelled by the push of this status commit (Tests workflow cancels in-progress runs per branch).
- NEXT (to continue): read this file; rerun the green loop on the current HEAD of `claude/forms-gop`: full suite
  (`PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers .venv/bin/python -m pytest -q -rs --cov --cov-report=term`),
  `ruff check .`, `kiem_nhanh.py --co-so origin/main --so-seed 20`, CI Tests on that HEAD (Linux job: if it dies in
  "Cai Chromium cho Playwright" with apt DNS errors, only rerun failed jobs), trigger the Windows build workflow;
  all green -> line 3 `STATUS: IT-UI GREEN` + numbers + report link, push. Then answer "Waiting for Truong".

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
- 2026-11-11 23:13 INTEGRATE + INTEGRATE-FIX1 reviewed; green loop round 1 started on 1c52030.
- 2026-11-12 00:00 PAUSED by Truong; scheduled check-ins deleted, local suite stopped.
