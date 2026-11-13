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
