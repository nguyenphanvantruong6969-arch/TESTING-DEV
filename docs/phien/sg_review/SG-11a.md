# Review SG-11a (checker, round 0) — git diff e676654..103aef6, branch claude/sg-a

Verdict: **PASS**

1. Scope — all five fixed, nothing else. M6 `color-scheme: light` on `:root`; M7 `@media (max-width:1100px)` (narrower `.main` padding, `#kqBang` cell min-width/padding; ≥1100 px unchanged); L1 `.hs-buoi-nhan` → `--gold-text`; L4 `.main:has(#view-scoring.is-active)` shares the Kết quả full-width rule; L5 `#xuatFaAnGoiY` hint + `hidden = !!fa` in `loadMatchResults` + `.hint-text[hidden]` rule + vi/en string. M4 not touched. Backend: only a new test .py in the diff.
   Fable's report unreadable (D-A1): findings known only from the spec line; the "For Truong" note (consistency table + glossary deferred, report unreadable) EXISTS in STATUS_A.md and in MANH_A_SG11a.md.
2. Red-first — scratch worktree at e676654 + only the new test file: 6 failed / 9 passed (M6, M7 ma-1024, L1, L4 ×2, L5 non-FA). At 103aef6: 15 passed. Every finding has a red test.
3. Mutation (scratch worktree at 103aef6, one break each, restored): remove color-scheme → M6 test fails; L1 back to `--gold` → L1 fails; L4 `width:auto` → both L4 fail; media query disabled → M7 ma-1024 fails; L5 `hidden = true` → L5 non-FA fails.
4. Tests ran for real — `tests/test_giao_dien_*.py` (72 files) + `test_van_phong_tu_nhien.py` + `test_ws_nhan.py` with Chromium: **546 passed, 0 skipped, 0 failed** (15 min). New file alone: 15 passed.
5. Invariants — `kiem_nhanh` 7/7 (60 cases = 3 sets × 20 seeds byte-identical; ruff clean; i18n keys vi+en; no change of run_history). Python outside tests untouched → inv. 1–8 not at risk; DA core untouched.
6. Strings — `xuat_fa_an_goi_y` in vi and en, inside the SG-A marker block (i18n.js lines ~1002 and ~1996). Plain words, no internal codes, `{slot_l}` is substituted ("club" in en screenshot). Quoted mode name matches `ws_r_fa_daa`.
7. Browser walkthrough (Chromium, data outside repo, scratchpad): Results (CLB view and student-code view) at 1024×768 vi, 1366×768 vi, 1920×1080 en: page overflow 0, table fits its container (1024: 678/678, 1366: 972/972, 1920: 1134/1134); Nhập điểm 1366 vi / 1920 en: same content width as Results, no overflow; All tabs at 1024 and 1366: no page overflow. Export area non-FA (vi 1366, en 1920): FA buttons hidden, hint shown once; FA workspace: four buttons visible, hint hidden. OS dark-mode emulation: page, tables, inputs stay light.
8. soat-ma — lõi: untouched; backend: untouched; giao diện: above + `lang` en/vi both fine; vệ sinh: ruff clean, MANH fragment written (CHANGELOG/TIEN_DO not edited, per 2.3).

Optional (does not block):
- `.hint-text[hidden] { display: none; }` and the M7 media block sit after the `=== end SG-C ===` marker at the end of `style.css`; allowed for person A (2.3) but lead A may want to move them above the SG-B/SG-C blocks at integration to keep the markers last.
- The M7 test only asserts no overflow for the "ma" view at 1024 (other widths are guards); fine.
