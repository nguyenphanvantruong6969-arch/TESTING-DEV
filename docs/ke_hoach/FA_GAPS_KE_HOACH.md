# FA gaps — spec per item (father only)

> Source of the gap list and rules: `INSTRUCTION_FILL_GAPS.md` PART 2 (G1–G9, gap table). One block per item, template
> F2. Status and decisions: `docs/phien/FA_GAPS_STATUS.md`. All numbers are SIMULATED data.

## Wave 1 — post-allocation core (GAP-0, GAP-1, GAP-2)

Shared decisions for wave 1 (SOLO, safest option, recorded in status "Review notes"):
- New module `fa_sau_xep.py` (pure functions + small DB readers/writers, no UI) and new mixin `api_sau_xep.py`
  (`SauXepMixin`, added to the bases of `PipelineAPI` in `api.py`). Both go in the code map of `CLAUDE_CHI_TIET.md`.
- New tables are appended to `DEFAULT_SCHEMA` (same pattern as `fa_ly_do`, `giu_cho`): `init_db` runs it then
  `di_tru_schema` on every open, so an old DB gains them; tests prove "old DB upgrades" and "twice = no-op".
- Post-allocation flags live ONLY in `cau_hinh_ws.MAC_DINH_TRUONG_HOC["rules"]`, never in `LUAT_XEP_MAC_DINH`, so
  they never enter `run_history.luat_xep` or the result fingerprint (toggling them never makes results "stale").
- New exception `cau_hinh_ws.FaTinhNangCanFa(ValueError)` (attribute `khoa`): a post-allocation flag True while
  `fa_daa` is not True. `_ws_phuong_thuc` maps it to `err("fa_tinh_nang_can_fa", khoa=e.khoa)` (before the generic
  `ValueError` branch). Reused by GAP-4 and GAP-13.
- "Base run of a day" = the latest `run_history` row whose `buoi_da_chay` is empty or contains that day (same rule
  as `api_xuat._doc_ly_do_moi_nhat`). Adjustments carry `run_id_base`; a rerun of that day makes them stale.
- GAP-2 waitlist reuses `fa_ly_do` (`outcome='REJECTED'`, `waitlist_pos`, `rank_in_list`) of the base run — the
  D4 order is already computed there by `fa_daa.ly_do_ket_qua`. No new priority logic.
- `match_results` and `run_history` are never written by any wave-1 code (G5).

### GAP-0 Adjustment log + replay  (vision §9.2–9.3; parent registry item A13; wave 1)
- Why: every seat change after publication must be traceable and replayable, never an in-place edit of the DA result.
- Flag: none (infrastructure; nothing calls it unless GAP-1/2/3/4 flags are on).
- Data: table `fa_dieu_chinh` in `DEFAULT_SCHEMA`:
  `id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL, run_id_base INTEGER NOT NULL, buoi TEXT NOT NULL,
  student_id TEXT NOT NULL, club_from TEXT, club_to TEXT, kind TEXT NOT NULL CHECK (kind IN ('release',
  'invite_offer','invite_accept','invite_decline','invite_expire','round2','appeal_rerun')), actor TEXT, note TEXT`.
  No foreign keys (audit trail like `fa_ly_do`); append-only. `invite_offer`/`invite_expire` extend the G5 list
  (offers must be logged too); they never move a seat.
- Backend (`fa_sau_xep.py`):
  - `KIND_DOI_CHO = ("release", "invite_accept", "round2")` — the only kinds that move a seat.
  - `vi_tri_hien_tai(ket_qua, run_goc, dieu_chinh) -> (vi_tri, lech)`. `ket_qua` {(sid, buoi): club_id|None} from
    `match_results`; `run_goc` {buoi: run_id}; `dieu_chinh` list of row dicts (keys = table columns). Rows replayed in
    `id` order. Row with `run_id_base != run_goc.get(buoi)` → not applied, `lech` gets `{"id", "ly_do": "run_cu"}`.
    Seat-moving row whose `club_from` != current value of (sid, buoi) (None == None counts as equal) or whose
    (sid, buoi) is not in `ket_qua` → not applied, `lech` gets `{"id", "ly_do": "khong_khop"}`. `release` sets None;
    `invite_accept` and `round2` set `club_to`. Other kinds: no change. Inputs never mutated. Pure, deterministic.
  - `run_goc_theo_buoi(cur) -> {buoi: run_id}` (rule above; days = DISTINCT `match_results.buoi`).
  - `doc_vi_tri(cur) -> (vi_tri, lech, run_goc)` reads `match_results` + `fa_dieu_chinh` and calls the pure function.
  - `ghi_dieu_chinh(cur, run_id_base, buoi, student_id, club_from, club_to, kind, actor="", note="") -> id`: the ONLY
    writer; INSERT only; `created_at` = local time `%Y-%m-%d %H:%M:%S`; raises ValueError for an unknown kind.
- UI: none. Export: none.
- kiem_nhanh: add `"fa_dieu_chinh"` to `BANG_NHAT_KY` in `.claude/skills/soat-ma/scripts/kiem_nhanh.py` (no UPDATE/
  DELETE allowed on it anywhere in app code).
- Tests first (kiem_nhan): `tests/test_fa_gap0_dieu_chinh.py`:
  1) no rows → `vi_tri == ket_qua`, `lech == []`.
  2) `ket_qua {("s1","thu_2"): "A"}`, rows [release A→None, invite_accept None→B] (same run) → `{("s1","thu_2"): "B"}`.
  3) order matters: rows given out of id order are replayed by id (same result as 2).
  4) release with `club_from="C"` while s1 is in A → unchanged, `lech == [{"id": 1, "ly_do": "khong_khop"}]`.
  5) row with `run_id_base` 1 while `run_goc {"thu_2": 2}` → unchanged, `lech` `run_cu`.
  6) `invite_offer`/`invite_decline`/`invite_expire`/`appeal_rerun` rows → unchanged, no `lech`.
  7) inputs are not mutated (deepcopy compare).
  8) DB: fresh `PipelineAPI` has table `fa_dieu_chinh`; an old DB (create via `init_db`, `DROP TABLE fa_dieu_chinh`,
     reopen through `init_db`) gains it; `di_tru_schema` run twice returns `[]` the second time and `sqlite_master`
     is unchanged.
  9) `ghi_dieu_chinh` with kind `"edit"` → ValueError; valid kind → row readable, `doc_vi_tri` applies it.
  10) `run_goc_theo_buoi`: full run (run 1) then `chi_buoi=["thu_2"]` run (run 2) → `{"thu_2": 2, "thu_3": 1}`.
  11) `kiem_nhanh.BANG_NHAT_KY` contains `fa_dieu_chinh`.
- Mutation to try: in `vi_tri_hien_tai` drop the `club_from` check → test 4 red; replay without sorting by id → 3 red.
- Invariant check: 60/60 identical; `match_results`/`run_history` untouched by the module (grep: no INSERT/UPDATE/
  DELETE on them in `fa_sau_xep.py`).
- Out of scope: any API/UI; appeals logic (GAP-3); round 2 (GAP-4).
- Size: M

### GAP-1 Attendance of the first 3 sessions  (vision §9.3; parent registry item A13; wave 1)
- Why: "Giáo viên điểm danh 3 buổi đầu. Vắng 2/3 buổi không phép → giải phóng chỗ."
- Flag: `rules.fa_diem_danh` default False; valid only when `fa_daa` is True (`FaTinhNangCanFa` →
  `fa_tinh_nang_can_fa`); non-bool → `ValueError` (generic `ws_du_lieu_sai`). Also covers GAP-2 (decision: invites
  only exist for seats released by attendance).
- Data: table `fa_diem_danh` in `DEFAULT_SCHEMA`: `run_id_base INTEGER NOT NULL, buoi TEXT NOT NULL, club_id TEXT
  NOT NULL, student_id TEXT NOT NULL, buoi_so INTEGER NOT NULL CHECK (buoi_so BETWEEN 1 AND 3), trang_thai TEXT NOT
  NULL CHECK (trang_thai IN ('CO_MAT','VANG_CO_PHEP','VANG_KHONG_PHEP')), updated_at TEXT,
  PRIMARY KEY (run_id_base, buoi, club_id, student_id, buoi_so)`. Editable input data (UPSERT / DELETE allowed here).
  Release = one `fa_dieu_chinh` row kind `release`, actor `diem_danh`.
- Backend:
  - `fa_sau_xep.NGUONG_VANG = 2`; `can_giai_phong(trang_thai_theo_buoi: dict) -> bool` (count of `VANG_KHONG_PHEP` ≥ 2).
  - `api_sau_xep.SauXepMixin.get_diem_danh(club_id="")` → `_ok({"bat": False})` when flag off. On:
    `{"bat": True, "clubs": [{club_id, name, buoi}] (clubs with ≥1 current member or released member, day order then
    club_id), "club_id": <chosen or first>, "hoc_sinh": [{student_id, name, buoi_1, buoi_2, buoi_3 (code or ""),
    so_vang_khong_phep, da_giai_phong}]}` — current members of the club (via `doc_vi_tri`) plus students released
    from it in the current base run (`da_giai_phong: True`), sorted by student_id. No run yet → `hoc_sinh: []`.
  - `luu_diem_danh(club_id, student_id, buoi_so, trang_thai)`: flag off → `fa_diem_danh_chua_bat`; `buoi_so` not in
    1..3 or `trang_thai` not in the 3 codes or "" → `diem_danh_gia_tri_sai`; student neither current member nor
    released from that club → `diem_danh_khong_thuoc_clb`. "" deletes the mark. One transaction: upsert, then if the
    student is still a current member and `can_giai_phong` → `ghi_dieu_chinh(kind="release", club_from=club_id,
    club_to=None, actor="diem_danh", note="vang_2_3")`, then (GAP-2) `moi_tiep`. Returns `_ok({"da_giai_phong": bool})`.
    Idempotent: a released student gets no second release row. Correcting marks later never undoes a release.
  - `export_diem_danh(output_path="")` via `_khoa_xuat` + `_duong_xuat(..., "diem_danh.xlsx")`: one sheet per club
    (title = club name cleaned by `so_excel.lam_sach`, cut to 31 chars, `/\?*[]:` removed, duplicates suffixed),
    header `Mã học sinh, Họ tên, Buổi 1, Buổi 2, Buổi 3, Số buổi vắng không phép, Đã giải phóng chỗ`, Vietnamese
    status words (Có mặt / Vắng có phép / Vắng không phép). Every text cell through `lam_sach`, formulas blocked like
    `fa_bien_ban.ghi_xlsx`. Flag off → `fa_diem_danh_chua_bat`. Returns `{path, n_clb}`.
- UI: `index.html` view-others: panel `#diemDanhPanel` (hidden) with `<select id="diemDanhClb">`, table body
  `#diemDanhBang`, button `#btnXuatDiemDanh`; each row has three `<select class="dd-o" data-student-id data-buoi-so>`
  (options "", CO_MAT, VANG_CO_PHEP, VANG_KHONG_PHEP) and, when released, a tag `.dd-giai-phong`. New file
  `js/10_theo_doi.js` (add to `js/_danh_sach.txt` before `08_khoi_dong` and to the script list in `index.html`):
  `taiDiemDanh()` (called whenever `loadMatchResults` runs), change on `.dd-o` → `luu_diem_danh` then reload.
  Wizard step 3 (`js/075_workspace.js`): checkbox `wzFaDiemDanh` sent only when checked (`fa_diem_danh: true`),
  review row `rvFaDiemDanh`. i18n keys (vi+en): `dd_tieu_de`, `dd_chon_clb`, `dd_buoi_n` ({n}), `dd_co_mat`,
  `dd_vang_co_phep`, `dd_vang_khong_phep`, `dd_so_vang`, `dd_da_giai_phong`, `btn_xuat_diem_danh`, `ws_r_fa_diem_danh`,
  `ws_r_fa_diem_danh_ngan`. Error codes in `i18n_errors.py` (vi+en): `fa_tinh_nang_can_fa`, `fa_diem_danh_chua_bat`,
  `diem_danh_gia_tri_sai`, `diem_danh_khong_thuoc_clb`.
- Export: `diem_danh.xlsx` as above (student names allowed: this is a per-club teacher list, not a lottery/aggregate
  export).
- Tests first (kiem_nhan): `tests/test_fa_gap1_diem_danh.py` (data via `tests/_fa.py` helpers, FA on, one run):
  1) `update_workspace_config({"rules": {"fa_diem_danh": True}})` with FA off → `["fa_tinh_nang_can_fa"]`; with FA on → ok;
     `{"fa_diem_danh": "co"}` → `["ws_du_lieu_sai"]`; default config has `fa_diem_danh` False and it is NOT in
     `run_history.luat_xep` after a run with it True.
  2) flag off: `get_diem_danh()` == `{"ok": True, "data": {"bat": False}, "errors": []}`; `luu_diem_danh` →
     `fa_diem_danh_chua_bat`.
  3) one unexcused → no release; second unexcused (other session) → `da_giai_phong` True, exactly one
     `fa_dieu_chinh` row kind release, `doc_vi_tri` gives None for that student/day; `match_results` byte-identical
     before/after; `run_history` row count unchanged.
  4) unexcused + excused + present → no release; a third save after release → still one release row.
  5) bad `buoi_so` 4 / bad code → `diem_danh_gia_tri_sai`; student of another club → `diem_danh_khong_thuoc_clb`.
  6) `get_diem_danh` lists the released student with `da_giai_phong` True and counts.
  7) export: xlsx opens with openpyxl, one sheet per club, the status words, a club named `"=X\x01"` neither breaks
     nor becomes a formula.
  `tests/test_giao_dien_fa_gap1_theo_doi.py` (Chromium, pattern of `tests/test_giao_dien_fa_ket_qua.py`):
  8) flag off → `#diemDanhPanel` hidden; flag on → panel shown, rows for the club's members; choosing
     VANG_KHONG_PHEP for sessions 1 and 2 of one student → row shows `.dd-giai-phong` and the DB has the release row;
     no page errors.
- Mutation to try: `NGUONG_VANG = 3` → test 3 red; drop the "already released" check → test 4 red.
- Invariant check: 60/60 identical; with the flag on, `match_results` and `run_history` unchanged after every action.
- Out of scope: automatic undo of a release, sessions after the 3rd, homeroom notifications.
- Size: L

### GAP-2 Waitlist invites on a released seat  (vision §9.3, D4; parent registry item A13; wave 1)
- Why: "Chỗ trống → mời học sinh đầu danh sách chờ (LotteryOrder trong số học sinh bị từ chối ở CLB đó và có ghi CLB
  đó cao hơn CLB hiện tại)" — D4 order SELECTIVE score→medal→STB, LIMITED medal→STB (already `waitlist_pos`).
- Flag: `rules.fa_diem_danh` (same as GAP-1). Invites only for clubs of type `GIOI_HAN` / `TUYEN_CHON`.
- Data: `fa_dieu_chinh` rows `invite_offer` (club_from = student's current club or None, club_to = the club),
  `invite_accept` (moves the seat), `invite_decline`, `invite_expire` (no move). An offer is pending until a later
  accept/decline/expire row for the same (run_id_base, buoi, student_id, club_to).
- Backend (`fa_sau_xep.py`):
  - `moi_dang_cho(dieu_chinh, run_goc) -> {offer_id: row}` (pure).
  - `hang_cho(ly_do_rows, vi_tri, run_goc, dieu_chinh, buoi, club_id) -> [student_id]` (pure): REJECTED rows of that
    (base run, day, club) ordered by `waitlist_pos`; keep a student only if not currently in the club, the club's
    `rank_in_list` < rank_in_list of the student's current club for that day (from the student's own `fa_ly_do` rows of
    the base run; current None → keep), no pending offer anywhere for that student on that day, and no earlier
    decline/expire for this club in this base run.
  - `moi_tiep(cur, buoi, club_id) -> [offer_id]`: if the club is GIOI_HAN/TUYEN_CHON and its base run has `fa_ly_do`
    rows: while (current members + pending offers to it) < `clubs.capacity` and `hang_cho` is not empty → write
    `invite_offer` for the head (actor `moi_cho`). Called after a release (GAP-1), after decline/expire (same club),
    and after an accept (for the club the student left, if any).
  - API `get_moi_cho_trong()` → flag off `{"bat": False}`; on `{"bat": True, "moi": [{id, buoi, club_id, club_name,
    student_id, name, club_hien_tai, created_at, trang_thai: "CHO"|"NHAN"|"TU_CHOI"|"HET_HAN"}]}` newest first.
  - API `tra_loi_moi(id_moi, ket_qua)` with `ket_qua` ∈ {"nhan", "tu_choi", "het_han"}: flag off →
    `fa_diem_danh_chua_bat`; unknown value → `diem_danh_gia_tri_sai`; offer not pending → `moi_khong_con_cho`.
    `nhan` → `invite_accept` (club_from = current club now, club_to = offer club); then `moi_tiep` for the left club.
    `tu_choi` / `het_han` → `invite_decline` / `invite_expire`; then `moi_tiep` for the same club. One transaction.
- UI: panel `#moiPanel` in view-others (hidden when flag off), list `#moiDanhSach`; pending rows have buttons
  `button.moi-tra-loi[data-moi-id][data-ket-qua]` (Nhận / Từ chối / Hết hạn). i18n (vi+en): `moi_tieu_de`,
  `moi_nhan`, `moi_tu_choi`, `moi_het_han`, `moi_trang_thai_CHO`, `moi_trang_thai_NHAN`, `moi_trang_thai_TU_CHOI`,
  `moi_trang_thai_HET_HAN`, `moi_trong`. Error code `moi_khong_con_cho` (vi+en).
- Export: none (the attendance export is enough for this wave).
- Tests first (kiem_nhan): `tests/test_fa_gap2_moi_cho.py` — dataset: LIMITED club G cap 2 with 4 applicants all
  ranking G first and FREE club T second (so 2 rejected with `waitlist_pos` 1, 2):
  1) release of a G member (two unexcused marks) → exactly one `invite_offer` to the `waitlist_pos` 1 student.
  2) `tra_loi_moi(id, "nhan")` → `doc_vi_tri` puts that student in G, removes from T; no new offer for T (FREE).
  3) `tu_choi` → offer goes to `waitlist_pos` 2; `het_han` on that one → no third candidate → no offer.
  4) answering a non-pending offer → `moi_khong_con_cho`; unknown `ket_qua` → `diem_danh_gia_tri_sai`.
  5) a student already moved into a better-ranked club is skipped (pure `hang_cho` test).
  6) SELECTIVE club: order follows `waitlist_pos` (score first) — pure test with crafted rows.
  7) flag off → `get_moi_cho_trong` `{"bat": False}`; `match_results` and `run_history` unchanged throughout.
  UI part in `tests/test_giao_dien_fa_gap1_theo_doi.py`: 8) after a release, `#moiPanel` shows one pending row;
  clicking its "Nhận" button → row shows NHAN status; no page errors.
- Mutation to try: ignore the capacity check in `moi_tiep` → test 1 red (two offers); skip the "declined before" filter
  → test 3 red.
- Invariant check: 60/60 identical; `compute_club_priority` untouched (no attendance/invite data read by it).
- Out of scope: time-based automatic expiry, notifications to students, invites for FREE clubs.
- Size: M

## Wave 2 — appeals, round 2, feedback, week-3 survey (GAP-3, GAP-4, GAP-5, GAP-6)

Shared decisions for wave 2 (SOLO, safest option, recorded in status "Review notes"):
- Same pattern as wave 1: logic in `fa_sau_xep.py`, API in `api_sau_xep.py` (`SauXepMixin`), UI in `js/10_theo_doi.js`
  (+ a results-tab panel for GAP-5), tables appended to `DEFAULT_SCHEMA`, flags only in `MAC_DINH_TRUONG_HOC["rules"]`
  and in `cau_hinh_ws.CO_SAU_XEP` (bool, needs `fa_daa`, `FaTinhNangCanFa`).
- New flags (all default False): `fa_khieu_nai` (GAP-3), `fa_vong_2` (GAP-4), `fa_phan_hoi` (GAP-5 kiosk screen +
  GAP-6 import share it: both are student surveys).
- Appeal window: constant `fa_sau_xep.SO_NGAY_KHIEU_NAI = 3`, overridable per workspace by the integer rule
  `fa_khieu_nai_so_ngay` (default 3, allowed 1..14; non-int → `ValueError`). Only in `MAC_DINH_TRUONG_HOC`, never in
  the fingerprint. "Publication" = `run_history.run_at` of the base run of that day. Clock read through
  `fa_sau_xep.bay_gio()` (tests monkeypatch it; `run_history` is never updated).
- Forms parts (GAP-5, GAP-6) are labelled **TH (untested on real Microsoft)** in generated guides and CHANGELOG.
- Survey data never reaches `compute_club_priority` (invariant 2); exports of survey data carry student ids only in the
  per-row sheet, never names.

### GAP-3 Appeals (data errors only, 3-day window)  (vision §9.2; parent registry item A13; wave 2)
- Why: "Gửi trong phần mềm; chỉ xét lỗi dữ liệu. Sửa dữ liệu → chạy lại thuật toán với cùng seed; không sửa tay kết quả."
- Flag: `rules.fa_khieu_nai` default False (needs `fa_daa`); `rules.fa_khieu_nai_so_ngay` int 1..14 default 3.
- Data: table `fa_khieu_nai` (`id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL, student_id TEXT NOT
  NULL, buoi TEXT NOT NULL, loai TEXT NOT NULL CHECK (loai = 'DATA_ERROR'), ghi_chu TEXT, run_id_base INTEGER NOT NULL,
  trang_thai TEXT NOT NULL CHECK (trang_thai IN ('CHO','CHAP_NHAN','TU_CHOI')), xu_ly_at TEXT, xu_ly_ghi_chu TEXT)`.
  Status changes are UPDATEs of `trang_thai` (input data, not the audit log). Acceptance also writes one
  `fa_dieu_chinh` row kind `appeal_rerun` (club_from = club_to = current club, note = appeal id) as the audit trace.
- Backend (`fa_sau_xep.py`): `bay_gio()`; `trong_han_khieu_nai(run_at: str, bay_gio: datetime, so_ngay) -> bool`
  (pure; `run_at` in `run_history` format; inclusive of exactly `so_ngay` days); `anh_huong_sau_chay_lai(khieu_nai_rows,
  run_goc, dieu_chinh)` (pure) → for each accepted appeal whose day now has a newer base run: `{"id", "student_id",
  "buoi", "da_chay_lai": True, "dieu_chinh_cu": [ids of adjustments of the old base run of that day]}`; not rerun yet →
  `da_chay_lai: False`.
  API: `gui_khieu_nai(student_id, buoi, ghi_chu)`: flag off → `fa_khieu_nai_chua_bat`; unknown student / day without a
  result → `khieu_nai_khong_hop_le`; window passed → `khieu_nai_qua_han` (params `so_ngay`); an open (CHO) appeal for
  the same student+day → `khieu_nai_trung`; ok → `{id}`. `get_khieu_nai()` → `{bat, so_ngay, khieu_nai: [{id,
  student_id, name, buoi, ghi_chu, trang_thai, created_at, xu_ly_ghi_chu, da_chay_lai, dieu_chinh_cu}]}` newest first.
  `xu_ly_khieu_nai(id, chap_nhan: bool, ghi_chu="")`: not CHO → `khieu_nai_da_xu_ly`; accept → status CHAP_NHAN +
  `appeal_rerun` row. The admin then fixes the data and runs the pipeline as usual (`run_pipeline`, locked seed); no
  code path here runs the pipeline or edits `match_results`.
  `export_khieu_nai(output_path="")` → `khieu_nai.csv` via `_ghi_csv_an_toan`-style writer (UTF-8 BOM, formula guard
  `_an_toan_cho_excel`): `id, student_id, buoi, trang_thai, created_at, ghi_chu, xu_ly_ghi_chu, da_chay_lai,
  dieu_chinh_cu` (ids joined by `;`).
- UI: panel `#khieuNaiPanel` in view-others (hidden when off): form `#knMa`, `#knBuoi` (select of days), `#knGhiChu`,
  `#btnGuiKhieuNai`; list `#knDanhSach` with `button.kn-xu-ly[data-kn-id][data-chap-nhan="1|0"]` for CHO rows, a
  "đã chạy lại" tag when `da_chay_lai`; `#btnXuatKhieuNai`. i18n vi+en: `kn_tieu_de`, `kn_goi_y` ({n} days), `kn_ma`,
  `kn_buoi`, `kn_ghi_chu`, `kn_gui`, `kn_chap_nhan`, `kn_tu_choi`, `kn_trang_thai_CHO|CHAP_NHAN|TU_CHOI`,
  `kn_da_chay_lai`, `kn_can_chay_lai`, `btn_xuat_khieu_nai`, `xuat_muc_khieu_nai`, `ws_r_fa_khieu_nai`. Error codes:
  `fa_khieu_nai_chua_bat`, `khieu_nai_khong_hop_le`, `khieu_nai_qua_han`, `khieu_nai_trung`, `khieu_nai_da_xu_ly`.
  Wizard checkbox `wzFaKhieuNai` (sent only when checked), review row `rvFaKhieuNai`.
- Tests first: `tests/test_fa_gap3_khieu_nai.py`: 1) flag rules (needs FA; `fa_khieu_nai_so_ngay` 0 / "3" →
  `ws_du_lieu_sai`); 2) off → `{"bat": False}` and `fa_khieu_nai_chua_bat`; 3) `trong_han_khieu_nai` boundaries (2 d
  23 h in, 3 d 0 h in, 3 d 1 min out); 4) send within window (monkeypatched `bay_gio`) ok, after window
  `khieu_nai_qua_han`, duplicate open → `khieu_nai_trung`, unknown student → `khieu_nai_khong_hop_le`;
  5) accept → status + one `appeal_rerun` row; second decision → `khieu_nai_da_xu_ly`; 6) after a release (GAP-1)
  and acceptance, a rerun of that day with the locked seed → `da_chay_lai` True and `dieu_chinh_cu` lists the release
  id; `run_history` grew by exactly one row; seed unchanged (`stb_lock.seed`); 7) export csv columns and a note
  `"=1+1"` written guarded. UI (`tests/test_giao_dien_fa_gap3_khieu_nai.py`): 8) send an appeal from the form → row
  appears with CHO; click accept → CHAP_NHAN; flag off → panel hidden.
- Mutation: `trong_han_khieu_nai` `<=` → `<` → test 3 red; skip the duplicate check → test 4 red.
- Invariant check: 60/60; `run_pipeline` untouched; `match_results` never written by GAP-3 code.
- Out of scope: automatic data fixing, notifications.
- Size: L

### GAP-4 Round 2  (vision §9.3, §8.7; parent registry item A13; wave 2)
- Why: "Vòng 2: học sinh chưa có CLB mong muốn được chọn trong các chỗ còn trống."
- Flag: `rules.fa_vong_2` default False (needs `fa_daa`).
- Data: `fa_dieu_chinh` rows kind `round2` (actor `vong_2`). One pass per (base run, day): a second call →
  `vong_2_da_chay`.
- Backend (`fa_sau_xep.py`): `can_vong_2(vi_tri, nguyen_vong, buoi)` (pure) → students of that day whose current club
  is None or not in their own preference list (fallback); `cho_con_lai(vi_tri, suc_chua, dang_moi, buoi)` (pure) →
  `{club_id: free seats}` = capacity − current members − pending offers, only clubs of that day, > 0;
  `chay_vong_2(thu_tu, chon, con_lai)` (pure serial dictatorship) → `[(sid, club_id)]`: students in `thu_tu` order
  (lottery order of the day), each takes the first club of `chon[sid]` that still has a seat; a student without a
  usable pick is skipped. Lottery order of the day = `sinh_stb_theo_buoi(stb_goc, days, seed, "stb_ngay")[buoi]`
  ascending (seed from `stb_lock`), same as the run; tie → student_id.
  API `get_vong_2(buoi="")` → `{bat, buoi, ds_buoi, da_chay, hoc_sinh: [{student_id, name, club_hien_tai}] in lottery
  order, cho_con_lai: [{club_id, name, con}]}`; `chay_vong_2_api(buoi, chon: {sid: [club_id, ...]})` → validates flag
  (`fa_vong_2_chua_bat`), unknown student/club or club of another day → `vong_2_lua_chon_sai`, already run →
  `vong_2_da_chay`; writes one `round2` row per placed student (club_from = current) and returns `{xep: [{student_id,
  club_id}], bo_qua: [student_id]}`.
- UI: panel `#vong2Panel` (view-others): select `#v2Buoi`, a row per eligible student with `<select class="v2-chon"
  data-student-id>` (options = clubs with free seats, plus "—"), button `#btnChayVong2`; result text `#v2KetQua`.
  i18n vi+en: `v2_tieu_de`, `v2_goi_y`, `v2_chay`, `v2_da_chay`, `v2_ket_qua` ({n}, {m}), `v2_khong_chon`,
  `ws_r_fa_vong_2`. Errors: `fa_vong_2_chua_bat`, `vong_2_lua_chon_sai`, `vong_2_da_chay`. Wizard `wzFaVong2`,
  `rvFaVong2`.
- Tests first: `tests/test_fa_gap4_vong_2.py`: 1) flag rules; 2) pure `chay_vong_2`: order respected, seat counts
  respected, skip when no seat; 3) pure `can_vong_2`: fallback student included, student in own NV excluded;
  4) API end-to-end: a student placed by fallback into FREE T while LIMITED G has a free seat (capacity 3, 2 applicants
  ranking only G... crafted so G has free seats) → round 2 pick G → `doc_vi_tri` shows G; second call →
  `vong_2_da_chay`; `match_results`, `run_history` unchanged; 5) pick of a club with no seat → skipped, listed in
  `bo_qua`. UI (`tests/test_giao_dien_fa_gap4_vong_2.py`): 6) panel lists the eligible student, choose G, click run →
  `#v2KetQua` shows 1 placed; flag off → hidden.
- Mutation: ignore seat count in `chay_vong_2` → test 2 red; drop the "already run" check → test 4 red.
- Invariant check: 60/60.
- Out of scope: multiple passes, student self-service.
- Size: M

### GAP-5 Three one-tap feedback questions  (vision §9.1; parent registry item A13; wave 2)
- Why: "Ngay dưới kết quả: 3 câu, mỗi câu 1 chạm – hài lòng 1–5; hiểu vì sao có/không; phần nào khó nhất".
- Flag: `rules.fa_phan_hoi` default False (needs `fa_daa`). Forms part is TH.
- Data: table `fa_phan_hoi` (`id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL, student_id TEXT NOT
  NULL, nguon TEXT NOT NULL CHECK (nguon IN ('kiosk','forms')), loai TEXT NOT NULL CHECK (loai IN ('ket_qua','tuan_3')),
  hai_long INTEGER CHECK (hai_long BETWEEN 1 AND 5), hieu_ly_do INTEGER CHECK (hieu_ly_do IN (0,1)), kho_nhat TEXT
  CHECK (kho_nhat IN ('chon_clb','xep_thu_tu','huy_chuong','thu_thach','khong_co')), con_di INTEGER CHECK (con_di IN
  (0,1)), muon_doi INTEGER CHECK (muon_doi IN (0,1)))`. Last answer per (student, loai) counts.
- Backend: `fa_sau_xep.KHO_NHAT = ("chon_clb","xep_thu_tu","huy_chuong","thu_thach","khong_co")`;
  `tong_hop_phan_hoi(rows) -> {n, hai_long_tb, hai_long_dem {1..5}, hieu_ly_do_ty_le, kho_nhat_dem, con_di_ty_le,
  muon_doi_ty_le}` (pure; last answer per student+loai; empty → n 0 and None rates).
  API `gui_phan_hoi(student_id, hai_long, hieu_ly_do, kho_nhat)` (flag off → `fa_phan_hoi_chua_bat`; bad values →
  `phan_hoi_gia_tri_sai`; unknown student → `student_not_found`); `get_phan_hoi_tong_hop()` → `{bat, ket_qua: {...},
  tuan_3: {...}}`; `nhap_phan_hoi_forms(file_base64)` (same transport as `import_so_nhap`) reads a Forms xlsx export (header row 1) by exact question titles from
  `bieu_mau` (`CAU_HAI_LONG`, `CAU_HIEU_LY_DO`, `CAU_KHO_NHAT`, `CAU_CON_DI`, `CAU_MUON_DOI`, plus the student-id
  title of `cau_ma_hoc_sinh()`); rows with unknown student ids are skipped and counted; detects feedback vs week-3 by
  which titles exist; returns `{n_ket_qua, n_tuan_3, bo_qua}`; nothing matches → `phan_hoi_tep_sai`.
  `export_phan_hoi(output_path="")` → `phan_hoi.xlsx`: sheet "Tổng hợp" (aggregates, no ids), sheet "Chi tiết"
  (student_id, loai, nguon, answers, created_at; no names).
- Forms (TH): `mau_forms_thi_clb/bieu_mau.py` constants above + `cac_phan_phan_hoi()` (student id + 3 choice
  questions); `tao_mau_forms.py --phan-hoi [--ra DIR]` writes `NHAP_FORMS_PHAN_HOI.docx` + `CAI_DAT_FORMS_PHAN_HOI.md`
  (TH label, settings: one response, required), byte-identical when rerun; exclusive with other modes.
- UI: in view-results a panel `#phanHoiPanel` (hidden when flag off): `#phMa` (student id), buttons
  `button.ph-hai-long[data-gia-tri=1..5]`, `button.ph-hieu[data-gia-tri=1|0]`, `button.ph-kho[data-gia-tri=<code>]`
  (one tap each, `aria-pressed`), `#btnGuiPhanHoi`, `#phKetQua`. Admin part in view-others: panel `#phanHoiTongPanel` (hidden when off) with the summary
  `#phTongHop`, export button `#btnXuatPhanHoi`, and import: hidden `<input type="file" id="phTep" accept=".xlsx">` +
  button `#btnNhapPhanHoi` → FileReader → `bufferSangBase64` → `nhap_phan_hoi_forms`; result text `#phNhapKetQua`. i18n vi+en for every label; errors
  `fa_phan_hoi_chua_bat`, `phan_hoi_gia_tri_sai`, `phan_hoi_tep_sai`. Wizard `wzFaPhanHoi`, `rvFaPhanHoi`.
- Tests first: `tests/test_fa_gap5_phan_hoi.py`: 1) flag rules; 2) send valid → stored, aggregate n=1; resend → last
  answer counts; bad values → `phan_hoi_gia_tri_sai`; 3) pure aggregate on crafted rows; 4) Forms generator `--phan-hoi`
  writes both files, rerun byte-identical, docx contains the 3 titles and TH label in the md; 5) importer on a crafted
  xlsx (titles from `bieu_mau`) imports 2 rows, skips 1 unknown id; wrong file → `phan_hoi_tep_sai`; 6) export: two
  sheets, no student names anywhere. UI (`tests/test_giao_dien_fa_gap5_phan_hoi.py`): 7) tap 4, "có", "huy_chuong",
  send → `#phKetQua` ok text and DB row; flag off → panel hidden.
- Mutation: aggregate counts all answers instead of the last per student → test 3 red.
- Invariant check: 60/60.
- Size: L

### GAP-6 Week-3 survey  (vision §9.3; parent registry item A13; wave 2)
- Why: "Tuần 3: thông báo 2 câu – Em còn đi CLB không?, Em muốn đổi không?"
- Flag: `rules.fa_phan_hoi` (shared with GAP-5). TH.
- Data: `fa_phan_hoi` rows `loai = 'tuan_3'` (`con_di`, `muon_doi`).
- Backend: Forms generator `tao_mau_forms.py --tuan-3` writes `NHAP_FORMS_TUAN_3.docx` + `CAI_DAT_FORMS_TUAN_3.md`
  (student id + 2 yes/no questions; TH label; byte-identical rerun); `bieu_mau.cac_phan_tuan_3()`. Import through the
  same `nhap_phan_hoi_forms` (GAP-5); aggregate `tuan_3` in `get_phan_hoi_tong_hop`; export sheet "Tuần 3" in
  `phan_hoi.xlsx` (rates + per-row with student_id only).
- UI: none beyond GAP-5's import/export buttons (the summary line shows week-3 rates when present).
- Tests first: `tests/test_fa_gap6_tuan_3.py`: 1) generator writes both files, rerun identical, md has TH; 2) import a
  crafted week-3 xlsx → `n_tuan_3` 2, aggregate rates; 3) export has sheet "Tuần 3" with the rates; 4) a file holding
  both feedback and week-3 titles imports both kinds.
- Mutation: swap `con_di`/`muon_doi` columns in the importer → test 2 red.
- Invariant check: 60/60.
- Size: M
