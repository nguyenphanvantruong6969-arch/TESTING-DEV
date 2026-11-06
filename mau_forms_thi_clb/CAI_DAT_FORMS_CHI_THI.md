# Cài đặt Microsoft Forms (chế độ chỉ thi) cho "Đăng ký câu lạc bộ và thi tuyển — mẫu"

> **Tệp này do `tao_mau_forms.py --chi-thi` sinh từ `de_thi.json`.** Đừng sửa tay —
> sửa `de_thi.json` rồi chạy lại. Ghi chú cho giáo viên: `GHI_CHU_GIAO_VIEN.md`.

Biểu mẫu chỉ có **bài thi**: không có câu Ranking (nguyện vọng nằm ở ứng dụng đăng ký) và
không có ô gõ mã học sinh (Forms tự ghi **Name** và **Email** khi bật *Record name*).

Tổng **60 câu** (10 CLB có thi, mỗi CLB một câu cổng + các câu đề), trần Forms là 200 câu mỗi biểu mẫu → **1 biểu mẫu**.

## Biểu mẫu — Thứ Hai, Thứ Ba, Thứ Tư, Thứ Năm, Thứ Sáu (60 câu)

Tệp Quick Import: `NHAP_FORMS_CHI_THI.docx`.

### Bố cục

| Phần | Tên phần | Câu hỏi | Loại | Bắt buộc |
|---|---|---|---|---|
| 1 | Thứ Hai · Dự thi CLB Cờ vua | 1 · `[thi-clb_covua]` | Choice | ✅ |
| 2 | Thứ Hai · Đề thi CLB Cờ vua | 2 · `[clb_covua-1]` | Choice | ✅ |
|  |  | 3 · `[clb_covua-2]` | Choice | ✅ |
|  |  | 4 · `[clb_covua-3]` | Choice | ✅ |
|  |  | 5 · `[clb_covua-4]` | Choice | ✅ |
|  |  | 6 · `[clb_covua-5]` | Choice | ✅ |
| 3 | Thứ Hai · Dự thi CLB Văn học | 7 · `[thi-clb_vanhoc]` | Choice | ✅ |
| 4 | Thứ Hai · Đề thi CLB Văn học | 8 · `[clb_vanhoc-1]` | Choice | ✅ |
|  |  | 9 · `[clb_vanhoc-2]` | Choice | ✅ |
|  |  | 10 · `[clb_vanhoc-3]` | Choice | ✅ |
|  |  | 11 · `[clb_vanhoc-4]` | Choice | ✅ |
|  |  | 12 · `[clb_vanhoc-5]` | Choice | ✅ |
| 5 | Thứ Ba · Dự thi CLB Tiếng Anh | 13 · `[thi-clb_tienganh]` | Choice | ✅ |
| 6 | Thứ Ba · Đề thi CLB Tiếng Anh | 14 · `[clb_tienganh-1]` | Choice | ✅ |
|  |  | 15 · `[clb_tienganh-2]` | Choice | ✅ |
|  |  | 16 · `[clb_tienganh-3]` | Choice | ✅ |
|  |  | 17 · `[clb_tienganh-4]` | Choice | ✅ |
|  |  | 18 · `[clb_tienganh-5]` | Choice | ✅ |
| 7 | Thứ Ba · Dự thi CLB Mỹ thuật | 19 · `[thi-clb_mythuat]` | Choice | ✅ |
| 8 | Thứ Ba · Đề thi CLB Mỹ thuật | 20 · `[clb_mythuat-1]` | Choice | ✅ |
|  |  | 21 · `[clb_mythuat-2]` | Choice | ✅ |
|  |  | 22 · `[clb_mythuat-3]` | Choice | ✅ |
|  |  | 23 · `[clb_mythuat-4]` | Choice | ✅ |
|  |  | 24 · `[clb_mythuat-5]` | Choice | ✅ |
| 9 | Thứ Tư · Dự thi CLB Robotics | 25 · `[thi-clb_robotics]` | Choice | ✅ |
| 10 | Thứ Tư · Đề thi CLB Robotics | 26 · `[clb_robotics-1]` | Choice | ✅ |
|  |  | 27 · `[clb_robotics-2]` | Choice | ✅ |
|  |  | 28 · `[clb_robotics-3]` | Choice | ✅ |
|  |  | 29 · `[clb_robotics-4]` | Choice | ✅ |
|  |  | 30 · `[clb_robotics-5]` | Choice | ✅ |
| 11 | Thứ Tư · Dự thi CLB Khoa học | 31 · `[thi-clb_khoahoc]` | Choice | ✅ |
| 12 | Thứ Tư · Đề thi CLB Khoa học | 32 · `[clb_khoahoc-1]` | Choice | ✅ |
|  |  | 33 · `[clb_khoahoc-2]` | Choice | ✅ |
|  |  | 34 · `[clb_khoahoc-3]` | Choice | ✅ |
|  |  | 35 · `[clb_khoahoc-4]` | Choice | ✅ |
|  |  | 36 · `[clb_khoahoc-5]` | Choice | ✅ |
| 13 | Thứ Năm · Dự thi CLB Tin học | 37 · `[thi-clb_tinhoc]` | Choice | ✅ |
| 14 | Thứ Năm · Đề thi CLB Tin học | 38 · `[clb_tinhoc-1]` | Choice | ✅ |
|  |  | 39 · `[clb_tinhoc-2]` | Choice | ✅ |
|  |  | 40 · `[clb_tinhoc-3]` | Choice | ✅ |
|  |  | 41 · `[clb_tinhoc-4]` | Choice | ✅ |
|  |  | 42 · `[clb_tinhoc-5]` | Choice | ✅ |
| 15 | Thứ Năm · Dự thi CLB Âm nhạc | 43 · `[thi-clb_amnhac]` | Choice | ✅ |
| 16 | Thứ Năm · Đề thi CLB Âm nhạc | 44 · `[clb_amnhac-1]` | Choice | ✅ |
|  |  | 45 · `[clb_amnhac-2]` | Choice | ✅ |
|  |  | 46 · `[clb_amnhac-3]` | Choice | ✅ |
|  |  | 47 · `[clb_amnhac-4]` | Choice | ✅ |
|  |  | 48 · `[clb_amnhac-5]` | Choice | ✅ |
| 17 | Thứ Sáu · Dự thi CLB Toán tư duy | 49 · `[thi-clb_toan]` | Choice | ✅ |
| 18 | Thứ Sáu · Đề thi CLB Toán tư duy | 50 · `[clb_toan-1]` | Choice | ✅ |
|  |  | 51 · `[clb_toan-2]` | Choice | ✅ |
|  |  | 52 · `[clb_toan-3]` | Choice | ✅ |
|  |  | 53 · `[clb_toan-4]` | Choice | ✅ |
|  |  | 54 · `[clb_toan-5]` | Choice | ✅ |
| 19 | Thứ Sáu · Dự thi CLB Lịch sử | 55 · `[thi-clb_lichsu]` | Choice | ✅ |
| 20 | Thứ Sáu · Đề thi CLB Lịch sử | 56 · `[clb_lichsu-1]` | Choice | ✅ |
|  |  | 57 · `[clb_lichsu-2]` | Choice | ✅ |
|  |  | 58 · `[clb_lichsu-3]` | Choice | ✅ |
|  |  | 59 · `[clb_lichsu-4]` | Choice | ✅ |
|  |  | 60 · `[clb_lichsu-5]` | Choice | ✅ |

### Rẽ nhánh

Chọn câu cổng → **…** → **Add branching**. Đáp án **"Có, em làm bài thi ngay bây giờ"** để nguyên; đáp án **"Không"** đặt **Go to**:

| Câu cổng | "Không" → Go to |
|---|---|
| `[thi-clb_covua]` CLB Cờ vua | **Thứ Hai · Dự thi CLB Văn học** |
| `[thi-clb_vanhoc]` CLB Văn học | **Thứ Ba · Dự thi CLB Tiếng Anh** |
| `[thi-clb_tienganh]` CLB Tiếng Anh | **Thứ Ba · Dự thi CLB Mỹ thuật** |
| `[thi-clb_mythuat]` CLB Mỹ thuật | **Thứ Tư · Dự thi CLB Robotics** |
| `[thi-clb_robotics]` CLB Robotics | **Thứ Tư · Dự thi CLB Khoa học** |
| `[thi-clb_khoahoc]` CLB Khoa học | **Thứ Năm · Dự thi CLB Tin học** |
| `[thi-clb_tinhoc]` CLB Tin học | **Thứ Năm · Dự thi CLB Âm nhạc** |
| `[thi-clb_amnhac]` CLB Âm nhạc | **Thứ Sáu · Dự thi CLB Toán tư duy** |
| `[thi-clb_toan]` CLB Toán tư duy | **Thứ Sáu · Dự thi CLB Lịch sử** |
| `[thi-clb_lichsu]` CLB Lịch sử | **End of the form** |

### Đáp án và điểm (chế độ Quiz)

Quick Import **không mang đáp án**. Mỗi câu đề thi: bấm vào đáp án đúng → **Correct answer**,
ô **Points** = **2**. Câu cổng: không cho điểm. Bộ chuyển đổi **chấm lại** theo bảng này và
báo nếu điểm Forms lệch (tick nhầm).

**CLB Cờ vua** (`clb_covua`, Thứ Hai)

| Câu | Đáp án đúng |
|---|---|
| `[clb_covua-1]` Quân nào đi theo hình chữ L? | c. Mã |
| `[clb_covua-2]` Muốn nhập thành thì cần điều kiện nào? | a. Vua chưa từng di chuyển |
| `[clb_covua-3]` Tốt đi tới hàng cuối cùng của bàn cờ thì sao? | b. Được phong thành quân khác (trừ Vua) |
| `[clb_covua-4]` Trường hợp nào ván cờ là HOÀ? | b. Bên tới lượt không còn nước đi hợp lệ và không bị chiếu |
| `[clb_covua-5]` Ký hiệu O-O nghĩa là gì? | a. Nhập thành cánh Vua |

**CLB Văn học** (`clb_vanhoc`, Thứ Hai)

| Câu | Đáp án đúng |
|---|---|
| `[clb_vanhoc-1]` Truyện Kiều là tác phẩm của ai? | a. Nguyễn Du |
| `[clb_vanhoc-2]` Câu “Mặt trời xuống biển như hòn lửa” dùng biện pháp tu từ nào? | a. So sánh |
| `[clb_vanhoc-3]` Mỗi cặp câu thơ lục bát gồm những câu nào? | a. Một câu 6 chữ và một câu 8 chữ |
| `[clb_vanhoc-4]` Tiểu thuyết Tắt đèn là của ai? | b. Ngô Tất Tố |
| `[clb_vanhoc-5]` Kể theo ngôi thứ nhất thì người kể xưng là gì? | a. Tôi |

**CLB Tiếng Anh** (`clb_tienganh`, Thứ Ba)

| Câu | Đáp án đúng |
|---|---|
| `[clb_tienganh-1]` She ___ to school every day. | b. goes |
| `[clb_tienganh-2]` Từ trái nghĩa với “ancient” là gì? | a. modern |
| `[clb_tienganh-3]` I have lived here ___ 2020. | a. since |
| `[clb_tienganh-4]` If it rains tomorrow, we ___ at home. | a. will stay |
| `[clb_tienganh-5]` Câu nào đúng ngữ pháp? | b. He doesn't like tea. |

**CLB Mỹ thuật** (`clb_mythuat`, Thứ Ba)

| Câu | Đáp án đúng |
|---|---|
| `[clb_mythuat-1]` Ba màu cơ bản trong hội hoạ truyền thống là gì? | a. Đỏ, vàng, lam |
| `[clb_mythuat-2]` Màu bổ túc của màu đỏ là màu nào? | b. Lục |
| `[clb_mythuat-3]` Luật xa gần giúp bức tranh có điều gì? | c. Cảm giác chiều sâu |
| `[clb_mythuat-4]` Tranh dân gian Đông Hồ thường in trên loại giấy nào? | a. Giấy điệp |
| `[clb_mythuat-5]` Pha màu lam với màu vàng thì được màu gì? | d. Lục |

**CLB Robotics** (`clb_robotics`, Thứ Tư)

| Câu | Đáp án đúng |
|---|---|
| `[clb_robotics-1]` Cảm biến siêu âm trên robot dùng để làm gì? | b. Đo khoảng cách |
| `[clb_robotics-2]` Vòng lặp trong lập trình dùng để làm gì? | a. Lặp lại một nhóm lệnh |
| `[clb_robotics-3]` Động cơ servo khác động cơ DC thường ở điểm nào? | c. Điều khiển được góc quay chính xác |
| `[clb_robotics-4]` Robot tránh vật cản đo được khoảng cách dưới 10 cm thì nên làm gì? | c. Dừng lại hoặc rẽ hướng khác |
| `[clb_robotics-5]` Arduino là gì? | a. Bo mạch vi điều khiển |

**CLB Khoa học** (`clb_khoahoc`, Thứ Tư)

| Câu | Đáp án đúng |
|---|---|
| `[clb_khoahoc-1]` Ở áp suất tiêu chuẩn, nước sôi ở bao nhiêu độ C? | b. 100 |
| `[clb_khoahoc-2]` Cây xanh tạo chất hữu cơ nhờ ánh sáng qua quá trình nào? | c. Quang hợp |
| `[clb_khoahoc-3]` Đơn vị đo lực là gì? | a. Niutơn (N) |
| `[clb_khoahoc-4]` Khí nào chiếm tỉ lệ lớn nhất trong không khí? | d. Nitơ |
| `[clb_khoahoc-5]` Trong thí nghiệm, “biến kiểm soát” là gì? | a. Yếu tố giữ nguyên để so sánh công bằng |

**CLB Tin học** (`clb_tinhoc`, Thứ Năm)

| Câu | Đáp án đúng |
|---|---|
| `[clb_tinhoc-1]` 1 byte bằng bao nhiêu bit? | b. 8 |
| `[clb_tinhoc-2]` Hệ nhị phân dùng những chữ số nào? | a. 0 và 1 |
| `[clb_tinhoc-3]` Số nhị phân 101 bằng bao nhiêu trong hệ thập phân? | b. 5 |
| `[clb_tinhoc-4]` Thuật toán là gì? | c. Dãy hữu hạn các bước để giải một bài toán |
| `[clb_tinhoc-5]` Mật khẩu nào mạnh nhất? | d. T0i#Hoc!2026 |

**CLB Âm nhạc** (`clb_amnhac`, Thứ Năm)

| Câu | Đáp án đúng |
|---|---|
| `[clb_amnhac-1]` Có bao nhiêu tên nốt nhạc cơ bản? | b. 7 |
| `[clb_amnhac-2]` Một nốt tròn dài bằng mấy nốt đen? | c. 4 |
| `[clb_amnhac-3]` Ký hiệu # trong bản nhạc gọi là gì? | a. Dấu thăng |
| `[clb_amnhac-4]` Nhịp 3/4 có ý nghĩa gì? | a. Mỗi ô nhịp 3 phách, mỗi phách là một nốt đen |
| `[clb_amnhac-5]` Bài Tiến quân ca do ai sáng tác? | b. Văn Cao |

**CLB Toán tư duy** (`clb_toan`, Thứ Sáu)

| Câu | Đáp án đúng |
|---|---|
| `[clb_toan-1]` Số tiếp theo của dãy 2, 4, 8, 16 là gì? | d. 32 |
| `[clb_toan-2]` Lớp có 30 học sinh, 40% là nữ. Lớp có bao nhiêu bạn nữ? | b. 12 |
| `[clb_toan-3]` Tổng ba góc trong một tam giác bằng bao nhiêu? | b. 180° |
| `[clb_toan-4]` Ba bạn bắt tay nhau, mỗi cặp bắt đúng một lần. Có bao nhiêu cái bắt tay? | b. 3 |
| `[clb_toan-5]` Số nguyên tố nhỏ nhất là số nào? | c. 2 |

**CLB Lịch sử** (`clb_lichsu`, Thứ Sáu)

| Câu | Đáp án đúng |
|---|---|
| `[clb_lichsu-1]` Chiến thắng Điện Biên Phủ diễn ra năm nào? | b. 1954 |
| `[clb_lichsu-2]` Ngô Quyền đánh thắng quân Nam Hán trên sông nào? | c. Sông Bạch Đằng |
| `[clb_lichsu-3]` Chủ tịch Hồ Chí Minh đọc Tuyên ngôn Độc lập vào ngày nào? | b. 2/9/1945 |
| `[clb_lichsu-4]` Vua Quang Trung đại phá quân Thanh vào năm nào? | b. 1789 |
| `[clb_lichsu-5]` Bình Ngô đại cáo do ai viết? | c. Nguyễn Trãi |

## Settings (mọi biểu mẫu)

| Cài đặt | Giá trị | Vì sao |
|---|---|---|
| Who can fill out this form | **Only people in my organization** | Học sinh đăng nhập tài khoản trường |
| **Record name** | **BẬT** | Cột **Email** của tệp xuất là khoá ghép với danh sách đăng ký; không bật thì không biết bài của ai |
| **One response per person** | **BẬT** | Đây là bài thi: nộp lại là làm lại. Bộ chuyển đổi cũng chỉ giữ phiếu **đầu** của mỗi email |
| Shuffle questions | **TẮT** | Xáo câu là hỏng rẽ nhánh |
| Shuffle options (từng câu đề thi) | Bật được | Chấm theo nội dung lựa chọn, không theo vị trí |
| Show results automatically (Quiz) | **TẮT** | Bật là em làm trước biết đáp án, chuyền cho em làm sau |
| Start date / End date | Đặt đủ cả hai | Hết giờ tự khoá, không phải canh |
