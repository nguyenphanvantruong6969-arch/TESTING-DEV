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
