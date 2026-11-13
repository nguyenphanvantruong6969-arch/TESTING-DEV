# SG-8 review (CHECKER, session_01YVAyu32HHT4cB1VP6Wyrys) — range b3570ac..03974ec, branch claude/sg-b

**Verdict: FIX-1** (Round 0 → FIX-1). The conversion to `{code, params}` is complete and clean for freshly uploaded
Phiếu, but a round saved before SG-8 now shows raw JSON in step 1. All data are SIMULATED.
Environment: scratch venv outside the repo (`requirements-dev.txt` + playwright 1.63.0); scratch worktrees removed.

## Fix list (FIX-1)
1. **Round files saved before SG-8 render as raw JSON in step 1.**
   `js/11_chuan_bi.js`: `const noiDung = (x) => trErr(x)` (line ~167) and `api_forms.get_forms_buoc_12`, which
   re-reads `phieu_clb_ket_qua.json` (written by every earlier `nap_phieu_clb`, "để mở lại thẻ vẫn thấy") and returns
   its `loi` / `canh_bao` unchanged. Old files hold `{ma, clb, noi_dung}` with no `code`, and `translateError` falls back
   to `JSON.stringify(entry)`. The code comment ("Tệp đợt cũ … vẫn hiện nguyên chữ") is therefore wrong for those two
   lists (the old `theo_loai` labels and old `chan` strings do pass through correctly).
   Why: backward compatibility of reopened rounds (a kiosk upgraded in the middle of a term); spec acceptance "step 1
   fully readable"; invariant 1 spirit (same stored data → same screen).
   Reproduced in Chromium (vi): upload a Phiếu, overwrite the `phieu_clb_ket_qua.json` of the round with the pre-SG-8
   shape (`loi=[{"ma":"phieu_thieu_cau_2","clb":"Cu A","noi_dung":"chưa trả lời câu 2: đã bỏ qua"}]`), `ChuanBi.lamMoi()` →
   the list shows `{"ma":"phieu_thieu_cau_2","clb":"Cu A","noi_dung":"…"}` verbatim.
   Fix (either): `noiDung = (x) => (x && x.code ? trErr(x) : x.clb + ": " + (x.noi_dung || ""))`, or map old items in
   `get_forms_buoc_12` (`code = "phieu_nd_" + ma`, `params = {clb}` when `code` is absent and `ma` is known).
   Verify: add a test that writes the old-shape JSON (as above) and asserts the lines read `Cu A: chưa trả lời câu 2: …`
   (vi) and contain no `{`/`"ma"`; legacy `theo_loai` `{"Tự do": 1}` and a string in `chan` must keep working.

## Optional (do not block)
- `tests/test_giao_dien_sg8_buoc1_tieng_anh.py::test_tieng_anh…` only asserts "no Vietnamese diacritics". My mutation
  `noiDung = x => x.clb + ": " + x.code` (raw code in English UI) left it GREEN (only the vi test went red). Add one
  English phrase assertion (e.g. `"hasn't answered question 2"`).
- English reads "Select Club: Selective club: waiting for…" / "Select Club: the Selective club has no criteria table"
  (club name repeated as in the vi source "CLB Tuyển chọn: CLB Tuyển chọn chưa ghi…"); wording only, same as before in vi.
- Step 4 (`api_forms_nap.py` `noi_dung`, `js/12_chuan_bi_nap.js:226`) still carries Vietnamese sentences; correctly out of
  SG-8 scope, but the English UI there is not translated (a separate item).

## Checklist 2.10 + lead points — evidence
1. **Scope:** diff = `api_forms.py` (`_dong_bao_cao`, `_clb_hien_thi` drops `loai_nhan`, `nap_phieu_clb` returns raw
   `kiem_truoc`, `theo_loai` keyed by Loại code, no-valid-club failure as codes), 14 new codes in the SG-B block of
   `i18n_errors.py` (+ regenerated `i18n_loi.js`), `js/11_chuan_bi.js` (`nhanLoai`, `nhanBuoi`, `noiDung`, `chan.map(trErr)`,
   `langchange` redraw), tests, MANH_B.md. Nothing else. Matches finding M5. Only gap = FIX-1 item 1.
2. **Red-first:** worktree at b3570ac + the two new test files → 8 failed, 2 passed (the 2 are guard tests); at 03974ec → 10 passed.
3. **Mutation (scratch worktree at 03974ec):** (i) `noiDung` printing the raw code → vi UI test red (en UI test stays green: see Optional);
   (ii) one `en` text replaced by Vietnamese → `test_moi_ma_noi_dung…en_khac_vi` red. Both restored, `git status` clean. Coder's own mutations (prefix `phieu_nd_x`) not repeated.
4. **Tests ran for real (lead point e):** every test file greping `api_forms|chuyen_phieu_clb|NHAN_LOAI_HIEN_THI|loai_nhan|nap_phieu_clb|get_forms_buoc_12|theo_loai|ChuanBi`
   (15 files: fa_gap12/gap13, fa_m1_phieu_clb, fa_m6_tai_lieu, fa_m7_dong_goi/nguon_mot_lan, fa_m8_bo_bieu_mau, giao_dien fa_m10_nut / fa_m7_nguon / fa_m7_the / fa_m9_nap /
   fg8_cau_chu / sg6, sg6, sg8) + `test_giao_dien_sg8…` + `test_ws_nhan` + `test_van_phong_tu_nhien` = **208 passed, 0 skipped**
   (Chromium, `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`). Full non-UI suite not re-run (coder: 5599 passed; known red a13_12 only). `ruff check .` clean.
5. **Invariants:** `kiem_nhanh --co-so origin/main --so-seed 20` = 7/7, 60 cases byte-identical; no DA core / `compute_club_priority` touched;
   inv. 6 `{ok,data,errors}` kept, new failure shape `[phieu_clb_tep_sai, <code per skipped club> | phieu_clb_khong_co_clb_hop_le]` only `{code, params}`; no schema, no CSV contract change.
6. **Strings (lead point b):** the 14 new texts sit only inside `=== SG-B ===`; `python tao_i18n_js.py` leaves `i18n_loi.js` unchanged (matches); all 14 in `MA_MOI_SAU_ANH_CHUP` (SG-B block);
   `test_ws_nhan` + `test_van_phong_tu_nhien` pass; no internal codes in vi/en. vi = old `NOI_DUNG` wording behind `"{clb}: "` (guard test compares every code).
   Only deliberate vi change: gate check `Buổi "thu_3"` → `Buổi "Thứ 3"` (improvement: the old text leaked an internal session code).
   **NOI_DUNG duplication verdict:** acceptable, not a violation of invariant 6, because invariant 6 governs the UI↔backend message contract and the UI path no longer reads the constant;
   the remaining copy only feeds a teacher-facing file written in Vietnamese (like the Excel headers and the Sổ nhập "Loại" labels), and `test_moi_ma_noi_dung_co_mot_ma_i18n_vi_giong_chu_cu…`
   fails if the two ever drift. Preferred (optional, later): `viet_bao_cao` builds each line with `format_message("phieu_nd_"+ma, {"clb": clb}, "vi")`; the .md stays byte-identical because vi = `"<clb>: " + NOI_DUNG`.
   Same reasoning for `NHAN_LOAI_HIEN_THI` ↔ `fa_loai_*` (guarded by `test_nhan_loai_trong_giao_dien_vi…`).
7. **UI walkthrough (lead point a), Chromium, browser_host, data outside the repo, Phiếu with 8 rows: three Loại, a skipped club for each of 4 reasons, 6 warnings, a gate check:**
   English at 1920×1080 → full `#cb-buoc-1` text has **0 Vietnamese characters** (summary "3 clubs loaded (Free 1, Limited 1, Selective 1)…", table headers/Session/Type, 4 errors, 6 warnings, check
   `Session "Tue" has no Free club…`), no overflow, no page error; screenshot reviewed. Vietnamese at 1366×768 vs the same code at b3570ac → text identical except the one deliberate line above.
   Language switch after upload now redraws (old code did not). Walkthrough scripts were scratch only (not committed).
8. **Files for teachers (lead point c):** `chuyen_phieu_clb.chuyen_phieu` on the same Phiếu at b3570ac vs 03974ec → `BAO_CAO_PHIEU_CLB.md` byte-identical and Sổ nhập (all sheets, all cells) identical.
   `mau_forms_thi_clb/` generator, `so_nhap.py`, `chuyen_phieu_clb.py` not in the diff → generator outputs unchanged by construction.
9. **soat-ma:** `kiem_nhanh` 7/7; tiers 1-3 read on the diff (no DA edit, no SQL, backward-compatible only for `theo_loai`/`chan`, not for `loi`/`canh_bao`: FIX-1);
   tier 4: `js/11_chuan_bi.js` (person C's file) edit minimal and declared in `MANH_B.md`, as is every other file.
10. **Old consumers (lead point d):** grep `js/` and `tests/` for `noi_dung` / `loai_nhan` / `theo_loai` / `nap_phieu_clb` / `get_forms_buoc_12`: only `js/11_chuan_bi.js` (updated); `js/12_chuan_bi_nap.js` uses step-4 `noi_dung`, a different list, untouched.
