Mode: CHU_TRI (parallel worker A, PROMPT_A.md; Phase 3 integration)
DONE 2026-11-12T15:47Z (no lock)
STATUS: IT-UI GREEN

# IT-UI status (FA-M7 … FA-M10, kiosk tab "Chuẩn bị đợt")

> English, ≤ 150 lines. Spec: `docs/ke_hoach/it_ui_song_song/PROMPT_A.md` + `docs/ke_hoach/IT_GIAO_DIEN_KE_HOACH.md`.
> All numbers SIMULATED; all Forms work TH (not tried on real Microsoft). BASE = fe37349.

## Current step
- DONE. All four items on `claude/forms-gop` @ d60d221 (code); report `docs/phien/bao_cao_dem/2026-11-12_it_giao_dien.md`.
- Green evidence: local full suite 5972 passed / 0 failed, coverage 93.52 %, no UI test skipped; kiem_nhanh --so-seed 20
  7/7, 60/60; generator (7 modes) + converter (3 demo sets) identical to BASE fe37349; CI Tests run 43231302370 green;
  Windows build run 43239577277 green (published to release `ban-moi-nhat`). No further check-ins scheduled.

## Workers
| Worker | Branch | Items | State |
|---|---|---|---|
| A | `claude/it-ui-a` | G0, FA-M7 | GREEN (CI run 43047307624, Windows build 43035758322) |
| B | `claude/it-ui-b` | FA-M9, FA-M10 | MERGED 2026-11-12 (f809e2b). Code done (started late, from 5196217). BLOCKED 2026-11-12 10:57: only failure = code-map test-file count 254 vs 260 in A-owned `CLAUDE_CHI_TIET.md`; suite 5925 passed, coverage 93 %; lead ran on Sonnet, not Opus |
| C | `claude/it-ui-c` | FA-M8 | MERGED 2026-11-12 (d06d2d8). GREEN 2026-11-12 07:55 (CI + Windows build green); edited the same count line (254→257) |

## Decisions
- B and C not merged (AUTO rule: RED/BLOCKED branches are not merged; their items count as not done).
- CI Linux job hit a GitHub runner apt DNS outage 5 times ("Cai Chromium cho Playwright"); only reran, no workflow change.
- The Windows build workflow uploads to the shared release `ban-moi-nhat` whatever branch it runs on.

## Waiting for Truong
- Where does `claude/forms-gop` merge (no PR opened)? Try one small cycle on real Microsoft Forms (drop the TH label)?

## Log (append only)
- 2026-11-11 11:52 A started; G0 c7b5d1d, FA-M7 d5a303e + 414a94c, FIX-1 db76ea9; it-ui-a GREEN 18:12.
- 2026-11-11 22:36 wait for B/C ended; INTEGRATE A alone.
- 2026-11-11 23:13 INTEGRATE + INTEGRATE-FIX1 reviewed; green loop round 1 started on 1c52030.
- 2026-11-12 00:00 PAUSED by Truong; scheduled check-ins deleted, local suite stopped.
- 2026-11-12 11:20 status refresh (Opus planner session): C GREEN, B BLOCKED on A-owned count; both unmerged; still PAUSED.
- 2026-11-12 12:5x INTEGRATE-2 (Opus planner session, Truong: "ghép"): merged B, C; fold; count 263.
- 2026-11-12 13:4x round 1: 1 failed (code-map backticks) -> FIX-1 by Sonnet (d60d221); round 2 local green.
- 2026-11-12 15:47 CI Tests + Windows build green -> IT-UI GREEN. Stopped (Truong: cut when green).
