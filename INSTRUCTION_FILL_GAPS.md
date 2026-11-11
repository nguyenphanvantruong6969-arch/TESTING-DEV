# INSTRUCTION — FILL ALL FA-DAA VISION GAPS (father / son sessions) — v2, 2026-11-10

> **Simplest start:** see `START_HERE.md` (two short prompts, Claude routes itself). The prompts below still work.

> **Order:** run this only **AFTER** `LATEST_INSTRUCTION.md` (7 small fixes) is finished (its report exists in
> `docs/phien/bao_cao_dem/*_sua_nho.md`). PR #14 may still be open; this job works on its own branch.
> **Goal:** bring every row of the vision priority table (`docs/ke_hoach/FA_DAA_VISION.md` §14), plus §11 (admin
> dashboard), §8.8 (improvement cycles) and §13.12 (compensation test), to **100 % of what code can do**.
> Anything that needs a decision only Truong can take is prepared up to the decision point and marked **WAIT-TRUONG**.
> **Coverage before this job (2026-11-10):** overall ~70 %; P1 ~85 %, P2 ~80 %, P3 ~43 %; §11 0 %; §8.8 0 %.

---

## PHẦN 1 — Cho người chạy (tiếng Việt, đọc hết, 3 phút)

### 1.1. Hai loại phiên
| | Phiên CHA | Phiên CON |
|---|---|---|
| Model | **Opus** | **Sonnet** |
| Việc | Viết spec, giao việc, soát, quyết GO / cần sửa, viết báo cáo cuối | Làm đúng MỘT đợt (2–3 mục), test trước, commit, đẩy |
| Có viết mã tính năng không | **Không** (chỉ tài liệu, spec, test soát) | **Có** |
| Số phiên | 1 (mở lại khi đầy ngữ cảnh) | Mỗi đợt một phiên MỚI |
| Nhánh | `claude/fa-gaps` | `claude/fa-gaps` |

### 1.2. Các bước
1. Mở **claude.ai/code** → kho **`nguyenphanvantruong6969-arch/TESTING-DEV`** → nhánh **`claude/keen-ride-72sa7t`**
   (lần đầu; phiên cha tự tạo nhánh `claude/fa-gaps`). Từ lần thứ hai trở đi chọn nhánh **`claude/fa-gaps`**.
2. **Mở phiên CHA**: model **Opus**, quyền **auto**. Dán nguyên văn:

```text
You are the FATHER session for the FA-DAA gap job. Read INSTRUCTION_FILL_GAPS.md (repo root) PART 2 completely, then execute section F (father protocol) step by step, starting at F0. Truong authorises: (1) creating branch claude/fa-gaps and committing/pushing ONLY to it; (2) creating child (son) cloud sessions and messaging them for this job; (3) scheduling check-in reminders for this session for this job only. Truong does NOT authorise merging any PR, force-pushing, or editing branch main. Do not use the Agent tool. Keep docs/phien/FA_GAPS_STATUS.md as the single source of truth and update it before every stop. When you stop for any reason, the last line of your message must be the GitHub link to docs/phien/FA_GAPS_STATUS.md on branch claude/fa-gaps.
```

3. Phiên cha sẽ **tự tạo phiên con**. Nếu nó in ra dòng **`SON PROMPT READY: wave <n>`** (nghĩa là không tự tạo
   được), bạn làm tay: mở **phiên mới**, model **Sonnet**, quyền **auto**, nhánh **`claude/fa-gaps`**, dán nguyên văn:

```text
You are a SON session for the FA-DAA gap job. Read INSTRUCTION_FILL_GAPS.md (repo root) PART 2 sections G, S and C, then read docs/phien/FA_GAPS_STATUS.md and do ONLY the wave written under "Current wave", following section S step by step from S0. Truong authorises commits and pushes ONLY to branch claude/fa-gaps. Do not use the Agent tool, do not create sessions, do not open or merge PRs, do not change any spec. When the wave is done, blocked, or you reach the context limit, update the status file, push, and print the GitHub link to docs/phien/FA_GAPS_STATUS.md on branch claude/fa-gaps as your last line.
```

4. Phiên con xong → quay lại **phiên cha**, gõ đúng một chữ: **`continue`**.
5. Lặp bước 3–4 cho tới khi phiên cha ghi **`ALL WAVES DONE`** và in link PR nháp. Gửi link đó cho Truong.

### 1.3. Xử lý sự cố
| Thấy gì | Làm gì |
|---|---|
| Phiên dừng giữa chừng, hết lượt, lỗi mạng | Mở phiên MỚI **cùng loại** (cha = Opus, con = Sonnet), nhánh `claude/fa-gaps`, dán lại đúng câu lệnh của loại đó |
| `CONTEXT LIMIT — restart same role` | Như trên: phiên mới cùng loại, cùng câu lệnh |
| `another FATHER/SON is RUNNING` | Có phiên khác đang chạy. Đợi 3 giờ hoặc báo Truong |
| `WAIT-TRUONG: <câu hỏi>` | Chụp màn hình gửi Truong. Không tự trả lời thay Truong |
| Claude hỏi chọn phương án kỹ thuật | Trả lời: **"Choose the safest option that keeps default behaviour byte-identical, record it in the status file."** |
| Claude xin merge, đổi nhánh `main`, force-push | Trả lời: **"No."** |

### 1.4. Ước lượng
4 đợt chính + tối đa 2 đợt sửa mỗi đợt. Mỗi đợt con 1–3 giờ. Toàn bộ: khoảng 1–3 ngày, tùy số lần soát.

---

## PART 2 — For Claude (English)

### G. Global rules (both roles — read every time)

**G1. Authority and precedence.** `CLAUDE.md` wins on invariants 1–8 and working rules 1–11. Truong explicitly
authorises the father/son session structure for THIS job; that overrides rule 10 only for separate cloud sessions.
Inside any session: **no Agent tool / subagents**. Rule 11 roles hold: father = Opus (plans, reviews), son = Sonnet
(codes, ticks).

**G2. Branch.** `claude/fa-gaps`. Father creates it once from `origin/claude/keen-ride-72sa7t`, or from `origin/main`
if PR #14 is already merged. Rebase on `origin/claude/keen-ride-72sa7t` if that branch moves (father only, before a
wave starts, never during one). Push only there. **Never** force-push, merge, close PRs, or touch `main`.

**G3. Files of this job.**
| File | Owner | Content |
|---|---|---|
| `docs/phien/FA_GAPS_STATUS.md` | father writes, son ticks | lock lines, current wave, item table, review notes, log — **single source of truth** |
| `docs/ke_hoach/FA_GAPS_KE_HOACH.md` | father only | one spec block per GAP item (template in F2) |
| `docs/phien/claude__fa-gaps.md` | both | branch handoff from `docs/phien/_TEMPLATE.md` (≤ 150 lines, English) |
| `docs/phien/bao_cao_dem/<date>_fa_gaps_wave<n>.md` | father | review report per wave (Vietnamese, ≤ 60 lines) |
| `docs/phien/bao_cao_dem/<date>_fa_gaps.md` | father | final report |
| `CHANGELOG.md`, `docs/ke_hoach/TIEN_DO.md` | son per item | rule 6 |

**G4. Default OFF, byte-identical.** Every new behaviour sits behind a new key in `rules` (see
`cau_hinh_ws.MAC_DINH_TRUONG_HOC["rules"]`, next to `"fa_daa": False`) defaulting to **False / old behaviour**, and only
usable when `fa_daa` is on (validate in `cau_hinh_ws._chuan_hoa`-style checks, error code via `i18n_errors.py`).
False keys are omitted from the fingerprint by `_luat_de_ghi_hoac_bam` — keep it that way. After EVERY item:
`kiem_nhanh.py --co-so origin/main --so-seed 20` → **60/60 identical** (3 datasets × 20 seeds). Not identical = the
item is not done.

**G5. Post-allocation changes (GAP-1, 2, 3, 4) — hard design constraints.**
- The DA result of a run (`match_results` for that run) is **never edited in place** and `run_history` is
  append-only (invariant 4).
- Every seat change after publication (release, invite accepted, round-2 pick, appeal fix) is written as one row in a
  NEW append-only table (recommended name `fa_dieu_chinh`: id, created_at, buoi, student_id, club_from, club_to,
  kind ∈ {release, invite_accept, invite_decline, round2, appeal_rerun}, actor, note, run_id_base). The "current
  placement" = latest run + adjustments replayed in id order. One pure function computes it; tests cover replay.
- An appeal that fixes DATA reruns the whole pipeline (invariant 5 order) with the **locked seed** (invariant 3) and
  appends a new `run_history` row; adjustments made on the old run are re-validated and listed for the admin, never
  silently dropped.
- Never feed attendance, appeals, feedback or round-2 data into `compute_club_priority` (invariant 2).

**G6. Schema.** New tables/columns only through `rbda_priority_pipeline.di_tru_schema` (idempotent, backup first,
test that running it twice is a no-op and that an old DB upgrades). No change to the CSV column contract (invariant 7);
new exports are NEW files.

**G7. Forbidden.** Editing `run_rbda`, `run_rbda_nhieu_buoi`, `club_choice_function`, `compute_club_priority`,
`verify_stability`; any new library (stop rule); deleting/overwriting `run_history`; using `hash()` for anything
random (use `zlib.crc32`); real school data, names, emails, tenant ids, app URLs; writing interpretation or
conclusions for the student's report (academic integrity). Microsoft parts stay labelled **TH (untested on real
Microsoft)**. **D8 stays open**: never choose Power Apps vs Forms.

**G8. UI rules.** Contract `{ok, data, errors}`; messages only from `i18n_errors.py` → `python tao_i18n_js.py`;
visible strings in `i18n.js` with vi AND en; no "Wharton" and no forbidden forms of address in visible text
(`kiem_nhanh` `chu_cam`); Chromium tests in `tests/test_giao_dien_fa_gap*.py` following `tests/test_giao_dien_fa_*.py`.
A skipped UI test is NOT a pass.

**G9. Locate code by function name** (`grep -n "def <name>" <file>`), never by line number.

---

### The gap list (codes, waves and minimum scope are FIXED; the father writes the detailed spec)

| Code | Vision § | What must exist at the end | Wave | Kind | Depends on |
|---|---|---|---|---|---|
| GAP-0 | — | `fa_dieu_chinh` table + pure replay function `vi_tri_hien_tai(...)` + tests (G5) | 1 | kiosk core of post-allocation | — |
| GAP-1 | §9.3 | Attendance: per club, the first 3 sessions; teacher marks present / excused / unexcused; 2 of 3 unexcused → seat released (adjustment row `release`), behind `rules.fa_diem_danh`; screen + xlsx export by club | 1 | kiosk | GAP-0 |
| GAP-2 | §9.3, D4 | Waitlist invites: on a released seat, offer to the head of that club's waitlist (D4 order: SELECTIVE score→medal→STB; LIMITED medal→STB; only students who ranked it above their current club); accept / decline / expire; each step an adjustment row; the next head is offered on decline | 1 | kiosk | GAP-0, GAP-1 |
| GAP-3 | §9.2 | Appeals: entry form in kiosk (student id, day, kind = data error only, note), 3-day window from publication (configurable), admin accept/reject; accept → admin fixes data → full rerun with locked seed (G5); list of affected students; export | 2 | kiosk | GAP-0 |
| GAP-4 | §9.3 | Round 2: students without any wanted club pick among remaining seats in STB order (one pass, logged as `round2`), behind `rules.fa_vong_2` | 2 | kiosk | GAP-0 |
| GAP-5 | §9.1 | 3 one-tap feedback questions (satisfaction 1–5; understood reason yes/no; hardest part: choose club / ordering / medals / challenge / none): kiosk screen after result + Forms generator section (`tao_mau_forms.py` / `bieu_mau.py`, flag `--phan-hoi`) + importer to a new table; xlsx export | 2 | kiosk + Forms (TH) | — |
| GAP-6 | §9.3 | Week-3 survey (2 questions: still attending? want to change?) Forms generator + importer + export | 2 | Forms (TH) | — |
| GAP-7 | §10 | Next-term capacity suggestion = last term NV1 demand per club, capped by the teacher's limit; uses `fa_daa.bang_nhu_cau`; export + a column in the demand table; teacher may only increase (reuse `so_sanh_suc_chua.py` rule) | 3 | kiosk | — |
| GAP-8 | §11 | Admin dashboard: every row of the §11 table that has data (no CLB; NV1 / top-2 rate; data vs lottery decisions from `fa_ly_do`; students who lost a lottery ≥ 1; registration rate after 3 days if available; rush-flag rate; grader deviation; attendance of first 3 sessions; satisfaction; understood reason; medal-change rate). Missing data → shown as "chưa có dữ liệu", never invented. Read-only screen + xlsx export | 3 | kiosk | GAP-1, 5, 9 |
| GAP-9 | §7.4 | Two-grader deviation: in `mau_forms_thi_clb/phan_tich_cau_hoi.py`, read an optional second-grader column, report mean absolute difference per club/question, flag ≥ 1.5 points; section in `ghi_bao_cao` | 3 | converter (TH) | — |
| GAP-10 | §5.2 | Reminders: Power Automate flow guide (open, −2 days, −3 hours; SELECTIVE not attempted ×2; < 50 % after 3 days → homeroom list via `T4M_FLOW_GUI_GVCN.md`) + a generator that produces the homeroom "not registered yet" lists from a registration export; respects 6,000 requests/user/day | 3 | docs + generator (TH) | — |
| GAP-11 | §5.1 | Path A autosave app: complete the Power Apps build kit (`mau_forms_thi_clb/bo_dung_t4m/`, spec `docs/he_sinh_thai/T4M_DAC_TA_SUA_APP.md` §12 R39–R54): DRAFT/SUBMITTED autosave, `Shuffle()` order, ▲▼, min 3, FREE warning, medal widget | 4 | Microsoft kit (TH) | **WAIT-TRUONG if D8 = Forms only** (then mark "not needed", 100 % by decision) |
| GAP-12 | §12 | Simulation: full "calculating" student (moves gold away from overcrowded clubs, learns from last term's cut-offs) + per-type lottery-loss table + "old vs new" table for all 3 types in `du_lieu_test/mo_phong_fa_daa.py`; tables only | 4 | measure only | — |
| GAP-13 | §8.8 | `stable_improvement_cycles` (Erdil & Ergin 2008) as a POST-processing step after DA, only cycles that violate lottery order alone, behind `rules.fa_vong_doi_cho` (False). Invariant 8: run in **measurement mode**, label "không bảo đảm ổn định" unless property tests prove stability w.r.t. score/medal; simulation table of benefit by student type (GAP-12) | 4 | kiosk, flag OFF | GAP-12 |
| GAP-14 | §8.4, §13.12 | Compensation credit (D1): **NO CODE.** Run GAP-12 two-term measurement, write a 1-page decision memo (options, incentive risk, numbers, what invariant-2 exception would be needed) in `docs/ke_hoach/FA_GAPS_D1_MEMO.md`; status WAIT-TRUONG | 4 | memo | GAP-12 |

**Not in this job (stay as they are):** real Microsoft test with IT; D8 decision; the Windows build workflow; anything
in the vision §15 "rejected" table.

---

### F. FATHER protocol (Opus)

**F0. Start or resume (every father session).**
1. Read `CLAUDE.md`, then `docs/phien/claude__fa-gaps.md` (if it exists), then this file, then
   `docs/phien/FA_GAPS_STATUS.md` (if it exists). Do NOT read the whole vision; read only the § of the items in the
   current wave.
2. Lock: if `RUNNING-FATHER: <UTC> <session>` in the status file is < 3 h old and not yours → print
   `another FATHER is RUNNING`, stop. Otherwise write/refresh your line, commit `GAP-KH: father lock`, push.
3. Look at "Current wave" and its state, and jump:
   | Status says | Go to |
   |---|---|
   | file missing | F1 |
   | `wave <n>: spec needed` | F2 |
   | `wave <n>: spec ready` | F3 |
   | `wave <n>: son running` | F4-wait |
   | `wave <n>: son done, waiting for father review` | F5 |
   | `wave <n>: GO` | F2 for the next wave, or F7 if none left |
   | `ALL WAVES DONE` | print link, stop |

**F1. Setup (once).**
```bash
git fetch origin claude/keen-ride-72sa7t main
git checkout -b claude/fa-gaps origin/claude/keen-ride-72sa7t   # or origin/main if PR #14 merged
```
Create `docs/phien/FA_GAPS_STATUS.md` from the template in F8, `docs/phien/claude__fa-gaps.md` from
`docs/phien/_TEMPLATE.md` (Goal = this job; Plan = the gap table codes with checkboxes), and an empty
`docs/ke_hoach/FA_GAPS_KE_HOACH.md` with a header. Status: `Current wave: 1 — spec needed`. Commit `GAP-KH: setup`,
push with `-u`. Baseline: run `kiem_nhanh.py --co-so origin/main --so-seed 20` and `tests/test_nhieu_buoi.py -k
TestTrungKhit`; record counts in the status file. Red baseline → status `BLOCKED: baseline red`, stop, tell Truong.

**F2. Write the specs of ONE wave** in `FA_GAPS_KE_HOACH.md`, one block per item, using EXACTLY this template:
```markdown
### GAP-n <title>  (vision §x; parent registry item <code>; wave <w>)
- Why: <one sentence from the vision>
- Flag: `rules.<key>` default False; valid only when `fa_daa` is on; error code `<code>` if misused
- Data: <new table/columns via di_tru_schema, or "none">; replay/adjustment rows (G5) if any
- Backend: <file> → new/changed functions by name, inputs, outputs, `{ok,data,errors}` shapes
- UI: <js file + function>, element ids, i18n keys (vi+en); or "none"
- Export: <file name>, columns; never student names in lottery/aggregate exports
- Tests first (kiem_nhan): <test file>: 1) … 2) … (each states the input and the exact expected output)
- Mutation to try: <which line, which test must go red>
- Invariant check: 60/60 identical; plus <item-specific property>
- Out of scope: <list>
- Size: S / M / L  (L → split into two waves of ≤ 3 items)
```
Read only the code you need to write correct function names (G9). If an item cannot be specified without a Truong
decision → write `WAIT-TRUONG: <one precise yes/no or A/B question>` in the status file, skip that item, continue.
Status: `Current wave: <n> — spec ready`, items of the wave → `TODO`. Commit `GAP-KH: spec wave <n>`, push.

**F3. Dispatch the son.**
1. Status: `Current wave: <n> — son running`, `son session: <id or "manual">`. Commit, push.
2. Try to create the son yourself with the claude-code-remote `create_session` tool:
   - `source_url`: `https://github.com/nguyenphanvantruong6969-arch/TESTING-DEV`, `source_revision`: `claude/fa-gaps`
   - model: the Sonnet model your environment offers (do not hard-code an id in repo files)
   - `title`: `FA gaps — son wave <n>`; `permission_mode`: inherit (never `plan`)
   - `prompt`: the SON prompt from PART 1 §1.2 step 3, verbatim
   Record the returned session id in the status file.
3. If `create_session` is unavailable or refused → print `SON PROMPT READY: wave <n>` and the SON prompt, update the
   handoff, and stop (the human starts the son and later types `continue`).

**F4-wait. Wait loop (only when you created the son).** Never poll with `sleep`. Schedule a check-in for this session
with `send_later` (45 minutes; message: `check son wave <n>`), then end your turn. On each check-in:
1. `get_session(<son id>)`: `status_bucket` working → schedule another check-in (45 min), end turn.
2. `failed` → read the last events (`list_events`, kinds user/assistant/result), record the reason, then either
   re-dispatch a NEW son for the same wave (max 2 times per wave) or mark the remaining items BLOCKED.
3. idle/completed → `git pull`; if the status file says `son done` → F5; if not (son stopped early, e.g. context
   limit) → dispatch a new son for the remaining items (counts toward the 2 re-dispatches).
Max total waiting per wave: 8 hours → then BLOCKED `son timeout`, report.

**F5. Review the wave (father does this himself; no code fixes by the father).**
For each item of the wave, in order:
1. `git log` — one commit per item, message `GAP-n: …`; spec followed; nothing outside the spec's files.
2. Tests: the item's test file(s) + `tests/test_nhieu_buoi.py -k TestTrungKhit` + `tests/test_wharton_pipeline.py` +
   all `tests/test_fa_*.py` + `tests/test_giao_dien_fa_*.py` (Chromium must really run; count PASSED, not skipped).
3. Mutation spot-check: break the line named in the spec, confirm red, restore (copy first, never `git checkout --`
   on uncommitted work).
4. `kiem_nhanh.py --co-so origin/main --so-seed 20` → 7/7 and 60/60 identical.
5. Skill `soat-ma` four tiers on the wave diff (`git diff <wave start>..HEAD`): report only.
6. Severity: **cao/trung** (wrong result, crash, invariant risk, data loss, privacy leak) → fix needed;
   **nhỏ** (wording, order, style) → list only.
Write `docs/phien/bao_cao_dem/<date>_fa_gaps_wave<n>.md` (Vietnamese, plain, ≤ 60 lines: table item / kết quả /
lỗi tìm thấy / mức) and in the status file either:
- `wave <n>: GO` (no cao/trung) → F2 for the next wave; or
- `wave <n>: NEEDS-FIX` + fix items `GAP-n-F1 …` each with repro + expected → write them as a mini-spec block in
  `FA_GAPS_KE_HOACH.md`, set `Current wave: <n>-fix<k> — spec ready` → F3.
**Loop limits:** max 2 fix waves per wave. A cao/trung bug still present after fix wave 2 → item BLOCKED with the
repro; continue with the next wave only if it does not depend on the blocked item.

**F6. Between waves.** Refresh `Coverage` in the status file (per §14 row, %), update the handoff "Current state"
and "Next steps", commit `GAP-KH: wave <n> reviewed`, push. If your context is above ~400k tokens → do C3 and stop.

**F7. Finish.**
1. All items DONE, BLOCKED, or WAIT-TRUONG. Run the full related suite once more + `kiem_nhanh --so-seed 20`.
2. Final report `docs/phien/bao_cao_dem/<date>_fa_gaps.md` (Vietnamese, plain words, ≤ 80 lines):
   `# Báo cáo lấp khoảng trống FA-DAA <ngày>`; one line `xong X/15, chặn Y, chờ Truong Z`; table
   `| Mục | Việc (1 câu dễ hiểu) | Kết quả | Commit |`; `## Độ phủ tầm nhìn` (each §14 row: before % → after %);
   `## Chờ Truong quyết` (each WAIT-TRUONG with the exact question and options); `## Bị chặn`; `## Kiểm tra`
   (test counts, UI really run, 60/60, ruff) with **"số liệu MÔ PHỎNG"**.
3. Status: `ALL WAVES DONE`. Remove your lock. Commit `GAP-BC: final report`, push, verify remote HEAD = local HEAD.
4. Open ONE **draft** PR `claude/fa-gaps → main` (mirror the repo PR template headings if one exists; body: summary,
   item table, links to the reports, "Truong merges"). Never merge.
5. Last line: link to `docs/phien/FA_GAPS_STATUS.md` on `claude/fa-gaps`. Stop.

**F8. Status file template** (`docs/phien/FA_GAPS_STATUS.md`):
```markdown
# FA gaps — status (single source of truth)
RUNNING-FATHER: <UTC> <session or "none">
RUNNING-SON: <UTC> wave <n> <session or "none">
Current wave: <n> — <spec needed | spec ready | son running | son done, waiting for father review | GO | NEEDS-FIX>
son session: <id | manual | none>   re-dispatches this wave: <0..2>   fix waves this wave: <0..2>

## Items
| Code | Wave | State (TODO/DOING/DONE/BLOCKED/WAIT-TRUONG) | Commit | Note |
|---|---|---|---|---|
| GAP-0 | 1 | TODO | | |
… (GAP-1 … GAP-14, then GAP-n-Fk fix rows as they appear)

## Coverage (vision §14 rows, % before → now)
## Waiting for Truong
## Review notes (newest last)
## Log (append only: date | role | what | result)
```

---

### S. SON protocol (Sonnet)

**S0. Start or resume.**
1. Read `CLAUDE.md`, `docs/phien/FA_GAPS_STATUS.md`, and ONLY the spec blocks of the current wave in
   `docs/ke_hoach/FA_GAPS_KE_HOACH.md`. Do not read the vision or other specs.
2. Status must say `son running` (or `spec ready`) for the current wave; otherwise print
   `nothing to do: <status line>` and stop.
3. Lock: if `RUNNING-SON` is < 3 h old and not yours → print `another SON is RUNNING`, stop. Otherwise write
   `RUNNING-SON: <UTC> wave <n> <your session>`, commit `GAP-KH: son lock wave <n>`, push.
4. Resume: skip items already `DONE` or `BLOCKED`.

**S1. Setup (once per session).**
```bash
git fetch origin claude/fa-gaps main
git checkout claude/fa-gaps && git pull --rebase origin claude/fa-gaps
python3 -m venv .venv && .venv/bin/pip install -q -r requirements-dev.txt
.venv/bin/pip install -q playwright==1.63.0
git fetch --unshallow 2>/dev/null; git fetch origin main:refs/remotes/origin/main
PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers .venv/bin/python -m pytest -q tests/test_giao_dien_wharton.py -x 2>&1 | tail -3
```
The last command must show PASSED tests. If UI tests only skip → every UI part is BLOCKED `no browser`; still do the
backend parts. Prefix EVERY UI test command with `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`.
Quiet test command (never paste full output):
```bash
.venv/bin/python -m pytest -q -p no:cacheprovider --no-header -rf --tb=no <files or -k> 2>&1 | grep -E '^(FAILED|ERROR)|passed|failed|skipped' | tail -25
```

**S2. Per item, in spec order — do a → j, one item at a time.**
- a. Set the item `DOING` in the status file (no commit needed yet).
- b. **Tests first:** write every test listed in the spec's "Tests first". Run them: RED, for the right reason
  (read the message; an ImportError is not "the right reason" unless the spec says the function is new).
- c. **Minimal code** to make them green. Follow the spec's function names, flag, data, UI ids, export names exactly.
  Schema → `di_tru_schema` + test (twice = no-op; old DB upgrades). Messages → `i18n_errors.py` then
  `python tao_i18n_js.py`; UI strings → `i18n.js` vi + en.
- d. **Related tests:** the item's tests + every `tests/` file that greps a function/file you changed +
  `tests/test_nhieu_buoi.py -k TestTrungKhit` + `tests/test_wharton_pipeline.py` + `tests/test_fa_*.py`;
  UI items also `tests/test_giao_dien_fa_*.py` and `tests/test_giao_dien_wharton.py`. Then `ruff check .`.
- e. **Mutation:** copy the file aside, apply the spec's mutation (or break one line of your fix), confirm a test goes
  red, restore from the copy, `git diff` shows only intended changes.
- f. **Invariant 1:** `.venv/bin/python .claude/skills/soat-ma/scripts/kiem_nhanh.py --co-so origin/main --so-seed 20`
  → 7/7, 60/60 identical. Not identical → fix before going on (counts as an attempt).
- g. **Bookkeeping:** new test file → update the test-file count in `docs/ke_hoach/CLAUDE_CHI_TIET.md` (code map row
  `tests/`); new module → add it to the code map there. `CHANGELOG.md` entry (date, item code, files, new tests);
  one row in `docs/ke_hoach/TIEN_DO.md`.
- h. **Status:** item `DONE` + commit hash placeholder; append a log row `date | son | GAP-n: tests red first, N
  related passed, UI M really ran, mutation caught, 60/60 | ok`. Tick in `docs/phien/claude__fa-gaps.md` Plan.
- i. **Commit** `GAP-n: <short summary>` (+ attribution lines your harness gives), then
  `git pull --rebase origin claude/fa-gaps && git push -u origin claude/fa-gaps`; network error → retry 2 s, 4 s, 8 s,
  16 s. Put the real hash in the status file in the next commit.
- j. Check context (C2). Next item.

**S3. Stop rules → BLOCKED.** Mark `BLOCKED: <one line why>` in the status file, commit, push, go to the next item that
does not depend on it, when: an invariant would break; baseline red; a new library is needed; a schema/CSV change
outside the spec; a forbidden function (G7) must change; the same test still fails after **3 honest attempts**; UI
tests only skip (UI part only); **the spec is wrong or unclear** → `BLOCKED: spec: <why>` (never re-spec yourself).

**S4. End of wave.**
1. Status: `Current wave: <n> — son done, waiting for father review`; summary line `done X, blocked Y`.
2. Handoff `docs/phien/claude__fa-gaps.md`: rewrite "Current state", append a session-log row.
3. Remove your `RUNNING-SON` line. Commit `GAP-KH: son wave <n> done`, push, verify
   `git rev-parse HEAD` == `git rev-parse origin/claude/fa-gaps` after `git fetch`.
4. Last line: link to `docs/phien/FA_GAPS_STATUS.md` on `claude/fa-gaps`. Stop. Do NOT start the next wave.

---

### C. Context management (both roles)

**C1. Read little.** Find code with `grep -n "def <name>"`, then read only that function (`sed -n 'a,bp'`). Never read
whole large files (`rbda_priority_pipeline.py`, `api_*.py`, `js/*.js`, `index.html`). Never paste full test output or
diffs; use the quiet pytest command and `git diff --stat`.

**C2. Budgets.** Son: stop new work at ~**300k** tokens. Father: at ~**400k**. One wave per son session; a new wave or
a re-dispatch always uses a NEW son session (fresh context). The father keeps decisions in the status file, specs in
`FA_GAPS_KE_HOACH.md`; never copies specs into chat.

**C3. Clean stop at the limit.** Finish the current step (never stop between "code changed" and "tests run"), update
the status file and the handoff ("Current state": exact next step; "Next steps"), remove your lock line, commit
`GAP-KH: context stop (<role>)`, push, print `CONTEXT LIMIT — restart same role with the same prompt` and the status
link. Stop. The Stop hook `.claude/hooks/handoff_khi_day_ngu_canh.py` also reminds you.

**C4. Zero-memory rule.** After every commit, a brand-new session with no chat history must be able to continue from
`CLAUDE.md` + `docs/phien/claude__fa-gaps.md` + `docs/phien/FA_GAPS_STATUS.md` + `FA_GAPS_KE_HOACH.md` alone.

---

### D. Things that bite in this repo
- Day order: always `khoa_sap_buoi` / `THU_TU_BUOI` (`chu_nhat` after `thu_7`), never a plain string sort.
- `tests/test_a13_12_tai_lieu.py::test_ban_do_ma_so_tep_test_la_so_that` counts `tests/test_*.py` files.
- `rules` keys that are False never appear in `run_history.luat_xep` or the fingerprint (`_luat_de_ghi_hoac_bam`).
- Variant/lottery randomness: `zlib.crc32` on UTF-8, never `hash()`; locked STB numbers never change (invariant 3).
- Lottery record and aggregate exports: no student names or ids.
- `EMAIL_MA_HS.csv` and any Forms export are personal data: never commit a real one; tests use simulated emails.
- UI tests skip silently without a browser: skipped ≠ passed.
- `kiem_nhanh --so-seed N` must give 3 × N cases after the small-fix job (FA-P7/SM-3); if it still prints 5 seeds,
  call `kiem_trung_khit(goc_moi, goc_cu, seeds=range(1, 21))` from that script directly.
- All numbers in reports are SIMULATED data; say so every time.
