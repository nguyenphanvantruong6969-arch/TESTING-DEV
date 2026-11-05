# T4M. Kế hoạch nghiên cứu các ứng dụng Microsoft và PowerSchool để bổ sung kiến trúc RB-DA

Trạng thái: KẾ HOẠCH, chưa nghiên cứu. Soạn 05/11/2026 theo yêu cầu của Truong ("viết prompt và lên kế hoạch nghiên cứu cụ thể các app để bổ sung cho architecture hiện có").
Mã việc: **T4M-NC** (ngoài sổ 33 mục, Truong yêu cầu 05/11/2026). Chỉ là nghiên cứu và tài liệu: không sửa mã, không đổi hợp đồng CSV, không đụng bất biến nào.
Quan hệ với T4: `T4_MO_HINH_HE_SINH_THAI.md` thiết kế trên Google vì giả định trường không có Power Apps. Giả định đó **sai với trường của Truong** (mục 1). T4M nghiên cứu hướng Microsoft; kết quả sẽ quyết T4-K2 (Google) dừng hẳn hay giữ cho ngành khác.

---

## 0. Mục tiêu, phạm vi, đầu ra

**Câu hỏi chính:** với hệ sinh thái sẵn có của trường (Power Apps "ECA Registration HVT", Microsoft 365 A3/A5, PowerSchool), mỗi ô trong kiến trúc (thu thập, lưu, khoá, xuất, chuyển đổi, xếp, trả kết quả, xử lý thay đổi) nên dùng ứng dụng nào, cần quyền và giấy phép gì, giới hạn ra sao, ai làm?

**Trong phạm vi:** Power Apps (canvas), SharePoint Lists, Dataverse / Dataverse for Teams, Power Automate, Excel Online và Office Scripts, OneDrive / thư viện SharePoint, Microsoft School Data Sync (SDS), Microsoft Entra ID, PowerSchool SIS, Teams và Outlook, Microsoft Forms (phương án lui), chính sách Power Platform (DLP, môi trường), chính sách cài phần mềm trên máy IT (SmartScreen, Intune, ký số).

**Ngoài phạm vi:** viết mã bộ chuyển đổi hay pha gói (chờ mã mục riêng); mô hình kinh doanh; tư vấn pháp lý (chỉ nêu ở mức khái niệm và đề nghị hỏi nhà trường).

**Đầu ra:**
1. `docs/he_sinh_thai/T4M_KET_QUA_TAI_LIEU.md`: kết quả đọc tài liệu cho từng câu NC, có nguồn và nhãn bằng chứng (mục 4).
2. Biên bản phỏng vấn IT và giáo viên ECA (lưu NGOÀI kho nếu có tên người hay dữ liệu thật; trong kho chỉ ghi tóm tắt đã ẩn danh).
3. `docs/he_sinh_thai/T4M_MICROSOFT.md`: thiết kế kiến trúc bản Microsoft, ma trận quyết định (mục 7), danh sách mã mục đề xuất để Truong duyệt.

---

## 1. Những gì đã biết (Truong trả lời 05/11/2026, chưa kiểm với IT)

| Mặt | Hiện trạng | Nguồn |
|---|---|---|
| Ứng dụng | Canvas app Power Apps "ECA Registration HVT" trong tenant Microsoft 365 của trường; hai ngôn ngữ; học sinh đăng nhập bằng tài khoản trường | Ảnh chụp màn hình |
| Màn hình | Bộ lọc Cơ sở (tự điền, khoá), Cấp học, Khối; Thứ 2 đến Thứ 6 mỗi ngày một ô thả xuống (một lựa chọn, **không xếp hạng**); danh sách lớp đã đăng ký kèm "(Đã khóa)" | Ảnh chụp màn hình |
| Quản lý | Bộ phận IT **và** giáo viên ECA | Truong |
| Đồng ý thử | Nhà trường **đã đồng ý** thử RB-DA | Truong |
| Giấy phép | Microsoft 365 A3 hoặc A5; **chưa rõ** có Power Apps / Power Automate Premium | Truong |
| Cơ chế | App **không chặn sĩ số**; chỉ tiêu có nhưng linh hoạt; đăng ký mở vài ngày; admin **khoá sau hạn**; việc chia lớp quá đông nhiều khả năng làm tay | Truong |
| Định danh | Email trường; PowerSchool **tự đồng bộ** vào app (cơ chế chưa rõ, có thể là SDS) | Truong |
| Quy mô | 500 đến 1.500 học sinh mỗi đợt; dưới 10 lớp mỗi buổi; mỗi cơ sở xếp riêng | Truong |
| Ưu tiên | Hiện **chưa** xét điểm. **Quyết định 05/11/2026 (Truong):** trường đổi quy trình theo RB-DA; CLB có thi tuyển dùng Tầng 1 (−điểm rồi STB), CLB không thi dùng Tầng 2 (STB). Bài thi do giáo viên CLB ra, **công cụ của dự án dựng giúp** (bản Microsoft của `tao-google-form-clb` / `xu-li-raw-forms`) | Truong |
| Buổi | Thứ 2 đến Thứ 6, buổi nào cũng tuỳ chọn | Truong |
| Gói | **Tiếng Nhật là gói nhiều buổi** (ví dụ 3A: Thứ 2, 4, 5); nhiều cấp độ, **trường chỉ định cấp** cho từng em; **cam kết cả năm** | Truong |
| Thay đổi | Có đăng ký muộn, xin đổi lớp, rút hoặc chuyển trường | Truong |
| Báo kết quả | Giáo viên chủ nhiệm báo | Truong |
| Người chạy kiosk | Bộ phận IT | Truong |
| Mục tiêu của trường | Giảm xếp tay; công bằng, minh bạch; dữ liệu cho đề tài | Truong |
| **Chưa biết** | Kho dữ liệu (SharePoint / Excel / Dataverse); xuất được Excel không; quyền của tài khoản học sinh; Premium; cài `.exe` trên máy IT; hạn đợt tới; số nguyện vọng mỗi buổi; chỉ tiêu tiếng Nhật; ECA gói khác | Truong chọn "Bỏ qua" |

Hệ quả thuật toán đã chốt về nguyên tắc (chi tiết thiết kế ở T4M_MICROSOFT.md sau này):
- Gói nhiều buổi phá điều kiện "các buổi độc lập" (`KE_HOACH_NHIEU_BUOI.md`, mục 2). Đề xuất **xếp hai pha**: pha 1 các gói (mỗi em tối đa một gói; cấp độ là điều kiện tham gia, không phải ưu tiên), khoá ngày, rồi pha 2 từng ngày như hiện nay. Bảo đảm chỉ đúng **trong từng pha**; phải ghi "không bảo đảm ổn định toàn tuần khi có gói" (bất biến 8).
- Em tiếng Nhật cam kết cả năm: kỳ sau trừ thẳng vào chỉ tiêu, không xếp lại; chỉ đổi chỉ tiêu, không đụng hàm ưu tiên (bất biến 2).
- Thi tuyển (quyết định 05/11/2026): điểm là đầu vào hợp lệ của `compute_club_priority` (không phải thứ hạng nguyện vọng, không phải kết quả đợt trước: bất biến 2 an toàn). Hợp đồng CSV giữ nguyên `test_club_k`, `score_k`, `<buoi>_test_club_k` (bất biến 7; kiosk và Sổ nhập đã có cột Điểm). Trần chọn thi: `TRAN_CLB_THI_MOI_BUOI = 5`. Việc mới là **đường thu điểm phía Microsoft** (NC-23 đến NC-26).

---

## 2. Bản đồ khoảng trống: ô kiến trúc, ứng dụng ứng viên, câu nghiên cứu

```
PowerSchool ─(SDS?)─► Entra ID / danh sách HS ─► [A] Power Apps ECA (thu, xếp hạng, gói)
                                                       │
                                               [B] Kho: SharePoint List / Dataverse
                                                       │ [C] khoá đợt
                                               [D] Xuất: thủ công / Power Automate → CSV trên thư viện
                                                       │
                                               [E] Bộ chuyển đổi → Sổ nhập (máy IT hay Office Scripts)
                                                       │
                                               [F] Kiosk RB-DA trên máy IT (ngoại tuyến)
                                                       │
                                               [G] Trả kết quả: ghi về kho, Teams / Outlook cho GVCN
                                                       │
                                               [H] Thay đổi theo thời gian: muộn / đổi / rút
```

| Ô | Ứng dụng ứng viên | Câu NC |
|---|---|---|
| A. Thu thập | Power Apps canvas (sửa app có sẵn); Microsoft Forms Ranking (phương án lui) | NC-05, NC-06, NC-18, NC-21 |
| B. Lưu | SharePoint List; Dataverse for Teams; Dataverse (Premium) | NC-01, NC-03, NC-04 |
| C. Khoá | Cột trạng thái trong kho; quyền chỉnh sửa theo thời gian | NC-10 |
| D. Xuất | Xuất Excel của SharePoint; Power Automate tạo CSV | NC-09, NC-13, NC-14 |
| E. Chuyển đổi | Python trên máy IT; Office Scripts trong Excel Online | NC-09, NC-22 |
| F. Xếp | Kiosk `.exe` (PyInstaller) trên máy Windows của IT | NC-15, NC-16 |
| G. Trả kết quả | Power Automate ghi về list; Teams, Outlook; app hiện kết quả | NC-11, NC-12, NC-13 |
| H. Thay đổi | Trạng thái "muộn", "xin đổi", "rút" trong app; kiosk chạy lại giữ STB | NC-17 |
| Nền | SDS, Entra ID, PowerSchool, giấy phép, DLP, môi trường | NC-02, NC-03, NC-07, NC-08, NC-14, NC-20 |
| Đối chiếu | Trang tham khảo của giáo viên (T4 mục 2.2) | NC-19 |

---

## 3. Danh mục câu nghiên cứu

Cột "Cách": **TL** = đọc tài liệu chính thức (giao phiên nghiên cứu, prompt P1); **IT** = hỏi IT hoặc giáo viên ECA (mục 6); **TH** = thử trong môi trường thử (mục 5, giai đoạn 3). "Quyết gì" là quyết định phụ thuộc vào câu trả lời.

| Mã | Câu hỏi | Quyết gì | Cách | Nguồn gợi ý (phải mở trang gốc) | Xong khi |
|---|---|---|---|---|---|
| NC-01 | App ECA lưu dữ liệu ở đâu (SharePoint List, Excel, Dataverse, Dataverse for Teams)? Tên bảng, tên cột, kiểu cột, một dòng là gì (một em một ngày, hay một em một đợt)? | Thiết kế bộ chuyển đổi; có cần sửa mô hình dữ liệu để chứa thứ hạng | IT | (nội bộ trường) | Có sơ đồ cột hoặc tệp mẫu ẩn danh |
| NC-02 | Tài khoản học sinh của Truong có vào `make.powerapps.com`, tạo app, flow, list thử được không? Tenant có chặn tạo môi trường? Có xin được quyền đồng sở hữu (co-owner) app ECA hay một môi trường phát triển riêng? Power Apps Developer Plan có dùng được với tài khoản trường? | Có làm được giai đoạn 3 (thử) không; ai sửa app | IT + TL | learn.microsoft.com: Power Apps Developer Plan; Power Platform environments; app sharing / co-owner | Biết rõ được làm gì, ai cấp |
| NC-03 | Giấy phép A3 / A5 cho quyền Power Platform nào: connector chuẩn hay Premium, Dataverse for Teams, giới hạn yêu cầu (request limits) mỗi ngày? | Có dùng được Dataverse, connector HTTP, Office Scripts qua flow mà không mua thêm | TL + IT | learn.microsoft.com: Power Platform licensing guide; "Power Apps and Power Automate licensing FAQ"; request limits and allocations | Bảng quyền theo A3/A5 có nguồn, và trường xác nhận gói thật |
| NC-04 | Giới hạn của kho ở quy mô 1.500 em × 5 ngày × 3 nguyện vọng (khoảng 22.500 dòng): ngưỡng xem 5.000 mục của SharePoint, giới hạn delegation của Power Apps (500 / 2.000 dòng), hàm nào delegable với SharePoint | Mô hình dữ liệu dạng dài (một dòng một nguyện vọng) hay dạng rộng; app có lọc đúng khi đông | TL + TH | learn.microsoft.com: SharePoint list limits; Power Apps delegation overview; SharePoint delegable functions | Bảng giới hạn có nguồn; khuyến nghị mô hình dữ liệu |
| NC-05 | Mẫu giao diện xếp hạng Top N trong canvas app: chặn chọn trùng, buổi để trống, hai ngôn ngữ, điện thoại; lưu nguyên tử (một lần Gửi ghi đủ các dòng) | Phương án sửa app cho giai đoạn 2; ước lượng công cho người sửa app | TL + TH | learn.microsoft.com: canvas app controls (Dropdown, Combo box, Gallery), `Patch` / `ForAll`, error handling `IfError`, `Errors()` | Một màn thử chạy được với dữ liệu giả, hoặc lý do không làm được |
| NC-06 | Giao diện gói: chỉ hiện gói tiếng Nhật cho em đúng cấp độ; một lần đăng ký gói chiếm Thứ 2, 4, 5 và khoá ba ô ngày đó; mỗi em tối đa một gói | Thiết kế pha 1 ở phía thu thập; bộ chuyển đổi phải gộp hay app đã gộp sẵn | TH + IT | như NC-05 | Màn thử, hoặc quy tắc kiểm cho bộ chuyển đổi |
| NC-07 | Cấp độ tiếng Nhật của học sinh lưu ở đâu: trường tuỳ biến trong PowerSchool, thuộc tính đồng bộ qua SDS, nhóm Entra, hay danh sách riêng của giáo viên? | Nguồn của điều kiện tham gia (`eligible_fn`, mục A3 của sổ) | IT | support.powerschool.com (custom fields); learn.microsoft.com (SDS attributes) | Biết nguồn và cách xuất |
| NC-08 | PowerSchool đồng bộ vào M365 bằng gì (School Data Sync hay cách khác)? Có những thuộc tính nào: mã học sinh PowerSchool, cơ sở, khối, lớp chủ nhiệm (section / homeroom)? Mã PowerSchool có tới được app không? | Định danh: chỉ email hay email kèm mã; nguồn cột Lớp cho kết quả theo GVCN | TL + IT | learn.microsoft.com: School Data Sync overview, SDS data format / attributes; support.powerschool.com: SDS / Microsoft integration | Bảng thuộc tính có nguồn; IT xác nhận cách trường dùng |
| NC-09 | Đường xuất: "Export to Excel / CSV" của SharePoint List (định dạng, mã hoá tiếng Việt, cột lookup / choice ra sao); hoặc Power Automate tạo CSV UTF-8 có BOM vào thư viện; cột có ổn định giữa các lần xuất | Bộ chuyển đổi đọc định dạng nào; thao tác của admin mấy bước | TL + TH | learn.microsoft.com / support.microsoft.com: export list to Excel / CSV; Power Automate "Create CSV table", "Create file" | Một tệp xuất thử từ list giả, đọc được bằng Python, giữ dấu tiếng Việt |
| NC-10 | Admin "khoá" như thế nào (cột trạng thái, tắt app, đổi quyền)? Sau khoá có còn đăng ký muộn? Có bản chụp tại thời điểm khoá? | Thời điểm lấy dữ liệu cho kiosk; xử lý em đến muộn (bất biến 3) | IT | (nội bộ trường) | Mô tả quy trình khoá hiện nay |
| NC-11 | Ghi kết quả kiosk về kho để app hiện "đã xếp": Power Automate đọc CSV / Excel từ thư viện rồi cập nhật list; connector nào là chuẩn, nào Premium; Office Scripts gọi từ flow | Kết quả trả về trong app hay chỉ qua GVCN | TL + TH | learn.microsoft.com: Excel Online (Business) connector, Office Scripts with Power Automate, SharePoint connector | Flow thử cập nhật được list giả, hoặc lý do không làm được |
| NC-12 | Gửi danh sách theo lớp chủ nhiệm cho GVCN qua Teams hoặc Outlook bằng Power Automate; giới hạn gửi; cần thông tin GVCN từ đâu (NC-08) | Cách báo kết quả thay cho in giấy | TL + IT | learn.microsoft.com: Teams connector, Office 365 Outlook connector limits | Phương án có nguồn và giới hạn |
| NC-13 | Giới hạn của Power Automate theo giấy phép M365: số hành động mỗi ngày, số lần chạy, thời gian chạy tối đa; đủ cho 1.500 em và vài chục GVCN không | Có chạy được tự động ở quy mô trường không | TL | learn.microsoft.com: Power Automate limits and configuration; request limits and allocations | Bảng giới hạn có nguồn, so với tải ước tính |
| NC-14 | Chính sách DLP (Data Loss Prevention) và môi trường của tenant: connector nào bị chặn, được ghép với nhau không | Flow ở NC-09, NC-11, NC-12 có bị chặn không | IT + TL | learn.microsoft.com: data policies (DLP) | IT xác nhận chính sách hiện hành |
| NC-15 | Máy IT có cài được kiosk `.exe` (PyInstaller, chưa ký số) không: SmartScreen, Defender, Intune, AppLocker; có cần ký số mã; thư mục dữ liệu đặt ở đâu (máy cục bộ, thư mục OneDrive đồng bộ) | Cách triển khai kiosk ở trường; có cần đổi cách đóng gói | IT + TL | learn.microsoft.com: Microsoft Defender SmartScreen, Intune Win32 app, code signing | IT xác nhận cách cài; danh sách việc cần làm nếu phải ký số |
| NC-16 | Chính sách dữ liệu của trường: dữ liệu học sinh (email, lớp, nguyện vọng) được chép ra máy IT ngoại tuyến không; lưu bao lâu; ai được xem. Văn bản pháp lý liên quan chỉ nêu ở mức khái niệm, đề nghị nhà trường tự xác định | Có được làm M1 (xuất ra kiosk) không; quy tắc lưu và xoá | IT | Quy định của trường; nhà trường tự tra văn bản pháp lý hiện hành về bảo vệ dữ liệu cá nhân | Nhà trường xác nhận bằng văn bản hoặc email |
| NC-17 | Luồng thay đổi: em đăng ký muộn, xin đổi, rút ghi vào đâu; ai duyệt; bao lâu chạy lại một lần; em tiếng Nhật cam kết cả năm | Thiết kế phần "thay đổi theo thời gian" (mục tiêu dự án) cho trường này | IT | (nội bộ trường) | Mô tả quy trình và tần suất |
| NC-18 | Phương án lui: Microsoft Forms câu hỏi Ranking (tối đa 10 mục) cho từng buổi, đăng nhập bằng tài khoản trường; xuất Excel; kiosk đã nhập được (`api_nhap.py`) | Nếu không sửa được app ECA thì thu thứ hạng bằng gì | TL | support.microsoft.com: Microsoft Forms Ranking, limits | Xác nhận giới hạn hiện hành có nguồn |
| NC-19 | Trang tham khảo của giáo viên (`magenta-crepe-416060.netlify.app/dang-ky-clb`): checklist 10 điểm ở T4 mục 2.2 | Có gì đáng giữ cho giao diện | TL (mở trang) | trang đó | Bảng 10 điểm điền xong |
| NC-20 | Nhiều cơ sở: một app chung lọc theo cơ sở hay nhiều app; xuất tách theo cơ sở được không | Mỗi cơ sở một workspace kiosk | IT | (nội bộ trường) | Mô tả hiện trạng |
| NC-21 | Quản lý phiên bản app khi sửa: xuất app ra tệp (`.msapp`, solution), Power Platform CLI (`pac canvas unpack`), lịch sử phiên bản trong Power Apps; khôi phục khi sửa hỏng | Sửa app an toàn, quay lại được | TL | learn.microsoft.com: Power Platform CLI canvas; app version history | Quy trình sửa an toàn 1 trang |
| NC-23 | Microsoft Forms dạng Quiz: tự chấm những loại câu nào, điểm từng câu, giới hạn số câu và số phản hồi, chỉ người trong tổ chức và ghi email tự động, chặn nộp nhiều lần, hẹn giờ mở/đóng, xuất Excel ra cột gì (Total points, từng câu) | Thu điểm bằng Forms Quiz được không; định dạng tệp điểm cho bộ chuyển đổi | TL + TH | support.microsoft.com: Microsoft Forms quiz, settings, limits; export responses to Excel | Bảng khả năng và giới hạn có nguồn; một tệp xuất thử |
| NC-24 | "Công cụ của ta dựng giúp" trên Microsoft: có API chính thức để **tạo** Microsoft Form từ đề (Graph) không? Nếu không: phương án nhập đề (Forms "Quick import" từ Word/PDF, sao chép mẫu `Duplicate`, Power Automate) và giới hạn | Kiến trúc của skill sinh bài thi bản Microsoft (tương đương `tao-google-form-clb`) | TL | learn.microsoft.com: Microsoft Graph API reference (Forms); support.microsoft.com: Quick import, share as template | Kết luận có nguồn; một phương án được chọn kèm lý do |
| NC-25 | Ghép điểm vào nguyện vọng: học sinh chọn CLB thi (tối đa 5 mỗi buổi) ở đâu (app ECA hay Forms), mỗi CLB một bài hay một bài nhiều phần; khoá theo email chữ thường; bài làm không tick, tick không làm, phiếu trùng xử lý theo luật của `xu-li-raw-forms` | Đặc tả bộ chuyển đổi điểm → cột `score_k` | TL + IT | `xu-li-raw-forms` (luật soát hiện có); NC-23 | Đặc tả 1 trang + test dựng trước |
| NC-26 | Công bằng và bảo mật bài thi: thi ở đâu (lớp, nhà), giám sát, lộ đề giữa các buổi, xử lý em vắng thi (điểm = trống, xếp như Tầng 2 hay xếp cuối) | Luật nghiệp vụ của Tầng 1 ở trường này; ghi vào workspace | IT (giáo viên ECA) | (nội bộ trường) | Giáo viên ECA xác nhận luật |
| NC-22 | Bộ chuyển đổi chạy ở đâu: Python trên máy IT (đã có kiosk) hay Office Scripts trong Excel Online (không cần cài) | Kiến trúc ô E | TL + TH | learn.microsoft.com: Office Scripts limits | Khuyến nghị có lý do |

Ưu tiên: **NC-01, NC-02, NC-03, NC-08, NC-16** chặn mọi việc khác; làm trước. NC-23, NC-24 làm bằng prompt P5 (mục 8); NC-25, NC-26 hỏi ở GĐ2.

---

## 4. Quy tắc bằng chứng

Áp dụng cùng `CLAUDE.md` (liêm chính học thuật, không subagent); dưới đây chỉ là phần riêng của T4M.

1. Mọi khẳng định mang một nhãn: **ĐXM** (đã mở trang gốc: địa chỉ, ngày đọc, trích ngắn), **TT-CXM** (chỉ thấy trong tóm tắt tìm kiếm), **GĐ** (giả định chưa kiểm), **HỎI-IT** (chỉ trường trả lời được), **TH** (đã thử ở môi trường thử: ngày, cách thử).
2. Giới hạn và giá đổi theo thời gian: luôn ghi ngày đọc.
3. Chỉ thử trên môi trường thử với dữ liệu giả; không đụng app thật.
4. Không đưa vào kho: tên, email, mã học sinh thật, `tenantId`, đường dẫn app, tên người. Tệp mẫu từ IT phải ẩn danh (giữ tên cột, thay giá trị).
5. Văn bản pháp lý về dữ liệu cá nhân: chỉ nêu ở mức khái niệm, ghi "nhà trường tự xác định".

---

## 5. Lộ trình (giả định Truong dành 1 đến 2 giờ mỗi ngày)

| Giai đoạn | Ngày | Việc | Ai | Câu NC | Mốc kiểm |
|---|---|---|---|---|---|
| GĐ0. Chuẩn bị | 1 | Gửi email xin gặp IT và giáo viên ECA (kèm bộ câu hỏi mục 6); thử đăng nhập `make.powerapps.com` bằng tài khoản trường, chụp màn hình thông báo nếu bị chặn | Truong | NC-02 | Đã hẹn được buổi gặp |
| GĐ1. Đọc tài liệu | 1 đến 4 | Phiên nghiên cứu chạy prompt P1, ra `T4M_KET_QUA_TAI_LIEU.md` | Phiên Opus | NC-03, 04, 05, 08, 09, 11, 12, 13, 14, 15, 18, 19, 21, 22 | **C1:** mọi câu TL có kết luận; ít nhất 80% khẳng định mang nhãn ĐXM |
| GĐ2. Phỏng vấn | 3 đến 8 (song song GĐ1) | Gặp IT và giáo viên ECA; xin tệp xuất mẫu đã ẩn danh; ghi biên bản ngoài kho, tóm tắt ẩn danh vào kho | Truong | NC-01, 02, 07, 10, 14, 16, 17, 20 | **C2:** có sơ đồ cột kho dữ liệu hoặc tệp mẫu; có câu trả lời NC-16 |
| GĐ3. Thử | 8 đến 13 | Chỉ khi NC-02 cho phép: dựng list giả 1.500 em; màn Top 3 mỗi ngày và màn gói; flow xuất CSV; flow ghi kết quả về. Dùng hướng dẫn từ prompt P3 | Truong (phiên Claude hướng dẫn) | NC-04, 05, 06, 09, 11, 22 | **C3:** mỗi thử nghiệm có kết quả "chạy được" hoặc lý do không |
| GĐ4. Tổng hợp | 13 đến 15 | Phiên thiết kế chạy prompt P2, ra `T4M_MICROSOFT.md`, ma trận quyết định, mã mục đề xuất | Phiên Opus, Truong duyệt | tất cả | **C4:** Truong duyệt ma trận và các mã mục |

Tổng: khoảng **3 tuần lịch**. GĐ1 không phụ thuộc trường; GĐ2 phụ thuộc lịch của IT.

**Hai kế hoạch dự phòng:**
- **Dự phòng A (IT chậm trả lời quá 1 tuần):** GĐ4 vẫn chạy với hai nhánh song song (kho là SharePoint List / kho là Dataverse), mọi điểm phụ thuộc trường mang nhãn HỎI-IT; bộ chuyển đổi thiết kế theo tệp xuất giả dựng từ ảnh chụp app. Gửi lại email kèm 5 câu chặn (NC-01, 02, 03, 08, 16) thay vì cả bộ.
- **Dự phòng B (không có quyền tạo app hay flow thử):** bỏ GĐ3 khỏi đường găng. Thay bằng: (1) bản vẽ màn hình trên giấy hoặc Figma cho Top 3 và gói, đưa giáo viên ECA xem; (2) thử xuất và chuyển đổi bằng tệp Excel giả trên máy; (3) đề nghị IT tự làm thử theo hướng dẫn 1 trang (prompt P3 viết cho IT thay vì cho Truong).

---

## 6. Bộ câu hỏi phỏng vấn (in ra mang theo)

**Cho IT:**
1. App ECA lưu dữ liệu ở đâu (SharePoint List, Excel, Dataverse)? Cho em xem tên cột được không? (NC-01)
2. Admin xuất danh sách đăng ký ra Excel được không? Cho em một tệp mẫu đã xoá tên và email thật được không? (NC-01, NC-09)
3. Trường dùng gói A3 hay A5? Có mua thêm Power Apps / Power Automate Premium không? (NC-03)
4. Tài khoản học sinh có được tạo app, flow, list thử không? Nếu không, thầy cô có thể cấp một môi trường thử, hoặc thêm em làm đồng sở hữu một bản sao app không? (NC-02)
5. PowerSchool đồng bộ sang Microsoft 365 bằng gì (School Data Sync?) và có những thông tin nào: mã học sinh, cơ sở, khối, lớp chủ nhiệm? (NC-08)
6. Cấp độ tiếng Nhật của học sinh lưu ở đâu? (NC-07)
7. Tenant có chính sách chặn connector (DLP) không? (NC-14)
8. Máy IT có cài được phần mềm `.exe` không ký số không? Có SmartScreen, Intune, AppLocker chặn không? (NC-15)
9. Dữ liệu học sinh có được chép ra một máy ngoại tuyến để chạy xếp lớp không? Lưu bao lâu, ai được xem? (NC-16)
10. Mỗi cơ sở dùng chung một app hay app riêng? (NC-20)

**Cho giáo viên ECA:**
11. "Khoá" đăng ký làm thế nào? Sau khi khoá còn nhận em đến muộn không? (NC-10)
12. Khi lớp quá đông, hiện nay thầy cô chia thế nào? Mất bao lâu? (bối cảnh, so sánh trước và sau)
13. Chỉ tiêu mỗi lớp, và mỗi cấp tiếng Nhật, là bao nhiêu? Ai quyết? (đầu vào Sổ nhập)
14. Ngoài tiếng Nhật, còn ECA nào là gói nhiều buổi không? (pha 1)
15. Đổi lớp và rút giữa kỳ xử lý thế nào? Bao lâu xếp lại một lần? (NC-17)
16. Thầy cô muốn học sinh xếp hạng mấy nguyện vọng mỗi buổi? (giai đoạn 2; khuyến nghị Top 3)
17. Kết quả gửi GVCN theo dạng nào thì tiện nhất (Excel theo lớp, Teams, email)? (NC-12)
18. Đợt đăng ký tới vào khi nào? (lịch)

---

## 7. Mẫu ma trận quyết định (điền ở GĐ4)

| Ô | Lựa chọn | Giấy phép cần | Giới hạn chính (nhãn) | Ai làm, ai bảo trì | Rủi ro | Phương án lui | Khuyến nghị |
|---|---|---|---|---|---|---|---|
| A. Thu thập | | | | | | | |
| B. Lưu | | | | | | | |
| C. Khoá | | | | | | | |
| D. Xuất | | | | | | | |
| E. Chuyển đổi | | | | | | | |
| F. Xếp | | | | | | | |
| G. Trả kết quả | | | | | | | |
| H. Thay đổi | | | | | | | |

Mỗi ô có đúng một khuyến nghị, kèm câu NC làm căn cứ.

---

## 8. Prompt cho các phiên

Dán nguyên văn vào phiên mới trên nhánh `claude/upbeat-shannon-g5nnms`. Prompt viết tiếng Anh cho rẻ token (như tệp `docs/phien/`); phiên vẫn trả lời Truong bằng tiếng Việt. Luật chung nằm **một chỗ** ở 8.0; mỗi prompt chỉ ghi phần riêng.

### 8.0 Luật chung (mọi prompt trỏ về đây)

- **C1 Đọc:** `CLAUDE.md` → `docs/phien/claude__upbeat-shannon-g5nnms.md` → CHỈ các mục prompt liệt kê. Không đọc cả tệp khi đã có số mục.
- **C2 Bằng chứng:** nhãn và quy tắc ở mục 4. Trang không mở được: TT-CXM kèm lý do, không bịa.
- **C3 Phạm vi:** chỉ tài liệu, trừ khi prompt nói khác; không sửa `T4_MO_HINH_HE_SINH_THAI.md`. Trả lời Truong bằng tiếng Việt.
- **C4 Kết thúc:** cập nhật "Current state" và "Session log" của tệp bàn giao; một mục `CHANGELOG.md`; dòng T4M-NC trong `docs/ke_hoach/TIEN_DO.md`; chạy `python .claude/skills/soat-ma/scripts/kiem_nhanh.py`; commit, push. Báo cáo cuối không quá 10 dòng.

### P1. Đọc tài liệu (Opus, cần mạng) — GĐ1

```
T4M-NC, phase GĐ1. Follow §8.0 of docs/he_sinh_thai/T4M_KE_HOACH_NGHIEN_CUU.md.
Read: that file §2–4; docs/he_sinh_thai/T4_MO_HINH_HE_SINH_THAI.md §2.2 (NC-19 checklist), §9.1, §16 only.
Task: answer every NC whose "Cách" contains TL. Per NC: open the original page; record a one-sentence
conclusion, figures with their conditions (licence, effective date), URL, read date, short quote, label,
impact on the §2 cell, follow-up question for IT.
Output docs/he_sinh_thai/T4M_KET_QUA_TAI_LIEU.md: summary table (one row per NC), one section per NC,
new IT questions, sources. Pre-fill the §7 matrix cells that documentation alone settles.
Report: count of ĐXM vs TT-CXM; the 3 findings that change the design most.
```

### P2. Tổng hợp và thiết kế (Opus) — GĐ4

```
T4M, phase GĐ4. Follow §8.0 of docs/he_sinh_thai/T4M_KE_HOACH_NGHIEN_CUU.md.
Read: that file §1–7; docs/he_sinh_thai/T4M_KET_QUA_TAI_LIEU.md; the anonymised interview summary and the
P4 answer that Truong pastes; the sample export only via the path Truong gives (never commit real data).
On demand only: docs/KE_HOACH_NHIEU_BUOI.md §2 and §5; docs/ke_hoach/SO_DANG_KY_33_MUC.md item A3;
T4_MO_HINH_HE_SINH_THAI.md §7.4 and §11.
Write docs/he_sinh_thai/T4M_MICROSOFT.md:
1. Executive summary, at most 10 lines.
2. Architecture for cells A–H (§2): one app per cell, citing the NC that justifies it.
3. The §7 matrix, fully filled.
4. Store data model (columns, key, what one row is), export format, mapping to Sổ nhập. Invariant 7: the
   kiosk CSV contract does not change; state what must be checked when student_id is an email.
5. Bundle phase: phase 1 bundles (max one bundle per student; level = eligibility, not priority), lock those
   days, phase 2 per day. Label "bảo đảm trong từng pha, không bảo đảm ổn định toàn tuần khi có gói" (inv. 8).
   No bundles ⇒ byte-identical results (inv. 1). Year-committed seats only reduce quota (inv. 2).
   Late arrivals per inv. 3.
6. Change flows: late, swap, withdraw (NC-17).
7. Risks, open questions, phased roadmap; label every estimate as an estimate.
8. Proposed item codes, each with a kiem_nhan field so tests can be written first.
9. Recommendation on T4-K2 (Google); Truong decides.
If an invariant conflicts with the design: stop and ask Truong.
Report: the decisions Truong must approve.
```

### P3. Hướng dẫn môi trường thử (Sonnet) — GĐ3

```
T4M-NC, phase GĐ3. Follow §8.0 of docs/he_sinh_thai/T4M_KE_HOACH_NGHIEN_CUU.md.
Read: that file §3 rows NC-02, 04, 05, 06, 09, 11, 22 and §5; the same NC sections of
docs/he_sinh_thai/T4M_KET_QUA_TAI_LIEU.md.
Write docs/he_sinh_thai/T4M_HUONG_DAN_THU.md, step by step for a non-expert, sandbox only:
1. Fake list, long model (one row per preference: fake email, campus, grade, day, rank, club_id), plus bundle
   and level tables. Dataverse for Teams only if NC-03 allows it.
2. Python generator for 1,500 fake students: fixed seed, standard library only, under du_lieu_test/, with a
   small test (CLAUDE.md rule 2).
3. Canvas screens: Top 3 per day (no duplicates, empty day valid, Patch + IfError); bundle (shown only for the
   student's level, takes its days, max one bundle).
4. Flows: export CSV UTF-8 with BOM to a library; write results back to the list.
5. Checklist per step: pass / fail / reason; timings labelled as simulated; screenshots Truong should take.
Mark every Premium dependency and give a standard-connector alternative.
```

### P4. Hợp đồng nhập của kiosk (Haiku, chỉ đọc) — trước GĐ4

```
Read-only (CLAUDE.md rule 11): edit nothing, skip §8.0 C4. Answer in Vietnamese in chat, at most 40 lines,
citing function names. Locate code by function name with grep; do not read whole files:
api_nhap.py, so_nhap.py, rbda_priority_pipeline.py, lop_hoc_sinh.py.
1. Microsoft Forms import: which functions, columns, accepted formats and encodings.
2. Sổ nhập: sheets and columns, which are required, where the Lớp column is read.
3. student_id constraints: length, characters, is an email accepted, case sensitivity.
4. Multi-session: session labels, <buoi>_pref_k, is an empty session valid.
5. Limits an adapter must respect: max preferences, clubs, sessions.
```

### P5. Đường thu điểm thi trên Microsoft (Opus, cần mạng) — thêm 05/11/2026

Lý do: Truong quyết 05/11/2026 trường đổi quy trình theo RB-DA, có thi tuyển; bài thi do giáo viên ra, công cụ của dự án dựng giúp.

```
T4M-NC, quiz path. Follow §8.0 of docs/he_sinh_thai/T4M_KE_HOACH_NGHIEN_CUU.md.
Read: that file §1 (row "Ưu tiên" and the bullets under it), §3 rows NC-23..26, §4;
.claude/skills/tao-google-form-clb/SKILL.md and .claude/skills/xu-li-raw-forms/SKILL.md (headings first, then
only the parts about form structure, grading, export columns and anomaly rules).
Task: answer NC-23 and NC-24 from original Microsoft pages (labels per §4; never claim an API exists without the
reference page). Then design, without code: (a) how the Microsoft version of tao-google-form-clb builds a
teacher quiz (chosen path from NC-24 with reasons and limits); (b) the export -> score_k mapping for NC-25,
reusing the xu-li-raw-forms anomaly rules, emails lowercased; (c) the business rules NC-26 must settle,
as questions for the ECA teacher. The kiosk CSV contract does not change (invariant 7).
Output: new section §7 "Đường thu điểm" in docs/he_sinh_thai/T4M_KET_QUA_TAI_LIEU.md; add NC-25/26 questions
to docs/he_sinh_thai/T4M_PHIEU_PHONG_VAN.md (ECA block); proposed item codes with kiem_nhan for a later Sonnet
session. Report: what Truong must decide.
```
