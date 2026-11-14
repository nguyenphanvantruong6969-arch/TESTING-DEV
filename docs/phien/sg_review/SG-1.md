# Review SG-1 (C3) — checker, round 0 — diff 5b474dd..9934af2 — verdict FIX-1

Evidence per checklist point (spec: SOAT_GIAO_DIEN_KE_HOACH.md §3 SG-1; Fable report unreadable, D-A1).

1. **Scope** — mostly OK, one defect. Blocking error `fa_clb_tuyen_chon_chua_co_diem` {club_id, so_dang_ky, so_nv1} is added in
   `fa_daa.kiem_truoc_fa`; `kiem_fa_tu_csdl` feeds it from `club_scores`, so run (`api.run_pipeline`) and health report
   (`get_data_health_report`) call the SAME function (same numbers). Text names the club, the count, and both fixes. Nothing extra.
   `so_dang_ky` = students whose list contains the club: correct. **`so_nv1` is wrong with more than one session (see FIX-1).**
   Preview path `api_nhap._canh_bao_fa_xem_truoc` does not pass `tested_scores`, so it does not show the new error (workbook scores
   are not read there). Spec names only `kiem_truoc_fa` / health report, so not a defect; noted under Optional.
2. **Red-first** — scratch worktree at 5b474dd + only the new test file: 5 failed / 3 passed (the 3 passes are the negative cases).
   At 9934af2: all 8 pass.
3. **Mutation** — replaced `and not tested_scores.get(cid)` by `and False` → 3 tests fail (pure fn, pipeline, health). Restored; tree clean.
4. **Tests** — `tests/test_sg1_tuyen_chon_khong_diem.py`, `test_fa_huy_chuong.py`, `test_ws_nhan.py`, all `tests/test_fa_*.py`:
   321 passed. No UI item, no Chromium test needed. The edit to `test_pipeline_chay_duoc_voi_huy_chuong_khong_can_100_diem` only
   adds one score because the old test built exactly the now-blocked case: justified, minimal.
5. **Invariants** — `kiem_nhanh --co-so origin/main --so-seed 20`: **7/7** (60 cases byte-identical). Non-FA: check is only
   reached from the FA branch (`kiem_fa_tu_csdl` / `bat_fa`); test `test_khong_fa_khong_co_loi_moi` passes. Inv. 2: no change to
   priority code. Inv. 5: blocked run stops in validate, `run_history`/`match_results` stay empty (test). Inv. 6: `{code, params}`.
   No schema/CSV change. DA core untouched.
6. **Strings** — vi + en present, natural, no internal code, inside `=== SG-A ===` block only; `i18n_loi.js` regenerated
   (kiem_nhanh `i18n_loi_khop` OK); code listed in `MA_MOI_SAU_ANH_CHUP` inside the SG-A block.
7. **UI** — not a UI item (message is shown by the existing error renderer); not walked in a browser.
8. **soat-ma** — `kiem_nhanh` all 7 OK. Manual read of the diff for tiers 1–4: no other findings; MANH_A.md fragment present, CHANGELOG/TIEN_DO not edited (correct).
9. Special: none for SG-1.

## FIX-1 (blocking)
1. `fa_daa.kiem_truoc_fa`, line `so_nv1=sum(1 for s in dang_ky if preferences[s][0] == cid)`.
   - Wrong: it counts only students whose OVERALL first club is `cid`. Preferences are one list per student across all sessions
     (`preferences.rank` is global), but "first choice" in FA means first choice WITHIN THE SESSION: see `fa_daa` demand table
     (`nv1`: "số em xếp CLB này đầu tiên TRONG BUỔI", `thay_buoi` logic). In a multi-session workspace the block message would
     report too few (often 0) first-choice students.
   - Repro (checked): clubs A (b1, TU_DO), S (b2, TUYEN_CHON, san 5); prefs s1=[A,S], s2=[A,S]; `tested_scores={}` →
     `so_nv1: 0`; expected 2 (S is each student's first choice in b2).
   - Why: finding C3 / spec use so_nv1 as "how many have it as first choice"; the number must agree with the demand table the
     teacher already sees (rule: same numbers from one definition).
   - Fix: count students for whom `cid` is the first club of its session among their list (same rule as `nhu_cau` `thay_buoi`;
     reuse it or a small shared helper; do not change the demand table's output).
   - Verify: add a test with two sessions (above repro) asserting `so_nv1 == 2`; single-session test stays 3/2; rerun
     `test_sg1_*`, `test_fa_*`, `kiem_nhanh` 7/7.

## Optional (does not block)
- `api_nhap._canh_bao_fa_xem_truoc` could also pass scores from the workbook so the preview warns early (separate item if wanted).

---

# Round 1 — checker — diff 5b474dd..95de0b9 (whole item, after FIX-1) — verdict PASS

Full 2.10 checklist redone on the whole diff. Production code at HEAD equals 95de0b9 (later commits are docs only).

**FIX-1 confirmed done.** `fa_daa.dem_nv1_trong_buoi(clubs, preferences)` counts, per student, the first club of each session
(`thay_buoi` logic, `BUOI_MAC_DINH` fallback, clubs not in `clubs` skipped). `kiem_truoc_fa` uses `nv1_buoi[cid]` for `so_nv1`;
`bang_nhu_cau` now calls the same helper (one definition). Repro from round 0 now gives `so_nv1 == 2`.

1. **Scope** — OK. Blocking `fa_clb_tuyen_chon_chua_co_diem` {club_id, so_dang_ky, so_nv1}; same function feeds run and health
   report via `kiem_fa_tu_csdl`; `so_nv1` now per session; nothing extra. Only change outside the item: `test_fa_huy_chuong`
   adds one score (justified, round 0).
2. **Red-first** — scratch worktree at 5b474dd + new test file: 6 failed / 3 passed. FIX-1 test on 9934af2 (before the fix):
   fails with `so_nv1: 0 != 2`. At 95de0b9: 9 passed.
3. **Mutation** — (a) helper counts only the overall first club (`ds[0] == c`) → `test_ham_thuan_hai_buoi_nv1_tinh_theo_buoi` fails;
   (b) `so_nv1=0` constant → 4 tests fail. Worktrees removed; main tree clean.
4. **Tests** — `test_sg1_*`, `test_ws_nhan`, all `tests/test_fa_*.py`, and `test_giao_dien_fa_ket_qua.py` (Chromium, `/opt/pw-browsers`):
   **2318 passed, 1 skipped** (the skip is `test_fa_tinh_chat.py:255`, a deferred V§13.12 item, not Chromium, not related).
   `bang_nhu_cau` output unchanged: its tests (`test_fa_nhu_cau`, `test_fa_gap7_goi_y`, `test_fa_m6_tai_lieu`, `test_fa_tinh_chat`)
   pass, and a differential check of 300 random multi-session cases (incl. `buoi=None`, unknown club ids, empty lists) gives the
   identical md5 of all outputs at 5b474dd and 95de0b9.
5. **Invariants** — `kiem_nhanh --co-so origin/main --so-seed 20`: **7/7** (60 cases byte-identical, ruff clean, no UPDATE/DELETE on
   `run_history`). Inv. 2: priority code untouched. Inv. 5: blocked run stops in validate, no rows written (test). Inv. 6: `{code, params}`,
   one message source. Inv. 7: no schema/CSV change. DA core untouched; `club_scores` is only read.
6. **Strings** — vi + en, natural, no internal code; inside `=== SG-A ===` only; `i18n_loi.js` matches regeneration; code in
   `MA_MOI_SAU_ANH_CHUP` (SG-A block).
7. **UI** — not a UI item (existing error renderer); no browser walkthrough needed. `test_giao_dien_fa_ket_qua.py` ran for real (no skips).
8. **soat-ma** — `kiem_nhanh` 7/7; manual read of the whole diff, four tiers: no findings. MANH_A.md fragment present and now accurate;
   CHANGELOG/TIEN_DO not edited (correct). Optional: the fragment could mention `dem_nv1_trong_buoi` (one-line doc nit).
9. **Special** — none for SG-1.

No blocking findings. Optional list from round 0 still stands (preview path does not pass workbook scores).
