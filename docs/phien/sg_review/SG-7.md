# SG-7 review (checker, session_01VfPzNv27d7DuoAmjt9g79n) — range 9709a20..b4800ad — verdict PASS

Fable's report unreadable: judged against SOAT_GIAO_DIEN_KE_HOACH.md §3 SG-7 (FG-6 rule, ONE shared JS helper, no third style).

## Passed
- ONE helper `veCanhBaoGom` (`js/00_nen.js`, single definition). Step 4 (`js/12_chuan_bi_nap.js`) and the import panel
  (`veCanhBaoNhap`, `js/02_van_hanh.js`) both call it. Old code gone: `CANH_BAO_HIEN_DAU`, the "Xem 5 dòng đầu" button and
  the `slice(0, 30)` + internal-code prefix (`ma: `) are not in the JS any more (grep clean).
- Counts: group > 5 shows "N cảnh báo cùng loại" + exactly 5 examples + "và (N−5) trường hợp nữa"; group ≤ 5 shows all lines, no
  header, no "nữa". Walkthrough with 120 same-code warnings: "120 …", 5 lines, "và 115 trường hợp nữa" (115 = 120−5). Text is
  set with `textContent` (no innerHTML, no XSS path). Backend `canh_bao` items always carry `ma`, so grouping by code is safe.
- Walkthrough in browser mode, data folder outside the repo (scratchpad), real UI: 1366×768 vi and 1920×1080 en
  (language via the EN toggle): import panel and step 4 both render the same style; no horizontal overflow; panel height
  165 px for 120 warnings; no page errors; en shows "120 warnings of the same kind. Examples:" / "and 115 more cases".
  (Step-4 API and the import list were fed by `page.route` / `canhBaoNhapGanNhat`, same as the item tests.)
- Strings only in the SG-C i18n block, vi + en (`canh_bao_gom_dau`, `canh_bao_gom_nua`); no internal codes visible
  (test asserts it). CSS only in the SG-C block of `style.css`. No expand button remains, so no keyboard-access gap.
- Tests (UI really run in Chromium, PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers): `test_giao_dien_sg7_canh_bao_gom`,
  `test_giao_dien_t3_l2_van_hanh` (2 T3-02 tests rewritten to the new rule), `test_ws_nhan`, `test_van_phong_tu_nhien`
  = 74 passed, 0 skipped. `ruff check .` clean. `kiem_nhanh` 7/7 (60 cases, 3 sets × 20 seeds identical).
- soat-ma tiers: 1 core and 2 backend untouched (diff is JS/CSS/i18n/tests/docs only); 3 UI: textContent, no new API call,
  both languages checked; 4 hygiene: `i18n_khoa`, `chu_cam`, `ma_loi_js` pass. Only red test: the known
  `test_a13_12_tai_lieu::test_ban_do_ma_so_tep_test_la_so_that` code-map count (275 files) — expected, person A fixes at integration.
- Mutation check not re-run by me (checkers must not touch code); coder's log reports it (removing the 5-example slice → 2 UI tests fail).

## Notes (not blocking, no fix needed)
1. FG-6 run-log grouping (`showLog`, `LOG_SO_LOI_MOI_MA`, "và N lỗi nữa") is a separate renderer for errors with technical
   detail; same rule in spirit (group by code, cap, "and N more") but no count header and the word "lỗi". It is not one of the two
   surfaces SG-7 names; I judge it consistent, not a third style. `ketQuaNapForms` (`js/10_theo_doi.js`) still prints an uncapped
   `<ul>` of per-reason items (different data, FG-6 one-sentence toast); out of SG-7 scope.
2. Step 4 with a single code shows "120 cảnh báo:" then "120 cảnh báo cùng loại. Ví dụ:" — slightly redundant, cosmetic.
3. Dead leftovers outside the SG-C block, for person A at integration: i18n keys `canh_bao_gom`, `canh_bao_xem_dau`,
   `canh_bao_thu_gon`; the old flex rule `.canh-bao-nhom` (style.css ~2889), overridden by the SG-C rule.
