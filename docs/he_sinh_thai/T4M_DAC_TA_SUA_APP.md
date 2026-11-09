# T4M-M1 / M6. Đặc tả sửa app ECA: từ "một lựa chọn mỗi ngày" sang tối đa 7 nguyện vọng, tick chọn thi và điểm quyết tâm

Mã việc: **T4M-NC / T4M-M1** (Truong duyệt 06/11/2026), sửa theo **T4M-M6** (Truong quyết 06/11/2026, vòng 4: tối đa **7** nguyện vọng mỗi ngày thay cho mức 3 nguyện vọng đề xuất trước đó, **tick chọn thi** tối đa 5 CLB mỗi ngày, **điểm quyết tâm** thu trên app). Soạn **06/11/2026**. Tài liệu cho **người sửa app (IT)**; chưa ai chạy.
Nhãn: **ĐXM** (đã mở trang gốc, `T4M_KET_QUA_TAI_LIEU.md`), **GĐ** (giả định, chưa kiểm; **mọi công thức dưới đây là GĐ**), **HỎI-IT**, **TH** (việc cần thử; pass/fail điền ở mục 9 của `T4M_HUONG_DAN_THU.md`, viết tắt HDT).
Phạm vi: chỉ sửa **bản sao** của app trong môi trường thử (NC-02). **Không đụng app thật**, không ghi tên thật, email thật, `tenantId`, địa chỉ app vào kho mã hay ảnh chụp.

## 0. Hiện trạng và đích

| | Hôm nay (ảnh chụp app, kế hoạch §1) | Đích |
|---|---|---|
| Mỗi ngày Thứ 2 đến Thứ 6 | 1 ô thả xuống, 1 lựa chọn, không xếp hạng | Tối đa 7 ô: `NV1` > … > `NV7` (xếp hạng); số ô = min(7, số CLB của ngày đó) |
| Chọn CLB nào để thi | (HỎI-IT) | Mỗi dòng NV có CLB có đề thì có ô tick "Thi"; tối đa **5** tick mỗi ngày (`TRAN_CLB_THI_MOI_BUOI` của kiosk) |
| Điểm quyết tâm | không có | Mỗi ngày hai quỹ 100 điểm: quỹ 1 chia cho CLB đã tick thi, quỹ 2 cho CLB còn lại (`HUONG_DAN_SU_DUNG.md` §14) |
| Ngày không chọn | (HỎI-IT) | Hợp lệ, mọi ô `NV`, `THI`, `WP` của ngày trống |
| Sức chứa CLB | không giới hạn, xếp tay | không đổi ở app; kiosk xếp theo chỉ tiêu |
| Khoá | admin khoá sau hạn | `TrangThai = "Đã khóa"` tắt mọi ô |

Kho (đã chốt, HDT §0.2): **SharePoint List**, mô hình **rộng**: một dòng cho mỗi (học sinh, ngày). Nếu kho thật là Dataverse thì cột giữ nguyên, công thức đổi theo (HỎI-IT, NC-01). Nhánh L/D: `T4M_MICROSOFT.md`.

## 1. Cột dữ liệu (khớp bộ sinh `du_lieu_test/sinh_xuat_lists_gia.py` và bảng cột HDT §1)

| Cột | Kiểu | Bắt buộc | Ghi chú |
|---|---|---|---|
| `Email` | Một dòng văn bản | có | Không dùng kiểu Person (NC-04, ĐXM). Hạ chữ thường khi nạp nếu làm được (GĐ); bộ chuyển đổi dù sao cũng hạ chữ thường |
| `CoSo`, `Khoi`, `Lop` | Choice / Số / Văn bản | có | `Lop` nguồn thật là HỎI-IT (NC-08) |
| `Thu` | Choice (`Thứ 2` … `Thứ 6`) | có | |
| `NV1` … `NV7` | Một dòng văn bản (mã CLB) | `NV1` không bắt buộc | Rỗng = chưa chọn |
| `THI1` … `THI7` | Một dòng văn bản: `Có` hoặc rỗng | không | Chỉ số k đi cùng `NVk`. `Có` chỉ hợp lệ khi CLB ở `NVk` có đề (`FormUrl` không rỗng ở list `CLB`, `T4M_CONG_THI.md`) |
| `WP1` … `WP7` | Số nguyên ≥ 0 | không | Điểm quyết tâm của CLB ở `NVk`; rỗng = 0. Quỹ 1 = các `WPk` có `THIk = Có`; quỹ 2 = các `WPk` còn lại |
| `TrangThai` | Choice (`Đang mở`, `Đã khóa`) | có | Đặt hàng loạt khi khoá |
| `CapDo`, `Goi` | Choice | không | Chỉ tạo cột; màn hình: mục 8 |

Ba nhóm cột `NVk`, `THIk`, `WPk` có **cùng chỉ số k** và là hợp đồng với bộ chuyển đổi (T4M-Q5a/b/c, `T4M_KE_HOACH_TU_DONG.md` §8). Một dòng list nay có khoảng 30 cột (ước lượng, TH: kiểm giới hạn số cột và hiển thị của list ở bước 3.1 của HDT).

Bảng phụ `CLB_GIA` (`Thu`, `ClubId`, `TenCLB`, `ChiTieu`) dưới 500 dòng. Không đổi tên cột đã có nếu app thật đã dùng: thêm cột mới và ghi tương ứng vào bộ chuyển đổi (`doc_lists` đọc theo tên cột, bỏ cột thừa; HỎI-IT).

## 2. Hành vi màn hình

1. **Lấy dòng của em:** `Items` = `Filter(ECA, Email = User().Email)` (uỷ quyền được, NC-04). Một em thấy đúng 5 dòng. Email viết hoa trong dữ liệu vẫn phải khớp (rủi ro: so sánh phân biệt hoa thường; chuẩn hoá chữ thường ở dữ liệu nạp).
2. **Nguồn CLB mỗi ngày:** `ClearCollect(colCLB, Filter(CLB_GIA, Thu = <ngày>))` (phép lọc `=` ở nguồn). Việc loại CLB đã chọn làm **trên collection** `colCLB` (cục bộ), không đẩy `<>` lên SharePoint.
3. **Số ô và không trùng:** số ô thả xuống của ngày = `min(7, CountRows(colCLB))` (nếu ngày có 4 CLB thì 4 ô). Ô `NVk` loại giá trị của `NV1..NV(k-1)`. Đổi một ô thì kiểm lại các ô sau có trùng không, xoá ô trùng (cùng với `THIk`, `WPk` của ô đó).
4. **Không chừa ô giữa:** `NV(k+1)` chỉ bật khi `NVk` có giá trị (`DisplayMode`). Xoá `NVk` thì dồn các ô sau lên một bậc **kèm `THI` và `WP` của chúng** (hoặc xoá hết các ô sau; chọn một cách và ghi rõ ở app).
5. **Ngày trống hợp lệ:** mọi ô `NV`, `THI`, `WP` của ngày rỗng vẫn Gửi được; không có hộp thoại ép chọn.
5a. **Tick "Thi" (T4M-M6):** cạnh mỗi ô `NVk` có ô tick, **chỉ hiện khi CLB đang chọn có đề** (`FormUrl` không rỗng trong `colCLB`). Tối đa **5 tick mỗi ngày**: đủ 5 thì các ô tick còn lại tắt (`DisplayMode.Disabled`) và hiện chữ "Tối đa 5 CLB thi mỗi ngày"; bỏ một tick thì bật lại. Đổi hoặc xoá CLB ở `NVk` thì `THIk` và `WPk` của ô đó bị xoá. Tick chỉ nói "em chọn thi CLB này", **không** ảnh hưởng thứ tự xếp hạng.
5b. **Bước điểm quyết tâm của ngày (T4M-M6):** sau các ô `NV`, mỗi ngày có hai khung. **Khung 1** liệt kê CLB đã tick; **khung 2** liệt kê các CLB còn lại. Mỗi CLB một ô số nguyên ≥ 0; mỗi khung có bộ đếm "Đã dùng X / 100" cập nhật khi gõ. Khung chỉ có một CLB: ô tự điền 100 và khoá. Khung không có CLB thì không hiện và không đòi điểm. Đổi tick sau khi đã chia điểm: điểm hai khung của ngày đó bị xoá, hiện dòng "Cần chia lại điểm" (khớp kiosk, `HUONG_DAN_SU_DUNG.md` §14). Ô không phải số nguyên ≥ 0 (`12,5`, `-3`, `abc`) bị từ chối ngay, không lưu.
5c. **Chặn Gửi:** nút Gửi tắt (hoặc báo lỗi, không ghi) khi có ngày mà một khung **không rỗng** có tổng khác 100; thông báo nêu đúng ngày, đúng khung và còn thiếu hay thừa bao nhiêu. Lý do: kiosk không chạy xếp khi điểm chưa đủ, nên chặn ngay ở app (bộ chuyển đổi chỉ cảnh báo, không sửa giá trị).
6. **Nhãn hai ngôn ngữ:** mọi chữ trên màn lấy từ một collection `colNhan` (khoá, vi, en) đọc theo biến ngôn ngữ; không viết chữ cứng trong điều khiển. Tên CLB hai ngôn ngữ: nếu `CLB_GIA` chỉ có một tên thì ghi HỎI-IT, không tự dịch.
7. **Điện thoại:** bố cục đáp ứng (responsive), ô thả xuống bấm được bằng ngón tay, không cuộn ngang. Mỗi ngày một thẻ gập được.
8. **Hiện trạng đã lưu:** mở app lại thì `NV1..NV7`, các tick `THI` và điểm `WP` hiện đúng giá trị đã Gửi (đọc từ list, không từ biến cục bộ).
9. **Màn điện thoại (T4M-M6, HỎI-ECA):** bảy dòng NV, tick và hai khung điểm phải dùng được bằng ngón tay: bàn phím số cho ô điểm, bộ đếm luôn nhìn thấy khi gõ, không cuộn ngang. Giáo viên ECA có chấp nhận chia điểm trên màn điện thoại không: câu ECA-12 của phiếu phỏng vấn.

## 3. Gửi, `Patch` và `IfError` (GĐ)

```
IfError(
    ForAll(GalleryNgay.AllItems As Dong,
        Patch(ECA, LookUp(ECA, ID = Dong.ID),
            {NV1: Dong.NV1.Selected.ClubId, NV2: Dong.NV2.Selected.ClubId, /* … đến NV7 */
             THI1: If(Dong.Tick1.Value, "Có", Blank()), /* … đến THI7 */
             WP1: Value(Dong.Diem1.Text), /* … đến WP7 */ })),
    Notify(T("loi_luu") & " " & FirstError.Message, NotificationType.Error),
    Notify(T("da_luu"), NotificationType.Success)
)
```

`GalleryNgay`, `Dong`, `Tick1`, `Diem1`, `T()` là tên ví dụ. Mỗi `Patch` là một yêu cầu và **một `Patch` ghi cả 21 cột** (`NV`, `THI`, `WP`) của dòng: 5 ngày = 5 yêu cầu, xa dưới 6.000 mỗi người mỗi 24 giờ (NC-13, ĐXM). Trước `IfError` kiểm điều kiện 5c (mỗi khung không rỗng đủ 100, tối đa 5 tick); không đủ thì không `Patch` ngày nào.
- **Không có giao dịch** trong SharePoint (NC-05): một lần Gửi có thể lưu nửa chừng. Yêu cầu: thông báo nêu **đúng ngày chưa lưu**, bấm Gửi lại thì ghi đủ (idempotent: `Patch` cùng giá trị không sinh dòng thừa).
- Trước mỗi `Patch` kiểm `LookUp(ECA, ID = Dong.ID).TrangThai = "Đang mở"` (đọc lại, `=` uỷ quyền được) để người mở app trước giờ khoá không ghi đè sau khoá.
- Em không tự sửa được trực tiếp list ngoài app: quyền SharePoint của học sinh chỉ đọc hoặc chỉ qua app (HỎI-IT, rủi ro: chỉnh `NV` bằng công cụ khác).

## 4. Khoá theo `TrangThai`

- Khi `TrangThai = "Đã khóa"`: mọi ô `NV`, tick `THI` và ô điểm `WP` của dòng đó `DisplayMode.Disabled`, nút Gửi tắt, hiện nhãn "Đã khóa / Locked".
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
| R2 | Mỗi ngày có `min(7, số CLB của ngày)` ô `NV` | Ngày có 9 CLB hiện 7 ô; ngày có 4 CLB hiện 4 ô; không bao giờ hơn 7 | 5.2 |
| R3 | Không chọn trùng CLB trong một ngày | Ô `NV2` không có CLB của `NV1`; ô `NV7` không có CLB của sáu ô trước; đổi `NV1` thành trùng `NV2` thì `NV2` bị xoá (kèm `THI2`, `WP2`) | 5.2 |
| R4 | Không ô trống chen giữa | `NV2` tắt khi `NV1` rỗng; xoá `NV1` thì `NV2..NV7` không còn giá trị mồ côi (dồn lên thì `THI`, `WP` đi theo) | 5.2 |
| R5 | Ngày trống hợp lệ | Gửi với một ngày mọi ô rỗng, lưu thành công, dòng đó `NV1..NV7`, `THI1..THI7`, `WP1..WP7` đều rỗng | 5.2 |
| R6 | Gửi ghi đủ 5 dòng | Sau Gửi, list có 5 dòng đúng giá trị ở cả ba nhóm cột `NV`, `THI`, `WP` | 5.3 |
| R7 | Lỗi nửa chừng được báo đúng ngày | Cố ý làm hỏng `Patch` dòng thứ 3: thông báo nêu ngày đó; Gửi lại thì đủ | 5.3 |
| R8 | Khoá theo `TrangThai` | Dòng `Đã khóa` không sửa được, dòng `Đang mở` sửa được; `Patch` bị chặn nếu khoá giữa chừng | 5.4 |
| R9 | Chỉ phép lọc uỷ quyền được | Giới hạn dòng = 1: không cảnh báo uỷ quyền ở công thức nào chạm `ECA` | 5.1 |
| R10 | Hai ngôn ngữ | Chuyển vi/en: mọi nhãn đổi, không chữ cứng sót | HDT §9 dòng 5.5 |
| R11 | Điện thoại | Mở trên điện thoại, thao tác các ô một ngày (tới 7 ô) bằng ngón tay, không cuộn ngang | 5.4 |
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

Bổ sung cho màn nguyện vọng (tối đa 7 mỗi ngày) ở mục 2. Thiết kế tổng thể: `T4M_CONG_THI.md` §1 đến §5. Flow ghi "Đã làm": `T4M_FLOW_DA_LAM.md`. **Mọi công thức là GĐ, mọi kiểm là TH.** Chỉ connector chuẩn; app **không** có connector Forms (Power Apps: Not available, KQ §7.1 ĐXM), nên app chỉ mở liên kết và đọc list.

### 10.1 Dữ liệu thêm
| Thứ | Cột | Ghi chú |
|---|---|---|
| List `CLB` (tạo từ `CLB.csv` do `tao_mau_forms.py --moi-clb` sinh, T4M-Q4a) | `ClubId`, `Ten`, `Buoi`, `FormUrl` | `FormUrl` rỗng = CLB không thi. IT dán liên kết biểu mẫu sau khi tạo; dưới 500 dòng nên đọc trọn vào collection |
| List `BaiThi` (flow ghi, app chỉ đọc) | `Email`, `ClubId`, `ResponseId`, `NopLuc` (`Diem` không dùng ở mức 5a) | `Email` chữ thường. Một dòng mỗi bài đã nộp |

### 10.2 Hành vi màn hình
1. **CLB em đã tick thi (T4M-M6):** từ năm dòng `ECA` của em (mục 2.1) gom, của mọi ngày, các `NVk` mà `THIk = "Có"` vào `colChon` (`ForAll` + `Collect`, cục bộ), rồi `colThi` = các dòng `colCLB` có `ClubId` thuộc `colChon` và `FormUrl` không rỗng. **CLB có đề nhưng em không tick thì không hiện thẻ**, kể cả khi nằm trong `NV`: tối đa 5 thẻ mỗi ngày. Lọc `FormUrl` và `ClubId in` làm **trên collection**, không đẩy lên SharePoint (`IsBlank`, `Not` không uỷ quyền, mục 5).
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
ForAll(colEca As E, Collect(colChon, Filter(Table({Id: E.NV1, T: E.THI1}, {Id: E.NV2, T: E.THI2}, /* … đến NV7, THI7 */), T = "Có")));
// Items của thư viện
Filter(colCLB, ClubId in colChon.Id && FormUrl <> "")
// Trạng thái từng thẻ
!IsEmpty(Filter(colBaiThi, ClubId = ThisItem.ClubId))
```
`colCLB`, `colChon`, `colEca` là tên ví dụ. Chỉ hàng có `T = "Có"` vào `colChon`; lọc làm trên bảng cục bộ nên không dính giới hạn uỷ quyền (GĐ, TH).

### 10.4 Bảng yêu cầu và kiểm pass/fail (nối tiếp R1 đến R14, mục 7)

Dòng 13.1 đến 13.4 của HDT §9 (mục 13 của HDT; Opus thêm khi soát 06/11/2026; số 7.x đã dùng cho flow xuất CSV).

| # | Yêu cầu | Kiểm (pass khi) | HDT §9 |
|---|---|---|---|
| R15 | Chỉ hiện CLB có thi mà em đã **tick** | Tài khoản thử chọn 3 CLB có đề, tick 2, và 1 CLB không đề: màn hiện đúng 2 thẻ (CLB có đề không tick và CLB không đề không hiện) | 13.1 |
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

## 11. Top 7, tick chọn thi và điểm quyết tâm: bảng yêu cầu (T4M-M6, Truong quyết 06/11/2026)

Hành vi: mục 2 (điểm 3, 4, 5a, 5b, 5c, 8, 9). Nối tiếp R1 đến R24. Kết quả điền ở **HDT §9 dòng 14.x** (mục 14 của HDT). **Tất cả là TH**: chưa ai dựng, chưa có số đo. Quy tắc nền: kiosk đã có sẵn tick (ô "Điểm thi" chữ `thi`), trần 5 (`so_nhap_qua_tran_thi`) và điểm quyết tâm (`diem_w`); app chỉ cần ghi đúng ba nhóm cột `NVk`, `THIk`, `WPk` (`T4M_KE_HOACH_TU_DONG.md` §8). Không sửa lõi, schema, hợp đồng CSV.

| # | Yêu cầu | Kiểm (pass khi) | HDT §9 |
|---|---|---|---|
| R25 | Ô tick "Thi" chỉ hiện ở dòng NV có CLB có đề | Chọn CLB có `FormUrl` thì thấy tick; chọn CLB không có `FormUrl` thì không có tick; đổi từ CLB có đề sang CLB không đề thì tick biến mất và `THIk` rỗng | 14.1 |
| R26 | Tối đa 5 tick mỗi ngày | Tick 5 CLB: các tick còn lại tắt và có chữ giải thích; bỏ một tick thì tick lại được; thử ngày có 7 CLB đều có đề: không thể tick CLB thứ 6 | 14.1 |
| R27 | Xoá hoặc đổi CLB ở `NVk` thì xoá `THIk`, `WPk` của ô đó | Tick và nhập điểm cho `NV3`, rồi đổi `NV3` sang CLB khác: tick tắt, điểm rỗng; list sau Gửi không còn giá trị mồ côi | 14.2 |
| R28 | Hai khung điểm đúng theo tick | CLB đã tick nằm ở khung 1, CLB còn lại ở khung 2; đổi tick thì CLB chuyển khung và điểm của ngày đó bị xoá, hiện "Cần chia lại điểm" | 14.2 |
| R29 | Bộ đếm "Đã dùng X / 100" đúng khi gõ | Gõ lần lượt các ô: bộ đếm của khung đó cập nhật ngay; khung kia không đổi | 14.3 |
| R30 | Khung chỉ có một CLB tự điền 100 và khoá; khung rỗng không đòi điểm | Ngày tick đủ mọi CLB (khung 2 rỗng) và ngày không tick (khung 1 rỗng): Gửi được khi khung kia đủ 100; khung một CLB hiện 100 và không sửa được | 14.3 |
| R31 | Chặn Gửi khi khung không rỗng ≠ 100 | Để khung 1 tổng 90: Gửi bị chặn, thông báo nêu đúng ngày, khung, còn thiếu 10; sửa thành 100 thì Gửi được; tổng 110 báo thừa 10 | 14.3 |
| R32 | Ô điểm chỉ nhận số nguyên ≥ 0 | Gõ `12,5`, `-3`, `abc`: bị từ chối ngay, không lưu; để trống tính là 0 | 14.3 |
| R33 | Một lần Gửi vẫn 5 yêu cầu `Patch`, ghi đủ ba nhóm cột | Sau Gửi, list có 5 dòng; mỗi dòng đúng `NV1..NV7`, `THI1..THI7` (`Có` hoặc rỗng), `WP1..WP7` (số nguyên); lịch sử chạy cho thấy 5 yêu cầu | 14.4 |
| R34 | Khoá tắt cả tick và ô điểm | Dòng `Đã khóa`: không tick được, không gõ điểm được, nút Gửi tắt | 14.4 |
| R35 | Thẻ Thi tuyển theo tick | CLB có đề trong `NV` nhưng không tick thì không có thẻ; tick rồi bỏ tick, bấm Làm mới thì thẻ biến mất; không bao giờ quá 5 thẻ mỗi ngày | 14.4 |
| R36 | `FormUrl` khớp `de_thi.json` | Mọi CLB có đề trong `de_thi.json` có `FormUrl` ở list `CLB`; CLB không đề thì `FormUrl` rỗng (nếu lệch thì bộ chuyển đổi cảnh báo "tick ở CLB không có đề") | 14.5 |
| R37 | Tệp xuất qua bộ chuyển đổi không cảnh báo | Xuất List từ bản sao, chạy `chuyen_forms_sang_phan_mem.py --chi-thi --lists`: 0 cảnh báo về tick (không đề, quá 5) và điểm (khung ≠ 100, ô không nguyên). Cảnh báo "vắng thi" chỉ có khi chạy kèm tệp xuất Forms và là hợp lệ khi em tick mà không nộp, nên không tính ở đây | 14.5 |
| R38 | Hai ngôn ngữ và điện thoại cho nhãn và màn mới | Chuyển vi/en: nhãn tick, khung, bộ đếm, thông báo đổi hết; điện thoại: bảy dòng + hai khung thao tác bằng ngón tay, bàn phím số, không cuộn ngang | 14.4 |

R36 và R37 cần D1 (T4M-Q5a/b/c) có mã trên nhánh; trước đó chỉ kiểm được R25 đến R35 bằng mắt trên app thử.

## 12. FA-DAA, đường A: màn đăng ký v2 và widget huy chương (FA-M5, TH, soạn 09/11/2026)

Mã việc: **FA-M5** (kế hoạch `docs/ke_hoach/FA_DAA_KE_HOACH.md` §3; tầm nhìn `FA_DAA_VISION.md` §5.1, §6). **Mọi công thức là GĐ, mọi kiểm là TH**: chưa ai dựng, chưa có số đo. Quyết định **D8** (Power Apps hay Forms) **chưa có**; mục này chỉ mô tả **đường A**. Đường B là FA-M2 (`mau_forms_thi_clb/CAI_DAT_FORMS_DANG_KY.md` do `tao_mau_forms.py --fa-daa` sinh). Chỉ sửa **bản sao** app (NC-02); không dữ liệu thật trong kho mã.

Mục này **thay thế** cho workspace FA: bước điểm quyết tâm hai khung (mục 2, điểm 5b, 5c: "Đã dùng X / 100", chặn Gửi theo tổng) và tick chọn thi (5a) cùng các yêu cầu R25 đến R38. Workspace không FA vẫn theo mục 2 và 11.

### 12.1 Cột dữ liệu (list `ECA`, một dòng mỗi học sinh × ngày; bộ dựng `tao_bo_dung_t4m.py --fa-daa`)

| Cột | Kiểu | Ghi chú |
|---|---|---|
| `Email`, `CoSo`, `Khoi`, `Lop`, `Thu`, `NV1`…`NV7`, `CapDo`, `Goi` | như mục 1 | không đổi |
| `WP1`…`WP7` | Số | **huy chương** của CLB ở `NVk`: 60 (vàng), 30 (bạc), 10 (đồng) hoặc rỗng. Không còn nghĩa "điểm quyết tâm". Cột có sẵn, dùng lại |
| `HC_TuChinh` | Văn bản | `Có` khi em đã tự chỉnh huy chương của ngày đó; rỗng = chưa chỉnh |
| `TrangThai` | Choice | `DRAFT` (tự lưu), `SUBMITTED` (đã nộp), `Đã khóa` (admin khoá sau hạn: đặt từ `SUBMITTED`) |
| `THI1`…`THI7` | — | **bỏ** ở chế độ FA: em xếp CLB Tuyển chọn nào thì phải làm bài CLB đó (biểu mẫu FA-M4); chưa làm thì bị coi NOT_ATTEMPTED khi xếp |

List `CLB_GIA` (hoặc `CLB`) cần thêm các cột lấy từ Phiếu thiết lập CLB (FA-M1, HỎI-IT về tên cột thật): `Loai` (Tự do / Giới hạn / Tuyển chọn), `ChiTieu`, `DiemSan`, `MoTa`. **Bộ chuyển đổi (FA-M3)**: bỏ dòng `DRAFT` (trừ khi chạy với `--nhan-ban-nhap`), lấy lần lưu cuối của (em, ngày), tự điền huy chương mặc định khi mọi `WPk` của ngày trống và `HC_TuChinh` trống, giữ nguyên `WPk` khi em đã đặt. Lệnh: `chuyen_forms_sang_phan_mem.py --fa-daa --so-nhap-clb SO_NHAP_CLB.xlsx --lists ECA.csv`.

### 12.2 Màn đăng ký (V§5.1)

1. **Một câu hướng dẫn** duy nhất ở đầu màn: "Xếp đúng thứ tự em thích. Xếp CLB khó vào lên đầu không làm em mất cơ hội ở CLB sau." (lấy từ `colNhan`, hai ngôn ngữ).
2. **Thứ tự CLB xáo ngẫu nhiên cho từng em:** `ClearCollect(colCLBNgau, Shuffle(Filter(CLB_GIA, Thu = <ngày>)))` ở `OnVisible` của thẻ ngày; chỉ chạy một lần mỗi lần mở ngày (thứ tự không đổi khi em chạm), để mỗi em thấy một thứ tự khác nhau.
3. **Hai khu:** "Các CLB của ngày" (`colCLBNgau` trừ `colXep`) và "Danh sách của em" (`colXep`, tối đa 7). Mỗi thẻ trong "Danh sách của em" có nút **▲**, **▼** (đổi chỗ với dòng kề, `Patch` trên `colXep`), **Bỏ**; không bắt buộc kéo thả. Hoán đổi hai dòng: `Patch(colXep, Index(colXep, i), {Ma: Index(colXep, i - 1).Ma, ...})` rồi ngược lại (GĐ).
4. **Thẻ CLB:** tên, mô tả một dòng, lịch, số chỗ, nhãn loại, có thử thách hay không, một ảnh. Nhãn: Tự do: "Tự do tham gia – em chắc chắn có chỗ." Giới hạn: "Giới hạn N chỗ – nếu đông, xét huy chương rồi bốc thăm." Tuyển chọn: "Tuyển chọn – N chỗ – có thử thách X phút. Dưới mốc M điểm sẽ không được xét." Học sinh **không** thấy số liệu nhu cầu và số huy chương mỗi CLB đang nhận.
5. **Tối thiểu 3 nguyện vọng mỗi ngày** (hoặc tất cả nếu ngày có ít hơn 3 CLB): nút Nộp tắt kèm chữ giải thích. Nếu danh sách không có CLB Tự do: hiện "Thêm một CLB Tự do để chắc chắn có chỗ." (cảnh báo, không chặn).
6. **Tự lưu:** sau mỗi thao tác (thêm, bỏ, ▲▼, đổi huy chương) chạy **một** `Patch` ghi `NV1`…`NV7`, `WP1`…`WP7`, `HC_TuChinh` và `TrangThai = "DRAFT"` của dòng ngày đó. Mở lại app thì đọc từ list (không từ biến cục bộ) và làm tiếp.
7. **Nộp:** `Patch` đặt `TrangThai = "SUBMITTED"` cho từng ngày có đủ điều kiện (mục 5), kiểm đọc lại `TrangThai <> "Đã khóa"` trước mỗi `Patch` (như mục 3). Hiện màn xác nhận; email tóm tắt là việc của flow (FA-M6). Sau khoá: mọi ô tắt, nhãn "Đã khóa / Locked".
8. **Số yêu cầu (NC-13, giới hạn 6.000 mỗi người mỗi 24 giờ):** giả sử tối đa 40 thao tác mỗi ngày × 5 ngày = 200 `Patch` tự lưu + 5 `Patch` nộp = 205 yêu cầu, còn xa dưới 6.000 (GĐ: 40 thao tác là ước lượng, chưa đo; đo ở R51).
9. Chỉ dùng phép lọc uỷ quyền được (mục 5), nhãn hai ngôn ngữ từ `colNhan`, điện thoại như mục 2 (điểm 6, 7).

### 12.3 Widget huy chương (V§6.1, D2)

1. **Ba ô huy chương** trên "Danh sách của em": vàng (60), bạc (30), đồng (10), mỗi ô chứa **một** CLB.
2. **Mặc định:** vàng, bạc, đồng cho ba CLB **không Tự do** xếp cao nhất trong danh sách của ngày; CLB Tự do bỏ qua. Ít hơn ba CLB không Tự do thì huy chương thừa để trống.
3. **Chưa chỉnh tay** (`HC_TuChinh` rỗng): đổi thứ tự thì huy chương **tự cập nhật** theo thứ tự mới, và app ghi `WPk` tương ứng. **Đã chỉnh tay** (`HC_TuChinh = "Có"`): giữ nguyên, hiện nhắc nhẹ "Huy chương không đổi theo thứ tự nữa vì em đã tự đặt".
4. **Hoán đổi** huy chương giữa các CLB trong danh sách; **mỗi CLB tối đa một huy chương**; không đặt vào CLB Tự do; một huy chương chỉ ở một CLB. Bỏ CLB khỏi danh sách thì huy chương của nó bị xoá (và nếu chưa chỉnh tay thì tự cập nhật lại).
5. Khi đặt **vàng vào CLB Tuyển chọn** hiện: "Huy chương ở CLB Tuyển chọn chỉ dùng khi bằng điểm, và chỉ khi em vượt mốc."
6. **Không** ô số, **không** bộ đếm "Đã dùng X / 100", **không** hai khung: chỉ thứ tự vàng > bạc > đồng > không có ý nghĩa (V§6.2); 60/30/10 chỉ để tương thích quỹ 100 điểm của kiosk.
7. Ánh xạ: `WPk` của CLB ở `NVk` = 60, 30, 10 theo huy chương, rỗng nếu không có. Kiosk dùng đúng một quỹ (`fa_daa.diem_huy_chuong_hieu_luc`).

### 12.4 Bảng yêu cầu và kiểm pass/fail (nối tiếp R1 đến R38; tất cả TH)

| # | Yêu cầu | Kiểm (pass khi) |
|---|---|---|
| R39 | Thứ tự CLB xáo cho từng em | Hai tài khoản thử mở cùng ngày thấy hai thứ tự khác nhau; trong một lần mở, thứ tự không đổi khi chạm |
| R40 | ▲ ▼ đổi đúng chỗ | Mỗi nút đổi đúng một dòng với dòng kề; ▲ ở dòng đầu và ▼ ở dòng cuối tắt |
| R41 | Danh sách tối đa 7 và không trùng | Không thêm được CLB thứ 8; CLB đã vào danh sách biến khỏi khu "Các CLB của ngày" |
| R42 | Tối thiểu 3 nguyện vọng mỗi ngày | Ngày có 9 CLB: dưới 3 thì Nộp tắt, đủ 3 thì bật; ngày có 2 CLB: chọn cả 2 là Nộp được |
| R43 | Cảnh báo thiếu CLB Tự do | Danh sách không có CLB Tự do hiện đúng câu cảnh báo; thêm một CLB Tự do thì câu biến mất; Nộp vẫn được |
| R44 | Tự lưu DRAFT | Sau mỗi thao tác, list có dòng đúng `NVk`, `WPk` và `TrangThai = DRAFT`; đóng và mở lại app thì danh sách và huy chương hiện đúng |
| R45 | Nộp đặt SUBMITTED | Nộp 5 ngày: 5 dòng `SUBMITTED`; màn xác nhận hiện |
| R46 | Khoá | Dòng `Đã khóa`: không sửa được; Nộp bị chặn nếu khoá giữa chừng |
| R47 | Nhãn thẻ theo loại | Ba loại hiện đúng ba câu nhãn; không số liệu nhu cầu, không số huy chương mỗi CLB |
| R48 | Huy chương mặc định | Danh sách [Tự do, A, B, C]: vàng A, bạc B, đồng C, Tự do không nhận; danh sách [Tự do, A]: chỉ vàng A |
| R49 | Tự cập nhật khi chưa chỉnh tay; giữ khi đã chỉnh | Đổi ▲▼ khi `HC_TuChinh` rỗng: huy chương đổi theo; sau một lần hoán đổi tay (`HC_TuChinh = Có`): đổi ▲▼ không làm huy chương đổi, có nhắc nhẹ |
| R50 | Hoán đổi đủ mọi cách, mỗi CLB tối đa một | Đặt được cả 6 cách vàng/bạc/đồng cho ba CLB; không đặt hai huy chương vào một CLB; không đặt vào CLB Tự do |
| R51 | Số yêu cầu | Một em làm trọn 5 ngày: ghi số `Patch` thật trong lịch sử chạy, dưới 6.000 (ước lượng 205) |
| R52 | Nhắc vàng ở Tuyển chọn | Đặt vàng vào CLB Tuyển chọn hiện đúng câu nhắc; đặt vào CLB Giới hạn thì không |
| R53 | Tệp xuất qua bộ chuyển đổi FA không cảnh báo | Xuất List từ bản sao, chạy `chuyen_forms_sang_phan_mem.py --fa-daa --lists`: 0 cảnh báo, trừ dòng `DRAFT` còn sót; huy chương hợp lệ |
| R54 | Hai ngôn ngữ, điện thoại, không dữ liệu thật | Chuyển vi/en: mọi nhãn mới đổi; điện thoại: không cuộn ngang; rà tệp và ảnh: không tên, email thật, `tenantId`, địa chỉ app |

### 12.5 Còn mở

- **D8** (đường A hay B) chờ cuộc họp GĐ2; bộ dựng và đặc tả này chỉ để sẵn.
- Tên cột thật của `CLB_GIA` và quyền sửa app (NC-01, NC-02): HỎI-IT. Công thức Power Fx trong bộ dựng (`02_app/`) vẫn của chế độ thường, chưa viết lại cho màn FA.
- Dòng `DRAFT` còn sót sau hạn: bộ chuyển đổi bỏ qua (em coi như không đăng ký, theo V§8.6 thành CLB Tự do); có nên giữ làm mặc định hay không là câu hỏi cho Truong.
