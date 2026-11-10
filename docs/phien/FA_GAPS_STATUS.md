# FA gaps — status (single source of truth)
RUNNING-FATHER: 2026-11-10T13:10Z session_01VfPzNrpxpetDBgbwqiigmr (SOLO)
RUNNING-SON: 2026-11-10T13:10Z wave 2 session_01VfPzNrpxpetDBgbwqiigmr (SOLO)
Current wave: 2 — son running
son session: solo   re-dispatches this wave: 0   fix waves this wave: 0

Mode: SOLO (START_HERE.md §2.2b) — one session plays father and son; never asks; technical choices = safest option that
keeps default behaviour byte-identical, recorded under "Review notes".
Branch base: origin/claude/keen-ride-72sa7t @ 60f75a5 (PR #14 not merged yet).

## Items
| Code | Wave | State (TODO/DOING/DONE/BLOCKED/WAIT-TRUONG) | Commit | Note |
|---|---|---|---|---|
| GAP-0 | 1 | DONE | c6e0405 | fa_dieu_chinh + vi_tri_hien_tai |
| GAP-1 | 1 | DONE | a10eee5+bb49d11 | attendance |
| GAP-2 | 1 | DONE | 541f945+next | waitlist invites |
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
- P3 "Điểm danh, danh sách chờ, vòng 2, khảo sát tuần 3, khiếu nại": 0 % → 40 % (wave 1)
- P3 "Ưu tiên bù, gợi ý số chỗ từ kỳ trước": 0 % (waves 3–4)
- P3 "Module mô phỏng + chế độ so sánh": as before (wave 4)
- P2 "… 3 câu phản hồi": phản hồi 0 % (wave 2)

## Waiting for Truong

## Review notes (newest last)
- W2 decisions (SOLO): flags fa_khieu_nai, fa_vong_2, fa_phan_hoi (GAP-5 + GAP-6 share); appeal window int rule
  fa_khieu_nai_so_ngay (default 3, 1..14), clock via fa_sau_xep.bay_gio(); round 2 = one-pass serial dictatorship in
  the day's lottery order; Forms parts labelled TH.
- W1 review: GO. Nhỏ N1–N4 listed in bao_cao_dem/2026-11-10_fa_gaps_wave1.md (UI hides panel on any error; generic
  save error code wording; old-run attendance not shown after rerun; redundant FREE guard in moi_tiep).
- W1 decisions (SOLO): new module fa_sau_xep.py + mixin api_sau_xep.py; tables via DEFAULT_SCHEMA (init_db runs
  di_tru_schema each open); post-allocation flags only in MAC_DINH_TRUONG_HOC rules (never in LUAT_XEP_MAC_DINH →
  never in fingerprint); GAP-2 shares flag fa_diem_danh; kinds invite_offer/invite_expire added to G5 list; waitlist
  reuses fa_ly_do.waitlist_pos (D4 already computed).

## Log (append only: date | role | what | result)
| 2026-11-10 | father (SOLO) | F1 setup: branch from keen-ride 60f75a5; phase 1 done 7/7 (bao_cao_dem/2026-11-10_sua_nho.md) | ok |
| 2026-11-10 | father (SOLO) | F2 spec wave 1 (GAP-0, 1, 2) | ok |
| 2026-11-10 | son (SOLO) | GAP-0: 16 tests red first, 2456 related passed, mutation caught x2, 60/60 | ok |
| 2026-11-10 | son (SOLO) | GAP-1: 13 tests red first, 4768 related passed, UI 3 really ran, mutation caught x2, 60/60 | ok |
| 2026-11-10 | son (SOLO) | GAP-2: 10 tests red first, 4636 related passed, UI 4 really ran, mutation caught x3, 60/60 | ok |
| 2026-11-10 | father (SOLO) | F5 review wave 1: GO (0 cao/trung, 4 nhỏ); report bao_cao_dem/2026-11-10_fa_gaps_wave1.md | ok |
| 2026-11-10 | father (SOLO) | F2 spec wave 2 (GAP-3..6) | ok |
