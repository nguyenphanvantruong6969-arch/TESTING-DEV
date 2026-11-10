# FA gaps — status (single source of truth)
RUNNING-FATHER: 2026-11-10T22:55Z solo
RUNNING-SON: 2026-11-10T22:55Z wave 2 solo
Current wave: 4 — son done, waiting for father review (wave 3: GO)
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
| GAP-3 | 2 | DONE | 513711a | appeals |
| GAP-4 | 2 | DONE | e76bf48+b0d832e | round 2 |
| GAP-5 | 2 | DONE | e76bf48+fixes | 3 feedback questions |
| GAP-6 | 2 | DONE | e76bf48 | week-3 survey |
| GAP-7 | 3a | DONE | 18fb8d7 | next-term capacity; 60/60 checked with wave 3a run |
| GAP-8 | 3b | DONE | 6b0ce75 | admin dashboard |
| GAP-9 | 3a | DONE | 6587a64 | two-grader deviation; 60/60 checked with wave 3a run |
| GAP-10 | 3a | DONE | 3243c3a | reminders; 60/60 checked with wave 3a run |
| GAP-11 | 4 | DONE | cd1d694 | Power Apps autosave kit (D8 still open: kit only) |
| GAP-12 | 4 | DONE | 9a93289 | simulation (code before test: deviation from S2.b, mutations caught x2) |
| GAP-13 | 4 | DONE | 0bc53b1 | stable improvement cycles, measurement mode; spec edge rule corrected |
| GAP-14 | 4 | WAIT-TRUONG | fc7afa8 | D1 memo written (docs/ke_hoach/FA_GAPS_D1_MEMO.md); decision is Truong's |

## Baseline
- 2026-11-10: `kiem_nhanh --co-so origin/main --so-seed 20` 7/7, 60/60 identical (run at 9ce1be3, same code as 60f75a5); `tests/test_nhieu_buoi.py -k TestTrungKhit` 7 passed. SIMULATED data.

## Coverage (vision §14 rows, % before → now)
- P1 "… tự lưu, nhắc hạn, tối thiểu 3 NV, huy chương mặc định": kit/docs only before → Power Fx formulas (GAP-11, TH) + reminder flow guide and lists (GAP-10, TH); real Microsoft test still open
- P2 "… 3 câu phản hồi": 0 % → 100 % (GAP-5: kiosk + Forms TH)
- P3 "Điểm danh, danh sách chờ, vòng 2, khảo sát tuần 3, khiếu nại": 0 % → 100 % (GAP-1..4, 6)
- P3 "Ưu tiên bù, gợi ý số chỗ từ kỳ trước": 0 % → 50 % (GAP-7 done; D1 = memo, WAIT-TRUONG)
- P3 "Module mô phỏng + chế độ so sánh": FA-10 base → 100 % of the §12 list (GAP-12 calculating student, per-type tables)
- §11 dashboard (not a §14 row): 0 % → 100 % of rows with kiosk data; 3 rows "chưa có dữ liệu" by design (GAP-8)

## Next step (exact, for the next session)
1. Wait for / rerun the two broad suites: wave 3 snapshot b0d832e (log scratch full_w3) and final HEAD 8069c08 (full_w4):
   `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers .venv/bin/python -m pytest -q -p no:cacheprovider -rfs tests` (~24 min).
2. Fix reds (son hat), then write bao_cao_dem/2026-11-10_fa_gaps_wave3.md and _wave4.md (F5), then F7: final report
   bao_cao_dem/2026-11-10_fa_gaps.md, status ALL WAVES DONE, ONE draft PR claude/fa-gaps → main.

## Waiting for Truong
- GAP-14 / D1: "Kỳ 2 dùng A (không bù), B (bù đầy đủ V§8.4) hay C (bù hẹp, chỉ CLB đã thua)? Nếu B hoặc C: đồng ý ghi ngoại lệ bất biến 2 (chỉ tầng bốc thăm, nguồn fa_ly_do LOTTERY ở NV1, mỗi credit một lần, tắt mặc định) không?" — xem docs/ke_hoach/FA_GAPS_D1_MEMO.md.

## Review notes (newest last)
- W2 notes (SOLO son): GAP-4/5/6 share files, so they landed in ONE commit (e76bf48) instead of one per item (deviation
  from S2.i). Spec deviations: `cho_con_lai` takes a 5th arg (clubs of the day); `tong_hop_phan_hoi(rows, loai)`;
  round-2 "already run" = any round2 row of the base run+day (an all-skipped pass can be run again). W1 nhỏ N1
  (panels hid on any error → now `batKhung` shows a toast) and N2 (new code `loi_luu_sau_xep`) fixed in GAP-3.
- W2 decisions (SOLO): flags fa_khieu_nai, fa_vong_2, fa_phan_hoi (GAP-5 + GAP-6 share); appeal window int rule
  fa_khieu_nai_so_ngay (default 3, 1..14), clock via fa_sau_xep.bay_gio(); round 2 = one-pass serial dictatorship in
  the day's lottery order; Forms parts labelled TH.
- W1 review: GO. Nhỏ N1–N4 listed in bao_cao_dem/2026-11-10_fa_gaps_wave1.md (UI hides panel on any error; generic
  save error code wording; old-run attendance not shown after rerun; redundant FREE guard in moi_tiep).
- W1 decisions (SOLO): new module fa_sau_xep.py + mixin api_sau_xep.py; tables via DEFAULT_SCHEMA (init_db runs
  di_tru_schema each open); post-allocation flags only in MAC_DINH_TRUONG_HOC rules (never in LUAT_XEP_MAC_DINH →
  never in fingerprint); GAP-2 shares flag fa_diem_danh; kinds invite_offer/invite_expire added to G5 list; waitlist
  reuses fa_ly_do.waitlist_pos (D4 already computed).

- W2 review: GO (bao_cao_dem/2026-11-10_fa_gaps_wave2.md); 3 trung fixed in-wave (chu_cam wording, dash, Forms domain).
- W3 decisions (SOLO): split wave 3 into 3a (GAP-7, 9, 10) and 3b (GAP-8, size L); GAP-7 teacher limit in new table fa_gioi_han_gv; dashboard `khong_co_clb` is None before any run (never 0).
- W4 decisions (SOLO): D8 still open → GAP-11 built as kit only; GAP-12/13 tables only via chay_mo_phong_day_du (old FA-10 tables unchanged); GAP-13 measurement mode only.

- W3 review: GO (bao_cao_dem/2026-11-10_fa_gaps_wave3.md); 0 cao/trung.

## Log (append only: date | role | what | result)
| 2026-11-10 | father (SOLO) | F1 setup: branch from keen-ride 60f75a5; phase 1 done 7/7 (bao_cao_dem/2026-11-10_sua_nho.md) | ok |
| 2026-11-10 | father (SOLO) | F2 spec wave 1 (GAP-0, 1, 2) | ok |
| 2026-11-10 | son (SOLO) | GAP-0: 16 tests red first, 2456 related passed, mutation caught x2, 60/60 | ok |
| 2026-11-10 | son (SOLO) | GAP-1: 13 tests red first, 4768 related passed, UI 3 really ran, mutation caught x2, 60/60 | ok |
| 2026-11-10 | son (SOLO) | GAP-2: 10 tests red first, 4636 related passed, UI 4 really ran, mutation caught x3, 60/60 | ok |
| 2026-11-10 | father (SOLO) | F5 review wave 1: GO (0 cao/trung, 4 nhỏ); report bao_cao_dem/2026-11-10_fa_gaps_wave1.md | ok |
| 2026-11-10 | father (SOLO) | F2 spec wave 2 (GAP-3..6) | ok |
| 2026-11-10 | son (SOLO) | GAP-3..6 coded + own tests green; broad suites not confirmed; CONTEXT LIMIT stop | handoff |
| 2026-11-10 | son (SOLO) | GAP-3 broad suite on 513711a: 4791 passed / 4 skipped / 0 failed | ok |
| 2026-11-10 | son (SOLO) | wave-2 broad suite on 8c4b37d: 5733 passed / 2 failed (wording) / 4 skipped; fixed, rerun green | ok |
| 2026-11-10 | father (SOLO) | F5 review wave 2: GO; report bao_cao_dem/2026-11-10_fa_gaps_wave2.md | ok |
| 2026-11-10 | son (SOLO) | GAP-9, GAP-10, GAP-7, GAP-8: tests red first, own + related green, UI really ran, mutations caught, 60/60 after GAP-7 | ok |
| 2026-11-10 | son (SOLO) | GAP-11: kit formulas, default kit byte-identical, mutation caught | ok |
| 2026-11-10 | son (SOLO) | wave-3 broad suite on b0d832e: 5763 passed / 0 failed / 4 skipped | ok |
| 2026-11-10 | father (SOLO) | F5 review wave 3: GO; report bao_cao_dem/2026-11-10_fa_gaps_wave3.md | ok |
