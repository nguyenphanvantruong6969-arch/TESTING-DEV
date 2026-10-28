# Hướng dẫn sử dụng — Phần mềm phân bổ câu lạc bộ (RB-DA Kiosk)

> Viết cho người **chưa từng mở phần mềm này**. Mỗi bước nói rõ: bấm vào đâu,
> sẽ thấy gì, và làm gì nếu không thấy như vậy.
>
> Tài liệu do AI soạn theo yêu cầu của học sinh, có ghi trong nhật ký AI.
> Đây là **tài liệu vận hành phần mềm**, không phải bài nghiên cứu.

---

## Mục lục

1. [Phần mềm này làm gì](#1-phần-mềm-này-làm-gì)
2. [Cần chuẩn bị gì](#2-cần-chuẩn-bị-gì)
3. [Mở phần mềm lần đầu](#3-mở-phần-mềm-lần-đầu)
4. [Nhìn quanh màn hình](#4-nhìn-quanh-màn-hình)
5. [Sổ nhập CLB — từng cột nghĩa là gì](#5-sổ-nhập-clb--từng-cột-nghĩa-là-gì)
6. [Chạy trọn quy trình — 5 bước](#6-chạy-trọn-quy-trình--5-bước)
7. [Đọc bảng kết quả](#7-đọc-bảng-kết-quả)
8. [Nhập tay tại chỗ](#8-nhập-tay-tại-chỗ)
9. [Làm lại từ đầu, và chuyện sao lưu](#9-làm-lại-từ-đầu-và-chuyện-sao-lưu)
10. [Bảng tra cảnh báo](#10-bảng-tra-cảnh-báo)
11. [Sự cố hay gặp](#11-sự-cố-hay-gặp)
12. [Thuật toán làm gì](#12-thuật-toán-làm-gì)
13. [Giới hạn đã biết](#13-giới-hạn-đã-biết)
14. [Điểm quyết tâm (tuỳ chọn)](#14-điểm-quyết-tâm-tuỳ-chọn)

---

## 1. Phần mềm này làm gì

Trường có nhiều câu lạc bộ, mỗi CLB có số chỗ giới hạn. Học sinh xếp hạng
nguyện vọng của mình. Phần mềm quyết định **ai vào CLB nào**.

Nó không quyết định bừa. Nó chạy một thuật toán có tên **RB-DA**, bảo đảm hai
điều: không có cặp học sinh–CLB nào mà **cả hai** đều muốn đổi cho nhau (gọi là
*kết quả ổn định*), và một số chỗ được **dành riêng** cho học sinh thuộc diện ưu
tiên do trường tự đặt.

Phần mềm chạy **hoàn toàn ngoại tuyến** trên một máy tính Windows. Không gửi dữ
liệu đi đâu, không cần Internet.

---

## 2. Cần chuẩn bị gì

| Cần | Ghi chú |
|---|---|
| Máy tính **Windows 10 hoặc 11** | Không cần cài đặt gì thêm |
| Thư mục phần mềm, trong đó có `PhanBoCauLacBo.exe` | Giải nén từ tệp `.zip` |
| **Một Sổ nhập CLB** (tệp Excel) | Xem mục 5. Có sẵn bộ ví dụ để thử |
| Khoảng 15 phút cho lần đầu | |

**Bộ ví dụ để tập:** thư mục `du_lieu_test/vi_du_huong_dan/` — 10 học sinh, 4
CLB. Cả hướng dẫn này dùng đúng bộ đó, nên bạn làm theo tới đâu là đối chiếu
được tới đó.

> ⚠️ Mọi bộ dữ liệu đi kèm phần mềm đều là **DỮ LIỆU MÔ PHỎNG** — tên và điểm
> đều là bịa. Không được trình bày như số liệu khảo sát thật.

---

## 3. Mở phần mềm lần đầu

**Bước 1.** Chuột phải vào tệp **`.zip`** *(làm trước khi giải nén)* → **Properties**
→ cuối tab *General*, nếu có ô **Unblock** thì tích vào → **OK**.

Bỏ qua bước này thường vẫn chạy được — phần mềm tự xử lý. Nhưng làm thì chắc hơn.

**Bước 2.** Giải nén vào một thư mục, rồi bấm đúp `PhanBoCauLacBo.exe`.

**Bước 3.** Windows có thể hiện bảng xanh **"Windows protected your PC"**.

> Đây **không phải lỗi phần mềm**. Mọi ứng dụng không mua chứng chỉ ký số
> thương mại đều bị cảnh báo như vậy.

Bấm **More info** → **Run anyway**. Windows nhớ lựa chọn, nên chỉ hiện lần đầu
trên mỗi máy.

**Bước 4.** Cửa sổ phần mềm mở ra. Nhìn **góc dưới bên trái**: dòng cuối phải
ghi **"Cửa sổ ứng dụng riêng"**. Nếu ghi **"Chế độ dự phòng (trình duyệt)"** màu
vàng thì xem [mục 11](#11-sự-cố-hay-gặp).

---

## 4. Nhìn quanh màn hình

Bên trái là **thanh bên**, luôn hiện. Nó cho biết cơ sở dữ liệu đang kết nối,
lần chạy gần nhất là khi nào, và phần mềm đang vẽ cửa sổ bằng đường nào.

Trên cùng là **năm thẻ**:

| Thẻ | Dùng để |
|---|---|
| **01 · Vận hành sắp xếp** | Nạp tệp, xem cảnh báo, chạy sắp xếp, xuất kết quả |
| **02 · Kết quả** | Xem ai vào CLB nào, mỗi CLB đầy đến đâu |
| **03 · Nhập dự phòng** | Gõ tay cho em không nộp được qua biểu mẫu |
| **04 · Quản lý CLB & dự trữ** | Thêm/sửa CLB, gán diện ưu tiên, xoá dữ liệu |
| **05 · Chấm điểm (mù)** | Giáo viên nhập điểm vòng thi |

**"Chấm điểm mù" nghĩa là gì:** màn hình chấm điểm **chỉ hiện mã và họ tên**. Nó
không hiện số bốc thăm, cũng không hiện em đó xếp CLB này là nguyện vọng thứ
mấy. Người chấm không biết cho điểm này thì ai được lợi.

---

## 5. Sổ nhập CLB — từng cột nghĩa là gì

Mọi dữ liệu nằm trong **một tệp Excel**: Sổ nhập CLB. Lấy sổ bằng nút **Tải sổ
nhập mẫu** ở thẻ **01 · Vận hành sắp xếp** — phần mềm đã có CLB thì sổ điền sẵn
danh sách CLB. Sổ có hai trang để điền và một trang **Hướng dẫn**. Hướng dẫn
một trang đầy đủ: `mau_csv/HUONG_DAN_SO_NHAP.md`.

Bộ ví dụ của hướng dẫn này là `du_lieu_test/vi_du_huong_dan/SO_NHAP_VIDU.xlsx`.

### Trang `1. CLB` — mỗi CLB một dòng

| Cột | Bắt buộc | Nghĩa |
|---|---|---|
| Tên CLB | ✔ | Tên hiển thị, có dấu thoải mái. **Không được trùng** — trang 2 chọn CLB theo tên này |
| Buổi | | **Buổi sinh hoạt trong tuần**, chọn Thứ 2 … Chủ nhật. Xem mục 5b |
| Chỉ tiêu | ✔ | **Tổng** số chỗ |
| Suất ưu tiên | | Trong tổng số đó, bao nhiêu chỗ **dành riêng** cho Nhóm ưu tiên |
| Nhóm ưu tiên | | Nhãn diện ưu tiên. Bỏ trống nếu CLB không có suất dự trữ |
| Mã CLB | | Bỏ trống: phần mềm tự tạo từ tên |

Bộ ví dụ:

| Tên CLB | Chỉ tiêu | Suất ưu tiên | Nhóm ưu tiên |
|---|---|---|---|
| CLB Bóng rổ | 3 | 1 | chinh_sach |
| CLB Tin học | 2 | | |
| CLB Mỹ thuật | 2 | | |
| CLB Nấu ăn | 3 | | |

Đọc dòng đầu: Bóng rổ có **3 chỗ**, trong đó **1 chỗ** dành cho học sinh mang
nhãn `chinh_sach`. Hai chỗ còn lại cạnh tranh bình thường.

> **Suất ưu tiên nằm TRONG Chỉ tiêu, không cộng thêm.** Ghi 3 và 1 nghĩa là 3
> chỗ tất cả, không phải 4.

### Trang `2. Học sinh` — mỗi học sinh một dòng

| Cột | Nghĩa |
|---|---|
| Mã HS | Mã học sinh. Bắt buộc, không được trùng |
| Họ tên | Họ tên |
| Nhóm ưu tiên | Nhãn diện ưu tiên của em này. Bỏ trống nếu không thuộc diện nào |
| Nguyện vọng 1 (ô gộp, hàng 1) | Nguyện vọng **mong muốn nhất**. Dưới ô gộp có cột **CLB**: chọn tên CLB trong danh sách thả xuống |
| Nguyện vọng 2, 3, … | Nguyện vọng tiếp theo, cùng cấu trúc |
| Điểm thi (hàng 2, cùng nhóm) | Điểm thi của CLB **ngay bên trái**. Trống = không thi. Chữ `thi` = đã thi, chấm sau |

Sheet này có **hai hàng tiêu đề** (từ A13.4): hàng 1 là các ô gộp "Nguyện vọng k", hàng 2 là tên cột trong từng
nhóm (CLB, Điểm thi, và Điểm quyết tâm khi bật). Cột đầu gộp dọc hai hàng; dữ liệu bắt đầu từ **hàng 3**. Chèn hay
xoá cột trong một nhóm thì phần mềm báo lỗi "cột lệch nhóm" và không nạp gì. Sổ cũ chỉ có một hàng tiêu đề vẫn nạp được.

Bộ ví dụ (3 dòng đầu và dòng cuối; mỗi nhóm có hai cột CLB và Điểm thi):

| Mã HS | Họ tên | Nhóm ưu tiên | NV 1: CLB | NV 1: Điểm thi | NV 2: CLB | NV 2: Điểm thi |
|---|---|---|---|---|---|---|
| HS01 | Nguyễn Văn An | | CLB Bóng rổ | 9 | CLB Tin học | 7,5 |
| HS02 | Trần Thị Bình | | CLB Bóng rổ | 8,5 | CLB Mỹ thuật | 8 |
| HS04 | Phạm Thu Dung | chinh_sach | CLB Bóng rổ | 6 | CLB Mỹ thuật | 6,5 |
| HS10 | Dương Bá Minh | | CLB Bóng rổ | 7 | *(để trống)* | |

Có sẵn điểm trong sổ thì **không phải gõ tay** ở thẻ Chấm điểm.

Ô trống là bình thường. Nhưng lưu ý HS10: em chỉ xếp **một** nguyện vọng, vào
đúng CLB đông nhất. Em này sẽ không có đường lui — xem [mục 7](#7-đọc-bảng-kết-quả).

### Ba quy tắc dễ sai nhất

1. **Chọn tên CLB trong danh sách thả xuống, đừng gõ tay.** Gõ sai một chữ thì
   phần mềm không nạp gì cả và chỉ đúng ô sai.
2. **Điểm phải nằm ngay cạnh CLB của nó.** Điểm 2 là điểm của CLB ở NV2. Vì thế
   không thể ghi điểm cho một CLB em không xếp nguyện vọng — mà lượt thi đó vốn
   bỏ phí: dù điểm cao cũng không vào được.
3. **Mã học sinh phân biệt hoa/thường.** `HS01` và `hs01` là **hai** người khác
   nhau. Phần mềm cảnh báo khi thấy hai cách viết chỉ khác hoa/thường.

---

## 5b. Nếu trường tổ chức CLB vào NHIỀU buổi trong tuần

Bỏ qua mục này nếu trường chỉ tổ chức một buổi — khi đó để trống cột Buổi, và
màn hình cũng không hiện thêm thứ gì.

### Khai buổi cho từng CLB

Chọn buổi ở cột **Buổi** của trang `1. CLB`. Quy tắc duy nhất: **hai CLB cùng
buổi là trùng giờ**, nên một em chỉ vào được một trong hai.

| Tên CLB | Buổi | Chỉ tiêu |
|---|---|---|
| CLB Bóng đá | Thứ 3 | 20 |
| CLB Tin học | Thứ 5 | 16 |

Nếu trường tổ chức hai tiết khác nhau trong cùng một ngày thì gõ tay tên buổi
như `thu_3_tiet_9` và `thu_3_tiet_10` — phần mềm giữ nguyên tên buổi lạ.

> ⚠️ **Khai buổi cho một số CLB rồi bỏ trống số còn lại là hỏng.** Những CLB
> bỏ trống sẽ bị gom vào một buổi chung, tức là bị coi là trùng giờ với nhau.
> Phần mềm có kêu cảnh báo, nhưng tốt nhất là khai đủ hoặc bỏ trống tất cả.

### Nguyện vọng: vẫn một danh sách

Trang `2. Học sinh` **không đổi** khi trường có nhiều buổi: các nhóm Nguyện vọng 1, 2, … là một
danh sách chung. Phần mềm tự chia theo buổi của từng CLB, giữ đúng thứ tự em
đã xếp trong mỗi buổi.

| Mã HS | Nguyện vọng 1 | Nguyện vọng 2 | Nguyện vọng 3 |
|---|---|---|---|
| HS001 | CLB Bóng đá *(Thứ 3)* | CLB Cờ vua *(Thứ 3)* | CLB Tin học *(Thứ 5)* |

Phần mềm hiểu: Thứ 3 em muốn Bóng đá rồi Cờ vua; Thứ 5 em muốn Tin học. Em
**bận buổi nào thì không chọn CLB nào của buổi đó** — không có cột riêng để
khai lịch bận.

Mỗi buổi tối đa 10 nguyện vọng và 5 CLB dự thi.

### Xem trước tải từng buổi TRƯỚC khi chạy

Thẻ **Quản lý CLB & dự trữ** có bảng **Tải theo buổi**: mỗi buổi có bao nhiêu
chỗ, bao nhiêu em muốn, và tỉ lệ chọi.

Buổi nào chọi cao mà buổi khác còn trống thì **dời một CLB sang buổi vắng** —
sửa được trước khi chạy, thay vì chạy xong mới đi giải thích vì sao nhiều em
trượt.

*Tỉ lệ chọi đếm theo **số học sinh**, không phải số lượt nguyện vọng, vì mỗi
em chỉ lấy được một chỗ trong một buổi.*

### Bốc thăm qua các buổi — không phải chọn nữa

Nhiều buổi thì phần mềm **xáo lại thứ tự ở mỗi buổi**. Không có gì để chọn:
đây là cách duy nhất, và nó được chọn bằng phép đo chứ không bằng cảm tính
(**TN7** trong `docs/NGHIEN_CUU_TOI_UU.md`).

Lý do bằng một câu: nếu dùng chung một bộ số cho cả tuần thì em rút phải số
xấu sẽ đứng cuối ở **mọi** buổi — may rủi cộng dồn lên đúng một em. Xáo lại
mỗi buổi thì may rủi san đều. Đo trên dữ liệu mà bốc thăm quyết định, cách này
cứu **1,2 tới 79,0 em trên 200**, tuỳ mức chật.

> **Trường chỉ tổ chức một buổi thì không đổi gì.** Một buổi thì không có gì
> để san đều, nên phần mềm dùng thẳng bộ số đã khoá — kết quả y hệt các bản
> trước.
>
> **Trường đã chạy nhiều buổi bằng bản cũ** (bản còn cho chọn cách bốc thăm)
> thì lần chạy tới **sẽ ra kết quả khác**. Bộ số đã khoá không đổi, nhưng thứ
> tự trong từng buổi thì đổi. Đã công bố kết quả rồi thì cân nhắc trước khi
> chạy lại.

### Chỉ xếp một buổi, hoặc một dải buổi

Thẻ **Vận hành sắp xếp**, khối **Buổi sẽ xếp** ngay trên các bước xử lý. Mặc
định chọn hết — bấm Chạy mà không để ý khối này thì kết quả y như trước.

Hai cách chọn, cùng sửa một tập:

| Cách | Dùng khi |
|---|---|
| **Bấm vào từng buổi** để bật/tắt | Chỉ một buổi, hoặc vài buổi rời rạc |
| **Từ … đến …** | Một dải liên tiếp, ví dụ thứ Hai đến thứ Năm |

> **Buổi không chọn GIỮ NGUYÊN kết quả của lần xếp trước.** Đây là điểm chính
> của tính năng: một câu lạc bộ thứ Năm đổi sức chứa hoặc bị huỷ thì xếp lại
> riêng thứ Năm, các ngày đã in ra dán bảng không bị đụng tới. Dòng chữ dưới
> các nút luôn nói rõ buổi nào đang được giữ.
>
> Một ngoại lệ, và là ngoại lệ đúng: **câu lạc bộ nào vừa được dời sang buổi
> khác thì kết quả cũ của nó ở buổi cũ bị xoá**, kể cả khi buổi cũ không được
> chọn. Dòng đó mô tả một việc không còn xảy ra được — em ấy sinh hoạt câu lạc
> bộ đó vào một ngày mà câu lạc bộ đó không còn họp. Giữ lại thì bảng lấp đầy
> đếm thừa và có em hiện ra ở hai ngày cùng lúc.

**Chạy riêng một buổi cho đúng kết quả của buổi đó khi chạy cả tuần.** Không
có chuyện xếp lần lượt từng ngày lại ra kết quả khác xếp cả tuần một lần —
phần mềm có test canh điều này trên cả năm buổi.

> ⚠️ **Không vẽ lại số bốc thăm khi chỉ xếp một phần.** Phần mềm chặn hẳn, kèm
> lời giải thích. Vẽ lại là đổi thứ tự ưu tiên của **mọi** buổi, kể cả những
> buổi đang giữ kết quả cũ — kết quả cũ ấy lập tức không còn giải thích được
> bằng bộ số mới. Muốn vẽ lại thì chọn tất cả các buổi.

> 🔒 **Hạt giống khoá cùng bộ số bốc thăm.** Hạt giống chính là thứ sinh ra
> thứ tự ưu tiên của từng buổi, nên đổi nó cũng là đổi thứ tự của **mọi**
> buổi — cùng tác dụng như vẽ lại số bốc thăm. Vì thế sau lần chạy đầu, ô hạt
> giống **chỉ đọc**: nó hiện đúng hạt giống đã khoá, kèm một dòng giải thích
> ngay dưới dòng trạng thái khoá. Muốn dùng hạt giống khác thì bấm **Vẽ lại số
> bốc thăm…** (ô sẽ mở ra), nhập hạt giống mới, rồi chạy cho cả tuần.
>
> Trước đây ô này sửa tự do khi chạy cả tuần: đổi 42 thành 43 rồi chạy lại là
> 22 trên 800 ô của bộ mẫu sáu buổi đổi chủ, trong khi màn hình vẫn báo "đã
> khoá". Nay đổi hạt giống phải đi qua đúng cửa xác nhận hai bước như vẽ lại.
>
> Xoá dữ liệu (mục 9) mở khoá cả bộ số lẫn hạt giống.

**Nhãn buổi và thứ tự ngày.** Phần mềm nhận ra các cách viết thường gặp —
`thu_2`, `thu 2`, `Thứ Hai`, `t2`, và cả nhãn có đuôi như `thu_3_tiet_9` — rồi
sắp theo đúng thứ tự trong tuần. Nhãn không nhận ra được (ví dụ `ngoai_khoa`)
vẫn dùng bình thường, chỉ xếp xuống cuối danh sách theo vần chữ cái.

### Thứ tự bốc thăm của từng buổi đọc ở đâu

Thẻ **Kết quả**, bảng **Số bốc thăm theo buổi**: mỗi em một dòng, mỗi buổi một
cột. Tệp Excel kết quả có cùng bảng này ở trang *Dấu vết (kỹ thuật)*.

Đây là thứ để trả lời câu phụ huynh sẽ hỏi: *"vì sao con tôi thứ Ba đứng thứ 30
mà thứ Sáu đứng thứ 120?"*

**Và nó không làm mất tính minh bạch.** Trường vẫn chỉ công bố **một** thứ: bộ
số đã khoá cộng với con số gieo trong ô `seed`. Thứ tự từng buổi suy ra từ hai
thứ đó theo một quy tắc cố định, nên ai tính lại cũng phải ra đúng bảng ấy —
không có bước nào phần mềm tự bốc thêm.

### Kết quả đọc ở đâu

Thẻ **Kết quả** có thêm hai khối khi trường dùng nhiều buổi:

- **Thời khoá biểu tuần** — mỗi em một dòng, mỗi buổi một ô. Ô trống nghĩa là
  buổi đó em không có CLB nào.
- **Độ phủ theo học sinh** — bao nhiêu em được mấy CLB, và **bao nhiêu em
  không có CLB nào cả tuần**. Con số cuối là thứ tỉ lệ lấp đầy từng CLB không
  bao giờ cho thấy.

Trong tệp Excel kết quả, trang *Danh sách học sinh* lúc này chính là thời khoá
biểu tuần (dán bảng được). Ai cần thêm mỗi buổi một tệp `.csv` riêng thì đánh dấu
*Kèm các tệp CSV rời* — xem Bước 5.

---

## 6. Chạy trọn quy trình — 5 bước

### Bước 1 — Nạp Sổ nhập CLB

Thẻ **01 · Vận hành sắp xếp**. Kéo sổ thả vào ô kéo-thả, hoặc bấm vào ô đó để
chọn tệp.

Phần mềm **đọc thử, chưa ghi gì**, rồi hiện một dòng tóm tắt — với bộ ví dụ:
*"Sẵn sàng nhập: 4 CLB · 1 buổi · 10 học sinh · 19 nguyện vọng · 19 lượt thi"*.
**Đối chiếu con số này trước khi bấm nhập.**

Sổ có lỗi thì phần mềm liệt kê từng lỗi kèm trang và dòng, và **không cho
nhập** — sửa trong Excel, lưu, kéo vào lần nữa. Muốn thấy trước bảng lỗi trông
thế nào: kéo thử `du_lieu_test/SO_NHAP_CO_LOI_CO_Y.xlsx`.

Bấm **Nhập sổ**. Dòng tóm tắt đổi thành *"Xong: … "* kèm số liệu.

### Bước 2 — Đọc mục *Cảnh báo dữ liệu*

Ngay dưới ô nạp tệp. Đây là **bước quan trọng nhất và cũng là bước hay bị bỏ qua
nhất**.

Cảnh báo ở đây **không chặn** phần mềm chạy. Chúng là những thiếu sót vẫn để
thuật toán chạy trơn tru nhưng **âm thầm làm đổi kết quả**. Chạy mà không đọc thì
sẽ có kết quả — chỉ là không phải kết quả bạn tưởng.

Với bộ ví dụ, chỗ này phải ghi **0 cảnh báo**. Nếu có, tra [mục 10](#10-bảng-tra-cảnh-báo).

### Bước 3 — Chấm điểm *(bỏ qua nếu tệp đã có điểm)*

Thẻ **05 · Chấm điểm (mù)**. Chọn CLB, nhập điểm cho từng em, bấm lưu.

> Ô điểm nhận **cả hai cách viết**: `8,5` (kiểu Việt) và `8.5` đều lưu thành
> cùng một giá trị. Lưu xong màn hình hiện lại `8.5` — đó là cùng con số, không
> phải máy sửa gì.

Bộ ví dụ đã có sẵn điểm trong tệp 2, nên bước này bỏ qua.

### Bước 4 — Chạy sắp xếp

Quay lại thẻ **01**. Bấm **Chạy sắp xếp**.

Phần mềm hỏi lại một lần trước khi chạy — vì chạy lần hai sẽ **ghi đè** kết quả
lần trước. Bấm xác nhận.

Màn hình hiện tiến trình 5 bước: sao lưu → kiểm tra dữ liệu → bốc thăm → chạy
thuật toán → ghi kết quả.

> **Ô `seed`** là hạt giống bốc thăm, mặc định `42`. Cùng dữ liệu và cùng `seed`
> thì **luôn ra cùng kết quả** — kể cả trên máy khác, hệ điều hành khác, và
> **kể cả khi nhập học sinh theo thứ tự khác**. Đó là cách kiểm chứng lại kết quả
> sau này. Chỉ nhập được ở lần chạy **đầu tiên** (hoặc sau khi xoá dữ liệu):
> từ đó ô này khoá cùng bộ số bốc thăm, và muốn đổi phải bấm **Vẽ lại số bốc
> thăm…**.
>
> Bốc thăm vẫn hoàn toàn ngẫu nhiên: mã học sinh **không** quyết định ai được số
> tốt. Em `HS01` không hề có lợi thế nào so với em cuối danh sách.

### Bước 5 — Xuất kết quả

Ở thẻ **02 · Kết quả**, mục **Xuất dữ liệu** ở đầu trang: để nguyên ô *Kết quả
sắp xếp* đã đánh dấu và bấm **Xuất các mục đã chọn**. Phần mềm ghi vào **thư mục
Tải xuống** (`Downloads`) của máy — đúng chỗ trình duyệt để tệp tải về, ai cũng
biết tìm. Đường dẫn đầy đủ của từng tệp hiện ngay dưới nút, **không tự tắt**, kèm nút
**Mở thư mục** mở thẳng thư mục chứa tệp.

Có dải vàng *"Dữ liệu đã được sửa sau lần chạy gần nhất"* ở đầu thẻ thì **chạy lại
trước khi xuất** (nút **Đi tới Vận hành sắp xếp** ngay trên dải) — kết quả đang xem được tính từ dữ liệu cũ. Tệp tổng hợp cũng ghi
điều này ở dòng *"Kết quả còn khớp dữ liệu"*, để tệp đã mang đi rồi vẫn tự nói được.

> **Xuất nhiều lần không ghi đè lần trước.** Đã có `ket_qua_phan_bo.xlsx` thì lần
> sau ra `ket_qua_phan_bo (2).xlsx`, rồi `(3)`… giống hệt cách trình duyệt làm.
> Số lớn nhất là lần mới nhất.
>
> Máy nào không có thư mục Tải xuống (hoặc không ghi được vào đó) thì tệp quay về
> nằm cạnh `app.db` như trước — việc xuất **không bao giờ thất bại** chỉ vì
> chuyện chỗ để tệp.

Mỗi lần xuất ra **một tệp Excel duy nhất**, `ket_qua_phan_bo.xlsx`, gồm sáu trang
theo đúng thứ tự người đọc cần:

| Trang | Có gì | Ai dùng |
|---|---|---|
| **Hướng dẫn** | Mấy con số chính (bao nhiêu em, bao nhiêu em đã có CLB, bao nhiêu em chưa có chỗ, tỉ lệ được nguyện vọng 1), và **mục lục bấm được** tới các trang khác. Kết quả đã cũ thì dòng cảnh báo đỏ hiện ngay ở đây | Người mở tệp lần đầu |
| **Danh sách học sinh** | Mỗi em một dòng kèm CLB của em. Bấm mũi tên ở dòng tiêu đề để **lọc theo CLB**. Trường nhiều buổi: đây là **thời khoá biểu tuần**, mỗi buổi một cột. Dòng tô đỏ là em chưa có chỗ | Ban giám hiệu, giáo viên chủ nhiệm |
| **Theo CLB** | Mọi CLB trên một trang, mỗi CLB một khối có số thứ tự. **In ra là mỗi CLB một tờ riêng** | Giáo viên phụ trách CLB |
| **Chưa có chỗ** | Đích danh các em chưa vào CLB nào, kèm em đã khai mấy nguyện vọng và các CLB đó chọi bao nhiêu | Nhóm xử lý tiếp |
| **Thống kê** | Từng CLB (đăng ký, tỉ lệ chọi, lấp đầy), tải từng buổi, độ phủ, nguyện vọng thứ mấy thì được, suất dự trữ dùng tới đâu | Họp ban giám hiệu |
| **Dấu vết (kỹ thuật)** | Hạt giống, cách bốc thăm, thời điểm khoá bộ số — đủ để **ai cũng tính lại** được kết quả; trường nhiều buổi có thêm số bốc thăm từng buổi. Tab màu xám: không cần đọc để dùng kết quả | Khi có người hỏi "bảng này ở đâu ra" |

Mọi trang in vừa khổ **A4**, có tên trang và số trang ở chân. Ở hai trang danh
sách, dòng tiêu đề cột đứng yên khi cuộn và lặp lại ở đầu mỗi tờ in.

**Cần tệp `.csv` cho phần mềm khác?** Đánh dấu thêm ô **Kèm các tệp CSV rời** ngay
dưới ô *Kết quả sắp xếp*. Phần mềm ghi thêm, cùng tên gốc với tệp Excel:

- `ket_qua_phan_bo.csv` — toàn bộ học sinh, mỗi em (mỗi buổi) một dòng
- `ket_qua_phan_bo_tong_hop.csv` — xem mục dưới
- thư mục `ket_qua_phan_bo_theo_club/` — mỗi CLB một tệp, kèm `_chua_duoc_xep.csv`
- trường nhiều buổi: `..._thoi_khoa_bieu.csv`, `..._so_boc_tham_theo_buoi.csv` và
  thư mục `..._theo_buoi/` (một tệp mỗi buổi)

Mọi tệp đều mở được bằng Excel, tiếng Việt không vỡ dấu.

#### Tệp tổng hợp — đọc trước khi mang kết quả đi đâu

`..._tong_hop.csv` (chỉ có khi đánh dấu *Kèm các tệp CSV rời*) là tệp trả lời câu
hỏi **"kết quả này tính thế nào"**. Cùng nội dung ấy nằm sẵn trong tệp Excel, chia
ra ba trang *Thống kê*, *Chưa có chỗ* và *Dấu vết (kỹ thuật)*. Tệp `.csv` có bảy phần:

| Phần | Nội dung |
|---|---|
| **Dấu vết lần chạy** | Hạt giống, cách bốc thăm, thời điểm khoá bộ số, thời điểm chạy, buổi đã chạy |
| **Độ phủ** | Bao nhiêu em được 0, 1, 2… câu lạc bộ trong tuần |
| **Từng câu lạc bộ** | Số em đăng ký, số em đặt nguyện vọng 1, tỉ lệ chọi, đã xếp trên sức chứa |
| **Tải từng buổi** | Buổi nào chật, buổi nào rộng (chỉ hiện khi trường dùng nhiều buổi) |
| **Mức đáp ứng nguyện vọng** | Bao nhiêu chỗ là nguyện vọng 1, 2, 3, 4 trở lên |
| **Suất dự trữ dùng tới đâu** | Từng câu lạc bộ có dự trữ: đã dùng bao nhiêu, **còn thừa** bao nhiêu |
| **Em chưa có chỗ nào** | Đích danh, kèm em ấy đã khai mấy nguyện vọng và vào những câu lạc bộ chọi bao nhiêu |

Màn hình, tệp Excel và tệp `.csv` đọc **chung một nguồn**, nên không có đường
nào để chúng nói khác nhau.

> Số thập phân trong các tệp `.csv` viết theo kiểu Việt Nam — `4,61` chứ
> không phải `4.61` — vì Excel trên máy cài tiếng Việt hiểu dấu chấm là dấu
> phân cách hàng nghìn. Riêng các trang trong sổ Excel giữ **số thật** (kiểu
> số, không phải chữ) để còn sắp xếp và tính toán được; Excel tự hiển thị
> theo máy của người mở.

> **Ba dòng đầu là thứ quan trọng nhất trong cả bộ tệp.** Hạt giống cộng bộ số
> đã khoá cộng cách bốc thăm là đủ để **bất kỳ ai tính lại** và phải ra đúng kết
> quả này. Không có ba dòng đó thì sáu tháng sau, khi có người hỏi "bảng này ở
> đâu ra", không còn gì để trả lời.

> Tệp kết quả là **dữ liệu học sinh**. Cân nhắc trước khi gửi qua email hay chép
> lên máy dùng chung.

> **Vì sao mục "Kết quả sắp xếp" bị khoá?** Mục này chỉ dùng được khi đã có kết quả xếp. Chưa chạy xếp, hoặc lần chạy bị chặn, thì ô bị khoá và có dòng vàng "Chưa có kết quả xếp. Chạy xếp trước." Chạy xếp thành công rồi quay lại thẻ Kết quả là ô mở lại. Các mục khác (dữ liệu đầu vào, hồ sơ học sinh) vẫn xuất được.

**Thông báo nổi** ở góc dưới bên phải: thông báo thành công tự đóng sau 6 đến 10 giây (đưa chuột vào thì dừng đếm); lỗi và cảnh báo ở lại cho tới khi bạn bấm ×.

#### Xuất thêm: dữ liệu đầu vào, thay đổi, hồ sơ học sinh

Cùng mục **Xuất dữ liệu**, đánh dấu thêm ô nào thì xuất thêm thứ đó — một lần bấm:

| Ô | Ra tệp gì | Dùng để làm gì |
|---|---|---|
| **Dữ liệu đầu vào hiện tại** | Một Sổ nhập CLB `SO_NHAP_CLB_<ngày_giờ>.xlsx` | Lưu lại **đúng dữ liệu đang có, kể cả mọi chỗ sửa tay** sau khi nạp. Kéo sổ vào ô nạp của một máy khác là dựng lại y nguyên. Lượt thi một CLB mà em không xếp nguyện vọng thì sổ không chứa được (lượt đó không đổi được kết quả) — phần mềm báo số lượt đó |
| **Thay đổi so với lần chạy trước** | `thay_doi_ket_qua.csv` | Sau khi sửa điểm rồi chạy lại: **những em nào đổi kết quả**, CLB cũ → CLB mới, và loại thay đổi (*Đổi CLB, Mới được xếp, Mất chỗ, Đổi diện…*). Ô này mờ đi khi chưa chạy đủ hai lần |

**Hồ sơ một em hoặc nhiều em** — ba chỗ, chọn chỗ nào tiện:

| Đang ở đâu | Làm gì |
|---|---|
| Thẻ **03**, đang mở một em | Bấm **Xuất CSV em này** (cạnh *Sửa lại từ đầu*). Em còn thay đổi chưa lưu thì phần mềm nhắc lưu trước |
| Thẻ **02**, mục Xuất dữ liệu | Bấm **Chọn học sinh…** → phần mềm đưa xuống bảng *Danh sách xếp CLB* → đánh dấu các em → quay lên, ô **Hồ sơ học sinh đã chọn** đã tự bật → **Xuất các mục đã chọn** (cùng lúc với các mục khác) |
| Thẻ **04**, danh sách học sinh | Đánh dấu (dòng tiêu đề chọn cả trang; số em đang đánh dấu hiện bên cạnh) → **Xuất CSV học sinh đã đánh dấu** |

Mỗi dòng trong tệp là một CLB em có dính tới: đã đăng ký thi chưa, điểm, nguyện vọng
thứ mấy, số bốc thăm, và kết quả.

- Ở thẻ 02, **tập đã chọn giữ nguyên khi đổi ô tìm**: tìm "An" đánh dấu một em, tìm
  "Bình" đánh dấu thêm một em, bấm xuất là ra cả hai.
- Ô đánh dấu ở dòng tiêu đề chọn **các em đang hiện** (sau khi lọc), không phải cả
  trường.
- Trường **nhiều buổi**: bảng chỉ liệt kê chỗ đã xếp, nên em không được xếp buổi nào
  không có dòng để đánh dấu. Bật **Hiện cả em chưa được xếp** — mỗi em như vậy thêm
  một dòng ghi *Cả tuần*.

> ⚠️ **Tệp dữ liệu đầu vào và tệp hồ sơ học sinh có ĐIỂM CHẤM và SỐ BỐC THĂM.**
> Không gửi cho giáo viên chấm điểm — chấm mù chỉ còn ý nghĩa khi người chấm không
> thấy những con số đó.

---

## 7. Đọc bảng kết quả

Thẻ **02 · Kết quả**, hoặc mở tệp vừa xuất.

### Đóng bớt những mục chưa cần nhìn

Thẻ này có chín mục xếp dọc. Bấm vào **tiêu đề mục** (hoặc mũi tên ▾ bên
trái) để đóng hoặc mở mục đó; nút **Thu gọn tất cả** ở góc trên bên phải làm
một lượt cho cả chín.

Lần đầu mở, ba mục trả lời câu hỏi chính — *Tỉ lệ lấp đầy*, *Độ phủ*,
*Danh sách xếp CLB* — được mở, sáu mục tra cứu còn lại thu gọn sẵn. Phần mềm
**nhớ** lựa chọn của bạn cho những lần sau.

Mục đang đóng vẫn hiện con số bên cạnh tiêu đề (*Thời khoá biểu tuần ·
160 em*), nên nhìn là biết bên trong có gì.

> **Đóng một mục không xoá gì cả.** Đây thuần tuý là chuyện nhìn cho gọn:
> dữ liệu không đổi, và tệp xuất ra vẫn đủ mọi mục dù lúc bấm Xuất bạn đang
> đóng hết.

### Bốn mục trả lời những câu hỏi bảng kết quả không trả lời

#### Theo từng câu lạc bộ — *ai ở trong, và bao nhiêu em muốn vào*

Thanh lấp đầy nói `16/16` giống hệt nhau cho một câu lạc bộ đầy với 18 em
đăng ký và một câu lạc bộ đầy với 90 em đăng ký. Với nhà trường đó là hai
bài toán khác hẳn. Bảng này thêm phía **cầu**: số em đăng ký, số em đặt làm
nguyện vọng 1, và tỉ lệ chọi.

Bấm **Xem danh sách** ở cuối một dòng để hiện **danh sách thành viên** câu
lạc bộ đó ngay bên dưới — tờ giấy đưa cho thầy cô phụ trách. Trước đây chỉ
lấy được bằng cách bấm Xuất rồi mở từng tệp trong thư mục `..._theo_club/`.

> ⚠️ **Cột "Số em đăng ký" KHÔNG cộng dồn được.** Trong cùng một buổi, một em
> khai ba câu lạc bộ thì được đếm ở cả ba dòng, trong khi em ấy chỉ lấy được
> **một** chỗ. Cộng cả cột rồi chia cho tổng chỉ tiêu sẽ ra một tỉ lệ chọi
> phồng lên vô nghĩa. Muốn tỉ lệ chọi **theo buổi** thì đọc bảng *Tải từng
> buổi* ở thẻ **04 · Quản lý CLB**.

#### Suất dự trữ dùng tới đâu

Một suất dự trữ không ai dùng **không báo lỗi và không hiện ở đâu** — nó
lặng lẽ trở thành một suất thường. Cơ chế vẫn chạy đúng, còn ý định ưu tiên
thì biến mất. Cột **Còn thừa** là con số để quyết định nới nhãn ưu tiên hay
hạ chỉ tiêu dự trữ năm sau; khác 0 thì nó hiện màu đỏ.

#### Mức đáp ứng nguyện vọng

Độ phủ nói *bao nhiêu em có chỗ*, không nói *chỗ ấy có phải thứ em muốn
không*. Một lần chạy 90% em được nguyện vọng 1 và một lần phần lớn em được
nguyện vọng 4 cho ra **cùng một con số độ phủ**. Đây là con số phân biệt
được hai lần chạy ấy, và là con số nhà trường bị hỏi đầu tiên khi công bố.

Mục này có hai hình vẽ từ cùng một số liệu:

- **Vành khuyên** bên trái cho thấy mỗi thứ hạng chiếm **bao nhiêu phần trên
  tổng số chỗ đã xếp**. Con số ở giữa là tỉ lệ nguyện vọng 1. Màu càng đậm là
  nguyện vọng càng cao; chú giải bên dưới ghi số chỗ và phần trăm của từng
  phần.
- **Thanh ngang** bên phải để **so hai mức gần nhau** (ví dụ nguyện vọng 3 và
  nguyện vọng 4 trở lên) — việc mà hình tròn làm kém.

Rê chuột (hoặc dùng bàn phím di tới) một cung hay một thanh để xem số chỗ,
phần trăm, và phần trăm **cộng dồn** tới thứ hạng đó.

#### Em chưa có chỗ nào

Danh sách tên kèm **em ấy đã khai gì**: bao nhiêu nguyện vọng, vào những câu
lạc bộ chọi bao nhiêu. Một em khai **một** nguyện vọng vào câu lạc bộ chọi 5
lần là một chuyện; một em khai **tám** nguyện vọng mà vẫn trắng tay là chuyện
khác hẳn — và hai chuyện đó cần hai cách xử lý khác nhau.

| Cột | Nghĩa |
|---|---|
| Mã học sinh, Họ tên | |
| Mã CLB, Tên CLB | CLB em được xếp vào. **Trống = chưa được xếp** |
| **Nguyện vọng thứ** | Em vào CLB này là nguyện vọng thứ mấy của em. `1` là toại nguyện |
| **Diện trúng tuyển** | `Thường` = cạnh tranh ở chỉ tiêu chung · `Dự trữ` = vào bằng suất dành riêng |
| Nhóm dự trữ | Nhãn diện ưu tiên của em, nếu có |

### Kết quả đúng của bộ ví dụ

Chạy với `seed = 42`:

| Mã | Họ tên | CLB | NV thứ | Diện |
|---|---|---|---|---|
| HS01 | Nguyễn Văn An | CLB Bóng rổ | 1 | Thường |
| HS02 | Trần Thị Bình | CLB Bóng rổ | 1 | Thường |
| HS03 | Lê Minh Cường | CLB Nấu ăn | **2** | Thường |
| HS04 | Phạm Thu Dung | CLB Bóng rổ | 1 | **Dự trữ** |
| HS05 | Hoàng Văn Đức | CLB Tin học | **2** | Thường |
| HS06 | Vũ Ngọc Giang | CLB Tin học | 1 | Thường |
| HS07 | Đỗ Thị Hạnh | CLB Mỹ thuật | 1 | Thường |
| HS08 | Bùi Quang Khánh | CLB Mỹ thuật | 1 | Thường |
| HS09 | Ngô Phương Linh | CLB Nấu ăn | 1 | Thường |
| **HS10** | Dương Bá Minh | *(trống)* | — | — |

Sức chứa: Bóng rổ **3/3** · Mỹ thuật **2/2** · Tin học **2/2** · Nấu ăn **2/3**

Ở thẻ **02 · Kết quả** còn có biểu đồ *Tỉ lệ lấp đầy theo CLB*. Mỗi thanh đọc
như sau: phần **vàng** là số em vào **bằng suất dự trữ**, phần **xanh** là số em
vào ở chỉ tiêu chung, phần **trắng còn lại** là chỗ chưa lấp đầy. Hai phần màu
cộng lại đúng bằng con số in bên phải thanh.

**Ra khác bảng này là có gì đó đã đổi** — dữ liệu, `seed`, hoặc phiên bản phần mềm.

### Ba điều bảng này cho thấy

**HS03 và HS05 không được nguyện vọng 1.** Sáu em xếp Bóng rổ làm nguyện vọng 1
nhưng chỉ có 3 chỗ. Hai em này tụt xuống nguyện vọng 2.

**HS04 vào bằng suất dự trữ.** Em này điểm Bóng rổ **6,0** — thấp nhất trong số
em xếp Bóng rổ. Chạy thử lại sau khi bỏ suất dự trữ đi thì **đúng một chỗ đổi
chủ**:

| | Có suất dự trữ | Bỏ suất dự trữ |
|---|---|---|
| HS04 *(6,0 · diện chinh_sach)* | **CLB Bóng rổ** | **chưa được xếp** |
| HS03 *(8,0)* | CLB Nấu ăn | CLB Bóng rổ |

**HS10 chưa được xếp, dù Nấu ăn còn trống một chỗ.** Vì em chỉ xếp **một** nguyện
vọng, vào đúng CLB đông nhất. Thuật toán **không nhét học sinh vào CLB các em
không chọn** — nếu có, nó đã tự quyết thay các em.

> Gặp tệp `_chua_duoc_xep.csv` không có nghĩa là phần mềm hỏng. Nó có nghĩa là
> những em đó cần được hỏi lại nguyện vọng. **Cách phòng: khuyến khích học sinh
> xếp nhiều nguyện vọng.**

---

## 8. Nhập tay tại chỗ

Dùng khi học sinh không nộp được qua biểu mẫu.

Thẻ **03 · Nhập dự phòng**. Ba bước tách biệt, không ảnh hưởng lẫn nhau:

1. **Tìm hoặc tạo học sinh** — gõ mã hoặc tên. Gõ có dấu hay không dấu, hoa hay
   thường đều được: `binh`, `BÌNH`, `Bình` cùng ra "Lê Thị Bình". Chưa có thì bấm
   *Tạo học sinh mới*.
2. **Chọn CLB muốn thi** — đánh dấu các CLB em muốn thi.
   **Bỏ đánh dấu một CLB đã được chấm điểm là em rút khỏi bài thi đó:** bấm *Lưu*
   thì điểm của CLB ấy bị xoá theo, và màn hình báo *"đã xoá N điểm của CLB bỏ
   chọn"*. Đánh dấu lại thì em quay về thẻ 05 với ô điểm **trống**, phải chấm lại.
3. **Xếp hạng nguyện vọng** — chọn theo thứ tự, nguyện vọng 1 là mong muốn nhất.

Đánh dấu hay xếp nguyện vọng **chưa vào máy cho tới khi bấm Lưu**. Còn thay đổi chưa
lưu thì cạnh nút Lưu hiện **• Chưa lưu**; bấm sang em khác, tạo em mới hay sang thẻ
khác lúc đó thì phần mềm **dừng lại và nhắc**. Muốn bỏ thay đổi thật thì bấm lại
đúng chỗ đó lần nữa (trong 4 giây).

Nút **Sửa lại từ đầu** xoá cả ô đánh dấu, nguyện vọng **và điểm đã chấm** của em.
Nạp lại tệp chọn CLB thi cũng theo đúng luật này: CLB nào không còn trong tệp mới
thì điểm cũ của CLB đó bị xoá, và phần cảnh báo sau khi nạp nêu tên từng em.

Có nút **Xoá học sinh** cho trường hợp tạo nhầm mã. Nút này **bị chặn** nếu em đó
đã nằm trong kết quả của lần chạy gần nhất — phải chạy lại phân bổ trước.

### Thêm học sinh SAU khi đã chạy lần đầu

Chạy phân bổ lần đầu là **khoá bộ số bốc thăm** lại. Thêm học sinh sau đó — qua
màn hình này hoặc bằng cách nạp thêm một tệp — thì:

- **Thứ tự giữa các em đã có giữ nguyên tuyệt đối.** Không em nào bị đẩy lên hay
  tụt xuống so với em khác vì có người mới vào.
- **Em mới bốc một vị trí ngẫu nhiên** trong dàn số — có thể trên, có thể dưới em
  cũ. Đúng nghĩa bốc thăm, giống như em có mặt từ đầu.

> Nghĩa là **em mới có thể giành được suất mà một em cũ đang giữ**. Đó là điều
> phải xảy ra nếu muốn công bằng: cho em mới một cơ hội thật thì cơ hội đó phải
> lấy từ đâu đó. Việc này cũng đã đúng như vậy với **điểm thi** — một em mới điểm
> cao vẫn luôn đánh bật được em cũ điểm thấp hơn.
>
> Vẫn nên **chốt danh sách trước khi chạy lần đầu**. Chạy sớm rồi thêm dần không
> sai, nhưng kết quả công bố ở mỗi lần chạy có thể khác nhau.

---

## 9. Làm lại từ đầu, và chuyện sao lưu

### Nạp tệp chỉ CỘNG THÊM học sinh

Đây là điều dễ hiểu nhầm nhất. Nạp tệp **không xoá** học sinh đã có. Đó là hành
vi đúng — trường nạp khối 10 rồi nạp khối 11 thì không được mất khối 10.

Nhưng nghĩa là: **muốn chạy thử lại với bộ dữ liệu khác thì phải xoá trước**.
Không xoá thì học sinh của lần trước vẫn chiếm suất và làm lệch kết quả.

### Cách xoá

Thẻ **04 · Quản lý CLB & dự trữ**, kéo xuống cuối trang, khối **Vùng nguy hiểm**:

| Nút | Xoá gì |
|---|---|
| **Xoá toàn bộ học sinh (giữ CLB)** | Học sinh, nguyện vọng, điểm, kết quả — **giữ** danh sách CLB |
| **Xoá toàn bộ dữ liệu** | Như trên, và xoá cả danh sách CLB |

Phải bấm **hai lần** mới xoá thật. Bấm một lần chỉ đổi nhãn nút thành *"Bấm lần
nữa để…"*; không bấm tiếp trong 4 giây thì nút tự nhả.

### Không mất gì

Cả hai nút đều **tự sao lưu `app.db`** trước khi xoá. Tên tệp sao lưu hiện trong
thông báo, dạng `app.db.bak-20260901_132528`. Muốn lấy lại: đóng phần mềm, đổi
tên tệp đó thành `app.db`.

**Nhật ký các lần chạy không bao giờ bị xoá** — dấu vết kiểm toán được giữ nguyên.

### Sao lưu thường ngày

Toàn bộ dữ liệu nằm trong **một tệp duy nhất**: `app.db`, cạnh
`PhanBoCauLacBo.exe`. Sao lưu = đóng phần mềm rồi chép tệp đó ra USB. Không cần
chép tệp nào khác.

---

## 10. Bảng tra cảnh báo

Bảy quy tắc rà soát. Mỗi cảnh báo nói một điều **vẫn để phần mềm chạy** nhưng làm
đổi kết quả.

| Cảnh báo | Nghĩa là gì | Sửa ở đâu |
|---|---|---|
| **CLB … chưa chấm điểm ai** | Có em đăng ký thi nhưng chưa ai được chấm. Cả nhóm rơi xuống tầng 2, vòng thi coi như không có tác dụng | Thẻ 05 · Chấm điểm |
| **CLB … mới chấm x/y** | Em chưa có điểm bị xếp **dưới tất cả** em đã có điểm, kể cả em thấp nhất | Thẻ 05 · Chấm điểm |
| **n lượt thi bỏ phí** | Em đăng ký thi một CLB nhưng không xếp CLB đó vào nguyện vọng. Điểm cao mấy cũng không vào được | Sửa tệp 3, nạp lại |
| **n em chưa xếp nguyện vọng nào** | Những em này chắc chắn không được xếp vào đâu | Sửa tệp 3, hoặc thẻ 03 |
| **Nhãn dự trữ "…" không CLB nào dùng** | Gõ sai chính tả nhãn. Em mang nhãn đó **mất quyền ưu tiên ở mọi nơi**. Cảnh báo có kèm mã học sinh | Thẻ 04: tìm mã em, đánh dấu, để trống ô nhãn, bấm *Gán* |
| **CLB … có suất dự trữ nhưng chưa đặt nhãn** | Các suất đó âm thầm thành suất phổ thông | Thẻ 04: sửa CLB |
| **CLB … dành suất cho nhãn chưa em nào mang** | Suất dự trữ sẽ không dùng đến | Kiểm tra lại cột `reserve_group` ở tệp 2 hoặc 3 |
| **Tổng chỗ ít hơn số học sinh** | Chắc chắn có em không có chỗ. Đây là thông tin, không phải lỗi | Tăng chỉ tiêu, hoặc chấp nhận |
| **CLB … có n điểm lệch hẳn** | Một điểm cách xa hẳn các điểm còn lại của chính CLB đó — thường là gõ `70` thay vì `7.0`. Điểm sai đẩy em đó lên đầu bảng và kéo em khác tụt xuống | Thẻ 05 · Chấm điểm |

Ngoài ra, **lúc nạp tệp** còn có cảnh báo riêng: mã trùng hoa/thường, một mã xuất
hiện hai dòng, mã nghi bị Excel cắt mất số 0 đứng đầu, mã CLB không tồn tại, cột
điểm đặt nhầm vào tệp nguyện vọng.

---

## 11. Sự cố hay gặp

### Màn hình ghi "Đang kết nối với phần lõi chương trình…"

Bình thường. Lần mở **đầu tiên sau khi cài** hay lâu hơn những lần sau, vì
Windows còn đang dựng bộ hiển thị và quét tệp mới. Cứ để yên, đừng bấm gì.

Nếu sau đó hiện câu **"Không kết nối được với phần lõi chương trình"**:

1. Đóng hẳn cửa sổ rồi mở lại phần mềm — phần lớn trường hợp hết ngay.
2. Vẫn vậy thì gửi tệp **`loi_khoi_dong.txt`** (nằm cùng thư mục với `app.db`)
   cho người phụ trách. Tệp đó ghi rõ phần mềm hỏng ở bước nào — không có nó thì
   chỉ còn cách đoán.

> Bản trước có lỗi ở chỗ này: đôi khi màn hình hiện câu tiếng Anh
> *"Backend not ready yet"*. Đã sửa. Nếu vẫn thấy câu tiếng Anh đó, nghĩa là bản
> `.exe` đang dùng là **bản cũ** — cần lấy bản mới.

### Mở tệp xuất ra bằng Excel thì vỡ dấu tiếng Việt

Không nên xảy ra — phần mềm ghi kèm dấu nhận dạng (BOM) để Excel hiểu đúng.
Nếu vẫn vỡ: trong Excel dùng **Data → From Text/CSV**, chọn mã hoá **UTF-8**.

### Phần mềm mở ra trong cửa sổ Edge

Nhìn góc dưới bên trái. Ghi **"Chế độ dự phòng (trình duyệt)"** màu vàng nghĩa là
cửa sổ gốc không mở được.

Nguyên nhân: Windows gắn dấu *"tải từ Internet"* vào tệp giải nén từ `.zip` tải
về. Bản mới **tự gỡ dấu** lúc khởi động nên hiếm khi gặp. Nếu gặp:

1. Chuột phải tệp `.zip` → **Properties** → tích **Unblock** → giải nén lại vào
   thư mục **mới**
2. Đã lỡ giải nén rồi thì mở PowerShell tại thư mục đó, gõ:
   `Get-ChildItem -Recurse | Unblock-File`
3. Vẫn không được thì mở tệp **`loi_khoi_dong.txt`** cạnh `PhanBoCauLacBo.exe` —
   trong đó có nguyên văn lý do.

> Chạy ở chế độ dự phòng **không thiếu tính năng nào**. Khác biệt duy nhất là máy
> phải có sẵn Edge hoặc Chrome.

### Nạp tệp xong mà số học sinh cao hơn mong đợi

Dữ liệu lần trước vẫn còn. Xem [mục 9](#9-làm-lại-từ-đầu-và-chuyện-sao-lưu).

### Lỡ xoá dữ liệu

Tệp `app.db.bak-…` nằm cạnh `PhanBoCauLacBo.exe`. Đóng phần mềm, đổi tên tệp đó
thành `app.db`.

### Excel làm mất số 0 đứng đầu mã học sinh

`0012345` để Excel tự nhận định dạng thì thành `12345`. Phần mềm **phát hiện
được** và cảnh báo, nhưng **không cứu được** — nó không biết mã gốc dài bao nhiêu.
Sổ nhập mẫu đã để sẵn cột Mã HS ở dạng **Text**. Dán dữ liệu từ nơi khác vào thì
dùng *Dán giá trị* (Paste Values) để giữ dạng đó.

---

## 12. Thuật toán làm gì

Phần này mô tả **cách phần mềm hoạt động**, để người dùng hiểu vì sao kết quả ra
như vậy.

### Ý tưởng gốc: học sinh "nộp đơn" theo vòng

1. Mỗi em nộp đơn vào **nguyện vọng 1** của mình.
2. Mỗi CLB xếp hạng tất cả đơn nhận được, **giữ tạm** số em bằng đúng chỉ tiêu,
   từ chối phần còn lại.
3. Em bị từ chối nộp tiếp vào **nguyện vọng kế tiếp**.
4. Lặp lại cho tới khi không còn ai bị từ chối.

Điểm mấu chốt: CLB chỉ **giữ tạm**. Vòng sau có em giỏi hơn nộp vào thì em đang
được giữ bị đẩy ra, và lại đi nộp tiếp. Nhờ vậy không ai bị chốt sớm một cách bất
công. Bộ ví dụ chạy xong sau **2 vòng**.

### CLB xếp hạng đơn thế nào

Hai tầng:

- **Tầng 1** — em **có thi** CLB đó: xếp theo **điểm**, cao trước.
- **Tầng 2** — em **không thi** nhưng có xếp nguyện vọng: xếp theo **số bốc thăm**.

Tầng 1 luôn đứng trên tầng 2. Bằng điểm nhau thì **số bốc thăm** phân định.

### Số bốc thăm (STB)

Mỗi em được bốc **một số duy nhất**, dùng chung cho **mọi** CLB. Không phải mỗi
CLB bốc lại một lần.

Vì sao quan trọng: nếu mỗi CLB bốc riêng, một em xui có thể xui ở tất cả các CLB
cùng lúc. Bốc một lần dùng chung thì rủi ro trải đều hơn.

Số bốc thăm sinh từ ô `seed`. Cùng `seed` → cùng bộ số → cùng kết quả. Sau lần
chạy đầu, số bốc thăm **và hạt giống** bị **khoá** để lần chạy sau không vô tình
bốc lại và làm đổi kết quả đã công bố.

### Đổi `seed` thì kết quả đổi tới đâu

Câu hỏi tự nhiên: nếu bốc thăm khác đi thì kết quả khác tới mức nào? Đã **đo**,
chạy lại toàn bộ quy trình với **200 seed** trên ba bộ dữ liệu:

| Bộ dữ liệu | Số em **không bao giờ** đổi CLB | Em đổi CLB (trung bình / nhiều nhất) |
|---|---|---|
| Ví dụ hướng dẫn — 10 em / 4 CLB | **10 / 10 (100%)** | 0 / 0 |
| Bộ sạch — 140 em / 12 CLB | **127 / 140 (91%)** | 6,0 / 11 em |
| Bộ TEST — 120 em / 10 CLB | **116 / 120 (97%)** | 1,9 / 4 em |

Bộ ví dụ trong hướng dẫn này **không có em nào hoà điểm và không em nào dự tuyển
CLB mình không thi**, nên `seed` không có chỗ nào để chen vào: đổi seed kiểu gì
cũng ra **đúng một kết quả**. Đó là minh hoạ trực tiếp cho quy tắc ở trên — điểm
đứng trước, bốc thăm chỉ phân định khi điểm đã hoà.

Hai điều nữa đã đo:

- **Mọi seed đều cho kết quả ổn định** — không có cặp phá vỡ nào ở bất kỳ seed
  nào trong 200 seed. Đổi seed đổi *ai* được suất trong nhóm hoà nhau, chứ không
  làm kết quả sai.
- **Seed có thể đổi cả việc một em có suất hay không**, không chỉ đổi CLB. Đã
  đếm riêng: trên **270 em của cả ba bộ, đúng 3 em (1,1%)** rơi vào diện này —
  0 em ở bộ ví dụ, 1 em (0,7%) ở bộ sạch, 2 em (1,7%) ở bộ TEST. Còn lại thì
  hoặc luôn có suất, hoặc luôn không, bất kể seed.

**Ba em đó rơi vào diện bấp bênh trong trường hợp nào:** em bị từ chối hết các
nguyện vọng trên, rơi xuống **nguyện vọng cuối cùng còn với tới được**, và ở
đúng đó lại đứng ngay ranh giới chỉ tiêu trong một nhóm hoà nhau. Thua lượt bốc
thăm ở chỗ đó thì không còn nguyện vọng nào phía dưới để rơi tiếp.

Một em trong số đó chỉ đăng ký **2 nguyện vọng**, nên không có lưới nào đỡ. Số
liệu chi tiết từng em ở `du_lieu_test/SO_LIEU_DA_KIEM_CHUNG.md` mục 3c.

Tái lập: `python du_lieu_test/do_anh_huong_seed.py --so-seed 200`

### Suất dự trữ

Trong `capacity` chỗ của một CLB, `reserve_capacity` chỗ được xét **trước** và
**chỉ** dành cho em mang đúng `reserve_group` của CLB đó.

Trường **tự đặt** tiêu chí. Phần mềm chỉ so khớp nhãn giữa CLB và học sinh, không
cài sẵn bất kỳ chính sách nào.

Suất dự trữ là *mềm*: nếu không đủ em thuộc diện đó, chỗ thừa **chuyển thành chỗ
phổ thông** chứ không bỏ trống.

### "Kết quả ổn định" nghĩa là gì

Khi chạy xong, không tồn tại cặp (học sinh X, CLB Y) nào mà **cả hai** đều muốn
đổi: X thích Y hơn CLB đang được xếp, **và** Y cũng sẵn sàng nhận X thay cho một
em đang giữ chỗ.

Phần mềm **tự kiểm chứng** điều này sau mỗi lần chạy. Bộ ví dụ: **0 cặp chặn**.

---

## 13. Giới hạn đã biết

Ghi ra để người dùng biết trước, không phải để bào chữa.

| Giới hạn | Ảnh hưởng |
|---|---|
| **Tối đa 10 nguyện vọng mỗi em MỖI BUỔI** | Tính theo từng buổi, không phải cả tuần — trường sáu buổi thì một em xếp được tới 60 nguyện vọng. Buổi nào quá 10 thì **riêng buổi đó** không được nhập, có cảnh báo nêu đích danh; các buổi khác vẫn nhập. Trường một buổi: y hệt như trước |
| **Tối đa 5 câu lạc bộ dự thi mỗi buổi** | Luật mới. Buổi nào quá 5 thì buổi đó không được nhập, kể cả điểm của nó |
| **Điểm bất thường chỉ được CẢNH BÁO, không bị chặn** | Phần mềm không đặt trần cứng (trường có thể chấm thang 100), mà so mỗi điểm với trung vị của chính CLB đó. Lệch quá 3 lần thì báo — bắt được cả `70` lẫn `0.85`. Nhưng một điểm sai *vừa phải*, ví dụ 9 thay vì 8, thì không cách nào phát hiện được |
| **Chưa có nút "Sao lưu ngay"** | Phần mềm tự sao lưu trước mỗi lần chạy và trước khi xoá. Sao lưu thường ngày vẫn phải chép tay tệp `app.db` |
| **Windows cảnh báo nhà phát hành không xác định** | Do chưa mua chứng chỉ ký số thương mại, không phải lỗi phần mềm |
| **Vài em có suất hay không phụ thuộc bốc thăm** | Đo trên 270 em của ba bộ dữ liệu: **3 em (1,1%)**. Đây không phải lỗi — xem ngay dưới |

### Vì sao có em phụ thuộc bốc thăm, và vì sao đó không phải lỗi

Khi hai em **bằng điểm nhau** ở cùng một CLB còn đúng một chỗ, phải có gì đó phân
định. Mọi cách khác đều **thiên vị có hệ thống**: xếp theo thứ tự nhập thì ai nộp
sớm luôn thắng; xếp theo mã học sinh thì em mã nhỏ luôn thắng — cùng một người
được lợi ở **mọi** CLB, năm này qua năm khác. Bốc thăm không thiên vị ai.

Đã đo và **không** xảy ra ba điều đáng lo:

| Nếu | Đo được |
|---|---|
| Bốc thăm lật ngược kết quả của em **điểm khác nhau** | **Không.** 3 em 3 điểm khác nhau, 100 seed, cùng một kết quả |
| Bốc thăm làm kết quả mất tính ổn định | **Không.** 0 cặp phá vỡ trên 200 seed, cả ba bộ |
| Bốc thăm thiên vị một em cụ thể | **Không.** Hai em hoà điểm tranh một suất: cả hai đều từng thắng |

**Chỗ thật sự cần giữ, và phần mềm đã giữ:** vì bốc thăm *có* đổi số phận của vài
em, việc bốc đi bốc lại rồi chọn kết quả vừa ý là rủi ro thật. Sau lần chạy đầu,
bộ số bốc thăm và hạt giống bị **khoá**; bốc lại hay đổi hạt giống phải bật cờ
riêng, không thể lỡ tay; và **mỗi
lần chạy đều ghi thêm một dòng vào lịch sử** kèm `seed` và dấu "đã bốc lại" —
bảng đó **không bao giờ bị ghi đè**, kể cả khi xoá toàn bộ dữ liệu. Ai bốc lại để
dò seed đẹp sẽ để lại dấu vết không xoá được.

**Điều nhà trường nên làm — quan trọng hơn mọi thứ trên:** nói với học sinh rằng
**hãy xếp hết những CLB em thật sự chấp nhận vào**. Đã đo hẳn hoi — cùng bộ dữ
liệu 140 em, chỉ cắt ngắn danh sách nguyện vọng:

| Mỗi em xếp | Số em không có suất (trung bình) |
|---|---|
| 1 nguyện vọng | **48 em** |
| 2 nguyện vọng | 26 em |
| 3 nguyện vọng | 15 em |
| 4 nguyện vọng | 7,5 em |
| 5 nguyện vọng | 1,2 em |
| 6 nguyện vọng | **0,3 em** |

Bỏ trống nguyện vọng là tự bỏ cơ hội của chính mình.

> ### ⚠️ Nhưng KHÔNG được bắt học sinh điền cho đủ số ô
>
> Bảng trên đo chuyện **cắt bớt** nguyện vọng của em vốn đã khai đủ — tức nó cho
> thấy em **mất gì khi không khai hết những CLB mình vẫn chấp nhận**. Nó **không**
> nói rằng bắt em khai thêm CLB em **không muốn** thì tốt.
>
> Bắt khai thêm CLB không muốn thì em có thể **bị xếp đúng vào CLB đó**, và với
> em như thế còn tệ hơn không có suất. Trường cũng mất luôn dữ liệu về nguyện
> vọng thật.
>
> Cách nói đúng với học sinh: *"Em cứ xếp theo đúng thứ tự em muốn, và đừng bỏ
> sót CLB nào em sẵn sàng vào. Khai thật là có lợi nhất cho em."*
>
> Và **không có suất không phải lúc nào cũng là thất bại**: em chỉ muốn 2 CLB, cả
> hai đều hết chỗ, thì không có suất là câu trả lời trung thực.

Số liệu đầy đủ: `du_lieu_test/SO_LIEU_DA_KIEM_CHUNG.md` mục 3c.
Ba câu hỏi hay gặp nhất về bốc thăm, kèm số đo: **`docs/GIAI_DAP_BOC_THAM.md`**.

## 14. Điểm quyết tâm (tuỳ chọn)

> Dành cho người bảo trì: trong mã và trong tên cột tệp, tính năng này vẫn gọi là `wharton` (ví dụ `rules.wharton`, cột `wp_k`).

Mặc định **TẮT**: không bật thì phần mềm chạy y hệt như trước, kể cả kết quả và dấu vân tay dữ liệu.
Khi bật, mỗi học sinh tự chia điểm để nói mình muốn CLB nào hơn. Điểm này được xét **trước** số bốc thăm
và **sau** điểm thi; thứ tự nguyện vọng không bao giờ ảnh hưởng thứ tự ưu tiên của CLB.

### Hai quỹ điểm

- Mỗi buổi, mỗi học sinh có **hai quỹ, mỗi quỹ đúng 100 điểm** (số nguyên từ 0 trở lên; ô trống tính là 0).
- **Quỹ 1** chia cho các CLB em có thi. Chỉ dùng để phá hoà khi hai em **bằng điểm thi**.
- **Quỹ 2** chia cho các CLB em không thi. Điểm cao hơn thì đứng trước; bằng điểm mới đến số bốc thăm.
- Quỹ nào chỉ có một CLB thì điền 100.

### Bật ở đâu

Màn **Không gian làm việc** → tạo mới → bước luật → ô **Dùng điểm quyết tâm** (hoặc chọn một mẫu đã bật sẵn).
Ô này chỉ dùng được khi cách xếp ưu tiên có điểm (Theo điểm, hoặc Nhóm trước rồi đến điểm) **và** điểm tính
riêng cho từng chỗ. Chọn "Chỉ theo nhóm" hoặc "Mỗi người một điểm duy nhất" thì ô tự khoá và bỏ chọn.

### Cột trong Sổ nhập và tệp CSV (chỉ khi đã bật)

| Tệp | Cột điểm quyết tâm |
|---|---|
| Sổ nhập | mỗi nhóm "Nguyện vọng k" có ba cột ở hàng 2: `CLB` · `Điểm thi` · `Điểm quyết tâm` (cột cuối ngay sau `Điểm thi`) |
| CSV nguyện vọng, dạng rộng | `wp_k` đi cặp `pref_k` |
| CSV nguyện vọng, cột theo buổi | `<buoi>_wp_k` đi cặp `<buoi>_pref_k` |
| CSV nguyện vọng, dạng dài | thêm cột `wp` cạnh `club_id` |

- Tệp **không có** các cột này thì nạp như cũ. Chưa bật mà tệp có các cột này thì chúng bị bỏ qua và phần mềm
  báo số ô đã bỏ.
- Nạp lại tệp cho một học sinh là **thay** mọi điểm quyết tâm cũ của em đó; em không có trong tệp thì giữ nguyên.
- Ô không phải số nguyên từ 0 trở lên (ví dụ `12,5`, `-3`, `abc`) bị báo và không lưu; các ô khác vẫn lưu.
- Nạp **không bị chặn** vì tổng chưa đủ 100: phần mềm chỉ cảnh báo. Việc chặn nằm ở bước chạy (xem dưới).
- Xuất "dữ liệu đầu vào" ra Sổ nhập rồi nạp lại thì điểm quyết tâm giống hệt.

### Học sinh chia điểm ở kiosk

Tab **Nhập tại chỗ** → chọn học sinh → **Bước 3. Điểm quyết tâm**. Mỗi buổi có hai khung (CLB đã thi, CLB không
thi); mỗi CLB một ô số và bộ đếm **Đã dùng X / 100**. Bấm **Lưu điểm quyết tâm**; chưa đủ 100 thì phần mềm báo còn
thiếu bao nhiêu ở quỹ nào và không lưu.

- Học sinh chỉ thấy điểm của chính mình: không có điểm chuẩn, độ đông hay điểm của bạn khác.
- Khung chỉ có một CLB thì ô tự điền 100 và khoá. Nếu em chưa bấm **Lưu**, lúc chạy xếp phần mềm vẫn tự điền 100 đó trong bộ nhớ (không ghi vào cơ sở dữ liệu), nên em không bị chặn chỉ vì chưa bấm Lưu; quỹ có từ hai CLB trở lên thì vẫn phải tự chia.
- Đổi ô tick thi ở Bước 1 **sau khi** đã chia điểm: điểm **không** tự chuyển sang quỹ kia. Khung hiện dòng
  *Cần chia lại điểm* và hồ sơ chưa hợp lệ cho tới khi chia lại.
- Bỏ một CLB khỏi nguyện vọng ở Bước 2 thì điểm đã đặt ở CLB đó bị xoá.
- Sau khi đã chạy xếp, điểm quyết tâm bị **khoá**: Bước 3 chỉ xem được, kèm dòng nhắc nhờ người quản lý mở khoá ở thẻ Quản lý (xem mục "Quản lý điểm quyết tâm" bên dưới).

### Quản lý điểm quyết tâm (thẻ Quản lý)

> **Thẻ Quản lý cần người giám sát máy.** Thẻ này không có mật khẩu: bảng điểm quyết tâm của cả khối, điểm chuẩn và nhật ký đều mở được từ máy kiosk. Hãy để máy kiosk dưới sự giám sát của giáo viên hoặc người phụ trách, không để học sinh ngồi một mình ở máy.

Khối **Điểm quyết tâm** chỉ hiện ở thẻ **Quản lý** khi không gian làm việc bật điểm quyết tâm; tắt thì thẻ Quản lý giống hệt như cũ. Thẻ Quản lý chia thành các **tab con**: *CLB*, *Học sinh*, *Điểm quyết tâm*, *Điểm chuẩn* và *Dữ liệu* (phần xoá dữ liệu). Hai tab điểm chỉ hiện khi bật điểm quyết tâm; tắt thì chỉ còn ba tab con. Khối này nằm ở tab con *Điểm quyết tâm*. Phần mềm nhớ tab con bạn vừa mở; chuyển tab bằng chuột hoặc phím mũi tên.

**Xem bảng điểm.** Mỗi dòng là một học sinh: điểm đã chia cho từng CLB, tách theo quỹ (Quỹ 1: CLB đã thi, Quỹ 2: CLB không thi) và theo buổi, kèm **Tổng** của từng quỹ (phải đúng 100). Ô được phần mềm tự điền 100 vì quỹ chỉ có một CLB thì ghi *tự điền*; ô chưa đặt hiện dấu —. Dùng ô tìm (gõ không dấu cũng được), các ô lọc Quỹ / Buổi / CLB và ô **Chỉ hồ sơ có vấn đề**; có phân trang. Dòng có vấn đề được tô viền đỏ và ghi *Chưa hợp lệ*, *Vắng thi* hoặc *Cần chia lại*.

**Đọc cảnh báo.** Phía trên bảng là danh sách **Hồ sơ cần xử lý**, chia hai nhóm: *Chưa chia đủ* (mọi lỗi sẽ chặn lần chạy xếp, như tổng khác 100) và *Vắng thi* (chỉ là cảnh báo, không chặn). Số liệu trùng với mục Cảnh báo dữ liệu ở thẻ Vận hành. Bấm vào một tên thì mở màn sửa của học sinh đó.

**Sửa điểm một học sinh.** Màn sửa có hai khung giống Bước 3 ở kiosk. Sửa xong bấm **Lưu điểm quyết tâm**; chưa đủ 100 thì phần mềm báo thiếu bao nhiêu ở quỹ nào và không lưu gì. Luật kiểm là đúng luật của kiosk.

**Xoá điểm.**
- Một học sinh: bấm **Xoá điểm của học sinh này** hai lần liên tiếp.
- Tất cả: bấm **Xoá điểm quyết tâm của tất cả học sinh**, gõ đúng chữ `XOA` rồi bấm xác nhận. Phần mềm tự sao lưu cơ sở dữ liệu trước khi xoá.

**Xử lý hàng loạt hồ sơ chia thiếu hoặc thừa.** Dưới danh sách *Hồ sơ cần xử lý* có hai nút:
- **Tải danh sách cần sửa:** tạo một tệp Excel liệt kê từng lỗi (mã, họ tên, buổi, quỹ, tổng hiện tại, thiếu hay thừa bao nhiêu, và câu lỗi). Nút này **không đổi điểm nào**.
- **Phóng cho đủ 100 theo tỉ lệ:** với mỗi học sinh chia thiếu hoặc thừa ở một quỹ, phần mềm **đổi điểm thay học sinh**: giữ tỉ lệ các điểm em đã đặt trong đúng quỹ đó và phóng cho tổng đúng 100 (làm tròn theo phần dư lớn nhất; hai CLB bằng phần dư thì CLB có mã nhỏ hơn được điểm lẻ; thứ hạng nguyện vọng không được dùng). Đây là thay đổi điểm của học sinh, nên cần gõ đúng chữ `PHONG` để xác nhận, phần mềm tự sao lưu trước, và mỗi thay đổi được ghi vào **Nhật ký thay đổi** (nguồn "thẻ Quản lý"). Học sinh chưa đặt điểm nào ở quỹ đó, hoặc còn lỗi khác (điểm ngoài nguyện vọng, cần chia lại, nguyện vọng chưa xếp xong) thì **không bị đổi** và được liệt kê lại để sửa tay. Đang khoá thì không phóng được.

**Khi chạy sắp xếp bị chặn vì hồ sơ điểm.** Thẻ Vận hành chỉ hiện một dòng tóm tắt, vài học sinh đầu (mỗi em một dòng gộp mọi lỗi của em) và nút **Mở danh sách cần xử lý**. Bấm nút để sang tab con *Điểm quyết tâm* với bộ lọc "chỉ hồ sơ có vấn đề" đã bật. Phần mềm vẫn kiểm đủ mọi học sinh, chỉ cách hiện gọn hơn.

**Vì sao bị khoá, và mở khoá.** Mỗi lần chạy xếp thành công khi bật điểm quyết tâm, điểm tự **khoá** để kết quả không đổi âm thầm sau đó. Khoá này riêng, không liên quan tới khoá số bốc thăm. Đang khoá thì không ghi được điểm ở đâu cả (thẻ Quản lý, Bước 3 ở kiosk, nạp cột điểm từ tệp; nạp tệp vẫn lưu nguyện vọng và cảnh báo rằng phần điểm bị bỏ). Việc xoá học sinh, xoá CLB, làm lại từ đầu hay xoá dữ liệu vẫn làm được. Muốn sửa: bấm **Mở khoá sửa điểm quyết tâm**, gõ đúng chữ `MO` rồi xác nhận. Kết quả đã xếp không tự đổi; lần chạy xếp tiếp theo sẽ khoá lại. Xoá dữ liệu (**Vùng nguy hiểm**) cũng mở khoá.

**Xem nhật ký.** Khi mở màn sửa của một học sinh, cuối màn là **Nhật ký thay đổi** của em đó (10 dòng mới nhất, bấm **Xem thêm** để xem tiếp): lúc nào, từ đâu (thẻ Quản lý, nhập tại chỗ, nạp tệp, xoá dữ liệu, hệ thống), tên tài khoản máy, và điểm trước và sau. Nhật ký chỉ ghi thêm, không bao giờ bị xoá hay sửa, kể cả khi xoá dữ liệu.

### Đọc điểm chuẩn và biểu đồ

Khi đã bật điểm quyết tâm và đã chạy xếp, quản trị xem được **điểm chuẩn** của từng CLB. Học sinh ở kiosk **không** thấy.

- **Tính thế nào.** Tính riêng cho từng CLB (và từng buổi), tách hai tầng và hai mức. Mức là suất thường hoặc suất dự trữ,
  theo đúng diện mà học sinh đã được nhận. **Tầng 2** (CLB không thi): điểm quyết tâm thấp nhất trong số em đã được nhận.
  **Tầng 1** (CLB có thi): điểm thi thấp nhất trong số em đã được nhận, kèm điểm quỹ 1 của chính em đó, ví dụ
  "8,25 điểm thi · 40 điểm quyết tâm". CLB còn chỗ thì ghi **0 (còn N chỗ)**. Ô "—": chưa có em nào ở tầng và mức đó.
- **Tab Kết quả.** Mục **Điểm chuẩn** luôn **đóng** mỗi lần vào thẻ; bấm **Xem điểm chuẩn** mới mở và hiện bảng tổng
  quan mọi CLB (thanh điểm chuẩn tầng 2, số đơn trên số chỗ, chấm đỏ khi đơn nhiều hơn chỗ). Phần mềm không nhớ trạng thái mở.
- **Tab Quản lý.** Khối **Điểm chuẩn** có bảng tổng quan, hộp chọn một CLB, bảng hai tầng x hai mức và hai biểu đồ:
  *cột phân bố* điểm quyết tâm của em tầng 2 (mỗi cột chia hai phần: được nhận là màu xanh, không được nhận là màu xám có
  gạch chéo) và *dải chấm* (mỗi em một chấm: đặc là được nhận, rỗng là không được nhận; di chuột hoặc chạm vào chấm để
  xem mã học sinh và điểm). Vạch đen dọc là mức chuẩn. Chỉ tính em đã thật sự xin vào CLB đó; em đã vào CLB xếp trước
  thì không tính (số em này được ghi bên dưới).
- Dải vàng "kết quả có thể đã cũ" hiện khi dữ liệu đã đổi sau lần chạy gần nhất.
- **Tệp xuất.** Sổ Excel kết quả có thêm trang **Điểm chuẩn** (mỗi CLB một dòng). Tắt điểm quyết tâm thì sổ xuất y như cũ.

### Khi nào lần chạy bị chặn

Ở bước **Kiểm tra dữ liệu**, trước khi bốc thăm: nếu hồ sơ của **bất kỳ** học sinh nào chưa hợp lệ (tổng khác 100,
điểm không phải số nguyên từ 0 trở lên, điểm đặt ở CLB không thuộc quỹ đó, nguyện vọng chưa xếp xong…), phần mềm
**không bốc thăm, không ghi gì**, và trả đủ danh sách: học sinh nào, quỹ nào, thiếu hay thừa bao nhiêu. Sửa xong thì
chạy lại. Mục **Cảnh báo dữ liệu** báo trước hai điều khi đã bật: số học sinh có hồ sơ chưa hợp lệ (mức cao, vì sẽ
chặn chạy) và số học sinh vắng thi (mức vừa).

### Cảnh báo vắng thi

Một học sinh tick thi CLB X và đặt điểm quỹ 1 cho X, nhưng đến lúc xếp không có điểm thi ở X. Khi đó X được xét như
CLB **không thi** của em: điểm quỹ 1 đã đặt cho X **không được tính**; nếu em có đặt điểm quỹ 2 cho X thì dùng điểm
đó, không có thì tính 0. Lần chạy vẫn tiếp tục; cảnh báo nằm trong chi tiết của bước Kiểm tra dữ liệu.

---

*Tài liệu này hướng dẫn vận hành phần mềm. Mọi nhận xét, diễn giải và kết luận về
kết quả phân bổ do người sử dụng tự viết.*
