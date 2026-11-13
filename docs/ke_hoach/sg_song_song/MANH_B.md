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

## SG-8 (M5, invariant 6) — step 1 of "Chuẩn bị đợt" speaks both languages
**CHANGELOG entry:** SG-8 — step-1 messages leave the API as codes. `api_forms._dong_bao_cao` returns `{ma, clb, code: "phieu_nd_<ma>", params: {clb}}` (13 new codes in the SG-B block of `i18n_errors.py`, vi text = the old `NOI_DUNG` wording behind "<CLB>: ", en added; `i18n_loi.js` regenerated); `theo_loai` is keyed by Loại code (TU_DO / GIOI_HAN / TUYEN_CHON) instead of the Vietnamese label; `loai_nhan` removed from the club rows (UI uses `loai`, label via existing `fa_loai_*` keys); `chan` (checks before the gate) is the raw `{code, params}` list instead of pre-translated Vietnamese; the "no valid club" failure returns `phieu_clb_tep_sai` + one code per skipped club (or new `phieu_clb_khong_co_clb_hop_le`) instead of a Vietnamese `detail`. `js/11_chuan_bi.js`: `nhanLoai`, `nhanBuoi` (session code -> `buoi_ma_*`), `noiDung = trErr`, `b1.chan.map(trErr)`, and a `langchange` listener that redraws the steps (so a language switch after loading the file now updates step 1 and 2). Files NOT changed on purpose: `chuyen_phieu_clb.NOI_DUNG` / `so_nhap.NHAN_LOAI_HIEN_THI` stay as constants only for the files the software writes (Sổ nhập "Loại" column, `BAO_CAO_PHIEU_CLB.md`); the UI path no longer reads them. Generator output and the .md report are byte-identical (golden text in the test, taken from the pre-SG-8 code).
Files: `api_forms.py`, `i18n_errors.py`, `i18n_loi.js`, `js/11_chuan_bi.js` (person C's file: step-1 draw functions + the new listener only), `tests/test_ws_nhan.py` (`MA_MOI_SAU_ANH_CHUP`, SG-B block).
New tests: `tests/test_sg8_thong_bao_buoc1.py` (8), `tests/test_giao_dien_sg8_buoc1_tieng_anh.py` (2, Chromium vi + en).
**TIEN_DO line:** SG-8 (M5) | done | files above | tests/test_sg8_thong_bao_buoc1.py (8), tests/test_giao_dien_sg8_buoc1_tieng_anh.py (2).
Note for A/C: vi UI change that is deliberate: the "Buổi `thu_3`" check line (FA gate check) now reads `Buổi "Thứ 3"` (the existing session-label rule `nhanHoaBuoi` applies now that the error is rendered by the UI). Step 4 (`api_forms_nap.py` `noi_dung`) is another list and was not touched (SG-8 scope = step 1). `js/11_chuan_bi.js` for SG-9: call sites unchanged.

## SG-8 FIX-1 — rounds saved before SG-8
**CHANGELOG entry:** SG-8 FIX-1 — `get_forms_buoc_12` maps old saved `loi`/`canh_bao` items `{ma, clb, noi_dung}` to `{code: "phieu_nd_<ma>", params: {clb}}` when `code` is absent and the `ma` is known; an unknown `ma` stays as stored and `js/11_chuan_bi.js` `noiDung` shows "<CLB>: <noi_dung>" for items without `code`. Legacy `theo_loai` (Vietnamese labels) and string `chan` entries keep showing as stored. Comment in `11_chuan_bi.js` corrected. English UI test now asserts a real English sentence (mutation `noiDung = x.clb + ": " + x.code` turns it red). New tests: old-shape JSON in `tests/test_sg8_thong_bao_buoc1.py` (1) and `tests/test_giao_dien_sg8_buoc1_tieng_anh.py` (2, vi + en).
**TIEN_DO line:** SG-8 FIX-1 | done | api_forms.py, js/11_chuan_bi.js | tests above.

## SG-11b (M4) — workspace chooser dialog focus
**CHANGELOG:** SG-11b (M4): `js/075_workspace.js` — new `wsBayTab` (document-level `keydown`, registered in `initWorkspace`): while a `.ws-overlay` is shown, Tab / Shift+Tab cycle inside the topmost one (chooser, wizard, edit row, and the FG-1 "features after allocation" dialog); focus that escaped is pulled back. Already present and kept: initial focus on the heading (`wsVeDanhSach` / wizard), `aria-modal="true"` in `index.html`, Esc closes only when `wsCoTheDong`, focus back to `#btnWorkspace` in `wsDongManChon`. New tests: `tests/test_giao_dien_sg11b_focus_man_chon.py` (5, Chromium). No new strings, no CSS.
**TIEN_DO:** SG-11b (M4) done — see CHANGELOG fragment above.
