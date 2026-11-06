# T4M. Cổng thi: chọn CLB → mở bài thi → cập nhật trạng thái → trả điểm → lặp lại (thiết kế, 06/11/2026)

Mã việc: **T4M-NC** (thiết kế, chưa có mã). Truong yêu cầu 06/11/2026. Chỉ tài liệu, chưa thử (TH). Nhãn: ĐXM / TT-CXM / GĐ / HỎI-IT như `T4M_KE_HOACH_NGHIEN_CUU.md` §4.

## 1. Luồng mong muốn
```
Học sinh mở app ECA (đăng nhập tài khoản trường)
  → chọn Top 3 mỗi buổi (đã có trong T4M_DAC_TA_SUA_APP.md)
  → màn "Thi tuyển": danh sách CLB có thi mà em đã chọn, mỗi CLB một nút
      [Làm bài]  → mở biểu mẫu thi CỦA RIÊNG CLB đó (Microsoft Forms, tab mới)
      em nộp bài → flow ghi "Đã làm" vào list BaiThi
      quay lại app → CLB đó hiện "Đã làm" (và điểm, nếu bật mục 5)
  → lặp lại với CLB kế tiếp
```

## 2. Kiến trúc (chỉ connector chuẩn, giấy phép M365)

| Thành phần | Dùng gì | Vai trò | Căn cứ |
|---|---|---|---|
| "Website" | **App Power Apps ECA** (đã có, học sinh đã đăng nhập) | Nhận CLB đã chọn, hiện nút làm bài, hiện trạng thái | NC-02, NC-05 |
| Bài thi | **Mỗi CLB có thi một biểu mẫu Forms dạng Quiz**, không câu cổng | Đề, hẹn giờ, một lần nộp, ghi Email | KQ §7.1 (ĐXM) |
| Bảng CLB | SharePoint List `CLB` thêm cột `FormUrl` | Nút [Làm bài] lấy địa chỉ ở đây | — |
| Trạng thái | SharePoint List `BaiThi` (Email, ClubId, ResponseId, NopLuc, Diem tuỳ chọn) | Một dòng mỗi bài đã nộp | NC-04 |
| Cập nhật trạng thái | **Power Automate**, mỗi biểu mẫu một flow nhỏ: *When a new response is submitted* → *Get response details* → *Create item* trong `BaiThi` | "Đã làm" xuất hiện vài giây đến vài phút sau khi nộp (GĐ) | Connector Forms: Standard, chỉ đọc (ĐXM) |
| Chấm điểm chính thức | **Bộ chuyển đổi Python** chấm lại từ `de_thi.json` khi khoá đợt | Điểm vào kiosk, không tin cột Points | KQ §7.0 |

Mở biểu mẫu: `Launch(LookUp(CLB, ClubId = x).FormUrl)` (hàm `Launch` của Power Fx, mở tab mới; ĐXM learn.microsoft.com/power-platform/power-fx/reference/function-param, ms.date 04/03/2025). Trạng thái: `Filter(BaiThi, Email = Lower(User().Email))` (lọc `=`, uỷ quyền được, NC-04). Nút ẩn khi đã có dòng `BaiThi` cho CLB đó; Forms "One response per person" chặn nộp lần hai ở phía Forms.

Trang cảm ơn của biểu mẫu (Customize thank you message, ĐXM KQ §7.1) ghi liên kết quay về app.

## 3. Vì sao mỗi CLB một biểu mẫu (không dùng câu cổng)
- Trạng thái theo từng CLB tự nhiên: một phản hồi = một bài của một CLB.
- Không cần rẽ nhánh; giáo viên CLB nào giữ biểu mẫu CLB đó; hẹn giờ áp cho đúng một đề (KQ §7.1: hẹn giờ áp cả biểu mẫu).
- Giới hạn: 400 biểu mẫu mỗi người, tính cả thùng rác (ĐXM). 10 đến 20 CLB là vừa; nên để **một tài khoản (giáo viên hoặc IT) sở hữu** hoặc mỗi giáo viên giữ biểu mẫu của mình (HỎI-IT).

## 4. Giới hạn và rủi ro
1. **Connector Forms không trả điểm Quiz** cho flow: chỉ thấy ở nguồn cộng đồng (TT-CXM, TechCommunity 2019–2024). Vì vậy flow **chỉ báo "Đã làm"**, không chép điểm từ Forms.
2. **Một flow mỗi biểu mẫu** (trigger nhận một Form Id; ĐXM connector). 10 biểu mẫu = 10 flow giống nhau, sao từ một flow mẫu. Biểu mẫu nhóm (Teams) phải dán Form Id tay (ĐXM).
3. **Số yêu cầu** (ước lượng): mỗi bài nộp khoảng 3 hành động. 1.500 em × 2 bài = 3.000 bài × 3 = 9.000 hành động trong cả đợt. Hồ sơ Low: 6.000 yêu cầu mỗi người mỗi ngày (ĐXM, NC-13); đợt mở vài ngày thì vừa, **một ngày cao điểm có thể chạm trần**. Chủ flow là tài khoản dịch vụ IT; xem lại khi biết số thật (HỎI-IT).
4. Trigger Forms có tần suất kiểm 86.400 giây cho kiểu cũ; kiểu webhook hiện tại báo ngay (ĐXM bảng throttling của connector). Trạng thái có thể trễ: app nên có nút "Làm mới".
5. **Em thi CLB không chọn**: biểu mẫu vẫn nhận (Forms không biết NV). App chỉ hiện nút cho CLB em đã chọn; bộ chuyển đổi vẫn bỏ điểm và báo (đã có).
6. Liên kết biểu mẫu chia nhau được; "Only people in my organization" + Email bảo đảm đúng người, không chống được làm hộ (NC-26, giáo viên ECA quyết cách giám sát).

## 5. "Trả điểm về": ba mức, chọn một
| Mức | Cách | Được | Mất |
|---|---|---|---|
| **5a (khuyến nghị V1)** | Không trả điểm trong app. Giáo viên bấm **Post scores** trong Forms khi hết đợt; em xem điểm trong Forms | Không cần flow chấm; không lệch điểm | Điểm nằm ở Forms, không ở app |
| 5b | Sau khi khoá, IT chạy bộ chuyển đổi, nạp **bảng điểm đã chấm lại** lên list `BaiThi` (Import / Edit in grid view) | Điểm chính thức (cùng số kiosk dùng) hiện trong app | Một bước tay của IT; không tức thời |
| 5c | Flow tự chấm: so từng câu với đáp án ở một list **chỉ tài khoản dịch vụ đọc được**, ghi `Diem` | Điểm gần như tức thời | Nhiều hành động hơn (thêm khoảng 1 hành động mỗi câu), nguy cơ lệch với Forms (TT-CXM), phải giữ đáp án ở hai nơi |

Điểm dùng để **xếp** luôn là điểm bộ chuyển đổi chấm lại (bất biến 2 không đổi; hợp đồng CSV không đổi).

## 6. Phần mềm của dự án phải thêm
- **Q4a.** `tao_mau_forms.py --moi-clb` sinh **một tệp Quick Import mỗi CLB** (không câu cổng) + bảng `CLB.csv` (ClubId, Ten, Buoi, FormUrl để trống) để IT tạo list `CLB` từ bảng tính.
- **Q4b.** Bộ chuyển đổi nhận **nhiều tệp xuất, mỗi tệp một CLB** (đã nhận nhiều tệp khi tách theo buổi; cần nhận diện CLB theo mã `[clb_x-k]` trong tiêu đề câu).
- **Q4c.** Tuỳ chọn `--bai-thi BaiThi.csv`: đối chiếu list trạng thái với các tệp xuất (bài có ở list mà thiếu ở tệp xuất, hoặc ngược lại), để IT biết đã xuất đủ chưa.
- **M5.** Tài liệu: màn "Thi tuyển" trong app (bổ sung `T4M_DAC_TA_SUA_APP.md`) + flow mẫu "Đã làm" (bổ sung `T4M_FLOW_GUI_GVCN.md` hoặc tệp riêng), kèm bảng kiểm pass/fail.

`kiem_nhan` đề xuất: Q4a sinh đúng N tệp cho N CLB có đề, sinh lại giống hệt; Q4b N tệp mỗi CLB một tệp cho cùng Sổ nhập như một biểu mẫu chung trên cùng dữ liệu giả; Q4c bài thiếu / thừa được liệt kê, khớp đủ thì rỗng; chế độ cũ không đổi (bất biến 1).

## 7. Phương án lui nếu không sửa được app
Trang SharePoint của đợt: danh sách CLB có liên kết biểu mẫu + một khung xem list `BaiThi` lọc **[Me]** (người đang xem). Không cá nhân hoá theo NV, nhưng không cần sửa app (GĐ, TH).
