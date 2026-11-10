# T4M. Flow nhắc hạn đăng ký CLB (GAP-10, V§5.2, tuỳ chọn)

> Chỉ tài liệu + một công cụ (10/11/2026). Chưa thử trên Power Automate thật: mọi bước nhãn **TH** (chờ thử), tên hành
> động / công thức nhãn **GĐ** (giả định từ tài liệu Microsoft, chưa chạy). Số giới hạn nhãn **ĐXM** (đã xác minh,
> `T4M_KET_QUA_TAI_LIEU.md` NC-11..14). Không có dữ liệu thật, tenantId, URL app hay tên người.
> Gửi tay (Outlook / Teams) vẫn là đường mặc định; flow chỉ để đỡ công.

## 1. Nguyên tắc
1. **Chỉ connector chuẩn:** Office 365 Outlook, Teams, SharePoint, Schedule (Recurrence), thao tác dữ liệu có sẵn.
   Không HTTP, không connector Premium (`T4M_HUONG_DAN_THU.md` §11).
2. **Chủ flow là tài khoản dịch vụ của IT** (như `T4M_FLOW_GUI_GVCN.md` §1): **HỎI-IT**.
3. Flow không đọc điểm, số bốc thăm hay kết quả xếp. Nó chỉ biết: hạn đăng ký, danh sách lớp, ai đã nộp phiếu.
4. **Giới hạn 6.000 yêu cầu / người / ngày (ĐXM).** Mỗi email, mỗi tin Teams, mỗi lần đọc một dòng list là một yêu
   cầu. Trước mỗi lần chạy, ước lượng: số người nhận × số bước. Vượt → gộp (mục 4).

## 2. Ba lần nhắc theo lịch (TH)
| Lần | Khi nào | Gửi cho | Nội dung |
|---|---|---|---|
| N1 | lúc mở cổng đăng ký | cả khối (một email nhóm, **1 yêu cầu**) | đường dẫn biểu mẫu, hạn chót |
| N2 | hạn chót **−2 ngày** | cả khối (email nhóm) | còn 2 ngày; nhắc làm bài thử thách cho CLB Tuyển chọn |
| N3 | hạn chót **−3 giờ** | cả khối (email nhóm) | còn 3 giờ; phiếu nháp chưa nộp không được tính |

Dựng (GĐ): ba flow **Scheduled cloud flow**, mỗi flow một `Recurrence` chạy MỘT lần đúng giờ (hoặc một flow, trigger
hằng giờ + điều kiện `utcNow()` nằm trong khung giờ của N1/N2/N3). Hành động: `Send an email (V2)` tới **địa chỉ
nhóm** của khối (một yêu cầu thay vì hàng trăm). Múi giờ: đặt `Time zone` của Recurrence là giờ Việt Nam.

## 3. Nhắc riêng CLB Tuyển chọn chưa làm bài thử thách (×2, TH)
- Hai lần: cùng lúc N2 và N3. Danh sách người nhận = em đã tick thi CLB Tuyển chọn mà chưa có bài nộp (xuất từ Forms
  phần thi, IT lọc bằng Excel).
- Mỗi em một email là **1 yêu cầu / em / lần**: 300 em × 2 lần = 600 yêu cầu — trong giới hạn. Quá 3.000 em thì gửi
  qua GVCN (mục 4) thay vì gửi từng em.

## 4. Sau 3 ngày mà dưới 50 % đăng ký → danh sách cho GVCN
1. Xuất phiếu đăng ký (Forms → Excel) và danh sách lớp `DANH_SACH.csv` (`student_id, class_id, homeroom_email`).
2. Chạy công cụ (máy IT, không cần mạng):
   ```
   python mau_forms_thi_clb/danh_sach_chua_dang_ky.py DANH_SACH.csv DANG_KY.xlsx --ra chua_dang_ky
   ```
   Ra: `chua_dang_ky_<lớp>.csv` (chỉ mã học sinh và lớp của em chưa đăng ký), `tong_hop.csv` (tỉ lệ từng lớp, cờ
   `DUOI_50` khi < 50 %). Công cụ in số email một lần gửi cần (mỗi lớp một email) và **cảnh báo khi vượt 6.000**.
3. Gửi mỗi tệp cho đúng GVCN bằng flow **`T4M_FLOW_GUI_GVCN.md`** (cùng cách ghép tên tệp → email; khoá ghép là tên
   tệp đã làm sạch). Chỉ gửi lớp có cờ `DUOI_50`, hoặc mọi lớp còn em chưa đăng ký — nhà trường chọn.

## 5. Ước lượng yêu cầu (ví dụ MÔ PHỎNG: 1.500 em, 40 lớp)
| Việc | Yêu cầu |
|---|---|
| N1 + N2 + N3, email nhóm | 3 |
| Nhắc thử thách ×2, 300 em | 600 |
| Danh sách GVCN, 40 lớp (đọc 40 tệp + 40 email) | ≈ 80 |
| **Tổng một đợt** | **≈ 683 < 6.000** |
Nếu gửi riêng cho từng em ở cả ba lần nhắc: 1.500 × 3 = 4.500 — sát giới hạn khi cộng các flow khác của cùng tài
khoản; vì vậy dùng email nhóm.

## 6. Chưa làm / hỏi IT
- Địa chỉ nhóm của khối, tài khoản dịch vụ, thư viện SharePoint: **HỎI-IT**.
- Thử thật cả ba lần nhắc trên một khối nhỏ trước: **TH**.
