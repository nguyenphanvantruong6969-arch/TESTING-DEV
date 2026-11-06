# T4M. Hướng dẫn thử trong môi trường thử (GĐ3)

Mã việc: **T4M-NC**, giai đoạn GĐ3 của `T4M_KE_HOACH_NGHIEN_CUU.md` (prompt P3, đã sửa theo bàn giao). Soạn **05/11/2026**.
Tài liệu vận hành, không phải kết luận đề tài. **Chưa ai chạy hướng dẫn này**; mọi mục "TH" bên dưới là việc cần thử, chưa phải kết quả.

Nhãn bằng chứng (mục 4 của kế hoạch): **ĐXM** (đã mở trang gốc, xem `T4M_KET_QUA_TAI_LIEU.md`), **GĐ** (giả định, chưa kiểm), **HỎI-IT**, **TH** (việc cần thử; kết quả điền vào bảng ở mục 9).
**Thời gian trong tài liệu là ước lượng mô phỏng, chưa đo.** Cột "đo thật" để trống cho người thử điền.

---

## 0. Đọc trước

### 0.1 Hai người đọc, hai đường

| Người đọc | Khi nào | Làm gì |
|---|---|---|
| **Truong** (mục 1 đến 9) | Chỉ khi IT cấp được môi trường thử (NC-02) | Tự dựng list giả, màn hình, flow; chụp ảnh; điền bảng mục 9 |
| **IT** (mục 10, **một trang**) | Dự phòng B của kế hoạch: Truong không có quyền tạo app/flow | IT tự làm bản rút gọn, gửi lại tệp xuất ẩn danh, ảnh chụp và bảng pass/fail |

Nếu chưa biết đường nào: gửi mục 10 cho IT trước. Đường đó rẻ nhất cho IT và vẫn trả lời được các câu NC-04, NC-09.

### 0.2 Quyết định đã chốt (đừng làm khác khi thử)

1. **Kho = SharePoint List** (NC-03, ĐXM). Không dùng Dataverse for Teams: không tạo môi trường mới từ 15/11/2026. Dataverse (loại đầy đủ) là Premium, không thử ở đây.
2. **Mô hình RỘNG**: một dòng cho mỗi (học sinh, ngày), cột `NV1`, `NV2`, `NV3` (NC-09, bàn giao). Lý do và mô hình dài bị loại: mục 2.
3. **V1 không ghi kết quả về từng dòng của list** (NC-13: hồ sơ "Low", 6.000 yêu cầu mỗi người mỗi 24 giờ, ĐXM). Kết quả ra bằng **Excel theo lớp chủ nhiệm** (`export_theo_lop` của kiosk), có thể gửi qua một flow (mục 8, tuỳ chọn).
4. Email phân biệt hoa thường ở kiosk (`student_id` so đúng từng ký tự). Bộ chuyển đổi **hạ chữ thường** email. Tệp giả cố ý có email viết hoa để thử việc này.
5. Chỉ **dữ liệu giả** (miền `example.test`). Không đụng app ECA thật, không ghi tên thật, email thật, `tenantId`, địa chỉ app vào kho mã hay ảnh chụp.

### 0.3 Việc cần có trước khi bắt đầu

- [ ] Một môi trường Power Platform không phải môi trường thật của trường (sandbox / managed developer / bản sao app), do IT cấp (NC-02). Developer Plan không còn tạo môi trường từ 15/11/2026 (ĐXM).
- [ ] Một site SharePoint thử mà Truong có quyền tạo list (HỎI-IT).
- [ ] Python 3 trên máy Truong (chỉ thư viện chuẩn) để sinh tệp giả và kiểm tệp xuất.

---

## 1. Sinh tệp giả

```
python du_lieu_test/sinh_xuat_lists_gia.py --ra lists_gia.csv                 # 1.500 em, 7.500 dòng
python du_lieu_test/sinh_xuat_lists_gia.py --so-hs 300 --seed 7 --ra nho.csv  # bản nhỏ, 1.500 dòng
```

Cùng `--seed` cho cùng từng byte. Tệp là UTF-8 **có BOM**, CRLF, dấu phẩy.

Bảng cột (đây là hợp đồng của bộ sinh; test `tests/test_sinh_xuat_lists_gia.py` kiểm khớp):

| Cột | Ý nghĩa | Kiểu cột nên tạo trong list | Ghi chú |
|---|---|---|---|
| `Email` | Email trường (giả), chữ hoa chữ thường lẫn lộn | Một dòng văn bản | **Không dùng kiểu Person**: kiểu Person chỉ uỷ quyền được Email và DisplayName (NC-04, ĐXM) và cách xuất chưa rõ (NC-09) |
| `HoTen` | Họ tên giả, có dấu tiếng Việt | Một dòng văn bản | Dùng để thử mã hoá |
| `CoSo` | `CS1` hoặc `CS2` | Lựa chọn (Choice) | Mỗi cơ sở xếp riêng; thử cách xuất cột Choice (NC-09) |
| `Khoi` | 6 đến 12 | Số | |
| `Lop` | Lớp chủ nhiệm giả, ví dụ `9A4` | Một dòng văn bản | Nguồn thật của cột này là HỎI-IT (NC-08) |
| `Thu` | `Thứ 2` đến `Thứ 6` | Lựa chọn (Choice) | Một dòng cho mỗi ngày |
| `NV1`, `NV2`, `NV3` | Mã CLB ưu tiên 1, 2, 3 của ngày đó; rỗng = chưa chọn | Một dòng văn bản | Không trùng nhau trong một dòng; không có ô trống chen trước ô có giá trị |
| `CapDo` | Cấp độ tiếng Nhật do trường chỉ định (khoảng 4% em); rỗng nếu không học | Lựa chọn | Là điều kiện tham gia, không phải ưu tiên |
| `Goi` | `3A` ở ba dòng `Thứ 2`, `Thứ 4`, `Thứ 5` của em đã đăng ký gói; rỗng nếu không | Lựa chọn | Dòng có `Goi` thì `NV1..NV3` rỗng (gói chiếm ngày đó) |
| `TrangThai` | `Đã khóa` hoặc `Đang mở` | Lựa chọn | App tắt chỉnh sửa khi `Đã khóa` |
| `Created` | Thời điểm tạo giả | (cột `Created` có sẵn của SharePoint) | **Không tự tạo cột tên này**; list đã có sẵn, nạp tệp thì bỏ cột này |

Quan hệ dòng: 1.500 em × 5 ngày = **7.500 dòng**. Ngày không chọn gì vẫn có dòng, với `NV1..NV3` rỗng (hợp lệ: buổi để trống, mục 3 của `T4M_KET_QUA_TAI_LIEU.md`).

**Điểm thi không nằm trong tệp này.** Câu lạc bộ có thi tuyển xếp theo Tầng 1 (điểm thi, rồi STB), câu lạc bộ không thi xếp theo Tầng 2 (STB). Bộ sinh này chỉ giả lập phần đăng ký nguyện vọng và gói; **điểm thi và danh sách CLB mỗi em chọn thi (tối đa 5 mỗi ngày) đến từ một tệp xuất bài thi riêng** (việc khác, prompt P5, không thuộc hướng dẫn này). Bộ chuyển đổi sau này sẽ ghép hai nguồn theo email đã hạ chữ thường.

Tệp xuất thật từ Lists sẽ có thêm các cột hệ thống (`ID`, `Title`, `Modified`, …) và thứ tự cột có thể khác. Bộ chuyển đổi phải đọc **theo tên cột** và bỏ qua cột thừa.

**Bảng CLB và gói đi kèm (tạo tay, nhỏ):**
- List `CLB_GIA` (cột `Thu`, `ClubId`, `TenCLB`, `ChiTieu`): ít nhất 3 CLB mỗi ngày là đủ thử giao diện; mã theo mẫu `T2-CLB01`. Đủ 6 đến 9 CLB mỗi ngày nếu muốn khớp tệp giả.
- List `GOI_GIA` (cột `MaGoi`, `Ngay1..Ngay3`, `CapDo`, `ChiTieu`): một dòng ví dụ `3A` | `Thứ 2` | `Thứ 4` | `Thứ 5` | `N5-A` | 25.

---

## 2. Mô hình dữ liệu: rộng (chọn) và dài (loại)

| | **Rộng (chọn)** | Dài (loại) |
|---|---|---|
| Một dòng là | (em, ngày) với `NV1..NV3` | (em, ngày, hạng) với `ClubId`, `Hang` |
| Số dòng 1.500 em, 5 ngày, 3 nguyện vọng | 7.500 | 22.500 |
| Trần xuất CSV của Lists | 30.000 dòng (NC-09, ĐXM): dư khoảng 4 lần | Dư khoảng 1,3 lần |
| Trần phân trang của flow hồ sơ Low | 5.000 (NC-13, ĐXM): vẫn phải lọc theo ngày | Phải lọc theo ngày **và** chia nhỏ hơn |
| Số lần ghi khi một em bấm Gửi | 5 (một lần mỗi ngày) | Tới 15 |
| Chặn trùng CLB trong một ngày | Làm trong app và kiểm lại ở bộ chuyển đổi | Làm được bằng chỉ mục duy nhất trên cột ghép (GĐ) |

**Lý do loại mô hình dài:** sát trần xuất CSV, nhiều lần ghi hơn trên một thao tác của học sinh, và vượt trần phân trang của flow nhanh hơn. **Cái giá của mô hình rộng:** số nguyện vọng cố định bằng số cột (ở đây 3; kiosk cho tới 10 mỗi buổi, `TRAN_NGUYEN_VONG_MOI_BUOI`); nếu trường tăng lên thì thêm cột `NV4`… và cập nhật bộ sinh; và kho không tự chặn trùng nên phải có hai lớp chặn (app và bộ chuyển đổi).

---

## 3. Dựng kho thử

**Bước 3.1. Tạo list `ECA_GIA`** (site SharePoint thử): tạo list trống, thêm cột theo bảng ở mục 1. Cột `Title` mặc định: đặt giá trị `Email|Thu` khi nạp (giá trị giả).
- Pass: list có đủ cột, kiểu đúng. Fail: thiếu quyền tạo list (ghi rõ thông báo, chụp ảnh).
- Ước lượng mô phỏng: 20 phút.

**Bước 3.2. Nạp dữ liệu giả.** Bắt đầu với `nho.csv` (1.500 dòng), sau đó `lists_gia.csv` (7.500 dòng). Cách nạp: tạo list từ CSV/Excel của Microsoft Lists, hoặc dán hàng loạt vào chế độ "Chỉnh sửa nhanh" (GĐ: chưa đọc trang hướng dẫn nạp; ghi lại cách đã dùng). Nếu nạp một lần không được 7.500 dòng, chia theo ngày.
- Pass: đếm dòng trong list bằng đúng số dòng tệp. Fail: ghi số dòng nạp được và thông báo lỗi.
- Ước lượng mô phỏng: 20 đến 40 phút.

**Bước 3.3. Đặt chỉ mục cho `Email` và `Thu`** (cài đặt list > chỉ mục cột). Mục đích: lọc theo hai cột này không vướng ngưỡng xem list (GĐ: ngưỡng 5.000 mục của chế độ xem là kiến thức SharePoint chung, chưa mở trang gốc trong GĐ1 cho riêng ngưỡng này).
- Pass: tạo được chỉ mục, mở chế độ xem lọc `Thu = Thứ 2` không báo lỗi ngưỡng. Fail: ghi thông báo.

---

## 4. Thử xuất (NC-09) và kiểm tệp

**Bước 4.1. Xuất.** Trong list, bỏ chọn mọi mục rồi **Export > Export to CSV** (ĐXM: nút chỉ hiện khi không chọn mục nào; tối đa 30.000 dòng; tệp là bản chụp). Chụp ảnh nút và hộp thoại.
- Pass: tải được tệp. Fail: không thấy nút, hoặc bị chặn (HỎI-IT, ghi lý do).

**Bước 4.2. Kiểm bằng Python** (chỉ thư viện chuẩn; sửa tên tệp):

```python
import csv, collections
with open("xuat_that.csv", "rb") as f:
    tho = f.read()
print("BOM:", tho.startswith(b"\xef\xbb\xbf"))
dong = list(csv.DictReader(tho.decode("utf-8-sig").splitlines(), restval=""))
print("so dong:", len(dong), "| cot:", list(dong[0].keys()))
print("dau tieng Viet:", any("Thứ" in (d.get("Thu") or "") for d in dong))
em = collections.defaultdict(set)
for d in dong:
    em[d["Email"].lower()].add(d["Email"])
print("so em:", len(em), "| email viet hoa:", sum(1 for v in em.values() if any(e != e.lower() for e in v)))
print("CapDo co gia tri:", sum(1 for d in dong if d.get("CapDo")), "| Goi co gia tri:", sum(1 for d in dong if d.get("Goi")))
```

Điền kết quả vào bảng mục 9. Câu hỏi cần trả lời bằng tệp thật, vì tài liệu **không ghi** (NC-09, ĐXM): (a) mã hoá có phải UTF-8 không; (b) cột Choice ra thành chữ thường hay có hậu tố; (c) tên cột trong tệp là tên hiển thị hay tên nội bộ (ví dụ có `_x0020_` không); (d) dòng tiêu đề có thêm cột hệ thống không.
- Pass: số dòng khớp, tiếng Việt đúng, `Thu`/`CoSo` ra chữ đọc được. Fail: chữ vỡ dấu hoặc cột Choice ra dạng khó đọc: ghi vài dòng đầu (đã là dữ liệu giả).
- Ước lượng mô phỏng: 10 phút.

**Bước 4.3 (tuỳ chọn). So tệp xuất với tệp sinh.** Nạp xong 7.500 dòng thì tệp xuất phải có 7.500 dòng dữ liệu (không tính tiêu đề). Chênh lệch: ghi lại.

---

## 5. Màn hình Top 3 mỗi ngày (NC-05)

**Việc cần thử:** em đăng nhập, thấy 5 ngày, mỗi ngày chọn tối đa 3 CLB không trùng, ngày để trống hợp lệ, bấm Gửi ghi đủ.
**Dùng app thử** (tạo mới trong môi trường thử), nguồn dữ liệu `ECA_GIA` và `CLB_GIA` (SharePoint, connector **chuẩn**). Công thức dưới đây là **GĐ**: chưa thử; chỉ `=` trên cột chữ và `Filter`/`LookUp` là đã có nguồn uỷ quyền (NC-04, ĐXM).

**Bước 5.1. Lấy các dòng của chính em.** Thư viện (Gallery), `Items`:
`Filter(ECA_GIA, Email = User().Email)` (uỷ quyền được). Kiểm: thanh thông báo uỷ quyền không hiện cảnh báo; **đặt giới hạn dòng dữ liệu = 1 trong Settings khi thử** để lộ lỗi uỷ quyền (khuyến nghị trong tài liệu, ĐXM).
- Pass: em có email viết hoa trong dữ liệu giả vẫn thấy đủ 5 dòng. Fail (rất có thể xảy ra): so sánh chữ có phân biệt hoa thường làm em không thấy dòng nào: ghi lại, đề xuất chuẩn hoá chữ thường ở dữ liệu nạp (HỎI: cách so sánh của kết nối SharePoint, GĐ).

**Bước 5.2. Ba ô thả xuống mỗi ngày.** `Items` của ô `NV1`: `Filter(CLB_GIA, Thu = ThisItem.Thu)`; ô `NV2`: bỏ CLB đang chọn ở ô `NV1`, ví dụ `Filter(CLB_GIA, Thu = ThisItem.Thu, ClubId <> DropNV1.Selected.ClubId)`; ô `NV3`: bỏ cả hai. `CLB_GIA` nhỏ (dưới 500 dòng) nên `<>` không đi qua giới hạn uỷ quyền (GĐ).
- Pass: không chọn trùng được; ô `NV2` không hiện CLB đã chọn ở `NV1`; để cả ba ô trống vẫn Gửi được. Fail: ghi tình huống chọn trùng lọt qua.
- Chặn ô trống chen giữa: `NV2` chỉ bật khi `NV1` có giá trị (`DisplayMode`), tương tự `NV3`. Pass/fail như trên.

**Bước 5.3. Gửi, ghi và báo lỗi.** Nút Gửi, `OnSelect` (GĐ):

```
IfError(
    ForAll(GalleryNgay.AllItems As Dong,
        Patch(ECA_GIA, LookUp(ECA_GIA, ID = Dong.ID),
            {NV1: Dong.NV1.Selected.ClubId, NV2: Dong.NV2.Selected.ClubId, NV3: Dong.NV3.Selected.ClubId})),
    Notify("Chưa lưu được: " & FirstError.Message, NotificationType.Error),
    Notify("Đã lưu", NotificationType.Success)
)
```

Tên điều khiển ở trên (`GalleryNgay`, `Dong`) là ví dụ; thay bằng tên trong app. Mỗi `Patch` là một yêu cầu: 5 ngày = 5 yêu cầu, rất xa dưới 6.000 mỗi ngày (NC-13).
- **Lưu nguyên tử** (NC-05): SharePoint không có giao dịch. Thử cố ý làm một `Patch` hỏng (tắt mạng giữa chừng, hoặc ghi vào cột chỉ đọc ở dòng thứ 3) và ghi lại: có ngày nào đã lưu, ngày nào chưa; thông báo lỗi có chỉ đúng ngày không. Pass: thông báo chỉ ra được ngày chưa lưu, bấm Gửi lại thì xong. Fail: lưu nửa chừng mà không báo.
- **Khoá:** khi `TrangThai = "Đã khóa"` mọi ô tắt (`DisplayMode.Disabled`). Pass: dòng giả có `Đang mở` sửa được, `Đã khóa` không sửa được.
- **Điện thoại:** mở app trên điện thoại, chụp ảnh. Pass: thao tác được bằng ngón tay. Fail: ghi lại ô nào khó bấm.
- **Hai ngôn ngữ** (app ECA thật có hai ngôn ngữ): ngoài phạm vi thử; chỉ ghi nếu có sẵn mẫu.
- Ước lượng mô phỏng cho cả mục 5: 3 đến 5 giờ cho người chưa quen Power Apps (**ước lượng, chưa đo**).

**Việc cần chụp:** màn hình 5 ngày; ô thả xuống `NV2` sau khi chọn `NV1`; thông báo lỗi khi cố ý làm hỏng; thông báo uỷ quyền (nếu có).

---

## 6. Màn hình gói tiếng Nhật (NC-06)

**Việc cần thử:** chỉ em có `CapDo` mới thấy gói; một lần đăng ký gói chiếm ba ngày; mỗi em tối đa một gói.
Đây là phần thử **giao diện**. Thuật toán xếp hai pha cho gói **chưa có trong kiosk**: cần mã mục riêng (Sổ nhập mỗi CLB đúng một Buổi, `T4M_KET_QUA_TAI_LIEU.md` mục 3).

**Bước 6.1. Hiện gói đúng cấp độ.** Thư viện gói: `Filter(GOI_GIA, CapDo = LookUp(ECA_GIA, Email = User().Email && Thu = "Thứ 2").CapDo)` (GĐ). Lưu ý: `CapDo` của em đọc từ một dòng bất kỳ của em; nếu rỗng thì ẩn cả màn gói (`Visible`).
- Pass: em có `CapDo = N5-A` thấy gói `3A`; em không có `CapDo` không thấy màn gói. Fail: ghi lại.

**Bước 6.2. Chiếm ba ngày.** Nút Đăng ký gói, `OnSelect` (GĐ): `Patch` ba dòng `Thứ 2`, `Thứ 4`, `Thứ 5` của em: `Goi: "3A"`, `NV1`, `NV2`, `NV3` bằng `Blank()`.
- Pass: ba dòng có `Goi = 3A` và NV rỗng; trên màn Top 3 ba ngày đó **khoá** (ô tắt, hiện chữ "Gói 3A"). Fail: ghi lại.
- Trước khi đăng ký, nếu ba ngày đang có NV thì app phải hỏi xác nhận xoá (kiểm lời nhắc). Pass/fail như trên.

**Bước 6.3. Tối đa một gói.** Nút Đăng ký gói chỉ bật khi em chưa có dòng nào `Goi` khác rỗng: `IsBlank(LookUp(ECA_GIA, Email = User().Email && Goi = "3A"))` (GĐ). Với một gói duy nhất trong thử nghiệm thì kiểm bằng cách bấm hai lần.
- Pass: lần hai bị chặn. Fail: ghi lại.
- Ước lượng mô phỏng: 1 đến 2 giờ (**ước lượng, chưa đo**).

---

## 7. Flow xuất CSV vào thư viện (NC-09, tuỳ chọn)

Chỉ làm sau khi bước 4 chạy tốt. Nếu nút Export của Lists đã đủ, **bỏ qua mục này** (đường thủ công 2 bước).

| Thành phần | Loại | Ghi chú |
|---|---|---|
| Kích hoạt thủ công (Manually trigger a flow) | Chuẩn | |
| SharePoint "Get items" | Chuẩn | |
| "Create CSV table" | Thao tác dữ liệu (GĐ: chuẩn) | |
| SharePoint "Create file" | Chuẩn | |
| ~~HTTP~~ | **Premium** | **Không dùng.** Thay thế chuẩn: các thao tác SharePoint ở trên |

**Bước 7.1. Lọc theo ngày.** Hồ sơ "Low" giới hạn phân trang 5.000 mục (NC-13, ĐXM) nên 7.500 dòng **không** lấy một lần được. Làm năm lần "Get items", mỗi lần có `Filter Query`: `Thu eq 'Thứ 2'` (1.500 dòng, dưới 5.000), … và một tệp cho mỗi ngày, hoặc gộp các bảng bằng "Select" (GĐ). Bật phân trang với ngưỡng 2.000 cho mỗi lần.
- Pass: năm lần đều ra đủ 1.500 dòng. Fail: số dòng ra là 100 (mặc định không bật phân trang): bật phân trang. Nếu vẫn thiếu: ghi số dòng.

**Bước 7.2. Tạo tệp CSV.** "Create CSV table" từ kết quả, rồi "Create file" vào thư viện `XUAT_GIA` (tên `lists_<thu>.csv`).
- Pass: tải tệp về, chạy đoạn Python ở 4.2 (đọc tệp vừa tải) và thấy tiếng Việt đúng, số dòng đúng. Ghi **có BOM hay không** (GĐ: chưa biết "Create file" ghi BOM không; kiosk đọc được cả hai vì bộ chuyển đổi đọc `utf-8-sig`).
- Fail: chữ vỡ dấu (ghi mã hoá thấy được). Phương án: dùng đường xuất thủ công.
- Ước lượng mô phỏng: 1 đến 2 giờ; **thời gian chạy flow: chưa đo** (điền ở mục 9).

---

## 8. Trả kết quả theo lớp (NC-11, NC-12, NC-13)

**Cách làm V1:** kiosk (máy IT) chạy xếp, xuất bằng `export_theo_lop` ra một tệp Excel cho mỗi lớp chủ nhiệm; **không** ghi từng dòng về list (6.000 yêu cầu mỗi người mỗi ngày, NC-13, ĐXM: 1.500 em × 5 ngày chạm khoảng 7.500 lần cập nhật).

**Flow gửi tệp (tuỳ chọn, một flow).**

| Thành phần | Loại | Ghi chú |
|---|---|---|
| Kích hoạt thủ công | Chuẩn | |
| SharePoint "Get files" (thư viện `KET_QUA_GIA`) | Chuẩn | Mỗi lớp một tệp |
| SharePoint "Get items" (list `GVCN_GIA`: `Lop`, `Email`) | Chuẩn | List giả: lớp và email giả của giáo viên chủ nhiệm |
| Outlook "Send an email (V2)" kèm tệp | Chuẩn | 300 lệnh mỗi 60 giây (ĐXM): đủ cho vài chục lớp |
| Teams "Post message in a chat or channel" | Chuẩn | 100 lệnh mỗi 60 giây (ĐXM); gửi **liên kết** tệp, không đính kèm (GĐ) |

**Bước 8.1.** Tạo `KET_QUA_GIA` với 3 tệp Excel giả (tên lớp giả, không có tên người thật), list `GVCN_GIA` với 3 dòng địa chỉ email **của chính Truong hoặc của IT** (không gửi tới người thật khác).
**Bước 8.2.** Chạy flow. Pass: 3 email/tin đến đúng người, đúng tệp theo lớp. Fail: ghi lỗi (thường gặp: tệp bị khoá, quyền, DLP chặn connector, NC-14).
**Bước 8.3.** Flow thuộc về **tài khoản dịch vụ của IT**, không phải tài khoản cá nhân: flow chủ rời tổ chức thì về hồ sơ Low; flow 90 ngày không chạy có thể bị tắt (NC-13, ĐXM). Chỉ ghi vào bảng; không thử trong môi trường thử.
**Không làm ở V1 và không thử:** flow đọc kết quả xếp và `Update item` từng dòng. Nếu muốn có số đo cho đề tài: chỉ đo 100 dòng trên list giả, ghi thời gian là "TH" kèm ngày.
- Ước lượng mô phỏng: 1 đến 2 giờ (**chưa đo**).

---

## 9. Bảng kết quả (điền khi chạy thật)

Mỗi dòng: đánh dấu **Pass** hoặc **Fail**; nếu Fail thì ghi **lý do** ngắn (thông báo lỗi nguyên văn, không có dữ liệu thật). "Ước lượng" là con số mô phỏng ở trên; "đo thật" để Truong hoặc IT điền.

| Bước | Việc | NC | Pass | Fail | Lý do nếu Fail | Ảnh chụp | Ước lượng | Đo thật |
|---|---|---|---|---|---|---|---|---|
| 3.1 | Tạo `ECA_GIA` đủ cột | NC-04 | ☐ | ☐ | | thông báo quyền (nếu lỗi) | 20 phút | |
| 3.2 | Nạp 1.500 rồi 7.500 dòng | NC-04, 09 | ☐ | ☐ | | số dòng đếm được | 20 đến 40 phút | |
| 3.3 | Đặt chỉ mục `Email`, `Thu` | NC-04 | ☐ | ☐ | | | 5 phút | |
| 4.1 | Export to CSV được | NC-09 | ☐ | ☐ | | nút và hộp thoại | 5 phút | |
| 4.2 | Tệp xuất: số dòng, tiếng Việt, cột Choice, tên cột | NC-09 | ☐ | ☐ | | kết quả đoạn Python | 10 phút | |
| 5.1 | Chỉ thấy dòng của mình, kể cả email viết hoa | NC-04, 05 | ☐ | ☐ | | | 30 phút | |
| 5.2 | Không chọn trùng; ô trống hợp lệ | NC-05 | ☐ | ☐ | | màn 5 ngày, ô `NV2` | 1 đến 2 giờ | |
| 5.3 | Gửi lưu đủ 5 dòng; lỗi một ngày được báo | NC-05 | ☐ | ☐ | | thông báo lỗi | 1 đến 2 giờ | |
| 5.4 | Khoá khi `Đã khóa`; điện thoại | NC-05 | ☐ | ☐ | | ảnh điện thoại | 30 phút | |
| 5.5 | Hai ngôn ngữ: chuyển vi/en, mọi nhãn đổi, không chữ cứng sót (R10 của `T4M_DAC_TA_SUA_APP.md`) | NC-05 | ☐ | ☐ | | màn vi và en | 30 phút | |
| 5.6 | Khôi phục phiên bản: Restore + Publish trên bản thử, app chạy lại như cũ (R12) | NC-21 | ☐ | ☐ | | trang Versions | 20 phút | |
| 6.1 | Gói chỉ hiện đúng cấp độ | NC-06 | ☐ | ☐ | | | 30 phút | |
| 6.2 | Đăng ký gói chiếm 3 ngày, khoá 3 ô | NC-06 | ☐ | ☐ | | | 1 giờ | |
| 6.3 | Tối đa một gói | NC-06 | ☐ | ☐ | | | 15 phút | |
| 7.1 | Flow xuất: đủ dòng theo từng ngày | NC-09, 13 | ☐ | ☐ | | lịch sử chạy | 1 giờ | thời gian chạy: |
| 7.2 | Tệp từ flow đọc được bằng Python | NC-09 | ☐ | ☐ | | | 30 phút | BOM: có / không |
| 8.2 | Flow gửi 3 tệp theo lớp | NC-11, 12 | ☐ | ☐ | | email nhận được | 1 đến 2 giờ | thời gian chạy: |

Câu cần trả về kế hoạch sau khi điền: (1) có lấy đủ 7.500 dòng bằng đường thủ công không; (2) có cần lọc theo ngày cho flow không; (3) so sánh chữ hoa thường của `Email` trong app ra sao; (4) lưu 5 ngày có thể hỏng nửa chừng không; (5) mã hoá và dạng cột Choice của tệp xuất.

---

## 10. Bản một trang cho IT (dự phòng B)

> Dành cho bộ phận IT khi Truong không có quyền tạo app/flow. Mục đích: trả lời hai câu bằng tệp thật: (1) tệp xuất "Export to CSV" từ list của trường trông thế nào; (2) list 7.500 dòng có vận hành được không. **Toàn bộ dữ liệu là giả.** Mất khoảng 1 đến 2 giờ (ước lượng mô phỏng, chưa đo).

1. Trong site thử (không phải site thật), tạo list `ECA_GIA` với các cột: `Email` (văn bản), `HoTen` (văn bản), `CoSo` (lựa chọn), `Khoi` (số), `Lop` (văn bản), `Thu` (lựa chọn), `NV1`, `NV2`, `NV3` (văn bản), `CapDo`, `Goi`, `TrangThai` (lựa chọn).
2. Nạp tệp `lists_gia.csv` (Truong gửi kèm; 7.500 dòng giả, bỏ cột `Created`). Nếu không nạp được một lần: nạp `nho.csv` (1.500 dòng) và ghi lại giới hạn gặp phải.
3. Đặt chỉ mục cho `Email` và `Thu`.
4. Bỏ chọn mọi mục, **Export > Export to CSV**, lưu tệp. Ẩn danh không cần (dữ liệu đã giả). Gửi lại tệp này.
5. Chạy đoạn Python ở mục 4.2 (hoặc gửi tệp để Truong chạy). Ghi: có BOM không; số dòng; cột `Thu` và `CoSo` ra chữ gì.
6. (Nếu IT muốn) Trong cùng site, tạo flow thủ công: "Get items" có lọc `Thu eq 'Thứ 2'` với phân trang bật, rồi "Create CSV table" và "Create file". Ghi: ra bao nhiêu dòng; thời gian chạy.
7. (Nếu IT muốn) Flow gửi một email có đính kèm tệp Excel tới chính địa chỉ của IT. Ghi: thành công hay bị chặn (DLP).

**Điền và gửi lại:**

| # | Pass / Fail | Lý do nếu Fail | Ghi chú (không dữ liệu thật) |
|---|---|---|---|
| 1 Tạo list | | | |
| 2 Nạp 7.500 dòng | | | số dòng nạp được: |
| 3 Chỉ mục | | | |
| 4 Export to CSV | | | tệp đính kèm |
| 5 Kiểm tệp | | | BOM: có/không; số dòng: |
| 6 Flow xuất | | | thời gian chạy: |
| 7 Flow gửi email | | | |

Kèm: tệp xuất ở bước 4 và ảnh chụp hộp thoại Export. **Không gửi** địa chỉ app, `tenantId`, tên hay email thật.

---

## 11. Phụ thuộc Premium và phương án chuẩn

| Việc | Cần Premium? | Phương án chuẩn |
|---|---|---|
| SharePoint List làm kho, Power Apps canvas đọc/ghi | Không (connector chuẩn, ĐXM) | — |
| Dataverse (loại đầy đủ) | **Có** | SharePoint List |
| Dataverse for Teams | Không, nhưng **không tạo mới từ 15/11/2026** (ĐXM) | SharePoint List |
| Connector HTTP, "Send an HTTP request" của dịch vụ khác | **Có** | Thao tác SharePoint / Excel Online (Business) chuẩn |
| Connector tuỳ biến (custom connector) | **Có** | Không cần ở V1 |
| Excel Online (Business), Outlook, Teams, SharePoint | Không (ĐXM) | — |
| Chạy Office Scripts từ flow | Không Premium; giới hạn 1.600 lần mỗi người mỗi ngày (ĐXM) | Bộ chuyển đổi Python trên máy IT (NC-22) |
| Ghi kết quả từng dòng về list | Không Premium, nhưng vượt hạn mức hồ sơ Low (ĐXM) | Excel theo lớp (`export_theo_lop`) |

---

## 12. Sau khi thử

1. Điền mục 9, đưa kết quả cho phiên Opus chạy P2 (GĐ4); không sửa `T4_MO_HINH_HE_SINH_THAI.md`.
2. Mọi tệp xuất ra từ môi trường thử chỉ chứa dữ liệu giả; vẫn không commit ảnh chụp có địa chỉ site hay tên tài khoản.
3. Việc còn thiếu để V1 chạy được và cần **mã mục riêng** (chờ P2): bộ chuyển đổi Lists -> Sổ nhập (hạ chữ thường email, đổi `Thu` thành `thu_2`…, xoay `NV1..NV3` thành danh sách nguyện vọng); xếp hai pha cho gói tiếng Nhật.
