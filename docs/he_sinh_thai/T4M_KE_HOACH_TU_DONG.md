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
1. Nếu có công cụ `send_message` (claude-code-remote): gửi tới phiên gốc `session_01YVAyu3Zzm2AEVFAPhazqHY`, tối đa 8 dòng: `DONE` hoặc `BLOCKED`, mã commit, kết quả test, quyết định cần Truong duyệt; với `BLOCKED` thì ghi câu hỏi chính xác cho Truong và các phương án.
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
