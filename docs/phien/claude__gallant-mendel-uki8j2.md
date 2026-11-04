# Branch handoff: claude/gallant-mendel-uki8j2 (coordinator file)

> Purpose: a fresh session reads CLAUDE.md, `docs/phien/T3_GIAO_THUC.md`, then THIS file, and can continue.
> Language: English. Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".
> Child roles keep their own files: `claude__gallant-mendel-uki8j2__impl.md`, `__tester.md`.

## Feature / goal
Execute the T3 UI debloat study (`docs/nghien_cuu/T3_DEBLOAT_GIAO_DIEN.md`) in four lots, automated by a coordinator +
implementer + tester chain (protocol: `docs/phien/T3_GIAO_THUC.md`). Item codes: outside the registry, Truong approved
2026-11-04: `T3-L0`..`T3-L3` (one TIEN_DO row each). Display-only changes except L0 B1/B2 backend guards.
Algorithm, `match_results`, `run_history`, STB, CSV column contract: untouched.

## Decisions (Truong, 2026-11-04; do not re-ask)
- Scope L0->L3. One branch; one open PR at a time; stacking on an unmerged PR allowed; Truong merges.
- Approval gate: end of each lot (PR + tester report + screenshots). CI red / review comments: impl fixes, max 3 rounds.
- Blocked item (rule 7): skip, list under "Needs Truong", continue. Push notify: PR ready, every session handoff.
- Thresholds: children 400k, coordinator 700k. Tester model: Opus for L0, Sonnet for L1-L3. Impl: Sonnet.
- Quality gate: related tests + soat-ma + tester diff review + screenshots; full suite only on CI.
  L0 additionally proves invariant 1 (3 datasets x 20 seeds identical match_results).
- B1: fix both layers. B3: change the error text only (no toggle).
- Tab 03 name: "Chi tiết và xuất tệp" / "Details and export".
- Results tab (T3-16/17/18) "strong": hide "Theo lớp" while no class exists; drop tier-2 sort row, sort by clicking column
  headers; drop the "Thứ tự" column.
- T3-19 yes ("Tải bảng này" in Results). T3-22: Điểm chuẩn ONLY in Quản lý (remove the card/button from tab 03;
  this overrides the study's suggestion and the 5.3 row `ql_tab_dc`).
- T3-27 yes (UI wording = Sổ nhập wording; display text only). T3-11 yes (wizard one step from template).
  T3-31 yes (Điểm chuẩn = one table; dot chart moves into per-club "Xem chi tiết"; drop 3-colour bar + 3 levels).
- NOT doing: T3-41 (em dash empty cells stay), removing the 01-06 numbers from the sidebar.
- T3-14 label route: option (a) from the study (JS table mirroring `NHAN_BUOI`, labels via `i18n.js`, test that both
  tables match). Coordinator default from the study's recommendation; tell Truong in the L2 PR.

## Lot L0: product bugs (study section 0) - tester Opus
- B1 / T3-26: editing a club with blank fields wipes reserve seats, priority group, session.
  UI (`js/05_quan_ly.js`): row click fills the form from the row; permanent labels on the 6 inputs.
  Backend (`create_or_update_club` and its API wrapper): on UPDATE, a field not sent keeps its stored value.
  Tests: "edit quota keeps reserve/group/session" (API) + UI test row-click prefill.
- B2 / T3-01: Run with 0 students or 0 clubs writes run_history and locks STB seed 42.
  UI: disable "Chạy sắp xếp" with a reason when 0 students or 0 clubs; no green "ready" on an empty workspace.
  Backend: refuse before backup/lock/any write with a new error code (i18n_errors.py vi+en -> `python tao_i18n_js.py`).
  Tests: empty workspace run -> {ok:false, code}; run_history row count and stb lock unchanged.
- B3 / T3-42: `wharton_ho_so_chua_hop_le` text points to a doable action (Quản lý, tab Điểm quyết tâm,
  "Phóng cho đủ 100"). vi+en; regenerate JS; test the text no longer mentions turning the feature off.

## Lot L1: text and small display (study section 8 lot 1)
T3-05, T3-08, T3-09, T3-13, T3-30, T3-36, T3-37, T3-38, T3-39, T3-40, T3-43, and text tables 5.1-5.3 EXCEPT:
`nav_others`/`others_title` and `nav_admin`/`admin_title` (L3), `ql_tab_dc` (kept, see decisions), `kq_sx_ngay`/
`kq_sap_nhan` (row removed in L3), T3-27 wording (L3). Fallback text in `index.html` must equal the catalog.

## Lot L2: fewer blocks, grouped buttons (study lot 2)
T3-14 (route a), T3-02, T3-03, T3-04, T3-06, T3-07, T3-10, T3-12, T3-15, T3-20, T3-21, T3-23, T3-24 (MOVE NV1 numbers,
never delete), T3-25, T3-28, T3-29, T3-32, T3-33, T3-34 (keep "Xuất CSV học sinh này" inside the ⋯ menu), T3-35.
Keep everything in study section 7 ("Những thứ KHÔNG nên bỏ").

## Lot L3: Truong's decisions above
Tab 03 rename; T3-16/17/18 strong; T3-19; T3-22 (remove from tab 03); T3-27; T3-11; T3-31; tab 05 label "Quản lý CLB".

## Plan (coord writes; impl/tester tick)
- [x] P0 protocol, role-aware Stop hook (`.claude/hooks/handoff_khi_day_ngu_canh.py`, tests/test_hook_ban_giao.py 6 cases)
- [ ] L0 impl  - [ ] L0 tester NO BUGS  - [ ] L0 PR
- [ ] L1 impl  - [ ] L1 tester NO BUGS  - [ ] L1 PR
- [ ] L2 impl  - [ ] L2 tester NO BUGS  - [ ] L2 PR
- [ ] L3 impl  - [ ] L3 tester NO BUGS  - [ ] L3 PR
- [ ] Final report to Truong (files, new tests, skipped items, screenshots)

## Sessions (overwrite on every change)
| Role | Session id | Model | Status |
|---|---|---|---|
| coord | session_01YVAyu1tdPE9AURCeJXaN5S | Opus | active |
| impl | session_01YVAytzNrwmcsLv5pa3nYSD | Sonnet | L0 running (GO L0 sent 13:15 UTC) |
| tester | (to create per lot: Opus L0, Sonnet L1+) | | |

## Current state (overwrite each handoff)
- P0 done (639b4e7). L0 sent to impl. No PR open.

## Needs Truong
- (none yet)

## Next steps (ordered)
1. Wait for "IMPL DONE L0"; then create tester (Opus) with `REVIEW L0 639b4e7..<head>`.

## Files touched
- .claude/hooks/handoff_khi_day_ngu_canh.py: role file `.claude/phien_vai.json`, per-role threshold and message
- .gitignore: `.claude/phien_vai.json`
- tests/test_hook_ban_giao.py: 6 cases for the hook
- docs/phien/T3_GIAO_THUC.md, docs/phien/claude__gallant-mendel-uki8j2.md: protocol and plan

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-04 | Opus (coord) | Asked Truong 16 decisions, wrote protocol + plan, role-aware hook | |
