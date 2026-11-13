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

## SG-6 (H1, D1 = A) — club time and room are kept and shown
**CHANGELOG entry:** SG-6 — nullable `clubs.gio` / `clubs.dia_diem` (TEXT) added via `di_tru_schema` (same pattern and same single
backup as the FA columns: `_them_cot_fa_cho_clb`; fresh DBs get them in `_BANG_RANG_BUOC["clubs"]`); second run = no-op. Sổ nhập CLB
sheet gets two OPTIONAL columns "Giờ" / "Địa điểm" (`so_nhap`: `COT_GIO`, `KHOA_GIO`; reader, `thanh_csv`, `ghi_so_nhap`; absent
column = keep stored value, empty cell = clear; written only when some club carries them, so old workbooks stay byte-identical).
`chuyen_phieu_clb` carries `C_GIO` / `C_DIA_DIEM` into the clubs. `import_clubs_csv` (club CSV only, NOT the student CSV contract)
reads the two optional columns. Shown only when filled: step-1 table (`_clb_hien_thi`, `bangClb`), Quản lý (`list_clubs_admin`),
results "Theo từng câu lạc bộ" (`get_club_fill_stats`, `get_danh_sach_clb`), student timetable (`get_thoi_khoa_bieu`), Excel sheets
"Theo CLB" (header line) and "Theo lớp" / timetable (cell "Tên (giờ, địa điểm)"), and the exported Sổ nhập round-trips them.
DA core, CSV contract and `match_results` untouched. Files: `rbda_priority_pipeline.py` (schema + `_them_cot_fa_cho_clb` list only),
`so_nhap.py`, `mau_forms_thi_clb/chuyen_phieu_clb.py`, `api_nhap.py`, `api_forms.py`, `api_bao_cao.py`, `api_quan_ly.py`, `api_xuat.py`,
`js/075_workspace.js` (helpers `chuGioDiaDiem`, `gioDiaDiemHtml`), `js/11_chuan_bi.js`, `js/03_ket_qua.js`, `js/05_quan_ly.js`,
`js/09_the_xem.js`, `i18n.js` (SG-B block: `cb_cot_gio`, `cb_cot_dia_diem`), `style.css` (SG-B block).
New tests: `tests/test_sg6_gio_dia_diem.py`, `tests/test_giao_dien_sg6_gio_dia_diem.py`.
**TIEN_DO line:** SG-6 (H1) | done | files above | tests/test_sg6_gio_dia_diem.py (11), tests/test_giao_dien_sg6_gio_dia_diem.py (2).
Note for A: touched `js/03_ket_qua.js` (your file) in two lines only — the `clb-ten` cell of the "Theo từng câu lạc bộ" table gets
`${gioDiaDiemHtml(c)}`, and the member-list title gets " · giờ, địa điểm". Also `js/09_the_xem.js` in two lines (timetable cell,
member-count line) and `js/05_quan_ly.js` (person C) in one cell of `loadAdminClubs`. All no-ops when the fields are empty.

## SG-2 FIX-1 (done during SG-6)
**CHANGELOG entry:** SG-2 FIX-1 — regenerated `mau_csv/SO_NHAP_CLB.xlsx` with `mau_csv/tao_so_nhap.py` after the SG-2 Hướng dẫn sentence change; cell diff vs 5c8ee63: only the Hướng dẫn sheet differs (other generated workbooks left untouched). **TIEN_DO line:** SG-2 FIX-1 | done | mau_csv/SO_NHAP_CLB.xlsx | tests/test_t1b_nhan_trung_cu.py green.

## SG-6 FIX-1 — real Forms route
**CHANGELOG entry:** SG-6 FIX-1 — `gio` / `dia_diem` now survive the real route: `so_de_thi.doc_clb_dot` (step-1 table redraw) and `chuyen_forms_sang_phan_mem.doc_clb_fa` (step 4 -> Sổ -> import) carry them only when the club declared them (no key otherwise, so workbooks without them are unchanged). New tests: Phiếu -> `chuyen_phieu` -> `chuyen_fa_daa` -> Sổ -> `import_so_nhap` -> `clubs.gio/dia_diem` (3 tests in `tests/test_sg6_gio_dia_diem.py`); Chromium upload through `#cb-b1-tep` shows two extra columns (vi + en) and exactly 4 columns without them (`tests/test_giao_dien_sg6_gio_dia_diem.py`). Generator snapshot (8 modes) identical to BASE.
**TIEN_DO line:** SG-6 FIX-1 | done | so_de_thi.py, chuyen_forms_sang_phan_mem.py | tests above.
Note for A: `mau_forms_thi_clb/chuyen_forms_sang_phan_mem.py` (person C's file) — one tuple in `doc_clb_fa` extended with "gio", "dia_diem" (SG-12 should keep it). Known: the step-1 table does not redraw on a language switch (pre-existing); the UI test switches language before uploading.
