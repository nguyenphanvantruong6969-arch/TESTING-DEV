# Brief for a Fable session: whole-kiosk UI and small-bug audit (four personas)

> Written 2026-11-13 by Opus for Truong. English on purpose; **reply to Truong in Vietnamese**.
> Read `CLAUDE.md`, then `docs/fable/01_PROJECT_CONTEXT.md` (skim), then this file. You do NOT need `02_FABLE_BRIEF.md`.
> Model for this job: the earlier report "Thử nghiệm forms-gop" (claude.ai artifact, 2026-11-12): a novice walkthrough
> plus a senior-dev review, with screenshots and a severity ledger. Do the same, but for **the whole program**.

## 1. Goal (one sentence)
Find everything that makes the kiosk confusing, ugly, inconsistent, slow to understand or quietly wrong for its real
users, from big blockers down to small polish, and hand Truong ONE visual report ranked by harm to real users.

## 2. Ground rules (non-negotiable)
- **Read-only on production code.** You run the app, read code and docs, and write your own scripts in a scratch folder.
  You never edit `*.py`, `*.js`, `*.html`, `*.css`, `i18n*` or tests. No commits to production files, no PR.
- Never write into the repo's own workspaces or `app.db`: every walkthrough uses a fresh temporary data folder.
- All data is SIMULATED. Label the report "SỐ LIỆU MÔ PHỎNG". Nothing is tried on real Microsoft Forms ("TH").
- No subagents (`CLAUDE.md` rule 10). Do not write commentary or conclusions for Truong's science report.
- Every finding needs evidence: a screenshot or a quoted string, exact repro steps, and where it lives in code
  (`file` + function name, never line numbers). No evidence → leave it out.

## 3. What to test
- **Code:** `origin/main` (contains PR #16: forms-gop + IT-UI "Chuẩn bị đợt"). Check out a clean worktree of it.
- **Already being fixed:** branch `origin/claude/fg-sua` (items FG-1…FG-9, spec `docs/ke_hoach/FORMS_GOP_SUA_KE_HOACH.md`)
  fixes most of the 18 findings of the earlier report. For every finding, check that branch too and tag it
  `FIXED ON fg-sua (FG-n)`, `PARTLY FIXED` or `NEW`. Put fixed ones in a short appendix, not in the main ledger.
- **Scope: EVERYTHING the user can see.** Every tab in the sidebar (Chuẩn bị đợt, Nhập nguyện vọng, Nhập điểm, Xếp,
  Kết quả, Chi tiết và xuất tệp, Quản lý), every dialog, menu, wizard step, toast, empty state, error state and
  exported file a person reads (.xlsx, .docx, .md guides, result notices).
- **Conditions to vary:** Vietnamese AND English UI; window sizes 1366×768 (typical school PC), 1280×800, 1920×1080;
  OS dark mode on (the app has no dark theme today: say whether that hurts); empty workspace, small data (120 students), large data (800 students),
  data with deliberate errors (`du_lieu_test/SO_NHAP_*_CO_LOI*.xlsx`), a one-day school and a multi-day school, FA mode on/off.
- **How to run:** browser mode (`browser_host.py`, see README, section on the fallback browser host) with the
  pre-installed Chromium + Playwright; the `tests/test_giao_dien_*` files show how to start and drive it headless.
  Screenshots for the report at `deviceScaleFactor: 2`.

## 4. Four personas (do all four, in this order)
1. **New IT admin, never saw the program.** Install/open → create workspace → download the sample workbook →
   load data → fix import errors → run → read results → publish → export → load the "after results" Forms file
   → handle an appeal. Speak your thoughts as quotes ("Where is the file?"). Note every point where you would
   have to phone someone. Count clicks for the main path.
2. **Club teacher.** Read the generated "Phiếu thiết lập CLB" (.docx + setup guide from `tao_mau_forms.py`) as the
   teacher who fills it: is every question clear, are the Có/Không branches obvious? Then build a simulated Forms
   export for 5 clubs and load it in "Chuẩn bị đợt" step 1. Check that what the teacher typed shows up where a teacher
   would expect it (club list, results, roster, notices).
   **Seed finding to verify and expand:** the form asks "Giờ" and "Địa điểm" (room), but the reader
   `mau_forms_thi_clb/chuyen_phieu_clb.py` declares `C_GIO`, `C_DIA_DIEM` and never uses them, so time and room are
   dropped on import. Confirm, list every place a room/time should appear (result list, student notice, teacher
   roster, export), and say what a fix touches (the `clubs` table → schema change → needs Truong's approval, rule 7).
3. **Student (15 years old).** Read every student-facing text: registration form(s) incl. the medal questions, the
   quiz pages, the result notice / email merge, the "after results" form and appeal branch. Flag jargon, internal
   codes (`[student_id]`, `(thu_2)`, FA-M6b, GAP-n, TH), wrong titles, unclear instructions, anything a student could
   misread in a way that changes their result.
4. **Senior dev reviewer.** Read the UI code (`index.html`, `js/*.js`, `style.css`, `i18n.js`) and the API layer
   behind each button. Look for: silent data loss (like the dropped room/time), buttons without busy state or
   `.catch`, duplicated handlers, implicit state, strings not in `i18n.js` or missing in one language, hard-coded
   Vietnamese in JS, inconsistent wording for the same thing, layout that breaks at 1366×768, keyboard/focus traps,
   colour contrast below WCAG AA, very long functions that swallow errors (`except Exception`).

## 5. What counts as a finding (severity)
| Severity | Meaning | Example |
|---|---|---|
| Critical | A real user cannot finish a main task, or a student can be placed or informed wrongly | feature unreachable; data silently dropped |
| High | Finishes only with outside help, or data can become dirty without warning | double import; case-sensitive ID |
| Medium | Confusing, inconsistent or misleading, but recoverable | numbers that disagree; wall-of-text errors |
| Low | Polish: alignment, spacing, wording, icons, ordering | checkbox 500 px from its label |
Rank inside each severity by how many users hit it. Group repeats of one root cause into ONE finding.

## 6. Deliverable: ONE visual report artifact (Vietnamese, plain language)
Publish it as a private claude.ai artifact (same style as "Thử nghiệm forms-gop") and give Truong the link. Sections:
1. **Kết luận nhanh**: 3 cards (main path OK or not, newest features reachable or not, finding counts by severity).
2. **One journey per persona**: numbered steps, green/amber/red dot, quotes, screenshot per key step.
3. **Ledger of findings**, most severe first: title, what happens, evidence, repro steps, code location, status tag.
4. **Design-system view of the whole UI**: one table of inconsistencies (buttons, headings, colours, spacing, wording
   of the same action across tabs) with a proposed single rule for each.
5. **What is already good** (short, honest).
6. **Fix order**: top 10 fixes, each with "why first", rough size (S/M/L), whether it touches schema / CSV contract /
   invariants, and a suggested registry item code or "new item". Fable does not implement them.
7. **Appendix**: findings already fixed on `fg-sua`; how to reproduce each walkthrough (data used, window size, language).
Keep the page under 16 MB (compress screenshots to JPEG).

## 7. Working order and stopping
1. Persona 1 on 120-student data, Vietnamese, 1366×768 → then repeat the main path in English and at 1920×1080.
2. Personas 2, 3, 4.
3. The condition sweep (sizes, themes, data sets) on every tab.
4. Write and publish the artifact. Then reply to Truong in Vietnamese: the link, the counts, the top 3 findings,
   and any question that only Truong can answer (e.g. approving a schema change for room/time).
Stop and ask Truong before: anything that would need a production-code edit to continue, or if `origin/main`
does not start at all.
