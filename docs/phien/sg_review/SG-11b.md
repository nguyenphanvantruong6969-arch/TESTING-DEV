# SG-11b review (M4: workspace chooser focus trap + Esc + initial focus)

Checker: session_01YVAytyjEXTMBsvTPMw9NsZ · range 5ab87d0..f1ae45a (branch tip 49c3351) · Round 0 → verdict **FIX-1**

## Evidence per checklist point
1. **Scope — OK.** Diff = `js/075_workspace.js` (+23, `wsBayTab` + one `addEventListener`), the new test file, fragment `MANH_B.md`. No M6/M7/L1/L4/L5, no CSS, no strings, no i18n, no Python. Initial focus (heading `#wsTieuDe`, tabindex -1), Esc-when-closable and focus return to `#btnWorkspace` already existed; the diff adds only the Tab trap.
2. **Red-first — real but partial.** Scratch worktree at 5ab87d0 + new test file: 2 failed (`test_tab_xoay_vong_ca_hai_chieu`, `test_tab_van_giu_bay_trong_trinh_huong_dan`), 3 passed (initial focus, Esc closes, Esc blocked at first start: pre-existing behaviour). At 49c3351: 5 passed.
3. **Mutation — OK.** Disabled the "Tab from last control wraps" branch in a scratch worktree → the same 2 Tab tests red. Worktrees removed.
4. **Tests ran for real.** `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`: new file + every `tests/test_giao_dien_*` that greps wsOverlay/wsMoManChon/btnWorkspace/wsMoTinhNang (a13_12_ws, a13_13_kiem_nhan, a14_lop, fg1_bat_tinh_nang, sg2_diem_quyet_tam, t3_l1_ws, t3_l3, ws_giao_dien, ws_nhan_giao_dien, ws_wharton_giao_dien) + `test_ws_nhan.py` + `test_van_phong_tu_nhien.py`: **150 passed, 0 skipped**. The known red a13_12 map test was not in this selection.
5. **Invariants.** `kiem_nhanh --co-so origin/main --so-seed 20`: 7/7 (60 cases identical); `ruff check .` clean. No Python in the diff, so inv. 2/5/6/7 and the DA core are untouched.
6. **Strings:** none added. OK.
7. **Browser walkthrough (Chromium, keyboard only; scratch probes outside the repo).** 1366×768 vi and 1920×1080 en screenshots: dialog fits, no horizontal overflow, focus ring visible on the focused control. Results:
   - List view: open → focus on heading; Tab/Shift+Tab wrap correctly (menu `⋯` summary, Mới, Nhập, Đóng); hidden file input and controls of a closed `⋯` menu are skipped; open menu items join the cycle.
   - Edit/rename row: cycle OK, re-render (`wsLamMoiDanhSach`) puts focus back on the heading.
   - Wizard (simple, and custom steps 1-3): Tab and Shift+Tab never leave the dialog (40 presses each).
   - FG-1 "features after allocation" dialog: cycles OK (Wharton / Lưu / Hủy).
   - Esc closes only when `wsCoTheDong`, focus → `#btnWorkspace`; at first start (2 workspaces, none chosen) Esc does nothing; after close, Tab on the main page works normally (no hijack).
   - Esc inside the wizard closes the whole chooser and drops typed input, same as the Cancel button; no half state (reopen → clean list).
8. **soat-ma four tiers on the diff.** Tier 1 (algorithm core) and 2 (backend): no Python in the diff, N/A. Tier 3 (UI): see item 7 and findings below. Tier 4 (hygiene/docs/tests): fragment written in `MANH_B.md`, no forbidden files edited, test file named per convention; test gaps listed below.
9. Special: n/a for SG-11b.

## FIX-1 (blocking)
1. **`js/075_workspace.js`, `initWorkspace` (Esc listener on `#wsOverlay` only).** Esc closes the chooser only while focus is inside the overlay element; focus on `<body>` makes it dead although `wsCoTheDong` is true. Why: M4 requires Esc to close the dialog; the coder moved Tab to `document` but left Esc on the overlay, so the two behave differently. Repro (closable chooser): click `#btnWorkspace`, click the hint text `#wsHop .hint-text` (activeElement becomes BODY), press Escape → `#wsOverlay` stays visible (reproduced). Same after the FG-1 dialog closes (item 2). How to verify: handle Escape in the same document-level handler (topmost `.ws-overlay` is `#wsOverlay` and `wsCoTheDong`; the FG-1 dialog keeps its own handler and must still close only itself); new UI test = click hint text then Esc → hidden and focus on `#btnWorkspace`; mutation = remove the document-level Esc path → test red.
2. **`js/075_workspace.js`, `wsMoTinhNang` → `dong()`.** Closing the FG-1 dialog (Esc, Hủy, or after Lưu when `wsCoTheDong` is false) re-shows the chooser but focus is left on `<body>` (`inTop=false` in the probe) — the dialog loses its focus anchor, so a keyboard user must Tab first (and see item 1). Why: lead point (a)/(b): focus must stay inside the dialog and return sensibly after a nested dialog. How to verify: after `dong(false)` focus lands inside `#wsOverlay` (heading `#wsTieuDe` or the `⋯` summary that opened it); UI test: open ⋯ → "Tính năng sau khi xếp…" → Esc → `document.activeElement` is inside `#wsOverlay`.
3. **`index.html` `#wsOverlay` (static `aria-modal="true"`) / `wsHienOverlay`.** `aria-modal="true"` stays on the hidden overlay (probe: `<div class="ws-overlay" id="wsOverlay" hidden aria-modal="true" …>`), while `role="dialog"` is removed when hidden. Why: lead point (c) / FG-1 rule: dialog semantics exist only while the dialog is shown. How to verify: set `aria-modal="true"` together with `role="dialog"` in `wsHienOverlay(true)` and remove both in `wsHienOverlay(false)`; drop the static attribute; test asserts no `aria-modal` and no `role` when hidden, both present when shown (the existing test only checks the open state).

## Optional (does not block)
- Esc with a row `⋯` menu open closes the whole chooser as well as the menu (the global handler in `js/00_nen.js` and the overlay handler both fire). Closing only the menu first would be nicer.
- The new tests never exercise the FG-1 dialog, the edit row, a re-render, or an open `⋯` menu; adding one cycle test for each would pin the behaviour verified manually above.
- Initial focus lands on the heading (tabindex -1), not a control; acceptable (reads the title, next Tab = first control), noted only.
- No existing shared focus helper in the repo (grep for `Escape`/`Tab` handling): `wsBayTab` does not duplicate anything.
- The coder did not run soat-ma as a separate pass (stated in the Log); done here.

---

# Round 2 (M4 only) — range 5ab87d0..29bfa1e (fix f1ae45a..29bfa1e, branch tip dff2363)

Checker: session_01YVAyu3PXika1Vx6orU1Yim-checker-r2 (Sonnet) · Verdict **PASS**

## FIX-1 closure (Chromium, keyboard only; scratch probes outside the repo, 1366×768 vi and 1920×1080 en)
1. **Esc at document level — closed.** Click `#wsHop .hint-text` (activeElement = BODY) → Esc → `#wsOverlay` hidden, focus on `#btnWorkspace`. Same after the FG-1 dialog closes. First start (no workspace chosen): Esc does nothing, also from body; Tab stays trapped (20 presses). Probe waited for the list to render (an earlier unwaited probe of mine raced the async render: probe error, not a product defect).
2. **Focus after FG-1 dialog — closed.** Esc and Hủy/Cancel both return focus inside `#wsOverlay` (the `⋯` summary), chooser stays open, role/aria-modal restored; next Esc closes the chooser. FG-1 Tab cycle (12 presses) stays inside it; Esc in FG-1 closes only FG-1.
3. **aria-modal — closed.** Hidden: no `role`, no `aria-modal`; shown: `dialog` + `true`. Static attribute gone from `index.html` (the one-attribute edit, declared in `MANH_B.md` for person A: confirmed it is the only `index.html` change).
4. **Menu-first Esc — closed.** Open row `⋯` menu → Esc closes only the menu, focus on its summary; second Esc closes the chooser.
- Wizard: Tab trap (15 presses) holds; Esc closes the chooser, reopen shows a clean list (same as round 1). Chooser Tab/Shift+Tab 20 presses each way stays inside. Screenshots at both sizes: no horizontal overflow, dialog fits.

## Global Esc handling / shared files
- Diff touches only `js/075_workspace.js`, `index.html` (1 attribute), the test file, `MANH_B.md`, status/review docs. `js/00_nen.js` is **unchanged**.
- `wsBanPhim` is a capture-phase `document` keydown listener registered once in `initWorkspace`. Its first line returns when no `.ws-overlay` is visible, so with the chooser hidden it does nothing: probe confirmed Esc and Tab on the main page behave normally (Tab is not hijacked, Esc not swallowed).
- `ev.stopPropagation()` is called only when a `details.menu-khac[open]` exists inside the topmost visible overlay. This is the only place another handler (the global `⋯`-menu close in `00_nen.js`) is pre-empted, and there the menu is closed by `wsBanPhim` itself. All other Esc handling in `js/`: grep finds only `00_nen.js:339` (closes every open `details.menu-khac`) and the FG-1 dialog's own `keydown` in `075_workspace.js`; the other `keydown` handlers (`00_nen.js:125`, `02_van_hanh.js`, `04_nhap_tai_cho.js`, `05_quan_ly.js`, `12_chuan_bi_nap.js`) react to Enter/Space/arrows only. No `<dialog>` / `showModal` in the app. So no other dialog/overlay/menu changes behaviour. UI tests that cover `menu-khac` (fg1_bat_tinh_nang, sg2_diem_quyet_tam, ws_giao_dien) and `test_giao_dien_t3_l2_van_hanh.py` (Esc) are in the run below.
- Mutation (scratch edit, restored, `git status` clean): capture → bubble phase → `test_dong_hop_tinh_nang_tra_focus_vao_man_chon` and `test_esc_dong_menu_truoc_roi_moi_dong_man_chon` red.

## Tests / hygiene (whole range)
- `tests/test_giao_dien_sg11b_focus_man_chon.py`: 9 passed, 5 runs in a row, no flake, no hard sleeps.
- New file + every `tests/test_giao_dien_*` grepping wsOverlay/wsMoManChon/btnWorkspace/wsMoTinhNang + `test_ws_nhan.py` + `test_van_phong_tu_nhien.py` + `test_giao_dien_t3_l2_van_hanh.py`: **128 passed, 0 skipped** (Chromium really ran).
- `kiem_nhanh --co-so origin/main --so-seed 20`: 7/7 (after fetching `main`; the first run said 6/7 only because `origin/main` was missing locally). `ruff check .` clean. No Python / CSS / i18n in the range, so tiers 1 and 2 (core, backend) are N/A and invariants 1–8 are untouched.
- soat-ma tier 3 (UI): item 5 (keyboard: Tab, Shift+Tab, Esc) exercised above; items 1–4, 6 not affected (no API calls, no data in `innerHTML`, no strings added). Tier 4: fragment updated in `MANH_B.md`, test file name per convention, no forbidden files edited. Round-1 evidence reused unchanged for: scope (M4 only), initial focus on the heading, edit-row/re-render focus, wizard custom steps, `⋯` menu items joining the cycle.
- Known expected red (not run in this selection): `test_a13_12_tai_lieu.py::test_ban_do_ma_so_tep_test_la_so_that`.

## Optional (non-blocking)
- The closed-state test checks role and aria-modal only for `#wsOverlay`; the FG-1 layer is a separate element created per call (removed on close), so nothing to leak.
