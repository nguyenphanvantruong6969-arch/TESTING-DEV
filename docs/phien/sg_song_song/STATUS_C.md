Mode: SG_SONG_SONG person C
LOCK: LEAD session_01VfPzNuse9EfjuDwwt7335U 2026-11-13T16:10Z
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
| SG-5 | TODO | 0 | | | | | |
| SG-7 | TODO | 0 | | | | | |
| SG-9 | TODO | 0 | | | | | |
| SG-12 | TODO | 0 | | | | | |

## Fix lists

## Decisions
- WARNING: lead is not Opus (`get_session` reports claude-sonnet-5-5 at setup; the serving model may change).
- Fable's report artifact is unreadable from this account ("artifact not found") → red tests come from the spec text
  of `SOAT_GIAO_DIEN_KE_HOACH.md` and the finding as reproduced in code (SG_SONG_SONG 2.1 fallback).

## For Truong

## Log
- 2026-11-13T16:10Z LEAD session_01VfPzNuse9EfjuDwwt7335U setup branch claude/sg-c from BASE 98709f1
