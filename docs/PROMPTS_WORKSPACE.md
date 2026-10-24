# Prompts for a cheaper model: multi-industry workspaces

Run the prompts **in order, one per session**. Paste the SHARED CONTEXT block first, then one TASK block.
Do not start a task until the previous one is pushed and its tests are green.

---

## SHARED CONTEXT (paste at the top of every prompt)

```
You are working in the repo rbda-kiosk (folder RB-STUFF-AFTER-UP). It is a Windows desktop app:
Python + pywebview + plain-script JS (no ES modules) + SQLite. It sorts school students into clubs
with the RB-DA algorithm (student-proposing deferred acceptance with soft reserves and a lottery
tie-break called STB).

Key files:
- main.py: entry point. resolve_db_path() at ~line 45. APP_TITLE at ~line 21.
- api.py: class PipelineAPI(db_path) at ~line 78. It is built from mixins in api_nhap.py (import),
  api_quan_ly.py (admin), api_xuat.py (export), api_bao_cao.py (results), api_cham_diem.py (scoring)
  and api_chung.py (helpers). _backup_db() is at ~line 698.
- rbda_priority_pipeline.py: the algorithm and the DB schema.
  - DEFAULT_SCHEMA is at ~line 1250. init_db() and connect_db() are in the same file.
  - TRAN_NGUYEN_VONG_MOI_BUOI = 10 (max choices per session) and TRAN_CLB_THI_MOI_BUOI = 5
    (max tested clubs per session) are at ~lines 91 and 96.
  - compute_club_priority() is at ~line 123.
- so_nhap.py: the import workbook "Sổ nhập CLB".
  - Sheet names are at lines 39-41 and column names at 50-58.
  - The header synonym tables _TEN_COT_CLB / _TEN_COT_HS are at ~196-210.
  - Readers: doc_so_nhap() and _tim_sheet(). Writer: ghi_so_nhap().
- i18n.js / i18n_errors.py / i18n_loi.js: vi/en text catalogs. tao_i18n_js.py generates parts of them,
  and tests/test_i18n_sync.py keeps them in sync.
- index.html: sidebar and 5 tabs. js/00_nen.js … js/08_khoi_dong.js are loaded in the order listed in
  js/_danh_sach.txt. chung.js holds callApi().
- tests/: pytest, about 100 files. Run with: python -m pytest -q

THE GOAL OF THE WHOLE PROJECT (you do ONE part of it, described in TASK below):
Turn the app into a multi-WORKSPACE app.
- Each workspace is a folder workspaces/<slug>/ containing its own app.db.
- Each workspace has its own vocabulary: 5 nouns, each with a vi label and an en label.
- Each workspace has its own rules. They are stored INSIDE its app.db, in a table
  workspace_settings(key TEXT PRIMARY KEY, value TEXT), as JSON under key 'config':
  {"name": "...", "industry": "school|company|event|custom",
   "labels": {"person":  {"vi":"Học sinh","en":"Student"},
              "slot":    {"vi":"Câu lạc bộ","en":"Club"},
              "session": {"vi":"Buổi","en":"Session"},
              "group":   {"vi":"Nhóm ưu tiên","en":"Priority group"},
              "score":   {"vi":"Điểm","en":"Score"}},
   "rules": {"max_choices": 10, "max_tests": 5,
             "priority": "score",            // "score" | "tier" | "score+tier"
             "tier_mode": "reserve",         // "reserve" (today's soft reserves) | "strict"
             "score_scope": "per_slot",      // "per_slot" (today) | "per_person" (one score for every slot)
             "tiers": []}}                   // ordered list of group names, best first (strict mode)
- The values above are the SCHOOL DEFAULTS. A missing row or a missing key means the school default.
  So old databases and every existing test must behave EXACTLY as they do today.
- One operator on one PC. No login, no server. Several slots per person happen only through
  sessions; never change the one-slot-per-person-per-session rule.

HARD RULES:
1. Do not change algorithm behaviour unless your TASK says so. compute_club_priority must never
   receive preference ranks (see its docstring).
2. Every existing test must still pass. Add new tests for what you build, under tests/test_ws_*.py.
3. Match the code style around you: Vietnamese identifiers and comments are normal here, so follow
   the file you are editing. Add or update matching i18n keys in BOTH vi and en for all user-visible
   text.
4. Keep the change to your TASK. Do not refactor unrelated code.
5. Before committing, run: python -m pytest -q. If a test fails, fix it. Never skip, delete or
   weaken a test.
6. Commit with a clear message and push: git push -u origin claude/cool-hamilton-5zpbc8
7. At the end, report: the files changed, the new tests, the pytest summary line, and anything left
   undone.
```

---

## TASK 1: Settings table and config module

```
TASK 1: workspace config storage. There are NO UI changes in this task.
1. In rbda_priority_pipeline.py, add to DEFAULT_SCHEMA:
   CREATE TABLE IF NOT EXISTS workspace_settings(key TEXT PRIMARY KEY, value TEXT)
   init_db() must create it in old databases too. Check how other tables were added (look for
   IF NOT EXISTS and migration helpers) and follow that pattern.
2. Create a new module cau_hinh_ws.py with:
   - MAC_DINH_TRUONG_HOC: the school-default dict from SHARED CONTEXT. Take max_choices and max_tests
     from TRAN_NGUYEN_VONG_MOI_BUOI and TRAN_CLB_THI_MOI_BUOI; do not hardcode them a second time.
   - doc_cau_hinh(db_path) -> dict: reads the 'config' row and deep-merges it over the defaults.
     A missing row or broken JSON returns the defaults; do not crash.
   - ghi_cau_hinh(db_path, cfg): validates, then writes. Validation:
     - max_choices is an int in 1..20.
     - max_tests is an int in 0..20, or None (meaning no limit).
     - priority, tier_mode and score_scope must be one of the allowed values.
     - every label has a non-empty vi; an empty en falls back to vi.
     On bad input raise ValueError with a clear message.
   - nhan(cfg, noun, lang) -> str: returns the label, falling back to vi.
3. Tests in tests/test_ws_cau_hinh.py:
   - defaults on a fresh DB;
   - defaults on an old DB that has no table yet;
   - a round trip through ghi then doc;
   - a partial config merges with the defaults;
   - broken JSON gives the defaults;
   - each validation error;
   - the en -> vi fallback.
```

## TASK 2: Workspace registry, migration and main.py

```
TASK 2: the workspace folders on disk. Depends on TASK 1 (cau_hinh_ws.py exists).
1. Create a new module workspace.py. All functions take a root directory argument; nothing global.
   - danh_sach(root) -> list of {slug, name, industry, path, modified}. It scans root/workspaces/*/app.db
     and ignores _trash.
   - tao(root, name, cfg) -> slug.
     - Slug = name with diacritics removed (reuse so_nhap.bo_dau), lowercase, '-' between words.
     - If the slug exists, add -2, -3, ...
     - Call init_db, then ghi_cau_hinh.
   - doi_ten(root, slug, new_name): changes only config.name; the folder keeps its slug.
   - xoa(root, slug): first copy app.db to a timestamped backup inside the folder, then move the
     whole folder to root/workspaces/_trash/<slug>-<timestamp>. Never delete files permanently.
   - nhan_ban(root, slug, new_name, kem_du_lieu: bool):
     - kem_du_lieu=True: copy the DB using the sqlite backup API (copy the style of
       PipelineAPI._backup_db).
     - kem_du_lieu=False: create a new DB with the same config.
   - luu_mau(root, slug, ten_mau): writes the config only (no data) to root/templates/<slug>.json.
     danh_sach_mau(root) lists the templates, and always includes a built-in "Trường học" entry
     made from MAC_DINH_TRUONG_HOC.
   - xuat_zip(root, slug, dest_path) and nhap_zip(root, zip_path) -> slug.
     - nhap_zip must reject zip entries with absolute paths or '..' (zip-slip).
     - nhap_zip must check that the zip contains app.db.
     - If the imported slug already exists, rename it like tao() does.
   - di_chuyen_db_cu(root): if root/app.db exists AND root/workspaces/ does not:
     - move root/app.db to root/workspaces/truong-hoc/app.db (also move app.db.bak-* files);
     - write a config with name "Trường học";
     - leave root/DA_CHUYEN_SANG_WORKSPACES.txt explaining the move (vi, one short paragraph).
     It must be safe to run twice.
2. main.py:
   - If argv gives a DB path, keep today's behaviour exactly (single DB, no workspaces).
   - Otherwise, root = the folder of the exe/script (see how resolve_db_path finds it). Call
     di_chuyen_db_cu(root). The UI will open a workspace later (TASK 3).
   - For now, if exactly one workspace exists, open it so the app keeps working before TASK 3.
     If none exists, create "Trường học" with the defaults and open it.
3. Tests in tests/test_ws_registry.py, using tmp_path:
   - each function's happy path;
   - slug collisions;
   - delete goes to trash and the backup exists;
   - duplicating with data vs without data;
   - zip round trip;
   - zip-slip is rejected;
   - migration runs once, is idempotent, and keeps the data rows (insert a club before migrating,
     then check it is still there).
```

## TASK 3: API, workspace picker, switcher and setup wizard

```
TASK 3: let the user hop between workspaces in the UI. Depends on TASKS 1-2.
1. PipelineAPI (api.py) gets an optional workspace root (pass it in from main.py) and these methods.
   Each returns the same {ok, ...} / error shape the other API methods use (copy that pattern):
   list_workspaces, list_templates, open_workspace(slug), create_workspace(name, cfg),
   rename_workspace, delete_workspace (require the confirmation text "XOA", like reset_data in
   api_quan_ly.py), duplicate_workspace, save_as_template, export_workspace (into the export folder),
   import_workspace(base64_zip), get_workspace_config, update_workspace_config.
   - open_workspace changes self.db_path, runs init_db, clears any cached data (search api.py for
     caches tied to db_path), and returns the config.
   - When the app was started with a DB path in argv, every workspace method returns an error
     saying workspaces are disabled in that mode.
2. Frontend (plain scripts, no modules; add the new files to js/_danh_sach.txt in the right order):
   - js/075_workspace.js:
     - A picker screen. Show it at startup when the backend has a workspace root and no workspace
       is open yet. It lists the workspaces (name, industry, last modified) with buttons
       Open / Rename / Duplicate / Export / Delete, plus "New" and "Import .zip".
     - Delete uses the existing two-step confirm button in chung.js.
   - A switcher in the sidebar header in index.html: it shows the current workspace name, and
     clicking it opens the picker. Switching reloads the data of every tab (find how
     08_khoi_dong.js boots the tabs and reuse that).
   - Setup wizard, 4 steps:
     (1) name + industry + start from template;
     (2) the 5 nouns with vi and en inputs; en may be blank;
     (3) rules: max_choices, max_tests (with a "no limit" checkbox), priority, tier_mode,
         score_scope, and the tiers list (edited only when tier_mode=strict);
     (4) review, then Create.
     Choosing a template pre-fills every step.
   - Style it with the existing tokens in style.css. Every text goes through i18n with vi and en.
3. Tests:
   - API tests in tests/test_ws_api.py.
   - One UI test that copies the style of the existing tests/test_giao_dien_*.py (they use
     tests/_trinh_duyet.py): create a workspace, switch to it, switch back, and check the header
     name changes.
```

## TASK 4: Vocabulary everywhere

```
TASK 4: show the workspace's words in place of the school words. Depends on TASKS 1-3.
1. i18n.js: find every vi/en string that names a domain noun:
   student / học sinh, club / CLB / câu lạc bộ, session / buổi, priority group / nhóm ưu tiên,
   score / điểm.
   - Replace the noun with a placeholder: {person}, {slot}, {session}, {group}, {score}.
   - The t() helper fills these from the open workspace's labels for the current language.
     Labels are loaded with get_workspace_config at boot and on every switch.
   - Add lowercase variants {person_l}, {slot_l}, ... for mid-sentence use.
   - Be careful with Vietnamese grammar. Rewrite a sentence if a plain swap reads badly.
2. Do the same for the Python texts the user sees: i18n_errors.py, and the sheet titles and column
   headers in api_xuat.py and so_excel.py. Pass the labels in; do not read global state.
3. The window title becomes "<slot label> — <workspace name>". Update it on switch if pywebview
   allows it; if not, at least set it on start.
4. Update tao_i18n_js.py and tests/test_i18n_sync.py if they need it. With the school defaults,
   every rendered string must stay IDENTICAL to today's. Write a test that checks this for a sample
   of 20 strings.
5. Tests:
   - A company workspace (Nhân viên/Employee, Nhóm dự án/Project team) makes the UI show those
     words and the Excel export headers use them.
   - en falls back to vi when blank.
```

## TASK 5: Per-workspace import template and configurable limits

```
TASK 5: Depends on TASKS 1-4.
1. so_nhap.py:
   - ghi_so_nhap(..., cfg=None). With cfg:
     - sheet names are "1. <slot vi>" and "2. <person vi>";
     - the NV columns go up to rules.max_choices;
     - per_slot: "<score vi> n" columns as today;
     - per_person: a single "<score vi>" column after the group column;
     - the group column header = the group label.
     cfg=None must produce exactly today's file.
   - doc_so_nhap(..., cfg=None): extend _tim_sheet and the _TEN_COT_* synonym lookups at run time
     with the workspace labels (compare with bo_dau, like the existing code). Old school headers
     MUST still be accepted. In per_person mode, read the single score column.
   - Keep so_nhap.py runnable on its own: it must not import cau_hinh_ws. Pass cfg as a plain dict.
2. Replace the uses of the constants TRAN_NGUYEN_VONG_MOI_BUOI / TRAN_CLB_THI_MOI_BUOI with
   cfg["rules"]["max_choices"] / ["max_tests"] (None = no limit) in:
   api_nhap.py (~1170, ~1330), api_quan_ly.py (~415, ~467), api.py (~388-401), and the check at
   rbda_priority_pipeline.py ~1046 (pass the limit in as a parameter that defaults to the constant).
   Keep the constants as the defaults.
3. The "download template" action in the UI uses the open workspace's cfg.
4. Tests:
   - A company workspace generates a template, then reads it back.
   - An old school workbook imports into a custom-label workspace.
   - max_choices=3 rejects a 4th choice.
   - max_tests=None accepts 12 tested slots.
   - The school defaults give byte-identical behaviour to before (reuse tests/_so_nhap_mau.py).
```

## TASK 6 (Phase 2): Rule options in the engine

```
TASK 6: Depends on TASKS 1-5.
1. score_scope = per_person:
   - Store one score per person. Use the club_scores table with a reserved club_id "__ca_nhan__",
     or a new column. Choose the option that changes less code, and explain why in the commit
     message.
   - When the data is loaded for a run (load_from_sqlite / the run_pipeline path), expand it into
     club_scores rows for every slot the person applied to. The engine itself stays unchanged.
2. tier_mode = strict:
   - compute_club_priority gets an optional tier_rank: dict[student_id, int] = None. A lower rank
     means higher priority; people not in the tiers list go last.
   - The sort key becomes (tier_rank, tested-first, -score, stb).
   - tier_rank comes from rules.tiers and the person's group (students.reserve_group).
   - In strict mode, do not apply the soft-reserve pass, because the tiers already give the
     priority. Thread a flag through run_rbda / run_rbda_nhieu_buoi with a default that keeps
     today's behaviour.
   - NEVER pass preference ranks into compute_club_priority.
3. priority = tier only: everyone counts as untested. Order = tier, then STB.
4. Scoring tab (js/06_cham_diem.js):
   - hide it when priority = "tier";
   - in per_person mode, show one score input per person, not one per (person, slot).
5. Data-health warnings (find the existing health report in api.py):
   - warn when strict tier is on and some people have no tier;
   - warn when per_person is on and some people have no score.
6. Tests:
   - strict tier ordering;
   - per-person expansion;
   - tier-only mode;
   - verify_stability(...) passes for random data in each mode (copy the style of the existing
     stability tests);
   - the school defaults give identical results to before on du_lieu_test data with a fixed seed.
```

---

# AFTER THE 6 TASKS: from "code done" to "shipped to real users"

## Context
When Tasks 1-6 are done, the code works in tests, but four things are still missing:
- **Nobody has checked the whole thing end to end.** Each task was tested alone, and cheap models can leave gaps where the tasks join.
- **The helper skills only speak "school".** These are sinh-du-lieu-clb, xu-li-raw-forms and tao-google-form-clb.
- **The docs describe the old single-database app.**
- **Existing schools will get an upgrade that moves their data.** That must be rehearsed on real data before it reaches them.

Truong's goal: **ship a new .exe to real users**. There is no non-school pilot yet, so company and event usage is **simulated** with generated data.

## Order of work
| # | Task | Model | Why this order |
|---|---|---|---|
| 7 | Integration audit and hardening | Opus (strong) | Find the gaps between the tasks before building more on top |
| 8 | Workspace-aware sample data generator (skill) and simulated pilot datasets | Sonnet | Needed before anyone can test company and event workspaces |
| 9 | Workspace-aware raw Forms processor (skill) | Sonnet | Depends on 8's config handling |
| 10 | Workspace-aware Google Form generator (skill) | Sonnet | Produces the raw files that 9 consumes |
| 11 | Simulated pilot run and UX fixes | Sonnet + you | Use the app like a company or event operator |
| 12 | Docs update | Sonnet | Write the docs once the behaviour is final |
| 13 | Release: upgrade rehearsal, build, rollout, rollback | You + Sonnet | Last step |

Every prompt below starts with the same SHARED CONTEXT block as Tasks 1-6, followed by this extra line:
`Tasks 1-6 (workspaces, config, vocabulary, per-workspace import, rule options) are DONE. Read docs/PROMPTS_WORKSPACE.md for what they built.`

---

## TASK 7: Integration audit and hardening (use a strong model)
```
TASK 7: audit the whole multi-workspace feature end to end, then fix what you find.
1. Read the full diff since commit 0e4d774: git diff 0e4d774 --stat, then the files themselves.
2. Check these joins between the tasks and fix any you find broken:
   - After you switch workspace, NO tab still shows data, labels or rules from the previous one.
     Check every tab: run, results, manual entry, admin, scoring.
   - Backups (_backup_db), exports and match_results.csv are written inside the OPEN workspace's
     folder, never in the root and never in another workspace.
   - The recovery screen (recovery.py / recovery.html) works when ONE workspace's app.db is corrupt:
     it recovers that workspace only, and the picker still lists the others.
   - The browser fallback (browser_host.py) exposes the new API methods too.
   - kiosk.spec packages every new .py and .js file (tests/test_dong_goi_du_tep.py only checks
     files loaded by the HTML pages; check the Python modules by hand), and the
     build-windows-exe.yml drift check still passes.
   - Starting with a DB path in argv still behaves exactly as before.
3. Security pass on workspace import/export:
   - zip-slip, zip bombs (cap the uncompressed size, e.g. 500 MB), symlinks in the zip;
   - a slug containing ../ or Windows-reserved names (CON, NUL...);
   - a malicious workspace_settings JSON (huge strings, wrong types) must fall back to safe values.
4. Add an end-to-end test file, tests/test_ws_e2e.py, that runs this sequence:
   a. Migrate a copy of du_lieu_test/app_DEMO_da_cham_diem.db.
   b. Create a company workspace (per_person KPI, strict tiers) and an event workspace (tier-only,
      3 sessions).
   c. Import a generated template into each one, run the pipeline in each, switch between them, and
      check the results never mix.
   d. Check verify_stability passes in all three workspaces.
5. Report every issue: fixed or not, and why.
```

## TASK 8: Workspace-aware sample data generator (skill) and simulated pilot data
```
TASK 8: generalise the skill .claude/skills/sinh-du-lieu-clb/ (SKILL.md + scripts/sinh_du_lieu.py).
1. Read SKILL.md and the script fully first.
2. The script gets an optional --cau-hinh <config.json> argument (same JSON shape as
   workspace_settings 'config'). Without it, the output must stay byte-identical to today's (school).
   With it:
   - use the workspace labels in the sheet and column names (match so_nhap.ghi_so_nhap(cfg=...));
   - respect max_choices and max_tests (None = no limit);
   - per_person: one score per person; per_slot: a score per tested slot;
   - tiers: assign each person a group from rules.tiers with realistic proportions
     (e.g. 10% / 30% / 60%);
   - add --kich-ban company|event presets that pick realistic sizes and names:
     company = 300 employees, 12 project teams, 1 session, KPI 0-100 per person,
               tiers Senior > Mid > Junior, strict;
     event   = 800 attendees, 24 workshops over 3 sessions, tier-only (VIP > Member > Guest),
               no scores.
     Use Vietnamese names and team/workshop names; reuse the name lists already in the script.
3. Generate and commit the simulated pilot data:
   du_lieu_test/bo_cong_ty/ and du_lieu_test/bo_su_kien/, each with config.json, SO_NHAP.xlsx and a
   README.md. The README gives one paragraph on what the data simulates and how to load it.
4. Update SKILL.md: when to pass --cau-hinh, with the two presets as examples. Keep its existing
   Vietnamese style. Update the description's trigger phrases to include "dữ liệu công ty",
   "dữ liệu sự kiện" and "workspace".
5. Tests: if a test for this skill exists (tests/test_dong_goi_skill.py, test_bo_sinh_du_lieu_tai_lap.py),
   extend it:
   - same seed gives the same output;
   - every generated workbook imports with zero errors into a workspace that has the matching config.
```

## TASK 9: Workspace-aware raw Forms processor (skill)
```
TASK 9: generalise .claude/skills/xu-li-raw-forms/ (SKILL.md + scripts/xu_li_raw.py).
1. Read both files fully. The script turns RAW_PHIEU.xlsx + DAP_AN.xlsx (from Google Forms) into
   SO_NHAP_CLB.xlsx.
2. Add an optional --cau-hinh <config.json> argument. Without it, the behaviour must stay
   unchanged. With it:
   - write the output workbook with the workspace labels and limits (reuse so_nhap.ghi_so_nhap with
     cfg; do not duplicate its logic);
   - per_person: if the form has one quiz/score for everyone, output one score column;
   - tier-only workspaces: skip grading entirely and read the group/tier from a form question whose
     title matches the group label;
   - the anomaly checks (duplicate submissions, malformed IDs, ticked-but-no-test...) stay, with
     messages that use the workspace nouns.
   Replace the hardcoded TRAN_THI = sdl.TRAN_CLB_THI_MOI_BUOI with rules.max_tests.
3. Update SKILL.md the same way as TASK 8.
4. Tests: build a small fake RAW_PHIEU for the company preset and one for the event preset, run
   the script, and import the result into a matching workspace with zero errors.
```

## TASK 10: Workspace-aware Google Form generator (skill)
```
TASK 10: generalise .claude/skills/tao-google-form-clb/ (SKILL.md + scripts/tao_form.py).
1. Read both files fully. The script produces a Google Apps Script (.gs) file that builds the
   registration + exam form.
2. Add --cau-hinh <config.json>. Without it, the .gs output must be byte-identical to today's.
   With it:
   - all form titles, questions and help texts use the workspace nouns (vi);
   - the ranking dropdowns go Top 1..max_choices;
   - "tick up to N to be tested" uses max_tests, and the step disappears when priority is tier-only;
   - per_person score: one shared quiz section in place of one exam per slot;
   - tier: add a required dropdown question "<group label>" whose choices are rules.tiers;
   - the export function must produce raw files that TASK 9's script accepts (keep the column
     names in sync; add a comment pointing to xu_li_raw.py).
3. Update SKILL.md, including the step-by-step guide for non-school operators
   (HR staff, event organisers).
4. Tests: generate the .gs file for school, company and event. Check it is syntactically plausible
   (balanced braces; node --check if node is available). Snapshot the key question titles.
```

## TASK 11: Simulated pilot run and UX fixes (you + Sonnet)
```
TASK 11: act as two NEW users who have never seen the app, and fix what confuses them.
Persona A, HR officer: "Assign 300 employees to 12 project teams by KPI, seniors first."
Persona B, event organiser: "Seat 800 attendees into 24 workshops over 3 time slots, VIPs first."
For each persona, using du_lieu_test/bo_cong_ty and bo_su_kien:
1. Run the app through the browser fallback (python main.py, then drive it with Playwright from
   /opt/pw-browsers). Do the full journey: create the workspace with the wizard, download the
   template, import the data, run, read the results, export to Excel.
2. Screenshot every screen. Write UX_PILOT_NOTES.md listing every point where:
   - a school word still appears;
   - a label reads badly in Vietnamese;
   - a step is unclear;
   - an error message does not say how to fix it;
   - a result table makes no sense for that industry (e.g. a "tested" column in a tier-only
     workspace).
3. Fix the small items (wording, hidden irrelevant columns, missing labels). List the big items
   without fixing them. Add a UI test for each fixed item where practical.
```
Your part: open the app yourself, do Persona A's journey, and add your own notes to UX_PILOT_NOTES.md before starting the Sonnet session.

## TASK 12: Docs update
```
TASK 12: update the documentation to describe workspaces.
1. Files: README.md (structure section: workspace.py, cau_hinh_ws.py, the workspaces/ layout),
   HUONG_DAN_SU_DUNG.md (a new section: "Không gian làm việc" covering picker, wizard,
   switch, duplicate, export/import, delete/restore from _trash), HUONG_DAN_CAI_DAT.md (the
   upgrade and migration note), BAN_GIAO.md, TAI_LIEU_DU_LIEU.md (the workspace_settings table
   and config JSON), mau_csv/HUONG_DAN_SO_NHAP.md (per-workspace templates).
2. Every .md that has a matching .html must get the same changes in the .html (written by hand).
   tests/test_tai_lieu_dong_bo.py checks key numbers match between the pair.
3. Add a short UPGRADE_NOTES.md (vi), written for school operators:
   - what changes when they open the new version (their data moves to workspaces/truong-hoc/, a
     note file is left behind);
   - nothing is lost;
   - how to roll back.
4. Keep the existing tone and language of each file.
```

## TASK 13: Release (you + Sonnet)
1. **Upgrade rehearsal.**
   - Collect copies of 2-3 real school `app.db` files (anonymise them if needed).
   - For each one: run the new exe on a copy, and confirm the migration, the result tab and the
     re-run results match what the old version shows. Use the same seed / stb_lock.
   - Ask Sonnet to write `tests/test_ws_nang_cap.py`, which does this automatically for
     `du_lieu_test/app_DEMO_da_cham_diem.db`.
2. **Build.**
   - Merge the branch through a PR.
   - Run `build-windows-exe.yml` (do not skip tests), then download the zip.
   - Smoke-test it on a clean Windows PC: first launch, migration, create a company workspace,
     switch, export.
3. **Rollback plan, written before shipping.**
   - Keep the old exe.
   - To roll back, run the old exe with `workspaces\truong-hoc\app.db` as its argument. It is still a
     normal database; the old version ignores the new `workspace_settings` table, so verify that
     once during the rehearsal.
4. **Rollout.**
   - Ship to one school first and wait one full allocation cycle before sending it to the others.
   - Send UPGRADE_NOTES.md with it.
5. **Feedback loop.**
   - Collect issues into one list, and triage them weekly.
   - When a real company or event organiser appears, rerun TASK 11 with their real (anonymised)
     data before they use it live.

## Later (not planned yet, revisit after real feedback)
- First-come priority (submission time). It was left out on purpose; add it only if a real event
  user needs it.
- True N-slots-per-person matching. Only if sessions prove too clumsy in practice.
- Sharing workspaces across PCs. Only if a second operator appears.

## Done means
- All tests are green, including test_ws_e2e and test_ws_nang_cap.
- The pilot notes have no open "small" items.
- Each md/html pair is in sync.
- The exe has been smoke-tested on clean Windows.
- One school ran a full cycle on the new version with no data loss.
