# SG-9 review (checker, session_01VfPzNt6qaZtDuK7uYC28bX) — range a1b6ecb..98908e1 — verdict PASS

Fable's report unreadable: judged against SOAT_GIAO_DIEN_KE_HOACH.md §3 SG-9 (one wrapper, disable + "Đang…" + `.catch` + `.finally`;
acceptance: rejecting API → button re-enabled + error toast; double click → one call).

## Passed
- `chayNut` / `chayTai` / `noiTiep` in `js/00_nen.js` (single definition). Bare `.then(` count in the 5 files = 0 (static test +
  my grep). `napTepForms` is now a thin user of `chayNut` (`giuDenKhiXong`, label `dang_nap`, `sauCung` clears the file input);
  all 10 FG-4 tests pass, and my mutations on `sauCung` / label restore make them fail (so they do exercise the shared path).
- Site-by-site read of all five diffs (≈70 sites): success callbacks, arguments and the refresh after success unchanged; `ok:false`
  still goes through the site's own `showErrorToast` (callApi already turns a rejected promise into `{ok:false}`, so the toast is the
  same one as before); `taiDiemDanh` chain → `noiTiep` keeps the same order (moi/khieu nai/vong 2/phan hoi, one after another);
  `btnChayVong2` still re-enables first and disables again after success; `loadAdminStudents`, `loadAdminWharton`, `moManSuaWharton`
  keep returning a promise to their callers. No site where a returned value is read later was found to receive `undefined`
  (the one that returns `res`, `buoiTaiCho`, is only reached on success, see note 3).
- Labels: every touched button is plain text + `data-i18n` (no icon/child nodes). Busy label "Đang xử lý…" / "Working…" (new key
  `dang_xu_ly`, vi + en, SG-C block). Label is restored exactly (checked vi and en for Quản lý, Theo dõi, Chuẩn bị). Language switch
  while busy (Save club button, 1.5 s delayed API): button ends with the NEW language label, not stuck on busy and not the old
  language (guard `textContent === chuBan`).
- `js/11_chuan_bi.js`: 6 hunks, call sites only (person B's area untouched). No double toast found at any site (no `.catch`/`finally`
  left outside the wrapper; `khiBan` no longer used in the 5 files).
- Real Chromium (PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers): ALL `tests/test_giao_dien_*.py` + `test_t3_l2_buoi.py` = 495 passed,
  0 skipped, 0 failed (831 s). Includes `test_giao_dien_sg9_nut_ban` (10 + static) and `test_giao_dien_fg4_nut_nap`.
- Walkthrough, data folder outside the repo (pytest tmp_path), 1366×768 vi and 1920×1080 en, API delayed 1.5 s through a Proxy:
  Quản lý (btnSaveClub), Theo dõi (btnGuiKhieuNai), Chuẩn bị (cb-b2-tai-mau): busy label shown, 1 API call after repeated clicks,
  button re-enabled and original label back, no page error. A real failing click (khiếu nại with an unknown student code): backend
  `ok:false` → readable toast, button re-enabled, label restored, no page error.
- Own mutation in a scratch worktree (removed afterwards, repo `git status` clean): (a) drop label restore in `chayNut` → 5 SG-9 +
  2 FG-4 tests fail; (b) drop `sauCung` → 4 FG-4 tests fail; (c) remove the `.catch(baoLoiGiaoDien)` in `chayNut` → ALL 20 TESTS STILL
  PASS (see note 1).
- `ruff check .` clean; `kiem_nhanh` 7/7 (60 cases). soat-ma: tiers 1–2 untouched (diff = JS/i18n/tests/docs, no `.py`); tier 3 above
  (double click, rejection, ok:false, both languages, no new API calls); tier 4: `chu_cam`, `i18n_khoa`, `ma_loi_js` pass.

## Notes (not blocking)
1. Test gap: the `.catch` inside `chayNut` is not what the tests prove. With it removed, the page-level `unhandledrejection` handler
   (`js/00_nen.js`) shows the same toast, so behaviour and tests are unchanged. Acceptance holds either way; a stricter test would count
   `console.error`/toasts (exactly one) or stub `window.onunhandledrejection`. Lead/A may add it; not needed for PASS.
2. Flags set before the call are not reset if the call throws SYNCHRONOUSLY: `S.dang` (`chuyen`, `js/12_chuan_bi_nap.js`) and `S5.dang`
   (`goi`). Reproduced with a Proxy whose function throws: button re-enabled and toast shown, but a second click does nothing
   (1 call, not 2). Real failures arrive as `{ok:false}` via `callApi` and reset the flags first, so this needs `pywebview.api[x]`
   itself to throw. Same as before SG-9 (not a regression). Cheap fix if wanted: reset the flag in `tuyChon.sauCung`.
3. `buoiTaiCho` (`js/05_quan_ly.js`, `veChiBaoPhuBuoi`) now holds the `chayTai` promise; on a thrown (not `ok:false`) failure it would
   hold `undefined`. Same sync-throw-only path as note 2; real failures give `{ok:false}` → reset to null as before (checked).
4. After a language switch while a Chuẩn bị button is busy, the step re-renders a fresh enabled button, so a second click can start
   a second call (flags `S.dang`/`S5.dang` protect only 12). Rare, not an SG-9 acceptance case.
5. Out of scope, seen in the walkthrough: the khiếu nại error text shows the internal session name `__mac_dinh__`.
6. Only red test expected: `test_a13_12_tai_lieu::test_ban_do_ma_so_tep_test_la_so_that` (file count) — person A fixes at integration
   (not run separately by me; the UI run above is the related set).

## Round 2 (checker session_01VfPzNt89iBAQw8naoMzV7d) — range 98908e1..c266cae (FIX-1) — verdict PASS

Own mutations in a scratch worktree of c266cae (removed afterwards), `tests/test_giao_dien_sg9_nut_ban.py` = 19 passed on the clean tree:
1. Remove the `.catch(baoLoiGiaoDien)` in `chayNut` (the `finally(khoi).then(khiXong)` branch) → the 5 `test_api_loi_nut_mo_lai_...` tests FAIL.
   Checked which assert fires: the toast count stays 1 (the page-level handler shows the same toast), `window.__unh` becomes 1 → the
   `unhandledrejection == 0` assert is what proves the `.catch`. (Round 1 note 1 is closed.)
2. Remove the `.catch` in `chayTai` → `test_chay_tai_bat_loi_mot_thong_bao_khong_unhandled` FAILS (1 failed, 18 passed).
3. Remove `sauCung` for `S5.dang` (`goi`) → the step-5 sync-throw UI test AND the static test fail (2 failed). The UI test makes exactly
   2 calls on 2 clicks on the good tree.
4. Remove `sauCung` for `S.dang` (`chuyen`) → only the static test fails (1 failed).

`S.dang` — is the static-only check adequate? A UI test IS feasible: the coder's reason ("needs uploaded files") does not hold, step 4
tests seed files with `set_input_files` (`test_giao_dien_fa_m9_nap.py::test_duong_a_lech_giua_hai_de_hien_hop_xac_nhan`). I wrote a
15-line scratch test (not committed) from that file's `mo` fixture, `_bo_lech`, `_de_3_de`: open path "A", `set_input_files([lst]+thi)`,
wait for 3 rows, replace `pywebview.api` by a Proxy whose `chuyen_tep_forms` counts and throws synchronously, click `#cb-nap-chuyen`,
wait for `.toast.is-error` and for the button to be enabled, click again, `wait_for_function(window.__goi === 2)`. Result: PASSES on
c266cae; with the `S.dang` `sauCung` removed it FAILS (timeout, only 1 call). So the behaviour is correct (verified), and the static
check does fail on removal, but it pins exact source text (a reformat breaks it, a behavioural regression with other wording would not).
Not blocking for PASS: recommend the lead/A swaps the static assert for that UI test (same shape as the step-5 test) at integration.

Re-runs (HEAD e5747dc = c266cae + docs): `ruff check .` clean; `kiem_nhanh` 7/7 (needed `git fetch origin main` for `trung_khit`: 15 cases
identical); `js/12_chuan_bi_nap.js` diff = exactly the two `sauCung` options (no other change); test diff = test file only.
Chromium (PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers): ALL `tests/test_giao_dien_*.py` + `test_t3_l2_buoi.py` = 498 passed, 0 skipped, 0 failed (738 s); includes SG-9 (19), FG-4 (10) and the tabs 05/10/11/12/13 files.
