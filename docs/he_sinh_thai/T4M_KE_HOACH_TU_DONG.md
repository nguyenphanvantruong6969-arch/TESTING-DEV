# T4M. Kế hoạch tự chạy (không cần Truong nhập liệu) — 06/11/2026

Mã việc: **T4M-NC**. Truong duyệt 06/11/2026: (1) gói tiếng Nhật: **thiết kế ngay, viết mã chờ duyệt**; (2) viết **nháp v0** `T4M_MICROSOFT.md` theo dự phòng A; (3) **tự chạy chuỗi**, chỉ dừng khi chạm bất biến; (4) **đo mô phỏng**, chỉ bảng số, không diễn giải.

Người điều phối: phiên Opus của nhánh (phiên gốc). Mỗi bước là **một phiên riêng** (quy tắc 11), không dùng subagent (quy tắc 10). Mọi phiên đọc `CLAUDE.md` rồi `docs/phien/claude__upbeat-shannon-g5nnms.md` trước.

## 1. Chuỗi bước

| Bước | Mã | Ai | Phụ thuộc | Đầu ra | Nhận khi |
|---|---|---|---|---|---|
| S0 | T4M-DEMO | Sonnet | — (đang chạy) | `du_lieu_test/demo_t4m.py`, bộ sinh bài thi giả, test | Test đạt; điều phối soát |
| S1 | T4M-VH | Sonnet | S0 | `docs/he_sinh_thai/T4M_VAN_HANH_MOT_DOT.md` | Đủ 8 bước của một đợt, mỗi bước có lệnh và chỗ kiểm |
| S2 | T4M-GOI-TK | Opus | — | `docs/he_sinh_thai/T4M_GOI_THIET_KE.md` | Có phân tích bất biến 1, 2, 3, 8 và `kiem_nhan`; KHÔNG có mã |
| S3 | T4M-GD4-V0 | Opus | S2 | `docs/he_sinh_thai/T4M_MICROSOFT.md` (v0) | Đủ 9 mục của P2; mọi điểm phụ thuộc trường mang nhãn HỎI-IT |
| S4 | T4M-DO | Sonnet | S0 | `du_lieu_test/do_t4m_thi.py`, `du_lieu_test/ket_qua_t4m/`, `docs/he_sinh_thai/T4M_DO_MO_PHONG.md` | Bảng số 3 bộ × 20 seed, nhãn MÔ PHỎNG, không câu nhận xét nào |

Song song được: S0 với S2; S1 với S4 (sau S0). Sau S3 và S4: dừng, báo Truong, chờ GĐ2.

## 2. Luật dừng (mọi bước)

Dừng, ghi vào tệp bàn giao, báo điều phối khi: bất biến xung đột với việc; cần thư viện mới; phải đổi hợp đồng CSV hoặc schema; phải sửa lõi (`run_rbda`, `compute_club_priority`, `club_choice_function`); test cũ đỏ mà không rõ lý do. Không bao giờ ghi dữ liệu thật, tenantId, URL app, tên người.

## 3. Luật chung khi kết thúc (mọi bước)

Đánh dấu dòng của mình trong Plan của tệp bàn giao, ghi đè "Current state" phần của mình, **thêm** một dòng Session log; một mục `CHANGELOG.md`; dòng T4M-NC trong `TIEN_DO.md`; chỉ chạy test liên quan + `ruff`; `git fetch origin main` rồi `python .claude/skills/soat-ma/scripts/kiem_nhanh.py`; `git pull --rebase` (xung đột ở CHANGELOG / tệp bàn giao: giữ cả hai bên); commit, push vào `claude/upbeat-shannon-g5nnms`. Báo cáo tiếng Việt, tối đa 10 dòng.

**Báo trạng thái về điều phối (Truong yêu cầu 06/11/2026):** xong bước, hoặc gặp luật dừng mục 2, thì báo ngay:
1. Nếu có công cụ `send_message` (claude-code-remote): gửi tới phiên gốc `session_01YVAyu14xCxoLe4ArvejR4i` (từ vòng 5; vòng 4 là `session_01YVAyu44juJNZ7h3oUwVHfW`, vòng 1–3 là `session_01YVAyu3Zzm2AEVFAPhazqHY`), tối đa 8 dòng: `DONE` hoặc `BLOCKED`, mã commit, kết quả test, quyết định cần Truong duyệt; với `BLOCKED` thì ghi câu hỏi chính xác cho Truong và các phương án.
2. Dù có công cụ hay không: ghi cùng khối đó vào tệp bàn giao, mục "Current state", dạng `STATUS <mã>: …`, rồi push.
3. Không chờ Truong trả lời trong phiên con; báo xong thì dừng.

## 4. Vòng điều phối

1. Phiên gốc hẹn tự kiểm (send_later) khoảng 40 phút một lần.
2. Mỗi lần, hoặc ngay khi nhận tin `DONE` / `BLOCKED` từ phiên con: đọc các dòng `STATUS` trong tệp bàn giao, xem trạng thái các phiên con; phiên nào xong thì **soát** (kéo nhánh, chạy test liên quan, so chế độ mặc định không đổi, đọc tài liệu theo "Nhận khi"); đạt thì mở bước kế; không đạt thì gửi phiên đó danh sách sửa.
3. Có `BLOCKED` cần Truong: phiên gốc hỏi Truong ngay (câu hỏi có phương án), không tự quyết thay.
4. Hết chuỗi: cập nhật tệp bàn giao, báo Truong tóm tắt và các quyết định chờ duyệt (mã gói, bảng đo).

## 5. Prompt

### S1. T4M-VH — Vận hành một đợt (Sonnet, chỉ tài liệu)
```
T4M-VH (Sonnet). Follow docs/he_sinh_thai/T4M_KE_HOACH_TU_DONG.md §2-3.
Read: T4M_KET_QUA_TAI_LIEU.md §5 and §7.4-7.5; T4M_HUONG_DAN_THU.md (headings, then the export and Teams parts);
mau_forms_thi_clb/README.md (quiz-only and "Chạy thử trọn chuỗi"); du_lieu_test/demo_t4m.py --help.
Write docs/he_sinh_thai/T4M_VAN_HANH_MOT_DOT.md in Vietnamese for the school IT staff: one allocation round, end to end,
8 steps: (1) teachers build quizzes (de_thi.json -> tao_mau_forms.py --chi-thi -> Quick Import -> CAI_DAT_FORMS_CHI_THI.md);
(2) open/close registration in the ECA app and the quiz form (dates); (3) lock; (4) export the List (Export to CSV) and
the quiz results (Open in Excel); (5) run the converter --chi-thi --lists, read every warning; (6) import the Sổ nhập
into the kiosk, one workspace per campus, run, read sanity/verify; (7) export per homeroom (export_theo_lop) and send via
Teams/Outlook (optional flow per T4M_HUONG_DAN_THU.md); (8) late arrivals / withdrawals: rerun, STB stays locked (inv. 3).
Each step: exact command or click path, what to check, what to do if it fails, which file to keep and where (privacy:
data stays on the IT machine; delete after the period the school sets — HỎI-IT). Max 150 lines. Label untested parts TH.
No code changes.
```

### S2. T4M-GOI-TK — Thiết kế gói nhiều buổi (Opus, chỉ tài liệu)
```
T4M-GOI-TK (Opus). Follow docs/he_sinh_thai/T4M_KE_HOACH_TU_DONG.md §2-3. DESIGN ONLY: no code (Truong 06/11/2026).
Read: T4M_KE_HOACH_NGHIEN_CUU.md §1 (bundle bullets); docs/KE_HOACH_NHIEU_BUOI.md §2 and §5; SO_DANG_KY_33_MUC.md
items A3, A7, A11, A12, G3 (only their sections); grep -n "^def run_rbda_nhieu_buoi\|^def run_full_pipeline" and read
those signatures; so_nhap.py sheet "1. CLB" reader (grep "Buổi").
Write docs/he_sinh_thai/T4M_GOI_THIET_KE.md:
1. Problem: a bundle = one club occupying a fixed set of days (e.g. 3A = thu_2+thu_4+thu_5); level = eligibility set by
   the school; max one bundle per student; year-committed seats.
2. Design: a two-phase ORCHESTRATOR above the existing pipeline (no change to run_rbda / compute_club_priority /
   club_choice_function). Phase 1: DA over bundles as one pseudo-session (eligibility filter by level, same STB,
   Tầng 1/2 as usual); phase 2: remove the bundle's days for assigned students, then the normal per-day run.
   Compare at least one alternative (e.g. bundle as a day-1 club with linked seats) and say why rejected.
3. Guarantees: stability/strategy-proofness hold within each phase only; label exactly "bảo đảm trong từng pha, không
   bảo đảm ổn định toàn tuần khi có gói" (inv. 8, measurement mode as in A12). Give a small counter-example of a
   week-level blocking pair. No bundles => byte-identical results (inv. 1): explain why the orchestrator is the identity.
   Year-committed seats reduce quota only (inv. 2). STB: one lottery for both phases (inv. 3).
4. Data: how a bundle is represented (Sổ nhập column, workspace config) and whether the CSV contract changes; if it
   must change, say so as a decision for Truong (rule 7) and propose the minimal, backward-compatible form.
5. Proposed item code(s) with kiem_nhan (tests first), files, risks, size estimate (labelled estimate).
6. Open questions for the ECA teacher (levels, quotas per level, other bundles).
Max 200 lines. Report: decisions Truong must approve.
```

### S3. T4M-GD4-V0 — Nháp kiến trúc (Opus, chỉ tài liệu)
```
T4M-GD4-V0 (Opus). Prompt P2 of docs/he_sinh_thai/T4M_KE_HOACH_NGHIEN_CUU.md §8, run under fallback A (plan §5):
there is NO interview summary yet; every school-dependent point is HỎI-IT and, where it changes the design, give two
branches (store = SharePoint List / store = Dataverse). Follow T4M_KE_HOACH_TU_DONG.md §2-3.
Read additionally: T4M_KET_QUA_TAI_LIEU.md (all), T4M_GOI_THIET_KE.md (for P2 item 5: summarise and link, do not
duplicate), T4M_VAN_HANH_MOT_DOT.md if it exists, T4M_DO_MO_PHONG.md if it exists (cite tables, no interpretation).
Write docs/he_sinh_thai/T4M_MICROSOFT.md marked "Bản nháp v0 — chưa có kết quả phỏng vấn (GĐ2)" at the top, with the 9
items of P2. Item 9 (T4-K2): present options only; Truong decides. Report: what must be revisited after GĐ2.
```

### S4. T4M-DO — Đo mô phỏng (Sonnet)
```
T4M-DO (Sonnet). Follow docs/he_sinh_thai/T4M_KE_HOACH_TU_DONG.md §2-3. Academic integrity (CLAUDE.md): numbers are
SIMULATED; write NO commentary, interpretation or conclusion — tables and method only; log the AI help in the project's
AI log (find it with grep -ril "nhật ký ai\|AI log" docs).
Read: du_lieu_test/demo_t4m.py; CLAUDE_CHI_TIET.md § "Kiểm verify nhanh"; existing du_lieu_test/ measurement scripts
(pick one as the style model).
Build du_lieu_test/do_t4m_thi.py: 3 fake datasets (e.g. 120 / 500 / 1,500 students, fixed generator seeds) × 20 STB
seeds × 2 conditions: (A) no quizzes (all Tầng 2), (B) quiz clubs as in de_thi.json (Tầng 1). Metrics per run: share
placed in 1st / top-3 choice per day, unassigned per day, share of Tầng 1 seats won by top-score students, verify
result (blocking pairs must be 0; report the count), run time. Output CSV in du_lieu_test/ket_qua_t4m/ and
docs/he_sinh_thai/T4M_DO_MO_PHONG.md (method, parameters, tables with mean / min / max, label "MÔ PHỎNG" in every
table title, the exact command to reproduce). Test: tests/test_do_t4m_thi.py (deterministic for fixed seeds; condition
A equals the plain pipeline byte-for-byte on one small case). Do not change product code.
```

## 6. Vòng 2 (Truong duyệt 06/11/2026)

Quyết định của Truong ngày 06/11/2026:
- Gói tiếng Nhật: **duyệt nguyên tắc D1–D5** của `T4M_GOI_THIET_KE.md`; mã A8-GOI-1..3 **chỉ viết sau khi giáo viên ECA trả lời Q1–Q3**.
- Duyệt **T4M-M1, T4M-M3, T4M-M4**. T4M-M2 chờ tệp xuất mẫu thật (GĐ2).
- T4-K2: **K2-b, giữ tạm dừng**.
- Chạy vòng 2 theo cùng luật §2–§4.

| Bước | Mã | Ai | Đầu ra | Nhận khi |
|---|---|---|---|---|
| R1 | T4M-M1 | Sonnet | `docs/he_sinh_thai/T4M_DAC_TA_SUA_APP.md` | Mỗi yêu cầu có một dòng kiểm pass/fail; chỉ dùng phép lọc ủy quyền được (KQ NC-04); không đụng app thật |
| R2 | T4M-M3 | Sonnet | Công cụ đối chiếu hai lần xuất List + test | `kiem_nhan` ở `T4M_MICROSOFT.md` §8; không đổi kiosk |
| R3 | T4M-M4 | Sonnet | `docs/he_sinh_thai/T4M_FLOW_GUI_GVCN.md` | Đủ giới hạn ĐXM NC-12, NC-13; connector chuẩn; tài khoản dịch vụ; không ghi ngược về list |

### R1. T4M-M1
```
T4M-M1 (Sonnet), docs only. Follow T4M_KE_HOACH_TU_DONG.md §2-3 (incl. DONE/BLOCKED report).
Read: T4M_MICROSOFT.md §2 cell A and §8 row M1; T4M_HUONG_DAN_THU.md (canvas screens, §9 checklist);
T4M_KET_QUA_TAI_LIEU.md NC-04, NC-05/06, NC-21; T4M_KE_HOACH_NGHIEN_CUU.md §1 (current app screens).
Write docs/he_sinh_thai/T4M_DAC_TA_SUA_APP.md for whoever edits the ECA app (IT): change list from today's app
(one pick per weekday) to Top 3 per day: data columns (wide model, NV1..NV3, TrangThai), screen behaviour
(no duplicates, empty day valid, bilingual labels, mobile), Patch + IfError, lock by TrangThai, delegable filters
only, version backup/restore steps (NC-21), and a numbered requirement table with one pass/fail check each.
Bundle screen: placeholder section "chờ A8-GOI" only. Label every formula GĐ (untested). Max 160 lines.
```

### R2. T4M-M3
```
T4M-M3 (Sonnet). Follow T4M_KE_HOACH_TU_DONG.md §2-3 (incl. DONE/BLOCKED report). Tests first (rule 2).
Read: T4M_MICROSOFT.md §6 and §8 row M3; T4M_VAN_HANH_MOT_DOT.md step 8; mau_forms_thi_clb/
chuyen_forms_sang_phan_mem.py doc_lists (reuse its parsing, do not duplicate); du_lieu_test/sinh_xuat_lists_gia.py.
Build a CLI next to the converter (e.g. mau_forms_thi_clb/doi_chieu_lists.py OLD.csv NEW.csv [--co-so CS1]
[--ra report.xlsx]) listing: new students, withdrawn students, rows whose NV1..NV3 / Lop / CoSo changed, keyed on
lowercased Email + Thu. kiem_nhan: identical files -> empty report; add/remove/edit one row -> exactly one entry of
the right kind; email case differences are not changes; kiosk untouched. Add a short section to
T4M_VAN_HANH_MOT_DOT.md step 8. Run related tests + ruff.
```

### R3. T4M-M4
```
T4M-M4 (Sonnet), docs only. Follow T4M_KE_HOACH_TU_DONG.md §2-3 (incl. DONE/BLOCKED report).
Read: T4M_KET_QUA_TAI_LIEU.md NC-11, NC-12, NC-13, NC-14; T4M_HUONG_DAN_THU.md (Teams/flow part);
T4M_VAN_HANH_MOT_DOT.md step 7; grep export_theo_lop to learn the output file names.
Write docs/he_sinh_thai/T4M_FLOW_GUI_GVCN.md: an optional Power Automate flow (standard connectors only) owned by an
IT service account that takes the per-homeroom Excel files from a SharePoint library and sends each homeroom
teacher their file via Outlook or Teams; mapping file homeroom -> teacher email (source HỎI-IT, NC-08); limits
with labels (ĐXM figures from KQ); failure handling and a manual fallback; DLP note (NC-14). No write-back to the
list (NC-13). Label untested steps TH. Max 120 lines.
```

## 7. Vòng 3: cổng thi (Truong duyệt 06/11/2026)

Truong duyệt **Q4a, Q4b, Q4c, M5** của `T4M_CONG_THI.md`. Trả điểm cho học sinh theo **mức 5a**: giáo viên bấm Post scores trong Forms; app không hiện điểm. Điểm dùng để xếp vẫn do bộ chuyển đổi chấm lại. Luật §2–§4 giữ nguyên.

| Bước | Mã | Ai | Đầu ra | Nhận khi |
|---|---|---|---|---|
| C1 | T4M-Q4a, Q4b, Q4c (tuần tự, một phiên) | Sonnet | `tao_mau_forms.py --moi-clb`, `CLB.csv`; bộ chuyển đổi nhận mỗi tệp một CLB; `--bai-thi` đối chiếu | `kiem_nhan` ở `T4M_CONG_THI.md` §6; chế độ cũ trùng khít |
| C2 | T4M-M5 | Sonnet | Màn "Thi tuyển" bổ sung vào `T4M_DAC_TA_SUA_APP.md`; `docs/he_sinh_thai/T4M_FLOW_DA_LAM.md` | Mỗi yêu cầu có một dòng kiểm pass/fail; chỉ connector chuẩn; lọc `=`; mức 5a |

### C1. T4M-Q4a/b/c
```
T4M-Q4a, Q4b, Q4c in this order (Sonnet). Follow T4M_KE_HOACH_TU_DONG.md §2-3 (incl. DONE/BLOCKED report).
Tests first (rule 2). Read: T4M_CONG_THI.md (all, short); mau_forms_thi_clb/README.md quiz-only part; functions you
change in tao_mau_forms.py, bieu_mau.py, chuyen_forms_sang_phan_mem.py (grep -n "^def"); tests/test_t4m_chi_thi.py.
Q4a: tao_mau_forms.py --moi-clb writes one Quick Import .docx per club that has de_thi (no gate question; tags
[clb_x-k] kept; settings note: Record name, One response per person, Show results OFF, timer optional) and
CLB.csv (ClubId, Ten, Buoi, FormUrl empty) for "Create a list based on a spreadsheet". Regeneration identical.
Q4b: the --chi-thi converter accepts N exports where each export holds ONE club's quiz (detect club by tags; an
export mixing clubs or an unknown tag stops with a clear error). Same fake data as one shared form => same
SO_NHAP_CLB.xlsx. A student missing from a club's export simply has no score for that club.
Q4c: optional --bai-thi BaiThi.csv (Email, ClubId, ResponseId, NopLuc): report rows in BaiThi without a matching
export row and export rows without a BaiThi row; all matched => empty section. Never changes scores.
Default and existing --chi-thi behaviour unchanged (inv. 1). Extend du_lieu_test/demo_t4m.py with --moi-clb only if
cheap. Update mau_forms_thi_clb/README.md and T4M_VAN_HANH_MOT_DOT.md steps 1, 4, 5. Related tests + ruff.
```

### C2. T4M-M5
```
T4M-M5 (Sonnet), docs only. Follow T4M_KE_HOACH_TU_DONG.md §2-3 (incl. DONE/BLOCKED report).
Read: T4M_CONG_THI.md; T4M_DAC_TA_SUA_APP.md (structure, requirement table); T4M_FLOW_GUI_GVCN.md (style, limits);
T4M_KET_QUA_TAI_LIEU.md NC-04, NC-13, §7.1 (Forms connector, settings).
(1) Add a section "Màn Thi tuyển" to T4M_DAC_TA_SUA_APP.md: list of the student's chosen clubs that have a quiz
(from their NV rows), button Launch(FormUrl) shown only when no BaiThi row exists and registration is open, status
"Đã làm"/"Chưa làm", Refresh button, delegable filters only (Email = Lower(User().Email)), no score shown (level 5a:
"Xem điểm trong Forms sau khi giáo viên công bố"). Add requirement rows (continue numbering) with pass/fail checks.
(2) Write docs/he_sinh_thai/T4M_FLOW_DA_LAM.md: one template flow per quiz form (trigger When a new response is
submitted -> Get response details -> Create item in BaiThi), owned by the IT service account, how to clone it per
form, Form Id for group forms, request estimate (label estimate) vs 6,000/day, failure handling, manual fallback
(IT exports responses and the converter --bai-thi report). Label untested TH. Max 120 lines.
```

## 8. Vòng 4: Top 7, tick chọn thi, điểm quyết tâm (Truong duyệt 06/11/2026)

Truong quyết: (1) mỗi ngày **tối đa 7** nguyện vọng có xếp hạng (thay Top 3; số ô = min(7, số CLB của ngày)); (2) **tick chọn thi**, tối đa **5 CLB có thi mỗi ngày** (`TRAN_CLB_THI_MOI_BUOI`); chỉ CLB được tick mới hiện ở màn Thi tuyển; (3) **thu điểm quyết tâm trên app** (phương án b): mỗi ngày hai quỹ 100 điểm, quỹ 1 cho CLB đã tick thi, quỹ 2 cho CLB còn lại.

Kiosk đã hỗ trợ đủ, **không sửa lõi, schema, hợp đồng CSV**: Sổ nhập ô "Điểm thi" chữ `thi` = tick mà chưa có điểm; cột "Điểm quyết tâm" (`ghi_so_nhap(..., luon_co_cot_w=True)`, khoá `diem_w`); trần 5 (`so_nhap_qua_tran_thi`); tick mà vắng thì bỏ điểm quỹ 1 và cảnh báo (`diem_wharton_hieu_luc`, `wharton_vang_thi`). Luật §2–§4 giữ nguyên.

**Cột List (mô hình rộng, mỗi dòng một em × một ngày), cố định cho cả hai bước:** `NV1..NV7` (mã CLB), `THI1..THI7` (`Có` hoặc trống; `Có` chỉ hợp lệ khi CLB ở `NVk` có đề), `WP1..WP7` (số nguyên ≥ 0, trống = 0). Chỉ số k của ba nhóm đi cùng nhau.

| Bước | Mã | Ai | Đầu ra | Nhận khi |
|---|---|---|---|---|
| D1 | T4M-Q5a, Q5b, Q5c (tuần tự, một phiên) | Sonnet | bộ chuyển đổi đọc `THIk`, `WPk`; dữ liệu giả và demo `--day-du` | List không có `THIk`/`WPk` cho Sổ nhập và BANG_DIEM trùng khít như trước; test mới viết trước; kiosk nạp được sổ có điểm quyết tâm và chạy với `rules.wharton` bật |
| D2 | T4M-M6 | Sonnet | đặc tả app (Top 7, tick, màn điểm quyết tâm), màn Thi tuyển theo tick, phiếu phỏng vấn, HDT | Mỗi yêu cầu mới có dòng kiểm pass/fail; chỉ lọc `=`; không còn chữ "Top 3" lỗi thời trong các tệp được giao |

Chạy song song được (cột đã cố định ở trên). D1 chỉ sửa mã, test, `mau_forms_thi_clb/README.md`, `T4M_VAN_HANH_MOT_DOT.md`; D2 chỉ sửa các tệp tài liệu liệt kê trong prompt D2. Cả hai đều ghi CHANGELOG, TIEN_DO, tệp bàn giao: `git pull --rebase`, giữ cả hai bên, **không bao giờ commit dấu xung đột**.

### D1. T4M-Q5a/b/c
```
T4M-Q5a, Q5b, Q5c in this order (Sonnet). Follow T4M_KE_HOACH_TU_DONG.md §2-3 and §8 (columns are FIXED there).
Tests first (rule 2). Read: §8; so_nhap.py docstrings of ghi_so_nhap and the reader of "Điểm thi"/"thi"/diem_w
(grep -n); HUONG_DAN_SU_DUNG.md §14 (two funds); rbda_priority_pipeline.diem_wharton_hieu_luc docstring;
chuyen_forms_sang_phan_mem.py functions doc_lists, phan_tich_chi_thi, ghi_tep_phan_mem, ghi_bang_diem;
du_lieu_test/sinh_xuat_lists_gia.py, demo_t4m.py, tao_mau_forms.ghi_mau_xuat_chi_thi; tests test_t4m_chi_thi,
test_t4m_cong_thi, test_demo_t4m.
Q5a (tick): when THIk columns exist, "thi" in the Sổ nhập follows the tick: ticked + submission -> score; ticked, no
submission -> cell "thi" (absent); NOT ticked + submission -> score dropped (kept in BANG_DIEM, Nạp = Không) with a
warning; tick on a club without de_thi -> warning, tick ignored; more than 5 ticks in a day -> warning, keep the
first 5 in NV order. Only clubs ticked count for --bai-thi as before (report only).
Q5b (determination points): when WPk columns exist, write diem_w per NV and call ghi_so_nhap with luon_co_cot_w=True.
Pre-check per student-day: fund 1 = ticked clubs, fund 2 = the rest; each non-empty fund must sum to exactly 100;
non-integer / negative cell -> warning, cell left empty. Warn only (the kiosk blocks the run); never change values.
Q5c: sinh_xuat_lists_gia gains optional NV up to 7, THIk, WPk (valid funds, deterministic; defaults unchanged);
ghi_mau_xuat_chi_thi submits only for ticked clubs when ticks exist, plus planted cases: one ticked-but-absent,
one submitted-not-ticked, one fund not summing to 100. demo_t4m.py --day-du (combinable with --moi-clb) uses them,
turns rules.wharton ON in the temp DB, and the summary ALWAYS prints "Điểm quyết tâm: BẬT/TẮT".
Invariant: a List without THIk/WPk gives byte-identical SO_NHAP_CLB.xlsx and BANG_DIEM.xlsx (ignore docProps/core.xml)
vs before; existing tests unchanged. No core change (stop rule §2). Update README (quiz-only part), ops guide steps 4-5
and appendix. Related tests + ruff + mutation check of 3 key branches (rule: test must go red).
```

### D2. T4M-M6
```
T4M-M6 (Sonnet), docs only. Follow T4M_KE_HOACH_TU_DONG.md §2-3 and §8 (columns are FIXED there).
Files you may edit: T4M_DAC_TA_SUA_APP.md, T4M_CONG_THI.md, T4M_MICROSOFT.md, T4M_PHIEU_PHONG_VAN.md,
T4M_HUONG_DAN_THU.md (all in docs/he_sinh_thai/). Read HUONG_DAN_SU_DUNG.md §14 (two funds of 100) first.
(1) T4M_DAC_TA_SUA_APP.md: Top 3 -> up to 7 per day (dropdown count = min(7, clubs that day), no duplicates, no gap);
per NV row a tick "Thi" shown only for clubs with a quiz, max 5 ticks per day; a "Điểm quyết tâm" step per day with
two boxes (fund 1 ticked clubs, fund 2 the rest), live "Đã dùng X / 100" counters, save blocked unless every
non-empty fund is exactly 100; columns NV1..NV7, THI1..THI7, WP1..WP7; Patch + IfError as before; delegable `=`
filters only. §10 Thi tuyển: cards = TICKED clubs only (not every quiz club in NV). New requirement rows (continue
numbering after R24) with pass/fail checks; add matching HDT §9 rows and a short HDT section; replace outdated
"Top 3" text in the five files. (2) T4M_CONG_THI.md §1 flow and T4M_MICROSOFT.md (v0) data table: same changes.
(3) Interview sheet: rewrite ECA-9 for tick (max 5); add ECA questions: do teachers accept determination points
(two funds of 100 per day) and is the phone screen acceptable; how many clubs per day (to size the 7 dropdowns).
Label everything untested TH; no numbers presented as measured.
```

## 9. Vòng 5: bộ dựng sẵn cho IT, T4M-BK (Opus đề xuất, **Truong duyệt 06/11/2026**; K0 xong 06/11, kết quả `T4M_KET_QUA_TAI_LIEU.md` §8)

Đích: từ mô phỏng sang **hệ thống thật trên sản phẩm Microsoft**, do **IT và giáo viên ECA** dựng trên bản sao app (kế hoạch nghiên cứu §1: IT và giáo viên ECA quản lý app, IT chạy kiosk). Dự án không đụng tenant của trường; dự án giao **một thư mục "nhập là dựng"** cho IT, sinh bằng một lệnh, kiểm được trên máy không có Microsoft 365. Mọi thứ chạm Microsoft vẫn nhãn **TH** cho tới khi IT chạy (HDT §9).

Không sửa lõi, schema, hợp đồng CSV; không thư viện mới (chỉ thư viện chuẩn Python + `openpyxl`, `python-docx` đã có). Luật §2–§4 giữ nguyên.

**Quyết định kỹ thuật của Opus (ghi để phiên con không làm khác):**
1. **Một list CLB:** bộ dựng tạo list `CLB` với đúng các cột của `CLB.csv` (`ClubId`, `Ten`, `Buoi`, `FormUrl`, T4M-Q4a); công thức app lọc `Filter(CLB, Buoi = <ngày>)` thay cho `CLB_GIA` (`Buoi` dùng cùng chữ `Thứ 2`…`Thứ 6` như cột `Thu` của `ECA`; phiên con kiểm điều này bằng test). Chỉ tiêu không vào app (mục 0 của đặc tả app). Tài liệu cũ nói `CLB_GIA` được sửa trỏ về `CLB`.
2. **Một nguồn cột:** định nghĩa cột của mọi list (`ECA`, `CLB`, `BaiThi`, `NHAT_KY_DA_LAM`) nằm ở một mô-đun; test so khớp với `sinh_xuat_lists_gia.cot_csv(7, True, True)`, `doc_lists` và tiêu đề `CLB.csv`. Không sửa các hàm cũ.
3. **Không tự chế gói flow `.zip`** hay tệp `.msapp`: không kiểm được ở đây, sai định dạng thì IT mất công hơn. Flow giao dưới dạng bảng cấu hình theo từng CLB + biểu thức để dán; IT dựng một flow mẫu, xuất gói, nhân bản (`T4M_FLOW_DA_LAM.md` §4).
4. **Công thức Power Fx khai triển đủ** `NV1..NV7`, `THI1..THI7`, `WP1..WP7` (không còn `/* … đến NV7 */`), sinh bằng mã để không gõ tay sai chỉ số; kiểm tĩnh bằng test (chỉ lọc `=` trên nguồn dữ liệu; tên cột đúng hợp đồng §8).

| Bước | Mã | Ai | Đầu ra | Nhận khi |
|---|---|---|---|---|
| K0 | T4M-BK0 | Opus (phiên gốc, đọc web) | `T4M_KET_QUA_TAI_LIEU.md` §8: cách tạo list có cột định sẵn mà **không cần quyền quản trị tenant** (Lists "từ CSV/Excel"; site script `createSPList` qua REST `ExecuteTemplateScript` với quyền chủ site; PnP PowerShell và việc phải tự đăng ký ứng dụng Entra từ 09/2024; Graph); Power Apps Studio dán YAML điều khiển (có không, định dạng nào); nhập/xuất gói flow | Mỗi cách một dòng: quyền cần, có sẵn trong A3/A5 không, nhãn ĐXM với đường dẫn trang gốc; chọn cách mặc định và cách lui. Nếu không cách nào tạo cột tự động mà không cần quản trị: K1 chỉ sinh CSV + hướng dẫn tay |
| K1 | T4M-BK1, BK2 (tuần tự, một phiên) | Sonnet | `mau_forms_thi_clb/bo_dung_t4m/` (tên GĐ): mô-đun cột; bộ sinh list theo cách K0 chọn (+ CSV mẫu cho cách lui); bộ sinh công thức Power Fx từng màn (nguyện vọng, điểm quyết tâm, Thi tuyển, khoá) từ đặc tả §2, §3, §10, §11; test viết trước | Test: cột khớp ba nguồn ở quyết định 2; công thức đủ 7 chỉ số, không `<>`/`in`/`IsBlank`/`Not` trong `Filter` trên `ECA`, `BaiThi`, `CLB`; sinh lại giống hệt từng byte; mọi tệp có dòng "TH: chưa chạy trên Power Apps" |
| K2 | T4M-BK3, BK4 (tuần tự, một phiên, sau K1) | Sonnet | bảng cấu hình flow `DaLam_<ClubId>` sinh từ `de_thi.json`; lệnh gộp `tao_bo_dung_t4m.py` ra thư mục + `.zip` (`01_lists/`, `02_app/`, `03_flow/`, `04_forms/` gọi `tao_mau_forms.py --moi-clb`, `HUONG_DAN_IT.md`); hướng dẫn: thứ tự dựng, mỗi bước một dòng pass/fail trỏ về R1..R38 và HDT §9 | Một lệnh sinh đủ; số flow = số CLB có đề; mỗi `ClubId` của bảng flow có trong `CLB.csv`; không tên thật, tenantId, URL; `demo_t4m.py` và mọi đầu ra cũ trùng khít |
| K3 | soát | Opus | soát K1, K2 theo cột "Nhận khi"; cập nhật trang mô phỏng nếu cần; báo Truong | Test liên quan đạt, `ruff` sạch, `kiem_nhanh` 7/7 |

Phụ thuộc: K0 → K1 → K2 → K3 (K1 cần cách tạo list do K0 chọn). K0 chọn (KQ §8.4): list mặc định **B** (site template, chủ site áp), **A** nếu có app Entra cho PnP, lui **C** (Lists từ CSV + thêm cột tay); app = công thức theo thuộc tính, **không** YAML điều khiển; flow = dựng tay một mẫu rồi nhân bản bằng gói.

### K1. T4M-BK1, BK2
```
T4M-BK1 then T4M-BK2 (Sonnet), one session. Follow T4M_KE_HOACH_TU_DONG.md §2-3 and §9 (the 4 Opus decisions
there are fixed). Tests first (rule 2). Read: §9; T4M_KET_QUA_TAI_LIEU.md §8 (all of it); T4M_DAC_TA_SUA_APP.md
§1, §2, §3, §4, §5, §10, §11; T4M_FLOW_DA_LAM.md §2 (BaiThi, NHAT_KY_DA_LAM columns);
du_lieu_test/sinh_xuat_lists_gia.cot_csv; chuyen_forms_sang_phan_mem.doc_lists docstring; tao_mau_forms.ghi_clb_csv.
New package mau_forms_thi_clb/bo_dung_t4m/ (stdlib only: json, csv, uuid; no new library).
BK1 columns + lists: module cot_lists.py = ONE definition of lists ECA, CLB, BaiThi, NHAT_KY_DA_LAM (internal name,
display name, type Text/Number/DateTime/Choice with choices, required). ECA = cot_csv(7, True, True) minus SharePoint
system column `Created`; `HoTen` optional (keep, not required). CLB = exactly ghi_clb_csv header. Generators:
(a) site_script.json: createSPList (templateType 100) per list, addSPField for Text/Number/DateTime,
addSPFieldXml for Choice; every field a FIXED id = uuid5(NAMESPACE_URL, "rbda-t4m/<list>/<col>") and internalName =
contract name; prints the action count and warns when > 30 (sync limit) and fails when > 300 (KQ §8.1).
(b) CSV templates for way C: header + one example row whose values make Lists guess the right type (fake data only).
(c) KIEM_COT_ECA.md: checklist to add missing ECA columns by hand (name, type, choices), with "add only if absent".
BK2 Power Fx: generator writes one .txt per screen (NguyenVong, DiemQuyetTam, ThiTuyen, Khoa) listing
"Control.Property = formula", fully expanded for k = 1..7 (no "…" or "/* … */"), from spec §2, §3, §10.3, §11;
data-source filters use `=` only, Lower(User().Email); local filtering on collections as in spec §5; App.OnStart
part labelled "dán tay" (App Object cannot paste code, KQ §8.2). Every generated file starts with a line
"TH: chưa chạy trên Power Apps / SharePoint" and the source spec section. Byte-identical regeneration.
Tests (write first, see red): columns of ECA == cot_csv(7,True,True) minus Created; CLB == ghi_clb_csv header;
doc_lists reads a CSV with exactly the ECA columns (via sinh_xuat_lists_gia) without warnings; Buoi values of
CLB.csv == Thu values of the fake Lists; GUIDs stable and unique; JSON valid and every field's internalName in the
contract; action count printed; formulas contain NV1..NV7, THI1..THI7, WP1..WP7 each; no `<>`, ` in `, IsBlank,
Not( inside any Filter( whose first argument is ECA, BaiThi or CLB; no real names, tenantId or URLs;
regeneration identical. Mutation-check 3 key tests (must go red). No core/schema/CSV change (stop rule §2).
Do NOT edit existing generators or the app spec text (report mismatches you find instead).
```

### K2. T4M-BK3, BK4
```
T4M-BK3 then T4M-BK4 (Sonnet), one session, after K1 is merged on the branch. Follow §2-3 and §9.
Tests first. Read: §9; T4M_KET_QUA_TAI_LIEU.md §8.3-8.4; T4M_FLOW_DA_LAM.md (all); T4M_DAC_TA_SUA_APP.md §7,
§10.4, §11 (R1..R38); T4M_HUONG_DAN_THU.md §9 (HDT rows); mau_forms_thi_clb/bo_dung_t4m/ from K1;
tao_mau_forms.py --moi-clb.
BK3 flow table: from de_thi.json, one row per club WITH a quiz: flow name DaLam_<ClubId>, ClubId constant,
empty Form Id / owner / tested-date cells for IT; plus the expressions to paste (toLower(responder), ClubId
constant, OData filter ResponseId eq '...') from FLOW_DA_LAM §3. Markdown + CSV. No .zip (decision 3).
BK4 one command: mau_forms_thi_clb/tao_bo_dung_t4m.py --de-thi <json> --ra <dir> [--zip] builds
01_lists/ (K1 outputs), 02_app/ (K1 formulas), 03_flow/ (BK3), 04_forms/ (tao_mau_forms --moi-clb outputs, called
as a function, not re-implemented), HUONG_DAN_IT.md: build order (lists -> CLB FormUrl -> app formulas -> flow ->
test round), each step one pass/fail line pointing to R1..R38 / HDT §9 rows, the three list ways A/B/C with the
permissions from KQ §8.1 and HỎI-IT marks. Byte-identical regeneration incl. the zip (fixed timestamps, sorted).
Tests: one command makes all four folders; flow rows == clubs with de_thi; every flow ClubId in CLB.csv;
HUONG_DAN_IT.md names every R1..R38 at least once; no real data/tenantId/URL; demo_t4m.py default, --moi-clb,
--day-du outputs unchanged (compare as in round 4). Update mau_forms_thi_clb/README.md and
T4M_VAN_HANH_MOT_DOT.md (one short section each). Related tests + ruff + mutation check of 3 key tests.
```

**Ngoài phạm vi T4M-BK (cần Truong hoặc IT):** chạy bộ dựng trong tenant (GĐ3, NC-02); tài khoản dịch vụ làm chủ flow; DLP; nạp dữ liệu thật. Nguyên mẫu riêng của Truong trên Developer Plan (hạn tạo môi trường 15/11/2026) là việc khác, chỉ làm nếu Truong yêu cầu.
