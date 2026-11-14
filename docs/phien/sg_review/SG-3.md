# SG-3 review (C2, FA preference rank) — checker session_01TGThn5ifqoQYavHTFkb9a4

Diff: `39de078..f2e7702` on `claude/sg-a`. Round 0. Spec: `SOAT_GIAO_DIEN_KE_HOACH.md` §3 SG-3, D3.
All data below is SIMULATED test data.

## Verdict: see Log line (PASS / FIX-1). Checklist evidence

1. **Scope — holds.** One post-process loop at the end of `fa_daa.chay_fa_daa` (step 7) rewrites
   `ket.per_buoi[buoi].rank_in_student_pref` to the index in the student's ORIGINAL list within the session
   (`preferences` filtered by `clubs_fa` and session); a club not in that list → key popped → NULL on write (D3).
   Panel `get_phan_bo_nguyen_vong` gets `ngoai_danh_sach`; `khong_ro` = the rest; results export and
   `js/03_ket_qua.js` show a separate label; vi + en strings inside the SG-A marker block only. Nothing else touched
   (no DA core, no schema, no `i18n_errors.py`).
2. **Red-first — holds.** Scratch worktree at `39de078` + only `tests/test_sg3_hang_fa.py`: 5 failed. At `f2e7702`: 5 passed.
3. **Mutation — holds.** (a) rank line → `hang_buoi.get(sid, 1)`: 4 of 5 fail. (b) `pop` → `pass`: 3 of 5 fail. Restored.
4. **Tests run for real.** Item tests 5/5. Related set (`-k "fa or nguyen_vong or dashboard or bao_cao or phan_bo or xuat or ket_qua"`
   incl. Chromium `test_giao_dien_*`, nothing skipped): see result line at the end of this file.
5. **Invariants — hold.** `kiem_nhanh` 7/7, 60 cases (3 sets × 20 seeds) byte-identical to `origin/main`
   (ruff, chu_cam, i18n all PASS). Inv. 2: the new loop only READS `preferences` to produce an OUTPUT value after the
   solve; `compute_club_priority` untouched. Inv. 5: pipeline order unchanged (step runs inside `chay_fa_daa`, before
   sanity/verify and the single write transaction). Inv. 6: panel still `{ok,data,errors}`. No schema / CSV change.
   `git diff --name-only` has no `rbda_priority_pipeline.py`.
6. **Strings — hold.** `nv_ngoai_danh_sach` vi "Xếp ngoài danh sách nguyện vọng" / en "Placed outside their choices", natural, no codes,
   inside `=== SG-A ===` block. (Optional: the export row text in `api_xuat.py` is hard-coded Vietnamese, same as the
   neighbouring "Nguyện vọng %d" rows — existing pattern.)
7. **UI — holds.** Browser mode (browser_host + Chromium), FA run with 2 fallback students (HS002, HS004): tab "Chi tiết/others" →
   panel "Mức đáp ứng nguyện vọng". vi 1366×768 and en 1920×1080: new row "Xếp ngoài danh sách nguyện vọng / Placed outside their choices"
   2 · 40 %, grey bar + donut arc + legend, label wraps to two lines without overflow (page and panel `scrollWidth ≤ clientWidth`),
   headline "40 % first choice · 60 % top 3" equals a direct count, no `pageerror`. Screenshots kept in scratchpad only. Table cells at
   `03_ket_qua.js` 530/920 already render NULL as "—".

### Lead's points
- **(a) Every reader/writer gets the corrected rank — holds.** `api.run_pipeline` uses `result = kq_fa.ket_qua`; the only writers
  (`cac_dong_ket_qua` / `cac_dong_match_results` in the pipeline) read `per_buoi[buoi].rank_in_student_pref`, which step (7)
  has already corrected. No top-level/merged rank dict exists on `KetQuaTuan` (only `per_buoi`), so nothing is built before step (7).
  `sanity_check_result` / `verify_stability` do not read rank. Everything else reads the DB column: `ket_qua_truoc` copy and
  `run_history` copy (`api.py` ~1365, ~1462), CSV (`api.py` ~889), `api_xuat` exports, `api_bao_cao` (dashboard line ~300, panel),
  `fa_sau_xep.doc_du_lieu_dashboard` / `chi_so_dashboard` (NULL handled: `ty_le_top2` guards `None`, `ty_le_nv1` counts `== 1`).
- **(b) Equals `rank_in_list` — holds.** Both use the same filter (`preferences` ∩ `kq.clubs`, same session). Test
  `test_hang_giong_rank_in_list_cua_ly_do` + my extra two-session run (HS001 `thu_4` placed in X2 = first of 4 declared clubs in `thu_4`,
  overall position 3): `match_results` rank = `fa_ly_do.rank_in_list` for every ACCEPTED row.
- **(c) Fallback into an unlisted club — holds.** NULL stored; panel shows it as its own label, not counted as any NV, not in `khong_ro`.
- **(d) Non-FA byte-identical — holds.** See 5. The loop is inside `chay_fa_daa` only.
- **(e) Academic list — complete (see below).**
- **(f) UI — see 7.**

### Checklist 9 — FA first-choice numbers (grep `docs/`, `du_lieu_test/`)
My own grep (`NV1`, `first-choice`, `top-2`, `ty_le_nv1`, `rank_in_student_pref`, % near them) confirms the coder's list:
- Not affected: `du_lieu_test/mo_phong_fa_daa.py` (`_dem_tc` uses true preference `thich`, only `assignment`), and the 63 % top-2 in
  `FA_DAA_VISION.md` ~206. No script in `du_lieu_test/` other than `bao_cao_phan_bo.py` / `demo_t4m.py` / `do_t4m_thi.py` / `do_boc_tham.py`
  reads the stored rank, and none of them runs FA (no `fa_daa` import / `fa_bat`), so their numbers (incl. `NGHIEN_CUU_TOI_UU.md` NV1 tables,
  `CO_CHE_THUAT_TOAN.md` 79 %) are DA-mode and unaffected.
- To re-check by Truong (cannot tell whether FA-mode): 48 %→79 % (`docs/fable/01_PROJECT_CONTEXT.md` ~128, `02_FABLE_BRIEF.md` ~64,
  `FA_DAA_VISION.md` ~360) and 29 %→47 % (`GIAM_MAY_RUI_KE_HOACH.md` ~26, says "true first choice").
- Any real/past FA run's `ket_qua_phan_bo.csv` / dashboard "Vào NV1" / panel; `bao_cao_phan_bo.py` if run on an FA database.
No number is missing from the coder's "For Truong" note.

## Round 0 findings
No blocking findings. Optional: (1) donut/bars: the new "outside" row and `khong_ro` share the grey `is-khong-ro` style
(distinguishable by label only; acceptable).

## soat-ma four tiers (on the diff)
Core: DA core untouched, STB/seed untouched. Backend: one extra SELECT in a read connection, `_ok/_fail` contract kept, no schema.
UI: one pushed row, i18n keys present in vi + en (`kiem_nhanh` i18n_khoa). Hygiene: ruff clean, new tests 5, MANH_A fragment present
(CHANGELOG/TIEN_DO not edited, per 2.3).

## Test results (item 4)
Related set at `f2e7702`: 2925 passed, 1 skipped, 0 failed. The one skip sits at ~83 % of the run; I did not identify it. Separately, all Chromium
UI tests `tests/test_giao_dien_fa_*.py` + `test_giao_dien_a13_12_ngon_ngu.py`: 65 passed, 0 skipped (`-rs`).

**Verdict: PASS.**
