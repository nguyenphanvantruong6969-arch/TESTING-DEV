# Ghi chú cho giáo viên: dựng bài thi CLB trên Microsoft Forms (1 trang)

Em nộp nguyện vọng ở ứng dụng đăng ký của trường; **biểu mẫu này chỉ để làm bài thi**. Điểm được ghép với
nguyện vọng qua **Email** của em. Thầy cô chỉ cần làm 4 việc: nhập đề, tick đáp án, đặt Settings, phát link.

## 1. Nhập đề (Quick Import)
1. Nhờ người phụ trách dự án gửi tệp `NHAP_FORMS_CHI_THI.docx` (sinh từ `de_thi.json`; nếu đề dài hơn 200 câu sẽ có
   `_1`, `_2`… mỗi tệp là một biểu mẫu riêng).
2. Vào forms.office.com bằng tài khoản trường → **Quick import** → chọn tệp Word **từ ổ máy** (không chọn từ
   SharePoint/OneDrive), tối đa **10 MB** → chọn dạng **Quiz**.
3. Soát từng câu: Quick Import hay biến một câu trắc nghiệm thành ô văn bản; bản tiếng Anh chuyển chính xác hơn.
4. **Giữ nguyên phần `[mã]` ở đầu mỗi câu hỏi** (ví dụ `[thi-clb_covua]`). Bộ chuyển đổi đọc điểm theo mã này.
5. Đặt rẽ nhánh theo bảng "Rẽ nhánh" trong `CAI_DAT_FORMS_CHI_THI.md` (chỉ đáp án "Không" của câu cổng).

## 2. Tick đáp án và điểm
Quick Import **không mang đáp án**. Với mỗi câu đề thi: bấm đáp án đúng để đặt **Correct answer**, điền ô
**Points** (điểm mỗi câu ghi trong `CAI_DAT_FORMS_CHI_THI.md`). Câu cổng "Em có dự thi… không?" **không** cho điểm.
Đáp án phải khớp bảng đáp án trong `CAI_DAT_FORMS_CHI_THI.md` (từ `de_thi.json`): bộ chuyển đổi chấm lại theo `de_thi.json`
và báo nếu điểm Forms lệch, tức là có câu tick nhầm.

## 3. Settings (bắt buộc, thiếu là hỏng việc ghép điểm)
| Cài đặt | Giá trị |
|---|---|
| Who can fill out this form | **Only people in my organization** |
| **Record name** | **BẬT** (để cột **Email** có trong tệp xuất; không bật thì không biết bài của em nào) |
| **One response per person** | **BẬT** (đây là bài thi, không cho làm lại) |
| **Show results automatically** | **TẮT** (bật là em làm trước thấy đáp án) |
| Shuffle questions | TẮT (xáo câu làm hỏng rẽ nhánh) |
| **Start date / End date** | Đặt đủ cả hai (hết giờ tự khoá) |

## 4. Giới hạn cần nhớ
- Mỗi biểu mẫu tối đa **200 câu** (tính cả câu cổng). Công cụ tự tách theo buổi khi vượt; mỗi biểu mẫu một link.
- Mỗi người tối đa 400 biểu mẫu, tính cả thùng rác: dùng lại biểu mẫu mẫu cho các đợt sau thay vì tạo mới nhiều lần.

## 5. Sau khi hết hạn
- Vào **Responses → Open in Excel**, gửi tệp `.xlsx` cho người phụ trách dự án. Không gửi qua kênh công khai (có tên
  và email học sinh).
- **Post scores không cần cho phần mềm xếp CLB.** Phần mềm chấm lại từ `de_thi.json`, không đọc cột điểm của Forms (chỉ
  dùng để đối chiếu). Chỉ bấm **Post scores** nếu nhà trường muốn học sinh xem điểm, sau khi đã chốt kết quả.
- Em vắng thi, em thi CLB mà không xếp nguyện vọng đó, phiếu nộp hai lần: bộ chuyển đổi liệt kê hết trong sheet
  *Cảnh báo*; thầy cô duyệt luật xử lý với nhà trường trước kỳ thi.
