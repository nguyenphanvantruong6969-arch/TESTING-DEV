# START HERE — one entry point for every run (2026-11-10)

> The human sends ONE short prompt (section 1). Claude reads this file and works out by itself which phase and which
> instruction file to run. Detailed instructions live in `LATEST_INSTRUCTION.md` (phase 1) and
> `INSTRUCTION_FILL_GAPS.md` (phase 2); this file only routes.

---

## 1. Cho người chạy (tiếng Việt)

> **Việc mới (2026-11-11): đưa việc IT vào giao diện kiosk (FA-M7 → FA-M10)** — không dùng tệp này; xem
> `docs/ke_hoach/it_ui_song_song/TU_DONG.md` (một câu dán, chạy tự động SOLO hoặc ĐIỀU PHỐI).

**Cách nhanh nhất — tự động hết, không cần nhập thêm:** mở MỘT phiên, model **Opus**, quyền **auto**, dán:

`Read START_HERE.md and act as SOLO. Truong authorises commits and pushes to claude/keen-ride-72sa7t and claude/fa-gaps only, scheduling check-in reminders for this session, and opening one draft PR at the end; never merge or close a PR; never force-push; no Agent tool; never ask me anything, just continue until ALL WAVES DONE.`

Một phiên làm cả hai giai đoạn, tự soát lại, tự sửa và tự lặp. Chỉ khi phiên bị ngắt hẳn và in `RESTART`, dán lại đúng
câu trên. Cách hai phiên CHA/CON bên dưới vẫn dùng được (soát độc lập hơn, nhưng cần người mở phiên con).

Chỉ có **2 câu lệnh**. Dùng đúng câu theo loại phiên.

| Loại phiên | Model | Câu lệnh dán vào |
|---|---|---|
| **CON** (làm việc) | **Sonnet** | `Read START_HERE.md and act as SON. Truong authorises commits and pushes to claude/keen-ride-72sa7t and claude/fa-gaps only; never merge or close a PR; no Agent tool.` |
| **CHA** (lên kế hoạch, soát) | **Opus** | `Read START_HERE.md and act as FATHER. Truong authorises commits and pushes to claude/fa-gaps only, creating son sessions and check-in reminders for this job; never merge a PR; no Agent tool.` |

**Cách mở phiên:** claude.ai/code → kho `nguyenphanvantruong6969-arch/TESTING-DEV` → nhánh
`claude/keen-ride-72sa7t` (chọn nhánh nào cũng được, Claude tự chuyển sang nhánh đúng) → chọn model → quyền
**auto** → dán câu lệnh → gửi.

**Thứ tự:**
1. Mở một phiên **CON**. Phiên này làm Giai đoạn 1 (sửa 7 lỗi nhỏ) rồi in ra link báo cáo.
2. Mở một phiên **CHA**. Phiên này bắt đầu Giai đoạn 2, tự tạo phiên con, chạy từng đợt và soát lại.
3. Phiên CHA in **`SON PROMPT READY`** → mở phiên **CON** mới (câu lệnh như trên). Phiên CON xong → quay lại phiên CHA,
   gõ `continue`.
4. Kết thúc khi phiên CHA ghi **`ALL WAVES DONE`** và gửi link PR nháp → gửi link cho Truong.

**Sự cố:** phiên dừng giữa chừng, hết lượt, `CONTEXT LIMIT` → mở phiên MỚI cùng loại, dán lại đúng câu lệnh đó.
`... is RUNNING` → đang có phiên khác chạy, đợi 3 giờ. `WAIT-TRUONG` → chụp màn hình gửi Truong.
Claude hỏi phương án kỹ thuật → trả lời *"Choose the safest option that keeps default behaviour byte-identical, record
it in the status file."* Claude xin merge, sửa `main`, force-push → trả lời *"No."*

---

## 2. For Claude (English) — the router

### 2.1. Before anything
1. `CLAUDE.md` is loaded; it wins on invariants. No Agent tool. Never merge/close a PR, never force-push, never touch
   `main`.
2. Fetch the state (do not trust the branch you were opened on):
```bash
git fetch origin claude/keen-ride-72sa7t main
git fetch origin claude/fa-gaps 2>/dev/null || true
```
3. Work out the phase:
   - **Phase 1 done** ⇔ `git ls-tree -r --name-only origin/claude/keen-ride-72sa7t docs/phien/bao_cao_dem/` lists a file
     ending in `_sua_nho.md`.
   - **Phase 2 started** ⇔ branch `origin/claude/fa-gaps` exists and holds `docs/phien/FA_GAPS_STATUS.md`.
   - **Phase 2 done** ⇔ that status file contains `ALL WAVES DONE`.
4. Branch note: if your environment designated a different branch, the human's prompt still authorises the branch
   named below; check it out and push there. If a push is refused by the server, push to your designated branch
   instead, write that branch name in the handoff/status file and in your final message, and stop.

### 2.2. Route table
| Your role | Phase state | Do |
|---|---|---|
| SON | phase 1 NOT done | `git checkout claude/keen-ride-72sa7t && git pull --rebase origin claude/keen-ride-72sa7t`, then follow **`LATEST_INSTRUCTION.md` PART 2** completely (sections 0→7). Last line: the report link it specifies. |
| SON | phase 1 done, phase 2 started, not done | `git checkout claude/fa-gaps && git pull --rebase origin claude/fa-gaps`, then follow **`INSTRUCTION_FILL_GAPS.md` PART 2 sections G, S, C** for the wave under "Current wave". |
| SON | phase 1 done, phase 2 not started | Print `Nothing for SON yet: start the FATHER session (Opus) first.` Stop. |
| SON | phase 2 done | Print `ALL WAVES DONE` + the status link. Stop. |
| FATHER | phase 1 NOT done | Phase 1 is a son job. If you can create sessions (claude-code-remote `create_session`), create ONE son for it (model Sonnet, repo `https://github.com/nguyenphanvantruong6969-arch/TESTING-DEV`, revision `claude/keen-ride-72sa7t`, prompt = the SON prompt in section 1 verbatim) and wait for it as in `INSTRUCTION_FILL_GAPS.md` F4-wait (check-ins with `send_later`, never `sleep`); when its `_sua_nho.md` report exists, continue with the next row. If you cannot create sessions: print `SON PROMPT READY: phase 1` and stop. |
| FATHER | phase 1 done, phase 2 not done | Follow **`INSTRUCTION_FILL_GAPS.md` PART 2 section F** from F0 (F1 creates `claude/fa-gaps` the first time). |
| FATHER | phase 2 done | Print `ALL WAVES DONE`, the status link and the draft PR link. Stop. |

### 2.2b. Role SOLO — one session does everything, no human input (Truong, 2026-11-10)
Use when the prompt says `act as SOLO`. Truong explicitly allows ONE session to play both roles for this job
(overrides `CLAUDE.md` rule 11 one-role-per-session for this job only). Never ask the human anything; never wait.
1. **Phase 1:** if not done, do the SON row for phase 1 (`LATEST_INSTRUCTION.md` PART 2). Do not stop after its report.
2. **Phase 2 setup:** do `INSTRUCTION_FILL_GAPS.md` F0–F1 (create `claude/fa-gaps`). Put `RUNNING-FATHER` and
   `RUNNING-SON` lock lines with your session; `son session: solo`.
3. **Loop per wave** (waves 1→4, then fix waves): F2 (write the wave spec, commit) → **switch hat** → S0–S4 (implement
   every item of the wave exactly as a son: tests first, one commit per item) → **switch hat** → F5 review.
   - Review with fresh eyes: re-read ONLY the spec block and `git diff <wave-start>..HEAD` (never your memory of
     writing it), rerun every test yourself, Chromium must really run, `kiem_nhanh --so-seed 20` 60/60, `soat-ma` 4 tiers.
   - NEEDS-FIX → fix wave (max 2 per wave, same loop) → 3rd failure BLOCKED. GO → next wave.
4. **Never ask.** A `WAIT-TRUONG` item: write the exact question in the status file "Waiting for Truong", mark it
   WAIT-TRUONG, continue with items that do not depend on it. A choice between technical options: take the safest one
   that keeps default behaviour byte-identical and record it in the status file.
5. **Never end your turn early.** Keep working until F7 (final report, `ALL WAVES DONE`, draft PR) is done. Long
   context is summarised automatically; before each wave, re-read the status file and the current spec block so the
   work never depends on chat memory (`INSTRUCTION_FILL_GAPS.md` C4). Commit + push after every item and every review.
6. **If the turn is about to end anyway** (tool budget, error, interruption): commit, push, update the status file
   with the exact next step, then try `send_later` (2 minutes, message `continue as SOLO from docs/phien/FA_GAPS_STATUS.md`).
   If that is refused, print `RESTART: paste the SOLO prompt again` and the status link.

### 2.3. Always
- Every stop: the last line of your message is a GitHub link (report, or `docs/phien/FA_GAPS_STATUS.md` on
  `claude/fa-gaps`).
- Context limits and clean stop: `INSTRUCTION_FILL_GAPS.md` section C (son ~300k, father ~400k tokens).
- If this file and an instruction file disagree on WHAT to build, the instruction file wins; on WHICH file to run,
  this file wins.
