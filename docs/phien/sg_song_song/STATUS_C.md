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
| SG-7 | DONE | 0 | 9709a20 | b4800ad | session_01VfPzNvgJo8vZQhB3sTbaQr | session_01VfPzNv27d7DuoAmjt9g79n | (UI tests, see review) |
| SG-9 | FIX-1 | 1 | a1b6ecb | 98908e1 | session_01VfPzNud4JhboVzj5e8xu4E | session_01VfPzNt6qaZtDuK7uYC28bX | (see review) |
| SG-12 | TODO | 0 | | | | | |

## Fix lists
### SG-5 FIX-1 (checker session_01VfPzNrFdN7RhAERrSNeTJV, docs/phien/sg_review/SG-5.md)
1. tests/test_fg7_bieu_mau_sau_ket_qua.py: for `fa_daa`, `fa_daa_mot` ONLY add a platform-independent content digest
   (sorted relative names + bytes of .md files + paragraph/table text of each .docx via python-docx), pinned once on
   posix, asserted on BOTH OSes; keep the posix byte hash as is.
2. On nt, for these two modes, skip only the byte-hash assert (reason string names SG-5), not the whole test.
3. Fix the overlong two-sentence comment line in that file.

### SG-9 FIX-1 (LEAD disagrees with checker PASS on two cheap points; checker notes 1-2 in docs/phien/sg_review/SG-9.md)
1. tests/test_giao_dien_sg9_nut_ban.py: make the `.catch` inside `chayNut` (and `chayTai`) provable — e.g. in the rejection test
   assert NO `unhandledrejection` reached the page (stub/count it) and exactly ONE error toast. Verify: removing that `.catch` must
   make the test fail.
2. js/12_chuan_bi_nap.js `chuyen` (`S.dang`) and the `goi` helper (`S5.dang`): reset the busy flag in the wrapper's `sauCung`
   (finally) so a synchronously thrown API call does not leave the step dead; add a UI test (API function that throws
   synchronously → second click makes a second call).

## Decisions
- WARNING: lead is not Opus (`get_session` reports claude-sonnet-5-5 at setup; the serving model may change).
- Fable's report artifact is unreadable from this account ("artifact not found") → red tests come from the spec text
  of `SOAT_GIAO_DIEN_KE_HOACH.md` and the finding as reproduced in code (SG_SONG_SONG 2.1 fallback).

- SG-7: helper placed in js/00_nen.js (no A/B edits there). Step-4 warning prefix `ma:` (internal code) dropped from visible text; old `slice(0,30)` cap replaced by the 5-example rule. Old i18n keys canh_bao_gom/xem_dau/thu_gon left (outside SG-C block).
- SG-7: dead leftovers outside the SG-C blocks (i18n keys `canh_bao_gom`, `canh_bao_xem_dau`, `canh_bao_thu_gon`; old `.canh-bao-nhom` flex rule in style.css) are left for lead A at integration, to avoid editing outside C's marker blocks. The FG-6 run-log grouping (`showLog`) stays as is: same rule in spirit, not one of SG-7's two surfaces.
- SG-9 (seen by checker, out of C scope): the khiếu nại error text shows the internal session name `__mac_dinh__` → for person A (SG-4 owns `gui_khieu_nai`).

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
- 2026-11-13T17:31Z CODER session_01VfPzNvgJo8vZQhB3sTbaQr SG-7 READY b4800ad red:3 of 4 new UI tests failed (step 4 and import panel had no grouping/5-example/'và N nữa', old button style, no shared helper) mutation:removing the 5-example slice in veCanhBaoGom -> 2 UI tests fail, restored
- 2026-11-13T17:48Z LEAD session_01VfPzNuse9EfjuDwwt7335U SG-7 READY b4800ad accepted (range 9709a20..b4800ad); checker r1 session_01VfPzNv27d7DuoAmjt9g79n
- 2026-11-13T17:51Z CHECKER session_01VfPzNv27d7DuoAmjt9g79n SG-7 PASS (see docs/phien/sg_review/SG-7.md)
- 2026-11-13T18:14Z LEAD session_01VfPzNuse9EfjuDwwt7335U SG-7 DONE (lead review: diff read; 17 UI tests pass in Chromium; own mutation 'và N nữa' count -> 2 fail, restored; checker kiem_nhanh 7/7, diff JS/CSS/i18n only) b4800ad
- 2026-11-13T18:11Z LEAD session_01VfPzNuse9EfjuDwwt7335U SG-9 CODING start 1bf5e85 coder session_01VfPzNud4JhboVzj5e8xu4E
- 2026-11-13T18:29Z CODER session_01VfPzNud4JhboVzj5e8xu4E SG-9 READY 98908e1 red:14 of 16 new tests failed on base (no busy state/double-click guard/.catch, 71 bare .then) mutation:removing nut.disabled=true in chayNut -> 5 double-click tests fail, restored; related: 606 UI/label tests pass, ruff clean
- 2026-11-13T18:38Z LEAD session_01VfPzNuse9EfjuDwwt7335U SG-9 READY 98908e1 accepted (range a1b6ecb..98908e1); checker r1 session_01VfPzNt6qaZtDuK7uYC28bX
- 2026-11-13T18:59Z CHECKER session_01VfPzNt6qaZtDuK7uYC28bX SG-9 PASS (a1b6ecb..98908e1; 495 UI tests passed 0 skipped, own mutation: removing .catch survives because unhandledrejection shows same toast -> notes only; see docs/phien/sg_review/SG-9.md)
- 2026-11-13T19:06Z LEAD session_01VfPzNuse9EfjuDwwt7335U SG-9 checker PASS overruled -> FIX-1 (2 points), sent to coder session_01VfPzNud4JhboVzj5e8xu4E
