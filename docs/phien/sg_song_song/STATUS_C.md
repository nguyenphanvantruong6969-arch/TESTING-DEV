Mode: SG_SONG_SONG person C
LOCK: LEAD session_01VfPzNuse9EfjuDwwt7335U 2026-11-13T15:55Z
STATUS: RUNNING
BASE: 98709f1f374368c65ee2833467715fd933dc84f6
SNAPSHOT: in a clean worktree of BASE run every mode of `mau_forms_thi_clb/tao_mau_forms.py`
(`""`, `--fa-daa`, `--fa-daa --mot-bieu-mau`, `--bien-the`, `--chi-thi`, `--phan-hoi`, `--sau-ket-qua`, `--tuan-3`),
each with `--ra <out>/m<i>` (i = 1..8 in that order). Notes: the default mode ignores `--ra` and writes
`NHAP_FORMS_THI_CLB.docx`, `MAU_XUAT_TU_FORMS.xlsx`, `CAI_DAT_FORMS.md` into `mau_forms_thi_clb/` (copy them into m1,
then `git checkout -- mau_forms_thi_clb/`); `--bien-the` exits non-zero on the stock `de_thi.json` (no
`de_thi_bien_the`) and writes nothing — expected. Unzip every .xlsx/.docx and delete `docProps/core.xml`, then
`diff -r` BASE-snapshot vs HEAD-snapshot. Deterministic (two BASE runs identical). Script used by the lead:
`snap.sh <worktree> <out>` — the loop above, nothing else.

## Items
| Item | State | Round | Start | End | Coder session | Checker session | Tests |
|---|---|---|---|---|---|---|---|
| SG-5 | DONE | 1 | bd6d821 | a4d950a | session_01VfPzNruBqHHaJZQcLRxRzS | session_01VfPzNvd9nsMJp4kwS7QzT8 (r2; r1 session_01VfPzNrFdN7RhAERrSNeTJV) | tests/test_sg5_huy_chuong.py, tests/test_fg7_bieu_mau_sau_ket_qua.py |
| SG-7 | CODING | 0 | eb6ef50 | | session_01VfPzNvgJo8vZQhB3sTbaQr | | |
| SG-9 | TODO | 0 | | | | | |
| SG-12 | TODO | 0 | | | | | |

## Fix lists
### SG-5 FIX-1 (checker session_01VfPzNrFdN7RhAERrSNeTJV, docs/phien/sg_review/SG-5.md)
1. tests/test_fg7_bieu_mau_sau_ket_qua.py: for `fa_daa`, `fa_daa_mot` ONLY add a platform-independent content digest
   (sorted relative names + bytes of .md files + paragraph/table text of each .docx via python-docx), pinned once on
   posix, asserted on BOTH OSes; keep the posix byte hash as is.
2. On nt, for these two modes, skip only the byte-hash assert (reason string names SG-5), not the whole test.
3. Fix the overlong two-sentence comment line in that file.

## Decisions
- WARNING: lead is not Opus (`get_session` reports claude-sonnet-5-5 at setup; the serving model may change).
- Fable's report artifact is unreadable from this account ("artifact not found") → red tests come from the spec text
  of `SOAT_GIAO_DIEN_KE_HOACH.md` and the finding as reproduced in code (SG_SONG_SONG 2.1 fallback).

- SG-7: helper placed in js/00_nen.js (no A/B edits there). Step-4 warning prefix `ma:` (internal code) dropped from visible text; old `slice(0,30)` cap replaced by the 5-example rule. Old i18n keys canh_bao_gom/xem_dau/thu_gon left (outside SG-C block).

## For Truong
SG-5 wording (vi; sits in the gold-medal question of each `--fa-daa*` registration form, after the question text; en: none, forms are Vietnamese-only):
"Huy chương giúp em được ưu tiên hơn bạn khác ở CLB đó: CLB có xét điểm thi thì chỉ dùng khi bằng điểm thi, CLB không xét điểm thi thì dùng trước khi bốc thăm. Em không chọn gì thì hệ thống tự đặt vàng cho nguyện vọng 1, bạc cho nguyện vọng 2, đồng cho nguyện vọng 3 (CLB Tự do không có huy chương nên được bỏ qua)."
Changed vs the brief: (1) "medals only break ties after the test score" is true only for clubs WITH scores; in `fa_daa` a Giới hạn club orders by medal BEFORE the lottery (key `(1, -medal, stb)`), so the text says both. (2) "leaving default never hurts" is not provable (not a dominant strategy), so it is NOT claimed. (3) Default is "first/second/third NON-free club", so the text says free clubs are skipped.
Placement is in the question title because Quick Import has no per-section description field (untested on real Forms).


## Log
- 2026-11-13T16:10Z LEAD session_01VfPzNuse9EfjuDwwt7335U setup branch claude/sg-c from BASE 98709f1
- 2026-11-13T15:55Z LEAD session_01VfPzNuse9EfjuDwwt7335U SG-5 CODING start 7f7b5ca coder session_01VfPzNruBqHHaJZQcLRxRzS
- 2026-11-13T16:01Z CODER session_01VfPzNruBqHHaJZQcLRxRzS SG-5 READY 7b7109a red:3 of 6 new tests failed (3 false 'chỉ còn 1 CLB' warnings counted, no description, swap present on 2-club day) mutation:forcing swap on / disabling reader day-size guard -> 2 new tests fail, restored
- 2026-11-13T16:32Z LEAD session_01VfPzNuse9EfjuDwwt7335U SG-5 READY accepted, range bd6d821..b9c4f32 (Start corrected to the assign commit); CHECKING
- 2026-11-13T16:32Z LEAD session_01VfPzNuse9EfjuDwwt7335U SG-5 checker r1 session_01VfPzNrFdN7RhAERrSNeTJV
- 2026-11-13T16:34Z CHECKER session_01VfPzNrFdN7RhAERrSNeTJV SG-5 FIX-1 (wording/snapshot/old-exports pass; nt hashes of fa_daa/fa_daa_mot stale -> content digest on both OS, see docs/phien/sg_review/SG-5.md)
- 2026-11-13T16:52Z LEAD session_01VfPzNuse9EfjuDwwt7335U SG-5 FIX-1 agreed, sent to coder session_01VfPzNruBqHHaJZQcLRxRzS
- 2026-11-13T16:52Z CODER session_01VfPzNruBqHHaJZQcLRxRzS SG-5 FIX-1 READY: (1) content digest _bam_noi_dung (names + .md bytes CRLF-normalised + docx paragraph/table text) pinned for fa_daa, fa_daa_mot, asserted on both OSes, posix byte hash kept; (2) on nt only the byte-hash assert is skipped (reason names SG-5); (3) comment fixed into separate lines, obsolete 'nt STALE' note removed from For Truong. mutation: changing the description text -> content-digest fail, restored
- 2026-11-13T17:10Z LEAD session_01VfPzNuse9EfjuDwwt7335U SG-5 FIX-1 READY a4d950a; checker r2 session_01VfPzNvd9nsMJp4kwS7QzT8
- 2026-11-13T17:11Z CHECKER session_01VfPzNvd9nsMJp4kwS7QzT8 SG-5 PASS (round 2, a4d950a; see docs/phien/sg_review/SG-5.md)
- 2026-11-13T17:40Z LEAD session_01VfPzNuse9EfjuDwwt7335U SG-5 DONE (lead review: diff read; 110 item/related tests pass; ruff clean; kiem_nhanh 7/7 60 cases; generator diff only m2/m3 --fa-daa* registration files) a4d950a
- 2026-11-13T17:26Z LEAD session_01VfPzNuse9EfjuDwwt7335U SG-7 CODING start eb6ef50 coder session_01VfPzNvgJo8vZQhB3sTbaQr
- 2026-11-13T17:31Z CODER session_01VfPzNuse9EfjuDwwt7335U SG-7 READY b4800ad red:3 of 4 new UI tests failed (step 4 and import panel had no grouping/5-example/'và N nữa', old button style, no shared helper) mutation:removing the 5-example slice in veCanhBaoGom -> 2 UI tests fail, restored
