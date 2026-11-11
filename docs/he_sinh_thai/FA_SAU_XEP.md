# FA-DAA: sau khi xếp (FA-M6) — kết quả cho học sinh, phản hồi, khiếu nại, nhắc hạn, điểm danh

> Soạn 09/11/2026. **Chỉ tài liệu.** Nhãn: **TH** = chưa thử trên Microsoft thật (SharePoint, Power Apps, Power Automate, Forms); **GĐ** = giả định chưa kiểm; **HỎI-IT** = cần IT trả lời. Quyết định **D8** (Power Apps hay Forms) **chưa có**: tài liệu này mô tả phần "sau xếp" cho cả hai đường, màn kết quả trong app (đường A) chỉ có ở đường A. Không sửa kiosk, lược đồ hay hợp đồng CSV. Nguồn: `FA_DAA_VISION.md` §9, §5.2; `T4M_FLOW_GUI_GVCN.md`; `T4M_DAC_TA_SUA_APP.md` §12.

## 1. Luồng

| Pha | Việc | Ai | Công cụ |
|---|---|---|---|
| Công bố | Xuất `ket_qua_ly_do.csv` (lần chạy mới nhất), nạp list `KetQua` | IT | kiosk → SharePoint (cách C) |
| Xem kết quả | Mỗi em xem lý do của mình; 3 nút phản hồi | học sinh | app (đường A) hoặc GVCN gửi tệp theo lớp (`T4M_FLOW_GUI_GVCN.md`) |
| Khiếu nại (3 ngày) | Chỉ lỗi dữ liệu | học sinh → admin | Forms "Khiếu nại kết quả" |
| Theo dõi | Điểm danh 3 buổi đầu, giải phóng chỗ, mời danh sách chờ | giáo viên, admin | list `DiemDanh`, bảng chờ xuất từ `KetQua` |
| Tuần 3 | Hai câu khảo sát | học sinh | Forms "Khảo sát tuần 3" |

## 2. List `KetQua` (nạp từ `ket_qua_ly_do.csv`, cách C)

Tệp do kiosk xuất (`export_ly_do_csv`): mỗi dòng một học sinh một CLB của một buổi, lần chạy mới nhất. Cột thật của tệp: `student_id`, `buoi`, `club`, `group`, `reason`, `sentence`, `stb`, `waitlist_pos`. Câu `sentence` không chứa mã học sinh khác; `stb` là số bốc thăm của CHÍNH em; `waitlist_pos` rỗng nếu không ở danh sách chờ.

Tệp không có email, mà app lọc theo email. **IT ghép email** trên máy IT: bộ chuyển đổi `chuyen_forms_sang_phan_mem.py --fa-daa` ghi thêm `EMAIL_MA_HS.csv` (cột `Email`, `student_id`; dữ liệu cá nhân, không gửi đi, không đưa lên kho mã), rồi chạy `python mau_forms_thi_clb/ghep_ket_qua_email.py ket_qua_ly_do.csv EMAIL_MA_HS.csv --ra KETQUA_NHAP_LIST.csv`: mỗi dòng kết quả được thêm email (hạ chữ thường) và đổi tên cột như bảng dưới; em không có trong tệp email thì báo, dòng vẫn ghi với `Email` rỗng. Nhập `KETQUA_NHAP_LIST.csv` vào list. Cột của list:

| Cột list | Kiểu | Lấy từ |
|---|---|---|
| `Email` | Một dòng văn bản, đặt chỉ mục | ghép từ `student_id` qua `EMAIL_MA_HS.csv` (`ghep_ket_qua_email.py`) |
| `MaHS` | Một dòng văn bản | `student_id` |
| `Buoi` | Một dòng văn bản | `buoi` (mã buổi, ví dụ `thu_2`) |
| `CLB` | Một dòng văn bản | `club` (tên CLB) |
| `Nhom` | Một dòng văn bản | `group` |
| `MaLyDo` | Một dòng văn bản | `reason` (RESERVED, SCORE, MEDAL, LOTTERY, BELOW_PASS, NOT_ATTEMPTED, CLUB_CLOSED…) |
| `CauGiaiThich` | Nhiều dòng văn bản | `sentence` (đã có tiếng Việt, không mã học sinh khác) |
| `STB` | Số | `stb` |
| `ViTriCho` | Số | `waitlist_pos` |

Số dòng: tới khoảng 1.000 em × 5 ngày × số CLB em ghi (tối đa 7 mỗi ngày) ≈ 35.000 dòng trong trường hợp xấu nhất (GĐ). Đặt chỉ mục `Email` để lọc `=` không dính ngưỡng 5.000 của khung nhìn (NC-04). **Rủi ro (HỎI-IT):** học sinh có quyền đọc list có thể mở list trực tiếp và đọc dòng của bạn khác; quyền từng mục không hợp với 35.000 dòng. Cách giảm cần IT chọn: học sinh chỉ đọc qua app, hoặc mỗi lớp một list, hoặc chỉ gửi tệp theo lớp qua GVCN (đường mặc định của `T4M_FLOW_GUI_GVCN.md`). Chưa chọn.

## 3. Màn kết quả trong app (đường A) và 3 nút phản hồi

1. `Items` = `Filter(KetQua, Email = Lower(User().Email))` (lọc `=`, uỷ quyền được). Mỗi ngày một thẻ: tên CLB và `CauGiaiThich` (luôn có lý do; mẫu câu do kiosk sinh, app không tự soạn lại).
2. Ngay dưới kết quả, **3 câu, mỗi câu một chạm**, ghi vào list `PhanHoi` (một dòng mỗi em mỗi lần công bố: `Email`, `LanChay`, `HaiLong`, `HieuLyDo`, `KhoNhat`, `NopLuc`):
   - "Em hài lòng với kết quả?" 1 đến 5 (`HaiLong`);
   - "Em có hiểu vì sao được xếp như vậy?" Có / Không (`HieuLyDo`);
   - "Phần nào khó nhất?" chọn CLB / xếp thứ tự / huy chương / thử thách / không có (`KhoNhat`).
3. Mỗi chạm là một `Patch` lên cùng dòng `PhanHoi` (3 yêu cầu mỗi em): rất nhỏ so với 6.000 (mục 7). Sửa câu trả lời trước hạn đóng phản hồi được.
4. Nếu chưa có app v2: GVCN nhận tệp theo lớp và chuyển lý do cho em; 3 câu phản hồi chuyển sang Forms một trang (cùng ba câu, Record name BẬT).
5. **Đường B, một biểu mẫu thay hai (FA-M6b, TH — chưa thử trên Microsoft Forms thật):** nếu cả phản hồi và khiếu nại đều chạy trên Forms, dùng MỘT biểu mẫu "Sau khi xem kết quả" thay cho biểu mẫu phản hồi và biểu mẫu khiếu nại riêng: `python mau_forms_thi_clb/tao_mau_forms.py --sau-ket-qua` ghi `NHAP_FORMS_SAU_KET_QUA.docx` và `CAI_DAT_FORMS_SAU_KET_QUA.md` (rẽ nhánh `[co_sai]`: Không → kết thúc; Có → phần báo lỗi dữ liệu theo buổi). Ở kiosk, nút **Nạp biểu mẫu Sau khi xem kết quả** (khung "Phản hồi của học sinh", thẻ "Chi tiết và xuất tệp") nạp một tệp Excel xuất từ biểu mẫu đó: phản hồi vào bảng phản hồi, khiếu nại vào danh sách khiếu nại, trong một lần ghi. Nút "Nạp từ Forms" cũ vẫn dùng được cho biểu mẫu ba câu riêng.

## 4. Khiếu nại (3 ngày) trên Forms

- Biểu mẫu "Khiếu nại kết quả": Start/End date = 3 ngày kể từ công bố; Record name BẬT; mỗi em tối đa một phiếu mỗi buổi (câu `Buoi` bắt buộc).
- Câu hỏi: mã học sinh (tự điền từ Email nếu có), buổi, CLB, **loại lỗi dữ liệu** (nhập sai nguyện vọng / điểm thử thách ghi sai / mất bài thi / lỗi hệ thống / khác), mô tả, ảnh tuỳ chọn. Câu đầu biểu mẫu: chỉ xét **lỗi dữ liệu**, không xét "em thấy bất công".
- Xử lý: admin xem từng phiếu; nếu đúng là lỗi dữ liệu thì sửa dữ liệu rồi chạy lại thuật toán với **cùng seed** (số bốc thăm đã khoá); không sửa tay kết quả. Mỗi lần chạy lại thêm một dòng `run_history` (không ghi đè). Sau 3 ngày không nhận phiếu mới.
- Chưa có chỗ nhập khiếu nại trong kiosk (tầm nhìn nói "trong phần mềm"; chưa làm, nằm ngoài FA-M6).
- **Một biểu mẫu thay hai (FA-M6b, TH):** thay biểu mẫu khiếu nại riêng bằng nhánh khiếu nại của biểu mẫu "Sau khi xem kết quả" (mục 3.5): chỉ lỗi dữ liệu, chọn một hoặc nhiều buổi, mỗi em một phiếu, mở 3 ngày từ lúc công bố. Hạn khiếu nại tính theo giờ hoàn thành do Forms ghi, nên admin nạp muộn vẫn công bằng. Nộp muộn hoặc nộp lần hai: em báo giáo viên chủ nhiệm, admin nhập tay ở mục Khiếu nại của kiosk.

## 5. Khảo sát tuần 3 trên Forms

Biểu mẫu hai câu, Record name BẬT: "Em còn đi CLB không?" (Còn / Không) và "Em muốn đổi không?" (Không / Có, kèm ô ghi CLB muốn đổi sang). Gửi đường dẫn bằng flow nhắc (mục 6) hoặc qua GVCN. Kết quả đọc bằng Excel; không có bước tự động đổi CLB.

## 6. Nhắc hạn bằng Power Automate (TH)

Chủ flow là **tài khoản dịch vụ của IT** (`T4M_FLOW_GUI_GVCN.md` §1.4). Chỉ connector chuẩn (SharePoint, Outlook).

| Flow | Khi nào | Người nhận | Nguồn danh sách |
|---|---|---|---|
| Mở cổng | lúc mở đăng ký | mọi học sinh | list `ECA` (hoặc danh sách học sinh) |
| Nhắc -2 ngày | 2 ngày trước hạn | em chưa nộp (`TrangThai` là DRAFT hoặc chưa mở, không phải SUBMITTED; đường B: em chưa có phiếu) | `ECA` lọc `TrangThai` |
| Nhắc -3 giờ | 3 giờ trước hạn | như trên | như trên |
| Chưa làm thử thách | 2 lần trước hạn thử thách (-2 ngày, -3 giờ) | em xếp CLB Tuyển chọn mà chưa có bài (NOT_ATTEMPTED) | list `CanNhac` (cột `Email`): IT chạy `chuyen_forms_sang_phan_mem.py --fa-daa` trên tệp xuất mới nhất, lấy các dòng NOT_ATTEMPTED trong `BANG_DIEM.xlsx` (sheet Cảnh báo), nạp lại `CanNhac` trước mỗi lần nhắc |
| Tỉ lệ đăng ký dưới 50 % sau 3 ngày | một lần | GVCN của lớp có em chưa đăng ký | IT xuất danh sách em chưa đăng ký theo lớp vào thư viện, rồi chạy flow gửi tệp theo lớp của `T4M_FLOW_GUI_GVCN.md` (đổi nội dung thư); tỉ lệ = số em SUBMITTED / tổng em, IT tính trên tệp xuất |

**Thiết kế để dưới hạn mức:** mỗi lần nhắc là **một lần chạy** đọc danh sách một lần, rồi gửi theo **lô**: mỗi thư gửi tới tối đa 50 người nhận ở ô Bcc (GĐ: giới hạn số người nhận mỗi thư của Exchange Online là chuyện của tenant, HỎI-IT). Không viết kiểu "mỗi em một thư" (xem mục 7).

## 7. Hạn mức 6.000 yêu cầu mỗi người mỗi 24 giờ (NC-13, ĐXM trong `T4M_FLOW_GUI_GVCN.md` §1.3)

Giả định: 1.000 học sinh, 5 ngày, mỗi hành động chạy tính một yêu cầu (GĐ, chưa đo; đo ở K13).

| Cách làm | Phép tính | Kết quả |
|---|---|---|
| Mỗi em một thư, 3 lần nhắc | 3 × 1.000 = 3.000 hành động gửi thư; nếu mỗi em thêm một hành động (điều kiện hoặc ghi nhật ký) thì 6.000 | **chạm hạn mức**: không dùng |
| Gửi theo lô 50 người nhận Bcc | mỗi lần nhắc: đọc ≈ 50 trang `ECA` (5.000 dòng ÷ 100 dòng mỗi trang) + vài hành động lọc + 20 thư; 3 lần ≈ 3 × 75 = 225 | còn rất xa 6.000 |
| Ghi từng dòng về list (không làm) | 1.000 em × 5 buổi ≈ 5.000 đến 7.500 cập nhật | vượt: vì vậy flow **không** ghi ngược về `ECA` |
| Ba nút phản hồi trong app | 3 `Patch` mỗi em, 1.000 em, nhưng tính theo từng người dùng app | 3 yêu cầu mỗi em |

Hạn mức tính theo **chủ flow** nên mọi flow dùng chung một tài khoản dịch vụ cộng dồn: cộng các flow cùng ngày lại (mở cổng + nhắc + gửi GVCN) và giữ dưới 6.000 với dư địa (HỎI-IT: hồ sơ giấy phép thật).

## 8. Điểm danh và danh sách chờ

**List `DiemDanh`** (một dòng mỗi em mỗi CLB đã xếp; tạo từ CSV mẫu, cách C): `Email`, `MaHS`, `CLB`, `Buoi1`, `Buoi2`, `Buoi3` (Choice: Có / Vắng có phép / Vắng không phép), `GhiChu`, và cột tính `GiaiPhong`:

`=IF((IF([Buoi1]="Vắng không phép",1,0)+IF([Buoi2]="Vắng không phép",1,0)+IF([Buoi3]="Vắng không phép",1,0))>=2,"Giải phóng chỗ","")` (GĐ, TH).

Luật (V§9.3): vắng **2 trong 3 buổi đầu không phép** thì giải phóng chỗ. Giáo viên CLB điền bằng khung nhìn bảng lọc theo CLB của mình (quyền theo giáo viên: HỎI-IT). Kiosk **chưa có** màn điểm danh; đây là việc ngoài FA-M6.

**Danh sách chờ (xuất):** từ `KetQua` lọc `ViTriCho` không rỗng, nhóm theo `CLB`, sắp `ViTriCho` tăng dần (thứ tự theo quyết định D4: Tuyển chọn điểm > huy chương > bốc thăm; Giới hạn huy chương > bốc thăm; chỉ các em xếp CLB đó cao hơn CLB hiện tại). Khi một chỗ được giải phóng, giáo viên mời em đầu danh sách (email hoặc Teams, tay); em nhận thì admin đổi CLB cho em và ghi lại. "Vòng 2" của V§9.3 (em chưa có CLB mong muốn được chọn trong chỗ còn trống) chưa có công cụ; việc đó để GĐ sau.

## 9. Bảng kiểm pass/fail (tất cả TH)

| # | Yêu cầu | Pass khi |
|---|---|---|
| K1 | Nhập `KetQua` từ CSV | Số dòng list = số dòng `ket_qua_ly_do.csv`; tiếng Việt không vỡ dấu; `Email` đã đặt chỉ mục |
| K2 | Em chỉ thấy kết quả của mình trong app | Hai tài khoản thử, mỗi em đúng các thẻ của mình (kể cả email viết hoa) |
| K3 | Luôn có lý do | Mọi thẻ có `CauGiaiThich`; không câu nào chứa mã học sinh khác |
| K4 | Ba nút phản hồi | Ba chạm ghi đúng một dòng `PhanHoi`; sửa trước hạn được |
| K5 | Rủi ro đọc trực tiếp list | Tài khoản học sinh thử mở list `KetQua` trực tiếp: ghi lại thấy hay không; chốt cách giảm với IT |
| K6 | Khiếu nại 3 ngày | Biểu mẫu tự đóng sau 3 ngày; phiếu có đủ loại lỗi dữ liệu |
| K7 | Chạy lại cùng seed | Sửa một lỗi dữ liệu thử, chạy lại: kết quả em không liên quan không đổi; `run_history` thêm dòng, không ghi đè |
| K8 | Khảo sát tuần 3 | Hai câu hiện đúng; có Email của người trả lời |
| K9 | Nhắc -2 ngày và -3 giờ | Chỉ em chưa nộp nhận thư; không em nào nhận hai thư cùng mốc |
| K10 | Nhắc thử thách | Chỉ em NOT_ATTEMPTED có tên trong `CanNhac` nhận thư, đúng hai lần |
| K11 | Dưới 50 % sau 3 ngày | GVCN nhận đúng danh sách em chưa đăng ký của lớp mình |
| K12 | Cột `GiaiPhong` | Hai buổi "Vắng không phép" thì hiện "Giải phóng chỗ"; một buổi thì không |
| K13 | Hạn mức | Cộng số yêu cầu thật của mọi flow trong một ngày cao điểm (lịch sử chạy): dưới 6.000 với dư địa |
| K14 | Không dữ liệu thật trong kho mã | Rà tệp và ảnh: không tên, email thật, `tenantId`, địa chỉ app |

## 10. Còn mở

- **D8** chờ cuộc họp GĐ2. **HỎI-IT:** nguồn email để ghép `KetQua`; quyền đọc list của học sinh (K5); giấy phép và hồ sơ hạn mức thật; giới hạn người nhận mỗi thư; quyền giáo viên trên `DiemDanh`.
- Chưa có trong kiosk (không thuộc FA-M6): màn điểm danh, nhập khiếu nại, vòng 2 và việc đổi CLB khi mời danh sách chờ.
