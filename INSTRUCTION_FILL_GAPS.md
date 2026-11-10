# INSTRUCTION — FILL ALL VISION GAPS (father/son sessions) — 2026-11-10

> Run this **AFTER** `LATEST_INSTRUCTION.md` (7 small fixes) is finished and PR #14 is merged or green.
> Goal: bring every vision priority row (`docs/ke_hoach/FA_DAA_VISION.md` §14, plus §11, §8.8, §13.12) to 100 %
> **where code can do it**. Items that need a Truong decision are prepared to the decision point and marked WAIT-TRUONG.

---

## PHẦN 1 — Cho người chạy (tiếng Việt)

Có **2 loại phiên**:
- **Phiên CHA (Opus)**: lên kế hoạch, viết spec, giao việc, soát kết quả. Không viết mã tính năng.
- **Phiên CON (Sonnet)**: làm đúng MỘT gói việc (một "đợt") rồi dừng.

### Bước chạy
1. claude.ai/code → kho `nguyenphanvantruong6969-arch/TESTING-DEV` → nhánh **`claude/keen-ride-72sa7t`**
   (phiên cha sẽ tự tạo nhánh mới `claude/fa-gaps` từ đó).
2. **Phiên CHA**: chọn **Opus**, chế độ **auto**, dán:
```text
You are the FATHER session. Read INSTRUCTION_FILL_GAPS.md PART 2 and do section F (father protocol) exactly. Truong authorises commits and pushes to branch claude/fa-gaps only, and authorises you to create and message child sessions for this job. Never merge a PR. Stop when section F says stop and print the status file link as your last line.
```
3. Khi phiên cha in ra **"SON PROMPT READY: wave <n>"** (nếu nó không tự tạo được phiên con), mở **phiên mới**, chọn
   **Sonnet**, auto, cùng kho, nhánh **`claude/fa-gaps`**, dán:
```text
You are a SON session. Read INSTRUCTION_FILL_GAPS.md PART 2 and do section S (son protocol) for the wave written in docs/phien/FA_GAPS_STATUS.md under "Current wave". Truong authorises commits and pushes to branch claude/fa-gaps only. No subagents. Stop when the wave is done and print the status file link as your last line.
```
4. Phiên con xong → quay lại phiên cha, gõ: `continue` (phiên cha soát rồi mở đợt tiếp).
5. Phiên nào dừng giữa chừng → mở phiên mới cùng loại, dán lại đúng câu đó. Mọi thứ được lưu trong tệp trạng thái.
6. Xong hết khi tệp `docs/phien/FA_GAPS_STATUS.md` ghi **"ALL WAVES DONE"**. Gửi link tệp đó cho Truong.

---

## PART 2 — For Claude (English)

### G. Global rules (both roles)
- `CLAUDE.md` wins on invariants 1–8 and rules 1–11. Truong explicitly authorises the father/son structure for this job
  (overrides rule 10 only for creating separate sessions; still **no Agent-tool subagents inside a session**).
- Branch: `claude/fa-gaps`, created by the father from `origin/claude/keen-ride-72sa7t` (or `origin/main` if PR #14 is
  merged). Push only there. Never force-push, never merge. The father opens ONE draft PR `claude/fa-gaps → main` at the end.
- **Single source of truth:** `docs/phien/FA_GAPS_STATUS.md` (father creates it). Holds: lock line, current wave, item
  table (code, wave, owner, state TODO/DOING/DONE/BLOCKED/WAIT-TRUONG, commit), review notes, session log.
- **Default OFF:** every new feature sits behind a rule flag defaulting to the old behaviour → invariant 1 (60/60
  identical, 3 datasets × 20 seeds) must hold after EVERY item.
- Forbidden: DA core functions (`run_rbda`, `run_rbda_nhieu_buoi`, `club_choice_function`, `compute_club_priority`,
  `verify_stability`), rank/previous-outcome into priority (invariant 2), deleting `run_history` rows, new libraries,
  CSV column contract changes not listed in an item spec. Need one → BLOCKED.
- Microsoft parts stay **TH (untested on real Microsoft)**; D8 stays OPEN; never pick Power Apps vs Forms.
- Data: simulated only. Never draft report commentary (academic integrity).

### Gap list (the father turns each into a spec in `docs/ke_hoach/FA_GAPS_KE_HOACH.md`; codes fixed here)

| Code | Vision | Gap to close | Wave | Notes |
|---|---|---|---|---|
| GAP-1 | §9.3 | Kiosk **attendance**: record 3 first sessions per club; 2/3 unexcused absences → release seat (flag) | 1 | New table via `di_tru_schema` (idempotent, backup first) |
| GAP-2 | §9.3 | **Waitlist invite flow**: free seat → offer to head of waitlist (D4 order), accept/decline, audit row | 1 | Reads existing `fa_ly_do.waitlist_pos`; never reruns DA |
| GAP-3 | §9.2 | **Appeal entry** in kiosk (3-day window, data errors only) → fix data → rerun same seed | 1 | Rerun uses locked STB (invariant 3); new `run_history` row |
| GAP-4 | §9.3 | **Round 2**: students without a wanted club pick among remaining seats (STB order) | 2 | Post-allocation step, logged; not a DA change |
| GAP-5 | §9.1 | **3 one-tap feedback questions**: kiosk screen + Forms generator section + import of results | 2 | Feeds GAP-8 |
| GAP-6 | §9.3 | **Week-3 survey** (2 questions) Forms generator + import | 2 | TH |
| GAP-7 | §10 | **Capacity suggestion** next term = last term NV1 demand, capped by teacher limit; export | 2 | Reads FA-7 demand table |
| GAP-8 | §11 | **Admin dashboard**: every §11 metric from `fa_ly_do`, results, GAP-1/5 data; export xlsx | 3 | Read-only screen |
| GAP-9 | §7.4 | **Two-grader deviation** report (< 1.5 points) in `phan_tich_cau_hoi.py` | 3 | TH |
| GAP-10 | §5.2 | **Reminders**: Power Automate flow kit + homeroom list (<50 % after 3 days) generator | 3 | Docs + generator; TH |
| GAP-11 | §5.1 | **Path A autosave app** build kit completion (DRAFT/SUBMITTED, Shuffle, ▲▼) | 3 | WAIT-TRUONG if D8 = Forms only |
| GAP-12 | §12 | Simulation: full **"calculating" student** behaviour + per-type lottery loss table | 3 | Measure only |
| GAP-13 | §8.8 | `stable_improvement_cycles` (Erdil & Ergin 2008) as post-processing, flag OFF | 4 | Invariant 8: measurement mode label "không bảo đảm ổn định" unless proven; property tests |
| GAP-14 | §8.4, §13.12 | **Compensation credit** D1 | 4 | **WAIT-TRUONG**: needs invariant-2 exception. Only run GAP-12 two-term measurement + write the decision memo; no code |

Waves 1→4 in order; inside a wave, items in table order. A son does ONE wave (or, if the wave is big, the father
splits it into "wave 1a/1b" with ≤ 3 items each).

---

### F. FATHER protocol (Opus)
**F0. Start / resume.** Read `CLAUDE.md`, `docs/phien/claude__keen-ride-72sa7t.md`, this file, then
`docs/phien/FA_GAPS_STATUS.md` if it exists (resume from it). Lock: a `RUNNING-FATHER:` line < 3 h old → stop.
**F1. Setup (first time only).** Create branch `claude/fa-gaps`; create `FA_GAPS_STATUS.md` (table above, all TODO)
and `docs/phien/claude__fa-gaps.md` (handoff from `_TEMPLATE.md`, Goal + Plan). Commit `GAP-KH: setup`, push.
**F2. Spec the next wave** in `docs/ke_hoach/FA_GAPS_KE_HOACH.md`: per item → parent registry item, files, functions
(by name), data model change (if any), flag name + default, UI strings (vi + en, via `i18n_errors.py`/`i18n.js`),
`kiem_nhan` (exact failing tests to write first), invariant check, out-of-scope. Read only the code you need.
Ask Truong (one question, then wait) ONLY if a spec needs a decision listed as WAIT-TRUONG.
**F3. Dispatch.** Set "Current wave: <n>" in the status file, commit, push. Then EITHER create a child session
(`create_session`, Sonnet, branch `claude/fa-gaps`, prompt = the SON prompt in PART 1 step 3) and wait for it,
OR print `SON PROMPT READY: wave <n>` and stop (the human starts the son).
**F4. Review** when the son reports done (or on `continue`): pull; for each item: re-run its tests + `TestTrungKhit`
+ `tests/test_fa_*.py` + related UI tests (Chromium must really run); `kiem_nhanh.py --co-so origin/main --so-seed 20`
(60/60); run skill `soat-ma` 4 tiers on the wave diff. Write review notes in the status file:
GO / NEEDS-FIX (list `GAP-n-Fk` fixes). NEEDS-FIX → dispatch a **fix wave** (same son protocol) before the next wave.
**F5. Loop.** Repeat F2→F4 until all items are DONE, BLOCKED or WAIT-TRUONG. **Loop limits:** max 2 fix waves per
wave; a 3rd failure → BLOCKED with reason. Max 4 main waves.
**F6. Finish.** Write `docs/phien/bao_cao_dem/<date>_fa_gaps.md` (Vietnamese, ≤ 80 lines: table per GAP, % coverage of
§14 before/after, blocked/wait items with the exact decision Truong must take, test counts, "SIMULATED data").
Status file: `ALL WAVES DONE`. Open ONE **draft** PR `claude/fa-gaps → main` (template headings). Print status link. Stop.

### S. SON protocol (Sonnet)
**S0.** Read `CLAUDE.md`, `docs/phien/FA_GAPS_STATUS.md` ("Current wave"), ONLY the specs of that wave in
`FA_GAPS_KE_HOACH.md`. Lock: write `RUNNING-SON wave <n>: <UTC>`; if another RUNNING-SON < 3 h exists → stop.
**S1. Setup** exactly as `LATEST_INSTRUCTION.md` PART 2 §1 (venv, playwright, `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`,
fetch `origin/main`), on branch `claude/fa-gaps`.
**S2. Per item** — exactly `LATEST_INSTRUCTION.md` PART 2 §3 steps a→h (red test first, minimal code, related tests,
mutation check, bookkeeping, `kiem_nhanh`, tick + log, commit `GAP-n: ...` + push), but tick in `FA_GAPS_STATUS.md`
and log in `docs/phien/claude__fa-gaps.md`. Schema change → `di_tru_schema` idempotent + backup + test.
**S3. Stop rules** = `LATEST_INSTRUCTION.md` §5. Never re-spec: if the spec is wrong/unclear → BLOCKED "spec: <why>".
**S4. End of wave:** status file "wave <n>: son done, waiting for father review", remove lock, push, print link. Stop.

### C. Context management (both roles)
- Read by **function name** and **sections**, never whole big files; quiet pytest command only; never paste logs.
- Before every commit: the status file must let a fresh session continue with zero chat history.
- Past ~**300k tokens** (son) / ~**400k** (father): finish the current step, update status + handoff ("Current state",
  "Next steps"), commit, push, print `CONTEXT LIMIT — restart same role with the same prompt`, stop.
- One wave per son session; a new wave = a new son session (fresh context).
- Father keeps only decisions and review notes in the status file; specs live in `FA_GAPS_KE_HOACH.md`.
