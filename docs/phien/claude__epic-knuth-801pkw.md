# Branch handoff: claude/epic-knuth-801pkw

> Purpose: a fresh session reads CLAUDE.md, then THIS file, and can continue without the old chat.
> Language: English (cheaper in tokens). Cap: 150 lines. Rewrite "Current state"; only APPEND to "Session log".
> File name = branch name with "/" replaced by "__" (see `.claude/hooks/handoff_khi_day_ngu_canh.py`).
> Written by the session when context passes ~400k tokens (after finishing its current prompt).

## Feature / goal
Follow-up to A14 (student class). Branch starts from `claude/a14-giao-dien` (fast-forwarded, includes
A14 part A + B). Truong's task file (2026-11-03), explicitly overriding the registry rule (rule 1):
- T1a: static sample `mau_csv/SO_NHAP_CLB.xlsx` has no "Lớp" column (software-generated sample has it).
  Add it and make that file the main sample.
- T1b: an old workspace whose saved config already has two nouns with the same label opens fine, but
  ANY later save (rename workspace, change a rule) is rejected with `nhan_trung_danh_tu` until labels
  are fixed. Fix that. No over-engineering.
- T2: merge sidebar tabs 02 (Kết quả), 06 (Thành viên CLB), 07 (Theo lớp) into TWO tabs:
  "Kết quả" (per-student timetable, members per club, members per class) and "Dữ liệu khác"
  (everything else that was in 02). Kết quả has two tiers (see Plan T2).
- T3 (later loop): UI debloat research, output one .md. T4 (later loop): data-collection ecosystem
  model (flowcharts/architecture images) for Truong to approve BEFORE any implementation.
Algorithm, match_results, run_history, CSV column contract: untouched.

## Plan (written by Opus; ticked by Sonnet)
T1a
- [x] Find how `mau_csv/SO_NHAP_CLB.xlsx` is built (`mau_csv/tao_so_nhap.py`) vs the generated sample
      (A14 adds "Lớp" after "Họ tên"). Give every student a SIMULATED class (fixed seed, plausible
      names like 10A1, 11A2...), regenerate the xlsx, keep everything else byte-for-byte equal in meaning.
- [x] Docs: `mau_csv/HUONG_DAN_SO_NHAP.md` (+ HUONG_DAN_SU_DUNG if it names a sample) say this file is
      THE main sample. Fix tests that pin the old header/hash.
T1b
- [x] `cau_hinh_ws` / `api_workspace`: a save is rejected only when it introduces a duplicate pair
      that the currently STORED config does not already have. Old duplicates pass (keep the existing
      warning path). New duplicates still get `nhan_trung_danh_tu`. Test both directions.
T2
- [x] Sidebar: 01 Vận hành, 02 Kết quả, 03 Dữ liệu khác, then Nhập tại chỗ, Quản lý, Nhập điểm
      (renumber). Remove tabs `members` and `theolop` as separate nav items.
- [x] Kết quả tier 1 (segmented control): Theo lớp | Theo CLB | Theo mã học sinh.
      Tier 2 (sort control): Theo ngày trong tuần | Theo mã học sinh | Theo lớp (the last one ONLY
      when tier 1 = Theo mã học sinh). One picker (class / club) or search box per tier-1 view.
      Remember last tier-1/tier-2 choice per machine (localStorage, try/catch). No scores, no lottery
      numbers in Kết quả (it is for BGH, club heads, homeroom teachers).
- [x] Dữ liệu khác = every remaining 02 section (summary, export, fill stats, coverage, preference
      distribution, unplaced, reserve, cutoffs, lottery numbers, full match list...).
- [x] i18n vi+en, text rules (no em dash, no "em/tôi/tớ" in UI descriptions), language switch re-render.
- [x] Update/replace Chromium UI tests that click the old tabs; new tests for tiers.
T4 (CON-4, design only, no code)
- [x] Design proposal docs/he_sinh_thai/T4_MO_HINH_HE_SINH_THAI.md + 5 diagrams in docs/he_sinh_thai/anh/ (rounds 1, 2, 3b done).
- [ ] Truong reviews and answers open questions (section 14.2 of the doc), then T4-K2 (Apps Script) may start.
Both
- [x] Related tests green, ruff, soat-ma, CHANGELOG, TIEN_DO, push. Opus runs the FULL suite at the end.

## Current state (overwrite each handoff)
- This session (Sonnet, CON-4) wrote the T4 design: docs/he_sinh_thai/T4_MO_HINH_HE_SINH_THAI.md plus anh/*.mmd/.svg/.png
  (a_kien_truc is hand-written SVG built by a script, b1, b2, c, d, e are Mermaid). Pushed through commit ca9e161
  ("T4 sửa vòng 3b"). "CON-4 FIXED round 3" was SENT to Opus session_01VfPzNvdGizkwxJ8cd64rmp. No code or tests touched.
- Network was blocked for the teacher's reference site and all official quota pages: every quota number is tagged
  TT-CXM (unverified, from search summaries) and every Google behaviour claim is GĐ-n (unverified assumption). Doc section 16 lists
  hosts to allow and what to verify.
- CON-1 work (T1a, T1b, T2, fix rounds 1 to 3) was finished earlier and reported (see Session log).
- In progress: nothing. Waiting for Opus review of round 3.

## Decisions and gotchas (keep short)
- T4 design core: Google Forms + one Sheets per cycle; tabs RAW (Forms' own, no script writes), hoc_sinh, clb, phieu (key =
  Forms response ID in LAST column), nhat_ky, cau_hinh, dieu_khien (formulas). Batch reads Forms API, upsert by raw_key,
  cursor moc_xu_ly moved last; 120 s cap checked before each block; rows with empty raw_key/trang_thai deleted at batch start.
- Export is its own menu (not tied to Chốt đợt), CSV parts of 1,000 submissions, manifest.json, one complete export per day
  unless phieu changed (phieu_phien_ban). Implementation conventions M1 to M26 are in doc section 7.7.
- Repo changes: T4-K1 (lop column, fff0f41) and T4-K3 (doc_raw multi-part, 7e64cc4) are DONE; only T4-K2 (Apps Script) remains.
- Doc text rules: Vietnamese, no em dash, no pronouns em/tôi/tớ. Diagram scripts live in the old session scratchpad (not in repo):
  re-render from the .mmd/.svg sources if needed (Mermaid 10.9.1 from npm + Playwright; a_kien_truc.svg is the source of its PNG).
- CON-1 notes: static sample mau_csv/SO_NHAP_CLB.xlsx is a blank template with only the Lớp column added; test_ws_nhan.py snapshot
  tolerates exactly the intended string changes; do not run git stash while background tests run.

## Next steps (ordered)
1. Read Opus messages (cross-session). If another T4 fix plan arrives, patch the doc by section (see 7.x numbering), re-render changed
   diagrams, LOOK at each PNG, commit "T4 sửa vòng N", push, send "CON-4 FIXED round N" with per-item status.
2. When the network is open: do doc section 16 (verify quota numbers and GĐ-n, then replace TT-CXM and GĐ tags with VERIFIED + URL).
3. Do not start T4-K2 coding until Truong approves the open questions (doc section 14.2).

## Files touched
- T4: docs/he_sinh_thai/T4_MO_HINH_HE_SINH_THAI.md, docs/he_sinh_thai/anh/ (a_kien_truc.svg/.png, b1_nop_phieu, b2_xu_ly_lo, c_duyet_xuat,
  d_erd, e_chuyen_doi as .mmd/.png), this file.
- CON-1 rounds: tests/du_lieu_ws/so_nhap_truoc_khi_co_cfg.json, tests/test_ws_so_nhap.py, CHANGELOG.md; earlier see CHANGELOG
  sections "T1a, T1b", "T2", "T2 sửa vòng 1/2".

## Session log (append only, newest last)
| Date | Model | What was done | Notes |
|---|---|---|---|
| 2026-11-03 | Opus | ff to a14-giao-dien, wrote plan for T1/T2 | coordinator session |
| 2026-11-03 | Sonnet | T1a, T1b, T2 implemented, tests green, pushed | static sample is a blank template (only Lớp column added); day sort = earliest session with a club |
| 2026-11-03 | Sonnet | Fix round 1 (F1-F8) from Opus plan | see CHANGELOG "T1/T2 sửa vòng 1" |
| 2026-11-03 | Sonnet | Fix round 2 (G1-G3) from Opus plan | see CHANGELOG "T2 sửa vòng 2" |
| 2026-11-03 | Sonnet | Fix round 3 (snapshot of Sổ guide text) | only Hướng dẫn A1,A16,A18,A23,A33 differed |
| 2026-11-03 | Sonnet | Handoff at context limit, round 3 committed | tests still pending, report to Opus not sent |
| 2026-11-03 | Sonnet | Final handoff: rounds 1-3 done and reported | nothing pending on this side |
| 2026-11-04 | Sonnet | CON-4: T4 design doc and 5 diagrams, rounds 1, 2, 3b pushed (ca9e161); handoff at context limit | design only; quotas unverified (network blocked); waiting for Opus review |
