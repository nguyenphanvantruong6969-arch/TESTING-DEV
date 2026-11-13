# Fragments for person A (lead A folds these into CHANGELOG.md / TIEN_DO.md at integration)

## SG-1 (C3) — selective club that nobody can pass

### CHANGELOG entry
- **SG-1 (C3)**: a TUYEN_CHON club that has applicants (students listing it) but no score row at all now blocks the
  FA run with `fa_clb_tuyen_chon_chua_co_diem` {club_id, so_dang_ky, so_nv1}; the same check shows as a "high" line in
  `get_data_health_report`. Files: `fa_daa.py` (`kiem_truoc_fa` gets optional `tested_scores`; `kiem_fa_tu_csdl` reads
  `club_scores`), `i18n_errors.py` (SG-A block, vi + en), `i18n_loi.js` (regenerated), `tests/test_ws_nhan.py`
  (`MA_MOI_SAU_ANH_CHUP`), `tests/test_fa_huy_chuong.py` (one existing test now gives club S a score, because it built
  exactly the blocked case). Default (non-FA) behaviour unchanged. New tests: `tests/test_sg1_tuyen_chon_khong_diem.py`.

### TIEN_DO line
- SG-1 (C3) — done: selective club with no scores blocks the run and is flagged in the health report.

## SG-3 (C2) — preference rank in FA mode

### CHANGELOG entry
- **SG-3 (C2)**: in FA mode `match_results.rank_in_student_pref` is now the position in the student's ORIGINAL list
  within the session (same value as `rank_in_list` in `fa_ly_do`), not the position in the trimmed/augmented in-memory
  list; a student placed by the fallback step into a TU_DO club they never listed gets NULL (decision D3).
  `get_phan_bo_nguyen_vong` returns a new key `ngoai_danh_sach` (placed, rank NULL, club never listed); `khong_ro` now
  counts only the rest. Panel + results export show "Xếp ngoài danh sách nguyện vọng" / "Placed outside their choices".
  Dashboard "Vào NV1" reads the corrected value (formula unchanged). Files: `fa_daa.py` (`chay_fa_daa`, step 7, output
  only; DA core untouched), `api_bao_cao.py`, `api_xuat.py`, `js/03_ket_qua.js`, `i18n.js` (SG-A block, vi + en).
  Default (non-FA) path unchanged (kiem_nhanh 60/60). New tests: `tests/test_sg3_hang_fa.py` (5).

### TIEN_DO line
- SG-3 (C2) — done: FA stores the original-list rank; fallback placements are NULL and shown separately.

## SG-4 (M3) — một luật khớp mã học sinh cho khiếu nại gõ tay
- CHANGELOG: `api_sau_xep.gui_khieu_nai` khớp mã bằng `fa_sau_xep.khop_ma_hoc_sinh` như đường Forms (đúng thắng; không thì `strip().casefold()` nếu đúng MỘT; mơ hồ bị từ chối); mã lưu không bị đổi. Tách lỗi: `khieu_nai_hs_khong_co` (không có học sinh) và `khieu_nai_chua_co_ket_qua` (có học sinh, chưa có kết quả ở buổi đó). Mã cũ `khieu_nai_khong_hop_le` giữ cho đường Forms (`nhap_sau_ket_qua_forms`). Tệp: `api_sau_xep.py`, `i18n_errors.py` (khối SG-A), `i18n_loi.js`, `tests/test_ws_nhan.py`. Test mới: `tests/test_sg4_khop_ma.py` (4); sửa 2 khẳng định cũ ở `test_fa_gap3_khieu_nai.py`, `test_fa_m6b_sau_ket_qua.py`.
- TIEN_DO: SG-4 (M3) xong, chờ soát.
