# SG parallel — person B status (single source of truth)

Mode: SG_SONG_SONG person B
LOCK: LEAD session_01YVAytz9tLyA9nbFitcHYj9 2026-11-13T15:30Z
STATUS: RUNNING
BASE: 98709f1f374368c65ee2833467715fd933dc84f6   SNAPSHOT: worktree of BASE; for m in "" --fa-daa "--fa-daa --mot-bieu-mau" --bien-the --chi-thi --phan-hoi --sau-ket-qua --tuan-3: `python mau_forms_thi_clb/tao_mau_forms.py $m --ra <dir>`. Default mode IGNORES --ra (rewrites MAU_XUAT_TU_FORMS.xlsx + NHAP_FORMS_THI_CLB.docx in place: copy them out, then `git checkout -- .`); --bien-the writes nothing (no de_thi_bien_the in de_thi.json). Compare without docProps/core.xml.

## Items
| Item | State | Round | Start | End | Coder session | Checker session | Tests |
|---|---|---|---|---|---|---|---|
| SG-2 (C1) | DONE | 0 | 5c8ee63 | d9da2c5 | session_01YVAyu23VvGaoDixHWJZn1G | session_01YVAyu3aEQRoHtkKoFwqkCc | tests/test_sg2_wharton_trong.py, tests/test_giao_dien_sg2_diem_quyet_tam.py |
| SG-6 (H1, D1 = A) | CODING | 0 | dc0451b | | session_01YVAyu2N9LpsmHLzKjBUGzq | | |
| SG-8 (M5) | TODO | 0 | | | | | |
| SG-11b (M4 only) | TODO | 0 | | | | | |

## Fix lists

### SG-2 regression (found by lead during SG-6, round "pre-check")
1. `mau_csv/SO_NHAP_CLB.xlsx` not regenerated after the SG-2 guide-sentence change -> `tests/test_t1b_nhan_trung_cu.py::test_t1a_so_mau_tinh_trung_so_mau_phan_mem_tao_moi_sheet` red (passes at 5c8ee63). Sent to SG-6 coder as a separate commit `SG-2 FIX-1`. Lesson: lead runs the full non-UI suite before each checker.

## Decisions
- SG-11b = finding M4 only (dialog focus trap + Esc + initial focus in `wsMoManChon`); M6/M7/L1/L4/L5 belong to person A (SG-11a).
- Strings go only inside the `=== SG-B: add below ===` … `=== end SG-B ===` marker blocks; CSS only in the SG-B block at the end of `style.css`.
- CHANGELOG / TIEN_DO lines go to `docs/ke_hoach/sg_song_song/MANH_B.md` (lead A folds them in).

- SG-2: blocked-run headline text (`wharton_ho_so_chua_hop_le`) left unchanged (old test B3 forbids "tắt"; extra entries in `errors` break detail-list tests). The "turn it off" hint + button "Mở Tính năng sau khi xếp…" live in `showLog` (js/02_van_hanh.js, person C's file, one row + one button).
- SG-2: preview warning is per fund (tested / untested) per day, mirroring `tu_dien_wharton_mot_clb`, so one-club funds (auto-filled) are not flagged.
- SG-2: updated `BAM_SO_MAU_MAC_DINH` in tests/test_fg2_xem_truoc_fa.py and regenerated du_lieu_test/SO_NHAP_DQT_*.xlsx: only the Hướng dẫn sheet changed (guide sentence, item 3).

- SG-2 lead review: accepted checker PASS; reran item tests + test_fg2/test_ws_nhan/test_van_phong_tu_nhien (78 passed, UI ran) and kiem_nhanh 7/7 (60 cases identical). Checker optional notes (hint shown also under FA; English dialog not eyeballed) left as non-blocking; lead A may re-check at integration.

- SG-6: "student notice" read as the student timetable (get_thoi_khoa_bieu cell + Excel timetable/Theo lớp cell "Tên (giờ, địa điểm)"); no separate notice exists in the app. Keys gio/dia_diem are added to API responses only when some club has them (old data: responses unchanged). Club CSV (not student CSV) accepts optional gio/dia_diem columns.
- SG-6: soat-ma four tiers not run as a separate pass; kiem_nhanh 7/7 (60 cases identical), ruff clean, 91 related test files: 1889 passed, 2 red.

## For Truong
(none)

## Log
2026-11-13T15:30Z LEAD session_01YVAytz9tLyA9nbFitcHYj9 - branch claude/sg-b created from BASE 98709f1
2026-11-13T15:26Z LEAD session_01YVAytz9tLyA9nbFitcHYj9 SG-2 CODING coder=session_01YVAyu23VvGaoDixHWJZn1G start=daca446
2026-11-13T15:35Z LEAD session_01YVAytz9tLyA9nbFitcHYj9 - generator snapshot of BASE taken (lead scratchpad, recipe above)
2026-11-13T15:55Z CODER session_01YVAyu23VvGaoDixHWJZn1G SG-2 READY d9da2c5 red:tests/test_a13_12_tai_lieu.py::test_ban_do_ma_so_tep_test_la_so_that (known) mutation:len(ds)>=99 -> test_diem_toan_0_van_bao+1 red; hopW.disabled=true -> UI switch test red; restored
2026-11-13T16:15Z LEAD session_01YVAytz9tLyA9nbFitcHYj9 SG-2 CHECKING checker=session_01YVAyu3aEQRoHtkKoFwqkCc range=5c8ee63..d9da2c5
2026-11-13T16:29Z CHECKER session_01YVAyu3aEQRoHtkKoFwqkCc SG-2 PASS
2026-11-13T16:50Z LEAD session_01YVAytz9tLyA9nbFitcHYj9 SG-2 DONE (checker PASS c70048f + lead review, kiem_nhanh 7/7) d9da2c5
2026-11-13T16:51Z LEAD session_01YVAytz9tLyA9nbFitcHYj9 SG-6 CODING coder=session_01YVAyu2N9LpsmHLzKjBUGzq start=dc0451b
2026-11-13T18:10Z CODER session_01YVAyu2N9LpsmHLzKjBUGzq SG-6 READY aad4846 red:tests/test_a13_12_tai_lieu.py::test_ban_do_ma_so_tep_test_la_so_that (known) + tests/test_t1b_nhan_trung_cu.py::test_t1a_so_mau_tinh_trung_so_mau_phan_mem_tao_moi_sheet (pre-existing from SG-2) mutation:so_nhap reader KHOA_GIO disabled -> 5 new tests red; restored
2026-11-13T17:45Z LEAD session_01YVAytz9tLyA9nbFitcHYj9 SG-6 lead sweep at aad4846: 5587 passed, red = a13_12 (known) + t1a (SG-2 regression) -> pre-check fix sent to coder
2026-11-13T17:50Z CODER session_01YVAyu2N9LpsmHLzKjBUGzq SG-6 READY 194305f fix:1 done (sample regenerated in separate commit, only Hướng dẫn differs; t1b/so_mau_co_cot_quyet_tam/a13_13_kiem_nhan/fg2_xem_truoc_fa 82 passed),2 done (sample has no Giờ/Địa điểm columns),3 done
