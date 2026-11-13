Mode: SG_SONG_SONG person A
LOCK: LEAD session_01TGThn8FotZk5dp89pKN66o 2026-11-13T12:54Z
STATUS: RUNNING
BASE: 98709f1f374368c65ee2833467715fd933dc84f6   SNAPSHOT: n/a for person A (no generator item; leads B/C hold the snapshot)
Branch claude/sg-a starts at ba4b207 = BASE + 2 doc-only commits (SG_SONG_SONG.md, claude__sg-sua.md) so workers read the current 2.9/2.10.

## Items
| Item | State | Round | Start | End | Coder session | Checker session | Tests |
|---|---|---|---|---|---|---|---|
| SG-1 (C3) | DONE | 1 | 5b474dd | 95de0b9 | session_01TGThn7GRLE7ML1TDfW53iL | session_01TGThn8ctQPeoQJvGZsej9z, session_01TGThn4rAzzXnkc6uQerb5h | test_sg1_tuyen_chon_khong_diem.py (9) |
| SG-3 (C2) | DONE | 0 | 39de078 | f2e7702 | session_01TGThn5vDcdjy25A1uMuruk | session_01TGThn5ifqoQYavHTFkb9a4 | test_sg3_hang_fa.py (5) |
| SG-4 (M3) | DONE | 1 | a959972 | 17eaf11 | session_01TGThn7xWLDq89PLMhnwS9V | session_01TGThn68N7shbENa7GNKWsZ, session_01TGThn6utYnaicoK4Ce6A5K | |
| SG-10 (M2) | CODING | 0 | f660d28 | | session_01TGThn6PGJParLMUADLpcQk | | |
| SG-11a (M6, M7, L1, L4, L5) | TODO | 0 | | | | | |

## Fix lists
- SG-4 FIX-1 (checker session_01TGThn68N7shbENa7GNKWsZ, lead agrees): 1. en text of the two new appeal codes: `{person}` -> `{person_l}`; regenerate i18n_loi.js.
- SG-1 FIX-1 (checker session_01TGThn8ctQPeoQJvGZsej9z, lead agrees): 1. `kiem_truoc_fa` so_nv1 must count first club WITHIN the club's session (as demand table `nv1`), not overall first; add a two-session test (expect 2).

## Decisions
- D-A1: Fable's report artifact is not readable from this account (artifact not found). Per 2.1, red tests come from the spec text (SOAT_GIAO_DIEN_KE_HOACH.md §3) and the code.
- D-A2: claude/sg-a branched from origin/claude/forms-gop tip (ba4b207), not BASE 98709f1: the two extra commits only touch docs/ke_hoach/SG_SONG_SONG.md and docs/phien/claude__sg-sua.md. Diffs and checker START use item Start hashes, so nothing else changes.
- D-A4: SG-1 round-1 checker logged its PASS line with the round-0 checker id (session_01TGThn8ctQ...); review file 'Round 1' section is the r2 session's work. Lead re-verified: 2311 tests passed, ruff clean, kiem_nhanh 7/7.
- D-A3: SG-11 scope for person A = M6, M7, L1, L4, L5 (+ one-line consistency rules, glossary list to docs/). M4 belongs to person B (SG-11b).

- D-A5 (SG-3): rank fixed as a post-process at the end of `fa_daa.chay_fa_daa` (writes into `ket.per_buoi[buoi].rank_in_student_pref`); `fa_daa.ly_do_ket_qua` `rank_in_list` was already original-list and per-session, unchanged. Panel: new key `ngoai_danh_sach` = placed, rank NULL, club never in `preferences`. Fable's HS001/HS002 rebuilt from spec (D-A1); test also needs a scored attempt in club S (HS005) or the SG-1 check blocks the run.

## For Truong
- SG-3 academic check (FA NV1 numbers possibly computed from trimmed-list rank): `du_lieu_test/mo_phong_fa_daa.py` + FA_DAA_VISION.md line ~206 (63 % top-2): NOT affected (true preference `thich`, only `assignment` used). 48 %→79 % (docs/fable/01_PROJECT_CONTEXT.md, 02_FABLE_BRIEF.md, FA_DAA_VISION.md ~360) and 29 %→47 % (GIAM_MAY_RUI_KE_HOACH.md): generating script not found, cannot confirm they are FA numbers; please check. FA_GAPS_KE_HOACH.md ~366 only describes the dashboard (no number). Other pre-scan files: no FA NV1 number. `du_lieu_test/bao_cao_phan_bo.py` reads stored rank: affected only if run with FA on. Any past FA run's `ket_qua_phan_bo.csv`/dashboard NV1 is affected.

## Log
2026-11-13T12:54Z LEAD session_01TGThn8FotZk5dp89pKN66o SETUP lead-is-opus ba4b207
2026-11-13T12:54Z LEAD session_01TGThn8FotZk5dp89pKN66o SG-1 CODING coder=session_01TGThn7GRLE7ML1TDfW53iL ffb6ce2
2026-11-13T13:04Z CODER session_01TGThn7GRLE7ML1TDfW53iL SG-1 READY 9934af2 red:5 of 8 new tests failed before fix (no tested_scores arg, no code in run/health) mutation:zero-score condition replaced by False -> 3 tests fail, restored
2026-11-13T14:44Z LEAD session_01TGThn8FotZk5dp89pKN66o SG-1 CHECKING checker=session_01TGThn8ctQPeoQJvGZsej9z 9934af2
2026-11-13T14:47Z CHECKER session_01TGThn8ctQPeoQJvGZsej9z SG-1 FIX-1 so_nv1 counts overall first choice, not first in session (see docs/phien/sg_review/SG-1.md)
2026-11-13T15:20Z LEAD session_01TGThn8FotZk5dp89pKN66o SG-1 FIX-1 sent to coder session_01TGThn7GRLE7ML1TDfW53iL 618e28b
2026-11-13T15:25Z CODER session_01TGThn7GRLE7ML1TDfW53iL SG-1 FIX-1: 1 done (dem_nv1_trong_buoi shared by bang_nhu_cau and kiem_truoc_fa; two-session test so_nv1==2; note: test adds a TU_DO club B in b2, else fa_thieu_clb_tu_do also fires) READY 95de0b9 red:two-session test failed with old count mutation:restored old sum(...)[0]==cid -> new test fails, reverted
2026-11-13T15:49Z LEAD session_01TGThn8FotZk5dp89pKN66o SG-1 CHECKING r2 95de0b9
2026-11-13T15:54Z CHECKER session_01TGThn8ctQPeoQJvGZsej9z SG-1 PASS
2026-11-13T16:13Z LEAD session_01TGThn8FotZk5dp89pKN66o SG-1 DONE lead-review agree 95de0b9
2026-11-13T16:13Z LEAD session_01TGThn8FotZk5dp89pKN66o SG-3 CODING coder=session_01TGThn5vDcdjy25A1uMuruk 39de078
2026-11-13T17:05Z CODER session_01TGThn5vDcdjy25A1uMuruk SG-3 READY f2e7702 red:5 of 5 new tests failed before fix (HS001 rank 1 vs original 2, fallback rank 1 not NULL, dashboard NV1 100% vs direct count 40%) mutation:rank line replaced by old value -> 4 tests fail, restored
2026-11-13T16:42Z LEAD session_01TGThn8FotZk5dp89pKN66o SG-3 CHECKING checker=session_01TGThn5ifqoQYavHTFkb9a4 f2e7702
2026-11-13T17:40Z CHECKER session_01TGThn5ifqoQYavHTFkb9a4 SG-3 PASS
2026-11-13T17:07Z LEAD session_01TGThn8FotZk5dp89pKN66o SG-3 DONE lead-review agree (2326 passed, kiem_nhanh 7/7) f2e7702
2026-11-13T17:07Z LEAD session_01TGThn8FotZk5dp89pKN66o SG-4 CODING coder=session_01TGThn7xWLDq89PLMhnwS9V c7ff951
2026-11-13T17:30Z CODER session_01TGThn7xWLDq89PLMhnwS9V SG-4 READY 53025b1 red:4 of 4 new tests failed before fix (hs010 with trailing space/case rejected, one code for both causes, new codes missing) mutation:khop_ma_hoc_sinh replaced by exact-only match -> case/space test fails, restored
2026-11-13T17:24Z LEAD session_01TGThn8FotZk5dp89pKN66o SG-4 CHECKING checker=session_01TGThn68N7shbENa7GNKWsZ 53025b1
2026-11-13T17:27Z CHECKER session_01TGThn68N7shbENa7GNKWsZ SG-4 FIX-1
2026-11-13T17:41Z LEAD session_01TGThn8FotZk5dp89pKN66o SG-4 FIX-1 sent to coder session_01TGThn7xWLDq89PLMhnwS9V 98d47ce
2026-11-13T17:50Z CODER session_01TGThn7xWLDq89PLMhnwS9V SG-4 FIX-1: 1 done ({person} -> {person_l} in both en strings, i18n_loi.js regenerated) READY 17eaf11 red:n/a (wording only; verified en text no longer capitalised via tests/test_sg4_khop_ma.py, test_ws_nhan, test_van_phong_tu_nhien pass, kiem_nhanh 7/7) mutation:n/a
2026-11-13T17:55Z LEAD session_01TGThn8FotZk5dp89pKN66o SG-4 CHECKING r2 17eaf11
2026-11-13T18:10Z CHECKER session_01TGThn6utYnaicoK4Ce6A5K SG-4 PASS
2026-11-13T18:12Z LEAD session_01TGThn8FotZk5dp89pKN66o SG-4 DONE lead-review agree (96 passed, kiem_nhanh 7/7) 17eaf11
2026-11-13T18:12Z LEAD session_01TGThn8FotZk5dp89pKN66o SG-10 CODING coder=session_01TGThn6PGJParLMUADLpcQk f660d28
