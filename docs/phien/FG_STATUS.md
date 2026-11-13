Mode: CHU_TRI_FG
RUNNING CHU_TRI_FG session_01VfPzNt8wLhNQyk5sYejKse 2026-11-13T01:14Z
STATUS: RUNNING

# FG status (FG-1 … FG-9, after user test of forms-gop)

> English, ≤ 150 lines. Spec: `docs/ke_hoach/FORMS_GOP_SUA_KE_HOACH.md`; mechanics: `docs/ke_hoach/FG_TU_DONG.md`.
> All numbers SIMULATED; all Forms work TH.

BASE = f5e8a41 (origin/claude/forms-gop at start)

## Current step
- STEP0 (spec §1b): delegate to a Sonnet worker.

## Item table
| Item | State | Commit | Tests |
|---|---|---|---|
| STEP0 | TODO | | |
| FG-1 | TODO | | |
| FG-3 | TODO | | |
| FG-4 | TODO | | |
| FG-5 | TODO | | |
| FG-6 | TODO | | |
| FG-2 | TODO | | |
| FG-7 | TODO | | |
| FG-8 | TODO | | |
| FG-9 | TODO | | |

## Snapshots
- Rebuild from BASE: `git worktree add <scratch>/base f5e8a41`, then in it run
  `mau_forms_thi_clb/tao_mau_forms.py <mode> --ra <scratch>/snap/<name>` for `--fa-daa`, `--fa-daa --mot-bieu-mau`,
  `--phan-hoi`, `--tuan-3` (and `--sau-ket-qua` for reference). Output verified deterministic (two runs, `diff -r` clean).
- Lead copy: `<scratchpad of session_01VfPzNt8wLhNQyk5sYejKse>/snap/{fa-daa,fa-daa_mot,phan-hoi,tuan-3,sau-ket-qua}`.

## Decisions
- D1–D4 as spec §1 (final).
- STEP0 commits the red tests it writes (they are each item's acceptance tests, rule 2); the item worker turns them
  green and may extend them. The branch is expected red between STEP0 and FG-9; the green loop runs at FINISH.
  A test already green on HEAD → item GONE-ON-HEAD; keep that test only if it adds coverage.

## Waiting for Truong
- (none yet)

## Workers
| Task | Session | State |
|---|---|---|
| STEP0 | (creating) | |

## Log
- 2026-11-13T01:14Z lead: branch claude/fg-sua created from BASE f5e8a41; lead model claude-opus-5-5; snapshots taken.
- 2026-11-13 WORKER session_01VfPzNuWUv3W6FtiR2fPPpB STEP0 DONE 63b6e73 (tests only, no production code; ruff clean; run on HEAD 24846d2: 41 failed / 15 passed over tests/test_fg*.py + tests/test_giao_dien_fg*.py)
  - FG-1: RED test_giao_dien_fg1_bat_tinh_nang.py::{test_khong_fa_thi_cac_o_bi_khoa_va_co_mot_dong_giai_thich, test_bat_phan_hoi_roi_khung_hien_o_the_chi_tiet, test_so_ngay_ngoai_khoang_giu_hop_thoai_va_hien_loi} (menu item missing). Server side GONE-ON-HEAD: test_fg1_bat_tinh_nang.py (4 API tests green, kept as coverage).
  - FG-2: RED test_fg2_xem_truoc_fa.py::{test_xem_truoc_gom_canh_bao_fa_theo_ma_co_so_dem, test_so_mau_che_do_fa_co_cot_loai_va_nhan_huy_chuong, test_bo_doc_nhan_huy_chuong_nhu_cot_diem_quyet_tam, test_so_mau_fa_120hs_hop_le_xem_truoc_sach_va_chay_duoc}. Green guards kept: default template golden hash, non-FA preview has no fa_* warnings.
  - FG-3: RED test_fg3_nap_lai.py (all 5). Appeal bug CONFIRMED on HEAD: reloading after CHAP_NHAN/TU_CHOI inserts a 2nd appeal (fa_khieu_nai count 2, expected 1).
  - FG-4: RED test_giao_dien_fg4_nut_nap.py::test_nut_bi_khoa_va_hien_dang_nap_khi_goi_api[both buttons]. Error-path tests (abort -> button usable, toast shown) are green on HEAD, kept as regression.
  - FG-5: RED test_fg5_khop_ma.py (all 6; sx.khop_ma_hoc_sinh missing, no ma_khong_khop key).
  - FG-6: RED test_fg6_ket_qua_nap.py (all 5), test_giao_dien_fg6_danh_sach_loi.py::{test_thong_bao_mot_cau_va_khung_co_danh_sach, test_buoc_kiem_tra_du_lieu_gom_loi_theo_ma}.
  - FG-7: RED test_fg7_bieu_mau_sau_ket_qua.py::{test_sau_ket_qua_voi_so_nhap_chi_liet_ke_ngay_co_clb, test_tieu_de_rieng_cho_che_do_sau_ket_qua, test_huong_dan_buoc_4_chi_duong_menu_khong_ten_khoa_cau_hinh, test_help_khong_con_ma_noi_bo, test_in_thu_muc_ra_tuyet_doi_o_dong_cuoi}. Byte-identity guards green (golden sha256 of fa_daa, fa_daa_mot, phan_hoi, tuan_3 trees, taken on HEAD, each deterministic over 2 runs). Spec sub-bullet "one guide line why [tag]/(code) stay": guide step 5 already says the kiosk reads them -> no test, FG-7 worker to judge.
  - FG-8: RED test_fg8_goi_y_suc_khoe.py (2) and test_giao_dien_fg8_cau_chu.py::{summary neutral when n_high=0, wizard 4 boxes disabled, checkbox same line as label, heading "Sau khi công bố kết quả", hide "Chưa chia buổi"}. Green guard: summary red when n_high>0.
  - FG-9: RED test_giao_dien_fg9_ux_nho.py::{test_thanh_ben_khong_con_so_thu_tu, test_tai_so_mau_co_nut_mo_thu_muc_va_tooltip_duong_dan}. Sub-bullet "chưa có chỗ nào · Cần xử lý" link: GONE-ON-HEAD for the KPI card (test_chi_so_chua_co_cho_bam_duoc_va_mo_khung green, kept): `.kpi-o[data-muc=chuaCoChoPanel]` is already a <button> that opens + scrolls the panel.
  - STEP0 notes (re-read vs current layout): (a) sidebar numbers are now 01–07 (07 = "Chuẩn bị đợt", hidden by default), not 01–06; the KPI strip and the "chưa có CLB" panel live in tab data-tab="others" (labelled "Chi tiết và xuất tệp"), not "results". (b) FG-9 "Tải sổ nhập mẫu" (taiSoNhapMau, js/02_van_hanh.js) already calls mo_thu_muc automatically and puts the full path in the toast sentence; test only requires a "Mở thư mục" toast button and the path in a title, whether auto-open stays is the worker's call. (c) FG-8 hide "Chưa chia buổi": label key buoi_chua_chia used by nhanBuoi (js/05_quan_ly.js); `#knBuoi` options show it today. (d) FA-M9: its import step RECOGNISES the after-results file (nhan_dien_tep_forms -> loai sau_ket_qua) but REJECTS it with error forms_tep_sau_ket_qua ("load it in the Feedback panel after allocation"); it does NOT load it. So FG-6/FG-8 do not need FA-M9 code, but FG-8 renames that panel group to "Sau khi công bố kết quả", leaving the wording of forms_tep_sau_ket_qua (i18n_errors.py, vi+en) stale: FG-8 worker should update that message text only (not FA-M9 logic), or log WAIT-TRUONG if it prefers. (e) env: no .venv existed; created with `python3 -m venv .venv` + requirements-dev + playwright==1.63.0 (ignored by git); UI tests run with PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers.
