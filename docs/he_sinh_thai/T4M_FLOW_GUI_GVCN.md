# T4M. Flow gửi tệp kết quả theo lớp cho giáo viên chủ nhiệm (T4M-M4, tuỳ chọn)

> Chỉ tài liệu (06/11/2026). Chưa thử trên Power Automate thật: mọi bước nhãn **TH** (chờ thử), công thức/tên hành động nhãn **GĐ** (giả định từ tài liệu Microsoft, chưa chạy). Số giới hạn nhãn **ĐXM** (đã xác minh, `T4M_KET_QUA_TAI_LIEU.md` NC-11..14, đọc 05/11/2026). Không có dữ liệu thật, tenantId, URL app hay tên người.
> **Tuỳ chọn:** gửi tay bằng Outlook/Teams (`T4M_VAN_HANH_MOT_DOT.md` bước 7) vẫn là đường mặc định; flow chỉ để đỡ công khi có vài chục lớp.

## 1. Phạm vi và nguyên tắc
1. Việc duy nhất của flow: lấy các tệp Excel theo lớp (kết quả `export_theo_lop`) trong một thư viện SharePoint và gửi mỗi tệp cho đúng giáo viên chủ nhiệm (GVCN).
2. **Chỉ connector chuẩn:** SharePoint, Outlook (Office 365 Outlook), Teams, và thao tác dữ liệu có sẵn. **Không** HTTP, không connector tuỳ biến (Premium, `T4M_HUONG_DAN_THU.md` §11).
3. **Không ghi ngược về list ECA** (NC-13): V1 không cập nhật từng dòng (1.500 em × 5 buổi ≈ 7.500 lần cập nhật, vượt 6.000 yêu cầu mỗi người mỗi ngày, ĐXM). Học sinh xem kết quả qua GVCN.
4. **Chủ flow là tài khoản dịch vụ của IT**, không phải tài khoản cá nhân: chủ flow rời tổ chức thì flow về hồ sơ Low; flow 90 ngày không chạy có thể bị tắt (NC-13, ĐXM). Tạo tài khoản dịch vụ: **HỎI-IT**.
5. Flow không chạm kiosk và không đọc dữ liệu thô (điểm, số bốc thăm): tệp theo lớp vốn không có hai thứ đó (`export_theo_lop`).

## 2. Đầu vào

| Thứ | Nguồn | Ghi chú |
|---|---|---|
| Thư mục `ket_qua_theo_lop` | Kiosk, thẻ **03 · Chi tiết và xuất tệp** (IT tải lên thư viện) | Mỗi lớp một tệp `<tên lớp>.xlsx`; em chưa có lớp vào `_chua_co_lop.xlsx`; tên tệp đã thay ký tự cấm bằng `_`, cắt tối đa 100 ký tự (`_ten_file_an_toan`, `_cat_ten_tep`); trùng tên thì thêm hậu tố |
| Thư viện SharePoint `KET_QUA_LOP` (tên gợi ý) | IT tạo | Mỗi đợt một thư mục con `<ngày đợt>`; quyền: chỉ tài khoản dịch vụ và IT |
| Tệp ánh xạ lớp → GVCN | List `GVCN` (cột `TenTep`, `Email`) hoặc Excel | **Nguồn: HỎI-IT, NC-08** (PowerSchool không có trong danh sách OneRoster của SDS, ĐXM). Khoá ghép là **tên tệp đã làm sạch** (`TenTep`), không phải tên lớp gốc: lớp tên có ký tự cấm sẽ lệch |
| Email GVCN | Cùng tệp ánh xạ | Chữ thường; mỗi lớp một người nhận (nhiều GVCN một lớp: cột `Email2`, TH) |

Soát trước khi chạy (thủ công, 1 phút): số tệp trong thư mục = số dòng ánh xạ (+1 nếu có `_chua_co_lop.xlsx`); không dòng nào thiếu email.

## 3. Các bước của flow (GĐ, TH)

| # | Hành động (connector chuẩn) | Cấu hình | Kiểm |
|---|---|---|---|
| 1 | Kích hoạt thủ công (Manually trigger a flow), đầu vào văn bản `ThuMuc` | IT chạy sau khi tải tệp lên | — |
| 2 | SharePoint **Get files (properties only)** | Thư viện `KET_QUA_LOP`, thư mục `ThuMuc` | Số tệp ≤ 5.000 (phân trang Low, ĐXM): vài chục lớp là vừa |
| 3 | SharePoint **Get items** (list `GVCN`) | Phân trang bật | Số dòng = số lớp |
| 4 | **Apply to each** trên tệp (đồng thời **1**, tuần tự) | Tuần tự để không chạm hạn mức Outlook/Teams | ≤ 5.000 mục, ≤ 500 hành động mỗi flow (ĐXM) |
| 5 | **Filter array** ánh xạ theo `TenTep` = tên tệp bỏ đuôi | | Không khớp → nhánh lỗi (§5) |
| 6 | SharePoint **Get file content** (hoặc dùng liên kết) | | Tệp ≤ 25 MB là đủ, mỗi tệp lớp rất nhỏ (GĐ) |
| 7a | Outlook **Send an email (V2)** kèm tệp, người gửi: hộp thư dùng chung của IT | Tiêu đề và nội dung tiếng Việt cố định (§4) | |
| 7b | (thay cho 7a) Teams **Post message in a chat or channel**, gửi **liên kết** tệp, không đính kèm | Chỉ nếu trường dùng Teams cho GVCN | ~28 KB mỗi tin (ĐXM) |
| 8 | Ghi vào list `NHAT_KY_GUI` (lớp, giờ, đã gửi/lỗi) hoặc chỉ dựa vào lịch sử chạy | Không chứa tên học sinh | Cuối chạy: số gửi = số tệp |
| 9 | Một email tóm tắt cho IT: số đã gửi, số lỗi, danh sách lớp lỗi | | |

**Chọn 7a hay 7b:** mặc định 7a (Outlook, 300 lệnh/60 giây, ĐXM). Teams chỉ có 100 lệnh/60 giây mỗi kết nối và tin tối đa khoảng 28 KB (ĐXM); với 50 GVCN cả hai đều xa giới hạn.

## 4. Nội dung thư (mẫu; IT chỉnh)
- Tiêu đề: `Kết quả xếp CLB — lớp <tên lớp>`.
- Nội dung: nêu lớp, đợt, tệp đính kèm là danh sách các em và CLB theo từng buổi; **không chuyển tiếp ngoài nhóm giáo viên**, **không đăng kênh công khai**; hỏi đáp gửi về hộp thư IT.
- Không có điểm thi, số bốc thăm hay diện trúng tuyển trong tệp (chủ ý của `export_theo_lop`). Nếu sau này thêm cột, soát lại điều này trước khi gửi.

## 5. Giới hạn (ĐXM) và việc phải làm

| Giới hạn | Số | Với trường (vài chục lớp) | Việc phải làm |
|---|---|---|---|
| Outlook (NC-12) | 300 lệnh/60 giây | Xa mức | Chạy tuần tự là đủ |
| Teams (NC-12) | 100 lệnh/60 giây mỗi kết nối; tin ~28 KB | Xa mức | Gửi liên kết, không dán nội dung |
| Hồ sơ Low (NC-13) | 6.000 yêu cầu/người/ngày (chuyển tiếp: 10.000/flow); vòng lặp, phân trang 5.000; 500 hành động/flow | Mỗi lớp ~4–6 hành động; 50 lớp ≈ 300 hành động | Nếu > 500 hành động: tách làm 2 flow (khối), hoặc gom vòng lặp |
| Flow ngừng 90 ngày (NC-13) | Có thể bị tắt | Đợt xếp có thể cách nhau nhiều tháng | Chạy thử 1 lần/quý hoặc bật lại trước đợt; ghi vào lịch IT |
| Chủ flow rời trường (NC-13) | Flow về Low | | Tài khoản dịch vụ (§1.4) và đồng sở hữu bởi ≥ 2 người IT |

Số hành động/lớp ở trên là **GĐ** (đếm từ bảng §3, chưa đo).

## 6. DLP (NC-14)
- Admin lập chính sách dữ liệu; nếu Outlook/Teams/SharePoint bị xếp vào nhóm không được trộn, flow bị treo hoặc cách ly; chính sách mới có hiệu lực trong 1 đến 24 giờ (ĐXM).
- **HỎI-IT trước khi dựng:** chính sách hiện hành có cho SharePoint + Outlook (hoặc Teams) cùng một flow không (NC-16). Không được: nhờ admin nới DLP chỉ để chạy flow này; nếu bị chặn thì dùng đường gửi tay.
- Thông báo cho IT/DPO rằng tệp có tên học sinh nằm trong thư viện và trong hộp thư GVCN: thời hạn xoá do trường đặt (HỎI-IT).

## 7. Xử lý lỗi và đường thủ công
1. **Lớp không có email / không khớp tên tệp:** flow bỏ qua, ghi vào email tóm tắt (bước 9); IT gửi tay tệp đó.
2. **Tệp bị khoá hoặc quyền lỗi:** thử lại 1 lần sau vài phút (Excel có thể khoá tới 6 phút, ĐXM); vẫn lỗi → gửi tay.
3. **DLP chặn (flow "suspended"):** dừng, báo admin; gửi tay cả thư mục.
4. **Gửi nhầm người:** thu hồi bằng yêu cầu của IT; không có nút "hoàn tác" của flow (TH). Hạn chế bằng bước soát §2 và bằng lần chạy thử ở §8.
5. **Đường thủ công đầy đủ (luôn dùng được):** mở thư mục kết quả theo lớp trên máy IT, gửi từng tệp bằng Outlook/Teams tới GVCN (`T4M_VAN_HANH_MOT_DOT.md` bước 7).
6. **Chạy lại sau khi xếp lại** (em muộn/rút): xuất thư mục **mới**, đặt thư mục con mới, gửi lại; thư mục cũ giữ nguyên (kiosk không ghi đè). Báo GVCN lớp có thay đổi (`thay_doi_ket_qua.csv`).

## 8. Thử (TH, chưa làm)
- Dùng `T4M_HUONG_DAN_THU.md` §8: thư viện `KET_QUA_GIA` 3 tệp giả, list `GVCN_GIA` 3 dòng, email của chính Truong hoặc IT; **không** gửi người thật.
- Pass: 3 thư đến đúng người, đúng tệp; email tóm tắt đúng số. Fail: ghi nguyên văn thông báo lỗi.
- Đo thật chỉ điền vào bảng của HDT §9; không điền số ước lượng thành số đo.

## 9. Việc chờ (không thuộc tài liệu này)
- NC-08: nguồn danh sách GVCN và có bao nhiêu GVCN mỗi lớp. NC-16: chính sách DLP. Có tài khoản dịch vụ hay không. Môi trường thử (NC-02).
