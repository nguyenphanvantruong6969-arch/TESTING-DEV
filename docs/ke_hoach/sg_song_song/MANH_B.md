# Fragment — person B (SG-2, SG-6, SG-8, SG-11b)

## SG-2 (C1) — default workspace must not trap a new user
**CHANGELOG entry:** SG-2 — `Trường học` template keeps `wharton: true` (invariant 1). (1) FG-1 dialog "Tính năng sau khi xếp…"
gets a switch "Dùng điểm quyết tâm" (`rules.wharton`; locked with a reason when `fa_daa` is on). (2) Workbook preview warns
(`so_nhap_canh_bao_wharton_trong`, one grouped line with count + example id) about students with ≥ 2 choices of the same
day/fund and no commitment points. (3) Hướng dẫn sheet no longer says "ô trống tính là 0" unconditionally. (4) Blocked-run
log gets a hint line + button "Mở Tính năng sau khi xếp…". Files: `api_nhap.py` (`_canh_bao_wharton_trong_xem_truoc`),
`so_nhap.py` (guide text), `js/075_workspace.js` (`wsMoTinhNang`, `wsMoTinhNangDangMo`), `js/02_van_hanh.js` (`showLog`, call site only),
`i18n_errors.py`, `i18n_loi.js`, `i18n.js`, `style.css`, `tests/test_ws_nhan.py`, `tests/test_fg2_xem_truoc_fa.py` (hash of default
sample workbook updated: only the Hướng dẫn sheet changed), `du_lieu_test/SO_NHAP_DQT_*.xlsx` (regenerated; only the Hướng dẫn sheet differs).
New tests: `tests/test_sg2_wharton_trong.py`, `tests/test_giao_dien_sg2_diem_quyet_tam.py`.
**TIEN_DO line:** SG-2 (C1) | done | files above | tests/test_sg2_wharton_trong.py (7), tests/test_giao_dien_sg2_diem_quyet_tam.py (3).
Note for A: touched `js/02_van_hanh.js` (person C's file) only in `showLog` (one hint row + one button).
