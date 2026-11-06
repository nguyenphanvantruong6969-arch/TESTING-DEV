# T4M-M1. Đặc tả sửa app ECA: từ "một lựa chọn mỗi ngày" sang Top 3 mỗi ngày

Mã việc: **T4M-NC / T4M-M1** (Truong duyệt 06/11/2026). Soạn **06/11/2026**. Tài liệu cho **người sửa app (IT)**; chưa ai chạy.
Nhãn: **ĐXM** (đã mở trang gốc, `T4M_KET_QUA_TAI_LIEU.md`), **GĐ** (giả định, chưa kiểm; **mọi công thức dưới đây là GĐ**), **HỎI-IT**, **TH** (việc cần thử; pass/fail điền ở mục 9 của `T4M_HUONG_DAN_THU.md`, viết tắt HDT).
Phạm vi: chỉ sửa **bản sao** của app trong môi trường thử (NC-02). **Không đụng app thật**, không ghi tên thật, email thật, `tenantId`, địa chỉ app vào kho mã hay ảnh chụp.

## 0. Hiện trạng và đích

| | Hôm nay (ảnh chụp app, kế hoạch §1) | Đích |
|---|---|---|
| Mỗi ngày Thứ 2 đến Thứ 6 | 1 ô thả xuống, 1 lựa chọn, không xếp hạng | 3 ô: `NV1` > `NV2` > `NV3` (xếp hạng) |
| Ngày không chọn | (HỎI-IT) | Hợp lệ, cả ba ô trống |
| Sức chứa CLB | không giới hạn, xếp tay | không đổi ở app; kiosk xếp theo chỉ tiêu |
| Khoá | admin khoá sau hạn | `TrangThai = "Đã khóa"` tắt mọi ô |

Kho (đã chốt, HDT §0.2): **SharePoint List**, mô hình **rộng**: một dòng cho mỗi (học sinh, ngày). Nếu kho thật là Dataverse thì cột giữ nguyên, công thức đổi theo (HỎI-IT, NC-01). Nhánh L/D: `T4M_MICROSOFT.md`.

## 1. Cột dữ liệu (khớp bộ sinh `du_lieu_test/sinh_xuat_lists_gia.py` và bảng cột HDT §1)

| Cột | Kiểu | Bắt buộc | Ghi chú |
|---|---|---|---|
| `Email` | Một dòng văn bản | có | Không dùng kiểu Person (NC-04, ĐXM). Hạ chữ thường khi nạp nếu làm được (GĐ); bộ chuyển đổi dù sao cũng hạ chữ thường |
| `CoSo`, `Khoi`, `Lop` | Choice / Số / Văn bản | có | `Lop` nguồn thật là HỎI-IT (NC-08) |
| `Thu` | Choice (`Thứ 2` … `Thứ 6`) | có | |
| `NV1`, `NV2`, `NV3` | Một dòng văn bản (mã CLB) | `NV1` không bắt buộc | Rỗng = chưa chọn |
| `TrangThai` | Choice (`Đang mở`, `Đã khóa`) | có | Đặt hàng loạt khi khoá |
| `CapDo`, `Goi` | Choice | không | Chỉ tạo cột; màn hình: mục 8 |

Bảng phụ `CLB_GIA` (`Thu`, `ClubId`, `TenCLB`, `ChiTieu`) dưới 500 dòng. Không đổi tên cột đã có nếu app thật đã dùng: thêm cột mới và ghi tương ứng vào bộ chuyển đổi (`doc_lists` đọc theo tên cột, bỏ cột thừa; HỎI-IT).

## 2. Hành vi màn hình

1. **Lấy dòng của em:** `Items` = `Filter(ECA, Email = User().Email)` (uỷ quyền được, NC-04). Một em thấy đúng 5 dòng. Email viết hoa trong dữ liệu vẫn phải khớp (rủi ro: so sánh phân biệt hoa thường; chuẩn hoá chữ thường ở dữ liệu nạp).
2. **Nguồn CLB mỗi ngày:** `ClearCollect(colCLB, Filter(CLB_GIA, Thu = <ngày>))` (phép lọc `=` ở nguồn). Việc loại CLB đã chọn làm **trên collection** `colCLB` (cục bộ), không đẩy `<>` lên SharePoint.
3. **Không trùng:** `NV2` loại giá trị của `NV1`; `NV3` loại `NV1` và `NV2`. Đổi `NV1` thì kiểm lại `NV2`/`NV3` có trùng không, xoá ô trùng.
4. **Không chừa ô giữa:** `NV2` chỉ bật khi `NV1` có giá trị; `NV3` chỉ bật khi `NV2` có giá trị (`DisplayMode`). Xoá `NV1` thì xoá luôn `NV2`, `NV3` (hoặc dồn lên).
5. **Ngày trống hợp lệ:** cả ba ô rỗng vẫn Gửi được; không có hộp thoại ép chọn.
6. **Nhãn hai ngôn ngữ:** mọi chữ trên màn lấy từ một collection `colNhan` (khoá, vi, en) đọc theo biến ngôn ngữ; không viết chữ cứng trong điều khiển. Tên CLB hai ngôn ngữ: nếu `CLB_GIA` chỉ có một tên thì ghi HỎI-IT, không tự dịch.
7. **Điện thoại:** bố cục đáp ứng (responsive), ô thả xuống bấm được bằng ngón tay, không cuộn ngang. Mỗi ngày một thẻ gập được.
8. **Hiện trạng đã lưu:** mở app lại thì `NV1..NV3` hiện đúng giá trị đã Gửi (đọc từ list, không từ biến cục bộ).

## 3. Gửi, `Patch` và `IfError` (GĐ)

```
IfError(
    ForAll(GalleryNgay.AllItems As Dong,
        Patch(ECA, LookUp(ECA, ID = Dong.ID),
            {NV1: Dong.NV1.Selected.ClubId, NV2: Dong.NV2.Selected.ClubId, NV3: Dong.NV3.Selected.ClubId})),
    Notify(T("loi_luu") & " " & FirstError.Message, NotificationType.Error),
    Notify(T("da_luu"), NotificationType.Success)
)
```

`GalleryNgay`, `Dong`, `T()` là tên ví dụ. Mỗi `Patch` là một yêu cầu: 5 ngày = 5 yêu cầu, xa dưới 6.000 mỗi người mỗi 24 giờ (NC-13, ĐXM).
- **Không có giao dịch** trong SharePoint (NC-05): một lần Gửi có thể lưu nửa chừng. Yêu cầu: thông báo nêu **đúng ngày chưa lưu**, bấm Gửi lại thì ghi đủ (idempotent: `Patch` cùng giá trị không sinh dòng thừa).
- Trước mỗi `Patch` kiểm `LookUp(ECA, ID = Dong.ID).TrangThai = "Đang mở"` (đọc lại, `=` uỷ quyền được) để người mở app trước giờ khoá không ghi đè sau khoá.
- Em không tự sửa được trực tiếp list ngoài app: quyền SharePoint của học sinh chỉ đọc hoặc chỉ qua app (HỎI-IT, rủi ro: chỉnh `NV` bằng công cụ khác).

## 4. Khoá theo `TrangThai`

- Khi `TrangThai = "Đã khóa"`: ba ô của dòng đó `DisplayMode.Disabled`, nút Gửi tắt, hiện nhãn "Đã khóa / Locked".
- Khoá **theo dòng**, không theo biến toàn app; admin đặt `TrangThai` hàng loạt (chế độ xem bảng hoặc dạng nhóm trong list) hoặc bằng màn admin sẵn có (HỎI-IT).
- Sau khoá, người IT xuất list (xem `T4M_VAN_HANH_MOT_DOT.md` bước 3 đến 4) và coi tệp đó là bản chốt.

## 5. Chỉ dùng phép lọc uỷ quyền được (KQ NC-04, ĐXM)

| Dùng | Không dùng trên SharePoint |
|---|---|
| `Filter`, `LookUp`, `Sort` với `=` trên chữ, số, đúng/sai, ngày | `<`, `>` trên chữ |
| `ClearCollect` từ `Filter(…, Thu = x)` | `IsBlank` (dùng `= Blank()`), `Not` / `!` |
| Lọc cục bộ trên collection (không bị giới hạn uỷ quyền) | `CountRows` coi như không uỷ quyền (GĐ) |

Khi thử: đặt giới hạn dòng dữ liệu = 1 để lộ cảnh báo uỷ quyền (khuyến nghị tài liệu, ĐXM). Không được còn cảnh báo vàng/xanh ở công thức nào chạm list `ECA`.

## 6. Sao lưu và khôi phục phiên bản (NC-21, ĐXM)

1. Trước khi sửa: vào **Details > Versions** của app (bản sao thử), ghi số phiên bản hiện tại; xuất danh sách cột list làm đối chiếu.
2. Sửa trong **bản sao** (Save as) hoặc nhánh phiên bản, không sửa trực tiếp bản đang chạy.
3. Khôi phục: **Details > Versions > Restore** chọn bản cũ. Restore **tạo phiên bản mới**; phải bấm **Publish this version** riêng thì mới có hiệu lực (trang ghi là tiền phát hành, kiểm lại khi làm). Phiên bản quá 6 tháng được đóng gói lại.
4. Đường hạ cấp: nếu bản mới lỗi trong hạn đăng ký, Restore về phiên bản ghi ở bước 1, Publish, rồi báo giáo viên ECA. Dữ liệu đã nhập không bị xoá vì cột cũ giữ nguyên (mục 1).

## 7. Bảng yêu cầu và kiểm pass/fail

Mỗi yêu cầu một dòng kiểm; điền kết quả vào HDT §9 (cột bước). Tất cả là **TH** cho tới khi có người chạy.

| # | Yêu cầu | Kiểm (pass khi) | HDT §9 |
|---|---|---|---|
| R1 | Em chỉ thấy dòng của mình, kể cả email viết hoa | Tài khoản thử có email hoa thấy đủ 5 dòng, không dòng của người khác | 5.1 |
| R2 | Mỗi ngày có ba ô `NV1..NV3` | Màn hình 5 ngày, 15 ô | 5.2 |
| R3 | Không chọn trùng CLB trong một ngày | Ô `NV2` không có CLB của `NV1`; đổi `NV1` thành trùng `NV2` thì `NV2` bị xoá | 5.2 |
| R4 | Không ô trống chen giữa | `NV2` tắt khi `NV1` rỗng; xoá `NV1` thì `NV2`, `NV3` không còn giá trị mồ côi | 5.2 |
| R5 | Ngày trống hợp lệ | Gửi với một ngày cả ba ô rỗng, lưu thành công, dòng đó `NV1..NV3` rỗng | 5.2 |
| R6 | Gửi ghi đủ 5 dòng | Sau Gửi, list có 5 dòng đúng giá trị | 5.3 |
| R7 | Lỗi nửa chừng được báo đúng ngày | Cố ý làm hỏng `Patch` dòng thứ 3: thông báo nêu ngày đó; Gửi lại thì đủ | 5.3 |
| R8 | Khoá theo `TrangThai` | Dòng `Đã khóa` không sửa được, dòng `Đang mở` sửa được; `Patch` bị chặn nếu khoá giữa chừng | 5.4 |
| R9 | Chỉ phép lọc uỷ quyền được | Giới hạn dòng = 1: không cảnh báo uỷ quyền ở công thức nào chạm `ECA` | 5.1 |
| R10 | Hai ngôn ngữ | Chuyển vi/en: mọi nhãn đổi, không chữ cứng sót | HDT §9 dòng 5.5 |
| R11 | Điện thoại | Mở trên điện thoại, thao tác 3 ô một ngày bằng ngón tay, không cuộn ngang | 5.4 |
| R12 | Phiên bản có thể khôi phục | Làm một lần Restore + Publish trên bản thử, app chạy lại như cũ | HDT §9 dòng 5.6 |
| R13 | Tệp xuất qua bộ chuyển đổi không cảnh báo | Xuất List từ bản sao, chạy `chuyen_forms_sang_phan_mem.py --chi-thi --lists`: 0 cảnh báo ở phần Lists (`T4M_MICROSOFT.md` §8 hàng M1) | 4.2 |
| R14 | Không dữ liệu thật trong kho mã | Rà tệp, ảnh: không tên, email thật, `tenantId`, địa chỉ app | (thủ công) |

R10 và R12 ứng với dòng 5.5 và 5.6 của HDT §9.

## 8. Màn hình gói (chờ A8-GOI)

Chỗ giữ chỗ. Chưa thiết kế, chưa sửa. Chờ giáo viên ECA trả lời Q1 đến Q3 và mã **A8-GOI-1..3** (Truong, 06/11/2026). Hiện chỉ giữ cột `CapDo`, `Goi` trong list (mục 1) và **không** hiện gì cho học sinh. Khi có mã, đặc tả sẽ bám `T4M_GOI_THIET_KE.md` và HDT §6.

## 9. Giao lại và việc còn mở

- Giao cho người sửa app: tài liệu này, HDT §1 (bảng cột), tệp giả `lists_gia.csv` (sinh bằng lệnh HDT §1).
- Còn mở: **NC-01** (kho thật là gì, tên cột thật), **NC-02** (có môi trường thử không), **NC-08** (nguồn `Lop`), cách app ECA thật đang lưu tiếng Việt/Anh, quyền SharePoint của học sinh.
- Sau khi có tệp xuất mẫu thật (GĐ2): đối chiếu mục 1 với tên cột thật, sửa tài liệu này một lần.

## 10. Màn "Thi tuyển" (T4M-M5, Truong duyệt 06/11/2026; mức điểm 5a)

Bổ sung cho màn Top 3 ở mục 2. Thiết kế tổng thể: `T4M_CONG_THI.md` §1 đến §5. Flow ghi "Đã làm": `T4M_FLOW_DA_LAM.md`. **Mọi công thức là GĐ, mọi kiểm là TH.** Chỉ connector chuẩn; app **không** có connector Forms (Power Apps: Not available, KQ §7.1 ĐXM), nên app chỉ mở liên kết và đọc list.

### 10.1 Dữ liệu thêm
| Thứ | Cột | Ghi chú |
|---|---|---|
| List `CLB` (tạo từ `CLB.csv` do `tao_mau_forms.py --moi-clb` sinh, T4M-Q4a) | `ClubId`, `Ten`, `Buoi`, `FormUrl` | `FormUrl` rỗng = CLB không thi. IT dán liên kết biểu mẫu sau khi tạo; dưới 500 dòng nên đọc trọn vào collection |
| List `BaiThi` (flow ghi, app chỉ đọc) | `Email`, `ClubId`, `ResponseId`, `NopLuc` (`Diem` không dùng ở mức 5a) | `Email` chữ thường. Một dòng mỗi bài đã nộp |

### 10.2 Hành vi màn hình
1. **CLB có thi mà em đã chọn:** từ năm dòng `ECA` của em (mục 2.1) gom `NV1..NV3` của mọi ngày vào `colChon` (`ForAll` + `Collect`, cục bộ), rồi `colThi` = các dòng `colCLB` có `ClubId` thuộc `colChon` và `FormUrl` không rỗng. Lọc `FormUrl` và `ClubId in` làm **trên collection**, không đẩy lên SharePoint (`IsBlank`, `Not` không uỷ quyền, mục 5).
2. **Trạng thái:** `ClearCollect(colBaiThi, Filter(BaiThi, Email = Lower(User().Email)))` (lọc `=`, uỷ quyền được, NC-04). "Đã làm" khi `colBaiThi` có dòng cùng `ClubId`; ngược lại "Chưa làm".
3. **Nút Làm bài:** `Launch(FormUrl)` (mở tab mới). Hiện **chỉ khi** chưa có dòng `BaiThi` của CLB đó **và** đang trong hạn (dòng `ECA` của em còn `TrangThai = "Đang mở"`); sau khoá thì ẩn, hiện nhãn "Đã đóng / Closed". Forms "One response per person" vẫn chặn nộp lần hai ở phía Forms.
4. **Nút Làm mới:** chạy lại `ClearCollect(colBaiThi, …)`. Cạnh nút ghi: "Trạng thái cập nhật sau vài giây đến vài phút".
5. **Em bỏ CLB khỏi NV sau khi đã thi:** dòng `BaiThi` vẫn có, nhưng CLB không còn trong `colThi` nên không hiện. Bộ chuyển đổi bỏ điểm CLB không chọn và báo (T4M_CONG_THI.md §4.5).
6. **Không hiện điểm** (mức 5a): ghi cố định "Xem điểm trong Forms sau khi giáo viên công bố" / "See your score in Forms after your teacher posts scores". Không cột `Diem`, không điều khiển điểm.
7. **Hai ngôn ngữ, điện thoại:** như mục 2.6 và 2.7: nhãn từ `colNhan`, thẻ mỗi CLB một dòng, nút đủ lớn cho ngón tay.
8. **Rỗng:** em không chọn CLB nào có thi thì hiện "Bạn không có CLB cần thi", không để màn trắng.

### 10.3 Công thức mẫu (GĐ)
```
// OnVisible của màn Thi tuyển
ClearCollect(colCLB, CLB);
ClearCollect(colBaiThi, Filter(BaiThi, Email = Lower(User().Email)));
ClearCollect(colEca, Filter(ECA, Email = Lower(User().Email)));
Clear(colChon);
ForAll(colEca, Collect(colChon, {Id: NV1}, {Id: NV2}, {Id: NV3}));
// Items của thư viện
Filter(colCLB, ClubId in colChon.Id && FormUrl <> "")
// Trạng thái từng thẻ
!IsEmpty(Filter(colBaiThi, ClubId = ThisItem.ClubId))
```
`colCLB`, `colChon`, `colEca` là tên ví dụ. Ô `NV` rỗng thêm giá trị rỗng vào `colChon`, không khớp CLB nào nên vô hại.

### 10.4 Bảng yêu cầu và kiểm pass/fail (nối tiếp R1 đến R14, mục 7)

Dòng 13.1 đến 13.4 của HDT §9 (mục 13 của HDT; Opus thêm khi soát 06/11/2026; số 7.x đã dùng cho flow xuất CSV).

| # | Yêu cầu | Kiểm (pass khi) | HDT §9 |
|---|---|---|---|
| R15 | Chỉ hiện CLB có thi mà em đã chọn | Tài khoản thử chọn 2 CLB có thi, 1 không thi: màn hiện đúng 2 thẻ | 13.1 |
| R16 | Nút Làm bài mở đúng biểu mẫu của CLB | Bấm mỗi thẻ: tab mới mở biểu mẫu đúng CLB (đối chiếu tiêu đề) | 13.1 |
| R17 | Trạng thái "Đã làm" xuất hiện sau khi nộp | Nộp bài thử, bấm Làm mới: thẻ chuyển "Đã làm" và nút Làm bài ẩn; ghi thời gian trễ thực đo | 13.2 |
| R18 | Không hiện nút khi đã làm hoặc đã khoá | Có dòng `BaiThi` thì không nút; đặt `TrangThai = Đã khóa` thì không nút, hiện "Đã đóng" | 13.2 |
| R19 | Không hiện điểm | Tìm trên mọi màn: không số điểm; có dòng "Xem điểm trong Forms…" | 13.3 |
| R20 | Chỉ lọc uỷ quyền được | Giới hạn dòng = 1: không cảnh báo uỷ quyền ở công thức chạm `BaiThi`, `ECA` | 13.3 |
| R21 | Em chỉ thấy bài của mình | Hai tài khoản thử: mỗi em chỉ thấy dòng `BaiThi` của mình (kể cả email hoa) | 13.3 |
| R22 | Hai ngôn ngữ, điện thoại | Như R10 và R11 cho màn này | 13.4 |
| R23 | Màn trống không lỗi | Tài khoản không chọn CLB thi: hiện thông báo, không lỗi công thức | 13.4 |
| R24 | Em không sửa được `BaiThi` | Tài khoản học sinh thử ghi trực tiếp vào list `BaiThi` bị từ chối (quyền chỉ đọc; HỎI-IT) | 13.4 |

### 10.5 Lui (nếu không sửa được app)
Trang SharePoint của đợt: danh sách CLB kèm liên kết biểu mẫu và khung xem `BaiThi` lọc **[Me]** (`T4M_CONG_THI.md` §7). Không rẽ theo NV; không cần sửa app.
