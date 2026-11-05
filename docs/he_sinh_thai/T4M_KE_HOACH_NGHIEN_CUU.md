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
| Ưu tiên | Không xét điểm: mọi em thuộc Tầng 2 (chỉ STB) | Truong |
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
| NC-22 | Bộ chuyển đổi chạy ở đâu: Python trên máy IT (đã có kiosk) hay Office Scripts trong Excel Online (không cần cài) | Kiến trúc ô E | TL + TH | learn.microsoft.com: Office Scripts limits | Khuyến nghị có lý do |

Ưu tiên: **NC-01, NC-02, NC-03, NC-08, NC-16** chặn mọi việc khác; làm trước.

---

## 4. Phương pháp và quy tắc bằng chứng

1. **Nhãn bằng chứng** cho mọi khẳng định trong kết quả:
   - **ĐXM** = đã xác minh: đã mở trang gốc, ghi địa chỉ, ngày đọc, và trích ngắn hoặc tóm tắt đúng câu liên quan.
   - **TT-CXM** = chỉ thấy trong tóm tắt kết quả tìm kiếm, chưa mở trang gốc (cùng nghĩa như T4).
   - **GĐ** = giả định chưa kiểm.
   - **HỎI-IT** = chỉ trường trả lời được.
   - **TH** = đã thử trong môi trường thử, ghi ngày và cách thử.
2. Giới hạn và giá **đổi theo thời gian**: ghi ngày đọc; trang nói "có thể thay đổi" thì ghi lại.
3. **Không đụng app thật của trường.** Mọi thử nghiệm làm trên môi trường thử, list giả, dữ liệu giả.
4. **Không đưa dữ liệu thật vào kho mã**: không tên, email, mã học sinh thật; tệp mẫu từ IT phải ẩn danh (giữ tên cột, thay giá trị). Không đưa `tenantId`, đường dẫn app hay tên người vào tài liệu trong kho.
5. **Liêm chính học thuật:** mọi số đo ở giai đoạn thử là dữ liệu mô phỏng. Nhận xét, diễn giải, kết luận cho báo cáo đề tài do Truong tự viết; tài liệu này và các tệp kết quả chỉ là tài liệu vận hành.
6. **Không subagent** (quy tắc 10 của `CLAUDE.md`).

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

Dán nguyên văn vào một phiên mới trên nhánh `claude/upbeat-shannon-g5nnms` (hoặc nhánh Truong chỉ định). Mỗi phiên đọc `CLAUDE.md`, rồi `docs/phien/claude__upbeat-shannon-g5nnms.md`, rồi tài liệu này.

### P1. Nghiên cứu tài liệu (phiên Opus, cần mạng) — GĐ1

```
Vai trò: phiên nghiên cứu cho mục T4M-NC (ngoài sổ, Truong yêu cầu 05/11/2026). Trả lời bằng tiếng Việt.

Đọc theo thứ tự: CLAUDE.md; docs/phien/claude__upbeat-shannon-g5nnms.md; docs/he_sinh_thai/T4M_KE_HOACH_NGHIEN_CUU.md (toàn bộ); docs/he_sinh_thai/T4_MO_HINH_HE_SINH_THAI.md chỉ mục 2.2, 9.1, 15, 16.

Việc: trả lời mọi câu NC có cột "Cách" chứa TL ở mục 3 (NC-02 phần tài liệu, 03, 04, 05, 08, 09, 11, 12, 13, 14, 15, 18, 19, 21, 22). Với mỗi câu:
1. Mở trang GỐC (learn.microsoft.com, support.microsoft.com, support.powerschool.com, trang của nhà cung cấp). Tóm tắt kết quả tìm kiếm không đủ: chỉ được ghi nhãn TT-CXM.
2. Ghi: kết luận một câu; số liệu và điều kiện áp dụng (giấy phép nào, ngày hiệu lực); địa chỉ trang; ngày đọc; trích ngắn đúng câu liên quan; nhãn (ĐXM / TT-CXM / GĐ / HỎI-IT) theo mục 4.
3. Nêu hệ quả cho ô kiến trúc (mục 2) và điều còn phải hỏi IT.
Trang không mở được thì ghi lý do và nhãn TT-CXM; không bịa nội dung.

Đầu ra: tạo docs/he_sinh_thai/T4M_KET_QUA_TAI_LIEU.md với (a) bảng tổng hợp một dòng mỗi câu NC; (b) một mục chi tiết mỗi câu; (c) danh sách câu hỏi mới cho IT; (d) danh sách nguồn. Điền trước những ô của ma trận mục 7 mà tài liệu đủ để điền, đánh dấu ô còn chờ IT.

Ràng buộc: không sửa mã, không sửa T4_MO_HINH_HE_SINH_THAI.md; không subagent; không đưa dữ liệu thật của trường, tenantId, đường dẫn app vào kho. Đây là tài liệu vận hành: không viết nhận xét hay kết luận cho báo cáo đề tài. Văn bản pháp lý về dữ liệu cá nhân chỉ nêu ở mức khái niệm và ghi "nhà trường tự xác định".

Kết thúc: cập nhật mục "Current state" và "Session log" của docs/phien/claude__upbeat-shannon-g5nnms.md (tiếng Anh), thêm một mục CHANGELOG.md, đánh dấu tiến độ T4M-NC trong docs/ke_hoach/TIEN_DO.md, chạy python .claude/skills/soat-ma/scripts/kiem_nhanh.py, commit và push lên nhánh. Báo Truong: số câu đã ĐXM, câu còn TT-CXM, ba phát hiện ảnh hưởng thiết kế nhiều nhất.
```

### P2. Tổng hợp và thiết kế (phiên Opus) — GĐ4

```
Vai trò: phiên thiết kế cho T4M (Microsoft). Trả lời bằng tiếng Việt.

Đầu vào (đọc theo thứ tự): CLAUDE.md; docs/phien/claude__upbeat-shannon-g5nnms.md; docs/he_sinh_thai/T4M_KE_HOACH_NGHIEN_CUU.md; docs/he_sinh_thai/T4M_KET_QUA_TAI_LIEU.md; tóm tắt phỏng vấn đã ẩn danh Truong dán vào chat; tệp xuất mẫu đã ẩn danh nếu có (Truong cho đường dẫn; KHÔNG commit tệp đó nếu còn dữ liệu thật). Chỉ khi cần: docs/KE_HOACH_NHIEU_BUOI.md mục 2 và 5; docs/ke_hoach/SO_DANG_KY_33_MUC.md mục A3; T4_MO_HINH_HE_SINH_THAI.md mục 7 và 11.

Việc: viết docs/he_sinh_thai/T4M_MICROSOFT.md gồm:
1. Tóm tắt điều hành 10 dòng.
2. Kiến trúc (sơ đồ chữ hoặc mermaid) theo tám ô A đến H của mục 2; mỗi ô chọn một ứng dụng, có câu NC làm căn cứ.
3. Ma trận quyết định mục 7 điền đủ.
4. Mô hình dữ liệu của kho (cột, khoá, một dòng là gì) và định dạng tệp xuất mà bộ chuyển đổi đọc; ánh xạ sang Sổ nhập và hợp đồng cột kiosk (bất biến 7: KHÔNG đổi hợp đồng; student_id là email thì nêu rõ có cần kiểm gì).
5. Thiết kế pha gói (pha 1: gói, mỗi em tối đa một gói, cấp độ là điều kiện tham gia; khoá ngày; pha 2: từng ngày), ghi rõ "bảo đảm trong từng pha, không bảo đảm ổn định toàn tuần khi có gói" (bất biến 8), cách giữ trùng khít khi không có gói (bất biến 1, quy tắc 3), cách giữ chỗ em cam kết cả năm mà không đụng hàm ưu tiên (bất biến 2), em đến muộn theo bất biến 3.
6. Luồng thay đổi theo thời gian (NC-17).
7. Rủi ro, câu hỏi còn mở, lộ trình theo giai đoạn (bộ chuyển đổi, thu thứ hạng, tự động hoá) kèm ước lượng ghi rõ là ước lượng.
8. Danh sách mã mục đề xuất (ví dụ T4M-K1 bộ chuyển đổi, T4M-K2 pha gói), mỗi mục có trường kiem_nhan để viết test trước.
9. Khuyến nghị về T4-K2 (Google): dừng hẳn, hay giữ cho ngành khác; Truong quyết.

Ràng buộc: chỉ tài liệu, không viết mã; không subagent; không dữ liệu thật; số liệu thử là mô phỏng; không viết nhận xét hay kết luận đề tài thay Truong. Dừng và hỏi Truong nếu một bất biến xung đột với thiết kế.

Kết thúc: cập nhật Plan và Current state trong docs/phien/claude__upbeat-shannon-g5nnms.md, CHANGELOG.md, TIEN_DO.md; chạy kiem_nhanh.py; commit, push. Báo Truong các quyết định cần duyệt.
```

### P3. Hướng dẫn dựng môi trường thử (phiên Sonnet) — GĐ3

```
Vai trò: phiên viết hướng dẫn thực hành cho mục T4M-NC, giai đoạn 3. Trả lời bằng tiếng Việt.

Đọc: CLAUDE.md; docs/phien/claude__upbeat-shannon-g5nnms.md; docs/he_sinh_thai/T4M_KE_HOACH_NGHIEN_CUU.md mục 3 và 5; docs/he_sinh_thai/T4M_KET_QUA_TAI_LIEU.md (NC-02, 04, 05, 06, 09, 11, 22).

Việc: viết docs/he_sinh_thai/T4M_HUONG_DAN_THU.md, hướng dẫn từng bước cho người KHÔNG chuyên (Truong hoặc IT) dựng trong MÔI TRƯỜNG THỬ, không đụng app thật:
1. Một SharePoint List giả (hoặc Dataverse for Teams nếu NC-03 cho phép) theo mô hình dài: một dòng một nguyện vọng (email giả, cơ sở, khối, buổi, hạng, club_id), cộng bảng gói tiếng Nhật và bảng cấp độ giả.
2. Một script Python sinh 1.500 em giả (đặt trong du_lieu_test/ hoặc thư mục tạm; không cần thư viện mới; seed cố định) để dán vào list.
3. Màn canvas Top 3 mỗi buổi: chặn chọn trùng, buổi trống hợp lệ, ghi bằng Patch có IfError; màn gói: chỉ hiện cho em đúng cấp, chiếm ba ngày, tối đa một gói.
4. Flow Power Automate xuất CSV UTF-8 có BOM vào thư viện; flow ghi kết quả về list.
5. Bảng kiểm: mỗi bước "đạt / không đạt / lý do", và các phép đo thời gian (ghi là mô phỏng).
Mỗi bước có ảnh chụp cần chụp lại để làm bằng chứng (Truong tự chụp). Chỗ phụ thuộc giấy phép Premium thì ghi rõ và cho đường thay thế bằng connector chuẩn.

Ràng buộc: không subagent; không dữ liệu thật; không tạo PR. Kết thúc: cập nhật tệp bàn giao nhánh, CHANGELOG.md, TIEN_DO.md; chạy kiem_nhanh.py; commit, push.
```

### P4. Tóm tắt hợp đồng nhập của kiosk (phiên Haiku, chỉ đọc) — trước GĐ4

```
Vai trò: phiên chỉ đọc (Haiku, quy tắc 11): KHÔNG sửa tệp, trả lời trong chat bằng tiếng Việt.

Đọc CLAUDE.md, rồi tìm theo TÊN HÀM (không đọc cả tệp) trong api_nhap.py, so_nhap.py, rbda_priority_pipeline.py, lop_hoc_sinh.py.

Trả lời ngắn, có dẫn tên hàm:
1. Kiosk nhập dữ liệu Microsoft Forms bằng những hàm nào, đọc cột nào, chấp nhận .csv / .xlsx nào, mã hoá nào.
2. Sổ nhập (SO_NHAP_CLB.xlsx) có những sheet và cột nào; cột nào bắt buộc; cột Lớp được đọc ở đâu.
3. student_id có ràng buộc định dạng không (độ dài, ký tự, có nhận email không, phân biệt hoa thường không).
4. Chế độ nhiều buổi đọc nhãn buổi và <buoi>_pref_k thế nào; buổi để trống có hợp lệ không.
5. Bất kỳ giới hạn nào (số nguyện vọng tối đa, số CLB, số buổi) mà bộ chuyển đổi Power Apps sang Sổ nhập phải tôn trọng.
Truong sẽ dán câu trả lời vào phiên P2.
```
