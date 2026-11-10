# FA gaps — status (single source of truth)
RUNNING-FATHER: 2026-11-10T13:10Z session_01VfPzNrpxpetDBgbwqiigmr (SOLO)
RUNNING-SON: 2026-11-10T13:10Z wave 1 session_01VfPzNrpxpetDBgbwqiigmr (SOLO)
Current wave: 1 — spec ready
son session: solo   re-dispatches this wave: 0   fix waves this wave: 0

Mode: SOLO (START_HERE.md §2.2b) — one session plays father and son; never asks; technical choices = safest option that
keeps default behaviour byte-identical, recorded under "Review notes".
Branch base: origin/claude/keen-ride-72sa7t @ 60f75a5 (PR #14 not merged yet).

## Items
| Code | Wave | State (TODO/DOING/DONE/BLOCKED/WAIT-TRUONG) | Commit | Note |
|---|---|---|---|---|
| GAP-0 | 1 | TODO | | fa_dieu_chinh + vi_tri_hien_tai |
| GAP-1 | 1 | TODO | | attendance |
| GAP-2 | 1 | TODO | | waitlist invites |
| GAP-3 | 2 | TODO | | appeals |
| GAP-4 | 2 | TODO | | round 2 |
| GAP-5 | 2 | TODO | | 3 feedback questions |
| GAP-6 | 2 | TODO | | week-3 survey |
| GAP-7 | 3 | TODO | | next-term capacity |
| GAP-8 | 3 | TODO | | admin dashboard |
| GAP-9 | 3 | TODO | | two-grader deviation |
| GAP-10 | 3 | TODO | | reminders |
| GAP-11 | 4 | TODO | | Power Apps autosave kit |
| GAP-12 | 4 | TODO | | simulation |
| GAP-13 | 4 | TODO | | stable improvement cycles |
| GAP-14 | 4 | TODO | | D1 memo |

## Baseline
- 2026-11-10: `kiem_nhanh --co-so origin/main --so-seed 20` 7/7, 60/60 identical (run at 9ce1be3, same code as 60f75a5); `tests/test_nhieu_buoi.py -k TestTrungKhit` 7 passed. SIMULATED data.

## Coverage (vision §14 rows, % before → now)
(filled after each wave)

## Waiting for Truong

## Review notes (newest last)
- W1 decisions (SOLO): new module fa_sau_xep.py + mixin api_sau_xep.py; tables via DEFAULT_SCHEMA (init_db runs
  di_tru_schema each open); post-allocation flags only in MAC_DINH_TRUONG_HOC rules (never in LUAT_XEP_MAC_DINH →
  never in fingerprint); GAP-2 shares flag fa_diem_danh; kinds invite_offer/invite_expire added to G5 list; waitlist
  reuses fa_ly_do.waitlist_pos (D4 already computed).

## Log (append only: date | role | what | result)
| 2026-11-10 | father (SOLO) | F1 setup: branch from keen-ride 60f75a5; phase 1 done 7/7 (bao_cao_dem/2026-11-10_sua_nho.md) | ok |
| 2026-11-10 | father (SOLO) | F2 spec wave 1 (GAP-0, 1, 2) | ok |
