# T4M. Kết quả đọc tài liệu (GĐ1) và hợp đồng nhập của kiosk (P4)

Mã việc: **T4M-NC**, giai đoạn GĐ1 của `T4M_KE_HOACH_NGHIEN_CUU.md`. Đọc ngày **05/11/2026**. Mức kỹ: vừa (1 đến 3 trang gốc mỗi câu).
Nhãn theo mục 4 của kế hoạch: **ĐXM** (đã mở trang gốc), **TT-CXM** (chỉ tóm tắt tìm kiếm hoặc nguồn cộng đồng), **GĐ** (giả định), **HỎI-IT**, **TH** (chưa có thử nào trong tài liệu này).
Tài liệu vận hành, không phải kết luận đề tài. Không chứa dữ liệu thật của trường.

---

## 0. Ba phát hiện thay đổi thiết kế nhiều nhất

1. **Hai thứ ngừng cho tạo mới từ 15/11/2026 (10 ngày nữa).** (a) Môi trường **Dataverse for Teams**: không tạo mới được; môi trường chưa nâng cấp bị treo 15/09/2027, xoá 30/10/2027. (b) **Power Apps Developer Plan** không còn tạo môi trường phát triển; môi trường phát triển "unmanaged" bị treo 15/12/2026, xoá từ 15/01/2027. Hệ quả: kho dữ liệu mới nên là **SharePoint List** (connector chuẩn); Truong **không tự lập môi trường thử miễn phí được nữa**, phải xin IT một môi trường (managed developer hoặc sandbox); và nếu app ECA hiện **đang chạy trên Dataverse for Teams** thì trường phải nâng cấp lên Dataverse trước 30/10/2027, việc cần dung lượng Dataverse và giấy phép trả phí (NC-01, NC-02, NC-03). ĐXM.
2. **PowerSchool KHÔNG có trong danh sách nhà cung cấp OneRoster API của School Data Sync.** Vậy "PowerSchool tự đồng bộ" đang đi đường khác (tệp CSV SDS, ClassLink, hay cách riêng). Nguồn của cơ sở, khối, lớp chủ nhiệm và **cấp độ tiếng Nhật** phải hỏi IT (NC-07, NC-08). ĐXM (danh sách ngày 30/10/2026).
3. **Giấy phép M365 = hồ sơ hiệu năng "Low" của Power Automate**: 6.000 yêu cầu mỗi người mỗi 24 giờ (giai đoạn chuyển tiếp: 10.000 mỗi flow), vòng lặp và phân trang tối đa 5.000 mục. Ghi kết quả về từng dòng (tới khoảng 7.500 lần cập nhật cho 1.500 em × 5 buổi) **vượt** mức chính thức. Hệ quả: V1 **không ghi kết quả về app bằng flow từng dòng**; trả kết quả theo lớp chủ nhiệm bằng tệp (kiosk đã có `export_theo_lop`) (NC-11, NC-13). ĐXM.

Thêm hai điểm cho thiết kế (từ P4, mục 3): Sổ nhập cho mỗi CLB **đúng một buổi**, nên gói tiếng Nhật nhiều buổi **không biểu diễn được** bằng Sổ hiện tại (cần mã mục riêng); `student_id` so **đúng từng ký tự, phân biệt hoa thường**, nên bộ chuyển đổi phải chuẩn hoá email về chữ thường.

---

## 1. Bảng tổng hợp

| NC | Kết luận một câu | Nhãn | Còn hỏi IT |
|---|---|---|---|
| NC-02 | Co-owner sửa và chia sẻ được app nhưng không xoá; Developer Plan hết tạo môi trường từ 15/11/2026, thay bằng managed developer environment (mỗi người một, admin bật) | ĐXM | Tài khoản học sinh có được tạo app/flow không; IT cấp môi trường thử nào |
| NC-03 | M365 chỉ có connector chuẩn; Premium, on-premises, custom cần giấy phép riêng; Dataverse for Teams không có cho A1 và đang bị khai tử | ĐXM | Trường có Premium không; app ECA chạy trên kho nào |
| NC-04 | SharePoint List tới 30 triệu mục; Power Apps chỉ xử lý cục bộ 500 dòng (tối đa 10.000) khi truy vấn không uỷ quyền được; với SharePoint uỷ quyền được `Filter`/`LookUp`/`=` trên chữ, không được `IsBlank`, `Not`, `<`/`>` trên chữ | ĐXM | Cột lọc của app hiện dùng kiểu gì |
| NC-05 | Mẫu Top N: lọc bằng `=` trên cột chữ (uỷ quyền được), chặn trùng trong app trước khi ghi; cần thử | ĐXM (giới hạn) + GĐ (mẫu) | — |
| NC-06 | Gói hiển thị theo cấp độ: điều kiện lọc `=` trên cột cấp độ uỷ quyền được; cấp độ phải có sẵn ở kho hoặc Entra | GĐ | Nguồn cấp độ (NC-07) |
| NC-08 | SDS miễn phí, nguồn là OneRoster API hoặc CSV SDS v2.1, chạy 2 lần mỗi ngày, ghi lên Entra: mã ngoài, vai trò, (tuỳ chọn) khối, số người dùng; tạo nhóm lớp. PowerSchool không có trong danh sách OneRoster | ĐXM | Đường đồng bộ thật của trường |
| NC-09 | Microsoft Lists xuất CSV tối đa 30.000 dòng, là bản chụp; xuất Excel là truy vấn `.iqy` một chiều; mã hoá và cách xuất cột Choice/Lookup/Person **không được ghi** | ĐXM + cần TH | Admin hiện xuất bằng cách nào |
| NC-11 | Excel Online (Business), SharePoint, Outlook, Teams đều là connector chuẩn; Office Scripts qua flow: 1.600 lần mỗi người mỗi ngày, 3 lần mỗi 10 giây, quá 120 giây là hết giờ | ĐXM | — |
| NC-12 | Teams: 100 lệnh mỗi kết nối mỗi 60 giây, tin nhắn khoảng 28 KB; Outlook: 300 lệnh mỗi 60 giây; vài chục GVCN là vừa | ĐXM | Danh sách GVCN lấy từ đâu |
| NC-13 | Hồ sơ Low (M365): 6.000 yêu cầu mỗi người mỗi ngày (chuyển tiếp 10.000 mỗi flow), vòng lặp/phân trang 5.000, 500 hành động mỗi flow, flow không chạy 90 ngày có thể bị tắt, chủ flow nghỉ thì về Low | ĐXM | — |
| NC-14 | Chính sách dữ liệu (DLP) do admin lập; vi phạm thì app/flow bị treo, hiệu lực trong 1 đến 24 giờ | ĐXM | Chính sách hiện hành của trường |
| NC-15 | SmartScreen cảnh báo tệp chưa có danh tiếng; tệp ký số có chứng chỉ có danh tiếng thì không cảnh báo; quản lý bằng Group Policy/Intune | ĐXM | Máy IT có cho chạy `.exe` chưa ký không |
| NC-18 | Microsoft Forms Ranking tối đa 10 mục (nguồn cộng đồng); kiosk đã giới hạn 10 nguyện vọng mỗi buổi theo đúng lý do này | TT-CXM | — |
| NC-19 | Trang của giáo viên là cổng "CLUBMATH": hai Google Form (giáo viên mở CLB, học sinh chọn CLB) và bảng điều khiển admin xuất "Excel chạy app" | ĐXM | Trường còn dùng trang này không |
| NC-21 | Power Apps giữ các phiên bản; "Restore" tạo phiên bản mới, phải "Publish" riêng | ĐXM (trang tiền phát hành) | — |
| NC-22 | Khuyến nghị bộ chuyển đổi chạy Python trên máy IT, không dùng Office Scripts | ĐXM (giới hạn) + GĐ (khuyến nghị) | — |
| NC-01, 07, 10, 16, 17, 20 | Chỉ trường trả lời được | HỎI-IT | Xem mục 4 |

---

## 2. Chi tiết từng câu

### NC-02. Quyền và môi trường thử
- **Co-owner:** "Can use, edit, and share the app but not delete or change owners." Chia sẻ cho hơn 100 người thì nên dùng security group. Quyền dữ liệu (list, tệp) phải chia sẻ riêng. Nguồn: learn.microsoft.com/power-apps/maker/canvas-apps/share-app (ms.date 17/09/2026). ĐXM.
- **Developer Plan:** "Starting November 15, 2026, signing up for the Developer Plan no longer creates a developer environment." Môi trường unmanaged bị treo 15/12/2026, xoá từ 15/01/2027. Thay thế: managed developer environment ("each user can create only one"), environment routing do admin bật, môi trường trial vẫn còn. Nguồn: learn.microsoft.com/power-platform/important-changes-coming (ms.date 02/11/2026); powerapps-flow-licensing-faq (ms.date 08/10/2026). ĐXM.
- **Hệ quả cho ô A, GĐ3:** dự phòng B của kế hoạch (không có môi trường thử) trở nên **khả năng cao**. Cần xin IT: bật environment routing, hoặc cấp một môi trường sandbox, hoặc cho Truong làm co-owner một **bản sao** app (không phải app thật).

### NC-03. Giấy phép
- "A standalone Power Apps or Power Automate plan license is required to access all Premium, on-premises, and custom connectors." SQL, Azure, Dynamics 365 đã thành Premium. Nguồn: powerapps-flow-licensing-faq (ms.date 08/10/2026). ĐXM.
- Dataverse for Teams: có trong "select Microsoft 365 subscriptions ... excluding plans for EDU A1"; mỗi môi trường tới 2 GB (khoảng 1 triệu bản ghi); **"Starting November 15, 2026, you can't create new Dataverse for Teams environments."** Treo 15/09/2027, xoá 30/10/2027; muốn giữ phải nâng cấp lên Dataverse, việc cần dung lượng Dataverse của tenant và người dùng có giấy phép Power Apps / Power Automate. Nguồn: như trên và important-changes-coming. ĐXM.
- Yêu cầu Power Platform: giấy phép M365 = 6.000 yêu cầu mỗi người mỗi 24 giờ. Nguồn: learn.microsoft.com/power-platform/admin/api-request-limits-allocations (ms.date 14/10/2026). ĐXM.
- **Hệ quả:** ô B chọn **SharePoint List** (chuẩn, không phụ thuộc Dataverse). Nếu app ECA đang dùng Dataverse for Teams: rủi ro lớn của trường, nêu với IT.

### NC-04. Giới hạn kho và uỷ quyền truy vấn
- SharePoint: "A list can have up to 30 million items"; trên 100.000 mục không tách quyền được ở mức list. Nguồn: learn.microsoft.com/office365/servicedescriptions/sharepoint-online-service-description/sharepoint-online-limits (ms.date 06/10/2026). ĐXM.
- Power Apps: truy vấn không uỷ quyền được thì "Power Apps gets the first 500 records"; nâng được tới 10.000; khuyên đặt 1 khi thử để lộ lỗi. Nguồn: delegation-overview (ms.date 07/10/2026). ĐXM.
- SharePoint uỷ quyền được: `=` trên mọi kiểu; `Filter`, `LookUp`, `Sort` trên số, chữ, đúng/sai, ngày; **không** `<`/`>` trên chữ, **không** `IsBlank` (dùng `= Blank()`), **không** `Not`; cột ID chỉ `=`; Person chỉ Email và DisplayName; `StartsWith` không dùng được trên trường con của Choice/Lookup. Nguồn: connection-sharepoint-online (ms.date 07/10/2026). ĐXM.
- **Tính cho trường:** mô hình dài (một dòng một nguyện vọng) 1.500 em × 5 buổi × 3 = 22.500 dòng. Kho chứa được; nhưng mọi màn hình phải lọc bằng `=` trên cột email (chữ) hoặc số. GĐ: `CountRows` trên SharePoint chưa thấy trong bảng uỷ quyền, coi như **không** uỷ quyền.

### NC-05, NC-06. Màn hình Top N và gói
- Dựa trên NC-04 (ĐXM): mỗi em chỉ đọc các dòng của mình bằng `Filter(List, Email = User().Email)` (uỷ quyền được), nên giới hạn 500 không chạm. Chặn chọn trùng trong app trước khi ghi. GĐ, cần TH.
- Gói: cột `cap_do` (chữ) trên dòng học sinh, lọc `=`. Cấp độ phải tồn tại ở kho hoặc Entra (NC-07). GĐ.
- Chưa đọc trang về `Patch`/`IfError`: để GĐ3.

### NC-08. PowerSchool và School Data Sync
- SDS "is a free service for Education"; nguồn là **OneRoster API** hoặc **CSV SDS v2.1**; chạy "twice (2x) daily"; admin cần SDS Plan 1 (A1) hoặc Plan 2 (A3/A5). Ghi lên người dùng Entra: User External Id, Organization External Id, Organization Role; tuỳ chọn Grade Level, User Number. Tạo nhóm lớp (Class external ID, title, course…), nhóm bảo mật theo trường + vai trò, đơn vị quản trị theo trường; dữ liệu cũng có qua Education API của Microsoft Graph. Nguồn: learn.microsoft.com/schooldatasync/school-data-sync-overview, /connect-data (ms.date 12/10/2026). ĐXM.
- Danh sách nhà cung cấp OneRoster (ms.date 30/10/2026) **không có PowerSchool**; có ClassLink. ĐXM. Bản SDS Classic có hướng dẫn PowerSchool riêng và đã ngừng 31/12/2024: TT-CXM (từ tóm tắt tìm kiếm).
- **Hệ quả:** ô Cơ sở tự điền có thể lấy từ thuộc tính Entra do SDS ghi, hoặc từ một list riêng. Cột Lớp (lớp chủ nhiệm) có thể lấy từ nhóm lớp của SDS nếu trường có đồng bộ lớp. HỎI-IT.

### NC-09. Đường xuất
- "Export > Export to CSV"; "The maximum is 30,000 rows"; tệp là bản chụp; chỉ hiện khi không chọn mục nào. "Export to Excel" tạo `query.iqy`, kết nối một chiều, Refresh để cập nhật. Trang **không** nói mã hoá và cách xuất cột Choice/Lookup/Person. Nguồn: support.microsoft.com/sharepoint/lists/data-and-lists/export-to-excel-from-sharepoint-or-lists (đọc 05/11/2026). ĐXM.
- Có tuỳ chọn "Export to CSV with schema" (2023): TT-CXM.
- **Hệ quả:** 22.500 dòng nằm dưới trần 30.000 nhưng chỉ dư 1,3 lần. Khuyến nghị kho lưu **dạng rộng theo (em, buổi)** (một dòng một em một buổi, cột NV1..NV3): 7.500 dòng, dư 4 lần. Kiểm mã hoá tiếng Việt và cột Choice ở GĐ3 (TH). Kiosk đã đọc được CSV có BOM và tệp `.xlsx` (mục 3).

### NC-11, NC-12, NC-13. Ghi kết quả về và thông báo
- Excel Online (Business): Standard; "List rows" trả 256 dòng mặc định, cần bật phân trang; tệp tối đa 25 MB; 100 lệnh mỗi kết nối mỗi 60 giây; tệp có thể bị khoá tới 6 phút; không hỗ trợ sửa đồng thời; "Run script ... up to 3 calls per 10 seconds and up to 1600 calls per day". Nguồn: learn.microsoft.com/connectors/excelonlinebusiness (cập nhật 11/07/2026). ĐXM.
- Office Scripts: cần A3/A5 (có trong danh sách); 1.600 lần Run script mỗi người mỗi ngày; 120 giây; yêu cầu và phản hồi tối đa 5 MB. Nguồn: learn.microsoft.com/office/dev/scripts/testing/platform-limits (ms.date 24/10/2024). ĐXM.
- Teams: Standard; 100 lệnh mỗi 60 giây; bot gửi 25 lần mỗi 300 giây; tin nhắn khoảng 28 KB. Outlook: Standard; 300 lệnh mỗi 60 giây. Nguồn: learn.microsoft.com/connectors/teams (cập nhật 05/11/2026), /connectors/office365 (cập nhật 01/10/2026). ĐXM.
- Power Automate hồ sơ Low (gồm "Microsoft 365 plans"): "Apply to each" 5.000 mục, phân trang 5.000, 500 hành động mỗi flow, flow 90 ngày không chạy có thể bị tắt, chủ flow rời tổ chức thì flow về Low. Yêu cầu: Office 365 6.000 mỗi người (chính thức), 10.000 mỗi flow (chuyển tiếp). Nguồn: learn.microsoft.com/power-automate/limits-and-config (ms.date 17/07/2026); api-request-limits-allocations. ĐXM.
- **Hệ quả:** gửi danh sách cho khoảng 50 GVCN (mỗi lớp một tin hoặc một email kèm tệp) nằm xa dưới giới hạn. Cập nhật từng dòng cho 1.500 em là sát hoặc vượt 6.000 yêu cầu: không làm ở V1. Flow nên do **tài khoản dịch vụ của IT** sở hữu, không phải tài khoản cá nhân.

### NC-14. DLP
- Admin lập chính sách; connector bị chặn thì app/flow vào trạng thái "suspended or quarantine"; hiệu lực "within an hour" thường, tối đa 24 giờ. Nguồn: learn.microsoft.com/power-platform/admin/wp-data-loss-prevention (ms.date 14/10/2026). ĐXM. Chính sách của trường: HỎI-IT.

### NC-15. Cài kiosk trên máy IT
- SmartScreen cảnh báo tệp không có trong danh sách tệp phổ biến; "If a URL, a file, an app, or a certificate has an established reputation, users don't see any warnings"; quản lý bằng Group Policy và Intune; có trong Windows Education A3/A5. Nguồn: learn.microsoft.com/windows/security/.../microsoft-defender-smartscreen (ms.date 23/04/2026). ĐXM.
- **Hệ quả:** bản PyInstaller chưa ký sẽ bị cảnh báo khi tải về. Hai đường: IT cho phép theo chính sách, hoặc ký số mã (tốn phí, để sau). HỎI-IT.

### NC-18. Microsoft Forms Ranking
- Câu hỏi Ranking tối đa 10 mục: chỉ thấy ở Microsoft Q&A và diễn đàn cộng đồng, không có trang hướng dẫn chính thức. TT-CXM. Kiosk đặt `TRAN_NGUYEN_VONG_MOI_BUOI = 10` cũng vì giới hạn này (mục 3).

### NC-19. Trang tham khảo của giáo viên (điền checklist mục 2.2 của T4)

| # | Việc | Kết quả (đọc 05/11/2026) |
|---|---|---|
| 1 | Trang con, nút, menu | Ba vai trò: Giáo viên "Mở CLB", Học sinh "Chọn CLB", Admin "Điều khiển" |
| 2 | Trường của biểu mẫu | Không thấy: hai nút dẫn sang hai Google Form, trang không chứa trường |
| 3 | Kiểm tra đầu vào | Không thấy trên trang |
| 4 | Dữ liệu gửi đi đâu | Google Forms; bảng admin là bản chụp, thay đổi áp dụng bằng cách gửi tin nhắn hoặc tệp JSON cho một trợ lý tên "Muse"; đồng bộ tối đa mỗi 30 phút |
| 5 | Giờ mở đóng | Không có giờ; hai công tắc bật/tắt nhận phản hồi cho từng biểu mẫu |
| 6 | Xác nhận, sửa phiếu | Không thấy trên trang |
| 7 | Đăng nhập | Không thấy bước đăng nhập ở khu admin |
| 8 | Điện thoại, tốc độ | Không đo |
| 9 | Chỗ lưu, quota | Netlify (trang tĩnh) + Google Forms; không đo |
| 10 | Điểm đáng giữ | Luồng "giáo viên mở CLB → admin duyệt, sửa chỉ tiêu → xuất Excel chạy app (chỉ CLB đã duyệt)" và tệp quyết định JSON tải về / nạp lại |

Nhận xét vận hành: khu admin không có bước đăng nhập (theo nội dung đọc được); nếu trang này dùng thật thì nên báo người làm trang. Đây là trang Google, khác hệ Microsoft của trường Truong.

### NC-21. Phiên bản app
- Details > Versions > Restore tạo **phiên bản mới**; "Publish this version" là bước riêng; bản cũ hơn 6 tháng được đóng gói lại. Nguồn: learn.microsoft.com/power-apps/maker/canvas-apps/restore-an-app (ms.date 10/03/2026, trang ghi là tiền phát hành). ĐXM. Chưa đọc trang Power Platform CLI (`pac canvas`): để sau.

### NC-22. Bộ chuyển đổi chạy ở đâu
- Office Scripts bị giới hạn 1.600 lần mỗi ngày, 120 giây, 5 MB mỗi lần gọi (NC-11, ĐXM), và cần Excel trên mạng.
- Khuyến nghị (GĐ): **Python chạy trên máy IT** cùng chỗ với kiosk; không phụ thuộc giấy phép hay giới hạn đám mây; viết test được trong kho; dữ liệu không ra khỏi máy trường.

---

## 3. P4: hợp đồng nhập của kiosk (đọc mã 05/11/2026)

1. **Nhập dữ liệu Microsoft Forms** (`api_nhap.py`, lớp `NhapDuLieuMixin`): `import_preferences_csv` (nguyện vọng), `import_test_selection_csv` (chọn CLB thi), `import_csv_auto` + `detect_csv_kind` (tự nhận loại); `xlsx_to_csv_text` đọc thẳng `.xlsx`. `_parse_csv_rows` tự nhận dấu `,` hoặc `;` và **cắt BOM**. Hai dạng: dài (`student_id,name,club_id,rank`) và rộng (`student_id,name,pref_1..pref_10`); nhiều buổi dùng cột `<buoi>_pref_k` (ví dụ `thu_3_pref_1`), mỗi buổi một câu Ranking.
2. **Sổ nhập** (`so_nhap.py`): sheet `1. CLB` (Tên CLB · Buổi · Chỉ tiêu · Suất ưu tiên · Nhóm ưu tiên · Mã CLB) và `2. Học sinh` (Mã HS · Họ tên · Nhóm ưu tiên · NV1 · Điểm 1 · …, hai hàng tiêu đề, dữ liệu từ hàng 3). Bắt buộc: `Mã HS`, `NV1`. Cột Lớp đọc ở `_doc_sheet_hs`, chuẩn hoá bằng `chuan_hoa_lop`; không có cột thì giữ lớp cũ. **Mỗi CLB có một ô Buổi**: gói nhiều buổi không biểu diễn được.
3. **`student_id`**: chuỗi bất kỳ khác rỗng; ô số như `20.0` thành `20` (`o_thanh_chu`); **trùng là trùng đúng từng ký tự**, "hs01" và "HS01" là hai em (có cảnh báo). Email được nhận như chuỗi; bộ chuyển đổi nên **đưa email về chữ thường** trước khi ghi.
4. **Nhiều buổi**: nhãn buổi chuẩn hoá bằng `ma_buoi` ("Thứ 2" → `thu_2`, …); một danh sách NV chung, thuật toán lọc theo buổi của CLB; buổi để trống là hợp lệ (em không có NV ở buổi đó).
5. **Trần**: `TRAN_NGUYEN_VONG_MOI_BUOI = 10`, `TRAN_CLB_THI_MOI_BUOI = 5` (`rbda_priority_pipeline.py`, chép ở `so_nhap.py`); trần thật theo workspace là `max_choices` (`_luat_nghiem`). Mẫu Sổ có sẵn 1.500 dòng học sinh, 60 dòng CLB.

---

## 4. Câu mới cho IT (bổ sung mục 6 của kế hoạch)

1. App ECA lưu dữ liệu trên **SharePoint List, Dataverse hay Dataverse for Teams**? Nếu là Dataverse for Teams: trường đã có kế hoạch nâng cấp trước 30/10/2027 chưa?
2. Trường có bật **environment routing** hoặc cấp được **môi trường sandbox / managed developer** cho em làm bản thử không? (Developer Plan hết tạo môi trường từ 15/11/2026.)
3. PowerSchool đồng bộ sang Microsoft 365 **bằng đường nào** (tệp CSV SDS, ClassLink, công cụ khác)? Có đồng bộ **lớp chủ nhiệm** và **cấp độ tiếng Nhật** không?
4. Admin xuất danh sách đăng ký **bằng nút Export của Lists hay cách khác**? Tệp có giữ dấu tiếng Việt không?
5. Flow của trường do **ai sở hữu** (tài khoản cá nhân hay tài khoản dịch vụ)?
6. Máy IT có cho chạy `.exe` **chưa ký số** không, hay cần đưa vào danh sách cho phép?
7. Có **chính sách DLP** nào chặn SharePoint, Excel Online, Teams, Outlook không?

---

## 5. Ma trận quyết định: phần tài liệu đủ để điền trước (mục 7 của kế hoạch)

| Ô | Khuyến nghị tạm | Giấy phép | Giới hạn chính | Căn cứ | Còn chờ |
|---|---|---|---|---|---|
| A. Thu thập | Giữ app Power Apps, thêm Top 3 mỗi buổi và màn gói | M365 (connector chuẩn) | Lọc bằng `=`; 500 dòng nếu không uỷ quyền | NC-04, NC-05 | Ai sửa app; môi trường thử (NC-02) |
| B. Lưu | SharePoint List, dạng một dòng mỗi (em, buổi) | M365 | 30 triệu mục; xuất CSV 30.000 dòng | NC-03, NC-04, NC-09 | Kho hiện tại (NC-01) |
| C. Khoá | Cột trạng thái trên list | M365 | — | — | Quy trình hiện tại (NC-10) |
| D. Xuất | Nút Export to CSV của Lists (thủ công, 2 bước) | M365 | 30.000 dòng; mã hoá chưa rõ | NC-09 | TH mã hoá |
| E. Chuyển đổi | Python trên máy IT | Không | — | NC-22 | Mã mục mới |
| F. Xếp | Kiosk trên máy IT, mỗi cơ sở một workspace | Không | SmartScreen | NC-15 | Chính sách cài |
| G. Trả kết quả | Tệp Excel theo lớp chủ nhiệm (`export_theo_lop`), gửi qua Teams/Outlook (tuỳ chọn flow) | M365 | 6.000 yêu cầu/người/ngày; không ghi từng dòng về app ở V1 | NC-11, NC-12, NC-13 | Danh sách GVCN (NC-08) |
| H. Thay đổi | Chạy lại kiosk, giữ STB (bất biến 3) | Không | — | — | Quy trình (NC-17) |

---

## 6. Nguồn (đọc 05/11/2026)

- learn.microsoft.com/power-platform/admin/powerapps-flow-licensing-faq (ms.date 08/10/2026)
- learn.microsoft.com/power-platform/important-changes-coming (ms.date 02/11/2026)
- learn.microsoft.com/power-platform/admin/api-request-limits-allocations (ms.date 14/10/2026)
- learn.microsoft.com/power-platform/admin/wp-data-loss-prevention (ms.date 14/10/2026)
- learn.microsoft.com/power-apps/maker/canvas-apps/delegation-overview (ms.date 07/10/2026)
- learn.microsoft.com/power-apps/maker/canvas-apps/connections/connection-sharepoint-online (ms.date 07/10/2026)
- learn.microsoft.com/power-apps/maker/canvas-apps/share-app (ms.date 17/09/2026)
- learn.microsoft.com/power-apps/maker/canvas-apps/restore-an-app (ms.date 10/03/2026)
- learn.microsoft.com/office365/servicedescriptions/sharepoint-online-service-description/sharepoint-online-limits (ms.date 06/10/2026)
- learn.microsoft.com/connectors/sharepointonline (cập nhật 01/08/2026)
- learn.microsoft.com/connectors/excelonlinebusiness (cập nhật 11/07/2026)
- learn.microsoft.com/connectors/office365 (cập nhật 01/10/2026)
- learn.microsoft.com/connectors/teams (cập nhật 05/11/2026)
- learn.microsoft.com/power-automate/limits-and-config (ms.date 17/07/2026)
- learn.microsoft.com/office/dev/scripts/testing/platform-limits (ms.date 24/10/2024)
- learn.microsoft.com/schooldatasync/school-data-sync-overview, /connect-data (ms.date 12/10/2026)
- learn.microsoft.com/schooldatasync/oneroster-provider-overview (ms.date 30/10/2026)
- learn.microsoft.com/windows/security/operating-system-security/virus-and-threat-protection/microsoft-defender-smartscreen (ms.date 23/04/2026)
- support.microsoft.com/sharepoint/lists/data-and-lists/export-to-excel-from-sharepoint-or-lists
- Trang tham khảo của giáo viên (NC-19), địa chỉ ở T4 mục 2.2
- TT-CXM: tóm tắt tìm kiếm về SDS Classic, "Export to CSV with schema", giới hạn Forms Ranking (Microsoft Q&A, diễn đàn cộng đồng)

---

## 7. Đường thu điểm thi trên Microsoft (P5: NC-23 đến NC-27, đọc 05/11/2026)

Bối cảnh: Truong quyết 05/11/2026 trường đổi quy trình theo RB-DA, có thi tuyển (Tầng 1); bài thi do giáo viên ra, công cụ của dự án dựng giúp. Mục này chỉ là tài liệu vận hành và đề xuất thiết kế, chưa có thử nào (TH).

### 7.0 Phát hiện lớn nhất: kho ĐÃ có đường Microsoft Forms
`mau_forms_thi_clb/` (đọc mã 05/11/2026) đã làm gần hết việc "công cụ của ta dựng bài thi":
- `de_thi.json` là nguồn duy nhất (buổi, CLB, chỉ tiêu, đề, đáp án); `tao_mau_forms.py` sinh `NHAP_FORMS_THI_CLB.docx` để **Quick Import**, `CAI_DAT_FORMS.md` (những gì Quick Import không mang: Ranking, rẽ nhánh, đáp án, điểm, cài đặt) và `MAU_XUAT_TU_FORMS.xlsx` (tệp xuất giả).
- `chuyen_forms_sang_phan_mem.py` đọc tệp Excel Forms xuất ra → `SO_NHAP_CLB.xlsx` + `BANG_DIEM.xlsx`; **chấm lại từ `de_thi.json`**, không tin cột "Points" của Forms, chỉ đem ra đối chiếu (lệch là đáp án trên Forms đã sai).
- `CAI_DAT_FORMS.md` mục 5 đã đặt: chỉ người trong tổ chức, **One response per person BẬT**, **Show results automatically TẮT**, Shuffle questions TẮT (giữ rẽ nhánh), Start/End date.
- Thiết kế cũ: MỘT biểu mẫu làm cả nguyện vọng (Ranking) lẫn thi; định danh là ô "Mã HS" học sinh tự gõ.

**Hai chỗ lệch với trường này:** (1) nguyện vọng ở trường nằm trong app Power Apps (ECA), không ở Forms, nên Forms chỉ còn phần **chọn CLB thi + làm bài**; (2) định danh nên là cột **Email** Forms tự ghi khi "Only people in my organization" + "Record name" bật, đưa về chữ thường, để ghép với dòng (em, buổi) của list, thay vì mã HS tự gõ.

### 7.1 NC-23. Microsoft Forms dạng Quiz
- Điểm: "Add a number in the **Points** text box to assign a point value for a correct answer". Câu Choice: tick **Correct Answer**, có thể nhiều đáp án đúng. Câu Text: "you can add one or more correct answers" (đoạn trích tìm kiếm của trang hỗ trợ: TT-CXM). Điểm từng phần (partial credit): không có trong tài liệu, nguồn cộng đồng mâu thuẫn → coi như **không có** (GĐ). Nguồn: support.microsoft.com/forms/create-a-quiz-with-microsoft-forms. ĐXM.
- Cài đặt (ĐXM, support.microsoft.com/office/adjust-your-form-or-quiz-settings-in-microsoft-forms-…): "Only people in my organization can respond" (có cho Office 365 Education) kèm **Record name** và **One response per person**; "Specific people in my organization" tới 100 tên, trong đó tới 20 nhóm; **Start date / End date**; **Set time duration** (hết giờ tự nộp); Shuffle questions (không dùng được khi có nhiều phần); **Show results automatically** mặc định BẬT, phải tắt; Practice mode; mở bằng ứng dụng **Take a Test** (môi trường thi khoá máy).
- Giới hạn (ĐXM, support.microsoft.com/forms/form-question-response-and-character-limits-in-microsoft-forms): **200 câu mỗi biểu mẫu**; 5.000.000 phản hồi; **400 biểu mẫu mỗi người, tính cả thùng rác**; câu hỏi 4.000 ký tự, mỗi lựa chọn 1.000 ký tự. Hệ quả: một biểu mẫu chung cho mọi đề chỉ chứa được khoảng **(200 − câu chọn CLB) ÷ số câu mỗi đề** đề; 20 CLB thi × 5 câu = 100 câu là vừa; nhiều hơn thì tách theo buổi.
- Xuất (ĐXM, support.microsoft.com/forms/check-and-share-your-quiz-results): Responses → **Open in Excel**; 5 cột đầu: ID, giờ bắt đầu, giờ xong, **Name, Email**; sau đó **Total points, Quiz feedback, Grade posted time**, các câu, rồi điểm và nhận xét từng câu. Học sinh chỉ thấy điểm sau **Post scores**. Có báo cáo cộng đồng về cột Total points trống trên Excel Online (TT-CXM) → không phụ thuộc cột này (đúng như bộ chuyển đổi hiện có).
- Giao bài qua **Teams Assignments**: quiz lưu thành biểu mẫu nhóm (giới hạn 200 biểu mẫu nhóm), có thẻ Grades; có báo cáo lệch điểm Forms ↔ Teams (TT-CXM). Không cần cho V1.
- Connector Microsoft Forms (ĐXM, learn.microsoft.com/connectors/microsoftforms, cập nhật 06/10/2025): **Standard** trong Power Automate; **"Power Apps: Not available"**; chỉ có trigger "When a new response is submitted" và hai hành động **đọc** (Get form details, Get response details); **không có hành động tạo biểu mẫu hay câu hỏi**; 300 lệnh mỗi 60 giây.

### 7.2 NC-24. Công cụ có tự tạo biểu mẫu được không
- Trang tổng quan Microsoft Graph v1.0 (ms.date 16/07/2024) **không liệt kê** tài nguyên Forms (ĐXM, nhưng trang tổng quan không đủ để chứng minh không có). Nhân viên và MVP trên Microsoft Q&A, TechCommunity (2023 đến 03/2026): **không có API được hỗ trợ để tạo** biểu mẫu; điểm cuối `/formsapi` là không chính thức (TT-CXM). Kết luận: **không xây trên API tạo biểu mẫu**.
- **Quick Import** (ĐXM, support.microsoft.com/forms/convert-a-word-or-pdf-form-or-quiz-to-microsoft-forms): Word/PDF **từ ổ máy**, không từ SharePoint/OneDrive; tối đa **10 MB**; chuyển tiêu đề, phụ đề, câu nhiều lựa chọn và câu văn bản; câu ghép cặp và nhiều chỗ trống thành câu văn bản; công thức phức tạp không hỗ trợ; tiếng Anh chuyển chính xác hơn; **đáp án không được nhập**: giáo viên tick sau khi soát.
- **Share as a template → Get a link to duplicate** (ĐXM, trang hỗ trợ cũ hơn): chép nội dung, không chép phản hồi. Dùng để giữ một biểu mẫu mẫu đã cài đặt sẵn và nhân ra cho mỗi đợt.
- **Hệ quả:** "công cụ của ta dựng giúp" trên Forms = sinh `.docx` Quick Import + danh sách việc tay (đáp án, điểm, cài đặt) + bộ chuyển đổi chấm lại. Đây đúng là cái `mau_forms_thi_clb/` đã làm. Phần tay còn lại: tick đáp án cho mọi câu (ví dụ 50 câu), đặt rẽ nhánh nếu một biểu mẫu chung.

### 7.3 NC-27 (mới). Bài thi ngay trong Power Apps
- Quyền dữ liệu (ĐXM, share-app, ms.date 17/09/2026): "you must also manage permissions for the data source or sources on which the app is based". Tức là học sinh dùng app phải có quyền trên list app đọc; suy ra (GĐ) **list nào app đọc thì học sinh đọc được cả ngoài app**. Vì vậy **đáp án không được nằm trong list học sinh đọc được**, và app không tự chấm ở máy học sinh.
- Cách giữ kín (GĐ, cần TH): list câu trả lời đặt Item-level permissions "Read items that were created by the user" (nguồn cộng đồng; người có Design/Full Control vẫn thấy hết: TT-CXM); chấm **ngoại tuyến bằng Python** với đáp án IT giữ (như bộ chuyển đổi hiện có); hoặc flow chạy bằng kết nối cố định ("Use this connection" cho run-only users) chấm trên máy chủ. Hành vi khi app gọi flow chưa có trang chính thức xác nhận (TT-CXM) → TH.
- Đưa đề vào: "Create a list based on a spreadsheet" (bảng Excel, đến 5.000 dòng theo trang hỗ trợ: TT-CXM) hoặc flow SharePoint chuẩn. Công cụ sinh tệp Excel đề từ `de_thi.json` → **tự động hoá trọn** phần dựng đề (khác Forms).
- Phải tự lập trình: hẹn giờ, xáo câu, chống làm lại, chế độ khoá máy (Forms có sẵn Take a Test). Cần người sửa app và môi trường (NC-02).

### 7.4 So sánh và khuyến nghị tạm (GĐ, Truong và IT quyết)

| Tiêu chí | Microsoft Forms Quiz | Bài thi trong Power Apps |
|---|---|---|
| Có sẵn trong kho | Gần đủ (`mau_forms_thi_clb/`) | Chưa có gì |
| Giấy phép | M365, không cần Premium | M365 (SharePoint), không cần Premium nếu không dùng connector Premium |
| Công cụ tự dựng đề | Một phần (Quick Import; đáp án tick tay) | Trọn (ghi list từ Excel) |
| Giữ kín đáp án | Forms giữ; tắt Show results | Phải thiết kế quyền, chấm ngoài máy học sinh |
| Hẹn giờ, khoá máy, một lần nộp | Có sẵn | Tự làm |
| Ghép với nguyện vọng | Qua Email chữ thường (hai tệp) | Cùng kho, cùng khoá |
| Cần môi trường / sửa app | Không | Có (NC-02) |
| Rủi ro | 200 câu, 400 biểu mẫu mỗi người; tick tay sai đáp án (bộ chuyển đổi bắt được nhờ chấm lại) | Công sửa app; lộ đáp án nếu đặt quyền sai |

**Khuyến nghị tạm: V1 dùng Microsoft Forms Quiz**, chỉnh `mau_forms_thi_clb/` cho trường này; **V2 cân nhắc Power Apps** khi IT đã cấp môi trường và muốn một app duy nhất. Lý do: dùng lại mã đã có test, không chặn bởi NC-02, công cụ có sẵn hẹn giờ và một lần nộp, giữ kín đáp án không cần thiết kế quyền.

### 7.5 NC-25. Ghép điểm vào `score_k` (đặc tả đề xuất)
1. Chọn CLB thi (tối đa 5 mỗi buổi, `TRAN_CLB_THI_MOI_BUOI`): **HỎI-ECA** đặt ở app ECA (cột trên dòng em-buổi) hay ở câu đầu của Forms. Khuyến nghị: trong Forms, cạnh bài thi, để app ECA chỉ sửa phần Top 3.
2. Khoá ghép: cột **Email** của Forms (không dùng ô gõ tay), `lower().strip()`, khớp email trên dòng list.
3. Luật soát dùng lại của `xu-li-raw-forms` / bộ chuyển đổi: phiếu trùng giữ phiếu đầu; thi mà không có nguyện vọng CLB đó thì bỏ điểm và báo; nguyện vọng có CLB thi mà không làm bài thì để trống điểm (hệ quả do NC-26 quyết); email không có trong list thì báo.
4. Đầu ra: cột Điểm của Sổ nhập (`score_k`, `<buoi>_test_club_k`), **hợp đồng CSV không đổi** (bất biến 7). Không có bài thi nào thì kết quả trùng khít như hiện nay (bất biến 1).

### 7.6 NC-26. Luật nghiệp vụ cần giáo viên ECA quyết
Thi ở đâu, có giám sát không (Take a Test cần máy Windows); một đề dùng cho mọi buổi hay mỗi buổi một đề (lộ đề); em vắng thi xếp thế nào (điểm trống = sau mọi em có điểm, hay như Tầng 2); thang điểm và hoà điểm (hoà thì STB, bất biến 3); ai giữ `de_thi.json` và đáp án.

### 7.7 Mã mục đề xuất (cho phiên Sonnet sau khi Truong duyệt)
- **T4M-Q1** Bộ chuyển đổi chế độ "chỉ thi": Forms không có câu nguyện vọng; khoá là cột Email (chữ thường); ghép với tệp xuất list (`du_lieu_test/sinh_xuat_lists_gia.py`). *kiem_nhan:* test dựng trước với tệp giả: email hoa/thường ghép đúng; phiếu trùng giữ phiếu đầu; email lạ bị báo; không có bài thi thì Sổ nhập trùng khít bản không điểm.
- **T4M-Q2** `tao_mau_forms.py` thêm chế độ "chỉ thi" (bỏ câu Ranking và mã HS, giữ đề, cài đặt "Record name" + Email); kiểm số câu ≤ 200 và tách theo buổi khi vượt. *kiem_nhan:* test đếm câu, test tách, `.docx` sinh lại giống hệt khi `de_thi.json` không đổi.
- **T4M-Q3** Ghi chú vận hành 1 trang cho giáo viên (Quick Import, tick đáp án, Settings bắt buộc, Post scores không cần cho kiosk). *kiem_nhan:* đối chiếu đủ các mục 7.1 có nhãn ĐXM.
- Thư viện: `python-docx` đã có trong `requirements-dev.txt`; không cần thư viện mới.

Nguồn mục 7 (đọc 05/11/2026): support.microsoft.com/forms/create-a-quiz-with-microsoft-forms; /office/adjust-your-form-or-quiz-settings-in-microsoft-forms-f255a4ba-e03c-4e12-b880-f7e8b62e0665; /forms/form-question-response-and-character-limits-in-microsoft-forms; /forms/check-and-share-your-quiz-results; /forms/convert-a-word-or-pdf-form-or-quiz-to-microsoft-forms; /office/share-a-form-or-quiz-as-a-template-82ea9d8a-260a-47a0-afdb-497f3d746e3f; /education/assignments/assign-quizzes-to-students-through-microsoft-teams; learn.microsoft.com/connectors/microsoftforms; learn.microsoft.com/graph/api/overview; learn.microsoft.com/power-apps/maker/canvas-apps/share-app; TT-CXM: Microsoft Q&A về Graph Forms API, item-level permissions, run-only users; support.microsoft.com/sharepoint/lists/data-and-lists/create-a-list-based-on-a-spreadsheet (đoạn trích).

## 8. Bộ dựng sẵn cho IT (T4M-BK0, đọc 06/11/2026)

Câu hỏi: dựng list có cột định sẵn, công thức app và flow **mà ít phải xin quyền quản trị tenant nhất**. Nhãn như trên. Chưa ai thử trong tenant của trường: mọi bước dựng vẫn **TH**.

### 8.1 Tạo list và thêm cột

| Cách | Quyền cần | Nhãn | Ghi chú |
|---|---|---|---|
| A. Site script JSON (`createSPList` + `addSPField` / `addSPFieldXml`), áp bằng `Invoke-PnPSiteScript -Script` | Quyền trên site (trang PnP: "when passing in a site script through -Script, you only need to have permissions to the site"); **nhưng** PnP PowerShell cần một ứng dụng Entra do tổ chức tự đăng ký (bắt buộc từ 09/09/2024; đăng ký cần quyền tạo app registration, nguồn thứ ba nói tối thiểu Cloud Application Administrator) | ĐXM (trang lệnh); TT-CXM (vai trò tối thiểu) | Hợp nhất: chạy lại **không nhân đôi**; list cùng tên thì **chỉ thêm cột còn thiếu** (ĐXM, trang tổng quan). Hợp với việc thêm `NV4..NV7`, `THI1..7`, `WP1..7` vào **bản sao list ECA có sẵn**. HỎI-IT: trường đã có app Entra cho PnP chưa |
| B. Cùng JSON, quản trị SharePoint đăng ký một lần (`Add-SPOSiteScript`, `Add-SPOSiteDesign`), chủ site áp qua **Settings > Apply a site template** | Đăng ký: quản trị SharePoint (GĐ: trang hướng dẫn dùng SharePoint Online Management Shell, không ghi vai trò; lệnh `*-SPO*` cần kết nối site quản trị). Áp: "site owner permissions or higher" (ĐXM) | ĐXM / GĐ | Áp không đồng bộ: trần **300 hành động hoặc 100.000 ký tự**; áp bằng `Invoke-SPOSiteDesign` (đồng bộ) chỉ **30** (ĐXM). Tenant tối đa 100 site script, 100 site template |
| C. Microsoft Lists "Create a list based on a spreadsheet" (CSV/Excel) | Chỉ quyền tạo list trên site | ĐXM (trang hỗ trợ, đoạn trích) | Kiểu cột **đoán theo dữ liệu**, sửa được ở bước Customize; bảng tối đa 5.000 dòng. Tạo list mới thì được; **không thêm cột vào list có sẵn**, nên với ECA phải thêm cột tay |

Hệ quả cho K1: (1) cùng một định nghĩa cột sinh ra **cả ba**: JSON site script (A và B), CSV mẫu một dòng tiêu đề + một dòng ví dụ để đoán đúng kiểu (C), và bảng kiểm thêm cột tay cho ECA (C). (2) Mỗi cột có `id` GUID **cố định** (khuyến nghị của Microsoft để chạy lại không thêm cột lần hai; sinh bằng `uuid.uuid5` theo tên list + tên cột, thư viện chuẩn) và `internalName` đúng tên trong hợp đồng §8 (`NV1`, `THI1`, `WP1`…). (3) `addSPField` chỉ có Text, Note, Number, Boolean, User, DateTime; cột Choice (`Thu`, `TrangThai`, `CoSo`) dùng `addSPFieldXml` (ĐXM). (4) Đếm hành động: ECA khoảng 30 cột + `CLB` 4 + `BaiThi` 4 + `NHAT_KY_DA_LAM` 4 ≈ 45 (ƯL): **vượt trần 30 của áp đồng bộ**, dưới 300 của áp không đồng bộ; bộ sinh phải in số hành động và cảnh báo khi > 30. (5) Rủi ro TH: bản sao ECA có cột `NV1..NV3` tạo tay (GUID khác) thì site script có thể tạo cột trùng tên hiển thị; hướng dẫn IT phải thử trên bản sao trước và chỉ thêm cột chưa có.

### 8.2 Công thức và điều khiển Power Apps
- **Code view** (ĐXM, learn.microsoft.com/power-apps/maker/canvas-apps/code-view, cập nhật 10/2026): xem, chép và **dán mã YAML của điều khiển** (cả điều khiển con) vào Studio để tạo điều khiển mới; mã được kiểm trước khi tạo; **phải dùng đúng định dạng YAML do Studio sinh**; không chép/dán được **App Object**; không sửa mã trong code view; trình duyệt phải cho phép clipboard.
- Hệ quả cho K1: bộ dựng giao **công thức Power Fx theo từng thuộc tính** (`OnVisible`, `Items`, `OnSelect`, `DisplayMode`…), dán vào thanh công thức: chắc chắn dùng được. **Không tự chế YAML điều khiển** khi chưa có mẫu do Studio sinh; khi IT có bản sao app, IT chép một điều khiển mẫu (View code > Copy code) gửi lại thì mới sinh YAML theo đúng mẫu đó (việc sau, TH). Công thức của `App.OnStart`/`App.Formulas` dán tay (App Object không dán YAML được).

### 8.3 Flow
- **Gói không thuộc solution** (ĐXM, learn.microsoft.com/power-automate/export-import-flow-non-solution): xuất `.zip` chỉ chủ hoặc đồng chủ flow; nhập cần vai trò **Environment Maker** ở môi trường đích; chọn "Create as new" hoặc "Update". Nguồn cộng đồng (TT-CXM): nút Import Package (Legacy) bị chặn khi quản trị bật "Create in Dataverse solutions".
- Hệ quả cho K2: giữ quyết định 3 của §9 (không tự chế `.zip`): IT dựng tay một flow `DaLam_<ClubId>` theo `T4M_FLOW_DA_LAM.md` §3, xuất gói, nhập lại cho từng CLB và đổi `Form Id` + hằng `ClubId` theo bảng do bộ dựng sinh. HỎI-IT: có quyền Environment Maker và legacy import có bị chặn không.

### 8.4 Chọn mặc định
- **List:** mặc định **B** nếu IT có quản trị SharePoint (một lần đăng ký, chủ site bấm áp; không cần app Entra), **A** nếu trường đã có app Entra cho PnP; lui **C** (không cần gì thêm). Cả ba từ cùng một tệp nguồn.
- **App:** công thức theo thuộc tính (mặc định); YAML điều khiển là việc sau.
- **Flow:** dựng tay một mẫu, nhân bản bằng gói.

Nguồn mục 8 (đọc 06/11/2026): learn.microsoft.com/sharepoint/dev/declarative-customization/site-design-json-schema; /site-design-overview; /get-started-create-site-design; /site-design-rest-api; support.microsoft.com/office/apply-and-customize-sharepoint-site-templates-39382463-0e45-4d1b-be27-0e96aeec8398; pnp.github.io/powershell/cmdlets/Invoke-PnPSiteScript.html; pnp.github.io/powershell/articles/registerapplication; learn.microsoft.com/power-apps/maker/canvas-apps/code-view; learn.microsoft.com/power-automate/export-import-flow-non-solution; support.microsoft.com/topic/380cfeb5-6e14-438e-988a-c2b9bea574fa (Create a list based on a spreadsheet). TT-CXM: o365reports.com (vai trò đăng ký app), cộng đồng Power Automate (legacy import bị chặn).
