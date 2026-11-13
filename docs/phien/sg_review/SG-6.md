# SG-6 review (CHECKER, session_01YVAyu1Uy5qgbSS878jxQF4) — range d7c9c19..194305f, branch claude/sg-b

**Verdict: FIX-1** (Round 0 → FIX-1). The schema, reader, exports and tests are sound, but the user's real path
(teacher Phiếu → "Chuẩn bị đợt" step 1 → step 4 → import) still loses the time and room, so the spec acceptance
("a club form export with 15:30-17:00 / Sân A → visible in each listed place") is not met. All data are SIMULATED.

## Fix list (FIX-1)
1. **Step-1 table never shows Giờ/Địa điểm in the real UI.**
   `mau_forms_thi_clb/so_de_thi.py::doc_clb_dot` whitelists the keys it returns
   (`club_id, name, buoi, capacity, reserve_capacity, reserve_group, loai`), so `api_forms.py::get_forms_buoc_12`
   (what `js/11_chuan_bi.js::veBuoc1` redraws from after every upload, via `lamMoi()`) returns clubs without
   `gio`/`dia_diem`, and `coGio` is always false. Only the one-shot return value of `nap_phieu_clb` has them, and
   the UI discards it. Why: spec §3 SG-6 lists the step-1 table; finding H1. The new test only checks
   `_clb_hien_thi` on hand-made dicts. Verify: in Chromium upload a Phiếu with "15:30-17:00" / "Sân A" through
   `#cb-b1-tep` → `#cb-b1-bang` has two extra headers (Giờ/Địa điểm, vi and en) and the values; a Phiếu without
   them → the table has exactly 4 columns as before. Add that UI test (upload through the input, not `_clb_hien_thi`).
2. **Step 4 drops them, so they never reach `clubs` in the real teacher flow.**
   `mau_forms_thi_clb/chuyen_forms_sang_phan_mem.py::doc_clb_fa` keeps only
   `("loai","capacity","diem_san","so_toi_thieu","suc_chua_phong")`, and `ghi_tep_phan_mem` builds the club dicts
   from `de["cau_lac_bo"]` + `clb_fa`. I ran it on the step-1 file written by `nap_phieu_clb` (it holds
   `Giờ`/`Địa điểm` = 15:30-17:00 / Sân A): `doc_clb_fa` returns no gio/dia_diem and the final `1. CLB` sheet has no
   Giờ/Địa điểm columns. So Quản lý, "Theo từng câu lạc bộ", Excel "Theo CLB"/"Theo lớp", rosters and the timetable
   never show them after the Forms → Sổ → import route (the only route that uses `chuyen_phieu_clb`).
   Fix: carry `gio`/`dia_diem` through `doc_clb_fa` and into the club dicts only when present (no key when empty →
   workbooks for data without them stay byte-identical). Verify: test Phiếu → `chuyen_phieu` → `chuyen_fa_daa`
   (or `chuyen_tep_forms`) → Sổ has the two columns → `import_so_nhap` → `clubs.gio='15:30-17:00'`,
   `clubs.dia_diem='Sân A'`; same chain with a Phiếu without them → Sổ identical to the one built at d7c9c19.

## Optional (do not block)
- Excel header labels `Giờ: ` / `Địa điểm: ` in `api_xuat.py` are hard-coded Vietnamese (same as the neighbouring "Đã xếp %d/%d chỗ", so consistent).
- Quản lý: the second line (time · room) is tight against the row below at 1920 px; cosmetic.

## Checklist 2.10 + lead points — evidence
1. **Scope:** diff = nullable `clubs.gio/dia_diem`, reader/`thanh_csv`/`ghi_so_nhap`, `chuyen_phieu_clb`, `api_nhap` club CSV, displays in `_clb_hien_thi`, `list_clubs_admin`, `get_club_fill_stats`, `get_danh_sach_clb`, `get_thoi_khoa_bieu`, Excel "Theo CLB"/"Theo lớp"/timetable, i18n/CSS in SG-B blocks. Nothing extra. Two places of the spec are not reached in the real flow → FIX-1 items 1-2.
2. **Red-first:** worktree at d7c9c19 + only the two new test files → 10 failed, 3 passed (the 3 are the "old data unchanged" guards); at 194305f → 13 passed.
3. **Mutation (scratch worktree at 194305f):** drop the two ALTER entries → 2 red; `KHOA_GIO = ()` (reader off) → 6 red; UI cells off (`gioDiaDiemHtml`/timetable cell) → 1 red; Excel header/cell off → 1 red. All restored/discarded.
4. **Tests ran for real:** new tests + `test_t1b_nhan_trung_cu` + SG-2 tests = 30 passed, 0 skipped (Chromium, `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`). Related non-UI set (so_nhap, schema, xuat, bao_cao, thoi_khoa, fa_m1, forms, phieu, a14, quan_ly, wharton_so_nhap, ws_so_nhap: 38 files) = 487 passed. `ruff check .` clean.
5. **Invariants:** `kiem_nhanh --co-so origin/main --so-seed 20` = 7/7, 60 cases (3 sets × 20 seeds) byte-identical. `gio`/`dia_diem` appear in `rbda_priority_pipeline.py` only in the table DDL and the ALTER list; DA core and `compute_club_priority` untouched (inv. 2, 5 unchanged). `{ok,data,errors}` kept; no new error codes. Student CSV contract (`club_id, student_id, test_club_k, score_k, pref_k, <buoi>_pref_k`) untouched: `thanh_csv` appends `gio`/`dia_diem` to the CLUBS csv only, and only when some club carries them; `api_nhap.import_clubs_csv` reads them only `if k in fieldnames` (absent column = keep stored value, present column + empty cell = NULL). SQL parameterised; the only interpolated text is the column names, taken from the constant `so_nhap.KHOA_GIO`. `_ghi_clb` is an UPSERT that does not list the two columns, so UI/CSV edits never wipe them.
6. **Strings:** `cb_cot_gio` Giờ/Time, `cb_cot_dia_diem` Địa điểm/Place, inside the SG-B marker block of `i18n.js` (vi and en); no internal codes; CSS in the SG-B block of `style.css`. `i18n_errors.py` untouched.
7. **UI (Chromium, browser_host, data outside the repo, no page errors, no horizontal overflow):** 1366×768 vi and 1920×1080 en — Quản lý table, results "Theo từng câu lạc bộ", per-club member caption, results by student ("CLB Cờ vua (15:30-17:00 · Sân A)"), long text (club name + long room name) wraps without overflow; club without data shows no extra text. **Step-1 table (Chuẩn bị đợt) at the same sizes: 4 columns only even with a Phiếu that has time and room → FIX-1 item 1.**
8. **soat-ma:** `kiem_nhanh` all 7 items PASS (ruff, forbidden words, JS error codes, i18n match/keys, byte-identical, no UPDATE/DELETE on history tables); tiers 1-3 read on the diff (no DA-core edit, parameterised SQL, backward-compatible reads); tier 4: MANH_B.md declares every touched file.
9. **Special (SG-6):** (a) `_them_cot_fa_cho_clb` on a synthetic old DB with FA columns but no gio/dia_diem → returns `['clubs.gio','clubs.dia_diem']`, second run `[]`; on a DB with none of the six → all six added, second run `[]`; each time exactly one `.bak-*` was written and it did NOT contain the new columns (backup before the ALTER); full `di_tru_schema` twice → second call `[]`, no extra backup; fresh `init_db` has both columns and `di_tru_schema` returns `[]`. Old workbooks load (tests + the DQT 120 HS and 3-session workbooks from d7c9c19).
- (b) Old-data identity: same workbook, seed 7, built at d7c9c19 vs 194305f — `match_results.csv`, `kq.csv`, timetable and per-seed CSVs identical; `get_club_fill_stats`, `get_danh_sach_clb`, `get_thoi_khoa_bieu`, `list_clubs_admin`, `export_du_lieu_dau_vao` identical; the exported results workbook differs only in "exported at" timestamps (`Dấu vết`, `Hướng dẫn` cells) and `*_tong_hop.csv` (timestamp too: it differs between two runs of the same commit).
- SG-2 FIX-1 (55fd02f): `mau_csv/SO_NHAP_CLB.xlsx` — sheets `1. CLB` and `2. Học sinh` cell-identical to d7c9c19; only `Hướng dẫn` changed (the Wharton guide sentence); `tests/test_t1b_nhan_trung_cu.py` passes.
- (d) Foreign files: `js/03_ket_qua.js` (2 lines), `js/05_quan_ly.js` (1 cell), `js/09_the_xem.js` (2 lines), `js/11_chuan_bi.js` (step-1 columns), `api_bao_cao.py`, `api_quan_ly.py`: minimal, all no-ops when empty, and declared in `docs/ke_hoach/sg_song_song/MANH_B.md`.
- Known red `tests/test_a13_12_tai_lieu.py::test_ban_do_ma_so_tep_test_la_so_that` not run here (expected; person A fixes the count).
