# SG parallel — person B status (single source of truth)

Mode: SG_SONG_SONG person B
LOCK: LEAD session_01YVAytz9tLyA9nbFitcHYj9 2026-11-13T15:30Z
STATUS: RUNNING
BASE: 98709f1f374368c65ee2833467715fd933dc84f6   SNAPSHOT: worktree of BASE; for m in "" --fa-daa "--fa-daa --mot-bieu-mau" --bien-the --chi-thi --phan-hoi --sau-ket-qua --tuan-3: `python mau_forms_thi_clb/tao_mau_forms.py $m --ra <dir>`. Default mode IGNORES --ra (rewrites MAU_XUAT_TU_FORMS.xlsx + NHAP_FORMS_THI_CLB.docx in place: copy them out, then `git checkout -- .`); --bien-the writes nothing (no de_thi_bien_the in de_thi.json). Compare without docProps/core.xml.

## Items
| Item | State | Round | Start | End | Coder session | Checker session | Tests |
|---|---|---|---|---|---|---|---|
| SG-2 (C1) | CODING | 0 | daca446 | | session_01YVAyu23VvGaoDixHWJZn1G | | |
| SG-6 (H1, D1 = A) | TODO | 0 | | | | | |
| SG-8 (M5) | TODO | 0 | | | | | |
| SG-11b (M4 only) | TODO | 0 | | | | | |

## Fix lists

## Decisions
- SG-11b = finding M4 only (dialog focus trap + Esc + initial focus in `wsMoManChon`); M6/M7/L1/L4/L5 belong to person A (SG-11a).
- Strings go only inside the `=== SG-B: add below ===` … `=== end SG-B ===` marker blocks; CSS only in the SG-B block at the end of `style.css`.
- CHANGELOG / TIEN_DO lines go to `docs/ke_hoach/sg_song_song/MANH_B.md` (lead A folds them in).

## For Truong

## Log
2026-11-13T15:30Z LEAD session_01YVAytz9tLyA9nbFitcHYj9 - branch claude/sg-b created from BASE 98709f1
2026-11-13T15:26Z LEAD session_01YVAytz9tLyA9nbFitcHYj9 SG-2 CODING coder=session_01YVAyu23VvGaoDixHWJZn1G start=daca446
2026-11-13T15:35Z LEAD session_01YVAytz9tLyA9nbFitcHYj9 - generator snapshot of BASE taken (lead scratchpad, recipe above)
