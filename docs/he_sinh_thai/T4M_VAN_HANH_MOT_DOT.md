# T4M. Vận hành một đợt xếp CLB (cho nhân viên IT của trường)

Mã việc: T4M-VH (06/11/2026). Chỉ tài liệu. Nhãn: **ĐXM** = có nguồn đã mở; **TH** = chưa thử, cần chạy thật; **HỎI-IT** = chờ trường trả lời.
Một đợt = một lần học sinh đăng ký (Top 3 mỗi ngày trong app ECA) + làm bài thi CLB (Microsoft Forms) → xếp → trả kết quả theo lớp.
Mọi dữ liệu học sinh **nằm trên máy IT**. Không gửi tệp có tên/email học sinh qua kênh công khai. Thời hạn xoá tệp sau đợt: **HỎI-IT**.
Tập thử không cần dữ liệu thật: `python du_lieu_test/demo_t4m.py --ra ./demo_ra` (120 em giả, ngoại tuyến, chạy trọn chuỗi bước 5 đến 7).

## Tóm tắt 8 bước

| # | Việc | Ai | Ra |
|---|---|---|---|
| 1 | Giáo viên dựng bài thi | Giáo viên CLB + người phụ trách dự án | Biểu mẫu Forms (có link) |
| 2 | Mở/đóng đăng ký và bài thi | IT / giáo viên ECA | Hai mốc ngày |
| 3 | Khoá | IT | List ở trạng thái "Đã khóa" |
| 4 | Xuất List và kết quả thi | IT | `DANH_SACH.csv`, `KET_QUA_FORMS.xlsx` |
| 5 | Chuyển đổi | IT | `SO_NHAP_CLB.xlsx`, `BANG_DIEM.xlsx` |
| 6 | Nạp vào kiosk và chạy | IT | Kết quả xếp |
| 7 | Xuất theo lớp và gửi | IT | Mỗi lớp một tệp Excel |
| 8 | Em đến muộn, rút | IT | Chạy lại, bộ số bốc thăm giữ nguyên |

## 1. Giáo viên dựng bài thi
Làm một lần mỗi đợt (hoặc nhân biểu mẫu mẫu: **Share as a template → Get a link to duplicate**, chép nội dung không chép phản hồi, ĐXM).
1. Giáo viên của từng CLB có thi gửi đề; người phụ trách dự án ghi vào `mau_forms_thi_clb/de_thi.json` (nguồn duy nhất: buổi, CLB, chỉ tiêu, đề, đáp án). `club_id` trong `de_thi.json` **phải trùng** mã CLB trong cột `NV1..NV3` của List.
2. Sinh tệp: `python mau_forms_thi_clb/tao_mau_forms.py --chi-thi` → `NHAP_FORMS_CHI_THI.docx` (vượt 200 câu thì `_1.docx`, `_2.docx`: mỗi tệp một biểu mẫu) và `CAI_DAT_FORMS_CHI_THI.md`.
3. Forms: forms.office.com bằng tài khoản trường → **Quick import** từ ổ máy (không từ SharePoint/OneDrive, tối đa 10 MB) → chọn **Quiz** (ĐXM).
4. Làm theo `CAI_DAT_FORMS_CHI_THI.md` và `mau_forms_thi_clb/GHI_CHU_GIAO_VIEN.md`: tick đáp án + điểm, đặt rẽ nhánh (chỉ đáp án "Không" của câu cổng), **giữ nguyên phần `[mã]` đầu mỗi câu**.
5. **Settings bắt buộc:** Only people in my organization · **Record name BẬT** · **One response per person BẬT** · **Show results automatically TẮT** · Shuffle questions TẮT · Start/End date đủ cả hai.
- **Kiểm:** tự điền hai phiếu (một phiếu thi, một phiếu chọn "Không" ở mọi câu cổng); làm tiếp bước 4 và 5 trên dữ liệu thử; bộ chuyển đổi **không cảnh báo** mới phát link. Sai cột phát hiện sau khi nhiều em nộp là sửa tay hàng loạt.
- **Nếu lỗi:** Quick Import biến câu trắc nghiệm thành ô văn bản → sửa tay (bản tiếng Anh chuyển chính xác hơn). Mỗi người tối đa 400 biểu mẫu kể cả thùng rác: dùng lại biểu mẫu mẫu.
- **Giữ:** `de_thi.json` + đáp án chỉ trên máy IT / người phụ trách (đừng đặt đáp án trong List học sinh đọc được).

## 2. Mở và đóng đăng ký
1. App ECA: đặt trạng thái các dòng là "Đang mở" (cách đặt: **HỎI-IT**, phụ thuộc kho hiện tại là SharePoint List hay Dataverse).
2. Forms: Start/End date (bước 1.5). **Đóng bài thi sau hạn đăng ký** hoặc cùng lúc, để không ai thi CLB mà chưa kịp xếp nguyện vọng.
3. Thông báo học sinh hai việc: xếp Top 3 ở app và làm bài thi ở link Forms (mỗi bài một lần).
- **Kiểm:** mở thử bằng một tài khoản học sinh thử (HỎI-IT có sẵn không); thử nộp hai lần, lần hai phải bị chặn.
- **Nếu lỗi:** em kêu không vào được Forms → thường do không đăng nhập bằng email trường; không mở rộng quyền sang "Anyone" (mất cột Email).

## 3. Khoá
1. Đến hạn: đặt trạng thái "Đã khóa" (app tắt chỉnh sửa; cách khoá hiện nay: **HỎI-IT**) và chắc Forms đã qua End date.
2. Từ lúc này không ai sửa List; sửa sau khoá = làm lại bước 4 (xuất lại).
- **Kiểm:** thử sửa một dòng bằng tài khoản học sinh thử: phải bị từ chối.

## 4. Xuất dữ liệu
1. **List:** mở list → bỏ chọn mọi mục → **Export > Export to CSV** (nút chỉ hiện khi không chọn mục; tối đa 30.000 dòng; tệp là bản chụp, ĐXM). Lưu `DANH_SACH.csv`. 1.500 em × 5 ngày = 7.500 dòng: đủ. Cột cần có: `Email`, `Thu`, `NV1..NVn`, tuỳ chọn `HoTen`, `Lop`, `CoSo`.
2. **Forms:** mỗi biểu mẫu → **Responses → Open in Excel** (hoặc Download a copy) → lưu `.xlsx`. Có nhiều biểu mẫu (tách theo buổi) thì lưu hết.
- **Kiểm** (đoạn Python 4.2 của `T4M_HUONG_DAN_THU.md`): có BOM hay không; tiếng Việt còn dấu; số dòng khớp số em × số ngày; cột `Thu`/`CoSo` ra chữ đọc được. Cách List mã hoá/đặt tên cột khi xuất: **TH** (tài liệu không ghi).
- **Nếu lỗi:** không thấy nút Export hoặc bị chặn → ghi lý do cho người phụ trách (HỎI-IT, có thể do chính sách DLP). Chữ vỡ dấu → xuất lại bằng đường khác, báo người phụ trách.
- **Giữ:** hai loại tệp chỉ trên máy IT, thư mục theo đợt, ví dụ `dot_2026_hk1/`. **Mỗi cơ sở xếp riêng** (CS1, CS2): giữ MỘT `DANH_SACH.csv` có cột `CoSo`, không cần tách tay; bộ chuyển đổi lọc bằng `--co-so` ở bước 5 (cần cột `CoSo`; giá trị khớp không phân biệt hoa thường). Phiếu thi của em cơ sở khác hiện cảnh báo "ở cơ sở khác hoặc không có trong danh sách", đó là cảnh báo mong đợi.

## 5. Chuyển đổi
```
python mau_forms_thi_clb/chuyen_forms_sang_phan_mem.py KET_QUA_FORMS.xlsx --chi-thi --lists DANH_SACH.csv --ra ./nap
```
Nhiều biểu mẫu: liệt kê nhiều `.xlsx` ngay sau lệnh. Chạy riêng cho từng cơ sở bằng `--co-so`: `... --co-so CS1 --ra ./nap_CS1`, rồi `... --co-so CS2 --ra ./nap_CS2` (cùng một `DANH_SACH.csv`, cùng các tệp Forms). Không có `--co-so` thì không lọc (như cũ). Cơ sở không có em nào, hoặc List thiếu cột `CoSo`: bộ chuyển đổi báo lỗi và không ghi tệp. `--co-so` mới kiểm bằng test, chưa chạy với tệp List thật (TH).
Luồng dữ liệu: cột Lớp của List đi vào cột Lớp của Sổ nhập (kiosk dùng để xuất theo lớp chủ nhiệm ở bước 7); Email (chữ thường) ghép bài thi với nguyện vọng; điểm được **chấm lại từ `de_thi.json`**, không tin cột Points của Forms.
1. **Đọc hết cảnh báo** (in ra màn hình, cũng ở sheet *Cảnh báo* của `BANG_DIEM.xlsx`). Ý nghĩa:
   - phiếu nộp hai lần → giữ phiếu đầu (đúng luật);
   - email không có trong List (hoặc, khi dùng `--co-so`, "ở cơ sở khác hoặc không có trong danh sách") → bỏ phiếu: kiểm xem có phải em ở cơ sở khác, em chuyển đến chưa có trong List, hay gõ sai;
   - thi một CLB mà không xếp nguyện vọng CLB đó → bỏ điểm (đúng luật);
   - điểm Forms lệch điểm chấm lại → **có câu tick nhầm đáp án**: sửa Forms hoặc `de_thi.json` rồi xuất lại.
2. Mở `BANG_DIEM.xlsx`, soát vài em theo chi tiết đúng/sai từng câu.
- **Nếu lỗi:** "thiếu câu" → ai đó xoá phần `[mã]` đầu câu; khôi phục tên câu. Không có bài thi nào → vẫn ra Sổ nhập (nguyện vọng, không điểm), hợp lệ cho CLB không thi.
- **Giữ:** `SO_NHAP_CLB.xlsx`, `BANG_DIEM.xlsx` trong thư mục đợt.

## 6. Nạp vào kiosk, chạy, đọc kiểm tra
1. Mở kiosk → màn **Không gian làm việc**: tạo (hoặc chọn) **một không gian cho mỗi cơ sở**, mẫu "Trường học". Cài kiosk trên máy IT: chính sách chạy `.exe` chưa ký số **HỎI-IT**.
2. Thẻ **01 · Xếp CLB**: kéo `SO_NHAP_CLB.xlsx` vào ô nạp → đối chiếu dòng tóm tắt (số CLB, học sinh, nguyện vọng, lượt thi) với bước 5 → **Nhập sổ**.
3. Đọc mục **Cảnh báo dữ liệu** ngay dưới ô nạp (bước hay bị bỏ nhất). Tra nghĩa ở `HUONG_DAN_SU_DUNG.md` mục 10.
4. Ô `seed`: để mặc định `42` hoặc theo quy định của trường; chỉ nhập được ở lần chạy đầu, sau đó **khoá cùng bộ số bốc thăm**.
5. **Chạy sắp xếp** → xác nhận. Tiến trình 5 bước: sao lưu → kiểm tra dữ liệu → bốc thăm → chạy thuật toán → ghi kết quả. Kết quả chỉ được ghi khi qua hai chốt kiểm (sanity và ổn định); không qua thì phần mềm báo lỗi, không ghi gì.
- **Kiểm:** số em chưa có chỗ (dòng đỏ ở danh sách) có hợp lý với chỉ tiêu; thẻ **02 · Kết quả** mở được theo lớp.
- **Nếu lỗi:** không cho nhập sổ → bảng lỗi kèm trang và dòng, sửa Excel rồi kéo lại. Chạy lại cùng dữ liệu cùng `seed` luôn ra cùng kết quả.
- **Giữ:** thư mục workspace (có `app.db` và bản sao lưu tự động) trên máy IT. **Không xoá** `app.db` giữa đợt: lịch sử các lần chạy được giữ.

## 7. Xuất theo lớp và gửi
1. Thẻ **03 · Chi tiết và xuất tệp** → xuất kết quả theo lớp (một thư mục, mỗi lớp chủ nhiệm một tệp Excel, không có điểm và số bốc thăm; em chưa có lớp vào `_chua_co_lop.xlsx`). Dải vàng "Dữ liệu đã được sửa sau lần chạy gần nhất" → chạy lại trước khi xuất.
2. Mở 2–3 tệp để soát tên lớp, số em.
3. Gửi: thủ công bằng Outlook/Teams tới giáo viên chủ nhiệm, hoặc một flow Power Automate tuỳ chọn (mô tả ở `T4M_HUONG_DAN_THU.md` mục 8; **TH**; flow thuộc tài khoản dịch vụ của IT). Danh sách email giáo viên chủ nhiệm: **HỎI-IT**.
4. V1 **không ghi kết quả ngược từng dòng vào app** (giới hạn 6.000 yêu cầu/người/ngày, ĐXM). Học sinh xem kết quả qua giáo viên chủ nhiệm.
- **Nếu lỗi:** tệp bị khoá khi gửi, hoặc DLP chặn Outlook/Teams → gửi bằng kênh trường cho phép, ghi lại cho người phụ trách.
- **Giữ:** thư mục kết quả theo lớp trong thư mục đợt; không đăng lên kênh công khai.

## 8. Em đến muộn, rút, đổi
- **Em mới / đến muộn:** thêm vào List (hoặc nạp thêm một Sổ nhập có em đó, hoặc thêm trực tiếp ở kiosk); **chạy lại**. Nạp tệp chỉ **cộng thêm**, không xoá em đã có. Bộ số bốc thăm **đã khoá**: thứ tự giữa các em cũ giữ nguyên, em mới bốc một vị trí ngẫu nhiên, nên em mới có thể giành suất đang do em cũ giữ.
- **Em rút:** bỏ đánh dấu CLB đã chấm điểm trong thẻ Quản lý rồi **Lưu**, hoặc xoá em (nút bị chặn nếu em đã có kết quả; xem `HUONG_DAN_SU_DUNG.md` mục 8). Sau đó chạy lại.
- **Thi bù:** em thi muộn → xuất lại Forms, chạy lại bước 5, nạp Sổ nhập mới, rồi chạy lại. Cách kiosk xử lý điểm nạp lại cho em đã có điểm: **TH** (thử bằng `demo_t4m.py` trước khi dùng thật).
- **Luôn:** sau chạy lại, xuất mục "Thay đổi so với lần chạy trước" (`thay_doi_ket_qua.csv`) để biết em nào đổi CLB, rồi báo giáo viên chủ nhiệm. Công bố sớm rồi chạy lại thì kết quả đã công bố có thể đổi: **chốt danh sách** trước lần chạy đầu càng sớm càng tốt.
- **Không làm:** đổi `seed` hay "Vẽ lại số bốc thăm" giữa chừng (đổi toàn bộ kết quả). Mỗi lần chạy thêm một dòng vào lịch sử, không bao giờ ghi đè.

## Phụ lục: lệnh chạy thử ngoại tuyến (không cần Microsoft)
```
python du_lieu_test/demo_t4m.py --ra ./demo_ra                         # 120 em
python du_lieu_test/demo_t4m.py --ra ./demo_ra --so-hs 200 --seed 7 --he-so-cho 1
```
Ra `lists_gia.csv`, `forms_chi_thi_gia.xlsx`, `SO_NHAP_CLB.xlsx`, `BANG_DIEM.xlsx`, `ket_qua_theo_lop/`. Dữ liệu hoàn toàn **mô phỏng**.

## Việc còn chờ (không thuộc tài liệu này)
HỎI-IT: kho của app ECA, cách khoá, đường PowerSchool → M365, danh sách giáo viên chủ nhiệm, chính sách cài `.exe`, thời hạn xoá tệp. **TH:** cách List mã hoá khi xuất, bộ chuyển đổi lọc theo cơ sở, flow gửi tệp.
