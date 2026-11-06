# T4M. Kiến trúc RB-DA trên hệ Microsoft của trường

> **Bản nháp v0 — chưa có kết quả phỏng vấn (GĐ2).** Viết theo **dự phòng A** của `T4M_KE_HOACH_NGHIEN_CUU.md` §5: IT chưa trả lời, nên mọi điểm phụ thuộc trường mang nhãn **HỎI-IT**; chỗ nào câu trả lời đổi thiết kế thì có **hai nhánh**: kho = SharePoint List (nhánh **L**) / kho = Dataverse (nhánh **D**). Phải soát lại toàn bộ sau GĐ2 (danh sách ở §10).

Mã việc: **T4M-GD4-V0** (bước S3 của `T4M_KE_HOACH_TU_DONG.md`), thuộc **T4M-NC**. Chỉ tài liệu: không sửa mã, không đổi hợp đồng CSV, không đụng bất biến nào. Soạn 06/11/2026.
Nhãn bằng chứng theo §4 của kế hoạch: **ĐXM**, **TT-CXM**, **GĐ**, **HỎI-IT**, **TH**. Mọi ước lượng ghi "(ước lượng)". Mọi số đo là **MÔ PHỎNG**. Không chứa dữ liệu thật, tenantId, địa chỉ app hay tên người.
Nguồn dùng: `T4M_KET_QUA_TAI_LIEU.md` (gọi tắt **KQ**), `T4M_GOI_THIET_KE.md` (**GOI**), `T4M_HUONG_DAN_THU.md` (**HDT**), `T4M_PHIEU_PHONG_VAN.md`. Vận hành từng bước của một đợt: `T4M_VAN_HANH_MOT_DOT.md` (S1, **VH**; tài liệu này không chép lại lệnh). Đo mô phỏng: `T4M_DO_MO_PHONG.md` (S4, **DO**; chỉ dẫn bảng, không diễn giải).

---

## 1. Tóm tắt điều hành (10 dòng)

1. **Giữ app Power Apps "ECA" của trường** làm cửa thu nguyện vọng; sửa để mỗi ngày nhận **Top 3** có xếp hạng thay cho một lựa chọn (ô A; NC-04, NC-05).
2. **Kho = SharePoint List, mô hình rộng** (một dòng mỗi em × ngày, cột `NV1..NV3`) là nhánh khuyến nghị: connector chuẩn, không cần Premium, xuất CSV dư khoảng 4 lần trần (NC-03, NC-09, ĐXM). Nhánh D chỉ khi app hiện đã chạy Dataverse (HỎI-IT, NC-01).
3. **Điểm thi qua Microsoft Forms Quiz** (chế độ "chỉ thi" đã có trong kho, T4M-Q1..Q3); ghép với nguyện vọng bằng **Email chữ thường**.
4. **Xuất thủ công** (Export to CSV của Lists; Open in Excel của Forms) → **bộ chuyển đổi Python trên máy IT** (`chuyen_forms_sang_phan_mem.py --chi-thi --lists`) → Sổ nhập → **kiosk ngoại tuyến**, mỗi cơ sở một workspace.
5. **Trả kết quả bằng Excel theo lớp chủ nhiệm** (`export_theo_lop`), gửi GVCN qua Teams/Outlook (tay, hoặc flow tuỳ chọn). V1 **không** ghi từng dòng về app (hồ sơ Low 6.000 yêu cầu/người/ngày, NC-13, ĐXM).
6. **Hợp đồng CSV của kiosk không đổi** (bất biến 7) cho mọi phần trừ gói tiếng Nhật.
7. **Gói tiếng Nhật**: thiết kế hai pha đã có (GOI), **chờ Truong duyệt D1–D5**; trước đó dùng phương án (c) "trường tự gán, chỉ trừ chỉ tiêu" làm V0.
8. **Thay đổi giữa kỳ** (muộn, đổi, rút): chạy lại kiosk, STB giữ khoá (bất biến 3); `run_history` thêm dòng (bất biến 4).
9. **Chặn lớn nhất**: chưa biết kho thật (NC-01), quyền môi trường thử (NC-02; Developer Plan hết tạo môi trường từ 15/11/2026, ĐXM), nguồn Lớp và cấp độ (NC-07, NC-08), chính sách dữ liệu (NC-16).
10. Quyết định chờ Truong: §9 (T4-K2), §8 (mã mục), D1–D5 của gói (§5).

---

## 2. Kiến trúc theo ô A–H

```
PowerSchool ─(đường đồng bộ: HỎI-IT, NC-08)─► Entra ID / list học sinh
        │
[A] App ECA (Power Apps canvas): Top 3 mỗi ngày + màn gói ── [A'] Forms Quiz "chỉ thi" (email tự ghi)
        │                                                        │
[B] SharePoint List (rộng)  ‖  nhánh D: bảng Dataverse           │
        │ [C] cột TrangThai = "Đã khóa" + tắt sửa trong app      │
[D] Export to CSV (tay)  ‖  nhánh D: xuất Excel của bảng   Open in Excel (tay)
        └──────────────────────┬─────────────────────────────────┘
[E] Python trên máy IT: chuyen_forms_sang_phan_mem.py --chi-thi --lists → SO_NHAP_CLB.xlsx + cảnh báo
        │
[F] Kiosk rbda-kiosk (.exe) trên máy IT, ngoại tuyến, mỗi cơ sở một workspace
        │
[G] export_theo_lop → Excel theo lớp → Teams/Outlook (tay hoặc flow tuỳ chọn, connector chuẩn)
        │
[H] Đợt bổ sung: xuất lại → chuyển đổi lại → chạy lại (STB khoá, em mới chèn ngẫu nhiên đều)
```

| Ô | Ứng dụng chọn (V1) | Căn cứ | Nhánh D khác gì |
|---|---|---|---|
| A. Thu thập | App ECA hiện có, sửa ô mỗi ngày thành Top 3 (dropdown ×3, chặn trùng trước khi ghi); màn gói hiện theo cấp | NC-04, NC-05, NC-06 (ĐXM giới hạn, GĐ mẫu) | Lọc uỷ quyền rộng hơn với Dataverse; mẫu màn giữ nguyên |
| A'. Điểm thi | Microsoft Forms Quiz, chế độ "chỉ thi" (`tao_mau_forms.py --chi-thi`) | NC-23, NC-24 (ĐXM), KQ §7.4 | Không đổi |
| B. Lưu | SharePoint List `ECA` dạng rộng | NC-03, NC-04, NC-09 (ĐXM) | Bảng Dataverse cùng cột; cần giấy phép/dung lượng (NC-03) |
| C. Khoá | Cột `TrangThai`; app tắt sửa khi "Đã khóa"; IT xuất ngay sau khoá | NC-10 (HỎI-IT) | Có thể dùng quyền theo vai trò của Dataverse (HỎI-IT) |
| D. Xuất | Lists "Export to CSV" (bản chụp, tối đa 30.000 dòng) | NC-09 (ĐXM; mã hoá và cột Choice: TH) | Xuất Excel/CSV của bảng Dataverse (TH; tên cột có thể là tên logic) |
| E. Chuyển đổi | Python trên máy IT (đã có, có test) | NC-22 (GĐ khuyến nghị), T4M-Q1 | Thêm bảng ánh xạ tên cột nếu tên khác (mã mục T4M-M2, §8) |
| F. Xếp | Kiosk `.exe` trên máy IT | NC-15 (ĐXM SmartScreen; chính sách: HỎI-IT) | Không đổi |
| G. Trả kết quả | `export_theo_lop` → Teams/Outlook | NC-11, NC-12, NC-13 (ĐXM) | Không đổi (V1 không ghi về kho ở cả hai nhánh) |
| H. Thay đổi | Chạy lại kiosk; STB khoá | NC-17 (HỎI-IT), bất biến 3 | Không đổi |

---

## 3. Ma trận quyết định (mẫu §7 của kế hoạch, điền đủ)

| Ô | Lựa chọn | Giấy phép cần | Giới hạn chính (nhãn) | Ai làm, ai bảo trì | Rủi ro | Phương án lui | Khuyến nghị |
|---|---|---|---|---|---|---|---|
| A. Thu thập | Sửa app ECA: Top 3 mỗi ngày, màn gói | M365 A3/A5, connector chuẩn (L); Premium nếu D (NC-03, ĐXM) | Truy vấn không uỷ quyền: 500 dòng (tối đa 10.000); lọc `=` trên chữ uỷ quyền được, `IsBlank`/`Not` thì không (NC-04, ĐXM) | Người sửa app: HỎI-IT; bảo trì: IT | Không có môi trường thử (NC-02); sửa hỏng app thật (NC-21: Restore tạo bản mới, ĐXM) | Forms Ranking mỗi ngày một câu (≤10 mục, TT-CXM; NC-18) | Sửa app ECA, thử trên **bản sao** trước (NC-05) |
| B. Lưu | SharePoint List rộng | M365 (L); Dataverse: dung lượng + giấy phép (D) | 30 triệu mục; xuất 30.000 dòng; 7.500 dòng cho 1.500 em (NC-04, NC-09, ĐXM) | IT | App ECA đang ở Dataverse for Teams: không tạo mới từ 15/11/2026, treo 15/09/2027, xoá 30/10/2027 (NC-03, ĐXM) | Nhánh D nếu trường đã có Dataverse | **L**, trừ khi NC-01 trả lời "đã ở Dataverse" |
| C. Khoá | Cột `TrangThai` + tắt sửa trong app | M365 | Khoá ở app, không ở kho: ai có quyền list vẫn sửa được ngoài app (GĐ, từ share-app ĐXM) | Giáo viên ECA bấm khoá; IT xuất | Sửa sau khoá làm lệch tệp xuất | Đặt quyền list chỉ đọc khi khoá (HỎI-IT) | Khoá rồi **xuất ngay**; tệp xuất là bản chụp chuẩn của đợt |
| D. Xuất | Export to CSV (tay, 2 bước) | M365 | 30.000 dòng; mã hoá, cột Choice/Lookup chưa ghi trong tài liệu (NC-09, ĐXM + TH) | IT | Mã hoá sai dấu tiếng Việt; tên cột đổi giữa các lần | Flow "Create CSV table" (lọc theo ngày vì phân trang 5.000, NC-13, ĐXM) | Tay; bộ chuyển đổi đọc **theo tên cột**, bỏ cột thừa (HDT §1) |
| E. Chuyển đổi | Python trên máy IT | Không | Không phụ thuộc đám mây | Dự án viết, có test; IT chạy | Tên cột thật khác tệp giả (NC-01) | Office Scripts (1.600 lần/ngày, 120 giây, ĐXM) — không khuyến nghị | Python (`--chi-thi --lists`) |
| F. Xếp | Kiosk `.exe` | Không | SmartScreen cảnh báo tệp chưa ký (NC-15, ĐXM) | IT chạy; dự án bảo trì | Chính sách cài chặn (AppLocker/Intune, HỎI-IT) | Chạy từ mã nguồn Python trên máy IT; ký số mã (tốn phí, để sau) | IT đưa vào danh sách cho phép |
| G. Trả kết quả | Excel theo lớp → Teams/Outlook | M365 | Teams 100 lệnh/60 giây, Outlook 300/60 giây (NC-12, ĐXM); ghi từng dòng về app vượt 6.000 yêu cầu (NC-13, ĐXM) | IT gửi; GVCN báo học sinh | Thiếu danh sách GVCN (NC-08) | Gửi tay theo thư mục lớp | Tệp theo lớp; flow tuỳ chọn do **tài khoản dịch vụ IT** sở hữu |
| H. Thay đổi | Đợt bổ sung: xuất lại, chạy lại | Không | Kết quả đã công bố có thể đổi khi chạy lại (G3 chưa làm) | Giáo viên ECA duyệt; IT chạy | Hạ chỗ em đã công bố | Chạy lại chỉ cho em mới bằng chỉ tiêu còn trống (thủ công, GĐ) | Chạy lại toàn bộ, báo trước "kết quả có thể đổi" đến khi có G1–G3 |

---

## 4. Mô hình dữ liệu, định dạng xuất, ánh xạ sang Sổ nhập

**4.1 Kho (nhánh L; nhánh D cùng cột, tên logic có tiền tố — TH).** Một dòng = **(em, ngày)**. Khoá logic = (`Email` chữ thường, `Thu`). 1.500 em × 5 ngày = 7.500 dòng (ước lượng theo quy mô Truong cho). Cột theo bộ sinh giả `du_lieu_test/sinh_xuat_lists_gia.py` (HDT §1):

| Cột kho | Kiểu (L) | Ý nghĩa | Sang Sổ nhập |
|---|---|---|---|
| `Email` | Một dòng văn bản (**không** Person: NC-04) | Định danh | `Mã HS` = `lower().strip()` |
| `HoTen` | Văn bản | Họ tên | `Họ tên` |
| `CoSo` | Choice | Cơ sở | Tách workspace (một Sổ mỗi cơ sở) |
| `Khoi` | Số | Khối | Không dùng ở V1 |
| `Lop` | Văn bản | Lớp chủ nhiệm (nguồn: HỎI-IT, NC-08) | Cột `Lớp` (T4M-Q1b xong 06/11/2026, 7f9a6bd: `doc_lists` đọc `Lop`/`Lớp`) |
| `Thu` | Choice | Thứ 2 … Thứ 6 | Buổi (`ma_buoi` → `thu_2`…) |
| `NV1..NV3` | Văn bản (mã CLB) | Top 3 của ngày | `NV1..` của em, lọc theo Buổi của CLB |
| `CapDo`, `Goi` | Choice | Cấp tiếng Nhật, gói đã chọn | **Chưa vào Sổ** (§5; cần A8-GOI-1) |
| `TrangThai` | Choice | Đã khóa / Đang mở | Chỉ để kiểm |

Điểm thi: tệp Forms riêng (`Email` tự ghi, các câu, Points) → bộ chuyển đổi **chấm lại** từ `de_thi.json` → `Điểm k` (= `score_k`, `test_club_k`) (KQ §7.5).

**4.2 Định dạng xuất.** Lists: CSV (bộ chuyển đổi đọc `utf-8-sig`, cắt BOM); Forms: `.xlsx` (nhiều tệp khi tách theo buổi). Kiểm mã hoá tiếng Việt và cách xuất cột Choice: **TH** (HDT §4).

**4.3 Bất biến 7.** Hợp đồng `club_id, student_id, test_club_k, score_k, pref_k, <buoi>_pref_k` **không đổi**: bộ chuyển đổi chỉ sinh Sổ nhập đúng các cột đã có. Ngoại lệ duy nhất là gói (§5, D2).

**4.4 Khi `student_id` là email — phải kiểm:**
1. Hạ chữ thường và cắt khoảng trắng ở **cả hai nguồn** (List, Forms) trước khi ghép; kiosk so đúng từng ký tự (KQ §3, mục 3).
2. Email trùng sau khi hạ chữ: giữ dòng đầu, báo (đã có trong `doc_lists`).
3. Email có trong Forms mà không có trong List: báo, bỏ điểm (đã có).
4. Email đổi giữa các kỳ (đổi tên miền, em chuyển cơ sở): STB gắn với `student_id`, đổi email = em mới (bất biến 3) → HỎI-IT: email có ổn định cả năm không.
5. Riêng tư: email là dữ liệu cá nhân; Sổ nhập, CSDL và tệp xuất chỉ nằm trên máy IT; thời gian lưu do trường đặt (NC-16, HỎI-IT).
6. Độ dài và ký tự: kiosk nhận chuỗi bất kỳ khác rỗng (KQ §3); không cần đổi.

**4.5 Nhánh D (Dataverse) khác gì cho bộ chuyển đổi.** Tên cột xuất có thể là tên hiển thị hoặc tên logic (`cr123_email`…): TH. Đề xuất một tệp ánh xạ tên cột tuỳ chọn cho bộ chuyển đổi (T4M-M2, §8); mặc định không có tệp thì hành vi như nay.

---

## 5. Pha gói (tiếng Nhật) — tóm tắt, chi tiết ở `T4M_GOI_THIET_KE.md`

> **Trạng thái: thiết kế xong (S2), các quyết định D1–D5 CHƯA được Truong duyệt.** Không viết mã trước khi duyệt và trước khi có câu trả lời ECA Q1–Q3 (GOI §6).

- **Cách xếp (D1, chờ duyệt):** bộ điều phối `run_rbda_co_goi` (tệp mới `goi_nhieu_buoi.py`) đặt **trên** `run_rbda_nhieu_buoi`; không sửa `run_rbda`, `compute_club_priority`, `club_choice_function`. Pha 1: DA trên các gói như một buổi giả `goi` (mỗi em tối đa một gói; **cấp độ là điều kiện tham gia**, lọc ở dữ liệu vào, không phải ưu tiên). Khoá các ngày của gói cho em đã được gói. Pha 2: từng ngày như hiện nay (GOI §2).
- **Nhãn bắt buộc (bất biến 8):** "**bảo đảm trong từng pha, không bảo đảm ổn định toàn tuần khi có gói**"; cặp phá vỡ toàn tuần chỉ đếm (cận trên "tiềm năng"), không chặn; phản ví dụ ở GOI §3.2.
- **Không có gói ⇒ trùng khít từng byte (bất biến 1):** bộ điều phối trả về đúng một lời gọi `run_rbda_nhieu_buoi` với đúng đối số cũ (GOI §3.4).
- **Cam kết cả năm (bất biến 2):** chỉ trừ chỉ tiêu và loại em khỏi pha 1; không đổi thứ tự ưu tiên của ai (GOI §3.5).
- **Đến muộn (bất biến 3):** một bộ STB khoá cho cả hai pha; pha 1 dùng hoán vị riêng của `goi` qua `_seed_cua_buoi` (crc32) — **D5 chờ duyệt**; em mới qua `chen_stb_cho_hoc_sinh_moi` (GOI §3.6).
- **Dữ liệu (D2, D3 chờ duyệt):** cột tuỳ chọn `goi_buoi`, tệp tuỳ chọn `04_goi.csv`, nhãn dành riêng `goi`; schema `clubs.goi_buoi`, bảng `goi_dieu_kien`, dòng `match_results (sid, 'goi', G)` (GOI §4). Đây là **thay đổi hợp đồng CSV và schema**: chỉ làm khi Truong duyệt (quy tắc 7).
- **Phía Microsoft:** cột `CapDo`, `Goi` của kho đã có trong bộ sinh giả; nguồn cấp độ là NC-07 (HỎI-IT); màn gói NC-06 (TH).
- **V0 trước khi duyệt:** phương án (c) — trường tự gán gói, IT trừ tay chỉ tiêu ngày bị chiếm và bỏ nguyện vọng ngày đó của em gói trước khi chạy (không cần mã; đủ nếu tiếng Nhật không quá tải, ECA Q3).

---

## 6. Luồng thay đổi: muộn, đổi, rút (NC-17)

Quy trình thật (ai duyệt, bao lâu một lần, ghi ở đâu): **HỎI-IT / HỎI-ECA** (NC-17, phiếu phỏng vấn câu 15). Thiết kế V1 dùng **khả năng kiosk đã có**, không cần mã mới; thao tác cụ thể ở VH §8:

| Tình huống | Phía Microsoft | Phía kiosk | Bất biến |
|---|---|---|---|
| **Đăng ký muộn** | Giáo viên ECA mở lại app cho em đó (hoặc nhập hộ vào list); `TrangThai` = "Đã khóa" sau khi nhập | Xuất lại → chuyển đổi lại → nạp; STB khoá; em mới nhận số qua `chen_stb_cho_hoc_sinh_moi` (chèn ngẫu nhiên đều, giữ thứ tự tương đối của em cũ) → chạy lại | 3, 4, 5 |
| **Xin đổi CLB** | Giáo viên ECA sửa `NV1..NV3` của dòng (em, ngày) sau khi duyệt | Chạy lại toàn bộ; `get_thay_doi_ket_qua` liệt kê `moi_duoc_xep` / `mat_cho` / `doi_clb` để báo đúng những em bị ảnh hưởng | 1, 4 |
| **Rút / chuyển trường** | Xoá dòng hoặc đặt trạng thái rút (cột mới `Rut`, HỎI-IT) | Nạp Sổ chỉ **cộng thêm**, không xoá em (VH §8): IT rút em trong thẻ Quản lý của kiosk; chạy lại; ghế trả về | 3 (STB em còn lại giữ nguyên thứ tự) |
| **Em tiếng Nhật cam kết cả năm** | Không mở lại cho em đó | V0: trừ tay chỉ tiêu; sau A8-GOI: danh sách cam kết (§5) | 2 |

**Giới hạn phải nói với trường:** chạy lại toàn bộ **có thể hạ chỗ em đã được công bố** (sổ 33 mục, rủi ro của G1: "đã đo, xem mục 3.3"; cần G3 "bảo vệ người đã công bố", chưa làm). Đến khi có G1–G3: (1) gom thay đổi thành **đợt bổ sung có lịch** (ví dụ mỗi tuần một lần, ước lượng; trường quyết), (2) báo trước "kết quả đợt bổ sung có thể đổi", (3) gửi GVCN chỉ danh sách thay đổi từ `get_thay_doi_ket_qua`.

---

## 7. Rủi ro, câu hỏi mở, lộ trình

**7.1 Rủi ro**

| # | Rủi ro | Mức (GĐ) | Giảm nhẹ |
|---|---|---|---|
| R1 | App ECA chạy trên Dataverse for Teams → phải nâng cấp trước 30/10/2027 (NC-03, ĐXM) | Cao nếu đúng | Hỏi IT ngay (NC-01); nhánh D |
| R2 | Không có môi trường thử (Developer Plan hết tạo từ 15/11/2026, ĐXM) | Cao | Dự phòng B: IT làm theo HDT §10 (một trang) |
| R3 | Tệp xuất thật khác tệp giả (tên cột, mã hoá, Choice) | Trung bình | Bộ chuyển đổi đọc theo tên cột; xin tệp mẫu ẩn danh (GĐ2) |
| R4 | Email không ổn định giữa các kỳ → STB coi là em mới | Trung bình | §4.4 mục 4 |
| R5 | Chính sách dữ liệu không cho chép ra máy ngoại tuyến (NC-16) | Chặn nếu đúng | Không có đường lui trong kiến trúc này; phải hỏi trước mọi việc khác |
| R6 | Chạy lại hạ chỗ em đã công bố | Trung bình | §6; G3 về sau |
| R7 | Cài `.exe` bị chặn (NC-15) | Trung bình | Danh sách cho phép; chạy từ mã nguồn |
| R8 | Gói tiếng Nhật quá tải trước khi có A8-GOI | Thấp–trung bình | V0 phương án (c); ECA Q3 |
| R9 | Đáp án Forms tick sai | Thấp | Bộ chuyển đổi chấm lại và báo lệch (KQ §7.0) |

**7.1b Số đo MÔ PHỎNG liên quan (chỉ dẫn, không diễn giải; nhận xét do học sinh viết).** Hai điều kiện (A) không thi, (B) CLB thi như `de_thi.json`, 3 bộ × 20 seed: tỉ lệ nguyện vọng 1 (DO §3), top-3 (DO §4), số em chưa có CLB mỗi buổi (DO §5, §9), suất Tầng 1 về nhóm điểm cao (DO §6, §10), số cặp phá vỡ `verify_stability_tuan` (DO §7), thời gian chạy (DO §8, liên quan ô F). Lệnh tái lập: DO mục "Tái lập".

**7.2 Câu hỏi mở** — chặn: NC-01, NC-02, NC-03 (Premium), NC-08, NC-16; không chặn: NC-07, NC-10, NC-14, NC-15, NC-17, NC-20, NC-25, NC-26, ECA Q1–Q8 của gói. Tất cả đã có trong `T4M_PHIEU_PHONG_VAN.md`.

**7.3 Lộ trình theo pha (thời gian là ước lượng)**

| Pha | Việc | Điều kiện vào | Ước lượng |
|---|---|---|---|
| P0 | GĐ2: phỏng vấn IT + ECA, tệp mẫu ẩn danh | — | 1–2 tuần lịch (phụ thuộc lịch IT) |
| P1 | Soát lại tài liệu này (§10); chọn nhánh L/D; T4M-Q1b-b (`--co-so`) | P0 xong | 1–2 phiên |
| P2 | Chạy thử "khô": tệp xuất mẫu → bộ chuyển đổi → kiosk → Excel theo lớp, trên máy IT | P1 | 1 buổi với IT |
| P3 | Sửa app ECA: Top 3 mỗi ngày (bản sao trước) | Có người sửa app + môi trường (NC-02) | 1–2 tuần (ước lượng) |
| P4 | Đợt thật đầu tiên, gói theo V0 (c) | P2, P3; trường đồng ý | Theo lịch trường |
| P5 | A8-GOI-1..3 nếu Truong duyệt D1–D5; G1–G3 cho thay đổi | Sau đợt đầu | Theo sổ (M, M, M–L) |

---

## 8. Mã mục đề xuất (chờ Truong duyệt — quy tắc 1)

Mỗi mục có `kiem_nhan` để viết test đỏ trước. Cỡ là ước lượng.

| Mã | Nội dung | `kiem_nhan` | Cỡ | Trạng thái |
|---|---|---|---|---|
| **T4M-Q1b** | `--chi-thi` ghi cột `Lớp` từ `Lop` của List vào Sổ nhập; bỏ đường vòng `set_student_class` trong demo | List có `Lop` ⇒ Sổ có `Lớp` đúng từng em; List không có `Lop` ⇒ Sổ trùng khít bản hiện nay; demo không còn gọi `set_student_class` mà `export_theo_lop` vẫn đúng | S | **Xong** 06/11/2026 (7f9a6bd); phần lọc `--co-so` (T4M-Q1b-b) còn chờ |
| **T4M-M1** | Đặc tả sửa app ECA (tài liệu cho người sửa app): Top 3 mỗi ngày, chặn trùng, ngày trống hợp lệ, `Patch` + `IfError`, khoá theo `TrangThai` | Mỗi yêu cầu có một dòng kiểm pass/fail trong HDT §9; tệp xuất từ bản sao app qua được `doc_lists` không cảnh báo | S (tài liệu) | Chờ NC-01, NC-02 |
| **T4M-M2** | Tệp ánh xạ tên cột tuỳ chọn cho bộ chuyển đổi (nhánh D, hoặc List có tên cột khác) | Không có tệp ánh xạ ⇒ đầu ra trùng khít từng byte; có tệp ⇒ tệp xuất đổi tên cột cho cùng Sổ; tên cột ánh xạ không tồn tại ⇒ lỗi rõ | S–M | Chỉ làm nếu GĐ2 cho thấy tên cột khác |
| **T4M-M3** | Đối chiếu hai lần xuất (đợt bổ sung): liệt kê em mới, em rút, dòng đổi NV trước khi chạy lại | Hai tệp giống nhau ⇒ rỗng; thêm/xoá/sửa một dòng ⇒ đúng một mục; không đổi gì ở kiosk | S | Chờ NC-17 |
| **T4M-M4** | Hướng dẫn flow gửi Excel theo lớp cho GVCN (connector chuẩn, tài khoản dịch vụ) | Đối chiếu đủ giới hạn ĐXM ở NC-12, NC-13; không ghi về list | S (tài liệu) | Tuỳ chọn |
| **A8-GOI-1..3** | Gói nhiều buổi: dữ liệu, bộ điều phối, nối kiosk | Ở GOI §5 (T1–T9 mỗi mục) | M, M, M–L | **Chờ Truong duyệt D1–D5** và ECA Q1–Q3 |

Không mục nào cần thư viện mới. Chỉ A8-GOI-1 đổi hợp đồng CSV/schema (D2, D3).

---

## 9. T4-K2 (Google): các phương án — Truong quyết

Hiện trạng: T4-K2 **tạm dừng** (Truong quyết 05/11/2026, `TIEN_DO.md`); T4-K1 và T4-K3 đã làm; phần còn lại là Apps Script lô, trigger, menu 15 mục, xuất theo phần (T4 §11.2 số 2).

| Phương án | Nội dung | Được | Mất |
|---|---|---|---|
| **K2-a. Dừng hẳn** | Đóng T4-K2; giữ T4 làm tài liệu tham khảo | Không tốn công cho đường trường này không dùng | Ngành khác dùng Google (nếu có) phải làm lại sau |
| **K2-b. Giữ tạm dừng** (hiện trạng) | Không làm, không đóng; xem lại khi có khách dùng Google | Không mất thiết kế; không tốn công bây giờ | Thiết kế có thể lỗi thời theo giới hạn Google đổi theo thời gian |
| **K2-c. Làm tiếp cho ngành khác** | Hoàn thành T4-K2 như sản phẩm chung, độc lập với trường này | Có sẵn đường Google cho 12 ngành | Tốn công (cỡ lớn), chưa có người dùng thật để thử |
| **K2-d. Thu gọn** | Chỉ giữ phần dùng chung được cho Microsoft (luật soát, xuất theo phần) và chuyển vào bộ chuyển đổi Python | Một bộ luật soát cho cả hai hệ | Phải tách lại thiết kế T4 |

Tài liệu này **không khuyến nghị**; Truong quyết.

---

## 10. Phải soát lại sau GĐ2

1. NC-01 → chọn nhánh L hay D; xoá nhánh còn lại ở §2, §3, §4.5.
2. NC-02 → P3 của lộ trình có làm được không; người sửa app (T4M-M1).
3. NC-03 → có Premium không (đổi cột "Giấy phép" của ma trận).
4. NC-08 → nguồn cột `Lop` và danh sách GVCN (§4.1, ô G).
5. NC-16 → chính sách chép dữ liệu ra máy IT, thời gian lưu (R5; nếu "không" thì kiến trúc phải đổi).
6. Tệp xuất mẫu ẩn danh → tên cột, mã hoá, Choice (§4.2; T4M-M2 có cần không).
7. NC-10, NC-17 → §3 ô C, §6.
8. ECA Q1–Q8 (GOI §6) và quyết định D1–D5 của Truong → §5, §8.
9. NC-25, NC-26 → luật em vắng thi, chọn CLB thi ở app hay Forms.
10. Đo lại DO với tệp xuất mẫu thật đã ẩn danh nếu trường cho phép (vẫn ghi MÔ PHỎNG nếu dữ liệu bịa). VH §5 (lọc theo cơ sở `--co-so`, T4M-Q1b-b) khi xong → §2 ô E.
