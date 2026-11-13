Mode: CHU_TRI_FG
RUNNING CHU_TRI_FG session_01VfPzNt8wLhNQyk5sYejKse 2026-11-13T01:14Z
STATUS: RUNNING

# FG status (FG-1 … FG-9, after user test of forms-gop)

> English, ≤ 150 lines. Spec: `docs/ke_hoach/FORMS_GOP_SUA_KE_HOACH.md`; mechanics: `docs/ke_hoach/FG_TU_DONG.md`.
> All numbers SIMULATED; all Forms work TH.

BASE = f5e8a41 (origin/claude/forms-gop at start)

## Current step
- Wave 3: FG-9 delegated to a Sonnet worker (task start = HEAD after this commit); then wave gate 3, FINISH.

## Item table
| Item | State | Commit | Tests |
|---|---|---|---|
| STEP0 | DONE (lead review OK) | 63b6e73 | 13 test files, 41 red / 15 green on 24846d2 |
| FG-1 | DONE (server side was GONE-ON-HEAD; FIX1 13e93f3) | 79f2de2 | test_fg1_bat_tinh_nang (4), test_giao_dien_fg1_bat_tinh_nang (3) |
| FG-3 | DONE | f2dc276 | test_fg3_nap_lai (5) |
| FG-4 | DONE | (see Log) | test_giao_dien_fg4_nut_nap (4) |
| FG-5 | DONE | e90555a | test_fg5_khop_ma (6) |
| FG-6 | DONE | (see Log) | test_fg6_ket_qua_nap (5), test_giao_dien_fg6_danh_sach_loi (2) |
| FG-2 | DONE | 9db3039 | test_fg2_xem_truoc_fa (10) |
| FG-7 | DONE (FIX1 d754dbd) | 8c8202c | test_fg7_bieu_mau_sau_ket_qua (16) |
| FG-8 | DONE | cd0b2df | test_fg8_goi_y_suc_khoe (2), test_giao_dien_fg8_cau_chu (6) |
| FG-9 | TODO (KPI-link sub-bullet GONE-ON-HEAD) | | |

## Snapshots
- Rebuild from BASE: `git worktree add <scratch>/base f5e8a41`, then in it run
  `mau_forms_thi_clb/tao_mau_forms.py <mode> --ra <scratch>/snap/<name>` for `--fa-daa`, `--fa-daa --mot-bieu-mau`,
  `--phan-hoi`, `--tuan-3` (and `--sau-ket-qua` for reference). Output verified deterministic (two runs, `diff -r` clean).
- Lead copy: `<scratchpad of session_01VfPzNt8wLhNQyk5sYejKse>/snap/{fa-daa,fa-daa_mot,phan-hoi,tuan-3,sau-ket-qua}`.

## Decisions
- Every review touching UI strings also runs tests/test_van_phong_tu_nhien.py and tests/test_ws_nhan.py (lesson from FG-1 FIX1).
- Workers must run `git fetch origin main:refs/remotes/origin/main` before `kiem_nhanh` (else trung_khit cannot compare).
- D1–D4 as spec §1 (final).
- STEP0 commits the red tests it writes (they are each item's acceptance tests, rule 2); the item worker turns them
  green and may extend them. The branch is expected red between STEP0 and FG-9; the green loop runs at FINISH.
  A test already green on HEAD → item GONE-ON-HEAD; keep that test only if it adds coverage.

## Waiting for Truong
- (none yet)

## Workers
| Task | Session | State |
|---|---|---|
| STEP0 | session_01VfPzNuWUv3W6FtiR2fPPpB | DONE |
| FG-1 | session_01VfPzNtE2gjQkFTnk4CKsg9 | DONE, review GO |
| FG-3 | session_01VfPzNv8yPVuUfCb3LScjpc | DONE, review GO |
| FG-4 | session_01VfPzNtbYjiRYVCMfuncuk2 | DONE, review GO |
| FG-5 | session_01VfPzNr3qCVAmDxcnmnLfjh | DONE, review GO |
| FG-6 | session_01VfPzNru1AhpnZkxiBZ3HP2 | DONE, review GO |
| FG-2 | session_01VfPzNs42szCLCJK8kCxfWR | DONE, review GO |
| FG-7 | session_01VfPzNvLWfY7KLXz5Lj6S7P | DONE, review GO after FIX1 |
| FG-8 | session_01VfPzNukgBtxgvdTkP7cCJi | DONE, review GO |
| FG-9 | (creating) | |

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
- 2026-11-13T01:40Z lead: STEP0 reviewed (tests rerun: 41 failed / 15 passed, UI really ran, ruff clean); spot-read FG-3/FG-5 tests vs spec: OK. No item fully GONE-ON-HEAD. FG-8 worker may update the TEXT of forms_tep_sau_ket_qua (vi+en) to name the new heading; no FA-M9 logic.
- 2026-11-13 WORKER session_01VfPzNtE2gjQkFTnk4CKsg9 FG-1 DONE 79f2de2
  - Red run before: 3 failed (test_giao_dien_fg1_bat_tinh_nang.py, menu item missing) / 4 green API tests. After: 38 passed (fg1 + test_ws_giao_dien + i18n). Fixed test_ws_giao_dien menu-order assert (added tinh_nang). Race fixed: dialog built synchronously, config fetched after.
  - Mutation: opened the disabled-without-FA guard (boxes always enabled) -> test_khong_fa_thi_cac_o_bi_khoa... red; restored; earlier mutation (no close-after-save) -> test_bat_phan_hoi... red; restored. ruff clean; kiem_nhanh 6/7 (only trung_khit: no origin/main in this container, UI-only change, not a code fault).
  - Note: wsOverlay lost static role=dialog; wsHienOverlay sets it only while visible.
- 2026-11-13T02:03Z lead: BASE f5e8a41 full suite (no --cov): 5972 passed, 4 skipped (none UI), 0 failed → no pre-existing failures.
- 2026-11-13T02:03Z lead: FG-1 review GO: diff 2f4cb69..c2c1854 matches spec (5 CO_SAU_XEP boxes + so_ngay, FA-off disabled + hint, server error kept in dialog, re-apply config); 27 passed (fg1 + test_ws_giao_dien, Chromium ran); mutation logged; kiem_nhanh --co-so origin/main 7/7.
- 2026-11-13 WORKER session_01VfPzNv8yPVuUfCb3LScjpc FG-3 DONE f2dc276
  - Red run before (HEAD without fix): tests/test_fg3_nap_lai.py 5 failed. After: 40 passed (fg3 + gap5 + m6b API/UI). ruff clean; kiem_nhanh --co-so origin/main 7/7.
  - Mutation: feedback dedupe disabled -> test_nap_hai_lan_phan_hoi_khong_them_dong red; Forms-appeal dedupe off (tu_forms=False) -> 3 appeal tests red; both restored.
  - Dedupe of Forms appeals applies only when the row has a real Forms completion time (no time -> old CHO rule, keeps m6b test with frozen clock). Two old exact-dict asserts extended with dong_moi/dong_trung (not loosened).
- 2026-11-13T02:27Z lead: FG-3 review GO: diff 9b888a2..ed411f7 matches spec D1=C (identical feedback row skipped+counted; Forms appeal with real completion time already stored in any state → khieu_nai_trung; manual appeals unchanged); created_at format matches the INSERT; related -k run: 80 passed, 5 red = FG-4/5/6 acceptance tests only (expected).
- 2026-11-13 WORKER session_01VfPzNtbYjiRYVCMfuncuk2 FG-4 DONE 06cb12d
  - Red run before: tests/test_giao_dien_fg4_nut_nap.py 2 failed (busy-state test, both buttons) / 2 green error-path tests. After: 4 passed; related (gap1 theo_doi, m6b, i18n) green, Chromium really ran. ruff clean; kiem_nhanh --co-so origin/main 7/7.
  - Mutation: removed `.finally(xong)` -> 4 failed; restored, 4 passed. (Code commit 06cb12d carries the message "ghi hash vào Log" by a shell-chain slip; content is the full FG-4 change.)
- 2026-11-13T02:52Z lead: FG-4 review GO: one helper napTepForms(nut, input, tenApi, khiXong) per spec, busy label, catch→generic toast, finally resets; 21 UI tests passed (Chromium ran).
- 2026-11-13T02:55Z lead: WAVE GATE 1 GREEN: merged origin/claude/forms-gop c1de264 (conflicts only in CHANGELOG/TIEN_DO, both sides kept) → e099a3c; ruff clean; wave tests 68 passed; kiem_nhanh --co-so origin/main --so-seed 20: 7/7, 60/60; generator diff -r vs BASE snapshots: 4/4 identical.
- 2026-11-13 WORKER session_01VfPzNPmYjiRYVCMfuncuk2 FG-5 DONE e90555a
  - Red run before: tests/test_fg5_khop_ma.py 6 failed (khop_ma_hoc_sinh missing, no ma_khong_khop). After: 6 passed; related -k run 66 passed, remaining 6 red = FG-6/FG-7 acceptance tests only. ruff clean; kiem_nhanh --co-so origin/main 7/7. Two old exact-dict asserts (gap5, m6b) extended with ma_khong_khop, not loosened.
  - Mutation: ambiguity ignored (casefold match takes first of many) -> test_khop_ma_ham_thuan + test_mo_ho_hai_em_ab_AB red; restored, 6 passed, git status clean.
- 2026-11-13T03:12Z lead: FG-5 review GO: pure khop_ma_hoc_sinh (exact, else unique strip+casefold) used in _chen_phan_hoi (both import paths) and the appeal loop; stored IDs unchanged; ma_khong_khop first 20 in order. (Worker Log line shows id ...NPmYji...; real worker session is session_01VfPzNr3qCVAmDxcnmnLfjh.)
- 2026-11-13 WORKER session_01VfPzNru1AhpnZkxiBZ3HP2 FG-6 DONE f91d1af
  - Red run before: tests/test_fg6_ket_qua_nap.py 4 failed (+1 green) and tests/test_giao_dien_fg6_danh_sach_loi.py 2 failed (Chromium ran). After: 9 passed incl. updated m6b UI test; related -k run (i18n/nhan/log/toast/khieu_nai/fg3-6, ~all green, exit 0). ruff clean; kiem_nhanh --co-so origin/main 7/7.
  - Mutation: log group cap 5 -> 500 => test_buoc_kiem_tra_du_lieu_gom_loi_theo_ma red; empty-file guard off => test_tep_rong_co_ma_rieng red; both restored.
  - Old keys n_ket_qua/n_tuan_3/n_khieu_nai/bo_qua kept (tests still read them). Three old asserts updated per spec (2 exact dicts + toast now one sentence, s3 detail moved to the list). Toast close "×" now CSS ::before so toast text ends with ".". venv created (.venv, gitignored).
- 2026-11-13T03:36Z lead: FG-6 review GO: result keys per spec (hoc_sinh, dong_moi, dong_trung, ma_khong_khop, dong_bo_qua[{dong,ly_do}], khieu_nai_*; old keys kept, still read by tests); toast one sentence, <ul> grouped by reason (all 3 ly_do have vi+en labels); run log groups errors by code, 5 each + 'và N lỗi nữa'; phan_hoi_tep_rong vi+en + MA_MOI_SAU_ANH_CHUP. Toast '×' moved to CSS ::before (aria-label kept). Old-test edits follow the spec's one-sentence toast, not loosened. Related -k run: 183 passed.
- 2026-11-13 WORKER session_01VfPzNs42szCLCJK8kCxfWR FG-2 DONE 9db3039
  - Red run before: tests/test_fg2_xem_truoc_fa.py 4 failed / 2 green guards (default-template hash, non-FA preview). After: 10 passed (4 acceptance + 4 new: group wording vi/en + "run blocked" line, preview writes nothing and import still works, sample deterministic + marked MÔ PHỎNG, FA guide). Related run (so_nhap*, wharton_so_nhap, i18n*, ws_nhan, skill_soat_ma, 41 files naming tao_so_nhap_mau/xem_truoc_so_nhap/i18n_errors): all green except the FG-1 string below. ruff clean; kiem_nhanh --co-so origin/main 7/7 (first run caught English "you" in the new message; fixed).
  - Mutation: FA preview check disabled -> grouped-warning tests red (2); reader alias "huy chuong" removed -> bid-column + sample-run tests red (2); both restored.
  - Design: grouped warning keeps the ORIGINAL code, params {nhom: true, n, vd}; display uses new "<code>_nhom" sentences (format_message + translateError pick them when params.nhom). Run-time single-item messages unchanged. FA template: all 4 FA club columns, bid column "Huy chương (60/30/10)" (list 60/30/10), FA-specific guide; default template untouched (hash guard green).
  - NOTE for lead (not FG-2): tests/test_van_phong_tu_nhien.py::test_moi_cau_hien_thi_deu_viet_tu_nhien is RED from FG-1's strings ws_tn_tieu_de (vi+en use an em dash "—" joining the sentence). FG-1 passed its own tests but this wording test was not in its related run; fix belongs to an FG-1 follow-up or FG-8 (wording).
  - Sample: du_lieu_test/SO_NHAP_FA_MAU_120HS.xlsx via du_lieu_test/tao_so_nhap_fa_mau.py (seed 20261113; content deterministic, file bytes differ per run only by zip timestamps).

- 2026-11-13 WORKER session_01VfPzNtE2gjQkFTnk4CKsg9 FG-1 FIX1 DONE 13e93f3
  - Red before: test_van_phong_tu_nhien.py::test_moi_cau_hien_thi_deu_viet_tu_nhien (ws_tn_tieu_de vi+en had a dash). Now: test_van_phong_tu_nhien + fg1 API + fg1 UI (Chromium ran) + i18n = 28 passed; ruff clean; kiem_nhanh 7/7.
- 2026-11-13T04:00Z lead: FG-2 review GO: FA preview warnings grouped per code (original code + params nhom/n/vd, '<code>_nhom' sentences vi+en in Python and JS), 'run will be blocked' line, import still allowed; FA template (che_do_fa) with Loại columns + 'Huy chương (60/30/10)'; reader alias 'huy chuong'; default template hash guard green; sample du_lieu_test/SO_NHAP_FA_MAU_120HS.xlsx (seed, MÔ PHỎNG). FG-2 worker found an FG-1 regression (em dash in ws_tn_tieu_de breaks test_van_phong_tu_nhien) the lead missed → FG-1 FIX1 sent to the FG-1 worker; done 13e93f3, review GO.
- 2026-11-13T04:35Z lead: WAVE GATE 2 GREEN: origin/claude/forms-gop has nothing new; ruff clean; kiem_nhanh --co-so origin/main --so-seed 20: 7/7, 60/60; generator diff -r: 4/4 identical; related -k run (fg, fa_m6b, fa_m2b, phan_hoi, khieu_nai, workspace, ws_, so_nhap, i18n, van_phong, thong_bao, nhan): 1705 passed, 3 skipped (numpy/POSIX, none UI), 14 failed = exactly the wave-3 acceptance tests (fg7 ×5, fg8 ×7, fg9 ×2), expected.
- 2026-11-13 WORKER session_01VfPzNvLWfY7KLXz5Lj6S7P FG-7 DONE 8c8202c
  - Red run before: tests/test_fg7_bieu_mau_sau_ket_qua.py 5 failed / 5 green (golden hashes). After: 10 passed + test_van_phong_tu_nhien (20 total); related run (m6b, mau_forms, m7, m8, gap5, m2, ws_nhan) 159 passed. ruff clean; kiem_nhanh --co-so origin/main 7/7.
  - Mutation: day filter disabled (all days kept) -> test_sau_ket_qua_voi_so_nhap_chi_liet_ke_ngay_co_clb red; restored.
  - Test bug fixed (not loosened): helper used c["ten"], real key is c["name"]. --help also had to lose "FA-DAA" (regex FA-[A-Z]\w*). Guide step 5 now explains why [tag]/(code) stay (added the sentence, no extra test).
- 2026-11-13 WORKER session_01VfPzNvLWfY7KLXz5Lj6S7P FG-7 FIX1 DONE d754dbd
  - Red before: 6 new tests failed (5 modes + default). After: test_fg7 + test_van_phong_tu_nhien + every test naming tao_mau_forms = 371 passed; ruff clean; kiem_nhanh 7/7; golden-hash guards green (stdout only). No existing test asserted the last stdout line.
  - Mutation: default-mode print removed -> test_che_do_mac_dinh red; restored.
- 2026-11-13T05:20Z lead: FG-7 review: day filter via --so-nhap-clb, own title, step 4 = menu path, help without internal codes, guide line on [tag]/(code) OK; fix round 1 asked for the absolute output folder in EVERY mode (spec), done d754dbd → GO. Code commit 8c8202c has message 'FG-7: log' (slip, explained in c42de59; help text is not under the byte-identity rule). 26 passed (fg7 + van_phong); generator diff -r 4/4 identical.
- 2026-11-13 WORKER session_01VfPzNukgBtxgvdTkP7cCJi FG-8 DONE cd0b2df
  - Red run before: tests/test_fg8_goi_y_suc_khoe.py 2 failed + tests/test_giao_dien_fg8_cau_chu.py 5 failed / 1 green guard (7 failed, 1 passed; Chromium ran). After: 8 passed; + test_van_phong_tu_nhien, test_ws_nhan, i18n sync/khoa, and 15 UI test files (wizard, health, appeals, feedback, FG-1/4/6, a13_11, t3) = all green. ruff clean; kiem_nhanh --co-so origin/main 7/7.
  - Mutation: summary always is-warn -> test_dong_tom_tat...[0-False] red; restored (git diff clean for that line).
  - Notes: tests/test_ws_nhan.py SUA_CO_Y extended for the intended health_panel_hint rewording (snapshot test). Hint text uses the real label "Nghiêm trọng"/"Serious" (an all-caps word trips the natural-wording test). forms_tep_sau_ket_qua text now names the group "Sau khi công bố kết quả" (vi+en), FA-M9 logic untouched. With one session the #knBuoi select is hidden and the appeals list drops the session label.
- 2026-11-13T05:45Z lead: FG-8 review GO: health hint vi+en says 'Nghiêm trọng' items block the run, summary red only when n_high>0; wizard 4 boxes disabled+unticked while FA off; checkbox same line (CSS :has on .ws-truong, checkbox only); heading 'Sau khi công bố kết quả' shown when either panel is; hint line on the two import buttons; one-session workspace hides #knBuoi and the session label; forms_tep_sau_ket_qua text only (FA-M9 logic untouched); test_ws_nhan SUA_CO_Y records the intended rewording. 85 passed (fg8, van_phong, ws_nhan, ws_giao_dien).
- 2026-11-13 WORKER session_01VfPzNsKCDN6sCNzaUQr5XA FG-9 DONE 39eb6a5
  - Red run before: tests/test_giao_dien_fg9_ux_nho.py 2 failed (sidebar numbers, toast button) / 1 green (KPI link, GONE-ON-HEAD, kept). After: 3 passed; with test_van_phong_tu_nhien + test_ws_nhan + test_giao_dien_a14_lop = 82 passed; 17 UI files naming the sidebar/taiSoNhapMau = 142 passed (Chromium via PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers). ruff clean; kiem_nhanh --co-so origin/main 7/7.
  - Mutation: numbers put back on first nav item + toast button not appended -> both acceptance tests red; restored, green, git status clean.
  - Old tests extended to the new state (no assertion dropped): test_giao_dien_a14_lop.py::test_thanh_ben_sau_khi_gop_va_bao_chua_co_ket_qua (7 tabs in order, no label starts with a digit; was 01–07), test_ws_so_nhap_giao_dien.py::_tai_mau (waits for a title containing .xlsx + "Mở thư mục" button; was .xlsx in toast text). fg9 sidebar test also checks 7 labels.
  - Decision: automatic folder opening KEPT (closest to today); button re-opens it. Path-free sentence uses new key so_mau_da_tao_ngan (vi+en); the feedback line under the drop zone still shows the full path. showToast gained opts.hanhDong {nhan, khiBam, tooltip}.
