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
