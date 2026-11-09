# Phiếu thiết lập CLB trên Microsoft Forms (FA-M1) — TH: CHƯA thử trên Microsoft thật

Forms không có cách tạo biểu mẫu bằng chương trình, nên tài liệu này là **hướng dẫn dựng tay**. Phần chuyển tệp
(`chuyen_phieu_clb.py`) đã có test, nhưng chưa từng chạy với tệp xuất thật từ Forms (TH).

## 1. Dựng biểu mẫu (mỗi giáo viên phụ trách CLB nộp một phiếu cho mỗi CLB)

Tên câu hỏi **giữ đúng từng chữ** như cột dưới đây (tệp Excel xuất ra dùng chính tên câu hỏi làm tiêu đề cột).

| # | Tên câu hỏi (= tiêu đề cột) | Kiểu trong Forms | Bắt buộc | Rẽ nhánh |
|---|---|---|---|---|
| 1a | Tên CLB | Văn bản | Có | |
| 1b | Buổi | Lựa chọn (Thứ 2 … Thứ 6) | Có | |
| 1c | Giờ | Văn bản | Không | |
| 1d | Địa điểm | Văn bản | Không | |
| 2 | Mở thêm nhóm được nếu đông không? (Có/Không) | Lựa chọn: Có / Không | Có | Có → câu "Sức chứa mỗi nhóm"; Không → "Số chỗ tối đa" |
| 2a | Sức chứa mỗi nhóm | Số | Có (nhánh Có) | |
| 2b | Số chỗ tối đa | Số | Có (nhánh Không) | |
| 2c | Lý do giới hạn | Văn bản (phòng / dụng cụ / người hướng dẫn) | Có (nhánh Không) | |
| 3 | Số thành viên tối thiểu | Số | Có | |
| 4 | Cần kỹ năng tối thiểu không? (Có/Không) | Lựa chọn: Có / Không | Có (nhánh Không) | Có → các câu 4a–4c |
| 4a | Loại thử thách | Lựa chọn: Trắc nghiệm / Video / Ảnh | Có (nhánh Có) | |
| 4b | Mốc tối thiểu (thang 10) | Số nguyên 1–10 | Có (nhánh Có) | |
| 4c | Bảng tiêu chí | Văn bản dài | Có (nhánh Có) | |
| 5 | Giữ chỗ (mã học sinh, cách nhau dấu phẩy) | Văn bản dài | Không | |

Forms chỉ rẽ nhánh theo **một** câu lựa chọn tại một thời điểm: dùng "Nhánh" sau câu 2, rồi sau câu 4. Cột của câu
bị bỏ qua sẽ để trống trong tệp xuất; bộ chuyển đổi chấp nhận điều đó. Nếu Forms của bạn không cho ép số nguyên,
bộ chuyển đổi vẫn kiểm lại và báo lỗi (xem bảng dưới).

## 2. Chuyển sang Sổ nhập

```bash
python mau_forms_thi_clb/chuyen_phieu_clb.py PHIEU_CLB.xlsx --ra ra/
# tuỳ chọn: --ky-truoc ky_truoc.csv   (cột name,buoi,capacity: CLB chưa nộp phiếu -> Giới hạn với chỉ tiêu kỳ trước)
```

Ra hai tệp: `SO_NHAP_CLB.xlsx` (sheet CLB có cột Loại, Điểm sàn, Tối thiểu, Sức chứa phòng + sheet "Giữ chỗ")
và `BAO_CAO_PHIEU_CLB.md`. Sổ này chỉ có sheet CLB; học sinh nạp ở bước đăng ký (FA-M3).

## 3. Quy tắc phân loại (V§4.1)

| Câu 2 | Câu 4 | Loại | Chỉ tiêu |
|---|---|---|---|
| Có | — | Tự do | = sức chứa mỗi nhóm |
| Không | Không | Giới hạn | = số chỗ tối đa |
| Không | Có | Tuyển chọn (chờ ban quản lý duyệt) | = số chỗ tối đa; điểm sàn = mốc tối thiểu |

## 4. Lỗi và cảnh báo

| Tình huống | Kết quả |
|---|---|
| Câu 2 trống; thiếu sức chứa/số chỗ; mốc ngoài 1–10 hoặc không nguyên | **Lỗi**: bỏ CLB đó khỏi sổ, ghi trong báo cáo |
| Khai Tự do nhưng có "Lý do giới hạn" | Cảnh báo: CLB bị giới hạn thật không được khai Tự do |
| Giới hạn thiếu lý do; thử thách không phải trắc nghiệm; thiếu tiêu chí | Cảnh báo |
| Nộp nhiều lần cùng tên CLB | Lấy phiếu cuối, cảnh báo |
| Chưa nộp phiếu (có trong `--ky-truoc`) | Giới hạn với chỉ tiêu kỳ trước, cảnh báo |
| Một buổi chưa có CLB Tự do, giữ chỗ vượt chỉ tiêu… | Lỗi chặn mở cổng (`fa_daa.kiem_truoc_fa`) |

Loại CLB khoá khi mở cổng đăng ký (V§4.1). Chưa có gì ở đây thay cho quyết định D8 (Power Apps hay Forms): đường nào
chọn thì phiếu này dùng chung.
