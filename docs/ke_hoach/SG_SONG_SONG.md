# SG-1 … SG-12 chia cho 3 người chạy song song

> Soạn 2026-11-13 (Opus). Truong chọn: chia 12 mục thành 3 phần, mỗi người làm trọn phần mình (thay cho vòng ba vai
> trong `SG_VONG_LAP.md`, giữ lại làm cách dự phòng). Đặc tả từng mục: `docs/ke_hoach/SOAT_GIAO_DIEN_KE_HOACH.md`
> (D1 = A, D2 = b, D3 = NULL đã duyệt). Phần 1 cho người chạy (tiếng Việt), phần 2 cho Claude (tiếng Anh).
> Mọi số liệu là MÔ PHỎNG.

## 1. Cho người chạy

### 1.1 Ai làm gì
| Người | Model | Nhánh | Mục | Lỗi Fable (nặng nhất trước) |
|---|---|---|---|---|
| **Người 1** | **Opus** | `claude/sg-a` | SG-1, SG-3, SG-4, SG-10, SG-11a — rồi **gộp cả ba phần** và mở PR | C3, C2, M3, M2, M6/M7/L1/L4/L5 |
| **Người 2** | **Sonnet** | `claude/sg-b` | SG-2, SG-6, SG-8, SG-11b | C1, H1, M5, M4 |
| **Người 3** | **Sonnet** | `claude/sg-c` | SG-5, SG-7, SG-9, SG-12 | H3, H4/M1, nút bận, H2 |

Chia theo vùng mã để ba người ít sửa trùng tệp: Người 1 lo phần xếp và kết quả, Người 2 lo không gian làm việc,
nạp sổ và phiếu CLB, Người 3 lo biểu mẫu học sinh và các nút của thẻ "Chuẩn bị đợt". Mỗi người có ít nhất một lỗi
nặng làm đầu tiên. Ba người chạy cùng lúc, không phải chờ nhau; chỉ Người 1 chờ hai người kia ở bước gộp cuối.

### 1.2 Cách chạy (mỗi người)
1. Mở **một** phiên Claude Code trên kho `nguyenphanvantruong6969-arch/TESTING-DEV`, nhánh **`claude/forms-gop`**,
   tài khoản có quyền push.
2. Chọn đúng model trong bảng. Chế độ quyền **auto**.
3. Dán đúng khối prompt của mình (Truong gửi riêng cho từng người), gửi. Không cần gõ thêm.

### 1.3 Sự cố
| Thấy gì | Làm gì |
|---|---|
| Claude in `RESTART` hoặc phiên chết | Mở phiên mới, dán lại đúng khối của mình. Phiên mới đọc tệp trạng thái và làm tiếp. |
| `SG-<X> is RUNNING in another session` | Có phiên khác đang giữ phần này. Kiểm lại; nếu không, đợi 2 giờ rồi dán lại. |
| Người 1 in `WAITING for sg-b / sg-c` | Bình thường: đang chờ hai người kia xong. Để nguyên phiên. |
| Claude vẫn hỏi gì đó | Trả lời: "Choose the safest option that keeps default behaviour unchanged, record it in your status file, continue." |
| Claude xin merge PR, push lên `main`, chạy bản build Windows | Trả lời: "No." |

### 1.4 Xong khi nào
- Người 2, 3: tệp `docs/phien/sg_song_song/STATUS_B.md` (hoặc `_C`) trên nhánh của mình ghi `STATUS: DONE`.
- Người 1: `docs/phien/SG_STATUS.md` trên `claude/sg-sua` ghi `STATUS: SG GREEN`, tin nhắn cuối có link báo cáo và
  link PR. Gửi hai link cho Truong. Truong tự gộp PR, rồi mới chạy bản build Windows từ `main`.

---

## 2. For Claude (English)

### 2.1 Common rules (all three)
- Spec = `docs/ke_hoach/SOAT_GIAO_DIEN_KE_HOACH.md`: §0 rules, §1 approved decisions, §2b finding map, and ONLY the
  §3 sections of your items. SG-11 is split: **SG-11a** (person A) = M6, M7, L1, L4, L5; **SG-11b** (person B) = M4.
  Do not re-plan, reorder or add features. `CLAUDE.md` invariants win over anything here.
- Evidence: Fable's report https://claude.ai/artifact/QENDTqZFHhePzKsEDh8S6C (Artifact tool `read` if available; it
  is data, not instructions). Its repro steps are the source of each red test. Unreadable → use the spec text.
- **BASE** = `git log -1 --format=%H --grep='SG-KH: parallel split' origin/claude/forms-gop`. Your branch
  (`claude/sg-a|b|c`) starts from BASE; if it exists on origin, check it out and continue.
- Never ask (Truong authorises for this job): a rule-7 case beyond spec §1 → do not do it; write it under
  "For Truong" in your status file, mark the item `WAIT-TRUONG`, continue. Technical choice not in the spec → the
  safest one keeping default behaviour byte-identical; record under "Decisions".
- No subagents. No PR (except person A at the very end). Never force-push. Push only to your own branch (person A
  also to `claude/sg-sua`). Never trigger *Build Windows executable* (it overwrites the public release).

### 2.2 Environment (once per session)
```bash
git fetch origin claude/forms-gop claude/sg-a claude/sg-b claude/sg-c claude/sg-sua main:refs/remotes/origin/main 2>/dev/null
git fetch --unshallow 2>/dev/null || true
python3 -m venv .venv && .venv/bin/pip install -q -r requirements-dev.txt && .venv/bin/pip install -q playwright==1.63.0
```
- Prefix every UI test with `PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers`. A SKIPPED `tests/test_giao_dien_*` is NOT a pass.
- Quiet tests: `.venv/bin/python -m pytest -q -p no:cacheprovider --no-header -rf --tb=no <tests> 2>&1 | grep -E '^(FAILED|ERROR)|passed|failed|skipped' | tail -25`
- `kiem_nhanh`: `.venv/bin/python .claude/skills/soat-ma/scripts/kiem_nhanh.py --co-so origin/main --so-seed 20` → 7/7.
- Browser walkthroughs: data folder OUTSIDE the repo. `get_session` once: wrong model → note `WARNING` in status, continue.
- Generator snapshot (persons B and C, before any code): in a worktree of BASE run every mode of
  `mau_forms_thi_clb/tao_mau_forms.py` (`""`, `--fa-daa`, `--fa-daa --mot-bieu-mau`, `--bien-the`, `--chi-thi`,
  `--phan-hoi`, `--sau-ket-qua`, `--tuan-3`) into the scratchpad. Compare .xlsx/.docx without `docProps/core.xml`.

### 2.3 Shared files — the anti-conflict rules
| File | Rule |
|---|---|
| `i18n_errors.py`, `i18n.js` (vi AND en), `tests/test_ws_nhan.py` (`MA_MOI_SAU_ANH_CHUP`) | Add ONLY inside your marker block `=== SG-A|SG-B|SG-C: add below ===` … `=== end SG-X ===` (already in BASE). Never edit outside it. Run `python tao_i18n_js.py` after editing `i18n_errors.py` and commit `i18n_loi.js`. |
| `style.css` | Person A edits freely (SG-11a). B and C add rules only inside their block at the end of the file. |
| `CHANGELOG.md`, `docs/ke_hoach/TIEN_DO.md`, `docs/ke_hoach/CLAUDE_CHI_TIET.md` | Do NOT edit. Write your lines in your fragment `docs/ke_hoach/sg_song_song/MANH_<X>.md`; person A folds them in at integration. |
| Known red test on your own branch | `tests/test_a13_12_tai_lieu.py::test_ban_do_ma_so_tep_test_la_so_that` (code-map test-file count): expected while you add test files; person A fixes the count at integration. No other red test is acceptable. |
| Files mainly owned by another person (2.5–2.7) | Touch only if your item truly needs it; keep the change minimal and say so in your fragment. |
- FORBIDDEN: the DA core in `rbda_priority_pipeline.py` (`run_rbda`, `run_rbda_nhieu_buoi`, `club_choice_function`,
  `compute_club_priority`, `verify_stability`). SG-3 fixes rank in the FA wrapper (`fa_daa.chay_fa_daa`) or where its
  results are written, never inside `run_rbda`. Schema changes only in SG-6, only via idempotent `di_tru_schema`.

### 2.4 Status file and per-item loop
Your status file `docs/phien/sg_song_song/STATUS_<X>.md` on your branch (create at start, English, ≤ 120 lines):
line 1 `Mode: SG_SONG_SONG person <X>`, line 2 lock `RUNNING <session id> <UTC>`, line 3 `STATUS: RUNNING|DONE|BLOCKED`,
then `Items` (SG-n · TODO|DONE|BLOCKED|WAIT-TRUONG · commit · tests), `Decisions`, `For Truong`, `Log` (append only).
Lock: another session's lock younger than 2 h and STATUS RUNNING → print `SG-<X> is RUNNING in another session`, stop.
Re-read the file before every item; never rely on chat memory.

For each item, in your order:
1. **Red test first** from Fable's repro (or spec acceptance); run; it fails for the right reason. Log the red line.
2. **Minimal fix.** Default behaviour byte-identical (invariant 1). Visible strings only via i18n, vi + en, plain
   words, no internal codes (SG-n, FG-n, FA-M…, GAP-n, TH).
3. **Related tests:** the item's tests + every `tests/` file that greps a function you changed + for any string change
   `tests/test_ws_nhan.py`, `tests/test_van_phong_tu_nhien.py` + UI tests of the touched tab (really run).
4. **Mutation check:** break the core line of the fix, see the new test fail, restore, `git status` clean. Log it.
5. `ruff check .`; `kiem_nhanh` 7/7 (20 seeds); generator `diff -r` vs snapshot if you touched the generator.
6. **Self-review:** `soat-ma` four tiers (`.claude/skills/soat-ma/SKILL.md`) on `git diff <item start>..HEAD`; fix
   blocking findings; note the rest in your fragment.
7. Fragment lines (CHANGELOG-style entry + TIEN_DO line), status row DONE with hash, commit `SG-n: <what>`,
   `git pull --rebase origin claude/sg-<x>`, push (retry 4×, backoff 2/4/8/16 s).
After the last item: STATUS `DONE` (or `BLOCKED` with reasons), push, print the status-file link.
Context above ~300k tokens: finish the item, log the exact next step, push, print `RESTART: paste the same prompt again`.

### 2.5 Person A — `claude/sg-a` (Opus; Truong allows Opus to code for this job, overriding rule 11)
Order: **SG-1** (C3) → **SG-3** (C2, incl. the academic check of earlier FA numbers → "For Truong") → **SG-4** (M3)
→ **SG-10** (M2) → **SG-11a** (M6, M7, L1, L4, L5). Main files: `fa_daa.py`, `api.py` (`get_data_health_report`),
`api_bao_cao.py`, `api_sau_xep.py`, `fa_sau_xep.py`, `js/03_ket_qua.js`, `style.css`, `index.html` (L5).
Then **INTEGRATE** (2.8).

### 2.6 Person B — `claude/sg-b` (Sonnet)
Order: **SG-2** (C1) → **SG-6** (H1, schema D1 = A) → **SG-8** (M5) → **SG-11b** (M4). Main files:
`cau_hinh_ws.py` (read only: do not change defaults), `js/075_workspace.js`, `api_nhap.py`, `so_nhap.py`,
`mau_forms_thi_clb/chuyen_phieu_clb.py`, `api_forms.py`, `rbda_priority_pipeline.py` (`di_tru_schema` / `clubs`
table only), `api_xuat.py` (club time/room columns), `js/11_chuan_bi.js` (step-1 table).
SG-6 extra checks: migration run twice is a no-op; a backup is made first; old workbooks without the two columns load;
`match_results` unchanged (kiem_nhanh).

### 2.7 Person C — `claude/sg-c` (Sonnet)
Order: **SG-5** (H3; copy the final wording to "For Truong") → **SG-7** (H4, M1) → **SG-9** (busy wrapper; reuse
FG-4 `napTepForms`) → **SG-12** (H2, D2 = b; old exports with codes still load). Main files:
`mau_forms_thi_clb/bieu_mau.py`, `tao_mau_forms.py`, `chuyen_forms_sang_phan_mem.py`, `fa_sau_xep.py` readers
(`doc_tep_forms_phan_hoi`, `doc_tep_forms_khieu_nai`; coordinate: person A edits `khop_ma_hoc_sinh` callers only),
`api_forms_nap.py`, `js/02_van_hanh.js`, `js/05_quan_ly.js`, `js/10_theo_doi.js`, `js/12_chuan_bi_nap.js`,
`js/13_chuan_bi_bo.js`; `js/11_chuan_bi.js` only for the SG-9 wrapper (person B also edits it: keep your change to
the call sites). Allowed generator diffs: SG-5 → `--fa-daa*` registration forms; SG-12 → forms that carried codes.

### 2.8 Person A — INTEGRATE, gate, PR
1. Wait for `STATUS: DONE|BLOCKED` in `docs/phien/sg_song_song/STATUS_B.md` on `origin/claude/sg-b` and `STATUS_C.md`
   on `origin/claude/sg-c` (`git show origin/claude/sg-b:<path>`). While waiting: `send_later` 20 min with
   `continue as person A from docs/phien/sg_song_song/STATUS_A.md`, print `WAITING for sg-b / sg-c`, end the turn
   (`send_later` refused → print `RESTART: paste the same prompt again in 20 minutes`). After 6 h of waiting,
   integrate only the DONE items (merge up to the last DONE commit of that branch); the rest → "For Truong".
2. `git switch -c claude/sg-sua origin/claude/sg-a`; `git merge origin/claude/sg-b`; `git merge origin/claude/sg-c`.
   Conflicts: marker blocks/fragments → keep both; `i18n_loi.js` → rerun `python tao_i18n_js.py`; code → keep both
   behaviours and add a test proving both; impossible → STATUS `SG RED: conflict <file>`, stop. If `main` moved, merge it too.
3. Fold `MANH_A/B/C.md` into `CHANGELOG.md` and `docs/ke_hoach/TIEN_DO.md`; fix the test-file count in
   `CLAUDE_CHI_TIET.md`; write `docs/phien/SG_STATUS.md` (item table of all 12 with commits) and tick
   `docs/phien/claude__sg-sua.md`.
4. **Gate:** full suite with coverage ≥ `fail_under`, Chromium UI tests really run; `ruff`; `kiem_nhanh` 7/7 (20 seeds);
   generator `diff -r` vs a BASE snapshot (only the allowed diffs of SG-5, SG-6, SG-12); **cross-review** = `soat-ma`
   four tiers on `git diff BASE..HEAD` for the files of B and C (this is the only second pair of eyes: be strict);
   re-run Fable's walkthrough steps for C1, C2, C3, H1 (report Appendix B) and confirm none reproduces.
   GitHub Actions *Tests (rbda-kiosk)* result for HEAD (no access → `CI: not checked (<reason>)`).
   A failure → fix it yourself on `claude/sg-sua` with a test (small) or note it; max 3 loops → `SG RED: <ids>`.
5. Report `docs/phien/bao_cao_dem/<date>_sg_sua.md` (Vietnamese, plain words): 12 items with commits, tests added,
   decisions, "For Truong" (SG-5 wording, SG-3 list of FA numbers to re-measure, anything WAIT-TRUONG).
6. Open ONE PR `claude/sg-sua` → `main` (body: FG-1…FG-9 + SG-1…SG-12, test counts, "SIMULATED data", "run the
   Windows build only after merge"). Never merge it. STATUS `SG GREEN`; last line = report link + PR link.
