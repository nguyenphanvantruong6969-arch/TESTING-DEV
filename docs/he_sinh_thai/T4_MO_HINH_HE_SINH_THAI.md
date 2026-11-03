# T4. Mô hình hệ sinh thái thu thập và quản lý dữ liệu (bản đề xuất để duyệt, sửa vòng 1)

Trạng thái: ĐỀ XUẤT, chưa triển khai, chờ Truong duyệt. Soạn 03/11/2026, sửa vòng 1 cùng ngày.
Phạm vi: thu thập đăng ký và thi tuyển CLB, quản lý, duyệt, xuất sang kiosk RB-DA.

> **Hai hạn chế (đọc trước).**
> 1. Phiên soạn bị chính sách mạng chặn nên **không mở được trang tham khảo của giáo viên** (`magenta-crepe-416060.netlify.app/dang-ky-clb`). Phần hiện trạng dựa trên mã và skill trong kho. Xem mục 2.2 và 16.
> 2. Không mở được trang hạn mức chính thức của Google, Microsoft, Supabase. Mọi số hạn mức và giá lấy từ **tóm tắt kết quả tìm kiếm**, mang nhãn **TT-CXM** = "CHƯA XÁC MINH (tóm tắt tìm kiếm, 03/11/2026)" kèm địa chỉ cần kiểm. Mọi nhận định về **hành vi** của Google Forms và Sheets mang nhãn **GĐ-n** (giả định chưa kiểm, bảng ở mục 3.2). Không con số hay hành vi nào trong tài liệu được khẳng định là đã đo.
>
> Thiết kế được chọn để vẫn đứng vững nếu các hạn mức sai lệch 2 lần (mục 9.3).

---

## 1. Tóm tắt điều hành (khuyến nghị trong 10 dòng)

1. Chọn **Phương án 1: Google** (Forms, Sheets, Apps Script, Drive). Chi phí 0 đồng, không máy chủ, quản trị viên không cần kỹ thuật.
2. **V1 gọn**: một Google Sheets mỗi đợt (và đối tượng) với sáu tab: `RAW` (tab của Forms, không script nào ghi vào), `hoc_sinh`, `clb`, `phieu` (một tab duyệt duy nhất), `nhat_ky`, `cau_hinh`, cộng một tab công thức `dieu_khien`.
3. **Không nhân đôi logic chấm.** Việc chấm và soát chỉ nằm ở `xu-li-raw-forms`. Admin không sửa câu trả lời: chỉ duyệt, từ chối, hoặc đổi phiếu nào được giữ (`ban_giu`). Câu trả lời sai thì học sinh nộp lại.
4. Apps Script **xử lý theo lô**, ghi `phieu` bằng upsert theo `raw_key`, dời con trỏ sau cùng: chạy lại hay bị ngắt ở phút thứ 6 không tạo bản trùng.
5. **Xuất = lọc RAW theo danh sách đã duyệt**, ghi thành **tệp riêng trên Drive** (RAW_PHIEU 19 cột cộng cột `lop`), không bao giờ là một tab, để ngân sách ô của Sheets chỉ chứa RAW dạng rộng và các tab nhỏ.
6. Lớp đến kiosk bằng thay đổi nhỏ trong kho (mục 11.2): cột thứ 20 `lop` lấy từ `hoc_sinh`, skill `xu-li-raw-forms` ghi vào cột Lớp của Sổ. Hợp đồng CSV của kiosk không đổi.
7. Việc quan trọng (chốt đợt, đổi phiếu giữ, từ chối) cần admin xác nhận trong hộp thoại và có dòng `nhat_ky`.
8. Ngưỡng chuyển sang Supabase đo được (mục 10). Microsoft bị loại vì Power Apps và Dataverse cần gói trả tiền.
9. Việc đầu tiên khi mở mạng: kiểm các trang ở mục 16.
10. Truong cần quyết các câu hỏi ở mục 14.2, trước hết là loại tài khoản Google của trường, và hai quyết định thiết kế DEC-1, DEC-2 ở mục 11.

---

## 2. Hiện trạng và trang tham khảo

### 2.1 Hiện trạng trong kho (đã đọc)

| Bước | Công cụ | Ghi chú |
|---|---|---|
| Dựng biểu mẫu | `TAO_GOOGLE_FORM.gs` | Top 1 đến Top 10 dạng thả xuống, tick tối đa 5 CLB thi, chỉ hiện đề CLB đã chọn, tự chấm |
| Thu thập | Google Forms | Học sinh nộp |
| Xuất raw | Hàm `chamTheoCLB` | Đọc `form.getResponses()`, tự bỏ phiếu trùng (giữ phiếu đầu), ra `RAW_PHIEU.xlsx` (dạng dài, 19 cột) và `DAP_AN.xlsx` trong thư mục Drive "Kết quả CLB ..." |
| Xử lý | `xu_li_raw.py` chạy trên máy | Chấm lại theo đáp án gốc, soát bất thường, ra `SO_NHAP_CLB.xlsx` |
| Nạp | Kiosk RB-DA | Nạp Sổ nhập, chạy xếp |

Khoảng trống: phải chép tay thư mục Drive về máy; không có nơi duyệt, từ chối từng phiếu; không có nhật ký; không có thông báo khi lỗi; chưa có khung nhiều đối tượng và nhiều đợt; không kiểm mã theo danh sách lớp trước khi nhận; Lớp chưa đi theo `RAW_PHIEU` nên Sổ nhập chưa có Lớp từ biểu mẫu.

### 2.2 Trang tham khảo của giáo viên: KHÔNG MỞ ĐƯỢC

Địa chỉ bị chặn (HTTP 403 ở bước CONNECT). Không có nội dung nào của trang được đọc, và tài liệu này **không suy đoán** trường, luồng hay giao diện của trang đó.

Đối chiếu trang tham khảo (làm khi mở được mạng):

| # | Việc cần kiểm | Dùng để quyết |
|---|---|---|
| 1 | Liệt kê trang con, nút, menu | Có phần quản trị hay chỉ có biểu mẫu |
| 2 | Từng trường: nhãn, kiểu (chữ, số, email, thả xuống, nhiều lựa chọn, tải tệp), bắt buộc hay không | So với yêu cầu loại trường |
| 3 | Kiểm tra đầu vào: định dạng mã, trùng mã, giới hạn số lựa chọn | So với mục 8 |
| 4 | Dữ liệu gửi đi đâu (Google Forms nhúng, Netlify Forms, API riêng, Sheets) | Tận dụng hay thay |
| 5 | Có giờ mở đóng, có chặn nộp khi đóng không | So với mở đóng theo giờ |
| 6 | Xác nhận sau khi nộp, có cho sửa phiếu không | Luồng người nộp, quy tắc "không sửa" |
| 7 | Tài khoản, đăng nhập hay ẩn danh | Vai trò, chống trùng |
| 8 | Chạy trên điện thoại, tốc độ tải | Đỉnh tải |
| 9 | Chỗ lưu và quota (Netlify: băng thông, số lần gửi biểu mẫu) | Chi phí ở 10.000 người nộp |
| 10 | Điểm đáng giữ lại (giao diện, chữ, bố cục) | "Nâng cấp trên nền cái cũ" |

---

## 3. Giả định

### 3.1 Quy mô (giả định thiết kế, không phải số đo)

Bốn đại lượng tách biệt:

| Đại lượng | Giả định | Cách dùng |
|---|---|---|
| Tổng người dùng đăng ký (có thể nộp) | 2.000 đến 10.000 mỗi chu kỳ | Cỡ `hoc_sinh` |
| Tổng phiếu nộp | Tối đa 1,3 phiếu mỗi người, tức **tối đa 13.000** | Cỡ `RAW` và `phieu` |
| Phiếu nộp đồng thời lúc đỉnh | 100 đến 300 phiếu trong phút đỉnh (1 đến 3% số người). **Không** giả định 10.000 cùng lúc | Đường nộp chỉ gồm Forms (GĐ-1, GĐ-2) |
| Khối lượng xử lý hằng ngày | Theo lô, mỗi lô trần 2 phút (mục 9.3) | Ngân sách trigger |

Vai trò: Submitter (học sinh, giáo viên) và Administrator (1 đến 2 người).

### 3.2 Giả định về hành vi Google (chưa kiểm, cần xác minh khi mạng mở)

| Mã | Giả định | Nếu sai thì |
|---|---|---|
| GĐ-1 | Google Forms hấp thụ được đỉnh nộp 100 đến 300 phiếu mỗi phút | Đợt thử đỉnh (mục 12); cân nhắc chia nhóm nộp theo lớp |
| GĐ-2 | Google tuần tự hoá việc ghi dòng vào tab phản hồi, không mất dòng | Đối soát số bấm Gửi với số dòng |
| GĐ-3 | Tab phản hồi chỉ được Google thêm dòng; script V1 không ghi vào. Sửa câu hỏi sau khi mở làm đổi cột | Quy tắc V1: không sửa biểu mẫu sau khi mở |
| GĐ-4 | Có đủ các loại trường: chữ, số, email, thả xuống, nhiều lựa chọn, tải tệp (số và email thực ra là chữ có kiểm tra định dạng) | Thu hẹp danh sách loại trường |
| GĐ-5 | Tuỳ chọn "cho phép sửa phản hồi" tắt được; tên đúng của tuỳ chọn cần kiểm | Phát hiện sửa bằng băm (mục 7.3) vẫn còn |
| GĐ-6 | Có hàm đóng nhận phản hồi (`setAcceptingResponses`) và đặt thông báo khi đóng | Đóng bằng tay |
| GĐ-7 | Dấu thời gian phản hồi độ phân giải giây, và giá trị ở tab phản hồi khớp `FormResponse.getTimestamp()` | Đổi cách ghép khoá ở bước xuất |
| GĐ-8 | Biểu mẫu kiểm tra được mã học sinh bằng biểu thức chính quy | Chỉ kiểm ở lô |
| GĐ-9 | "Giới hạn một phản hồi mỗi người" và tải tệp bắt buộc đăng nhập Google | Chống trùng chỉ theo mã học sinh (đã có) |
| GĐ-10 | Một lệnh `setValues` nhiều dòng có thể bị ngắt giữa chừng khi script bị dừng | Đã tính: ghi theo upsert, chạy lại an toàn (mục 7.2) |
| GĐ-11 | Sheets có lịch sử phiên bản dùng được làm lớp phụ cho nhật ký | Chỉ dựa vào `nhat_ky` |
| GĐ-12 | Ô trống trong lưới có thể vẫn tính vào trần ô | Quy tắc V1: xoá hàng và cột thừa |

---

## 4. Năm ưu tiên ràng buộc và cách thiết kế đáp ứng

| Ưu tiên | Cách đáp ứng |
|---|---|
| 1. Chi phí thấp | Chỉ dùng Forms, Sheets, Apps Script, Drive: 0 đồng với tài khoản Google sẵn có. Không dùng gói trả tiền |
| 2. Quản trị tối thiểu, không kỹ thuật | Bảng điều khiển là chính Sheets, menu có sẵn nút; mọi việc thường gặp tối đa 3 bước (mục 6.3); không cài đặt gì ngoài việc dán mã một lần |
| 3. Bảo trì thấp, không máy chủ | Không máy chủ, không cơ sở dữ liệu thứ hai; 4 trigger cố định; Google lo hạ tầng |
| 4. Tin cậy: không mất, không nhân đôi, không hỏng thầm lặng | RAW không script nào ghi; `phieu` là upsert theo `raw_key`; con trỏ dời sau cùng; băm phát hiện RAW bị sửa; đối soát số dòng; sao lưu hằng ngày (mục 8) |
| 5. Mở rộng đơn giản | Mỗi đợt một Sheets, lưu trữ sau chốt; ngưỡng chuyển sang Supabase đo được (mục 10), tên bảng và cột giữ nguyên |

---

## 5. Ánh xạ yêu cầu sang thành phần

| Yêu cầu | Thành phần V1 | Ghi chú |
|---|---|---|
| 1. Tạo và quản lý biểu mẫu | Google Forms sinh bằng `TAO_GOOGLE_FORM.gs` (đã có) | |
| 1. Nhiều đối tượng, nhiều đợt | Mỗi (đợt, đối tượng) một Sheets, đặt tên `<năm>_<đợt>_<đối tượng>` trong một thư mục Drive; thông số đợt nằm ở `cau_hinh`. Không có sổ đăng ký đợt riêng | Tránh kho thứ hai |
| 1. Loại trường | Chữ, số, email, thả xuống, nhiều lựa chọn (GĐ-4); tải tệp hoãn sang sau V1 (GĐ-9) | |
| 1. Mở, đóng biểu mẫu | Hai trigger theo giờ đã đặt trong `cau_hinh` gọi hàm đóng nhận phản hồi (GĐ-6) | |
| 1. Kiểm tra đầu vào | Kiểm tra ở biểu mẫu (GĐ-8) và ở lô (mục 8) | |
| 1. Hạn chế trùng | Giữ phiếu có dấu thời gian sớm nhất của mỗi mã (`ban_giu`), phiếu sau là `bo_nop_trung` | Khớp luật skill |
| 2. Kho trung tâm, tìm, lọc, sửa | Một Sheets mỗi đợt; lọc bằng chế độ xem lọc; sửa chỉ ở `phieu` (trạng thái, lý do, `ban_giu`) | Không sửa câu trả lời |
| 2. Xuất Excel và CSV | Menu "Xuất": tệp RAW_PHIEU trên Drive (xlsx hoặc CSV); tải `phieu` bằng chức năng tải của Sheets | |
| 3. Bảng điều khiển, trạng thái | Tab `dieu_khien` (công thức) và menu tuỳ biến, mục 6.3 | |
| 3. Duyệt, từ chối, sửa | Menu duyệt hàng loạt, từ chối kèm lý do, đổi phiếu giữ | Mục 7.4 |
| 3. Phân quyền | Hai vai trò: Submitter, Administrator | Mục 6.2 |
| 3. Lịch sử và quyết định quan trọng | `nhat_ky` | Mục 6.1 |
| 4. Tự đồng bộ, tự động hoá | Trigger lô, xuất, sao lưu | Mục 7 |
| 4. Thông báo | Email lỗi, bản tóm tắt hằng ngày, báo khi lô ngừng chạy | Hạn mức email: TT-CXM |
| 4. Người duyệt cho quyết định quan trọng | Chốt đợt qua hộp thoại xác nhận | |
| 5. Xuất cho phần mềm khác | Tệp RAW_PHIEU 19 cột cộng `lop` (V1), `DAP_AN.xlsx` có sẵn; skill ra Sổ nhập | Mục 11 |
| 5. API, tích hợp | V1 dùng tệp (kiosk ngoại tuyến); API `doGet` thuộc mục hoãn | |
| 5. Cấu trúc nhất quán | Tên tab, cột cố định (mục 6.1); chuyển Supabase giữ nguyên | |

---

## 6. Kiến trúc và mô hình dữ liệu

### 6.0 Kiến trúc

![Kiến trúc hệ sinh thái](anh/a_kien_truc.png)

Đầu ra V1 (thống nhất ở mục 5, 11, 13 và sơ đồ này): **một tệp RAW_PHIEU trên Drive** (cột `lop` thêm vào), `DAP_AN.xlsx` có sẵn; Sổ nhập do skill ra ngoại tuyến. Không có tab xuất.

### 6.1 Mô hình dữ liệu

![ERD](anh/d_erd.png)

Một Google Sheets mỗi (đợt, đối tượng). Một cơ sở dữ liệu duy nhất.

| Tab | Cột | Khoá | Ghi chú |
|---|---|---|---|
| `RAW` (tab phản hồi do Forms nối vào) | `thoi_gian`, các cột câu hỏi (cột `student_id` là mã học sinh học sinh tự gõ), có thể có email | Không có cột khoá riêng. Khoá logic tính ra ở `phieu` (`raw_key`) | Dạng rộng, một dòng mỗi phiếu. **Không script nào ghi vào** (GĐ-3). Bảo vệ ở mức cảnh báo. Quy tắc: không sắp xếp hay lọc tại chỗ, dùng chế độ xem lọc |
| `hoc_sinh` | `ma_hs`, `ho_ten`, `lop` | PK `ma_hs` | Admin nhập danh sách lớp. Dữ liệu thật của học sinh, không đưa vào kho mã. Ánh xạ `ma_hs` sang `student_id` khi xuất |
| `clb` | `club_id`, `ten`, `buoi`, `chi_tieu` | PK `club_id` | Chỉ tiêu do nhà trường lập. Dùng khi nạp Sổ nhập, không có khoá ngoại tới `phieu` |
| `phieu` (tab duy nhất đã xử lý) | `raw_key`, `ma_hs`, `trang_thai`, `ly_do`, `ban_giu`, `nguoi_duyet`, `thoi_gian_duyet` | PK `raw_key` | Một dòng mỗi dòng RAW. `ma_hs` tuỳ chọn trỏ tới `hoc_sinh` (trạng thái `ma_la` thì không khớp) |
| `nhat_ky` | `log_id`, `thoi_gian`, `nguoi`, `hanh_dong`, `doi_tuong`, `ly_do` | PK `log_id` | Chỉ thêm dòng. `doi_tuong` tuỳ chọn: `raw_key`, `ma_hs` hoặc `ky`. Ghi lỗi lô, quyết định quan trọng, lần xuất |
| `cau_hinh` | `khoa`, `gia_tri` | PK `khoa` | Thông số đợt (`ky_id`, `ten`, `doi_tuong`, `mo`, `dong`, `form_id`, `trang_thai_ky`), con trỏ, cửa sổ chạy lô, địa chỉ email, cờ `ghi_do` |
| `dieu_khien` | Công thức | không | Chỉ là hiển thị, không lưu dữ liệu |

`raw_key` = `<dấu thời gian phản hồi>|<ma_hs chuẩn hoá>|<băm 8 ký tự nội dung dòng RAW>` (GĐ-7). **Không** dùng số dòng, vì sắp xếp, chèn hay xoá dòng làm số dòng đổi. `raw_key` nằm ở `phieu`, không nằm ở RAW.

Trạng thái `phieu.trang_thai`:

| Giá trị | Ý nghĩa | Vào xuất? |
|---|---|---|
| `cho_duyet` | Hợp lệ, chờ admin | Không |
| `da_duyet` | Admin đã duyệt | Có, nếu `ban_giu = 1` |
| `tu_choi` | Admin từ chối, có lý do | Không |
| `bo_nop_trung` | Mã đã có phiếu giữ, đây là phiếu sau (`ban_giu = 0`) | Không |
| `ma_la` | Mã không có trong `hoc_sinh` (khác `bo_khong_ma`) | Không, đến khi admin xử lý |
| `bo_khong_ma` | Không có mã học sinh | Không |
| `raw_doi` | Dòng RAW đã bị sửa hoặc mất so với lúc xử lý (phát hiện bằng băm) | Không, đến khi admin xử lý |

`ban_giu` = 1 cho phiếu được giữ của mỗi `ma_hs`, 0 cho phiếu còn lại.

### 6.2 Vai trò và bảo mật

- **Submitter**: chỉ có đường dẫn biểu mẫu, không có quyền vào Sheets.
- **Administrator**: 1 đến 2 người được chia sẻ quyền sửa. Không có vai trò thứ ba.
- Tab RAW và `nhat_ky` được bảo vệ ở mức cảnh báo; Apps Script chỉ thêm dòng vào `nhat_ky` và không ghi vào RAW.
- Giới hạn biểu mẫu theo tên miền và việc bắt đăng nhập: GĐ-9, câu hỏi mở 1 và 2.

### 6.3 Trải nghiệm quản trị

**Bảng điều khiển hợp nhất** (tab `dieu_khien`, toàn công thức đếm trên `phieu`, không lưu dữ liệu):
- Số lượng theo trạng thái: `cho_duyet`, `da_duyet`, `tu_choi`, `bo_nop_trung`, `ma_la`, `bo_khong_ma`, `raw_doi`, mỗi trạng thái một màu.
- Đối soát: số dòng RAW so với số dòng `phieu`; lệch thì ô chuyển đỏ.
- Tình trạng lô: giờ chạy thành công gần nhất, số phút kể từ đó, lỗi gần nhất.
- Trạng thái đợt và thời gian còn lại đến giờ đóng.
- Số CLB còn thiếu chỉ tiêu trong `clb`.
- Lần xuất gần nhất: giờ, số phiếu, liên kết tệp.

**Số bước cho các việc chính** (đề xuất, cần thử với admin thật):

| Việc | Số bước |
|---|---|
| Duyệt hàng loạt các phiếu hợp lệ | 3: mở chế độ xem lọc `cho_duyet`, chọn các dòng, menu "Duyệt" (có thêm nút "Duyệt tất cả phiếu hợp lệ" kèm số lượng xác nhận) |
| Xử lý một phiếu lỗi (`ma_la`, `raw_doi`) | 3: chọn dòng, menu "Từ chối", nhập lý do. Riêng `ma_la` còn cách khác: thêm học sinh vào `hoc_sinh` rồi bấm "Xử lý lại phiếu mã lạ" (lô đánh giá lại các dòng `ma_la`) |
| Đổi phiếu giữ cho một học sinh | 3: chọn phiếu muốn giữ, menu "Giữ phiếu này", xác nhận |
| Chốt đợt | 2: menu "Chốt đợt", xác nhận |
| Xuất | 1: menu "Xuất RAW_PHIEU" (tự chạy sau khi chốt) |
| Xem lỗi | 1: bấm liên kết trong email, mở `nhat_ky` |

**Thao tác hàng loạt**: duyệt, từ chối kèm một lý do chung cho nhiều dòng, tải danh sách.
**Thông báo lỗi**: email khi lô lỗi (tối đa một email mỗi giờ), bản tóm tắt hằng ngày khi đang mở (phiếu mới, chờ duyệt, lỗi), cảnh báo khi lô ngừng chạy hơn một giờ.
**Dấu vết kiểm toán**: `nhat_ky` cho quyết định quan trọng; `phieu` giữ `nguoi_duyet` và `thoi_gian_duyet` của từng phiếu; lịch sử phiên bản của Sheets là lớp phụ (GĐ-11).

---

## 7. Luồng xử lý

### 7.1 Luồng nộp phiếu, kiểm tra, bỏ trùng, thử lại

![Luồng nộp phiếu](anh/b_nop_phieu.png)

### 7.2 Bảo đảm của lô: không trùng, an toàn khi bị ngắt

- **Một trigger, một cửa sổ.** Trigger lô chạy mỗi 10 phút, nhưng việc đầu tiên là đọc `cau_hinh`: ngoài cửa sổ (từ giờ mở đến giờ đóng cộng 2 giờ) thì thoát ngay. Hết cửa sổ, lô tự xoá trigger của chính nó.
- **Khoá**: `LockService` khoá script, một lô tại một thời điểm.
- **Con trỏ vị trí cộng điểm gác.** Con trỏ lưu số dòng RAW đã xử lý và dấu thời gian của dòng cuối đã xử lý. Mỗi lô kiểm dòng tại vị trí con trỏ còn đúng dấu thời gian đó. Lệch nghĩa là RAW đã bị sắp xếp hoặc xoá dòng: lô dừng, ghi `nhat_ky`, email admin.
- **Upsert theo `raw_key`.** Lô đọc tập `raw_key` đã có ở `phieu`, chỉ ghi các khoá chưa có, ghi từng khối ≤ 500 dòng. `raw_key` chưa có thì thêm; đã có thì bỏ qua. Con trỏ chỉ dời **sau cùng**, khi toàn bộ khối đã ghi.
- **Lô bị ngắt ở phút thứ 6** (hoặc ghi dở, GĐ-10): con trỏ chưa dời nên lần chạy sau đọc lại từ vị trí cũ, tính lại `raw_key`, bỏ qua dòng đã có và làm nốt dòng chưa có. Không có bản trùng. Phiếu ghi dở nếu có dòng hỏng thì lần sau bị bỏ qua do khoá đã có; việc đối soát số dòng (mục 8) bắt lệch.
- **Trần thời gian lô**: 2 phút; chạm trần thì dừng ở ranh giới khối, dời con trỏ đến khối cuối đã ghi xong, để lô sau làm tiếp.

### 7.3 Dòng RAW bị sửa

- V1 tắt "cho phép sửa phản hồi" (GĐ-5), và quy tắc vận hành: không sắp xếp, lọc tại chỗ hay sửa tab RAW.
- Nếu vẫn có sửa, lô phát hiện: `raw_key` cũ của phiếu không còn khớp dòng RAW nào (hoặc cùng dấu thời gian và mã nhưng băm khác). Phiếu đó được đặt `raw_doi`, và dòng RAW mới (nếu có) xử lý như phiếu mới. Admin quyết, không xuất tự động.
- Trước khi chốt đợt, lô kiểm lại **toàn bộ** băm RAW một lần (chia khối nếu cần), để bắt sửa nằm ở vị trí trước con trỏ.

### 7.4 Bỏ trùng và đổi phiếu giữ

- "Đầu" = dấu thời gian phản hồi sớm nhất của `ma_hs` trong đợt, **khớp luật của skill** (giữ phiếu đầu của mỗi mã).
- Lô chỉ đặt `ban_giu` cho dòng **mới**: nếu `ma_hs` đã có dòng `ban_giu = 1` thì dòng mới là `bo_nop_trung` và `ban_giu = 0`; chưa có thì `ban_giu = 1`. Lô không bao giờ đổi `ban_giu` của dòng cũ, nên quyết định của admin không bị ghi đè.
- Học sinh nộp lại để sửa câu trả lời: phiếu sau mặc định là `bo_nop_trung`. Admin đổi bằng menu "Giữ phiếu này": phiếu được chọn thành `ban_giu = 1`, `trang_thai = cho_duyet`; phiếu giữ trước thành `ban_giu = 0`, `bo_nop_trung`; ghi một dòng `nhat_ky` (ai, lúc nào, hai `raw_key`, lý do). Nếu đã xuất rồi thì xuất lại (mỗi lần xuất là một tệp mới có giờ trong tên, không ghi đè; kiosk dùng tệp mới nhất).
- Báo cáo của skill sẽ **ít phiếu trùng hơn trước**, vì xuất đã được lọc sẵn. Nơi chứa các bất thường nay là tab `phieu`; báo cáo của skill vẫn bắt các lỗi khác (đáp án lệch, một email nhiều mã, thiếu xếp hạng).
- Mã học sinh không có trong `hoc_sinh` là `ma_la`; không có mã là `bo_khong_ma`. Các dòng `ma_la`, `bo_khong_ma`, `raw_doi` có `ban_giu = 0` cho đến khi xử lý; khi một dòng `ma_la` được đánh giá lại thành hợp lệ, nó đi vào quy tắc giữ phiếu đầu như dòng mới.

### 7.5 Luồng duyệt và xuất sang kiosk

![Duyệt và xuất](anh/c_duyet_xuat.png)

---

## 8. Độ tin cậy

| Rủi ro | Biện pháp |
|---|---|
| Mất phiếu thầm lặng | RAW do Google ghi (GĐ-2), script không ghi vào; đối soát số dòng RAW với số dòng `phieu`; lệch thì ô điều khiển đỏ và email |
| Nhân đôi phiếu | `raw_key` duy nhất, upsert; mã trùng chỉ giữ phiếu đầu (mục 7.4) |
| **Xác thực đầu vào** | Ba lớp. (1) Biểu mẫu: bắt buộc, giới hạn số lựa chọn, kiểm mã bằng biểu thức chính quy (GĐ-8). (2) Lô: mã có trong `hoc_sinh`, trùng, băm RAW. (3) Xuất: skill soát bằng `soat()` (9 điều bắt buộc của phần mềm) và thử nạp Sổ bằng phần mềm thật |
| Hỏng dữ liệu | RAW không sửa; sửa ở `phieu` có `nguoi_duyet`, `thoi_gian_duyet` và dòng `nhat_ky` cho quyết định quan trọng |
| Nộp đồng thời | Forms hấp thụ (GĐ-1, GĐ-2); lô dùng khoá script, một lô tại một thời điểm |
| Vượt hạn mức tự động hoá | Ngân sách mục 9.3 và theo dõi trên trang Executions |
| Đồng bộ lỗi | Chạy lại an toàn (mục 7.2); email sau 3 lô liên tiếp lỗi |
| Nhất quán | Mỗi lô: ghi `phieu`, rồi `nhat_ky` nếu có lỗi, rồi dời con trỏ |
| Sao lưu và khôi phục | Một trigger hằng ngày chép toàn bộ Sheets sang thư mục Drive riêng, giữ 14 bản (số 14 là thiết kế); thêm một bản gắn nhãn khi **chốt đợt** và một nút "Sao lưu ngay". Sao lưu mỗi giờ: hoãn (xem mục 13.2) |
| Chỉnh nhầm tab RAW | Hoàn nguyên từ lịch sử phiên bản (GĐ-11) hoặc bản sao lưu; dựng lại `phieu` từ RAW bằng cách xoá `phieu` và chạy lô lại (mất quyết định duyệt đến lần sao lưu gần nhất) |

---

## 9. Hạn mức, kích cỡ và biên an toàn

### 9.1 Bảng hạn mức và nguồn

Tất cả: **Trạng thái nguồn = CHƯA XÁC MINH (tóm tắt tìm kiếm, 03/11/2026)**. Chưa đọc trang gốc nào.

| Hạn mức | Số liệu trong tóm tắt | Nguồn chính thức cần kiểm | Nguồn trong kết quả tìm kiếm |
|---|---|---|---|
| Apps Script: thời gian một lần chạy | 6 phút | `developers.google.com/apps-script/guides/services/quotas` | `developers.google.com/apps-script/quotas` |
| Apps Script: tổng thời gian trigger mỗi ngày | 90 phút (tài khoản thường), 6 giờ (Workspace) | như trên | như trên |
| Apps Script: trigger mỗi người mỗi script | 20 | như trên | như trên |
| Apps Script: thực thi đồng thời | 30 mỗi người, 1.000 mỗi script | như trên | như trên |
| Sheets API đọc và ghi mỗi phút | 300 và 300 mỗi dự án; 60 và 60 mỗi người mỗi dự án; quá thì lỗi 429; một nguồn nói tương lai có thể tính phí. V1 dùng `SpreadsheetApp`, chưa phụ thuộc | `developers.google.com/workspace/sheets/api/limits` | `developers.google.com/sheets/api/limits` |
| Trần ô Google Sheets | 10 triệu (thông báo 2022); một nguồn nói 20 triệu, chưa kiểm | trang giới hạn của Google Sheets trên `support.google.com` (địa chỉ chính xác chưa biết) | `workspaceupdates.googleblog.com/2022/03/ten-million-cells-google-sheets.html` |
| Google Forms nối Sheets | Báo cáo lẻ: Sheets nối ngừng nhận ở khoảng 100.000 phiếu | trang trợ giúp Google Forms | `blog.g-gen.co.jp/entry/limit-for-google-forms-spreadsheet-sync` (thứ ba) |
| LockService | `waitLock` báo lỗi khi hết giờ chờ; `tryLock` trả false; web app độc lập dùng khoá script. Chưa thấy trần thời gian khoá | `developers.google.com/apps-script/reference/lock/lock-service` | cùng trang |
| Email `MailApp` mỗi ngày | Chưa tìm được | trang quota Apps Script | không có |
| Microsoft Forms connector | 300 lệnh gọi mỗi kết nối trong 60 giây; một nguồn nói chu kỳ thăm 86.400 giây (nghi ngờ) | `learn.microsoft.com/en-us/connectors/microsoftforms/` | cùng trang |
| Power Automate miễn phí | Luồng tắt sau 90 ngày không kích hoạt (nguồn cộng đồng); hạn mức hành động mỗi ngày: chưa tìm được | `learn.microsoft.com/en-us/power-automate/limits-and-config` | `powerusers.microsoft.com` (không chính thức) |
| Microsoft Forms số phản hồi | 200 đến 5.000.000 tuỳ gói (thứ ba) | trang Forms của Microsoft | `gappsy.com/tools/microsoft-forms/` |
| Supabase miễn phí | 500 MB cơ sở dữ liệu, 5 GB egress, 1 GB tệp, 50.000 MAU, 2 dự án, tạm dừng sau 1 tuần không hoạt động, không sao lưu tự động | `supabase.com/pricing`; `supabase.com/docs/pricing` | cùng trang |
| Supabase Pro | 25 đô mỗi tháng; 8 GB đĩa; 250 GB băng thông (một nguồn thứ ba nói 50 GB, mâu thuẫn); sao lưu hằng ngày giữ 7 ngày | như trên | như trên |

Google nói hạn mức "có thể đổi hoặc bỏ bất cứ lúc nào, không báo trước" (theo tóm tắt, TT-CXM).

### 9.2 Ngân sách ô cho 13.000 phiếu (tối đa)

Bố cục: tab `RAW` dạng rộng, một dòng mỗi phiếu, mỗi câu hỏi một cột.

| Thành phần | Công thức | Điển hình (C = 220) | Xấu nhất (C = 400) |
|---|---|---|---|
| `RAW` | 13.000 phiếu nhân C cột | 2,86 triệu | 5,20 triệu |
| `phieu` | 13.000 nhân 7 cột | 0,09 triệu | 0,09 triệu |
| `hoc_sinh` | 10.000 nhân 3 cột | 0,03 triệu | 0,03 triệu |
| `nhat_ky` | giả định 5.000 dòng nhân 6 cột | 0,03 triệu | 0,03 triệu |
| `clb`, `cau_hinh`, `dieu_khien` | nhỏ | dưới 0,02 triệu | dưới 0,02 triệu |
| **Tổng** | | **khoảng 3,0 triệu** | **khoảng 5,4 triệu** |

Nguồn của C: **C = 220** là ước tính cho biểu mẫu mẫu 50 CLB (khoảng 100 câu đề thi, 65 câu đăng ký và xếp hạng của 5 buổi, tối đa 50 câu chọn thi tiếp), chưa đếm từ biểu mẫu thật. **C = 400** là ngưỡng mà skill `tao-google-form-clb` nói nên chia hai biểu mẫu (khoảng 400 câu hỏi). Số phiếu 13.000 là giả định ở mục 3.1.

So với trần 10 triệu (TT-CXM): điển hình dư 3,3 lần; xấu nhất dư 1,9 lần.
**Nếu trần thật chỉ bằng một nửa (5 triệu):** điển hình vẫn đủ (3,0 dưới 5), **xấu nhất không đủ** (5,4 trên 5). Vì vậy quy tắc V1: tích số phiếu tối đa nhân số cột RAW không vượt 4,5 triệu, tức với 13.000 phiếu thì **không quá khoảng 340 câu hỏi mỗi biểu mẫu**, vượt thì chia hai biểu mẫu theo nhóm buổi. Xoá hàng và cột thừa của lưới (GĐ-12).

Tệp xuất dạng dài là tệp **riêng**, không tính vào Sheets của đợt. Dạng dài có số ô lớn: giả định 40 dòng mỗi phiếu nhân 20 cột, 13.000 phiếu là khoảng 10 triệu ô. Vì vậy V1 xuất CSV ghi thẳng vào Drive bằng `DriveApp` thay vì dựng bảng tạm, hoặc tách phần (mục 11.3). Con số 40 dòng mỗi phiếu là giả định, cần đếm trên biểu mẫu mẫu.

### 9.3 Ngân sách trigger và biên 2 lần

Quy tắc: ngân sách thiết kế không quá **một phần ba** hạn mức thấp nhất nghe được.

Bốn trigger cố định (so với trần 20 mỗi người mỗi script: TT-CXM): (1) lô mỗi 10 phút, chỉ chạy trong cửa sổ mở; (2) một trigger hằng ngày: sao lưu cộng cảnh báo lô ngừng cộng bản tóm tắt; (3) hai trigger một lần đặt giờ mở và giờ đóng (tính là hai).

Tính cho ngày xấu nhất: biểu mẫu mở cả 24 giờ và đỉnh nằm **trong** giờ mở (không cộng chồng):

| Hạng mục | Cách tính | Phút trigger mỗi ngày |
|---|---|---|
| Lô lúc bận | 8 lô bận mỗi ngày nhân trần 120 giây | 16,0 |
| Lô nhàn (không có dòng mới, thoát nhanh) | 144 lô tổng cộng trừ 8 bận là 136 nhân khoảng 3 giây (giả định) | 6,8 |
| Sao lưu và cảnh báo hằng ngày | 1 lần nhân khoảng 90 giây (giả định) | 1,5 |
| Mở, đóng đợt | 2 lần nhân khoảng 10 giây (giả định) | 0,3 |
| **Tổng** | | **khoảng 24,6** |

Kết quả 24,6 phút dưới mức 30 phút (một phần ba của 90 phút, TT-CXM). Nếu hạn mức thật là 45 phút thì mức dùng là 55%, vẫn đủ. Các giả định 3 giây, 90 giây, 8 lô bận phải đo ở đợt thử (mục 12). Cửa sổ chạy lô được kiểm trong `cau_hinh` nên ngoài giờ mở không tốn thời gian trigger đáng kể. Lần xuất bằng tay do admin bấm tính theo hạn mức thực thi thủ công, chưa có số (TT-CXM chưa tìm được).

| Hạn mức (số trong tóm tắt, TT-CXM) | Mức dùng thiết kế | Nếu hạn mức thật bằng một nửa |
|---|---|---|
| Trigger 90 phút mỗi ngày | 24,6 phút | Nửa là 45: dư |
| 6 phút mỗi lần chạy | Trần lô 2 phút | Nửa là 3 phút: dư |
| 20 trigger mỗi người mỗi script | 4 trigger | Nửa là 10: dư |
| Trần ô 10 triệu | 3,0 triệu điển hình, 5,4 triệu xấu nhất | Nửa là 5 triệu: điển hình dư, xấu nhất không đủ, nên có quy tắc 340 câu hỏi ở 9.2 |
| Thực thi đồng thời | Một lô, khoá script | Không phụ thuộc |

---

## 10. Ngưỡng chuyển đổi đo được (từ Sheets sang Supabase)

![Ngưỡng chuyển đổi](anh/e_chuyen_doi.png)

| # | Ngưỡng | Cách đo |
|---|---|---|
| 1 | Độ trễ đồng bộ p95 quá 30 phút, 3 ngày liên tiếp | Trong đợt thử bật cờ `ghi_do` ở `cau_hinh`: mỗi lô ghi một dòng `nhat_ky` loại "đo" (giờ nộp của dòng mới nhất, giờ xử lý xong). Tắt ở đợt thật nếu đủ số liệu |
| 2 | Thời gian trigger dùng quá 50% hạn mức đã xác minh | Trang Executions của Apps Script, cộng thời gian mỗi ngày |
| 3 | Lỗi khoá hoặc lỗi 429 quá 1% số lần chạy lô | Đếm dòng lỗi trong `nhat_ky` so với tổng lần chạy |
| 4 | Số ô quá 50% giới hạn đã xác minh, hoặc bảng điều khiển tải quá 10 giây | Đếm ô; đo bằng đồng hồ với 13.000 dòng |
| 5 | Cần truy vấn quan hệ nhiều bảng mà bộ lọc và công thức không làm nổi | Ghi yêu cầu thật của admin; hai lần liên tiếp thì tính |

Trước khi chuyển: thử biện pháp rẻ (lô nhỏ hơn, tách Sheets theo nhóm buổi, lưu trữ đợt cũ). Chuyển V2 chỉ khi vẫn vượt sau một đợt đo lại; V2 giữ nguyên tên bảng và cột. Các ngưỡng 30 phút, 50%, 1%, 10 giây là quyết định thiết kế cần Truong duyệt, chưa dựa trên số đo.

---

## 11. Đầu ra, tích hợp và thay đổi cần trong kho

Hợp đồng cột kiosk (CLAUDE.md, bất biến 7): `club_id, student_id, test_club_k, score_k, pref_k, <buoi>_pref_k`, cùng Lớp (cột Lớp đã có trong `so_nhap.py`, mục A14). V1 **không đổi hợp đồng này**.

Đầu ra V1: một tệp `RAW_PHIEU` (CSV hoặc xlsx) trên Drive, `DAP_AN.xlsx` sẵn có, rồi `xu_li_raw.py` ra `SO_NHAP_CLB.xlsx`. Phiếu `tu_choi`, `bo_nop_trung`, `ma_la`, `raw_doi` không vào tệp xuất. Mỗi lần xuất tạo tệp mới có giờ trong tên và ghi vào `nhat_ky` (số phiếu, id tệp).

Lọc: danh sách phiếu xuất là `trang_thai = da_duyet` và `ban_giu = 1`. Việc dựng dòng, chấm và cột `diem_forms` dùng lại mã của `chamTheoCLB` (hàm này hiện đọc `form.getResponses()` và tự bỏ trùng giữ phiếu đầu); cần một tham số "chỉ lấy các phiếu có `thoi_gian|ma_hs` trong danh sách đã duyệt", áp dụng **trước** khi bỏ trùng. Chưa đọc kỹ `chamTheoCLB` ở T4, cần xem trước khi triển khai có tái dùng được hay phải tách hàm.

### 11.1 DEC-1 (cho Truong chọn): nguồn dựng RAW_PHIEU

| Lựa chọn | Ưu | Nhược |
|---|---|---|
| **A (khuyến nghị)** Dựng từ `form.getResponses()` như `chamTheoCLB`, lọc theo danh sách duyệt, ghép bằng `thoi_gian|ma_hs` | Giữ đủ 19 cột kể cả `diem_forms`, không viết lại phần mở gói và chấm | Phụ thuộc dấu thời gian khớp giữa tab RAW và API Forms (GĐ-7) |
| B Dựng từ tab RAW, tách cột theo mã `[ma_cau]` ở tiêu đề | Cùng nguồn với lô | Mất `diem_forms` (mất bước so điểm Forms với đáp án gốc), phải viết lại phần mở gói |

### 11.2 Thay đổi cần trong kho (để Truong duyệt trước khi triển khai)

Cần đăng ký thành mục trong sổ (quy tắc làm việc 1 của CLAUDE.md), không làm trước khi được duyệt.

| # | Thay đổi | Tệp chạm | Ghi chú |
|---|---|---|---|
| 1 | **Lớp.** Thêm cột tuỳ chọn thứ 20 `lop` vào `RAW_PHIEU` (một giá trị cho mỗi dòng của phiếu, lấy từ `hoc_sinh` theo mã). `xu_li_raw.py` đọc cột này nếu có và ghi vào cột Lớp của Sổ. Thiếu cột thì hành vi **như cũ** (mặc định không đổi) | `mau_forms_thi_clb/DINH_DANG_RAW.md`, `.claude/skills/xu-li-raw-forms/scripts/xu_li_raw.py` và `SKILL.md`, `tests/test_skill_xu_li_raw.py`, `CHANGELOG.md` | Không đụng hợp đồng CSV của kiosk, vì Sổ đã có cột Lớp (A14). Đụng hợp đồng RAW, nên phải đồng bộ tài liệu, skill và test cùng lúc |
| 2 | Hàm Apps Script mới: lô (`xuLyLo`), menu quản trị, xuất theo danh sách duyệt. Thêm vào khuôn `tao_google_forms.py` và `TAO_GOOGLE_FORM.gs` | `mau_forms_thi_clb/tao_google_forms.py`, `TAO_GOOGLE_FORM.gs`, `.claude/skills/tao-google-form-clb/`, `tests/test_skill_tao_google_form.py` | Skill nói `mau` rồi `tao` phải ra tệp giống hệt `TAO_GOOGLE_FORM.gs`: cập nhật cả hai cùng lúc |
| 3 | (Chỉ khi đợt thử cho thấy cần) `xu_li_raw.py` nhận nhiều phần `--raw` hoặc một thư mục các phần CSV cùng tiêu đề | `xu_li_raw.py`, test | Chỉ cần khi một tệp xuất vượt giới hạn bộ nhớ hoặc thời gian |

**Khuyến nghị cho Lớp (DEC-2):** lấy `lop` từ `hoc_sinh` lúc xuất (thay đổi số 1), **không** thêm câu hỏi "Lớp" vào biểu mẫu. Lý do: không thêm trường cho học sinh gõ nên không lệch mã, một nguồn duy nhất, và `ma_la` đã chặn mã không có trong danh sách. Phương án còn lại (thêm câu hỏi "Lớp" bắt buộc) cần thêm một cột RAW, dễ gõ sai, và vẫn phải sửa `DINH_DANG_RAW.md` và skill như thay đổi số 1.

### 11.3 Xuất khối lượng lớn

Mặc định một tệp CSV dựng trong bộ nhớ theo khối rồi ghi bằng `DriveApp`. Nếu đo thấy vượt giới hạn bộ nhớ hoặc trần 6 phút (GĐ chưa kiểm), tách phần ≤ 2.000 phiếu (giả định) và áp dụng thay đổi số 3. Với đợt ≤ 2.000 người, chỉ một phần.

---

## 12. Mục tiêu hiệu năng và cách kiểm

Sáu chỉ số, bảy con số mục tiêu (chỉ số thứ sáu gồm RPO và RTO). Đây là **mục tiêu đề xuất**, không phải kết quả; chưa có số nào đạt hay đo được.

| # | Chỉ số | Mục tiêu đề xuất | Cách kiểm |
|---|---|---|---|
| 1 | Tỷ lệ nộp thành công | Từ 99,9% trở lên (bấm Gửi thành công và có dòng RAW) | Đợt thử với biểu mẫu thử, nhiều thiết bị; so số bấm Gửi với số dòng RAW. Không bắn tải giả vào biểu mẫu thật |
| 2 | Độ trễ đồng bộ (nộp đến vào `phieu`), p95 | Không quá 15 phút khi đang mở (chu kỳ 10 phút cộng trần lô 2 phút, cộng dự phòng) | Cờ `ghi_do` ở đợt thử, tính p95 |
| 3 | Tải bảng điều khiển | Không quá 5 giây với 13.000 dòng | Dựng Sheets thử có dữ liệu tổng hợp 13.000 dòng nhân số cột điển hình, mở bằng trình duyệt, đo 5 lần |
| 4 | Thời gian xuất | Không quá 5 phút cho 10.000 phiếu | Đo từ lúc bấm đến lúc có tệp (ý nghĩa: trần 6 phút mỗi lần chạy, TT-CXM) |
| 5 | Tỷ lệ lô thất bại | Dưới 1% số lần chạy, và không lỗi nào mà không có thông báo | Đếm dòng lỗi trong `nhat_ky` so với tổng lần chạy ở trang Executions |
| 6a | RPO | 24 giờ cho quyết định duyệt (sao lưu hằng ngày); RAW do Google lưu giữ | Kiểm tuổi bản sao lưu mới nhất |
| 6b | RTO | 4 giờ làm việc | Diễn tập một lần: giả vờ hỏng Sheets, khôi phục từ bản sao, đo thời gian |

Kiểm đỉnh tải: 100 đến 300 phiếu trong một phút bằng nhiều người thật hoặc biểu mẫu thử riêng, kiểm cả ghi RAW và lô sau đó (GĐ-1).

---

## 13. Danh sách V1, để sau, và không làm

### 13.1 Cần cho V1

- Biểu mẫu sinh bằng `TAO_GOOGLE_FORM.gs` (đã có); tắt sửa phản hồi (GĐ-5); không sửa biểu mẫu sau khi mở.
- Một Sheets mỗi (đợt, đối tượng) với `RAW`, `hoc_sinh`, `clb`, `phieu`, `nhat_ky`, `cau_hinh`, `dieu_khien`.
- Lô: cửa sổ chạy, khoá, con trỏ cộng điểm gác, upsert theo `raw_key`, kiểm mã, bỏ trùng giữ phiếu đầu, phát hiện RAW bị sửa.
- Menu quản trị: duyệt hàng loạt, từ chối kèm lý do, đổi phiếu giữ, chốt đợt có xác nhận, "Sao lưu ngay".
- Xuất tệp RAW_PHIEU lên Drive (19 cột cộng `lop`), nối `xu-li-raw-forms`.
- Sao lưu hằng ngày cộng một bản khi chốt; email lỗi và bản tóm tắt hằng ngày.
- Thay đổi kho số 1 và 2 (mục 11.2), sau khi Truong duyệt.
- Một đợt thử đo các chỉ số ở mục 12.

### 13.2 Để sau (kèm lý do)

| Hạng mục | Lý do hoãn |
|---|---|
| Tab `nguyen_vong` và `bai_thi` | Nhân đôi logic chấm và xếp hạng đã có ở skill; không có nhu cầu duyệt theo nguyện vọng trong V1 |
| Sao lưu mỗi giờ | Sao lưu một Sheets lớn mỗi giờ tốn thời gian trigger; hằng ngày cộng khi chốt đủ cho V1 (RPO 24 giờ cho quyết định duyệt). Bật lại nếu đợt thử cho thấy cần |
| Tab đo p95 thường trực | Cờ `ghi_do` ở đợt thử là đủ; tránh tab thêm |
| Ghi nhật ký trước và sau cho từng hành động | `phieu` đã giữ `nguoi_duyet`, `thoi_gian_duyet`; `nhat_ky` chỉ ghi quyết định quan trọng. Thêm khi có yêu cầu kiểm toán |
| Trang web quản trị riêng, trang tra cứu trạng thái cho học sinh | Sheets đủ cho 1 đến 2 admin |
| API `doGet` trả JSON có mã | Kiosk ngoại tuyến, tệp là đủ |
| Tải tệp | Cần đăng nhập Google, dùng Drive của chủ biểu mẫu (GĐ-9) |
| Sinh trực tiếp `SO_NHAP_CLB.xlsx` bằng Apps Script | Skill đã làm, có test |
| Chuyển Supabase | Chỉ khi chạm ngưỡng mục 10 |

### 13.3 Không làm trừ khi có nhu cầu thật

- Hệ thống đăng nhập tự viết, phân cấp quyền quá hai vai trò.
- Cơ sở dữ liệu hoặc máy chủ thứ hai chạy song song với Sheets.
- **Nhân đôi logic chấm điểm hay xếp hạng ngoài `xu-li-raw-forms`.**
- Bảng điều khiển thời gian thực, ứng dụng di động.
- Gói trả tiền (Power Apps, Dataverse, Supabase Pro) để lấy tính năng.
- Học máy phát hiện trùng, dịch vụ email tự dựng.
- Đa khách hàng (đa tenant): thuộc mục tổng quát hoá ngành khác, làm riêng sau.
- Sửa câu trả lời của học sinh trong hệ thống (học sinh nộp lại, admin đổi phiếu giữ).

---

## 14. Rủi ro và câu hỏi mở

### 14.1 Rủi ro

| Rủi ro | Mức | Giảm thiểu |
|---|---|---|
| Hạn mức Google khác số tóm tắt | Trung bình | Biên 2 lần (9.3); kiểm khi mạng mở |
| Quá nhiều cột RAW làm chạm trần ô | Cao nếu làm sai | Quy tắc 340 câu mỗi biểu mẫu (9.2), chia hai biểu mẫu |
| Dấu thời gian RAW và API Forms không khớp (GĐ-7) | Chưa biết | Kiểm sớm trong đợt thử; phương án B ở DEC-1 |
| Xuất khối lượng lớn vượt bộ nhớ hoặc 6 phút | Trung bình | Tách phần, thay đổi kho số 3 |
| Học sinh không có tài khoản Google | Chưa biết | Câu hỏi 1 và 2 |
| Một người giữ Sheets | Trung bình | Hai admin, bản sao lưu |
| Người sửa hoặc sắp xếp tab RAW | Thấp | Bảo vệ tab, điểm gác con trỏ, băm, bản sao lưu |
| Danh sách lớp thiếu hoặc sai | Trung bình | Danh sách lớp do nhà trường cung cấp, `ma_la` chặn mã lạ |
| Số liệu mô phỏng bị hiểu là số đo | Thấp | Mọi số ghi rõ là giả định hoặc mục tiêu |

### 14.2 Câu hỏi mở cho Truong

1. Trường dùng **Google Workspace for Education** hay Gmail thường? (Giới hạn theo tên miền, hạn mức trigger 6 giờ hay 90 phút.)
2. Học sinh **đăng nhập Google** khi điền được không?
3. Có cần tải tệp ở V1 không?
4. Bao nhiêu **đối tượng** và **đợt** mỗi năm?
5. Danh sách lớp (`hoc_sinh`) lấy từ đâu, ai nhập?
6. Ai là hai admin, ai nhận email lỗi?
7. Chốt đợt cần một hay hai người xác nhận?
8. Trang giáo viên có phần nào đáng giữ? (Cần mở mạng, mục 2.2.)
9. Đồng ý ngưỡng mục 10 và mục tiêu mục 12 không?
10. Trường có Microsoft 365 giáo dục không? (Chỉ để khẳng định việc loại Phương án 2.)
11. **DEC-1**: dựng RAW_PHIEU từ API Forms (A, khuyến nghị) hay từ tab RAW (B)?
12. **DEC-2**: Lớp lấy từ `hoc_sinh` lúc xuất (khuyến nghị) hay thêm câu hỏi "Lớp" vào biểu mẫu?
13. Duyệt đăng ký hai thay đổi kho ở mục 11.2 (số 1 và 2) thành mục trong sổ?

---

## 15. So sánh ba phương án (tóm tắt)

Mọi con số: TT-CXM, nguồn ở mục 9.1.

| Tiêu chí | 1. Google | 2. Microsoft | 3. Tự dựng nhẹ (web tĩnh, Supabase) |
|---|---|---|---|
| Giới hạn miễn phí | Trigger 90 phút hoặc 6 giờ mỗi ngày, 6 phút mỗi lần chạy, trần 10 triệu ô; Forms không có trần phiếu cố định, thực tế do Sheets nối | Forms connector 300 lệnh mỗi 60 giây; luồng miễn phí chỉ dùng connector chuẩn; hạn mức hành động mỗi ngày chưa tìm được | 500 MB, tạm dừng sau 1 tuần, không sao lưu; Pro 25 đô mỗi tháng |
| Chi phí ở 10.000 người | Dự kiến 0 đồng | 0 đồng với connector chuẩn; Power Apps, Dataverse trả tiền (không chọn) | 0 đồng chịu rủi ro tạm dừng; cần Pro nếu muốn sao lưu |
| Xử lý đỉnh tải | Forms hấp thụ (GĐ-1), Apps Script xử lý sau theo lô | Luồng kích hoạt từng phiếu dễ bị giới hạn tốc độ | Phải tự bảo đảm, không đo được ở đây |
| Toàn vẹn | Raw chỉ thêm; không khoá ngoại, phải tự kiểm | Kiểu cột của SharePoint | Mạnh nhất (ràng buộc, giao dịch) |
| Bảo mật | Chia sẻ theo email; theo tên miền nếu Workspace | Theo thuê bao Microsoft 365 của trường nếu có | Tự cấu hình đăng nhập, quy tắc truy cập |
| Bảo trì | Gần như không | Tuỳ có tenant giáo dục | Cao nhất, admin không kỹ thuật khó tự xử lý |
| Tích hợp kiosk | Tệp, dùng nguyên skill hiện có | Phải viết lại phần xử lý raw | API, thuận cho V2 |

Kết luận: Phương án 1 đáp ứng năm ưu tiên (mục 4) với ít việc phải tự viết nhất, vì đã có `TAO_GOOGLE_FORM.gs` và `xu_li_raw.py`. Phương án 3 là hướng chuyển khi chạm ngưỡng (mục 10).

---

## 16. Việc cần làm khi mở mạng

Cho phép các host sau trong cài đặt mạng của môi trường (hướng dẫn: `read_documentation`, mục `environment.network`), rồi kiểm:

| Host | Việc cần kiểm |
|---|---|
| `magenta-crepe-416060.netlify.app` | Toàn bộ checklist mục 2.2 |
| `developers.google.com` | Quota Apps Script (thời gian chạy, trigger, đồng thời, email, số lần gọi URL, giới hạn thủ công); Sheets API limits; LockService; hàm đóng nhận phản hồi; dấu thời gian phản hồi (GĐ-6, GĐ-7); lô và `setValues` có bị ngắt dở không (GĐ-10) |
| `support.google.com` | Trần ô của Google Sheets (10 hay 20 triệu) và ô trống có tính không (GĐ-12); giới hạn Forms (số phiếu, tải tệp, đăng nhập, một phản hồi mỗi người, tên tuỳ chọn sửa phản hồi, GĐ-5, GĐ-9); lịch sử phiên bản (GĐ-11) |
| `learn.microsoft.com` | Giới hạn Power Automate theo gói; connector Forms; giới hạn SharePoint Lists |
| `supabase.com` | Giá và giới hạn gói miễn phí; điều kiện tạm dừng; sao lưu |
| Dịch vụ lưu trữ web tĩnh của trang tham khảo (Netlify, nếu dùng) | Băng thông, số lần gửi biểu mẫu |

Sau khi kiểm: đổi nhãn TT-CXM và GĐ-n thành "ĐÃ XÁC MINH ngày ... từ <địa chỉ>"; tính lại mục 9.2 và 9.3; nếu số lệch quá 2 lần thì xem lại thiết kế.

---

## 17. Danh sách nguồn

Tất cả là nguồn **thứ cấp qua tìm kiếm** (chưa đọc trang gốc), truy xuất 03/11/2026.

Chính thức (địa chỉ cần kiểm):
- Apps Script quotas: https://developers.google.com/apps-script/guides/services/quotas và https://developers.google.com/apps-script/quotas
- Sheets API usage limits: https://developers.google.com/workspace/sheets/api/limits và https://developers.google.com/sheets/api/limits
- LockService: https://developers.google.com/apps-script/reference/lock/lock-service
- Google Sheets 10 triệu ô: https://workspaceupdates.googleblog.com/2022/03/ten-million-cells-google-sheets.html
- Microsoft Forms connector: https://learn.microsoft.com/en-us/connectors/microsoftforms/
- Power Automate limits (không có trong kết quả tìm kiếm, chỉ là nơi nên kiểm): https://learn.microsoft.com/en-us/power-automate/limits-and-config
- Supabase pricing: https://supabase.com/pricing và https://supabase.com/docs/pricing

Thứ ba, chỉ tham khảo, không dùng để chốt:
- https://folderpal.io/articles/google-apps-script-quotas-and-workarounds-2026-breaking-limits-on-drive-automation
- https://blog.g-gen.co.jp/entry/limit-for-google-forms-spreadsheet-sync
- https://fast.io/resources/google-sheets-row-limit.md
- https://www.usecarly.com/blog/google-forms-response-limit/
- https://gappsy.com/tools/microsoft-forms/
- https://powerusers.microsoft.com/t5/General-Power-Automate/Is-it-really-free-and-for-long/m-p/1461008
- https://www.cloudzero.com/blog/supabase-pricing/ và https://www.jetadmin.io/blog/supabase-pricing-2026-guide-to-plans-limits-and-real-world-costs/

Tệp trong kho: `.claude/skills/tao-google-form-clb/SKILL.md`, `.claude/skills/xu-li-raw-forms/SKILL.md`, `mau_forms_thi_clb/DINH_DANG_RAW.md`, `mau_forms_thi_clb/TAO_GOOGLE_FORM.gs` (hàm `chamTheoCLB`), `so_nhap.py` (cột Lớp, mục A14).

Nguồn sơ đồ: `anh/*.mmd` (Mermaid 10.9.1) cho sơ đồ b, c, d, e; `anh/a_kien_truc.svg` (SVG viết tay) cho sơ đồ a; PNG vẽ bằng Playwright.
