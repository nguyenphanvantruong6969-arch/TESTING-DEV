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
| SG-5 | CHECKING | 0 | bd6d821 | b9c4f32 | session_01VfPzNruBqHHaJZQcLRxRzS | | tests/test_sg5_huy_chuong.py |
| SG-7 | TODO | 0 | | | | | |
| SG-9 | TODO | 0 | | | | | |
| SG-12 | TODO | 0 | | | | | |

## Fix lists

## Decisions
- WARNING: lead is not Opus (`get_session` reports claude-sonnet-5-5 at setup; the serving model may change).
- Fable's report artifact is unreadable from this account ("artifact not found") → red tests come from the spec text
  of `SOAT_GIAO_DIEN_KE_HOACH.md` and the finding as reproduced in code (SG_SONG_SONG 2.1 fallback).

## For Truong
SG-5 wording (vi; sits in the gold-medal question of each `--fa-daa*` registration form, after the question text; en: none, forms are Vietnamese-only):
"Huy chương giúp em được ưu tiên hơn bạn khác ở CLB đó: CLB có xét điểm thi thì chỉ dùng khi bằng điểm thi, CLB không xét điểm thi thì dùng trước khi bốc thăm. Em không chọn gì thì hệ thống tự đặt vàng cho nguyện vọng 1, bạc cho nguyện vọng 2, đồng cho nguyện vọng 3 (CLB Tự do không có huy chương nên được bỏ qua)."
Changed vs the brief: (1) "medals only break ties after the test score" is true only for clubs WITH scores; in `fa_daa` a Giới hạn club orders by medal BEFORE the lottery (key `(1, -medal, stb)`), so the text says both. (2) "leaving default never hurts" is not provable (not a dominant strategy), so it is NOT claimed. (3) Default is "first/second/third NON-free club", so the text says free clubs are skipped.
Placement is in the question title because Quick Import has no per-section description field (untested on real Forms).

- SG-5: `nt` hashes of fa_daa/fa_daa_mot in tests/test_fg7_bieu_mau_sau_ket_qua.py are STALE (posix re-pinned; Windows CI output needed).

## Log
- 2026-11-13T16:10Z LEAD session_01VfPzNuse9EfjuDwwt7335U setup branch claude/sg-c from BASE 98709f1
- 2026-11-13T15:55Z LEAD session_01VfPzNuse9EfjuDwwt7335U SG-5 CODING start 7f7b5ca coder session_01VfPzNruBqHHaJZQcLRxRzS
- 2026-11-13T16:01Z CODER session_01VfPzNruBqHHaJZQcLRxRzS SG-5 READY 7b7109a red:3 of 6 new tests failed (3 false 'chỉ còn 1 CLB' warnings counted, no description, swap present on 2-club day) mutation:forcing swap on / disabling reader day-size guard -> 2 new tests fail, restored
- 2026-11-13T16:32Z LEAD session_01VfPzNuse9EfjuDwwt7335U SG-5 READY accepted, range bd6d821..b9c4f32 (Start corrected to the assign commit); CHECKING
