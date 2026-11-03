# T3. Nghiên cứu giảm rối giao diện (debloat)

> **Dữ liệu trong mọi ảnh và số liệu dưới đây là MÔ PHỎNG** (sổ mẫu trong `du_lieu_test/`, tên và điểm do máy sinh). Không phải khảo sát hay học sinh có thật.
> Phạm vi: chỉ nghiên cứu, không sửa mã, chữ, giao diện hay test. Ngày chạy: 2026-11-03, nhánh `claude/epic-knuth-801pkw`, chế độ trình duyệt dự phòng (`browser_host.py`), Chromium 1280x800.
> Giao diện đã đối chiếu với HEAD `bfb340f` (các tệp `index.html`, `i18n.js`, `js/*.js` không đổi so với lúc chụp). Bản sửa vòng 1 (theo phản hồi của người kiểm) đã đối chiếu lại mã tại HEAD này.
> Quy ước chữ trong tệp này: không gạch dài, không đại từ nhân xưng. Khi cần trích chữ cũ có vi phạm, gạch dài được ghi là `⟨gạch dài⟩` và đại từ được ghi là `⟨đại từ⟩`.

## 0. Lỗi sản phẩm phát hiện khi khảo sát (ưu tiên cao hơn mọi đề xuất giao diện)

Ba mục dưới đây là lỗi hành vi hoặc lỗi chữ hướng dẫn, không phải chuyện thẩm mỹ. Chúng nên được đăng ký thành mã mục riêng (quy tắc 1 trong `CLAUDE.md`) trước khi làm các đề xuất gọn giao diện.

| # | Lỗi | Tái hiện | Mức | Cách sửa gợi ý |
|---|---|---|---|---|
| B1 | **Mất dữ liệu khi sửa CLB qua biểu mẫu** (T3-26) | Có CLB `clb_k` (chỉ tiêu 10, suất dự trữ 4, nhóm `chinh_sach`, buổi `thu_2`). Ở thẻ Quản lý, chỉ điền Mã, Tên, chỉ tiêu 20 rồi bấm "Lưu CLB". Kết quả trong CSDL: chỉ tiêu 20, suất dự trữ 0, nhóm trống, buổi về `__mac_dinh__`. Đã tái hiện lại ở vòng 1 bằng `create_or_update_club` (cùng hàm mà `js/05_quan_ly.js` dòng 1172 gọi, truyền cả sáu giá trị, ô trống thành giá trị rỗng) | **cao, mất dữ liệu im lặng** | Bấm dòng thì điền sẵn biểu mẫu từ dòng đó; và/hoặc chỉ gửi trường đã đổi; hiện nhãn thường trực cho sáu ô. Cần test mới cho "sửa chỉ tiêu không xoá suất dự trữ, nhóm, buổi" |
| B2 | **Chạy khi chưa có học sinh làm ghi lịch sử và khoá số bốc thăm ngoài ý muốn** (T3-01) | Workspace mới, bấm "Chạy sắp xếp" khi 0 học sinh: ghi thêm một dòng `run_history`, khoá `stb` seed 42 (`is_locked = 1`). Chạy tiếp với seed khác (`run_pipeline(seed=7)`) trả `{ok: false, errors: [hat_giong_da_khoa {cu: 42, moi: 7}]}` cho tới khi bấm "Bốc thăm lại" | vừa đến cao | Khoá nút "Chạy sắp xếp" khi 0 học sinh hoặc 0 CLB, kèm câu giải thích. An toàn với bất biến 3 và 4 (chỉ chặn trước khi chạy, không đổi cơ chế khoá hay ghi lịch sử) |
| B3 | **Câu lỗi chỉ việc giao diện không làm được** (T3-42) | `wharton_ho_so_chua_hop_le` (`i18n_errors.py` dòng 602) bảo "tắt Dùng điểm quyết tâm trong cấu hình không gian làm việc", nhưng công tắc đó chỉ có trong trình hướng dẫn tạo mới (`js/075_workspace.js` dòng 652), không có `update_workspace_config` nào được gọi từ `js/` và tab Điểm quyết tâm không có công tắc | vừa | Hoặc thêm công tắc (cần xác nhận hai bước vì chạm A13.13 và bất biến 1), hoặc đổi câu lỗi trỏ tới việc làm được: "Phóng cho đủ 100 theo tỉ lệ" ở Quản lý, tab Điểm quyết tâm |

Ngoài ra có một lỗi hiển thị nằm giữa lỗi và đề xuất: tên buổi lưu dạng mã (`thu_2`) và hiện nguyên mã ở nhiều nơi, kể cả khi Sổ nhập ghi "Thứ 2" (T3-14).

## 1. Cách làm (để Truong biết nguồn của từng nhận xét)

- Dựng máy chủ `browser_host.serve` trên bản sao workspace trong thư mục tạm (không đụng `app.db` thật), điều khiển bằng Playwright.
- Đóng vai bốn người dùng: (a) giáo viên chạy lần đầu, (b) thành viên BGH chỉ cần xem kết quả, (c) nhân viên kiosk thêm học sinh đến muộn, (d) quản trị đổi chỉ tiêu hoặc suất dự trữ. Thêm: bộ chuyển không gian làm việc, trình hướng dẫn tạo mới, đổi ngôn ngữ, chân thanh bên.
- Chụp mọi thẻ ở 1280x800 (chỉ giữ 11 ảnh được dẫn, thư mục `docs/nghien_cuu/anh_t3/`).
- Kiểm chữ bằng máy: tách 688 chuỗi `vi` trong `i18n.js`, 236 thông báo lỗi `vi` trong `i18n_errors.py`, 302 chuỗi tĩnh và 59 thuộc tính trong `index.html`, 43 chuỗi chữ Việt trong `js/*.js`, và toàn bộ chữ hiện trên màn hình lúc chạy; dò gạch dài, gạch ngang dài vừa, và các đại từ bị cấm bằng khớp biên từ.
- Những việc CHƯA đo, ghi rõ để không nhầm: không đo thời gian thao tác thật của người dùng thật; số cú bấm dưới đây là đếm từ chính các lần chạy thử; chưa mở từng thẻ con của 8 thẻ thu gọn ở thẻ 03 để so từng ô (chỉ so bằng ảnh `a11`); việc ô để trống ở biểu mẫu CLB ghi đè nhãn dự trữ cũ đã được tái hiện ở vòng 1 (mục 0, B1).
- Không có màn hình "Cài đặt" riêng trong bản này (không có khoá nào tên cài đặt trong `i18n.js`). Phần cài đặt thực tế chỉ gồm nút `EN`/`VI`, nút hiệu ứng, và hộp chọn không gian làm việc.

Nguyên tắc dùng để chấm (viết gọn):

| Ký hiệu | Nguyên tắc | Nguồn ý tưởng |
|---|---|---|
| P1 | Mỗi màn một việc chính, nút chính duy nhất, các việc phụ lùi xuống | trang chủ Google |
| P2 | Tiết lộ dần: chi tiết chỉ hiện khi người dùng hỏi | iPhone, Cài đặt |
| P3 | Nhận ra thay vì nhớ: nhãn nhìn thấy được, không bắt gõ lại mã | nguyên tắc dễ dùng của Nielsen |
| P4 | Chữ thường: không để thuật ngữ nội bộ (RB-DA, STB, seed, mã CLB, mã buổi) lên màn người dùng trường học | iPhone dùng không cần hướng dẫn |
| P5 | Mặc định đúng: người dùng không phải quyết định điều mà phần mềm đã biết | iPhone |
| P6 | Ít phần tử hơn nhưng mạnh hơn: mỗi số, biểu đồ, thẻ phải trả lời một câu hỏi người dùng thật sự có | trang chủ Google |
| P7 | Nhất quán: một khái niệm một tên, cùng tên với tệp Excel mà người dùng điền | |

## 2. Tóm tắt: mười thay đổi xếp theo tác động chia công sức

0. **Mục 0 trước hết**: B1 mất dữ liệu khi sửa CLB (T3-26), B2 chạy 0 học sinh khoá seed (T3-01), B3 câu lỗi chỉ việc không làm được (T3-42). Rồi mười thay đổi:
1. **Chặn bấm "Chạy sắp xếp" khi chưa có học sinh nào** và thôi báo màu xanh "Dữ liệu đã sẵn sàng" lúc trống (T3-01, S). Đã tái hiện: chạy với 0 học sinh vẫn bốc thăm và khoá số bốc thăm.
2. **Rút kết quả nhập sổ về một dòng + nút xử lý** khi sổ thiếu cột Điểm quyết tâm (T3-02, M). Hiện là 120 dòng cảnh báo y hệt nhau và một lỗi nghiêm trọng không chỉ chỗ sửa; sổ `SO_NHAP_TEST.xlsx` và `bo_sach/SO_NHAP_SACH.xlsx` vào là kẹt.
3. **Quản lý CLB: bấm vào dòng để sửa, hiện nhãn thường trực cho 6 ô** (T3-26, M). Hiện bấm dòng không làm gì; sửa chỉ tiêu phải gõ lại mã CLB.
4. **Kết quả: mở sẵn kiểu xem có dữ liệu, bỏ cột "Thứ tự", đặt nút tải Excel ngay trong thẻ** (T3-16, T3-17, T3-18; S đến M).
5. **Thu "Các bước xử lý" thành một dòng kết quả có nút "Chi tiết"**, giữ nguyên bước khi đang chạy và khi lỗi (T3-06, M).
6. **Thẻ 03 "Dữ liệu khác": bỏ hoặc gộp các thẻ trùng** (T3-20, T3-21, T3-22, M): mức lấp đầy trùng bảng theo CLB, danh sách xếp trùng thẻ 02, điểm chuẩn có hai lối vào.
7. **Đổi tên thẻ và mô tả cho người không có hướng dẫn** (mục 5, S): "Vận hành sắp xếp", "Nhập tại chỗ", "Quản lý CLB & dự trữ". Riêng tên "Dữ liệu khác" do Truong đặt ở T2 nên cần Truong quyết định.
8. **Sửa vi phạm quy tắc chữ** (mục 6, S): trình hướng dẫn tạo mới, tiêu đề cửa sổ, hai khoá khoảng số, và bảy chữ dự phòng cũ trong `index.html`.
9. **Nhập tại chỗ: đưa biểu mẫu "học sinh mới" lên cạnh ô tìm, tự cuộn tới phiếu, bỏ ô Lớp lặp, bỏ mã thô bên phải mỗi CLB** (T3-32 đến T3-35, M).
10. **Trình hướng dẫn tạo không gian làm việc từ mẫu: một bước, nút "Tạo"**; các bước 2 và 3 chỉ mở khi chọn "Tuỳ chỉnh" (T3-11, M). Kèm: gom nút phụ ở chân thanh bên (T3-12, S).

## 3. Bảng phát hiện

Cột "Loại": thừa, phức tạp, khó hiểu, chữ (vi phạm quy tắc chữ), bước (bước có thể cắt). Cột Công sức: S dưới nửa ngày, M 1 đến 2 ngày, L hơn 2 ngày. Cột Rủi ro nêu test hoặc bất biến chạm tới; "BB" là bất biến trong `CLAUDE.md`.

### 3.1. Thẻ 01 Vận hành sắp xếp

| ID | Màn hình/thẻ | Vị trí chính xác | Vấn đề (người dùng gặp) | Loại | Đề xuất cụ thể | Tác động | Công sức | Rủi ro |
|---|---|---|---|---|---|---|---|---|
| T3-01 | 01, cả trang trống (ảnh `a01`) | `index.html` `#healthSummary`, `#btnRun`; `js/02_van_hanh.js` (khối hiển thị sức khoẻ dữ liệu) | Workspace mới: ô Cảnh báo ghi xanh "Không thấy vấn đề nào. Dữ liệu đã sẵn sàng." trong khi 0 học sinh, 0 CLB. Nút "Chạy sắp xếp" bấm được. Đã bấm thử: kết quả "Sắp xếp xong: 0/0", bước Bốc thăm ghi "Đã bốc thăm cho 0 học sinh và khoá kết quả bốc thăm". Đây là UX cộng với khoá số bốc thăm ngoài ý muốn: có thêm một dòng `run_history`, seed 42 bị khoá, các lần chạy sau với seed khác bị từ chối (`hat_giong_da_khoa`) cho tới khi bấm "Bốc thăm lại" (mục 0, B2) | bước, khó hiểu | Khi `statStudents` = 0 hoặc `statClubs` = 0: khoá `#btnRun` và thay dòng xanh bằng "Chưa có dữ liệu. Nhập Sổ nhập CLB ở khung bên trên." Không đổi pipeline | cao | S | BB3 và BB4 không chạm (chỉ chặn trước khi chạy); test chạm: test giao diện 01 nếu có kiểm nút khi trống |
| T3-02 | 01, sau khi nhập sổ thiếu cột Điểm quyết tâm (ảnh `a02`) | `index.html` `#importWarnings`, `#healthList`; `js/02_van_hanh.js` (dựng danh sách cảnh báo nhập); quy tắc ở `cau_hinh_ws.py` (`rules.wharton` mặc định bật) | Nhập `du_lieu_test/SO_NHAP_TEST.xlsx` (120 học sinh) hoặc `bo_sach/SO_NHAP_SACH.xlsx` (140 học sinh) vào workspace mới: ô kết quả nhập in 120 (hoặc 140) dòng gần như giống nhau "Chưa dùng hết điểm quyết tâm: học sinh HS001 còn thiếu 100 điểm ở quỹ 1", rồi ô Cảnh báo ghi "NGHIÊM TRỌNG ... lần chạy xếp sẽ bị chặn cho tới khi sửa xong". Lời báo không chỉ chỗ sửa. Đường ra có thật nhưng nằm xa: thẻ Quản lý, tab Điểm quyết tâm có "Phóng cho đủ 100 theo tỉ lệ" (`#btnWhPhong`) và "Tải danh sách cần sửa" (`#btnWhTaiCanSua`); khung cảnh báo không dẫn tới đó. (Việc chặn là quyết định có chủ ý ở A13.13; vấn đề chỉ là cách báo.) | khó hiểu, thừa | (1) Gộp danh sách theo loại: một dòng "120 học sinh chưa chia đủ 100 điểm quyết tâm" + nút "Xem 5 dòng đầu". (2) Câu nghiêm trọng thêm liên kết nhảy tới Quản lý, tab Điểm quyết tâm, nơi có `#btnWhPhong`: "Chưa chạy được: 120 học sinh chưa chia đủ điểm quyết tâm. Mở Quản lý, mục Điểm quyết tâm, bấm \"Phóng cho đủ 100 theo tỉ lệ\"." (3) Giới hạn 5 dòng chỉ áp dụng cho cảnh báo thường, KHÔNG áp dụng cho lỗi chặn chạy (lỗi chặn luôn hiện, có thể dưới dạng đếm). Việc tắt tính năng sau khi đã tạo workspace là một mục riêng (T3-42) | cao | M | BB1 và A13.13 không đổi (chỉ đổi cách hiển thị); test chạm: `test_wharton_mac_dinh_bat.py` nếu ghim câu chữ, `test_wharton_*` giao diện |
| T3-03 | 01, khung Nhập dữ liệu | `index.html` `#btnImportAll`, `#btnClearQueue`; `i18n.js` `import_hint` | Hai nút "Nhập sổ" (màu chính) và "Bỏ tệp" hiện ngay khi chưa chọn tệp nào, tranh nút chính với "Chạy sắp xếp". Câu hướng dẫn dài 3 mệnh đề | thừa, khó hiểu | Ẩn `#importActions` đến khi có tệp trong hàng chờ (đã có dòng xem trước "Sẵn sàng nhập: 10 CLB · 1 buổi · 120 học sinh ..."; giữ dòng này, nó có giá trị). Rút `import_hint` xuống một câu (xem mục 5) | vừa | S | test giao diện nhập (`test_giao_dien_a13_12_nhap.py`) có thể tìm nút khi chưa có tệp |
| T3-04 | 01, hai nút kiểm tra | `index.html` `#btnHealthRecheck` ("Kiểm tra lại", khung Cảnh báo) và `#btnValidate` ("Kiểm tra dữ liệu", khung Các bước xử lý); `js/02_van_hanh.js` dòng 428 và 465 | Hai nút cùng ý nghĩa nhìn từ ngoài, cách nhau một khung. Đã đối chiếu mã ở vòng 1: `#btnValidate` gọi `check_data_integrity` rồi `loadHealthReport`; `#btnHealthRecheck` chỉ gọi `loadHealthReport`. Hai việc khác nhau nhưng người dùng không thấy khác biệt | thừa | Gộp: để một nút duy nhất "Kiểm tra lại dữ liệu" chạy cả kiểm tra toàn vẹn và nạp lại báo cáo sức khoẻ (không xoá thẳng `#btnValidate`, vì mất bước kiểm toàn vẹn) | vừa | S | test bấm `#btnValidate` theo id; BB5 (kiểm dữ liệu trong pipeline) không đổi vì đây là nút kiểm riêng ngoài pipeline |
| T3-05 | 01, ô số bốc thăm | `index.html` `#seedInput`, `#stbLockLine`, `#seedLockHint`; `i18n.js` `seed_locked_hint`, `seed_unlocked_for_redraw` | Ô "Số khởi tạo bốc thăm 42" luôn hiện trên đầu khung chạy; sau lần chạy đầu có HAI dòng nói cùng một ý (dòng "Số bốc thăm đã khoá từ ... " và dòng chữ đơn cách "Số khởi tạo 42 được khoá cùng số bốc thăm. Muốn đổi, bấm Bốc thăm lại"). "Số khởi tạo" là thuật ngữ kỹ thuật (seed) | khó hiểu, thừa | Ẩn `#seedInput` trong mục "Nâng cao" thu gọn (mặc định 42, nhập được như cũ). Giữ một dòng sau khi khoá: "Đã bốc thăm lúc 03/11/2026 03:18. Muốn bốc thăm lại, bấm "Bốc thăm lại..."." Xoá `#seedLockHint` | cao | S | BB3 không đổi (chỉ ẩn hiển thị); test chạm: test seed giao diện đọc `#seedInput` theo id |
| T3-06 | 01, khung Các bước xử lý (ảnh `a03`) | `index.html` danh sách bước; `i18n.js` `step_title_*`, `step_done_default`; `js/02_van_hanh.js` | Sáu bước nội bộ (Sao lưu, Kiểm tra, Bốc thăm, Xếp, Lưu, Xuất) với dòng chi tiết như tên tệp sao lưu `app.db.bak-20261103_031845_590311` và đường dẫn đầy đủ tệp CSV. Giáo viên chỉ cần biết "xong chưa, kết quả đâu". Cùng thông tin "88/120" lặp ở 4 nơi: dải số liệu, toast, dòng Chạy gần nhất ở chân thanh bên, và khung bước | thừa, phức tạp | Sau khi chạy xong thành công: thu cả 6 bước thành một dòng "Xong: 88/120 học sinh đã có CLB." + nút "Mở thư mục kết quả" + nút "Chi tiết" (mở lại 6 bước). Giữ nguyên danh sách bước khi đang chạy và khi có lỗi hoặc hoàn tác. Bỏ toast trùng nội dung | cao | M | BB5 giữ nguyên (chỉ đổi cách hiển thị, thứ tự bước không đổi); test chạm: test giao diện bước (`test_giao_dien_*` đọc `.step`) |
| T3-07 | 01, chọn buổi (ảnh `a03`) | `index.html` `#chonBuoiBox`, `#chonBuoiTu`, `#chonBuoiDen`; `js/02_van_hanh.js` `veChonBuoiDai`, `i18n.js` mô tả "Sắp xếp lại tất cả các buổi trong tuần." | Để chọn buổi có ba cơ chế cùng lúc: hai hộp thả "Từ" và "đến", các chip, và liên kết "Chọn tất cả". Mã buổi in thô `thu_2` (xem T3-14) | phức tạp, thừa | Giữ chip (bấm để bật hoặc tắt) và liên kết "Chọn tất cả"; bỏ hai hộp Từ/đến. Chỉ hiện khung này khi workspace có từ 2 buổi trở lên (đã đúng, giữ) | vừa | S đến M | `test_giao_dien_a13_12_*` có thể thao tác hộp Từ/đến |
| T3-08 | 01, dải số liệu và chân thanh bên | `index.html` `#statusStrip`; `i18n.js` `label_submitted_prefs`; `#lastRunLine` | "đã nộp nguyện vọng" bằng đúng số học sinh trong mọi sổ mẫu đã chạy (120 và 120). Ô Chạy gần nhất ở chân thanh bên in giờ dạng máy `2026-11-03T03:18:45` và "số khởi tạo 42" | thừa, khó hiểu | Bỏ ô "đã nộp nguyện vọng" khỏi dải (còn: học sinh, CLB, đã xếp CLB). Định dạng giờ `03/11/2026 03:18` (giống hộp chọn không gian làm việc, hiện đã dùng dạng này). Bỏ "số khởi tạo" khỏi `#lastRunLine` | thấp | S | test đọc `#statPrefs` theo id |
| T3-09 | 01, thẻ Lịch sử sắp xếp | `index.html` thẻ "Lịch sử sắp xếp" + nút "Hiện/ẩn" | Sau lần chạy đầu thẻ chỉ có tiêu đề và liên kết "Hiện/ẩn", thân rỗng | thừa | Chỉ hiện thẻ khi có từ 2 lần chạy; hoặc ghi sau tiêu đề "1 lần". Không đụng `run_history` (BB4 chỉ về dữ liệu) | thấp | S | thấp |
| T3-10 | 01, bố cục tổng | toàn `#view-pipeline` | Năm khung xếp dọc (dải số, Nhập dữ liệu, Cảnh báo, Các bước xử lý, Lịch sử) và bốn nút màu chính hoặc tương đương (Tải sổ nhập mẫu, Nhập sổ, Kiểm tra dữ liệu, Chạy sắp xếp) hiện cùng lúc. Người dùng không biết bước kế tiếp là gì (P1) | phức tạp | Theo trạng thái: chưa có dữ liệu thì chỉ nổi bật khung Nhập dữ liệu và khung Cảnh báo/Các bước thu gọn; có dữ liệu chưa chạy thì nổi bật "Chạy sắp xếp"; chạy xong thì nổi bật một dòng kết quả (T3-06). Mỗi lúc đúng một nút màu chính | cao | M | thấp, thuần hiển thị |

### 3.2. Thanh bên, không gian làm việc, trình hướng dẫn

| ID | Màn hình/thẻ | Vị trí chính xác | Vấn đề | Loại | Đề xuất cụ thể | Tác động | Công sức | Rủi ro |
|---|---|---|---|---|---|---|---|---|
| T3-11 | Hộp "Tạo không gian làm việc mới" (ảnh `a10`) | `js/075_workspace.js` (`ws_wz_*`, hàm dựng bước ở dòng 544) ; `i18n.js` `ws_wz_*` | Bốn bước kể cả khi chọn mẫu "Trường học" (mẫu đã điền sẵn cả bốn bước): nhập tên, Tiếp, Tiếp, Tiếp, Tạo = 5 cú bấm. Bước 3 "Luật xếp" có 10 ô gồm các từ như "Thứ hạng nhóm nghiêm ngặt", "Phạm vi của điểm", "Suất dự trữ mềm". Bước 4 "Xem lại" lặp lại các lựa chọn vừa chọn, kể cả dòng "Thứ tự các nhóm ... ⟨gạch dài⟩" trống | phức tạp, bước | Khi chọn mẫu có sẵn: bước 1 có nút "Tạo" ngay (2 cú bấm), kèm liên kết "Tuỳ chỉnh từ vựng và luật" để vào bước 2 và 3. Bỏ bước "Xem lại" (hoặc chỉ hiện khi đã vào tuỳ chỉnh). Ẩn dòng tóm tắt không áp dụng | cao | M | `tests/test_ws_giao_dien.py` (đã đi từng bước), `test_giao_dien_a13_12_ws.py`; BB1 không chạm |
| T3-12 | Chân thanh bên (ảnh `a03`, `a07`) | `index.html` `#btnMotionToggle`, `#dbStatusLine`, `#lastRunLine`, `#cheDoHienThi` | Bốn dòng chữ nhỏ trên mọi màn: "Hiệu ứng: bật" (nút), "Đã kết nối dữ liệu", "Chạy gần nhất ...", "Chế độ dự phòng (trình duyệt)". Hai dòng cuối chỉ có nghĩa với người sửa máy, không phải giáo viên | thừa, khó hiểu | Chỉ hiện `#dbStatusLine` khi mất kết nối hoặc lỗi (giữ cảnh báo an toàn, xem mục 8); bỏ `#cheDoHienThi` (hoặc để trong chú giải khi di chuột); bỏ `#lastRunLine` (đã có ở thẻ 03); đưa nút hiệu ứng vào một nút `⋯` cạnh `EN`. Nếu giữ nút hiệu ứng, đổi nhãn "Hiệu ứng: bật" thành "Hoạt ảnh: bật" cho đúng nghĩa chuyển động | vừa | S | `test_giao_dien_*` đọc các id này |
| T3-13 | Thanh trên cùng của thanh bên | `index.html` `.brand-sub`; `i18n.js` `brand_sub`, `page_title` | Dòng phụ "Reserve-Based DA" và tiêu đề tab trình duyệt "... · RB-DA" là tên thuật toán, không có nghĩa với giáo viên (P4) | khó hiểu | `brand_sub`: bỏ dòng. `page_title`: "Sắp xếp {slot}" | thấp | S | `test_i18n_*` ghim chuỗi |
| T3-14 | Toàn bộ nơi hiện tên buổi (kết quả, kiosk, quản lý) | `js/05_quan_ly.js` hàm `nhanBuoi` (dòng 48 đến 51, được gọi 27 lần trong `js/`); `so_nhap.py` dòng 70 đến 71 và hàm chuẩn hoá ở dòng 221 trở đi (đổi "Thứ 2" thành `thu_2`) và dòng 248 (đã có chiều ngược lại `thu_2` thành "Thứ 2"); `style.css` (tiêu đề cột viết hoa, chữ đơn cách ở thẻ 05) | Sổ nhập ghi "Thứ 2", "Thứ 4", "Thứ 6" (đã kiểm `du_lieu_test/SO_NHAP_MAU_120HS_3BUOI.xlsx`), nhưng khi nạp, buổi được lưu thành mã `thu_2`, `thu_4`, `thu_6`, và `nhanBuoi` trả lại đúng mã đó. Nên giáo viên và BGH thấy `THU_2` ở tiêu đề cột thẻ 02, `thu_2` ở thẻ 04 và 05. Sửa file mẫu không giúp gì: lỗi nằm ở phần hiển thị, không phải ở dữ liệu mẫu. Mã CLB `clb_coking` cũng hiện ở thẻ 04, 05, 06 | khó hiểu | (1) Sửa `nhanBuoi`: ánh xạ mã sang nhãn hiển thị (`thu_2` thành "Thứ 2", ..., `chu_nhat` thành "Chủ nhật"; mã lạ giữ nguyên chữ người dùng đã nhập), tái dùng bảng ánh xạ ngược có sẵn ở `so_nhap.py` hoặc giữ nhãn gốc lúc nhập. (2) Bỏ viết hoa tự động ở tiêu đề cột buổi. (3) Không hiện cột "Mã CLB" và mã `clb_*` ở thẻ 04 và 06; giữ mã ở thẻ 05 trong cột thu hẹp vì quản trị cần phân biệt CLB trùng tên | cao | M | Chạm cột buổi ở T2 (thẻ 02) nên `test_giao_dien_t2_ket_qua.py` đọc tiêu đề cột; không đổi dữ liệu lưu (BB7 không chạm); các test đọc `thu_2` trên giao diện phải đổi có chủ ý |
| T3-15 | Hộp chọn không gian làm việc (ảnh `a09`) | `js/075_workspace.js` (bảng danh sách); `i18n.js` `ws_*` | Mỗi dòng có sáu hành động chữ liền kề (Mở, Đổi tên, Nhân bản, Lưu thành mẫu, Xuất tệp nén, Xoá) và cột "Loại", "Sửa lần cuối", mã thư mục `khoi-11` in phụ. "Nhập tệp nén", "Xuất tệp nén" khó hiểu với người không quen | phức tạp, khó hiểu | Mỗi dòng: nút "Mở" + nút `⋯` chứa phần còn lại (Xoá đứng cuối, màu đỏ). Bỏ cột Loại khi chỉ có một loại. Ẩn mã thư mục. Đổi "Xuất tệp nén" thành "Sao lưu ra tệp ZIP", "Nhập tệp nén" thành "Khôi phục từ tệp ZIP", "Lưu thành mẫu" thành "Lưu làm mẫu" | vừa | M | `test_ws_giao_dien.py`, `test_giao_dien_a13_12_ws.py` tìm nút theo chữ |

### 3.3. Thẻ 02 Kết quả

| ID | Màn hình/thẻ | Vị trí chính xác | Vấn đề | Loại | Đề xuất cụ thể | Tác động | Công sức | Rủi ro |
|---|---|---|---|---|---|---|---|---|
| T3-16 | 02, cảnh vào đầu (ảnh `a05` có lớp; xem thêm ảnh chụp lúc chưa có lớp) | `index.html` `#kqTang1`; `js/03_ket_qua.js` (khôi phục lựa chọn đã nhớ) | Mặc định "Theo lớp". Với sổ chưa có cột Lớp (cả hai sổ mẫu lớn trong `du_lieu_test/` đều thế), thẻ mở ra một ô trống "Chưa có lớp (120)" và câu "Chưa có lớp nào. Hãy nhập cột Lớp trong Sổ nhập hoặc sửa ở thẻ ...". Người của BGH, chỉ muốn xem kết quả, vào đúng ngõ cụt | khó hiểu, bước | **Truong quyết định** (thiết kế T2 của Truong có ba lựa chọn tầng 1). Phương án giữ nguyên thiết kế: khi dữ liệu chưa có lớp nào, mặc định tầng 1 là "Theo mã học sinh" và vẫn giữ ba nút. Phương án gọn hơn: ẩn thêm nút "Theo lớp" và mục "Theo lớp" ở hàng sắp xếp khi chưa có lớp nào, chỉ hiện khi có ít nhất một lớp | cao | S | `test_giao_dien_t2_ket_qua.py` (khẳng định ba nút luôn có, dòng 40 trở xuống) phải đổi có chủ ý |
| T3-17 | 02, hàng "Sắp xếp" cấp 2 | `index.html` `#kqTang2`; `i18n.js` `kq_sap_nhan`, `kq_sx_ngay`, `kq_sx_ma`, `kq_sx_lop` | Ba nút xếp thứ hai nằm dưới ba nút xem. "Theo ngày trong tuần" khó hiểu vì các cột của bảng vốn đã là các ngày; không rõ sắp xếp theo gì. BGH phải đọc thêm một hàng điều khiển trước khi thấy dữ liệu. (Truong đã chọn thiết kế hai tầng ở T2, nên đây là đề xuất để Truong quyết định.) | phức tạp | Phương án nhẹ: bỏ hàng `#kqTang2`; mặc định theo mã học sinh; bấm vào tiêu đề cột để sắp xếp (kiểu bảng tính, người dùng đã quen). Nếu muốn giữ: đổi "Sắp xếp" thành "Xếp theo:" và "Theo ngày trong tuần" thành "Theo CLB mỗi ngày"; thu vào một hộp thả một dòng | vừa | M | `test_giao_dien_t2_ket_qua.py` (nhiều ca về tầng 2); có `localStorage` `rbda_ket_qua_xem_v1` |
| T3-18 | 02, bảng kết quả (ảnh `a05`) | `js/03_ket_qua.js` (dựng `#kqThan`), `i18n.js` `th_stt` (dòng 211) | Cột "Thứ tự" 1, 2, 3 ... là số dòng, không phải thông tin của học sinh; thêm một cột phải đọc | thừa | **Truong quyết định** (cột nằm trong thiết kế T2). Nếu duyệt: bỏ cột "Thứ tự". Giữ dòng đếm "30 học sinh · 7 chưa có chỗ" phía trên (có giá trị) | thấp | S | `test_giao_dien_t2_ket_qua.py` đọc `r.children[1]` (cột 2) theo vị trí, phải sửa chỉ số cột |
| T3-19 | 02 và 03, đường xuất tệp | `index.html` khung `Xuất dữ liệu` ở thẻ 03; thẻ 02 không có nút xuất | Người BGH xem xong kết quả muốn tải bảng đang thấy phải sang thẻ 03 và đọc năm ô tích. Thẻ 02 không có nút nào | bước | Thêm một nút "Tải bảng này (Excel)" ở góc thẻ 02, xuất đúng lớp/CLB đang chọn. Giữ khung xuất đầy đủ ở thẻ 03 | cao | M | BB6 (hợp đồng `{ok, data, errors}`), cần API xuất theo khung nhìn hoặc dùng `Xuất theo lớp` có sẵn |

### 3.4. Thẻ 03 Dữ liệu khác

| ID | Màn hình/thẻ | Vị trí chính xác | Vấn đề | Loại | Đề xuất cụ thể | Tác động | Công sức | Rủi ro |
|---|---|---|---|---|---|---|---|---|
| T3-20 | 03, thẻ "Danh sách xếp CLB" (ảnh `a04`, `a11`) | `index.html` thẻ `results_list_title`; `js/03_ket_qua.js` | Danh sách 138 dòng (mỗi dòng một cặp học sinh và CLB) cùng bộ lọc tìm, lớp, sắp xếp, đánh dấu chọn. Về nội dung trùng với thẻ 02 (cùng thông tin xếp học sinh vào CLB, cũng có bộ lọc lớp). Thêm cột "Loại chỗ" và "Hạng nguyện vọng" nên có thêm giá trị cho người kiểm tra | thừa | Giữ làm phần "Kiểm tra chi tiết" cho người vận hành, nhưng bỏ thẻ khỏi khung nhìn mặc định: đưa vào một mục "Chi tiết để kiểm tra" thu gọn cuối thẻ 03. Công dụng chọn học sinh để xuất hồ sơ (xem T3-23) giữ nguyên | vừa | S | `test_giao_dien_*` mở thẻ này theo id |
| T3-21 | 03, thẻ "Mức lấp đầy của từng CLB" và "Theo từng câu lạc bộ" (ảnh `a11`) | `js/03_ket_qua.js` (hai bộ dựng) | Hai thẻ liệt kê đúng cùng các CLB, cùng chỗ và cùng tỉ lệ chọi (cùng thấy "2,21×" ở cả hai). Thẻ trên là thanh ngang, thẻ dưới là bảng. Thanh ngang chỉ hiện ý tưởng "đầy hay trống", trong khi bảng đã có số | thừa | Gộp: một bảng "Theo từng CLB" thêm một cột thanh nhỏ (hoặc bỏ thanh). Bỏ thẻ "Mức lấp đầy". Ghi chú "Rê chuột ... Nhãn bên phải chỉ ra CLB cần để ý" là chú giải chỉ hiện khi rê chuột, trong máy cảm ứng và máy kiosk không dùng được; đưa thông tin đó thành cột chữ thường | vừa | M | `tests/test_giao_dien_bieu_do.py` (đoạn mã đã nhắc ở `js/03_ket_qua.js`), `test_giao_dien_lap_day_*` |
| T3-22 | 03 và 05, hai lối vào Điểm chuẩn (ảnh `a04`, `a06`) | `index.html` thẻ Điểm chuẩn ở 03 (nút `dc_xem`) và tab `#qlTabDc` ở 05 | Cùng một màn Điểm chuẩn có hai lối vào: một nút "Xem điểm chuẩn" trong thẻ có thân rỗng ở 03, và tab "Điểm chuẩn" ở 05. Thẻ ở 03 khi chưa mở chỉ có một tiêu đề và một nút | thừa | Giữ một nơi. Gợi ý: thẻ 03 (là kết quả, không phải quản lý); bỏ `#qlTabDc` khỏi thẻ 05 | vừa | S | `test_giao_dien_a13_12_ql_diem_chuan.py` |
| T3-23 | 03, khung "Xuất dữ liệu" (ảnh `a04`) | `index.html` khung `xuat_title`; `i18n.js` `xuat_opt_*`, `xuat_hint_*` | Năm ô tích (một ô lồng nhau), hai nút, và ba dòng chú thích (Xuất theo lớp, Hồ sơ học sinh, cảnh báo đỏ) trong một khung. Câu "Hồ sơ học sinh: bấm "Chọn học sinh..." rồi đánh dấu ... Đang mở một học sinh ở thẻ 04 thì bấm ..." nhắc số thẻ, dễ sai khi đổi thứ tự thẻ. Câu "đổ số liệu vào phần mềm khác" là khẩu ngữ | phức tạp | Mặc định chỉ hai nút: "Xuất kết quả (Excel)" và "Xuất theo lớp". Các ô tích khác nằm trong "Tuỳ chọn khác" thu gọn. Chú thích hồ sơ học sinh rút thành một câu, không nhắc số thẻ. Giữ nguyên cảnh báo đỏ (xem mục 7) | cao | M | `test_giao_dien_*xuat*`, `test_export_ket_qua.py` đọc các ô theo id |
| T3-24 | 03, năm ô số ở đầu (ảnh `a04`) | `index.html` `#view-others` thẻ `tom_tat_title`; `i18n.js` `tom_tat_*` | Năm ô số. "Suất dự trữ bỏ phí 0/9 Ổn" và "Được nguyện vọng 1: 63%, 100% trong 3 nguyện vọng đầu" là thuật ngữ nội bộ. Ô "Học sinh chưa có chỗ 32 Cần xử lý" mới là con số người dùng hành động | khó hiểu, thừa | Giữ ba ô: "Đã có CLB 88/120", "Chưa có CLB 32" (bấm vào để xem danh sách, màu cảnh báo), "Chỗ còn trống". Chuyển hai ô còn lại vào thẻ chi tiết tương ứng (CHUYỂN, không xoá: "Được nguyện vọng 1" và "trong 3 nguyện vọng đầu" là con số chính của báo cáo đề tài, xem mục 7) | vừa | S | `test_giao_dien_lap_day_*` hoặc test ô số |
| T3-25 | 03, bảng "Theo từng câu lạc bộ" | `js/03_ket_qua.js` | Tiêu đề cột "SỐ HỌC SINH ĐĂNG KÝ", "ĐẶT NGUYỆN VỌNG 1", "TỈ LỆ CHỌI" (hai dòng chữ dài, bị ngắt). "Tỉ lệ chọi" không phải từ thường dùng cho giáo viên | khó hiểu | "Số đăng ký", "Chọn là nguyện vọng 1", "Học sinh trên mỗi chỗ" | thấp | S | `th_*` trong test chữ |

### 3.5. Thẻ 05 Quản lý và các tab con

| ID | Màn hình/thẻ | Vị trí chính xác | Vấn đề | Loại | Đề xuất cụ thể | Tác động | Công sức | Rủi ro |
|---|---|---|---|---|---|---|---|---|
| T3-26 | 05 tab Câu lạc bộ (ảnh `a07`) | `index.html` `#clubFormId`, `#clubFormName`, `#clubFormCapacity`, `#clubFormReserveCapacity`, `#clubFormReserveGroup`, `#clubFormBuoi`, `#btnSaveClub`; `js/05_quan_ly.js` (bảng dòng 499, gọi API dòng 1172) | **Lỗi mất dữ liệu (mục 0, B1), mức cao.** (1) Bấm vào một dòng của bảng không điền vào biểu mẫu (đã thử: sáu ô vẫn trống), nên muốn đổi chỉ tiêu phải gõ lại mã CLB chính xác; gõ sai mã tạo CLB mới. (2) Biểu mẫu luôn gửi cả sáu giá trị: CLB `clb_k` (chỉ tiêu 10, suất dự trữ 4, nhóm `chinh_sach`, buổi `thu_2`) sau khi chỉ điền Mã, Tên, Tổng chỗ 20 rồi "Lưu CLB" còn lại (20, 0, trống, `__mac_dinh__`): suất dự trữ, nhóm ưu tiên và buổi bị xoá im lặng. (3) Sáu ô chỉ có chữ gợi ý; khi ô đã có giá trị (như ô "0" thứ tư) chữ gợi ý biến mất nên không biết ô đó là gì | phức tạp, bước, lỗi dữ liệu | Hiện nhãn thường trực phía trên mỗi ô (Mã, Tên, Chỉ tiêu, Suất ưu tiên, Nhóm ưu tiên, Buổi). Bấm dòng thì điền biểu mẫu từ dòng đó (hoặc sửa tại chỗ ô chỉ tiêu). Mã CLB của dòng đang sửa thì khoá. Chỉ gửi trường đã đổi, hoặc gửi giá trị cũ cho ô không đụng tới. Thêm test "sửa chỉ tiêu không xoá suất dự trữ, nhóm, buổi" | cao | M | BB7 không chạm (không đổi cột CSV); `test_giao_dien_*quan_ly*` điền biểu mẫu theo id |
| T3-27 | 05 tab Câu lạc bộ, thuật ngữ | `i18n.js` `admin_title`, `admin_desc`, nhãn cột, `placeholder_reserve_capacity` | Giao diện nói "Suất dự trữ", "Nhãn dự trữ", "Tổng chỗ"; Sổ nhập Excel mà người dùng điền (sheet `1. CLB`) ghi "Chỉ tiêu", "Suất ưu tiên", "Nhóm ưu tiên". Cùng khái niệm, hai tên (P7). Trình hướng dẫn tạo mới lại dùng "Nhóm ưu tiên" | khó hiểu | Dùng đúng từ của Sổ nhập ở mọi nơi trên giao diện: Chỉ tiêu, Suất ưu tiên, Nhóm ưu tiên. Đổi tên thẻ 05 thành "Quản lý CLB" (mục 5) | cao | M | `tests/test_ws_nhan.py` (danh sách chuỗi cho phép), nhiều test chữ vi; BB6 không đổi |
| T3-28 | 05, hai khối về buổi (ảnh `a07`) | `i18n.js` `admin_tai_buoi_title`, `admin_lich_tuan_title`; `js/05_quan_ly.js` (dòng 104, 138) | "Tải theo buổi" (bảng) và "Lịch tuần" (cột) cùng nói về tải mỗi buổi (cùng "46 · 2,3×"). Trong mẫu cả ba buổi đều gắn nhãn đỏ "Quá tải" nên nhãn mất tác dụng phân biệt. Lịch tuần có thanh mức lấp đầy mỗi CLB, ở mẫu tất cả đều đầy | thừa | Gộp thành một bảng "Tải theo buổi", bỏ khối "Lịch tuần" (hoặc để làm biểu đồ phụ khi bấm một buổi). "Tỉ lệ chọi 2.3×" đổi thành "2,3 học sinh trên mỗi chỗ" (dấu phẩy thập phân đã dùng ở nơi khác) | vừa | M | `test_giao_dien_*lich*` |
| T3-29 | 05 tab Điểm quyết tâm (ảnh dài, 25 dòng mỗi trang) | `index.html` `#qlPanelWh` | 120 học sinh, mỗi dòng 4 đến 9 dòng chữ "Quỹ 1 CLB ...: 67 CLB ...: 33 Tổng 100"; trang cao hơn 4400 px ở 1280 px rộng. Người quản trị cần xem hồ sơ có vấn đề chứ không đọc từng học sinh | phức tạp | Mặc định bật bộ lọc "Chỉ hồ sơ có vấn đề" (hộp đã có sẵn) và hiện số lượng ("0 hồ sơ cần xử lý"); bảng đầy đủ sau một nút "Xem tất cả" | vừa | S | `test_giao_dien_wharton_quan_ly.py` |
| T3-30 | 05 tab "Dữ liệu" (ảnh trong thư mục tạm, không đính kèm) | `i18n.js` `ql_tab_du_lieu`; khối "Vùng nguy hiểm" | Tên tab "Dữ liệu" mơ hồ (toàn phần mềm là dữ liệu); nội dung là xoá. Câu giải thích dài 3 câu | khó hiểu | Đổi tên tab thành "Xoá dữ liệu". Giữ nguyên hai nút đỏ và các bước xác nhận (xem mục 7) | vừa | S | `ql_tab_du_lieu` trong test chữ |
| T3-31 | 05 tab Điểm chuẩn (ảnh `a06`) | `js/05_quan_ly.js` hoặc `js/03_ket_qua.js` (biểu đồ điểm chuẩn, `dc_*`) | Một màn dùng bốn kiểu trực quan để trả lời "điểm thấp nhất để vào CLB này": thanh điểm hai thang, thanh xếp chồng ba màu với ba mức chữ ("Đủ chỗ", "Đông", "Rất đông"), bảng chi tiết hai hàng, và biểu đồ chấm 0 đến 100 có ba mục chú giải. Ở mẫu cả 9 CLB đều "Rất đông" nên mức này không phân biệt gì. Hai đoạn chú giải dài ("Thanh dài là điểm thấp nhất..." và "Đủ chỗ: ... Đông: ... Rất đông: ...") | phức tạp, thừa | Mặc định chỉ một bảng: CLB, điểm thi chuẩn, điểm quyết tâm chuẩn, số đơn trên số chỗ (bằng số). Đưa biểu đồ chấm sang "Xem chi tiết" của một CLB (nó trả lời "ai suýt đỗ", hữu ích cho người nghiên cứu hơn người trực kiosk). Bỏ thanh xếp chồng ba màu và ba mức chữ. Nếu giữ: gộp hai đoạn chú giải thành một chú thích | vừa | M | `test_giao_dien_a13_12_ql_diem_chuan.py`, `test_giao_dien_a13_10_diem_chuan.py`, `test_giao_dien_bieu_do.py` |

### 3.6. Thẻ 04 Nhập tại chỗ và thẻ 06 Nhập điểm

| ID | Màn hình/thẻ | Vị trí chính xác | Vấn đề | Loại | Đề xuất cụ thể | Tác động | Công sức | Rủi ro |
|---|---|---|---|---|---|---|---|---|
| T3-32 | 04, vị trí biểu mẫu học sinh mới (ảnh `a08`) | `index.html` `#newStudentId`, `#newStudentName`, `#newStudentLop`, `#btnCreateStudent` | Ô tìm ở trên cùng, nhưng biểu mẫu "Mã học sinh mới / Họ tên / Chọn lớp / Tạo học sinh mới" nằm dưới danh sách 8 phiếu (khoảng 1030 px từ đầu trang), sau đó phiếu nhập của học sinh vừa tạo hiện dưới nữa (khoảng 1100 px), nhân viên phải tự cuộn gần 900 px | bước, phức tạp | Đưa biểu mẫu "Học sinh mới" thành một hàng cạnh ô tìm (hoặc một nút "+ Học sinh mới" mở hàng này). Sau khi tạo hoặc chọn học sinh: tự cuộn đến phiếu và thu danh sách lại | cao | M | `test_giao_dien_a14_lop.py` (đã dựng sẵn quy trình tạo học sinh và chọn lớp) |
| T3-33 | 04, ô Lớp xuất hiện hai lần (ảnh `a08`) | `index.html` `#newStudentLop` và `#kioskLop` | Nhân viên chọn lớp ở hàng tạo ("Chọn lớp..."), rồi thấy lại một ô "Lớp" trong phiếu vừa mở | thừa | Chọn lớp một lần ở hàng tạo; phiếu chỉ hiển thị lớp (chỉ cho sửa khi bấm vào) | vừa | S | `test_giao_dien_a14_lop.py` có ca "tạo học sinh mới phải chọn lớp và gửi lớp" |
| T3-34 | 04, đầu phiếu học sinh (ảnh `a08`) | `index.html` `#btnXuatEmNay`, `#btnResetStudentEntry`, `#btnDeleteStudent` | Ba nút phụ ngang hàng với tên học sinh: "Xuất CSV học sinh này", "Sửa lại từ đầu", "Xoá học sinh". "Xuất CSV" thuộc về việc xuất; "Sửa lại từ đầu" không nói rõ xoá cái gì | thừa, khó hiểu | Gom vào một nút `⋯`: "Xoá nguyện vọng của học sinh này" (thay cho "Sửa lại từ đầu") và "Xoá học sinh" (xác nhận hai bước đã có). Bỏ "Xuất CSV học sinh này" khỏi phiếu (đã có ở thẻ 03). Nếu Truong muốn giữ lối xuất theo ngữ cảnh thì giữ nó trong `⋯` | vừa | S | `test_giao_dien_a14_*`, `test_giao_dien_a13_12_nhap.py` tìm `#btnXuatEmNay` |
| T3-35 | 04, hai bước (ảnh `a08`) | `index.html` bước 1 và 2; `i18n.js` `fallback_step1_title`, `fallback_step2_hint` | Phía phải mỗi CLB ở bước 1 in mã thô (`clb_coking`), ở bước 2 in mã buổi. Có hai nút Lưu riêng (Lưu CLB dự thi, Lưu nguyện vọng) và câu "Hai bước này không phụ thuộc nhau." (người đọc tự hỏi nghĩa là gì) | thừa, khó hiểu | Bỏ mã thô; ở bước 1 nhóm theo buổi như bước 2. Bỏ câu "Hai bước này không phụ thuộc nhau." Giữ hai nút Lưu riêng (xem mục 7: xoá điểm khi bỏ chọn CLB dự thi), nhưng đặt chấm "Chưa lưu" nổi hơn | vừa | S đến M | `test_giao_dien_*nhap*`, `fallback_chua_luu` giữ nguyên |
| T3-36 | 06 Nhập điểm, bảng tiến độ | `js/06_cham_diem.js`, `i18n.js` `scoring_overview_title` | Cột "MÃ CLB" (`clb_bcs`) và "THAO TÁC" chữ in hoa nhỏ; "Chấm →" (có mũi tên, mỗi dòng một liên kết). Tiến độ "60/60" có giá trị; mã CLB không | thừa | Bỏ cột mã CLB; nút "Chấm" rõ ràng thành nút phụ; thanh nhỏ tiến độ không cần | thấp | S | thấp |

### 3.7. Quy tắc chữ (chi tiết ở mục 6)

| ID | Màn hình/thẻ | Vị trí chính xác | Vấn đề | Loại | Đề xuất cụ thể | Tác động | Công sức | Rủi ro |
|---|---|---|---|---|---|---|---|---|
| T3-37 | Hộp tạo không gian làm việc, tiêu đề bước | `js/075_workspace.js` dòng 544 | Ghép chuỗi `t("ws_wz_buoc") + " ⟨gạch dài⟩ " + tenBuoc` nên màn hình hiện "Bước 1/4 ⟨gạch dài⟩ Thông tin chung" ở cả bốn bước | chữ | Đổi dấu nối thành ": " (cách khác là "Bước 1/4. Thông tin chung") | cao (hiện trên màn ở mỗi bước) | S | `test_ws_giao_dien.py` có thể đọc chuỗi này |
| T3-38 | Tiêu đề cửa sổ và nhãn trợ năng | `js/075_workspace.js` dòng 117 (tiêu đề cửa sổ), 602 và 606 (aria-label); `main.py` hàm `tieu_de_cua_so`; `js/04_nhap_tai_cho.js` dòng 748 (aria-label) | Dấu nối gạch dài trong "<tên chỗ xếp> ⟨gạch dài⟩ <tên workspace>" ở tiêu đề cửa sổ và nhãn đọc màn hình | chữ | Đổi thành " · " hoặc ": " (nhãn trợ năng dùng ": ") | thấp | S | `test_*cua_so*`, `test_a13_12_windows.py` có thể ghim tiêu đề |
| T3-39 | Hai khoá khoảng số ở trình hướng dẫn | `i18n.js` `ws_r_max_choices`, `ws_r_max_tests` | Chữ "(1⟨gạch nối⟩20)" và "(0⟨gạch nối⟩20)" dùng gạch ngang dài vừa (en dash) giữa hai số | chữ | "(từ 1 đến 20)" và "(từ 0 đến 20)" | thấp | S | `test_ws_nhan.py` nếu ghim |
| T3-40 | Chữ dự phòng cũ trong `index.html` | `index.html` dòng 309 (`ket_qua_cu_banner`), 330 (`xuat_theo_lop_hint`), 332 (`xuat_hint_hoc_sinh`), 333 và 774 (`xuat_canh_bao_diem`), 564 (`hien_ca_em_chua_xep`), 621 (`btn_xuat_em_nay`) | Bản dự phòng trong HTML còn gạch dài và đại từ "⟨đại từ⟩", lệch với catalog (catalog `i18n.js` đã sạch). Chỉ hiện khi tải chữ thất bại, nhưng lệch nguồn là mầm lỗi | chữ | Đổi các chữ này cho khớp catalog, hoặc xoá chữ dự phòng, chỉ để khoá `data-i18n` | thấp | S | `test_i18n_sync`/test chữ vi |
| T3-41 | Ký tự "⟨gạch dài⟩" làm ô trống | khắp thẻ 03, 05 (bảng nhãn dự trữ, điểm chuẩn, kết quả chưa có) | Một gạch dài đơn lẻ dùng làm "ô trống" (ví dụ cột Nhãn dự trữ, cột điểm). Không phải câu văn nên không thuộc quy tắc "mô tả", nhưng cùng ký tự bị cấm ở chữ mô tả; người đọc thấy không nhất quán | chữ | Truong quyết định: nếu cấm tuyệt đối, đổi ô trống thành dấu gạch nối ngắn "-" (đã dùng ở thẻ 02 cho ô không có CLB) để một kiểu duy nhất | thấp | S | nhiều test đọc ký tự trong ô (ký tự gạch dài); cần quét trước |
| T3-42 | 01 và 05, bật hoặc tắt Điểm quyết tâm sau khi đã tạo workspace | `js/075_workspace.js` dòng 652 (`wzWharton`, chỉ có trong trình hướng dẫn); `js/*.js` không gọi `update_workspace_config`; `i18n_errors.py` dòng 602 (`wharton_ho_so_chua_hop_le`) | Không có công tắc Điểm quyết tâm ở nơi nào sau khi tạo workspace; tab Điểm quyết tâm của thẻ 05 không có mục bật hoặc tắt. Câu lỗi lại bảo "tắt Dùng điểm quyết tâm trong cấu hình không gian làm việc": chỉ một việc giao diện không làm được (mục 0, B3) | khó hiểu, bước | Cách 1: thêm công tắc ở tab Điểm quyết tâm, có xác nhận hai bước vì đổi cách xếp (A13.13). Cách 2 (nhẹ hơn): sửa câu lỗi trỏ tới việc làm được, "Phóng cho đủ 100 theo tỉ lệ" ở Quản lý, tab Điểm quyết tâm, rồi sinh lại bằng `tao_i18n_js.py` | vừa | S (cách 2) hoặc M (cách 1) | BB1, A13.13, BB6 (một nguồn thông báo lỗi `i18n_errors.py`); test chạm: `test_i18n_sync.py` |
| T3-43 | Tệp Excel xuất cho BGH và giáo viên chủ nhiệm | `api_xuat.py` (chữ ghi trong tệp, xem mục 6.2) | Các trang chú thích, tiêu đề và dòng "rỗng" trong tệp Excel có gạch dài và đại từ ⟨đại từ⟩ (hàng chục dòng, ví dụ "Số ⟨đại từ⟩ đã có {slot_l}", "Chưa có chỗ" kèm gạch dài). BGH và giáo viên chủ nhiệm đọc đúng các tệp này, nên quy tắc chữ cần giữ nghiêm nhất ở đây | chữ | Viết lại các chuỗi theo mục 6.2: bỏ gạch dài, dùng nhãn học sinh theo từ vựng workspace ({person_l}) thay cho ⟨đại từ⟩ | cao | M | `tests/test_export_ket_qua.py`, `test_a14_lop_xuat.py` và các test đọc tệp Excel xuất ghim câu chữ |

## 4. Đường đi của bốn người dùng (số cú bấm hiện tại và sau đề xuất)

Số cú bấm tính từ lúc mở phần mềm, không tính thao tác ngoài phần mềm (điền Excel) và không tính gõ phím.

| Người dùng | Mục tiêu | Hiện tại | Chỗ vướng đã gặp | Sau đề xuất |
|---|---|---|---|---|
| (a) Giáo viên chạy lần đầu | Tạo không gian, nhập sổ, chạy, xuất | Tạo mới: bấm bộ chuyển, "Tạo mới", gõ tên, Tiếp x3, Tạo = 6 cú bấm. Nhập: bấm ô thả tệp, "Nhập sổ" = 2. Chạy = 1. Sang thẻ 03 = 1, "Xuất các mục đã chọn" = 1. **Tổng 11.** Nếu sổ thiếu cột Điểm quyết tâm: kẹt ở bước chạy, không có đường ra (T3-02) | Tạo mới 4 bước (T3-11). Danh sách 120 dòng cảnh báo. "Số khởi tạo", "Bốc thăm lại" khó hiểu (T3-05). Sáu bước nội bộ (T3-06). Phải sang 03 để xuất (T3-19) | Tạo mới: bộ chuyển, "Tạo mới", gõ tên, "Tạo" = 3. Nhập: thả tệp, "Nhập sổ" = 2. Chạy = 1. Nút "Tải kết quả Excel" ngay dòng kết quả ở 01 = 1. **Tổng 7**, và có đường ra khi sổ thiếu điểm |
| (b) Thành viên BGH | Xem kết quả một lớp rồi tải | Mở thẻ 02 = 1, nếu chưa có lớp thì chọn "Theo mã học sinh" = 1, hoặc chọn lớp = 1. Tải: thẻ 03 = 1, "Xuất theo lớp" = 1. **Tổng 4 đến 5** | Mở vào ngõ cụt khi chưa có lớp (T3-16). Hai hàng điều khiển trước khi thấy bảng (T3-17). Cột "Thứ tự" thừa (T3-18) | Mở thẻ 02 = 1 (vào thẳng chế độ có dữ liệu), chọn lớp = 1, "Tải bảng này" = 1. **Tổng 3** |
| (c) Nhân viên kiosk, học sinh đến muộn | Thêm một học sinh, nhập nguyện vọng | Thẻ 04 = 1, cuộn xuống đáy (~1000 px), gõ mã, gõ tên, chọn lớp = 1, "Tạo học sinh mới" = 1, cuộn xuống tiếp (~900 px), chọn lớp lần hai trong phiếu (nếu thấy) = 1, bước 1: tích N CLB thi + "Lưu CLB dự thi" = N+1, bước 2: bấm xếp hạng M lần + "Lưu nguyện vọng" = M+1. **Tổng 6 + N + M + cuộn hai lần** | Biểu mẫu nằm đáy (T3-32). Lớp hai lần (T3-33). Mã thô bên phải (T3-35) | Thẻ 04 = 1, gõ mã, tên ngay hàng trên cùng, chọn lớp = 1, "Tạo" = 1, phiếu tự cuộn vào tầm nhìn, N+1, M+1. **Tổng 5 + N + M, không cuộn tay.** Sau đó chạy lại bằng một liên kết "Chạy lại" ngay trong dải nhắc "Dữ liệu đã được sửa sau lần chạy gần nhất" (xem mục 7, giữ dải nhắc) |
| (d) Quản trị, đổi chỉ tiêu một CLB | Tăng chỉ tiêu CLB Cờ tướng từ 16 lên 20 | Thẻ 05 = 1, **bấm dòng không có tác dụng** (đã thử), gõ lại mã `clb_coking` + tên + chỉ tiêu mới, "Lưu CLB" = 1. **Tổng 2 cú bấm + gõ 3 ô, gõ sai mã tạo CLB mới.** Nếu CLB có suất dự trữ phải gõ đủ sáu ô (chưa kiểm ô trống có xoá dữ liệu cũ không) | Bấm dòng không điền biểu mẫu, ô không nhãn (T3-26) | Thẻ 05 = 1, bấm dòng hoặc ô chỉ tiêu = 1, sửa số, "Lưu" = 1. **Tổng 3 cú bấm, gõ 1 ô**, không gõ lại mã |

Các việc khác đã đi: chuyển không gian làm việc (bấm tên ở thanh bên, bấm "Mở" ở dòng cần mở = 2 cú bấm, hợp lý, chỉ giảm bớt nút phụ ở T3-15); đổi ngôn ngữ (bấm `EN` = 1 cú bấm, đổi đồng loạt thanh bên và nhãn, đạt yêu cầu); nút hiệu ứng (bấm một lần, chữ đổi "Hiệu ứng: tắt", không có phản hồi gì khác, ảnh hưởng không thấy rõ nên tách khỏi chân thanh bên, T3-12).

## 5. Bảng đổi chữ (tên thẻ, mô tả, nhãn)

Khoá nằm trong `i18n.js` khối `vi` (và khối `en` tương ứng). Chữ mới viết theo quy tắc: không gạch dài, không đại từ nhân xưng, câu ngắn, dùng từ của Sổ nhập.

### 5.1. Tên các thẻ ở thanh bên

| Khoá | Chữ cũ (vi) | Chữ mới (vi) | Lý do | en cũ | en mới |
|---|---|---|---|---|---|
| `nav_pipeline`, `pipeline_title` | Vận hành sắp xếp | Xếp CLB | "Vận hành" là từ của kỹ sư; việc người dùng làm là nhập sổ rồi xếp (P4) | Allocation | Run allocation |
| `nav_others`, `others_title` | Dữ liệu khác | Chi tiết và xuất tệp (**Truong quyết định**: Truong đặt tên cũ ở T2) | "Khác" không nói gì; thẻ này chỉ chứa số liệu chi tiết và xuất tệp | Other data | Details and export |
| `nav_fallback` | Nhập tại chỗ | Nhập nguyện vọng | Không rõ nhập gì, tại chỗ nào; việc thật là nhập nguyện vọng cho học sinh | Kiosk entry | Enter preferences |
| `nav_admin`, `admin_title` | Quản lý {slot_sl} & dự trữ | Quản lý {slot_sl} | "Dự trữ" là từ kỹ thuật; Sổ nhập gọi là "Suất ưu tiên", gộp trong quản lý CLB (T3-27) | Clubs & reserves | Manage clubs |
| `nav_results` | Kết quả | Kết quả (giữ) | Đã rõ | Results | Results |
| `nav_scoring` | Nhập {score_l} | Nhập {score_l} (giữ) | Đã rõ | Score entry | Score entry |

Ghi chú: các số 01 đến 06 trước tên thẻ làm hai việc, đánh số thứ tự và được nhắc trong câu chữ (ví dụ "thẻ 04" ở `xuat_hint_hoc_sinh`). Nên bỏ số nhắc trong câu chữ (dùng tên thẻ), và có thể bỏ luôn số ở thanh bên vì không có thứ tự bắt buộc.

### 5.2. Mô tả đầu trang các thẻ

| Khoá | Chữ cũ (vi) | Chữ mới (vi) | Lý do |
|---|---|---|---|
| `pipeline_desc` | Kiểm tra dữ liệu, bốc thăm, xếp {person_l} vào {slot_sl} và xuất kết quả. | Nhập Sổ nhập CLB, bấm Chạy để xếp {person_l} vào {slot_sl}, rồi tải kết quả. | Nói theo việc người dùng làm, không nói theo bước nội bộ |
| `others_desc` | Số liệu chi tiết của lần xếp: tóm tắt, xuất tệp, mức lấp đầy, nguyện vọng, số bốc thăm và danh sách đầy đủ. | Xuất tệp Excel và xem số liệu chi tiết của lần xếp. | Dài, liệt kê 6 thứ; thẻ nên được nhận ra bằng một câu |
| `kq_desc` | Xem {person_l} học {slot_sl} nào. Không có điểm hay số bốc thăm. | Giữ nguyên. | Rõ; câu thứ hai là nhắc quyền riêng tư (xem mục 7) |
| `admin_desc` | Thêm, sửa {slot_sl} và gán nhãn dự trữ cho {person_l}. Trường tự quyết định ai được dự trữ. Phần mềm chỉ ghép {person_l} và {slot_sl} có cùng nhãn. | Thêm hoặc sửa {slot_sl}, chỉ tiêu và suất ưu tiên. Nhóm ưu tiên của {person_l} chỉ được hưởng suất khi cùng nhãn với {slot_sl}. | Câu cuối cũ ("Phần mềm chỉ ghép ... cùng nhãn") không giải thích được nếu chưa biết "dự trữ" nghĩa là gì |
| `scoring_desc` | Chọn {slot_sl} để chấm. Danh sách chỉ có mã và họ tên, không có số bốc thăm hay thứ hạng nguyện vọng, để việc chấm điểm được khách quan. | Chọn {slot_sl} để chấm. Danh sách chỉ có mã và họ tên, để chấm khách quan. | Rút gọn, giữ lý do khách quan |
| mô tả thẻ 04 (`fallback_desc`) | Tìm hoặc tạo {person_l}, rồi làm hai bước: chọn CLB dự thi và xếp hạng nguyện vọng. Hai bước này không phụ thuộc nhau. | Tìm hoặc tạo {person_l}, rồi chọn CLB dự thi và xếp hạng nguyện vọng. | Bỏ câu cuối, dễ gây thắc mắc |
| `import_hint` | Toàn bộ dữ liệu nằm trong một tệp Excel duy nhất: Sổ nhập CLB. Chưa có sổ thì bấm "Tải sổ nhập mẫu", điền danh sách CLB và học sinh, lưu lại rồi kéo sổ vào ô bên dưới. | Chưa có Sổ nhập CLB? Bấm "Tải sổ nhập mẫu", điền xong rồi kéo vào ô bên dưới. | Một ý, một lệnh |

Bản tiếng Anh tương ứng cho sáu mô tả ở bảng 5.2:

| Khoá | en mới |
|---|---|
| `pipeline_desc` | Import the intake workbook, press Run to place {person_pl} in {slot_pl}, then download the results. |
| `others_desc` | Export Excel files and see detailed figures for the latest run. |
| `admin_desc` | Add or edit {slot_pl}, quotas and priority seats. A priority group only gets those seats in a {slot_l} with the same label. |
| `scoring_desc` | Choose a {slot_l} to score. The list shows only IDs and names, so scoring stays objective. |
| `fallback_desc` | Find or create a {person_l}, then choose test {slot_pl} and rank preferences. |
| `import_hint` | No intake workbook yet? Press "Download sample workbook", fill it in, then drag it into the box below. |

### 5.3. Tên tab con, nút và nhãn

| Khoá | Chữ cũ (vi) | Chữ mới (vi) | en mới |
|---|---|---|---|
| `ql_tab_du_lieu` | Dữ liệu | Xoá dữ liệu | Delete data |
| `ql_tab_wh` | Điểm quyết tâm | Giữ nguyên | giữ |
| `ql_tab_dc` | Điểm chuẩn | (bỏ tab, giữ ở thẻ 03, T3-22) | |
| `seed` (nhãn trước `#seedInput`) | Số khởi tạo bốc thăm | Mã bốc thăm (trong mục Nâng cao) | Draw seed (under Advanced) |
| `seed_locked_hint` + dòng `#stbLockLine` | Số khởi tạo {seed} được khoá cùng số bốc thăm. Muốn đổi, bấm "Bốc thăm lại…". | Bỏ dòng này; giữ một dòng: "Đã bốc thăm lúc {luc}. Muốn bốc thăm lại, bấm "Bốc thăm lại…"." | |
| `brand_sub` | Reserve-Based DA | (bỏ) | |
| `page_title` | Sắp xếp {slot} · RB-DA | Sắp xếp {slot} | |
| `dc_cot_don` | Đơn và chỗ | Số đơn và số chỗ | |
| (cột bảng thẻ 03) | Tỉ lệ chọi | Học sinh trên mỗi chỗ | Applicants per place |
| (cột bảng thẻ 03) | Đặt nguyện vọng 1 | Chọn là nguyện vọng 1 | |
| (nhãn ô thẻ 05) | Tổng chỗ / Suất dự trữ / Nhãn dự trữ | Chỉ tiêu / Suất ưu tiên / Nhóm ưu tiên | Quota / Priority seats / Priority group |
| `ws_wz_buoc` (ghép chuỗi ở `js/075_workspace.js`) | Bước 1/4 ⟨gạch dài⟩ Thông tin chung | Bước 1/4: Thông tin chung | Step 1/4: General |
| `ws_r_max_choices` | Số lựa chọn tối đa mỗi đợt (1⟨gạch nối⟩20) | Số lựa chọn tối đa mỗi đợt (từ 1 đến 20) | Max choices per round (1 to 20) |
| `ws_r_max_tests` | Số mục dự thi tối đa mỗi đợt (0⟨gạch nối⟩20) | Số mục dự thi tối đa mỗi đợt (từ 0 đến 20) | Max test entries per round (0 to 20) |
| `xuat_hint_hoc_sinh` | Hồ sơ {person_l}: bấm "Chọn {person_l}…" rồi đánh dấu {person_l} ở bảng bên dưới. Đang mở một {person_l} ở thẻ 04 thì bấm "Xuất CSV {person_l} này" ngay tại đó. | Hồ sơ {person_l}: bấm "Chọn {person_l}…" rồi đánh dấu trong bảng bên dưới. | Profiles: press "Choose ..." and tick them in the table below. |
| `xuat_opt_kem_csv` | Kèm các tệp CSV rời (chỉ cần khi đổ số liệu vào phần mềm khác) | Kèm các tệp CSV rời (dùng khi cần nạp sang phần mềm khác) | |
| `ws_*` nút | Xuất tệp nén / Nhập tệp nén / Lưu thành mẫu | Sao lưu ra tệp ZIP / Khôi phục từ tệp ZIP / Lưu làm mẫu | Back up to ZIP / Restore from ZIP / Save as template |
| `kq_sx_ngay` (nếu giữ hàng sắp xếp) | Theo ngày trong tuần | Theo CLB mỗi ngày | By club each day |
| `kq_sap_nhan` | Sắp xếp | Xếp theo | Sort by |
| nhãn câu cảnh báo | Chưa dùng hết điểm quyết tâm: {person_l} {ma} còn thiếu {n} điểm ở quỹ {q}. (lặp mỗi học sinh) | (gộp một dòng) {n} {person_l} chưa chia đủ 100 điểm quyết tâm. Xem 5 dòng đầu. | |
| (câu chặn nghiêm trọng, T3-02) | {n} học sinh có hồ sơ điểm quyết tâm chưa hợp lệ, nên lần chạy xếp sẽ bị chặn cho tới khi sửa xong. | Chưa chạy được: {n} {person_l} chưa chia điểm quyết tâm. Thêm cột Điểm quyết tâm vào sổ, hoặc tắt tính năng này ở thẻ Quản lý. | |

Chữ en "Allocation" ở `nav_pipeline` hiện không khớp với phiên bản vi dài hơn; đề xuất trên làm hai bản khớp nhau về nghĩa.

## 6. Danh sách vi phạm quy tắc chữ (kiểm bằng máy)

Quy tắc của Truong: mô tả và tên thẻ không có gạch dài và không có đại từ nhân xưng (danh sách cấm theo yêu cầu của Truong). Kiểm: biểu thức khớp biên từ, nạp từ `i18n.js` (khối `vi`), `i18n_errors.py` (`vi`), `index.html`, `js/*.js`, cộng toàn bộ chữ hiện thật trên các ảnh chụp.

Kết quả tổng (đã bổ sung ở vòng 1 sau khi người kiểm quét rộng hơn): catalog `i18n.js` khối `vi` (688 chuỗi) và `i18n_errors.py` khối `vi` (236 thông báo) sạch gạch dài và đại từ cấm. Vi phạm nằm ở những nơi ngoài catalog: tệp Excel xuất (`api_xuat.py`), màn phục hồi (`recovery.html`), phần ghép chuỗi trong `js/`, chữ en, và chữ dự phòng trong `index.html`. Danh sách dưới đây có thể chưa đủ vì chưa quét mọi tệp Python và mọi tài liệu. Vi phạm tìm được:

### 6.1. Hiện trên màn hình lúc chạy

| # | Tệp, vị trí | Khoá | Chữ hiện | Vi phạm | Đề xuất |
|---|---|---|---|---|---|
| 1 | `js/075_workspace.js` dòng 544 | `ws_wz_buoc` ghép với tên bước | "Bước 1/4 ⟨gạch dài⟩ Thông tin chung" (và các bước 2, 3, 4) | gạch dài, hiện ở cả bốn bước | "Bước 1/4: Thông tin chung" |
| 2 | `js/075_workspace.js` dòng 117; `main.py` hàm `tieu_de_cua_so` | (không dùng khoá) | tiêu đề cửa sổ "<tên chỗ xếp> ⟨gạch dài⟩ <tên workspace>" | gạch dài | " · " hoặc ": " |
| 3 | `js/075_workspace.js` dòng 602, 606; `js/04_nhap_tai_cho.js` dòng 748 | `aria-label` | "<x> ⟨gạch dài⟩ <y>" (đọc màn hình) | gạch dài (không thấy bằng mắt) | ": " |
| 4 | `i18n.js` | `ws_r_max_choices` | "Số lựa chọn tối đa mỗi đợt (1⟨gạch nối⟩20)" | gạch ngang dài vừa giữa hai số | "(từ 1 đến 20)" |
| 5 | `i18n.js` | `ws_r_max_tests` | "Số mục dự thi tối đa mỗi đợt (0⟨gạch nối⟩20)" | như trên | "(từ 0 đến 20)" |

### 6.2. Chỉ nằm trong chữ dự phòng của `index.html` (không hiện khi catalog tải được, nhưng lệch nguồn)

| # | Dòng | Khoá | Vi phạm |
|---|---|---|---|
| 6 | 309 | `ket_qua_cu_banner` | gạch dài |
| 7 | 330 | `xuat_theo_lop_hint` | gạch dài |
| 8 | 332 | `xuat_hint_hoc_sinh` | "⟨đại từ⟩" ba lần |
| 9 | 333 | `xuat_canh_bao_diem` | gạch dài |
| 10 | 564 | `hien_ca_em_chua_xep` | "⟨đại từ⟩" |
| 11 | 621 | `btn_xuat_em_nay` | "⟨đại từ⟩" |
| 12 | 774 | `xuat_canh_bao_diem` (lặp lần hai) | gạch dài |

### 6.2b. Tệp Excel xuất và màn phục hồi (ưu tiên cao, người ngoài đọc)

| # | Tệp, vị trí | Vi phạm | Ghi chú |
|---|---|---|---|
| 13 | `api_xuat.py`, các dòng chữ: 212, 225, 226, 239, 242, 244, 249, 252, 261, 270, 271, 276, 277, 285, 291, 328, 362, 364, 367, 383, 406, 469, 470, 471, 474, 475, 489, 504, 530, 531, 537, 543, 550, 561, 562, 568, 572, 590, 631, 661, 735, 745, 753, 754, 759, 771, 772, 779, 798, 809, 820, 825, 1079, 1381, 1384 | gạch dài và/hoặc ⟨đại từ⟩ (55 dòng có chuỗi chữ vi phạm; quét bằng `tokenize`, loại docstring và chú thích; chưa phân loại từng dòng là chữ hiện hay chuỗi nhật ký) | Đây là chữ ghi vào tệp Excel mà BGH và giáo viên chủ nhiệm mở. Ví dụ: "Chưa chạy sắp xếp lần nào, các trang danh sách đang ...", "Số ⟨đại từ⟩ đã có {slot_l}", "Tệp có {score_l} chấm và số bốc thăm, không gửi cho giáo viên chấm {score_l}." (bản trong tệp còn gạch dài) |
| 14 | `recovery.html` dòng 30 (`recovery_kg_cach_tieu_de`) và dòng 35 (`recovery_kg_khong_mat`) | gạch dài | Màn phục hồi khi dữ liệu hỏng, người dùng đang lo, chữ cần rõ nhất |
| 15 | `i18n.js` dòng 1359 và 1360 (khối `en`: `ws_r_max_choices`, `ws_r_max_tests`) | gạch ngang dài vừa giữa hai số ("1⟨gạch nối⟩20", "0⟨gạch nối⟩20") | Bản tiếng Anh của mục 4 và 5 trong 6.1 |

### 6.3. Ký tự gạch dài dùng làm ô trống (cần Truong quyết định, T3-41)

Một ký tự gạch dài đơn lẻ làm ô trống: `js/00_nen.js` dòng 79; `js/02_van_hanh.js` dòng 602 đến 605; `js/03_ket_qua.js` dòng 350, 512 đến 514, 531, 633, 987; `js/05_quan_ly.js` dòng 104, 138, 499, 591, 851, 975, 1473, 1626; `js/075_workspace.js` dòng 676; `index.html` dòng 75 đến 81 (dải số), 407, 463 và 464 (`#doPhuTb`, `#doPhuTrangTay`), 605, 619, 788, 875, 1007. Trong mô phỏng hiện ở bảng CLB (cột nhãn), bảng điểm chuẩn, danh sách học sinh. Không phải câu mô tả nhưng cùng ký tự bị cấm.

### 6.4. Ghi chú về nguồn dữ liệu của danh sách này

- Các mục 1, 4 và 5 thấy được trên màn hình (ảnh `a10` có tiêu đề bước và các ô khoảng số); mục 2 và 3 chỉ thấy khi xem tiêu đề cửa sổ và công cụ đọc màn hình. Các mục 6 đến 12 chỉ tìm thấy khi quét tệp; mô tả trong catalog `i18n.js` tương ứng đã được sửa ở T2.
- Các đại từ còn lại trong `js/03_ket_qua.js` (dòng 725, 942) và `js/05_quan_ly.js` (dòng 317) nằm trong chú thích mã nguồn, không hiện ra người dùng; không tính là vi phạm.
- Chưa quét: các tệp Python khác ngoài `api_xuat.py`, chữ trong tệp `.docx`, `.pptx`, tệp hướng dẫn `.md` và các sheet "Hướng dẫn" trong sổ Excel mẫu ngoài sheet `Hướng dẫn` của `mau_csv/SO_NHAP_CLB.xlsx` (đã quét, sạch).

## 7. Những thứ KHÔNG nên bỏ (kèm lý do)

| Thứ giữ | Ở đâu | Vì sao giữ |
|---|---|---|
| Dải nhắc "Dữ liệu đã được sửa sau lần chạy gần nhất, nên kết quả bên dưới có thể đã cũ" (và `dc_cu`, `xuat_kq_cu`) | thẻ 02, 03, điểm chuẩn, tệp xuất | An toàn dữ liệu: ngăn công bố kết quả cũ. Đã kiểm hoạt động thật: sau khi lưu CLB, thẻ 02 hiện dải này. Chỉ nên thêm liên kết "Chạy lại" vào đó |
| Xác nhận "Bốc thăm lại…" | thẻ 01 | Bất biến 3 (số bốc thăm khoá sau lần chạy đầu); bấm nhầm là mất công bằng giữa các lần chạy |
| Khối "Vùng nguy hiểm" và các xác nhận hai bước, sao lưu tự động trước khi xoá | thẻ 05 tab Dữ liệu | Thao tác xoá không hoàn lại; có sao lưu theo bất biến 5 và 7 |
| Chặn chạy khi hồ sơ điểm quyết tâm lỗi | pipeline, `health` | Quyết định có chủ ý ở A13.13. Chỉ đổi cách báo (T3-02), không đổi quy tắc |
| Cảnh báo đỏ "Tệp xuất có điểm chấm và số bốc thăm. Không gửi các tệp này cho giáo viên chấm điểm." | thẻ 03 | Bảo vệ tính khách quan khi chấm điểm và quyền riêng tư; BGH và giáo viên chủ nhiệm chỉ nhận tệp "Xuất theo lớp" |
| Câu "Không có điểm hay số bốc thăm" ở mô tả Kết quả, Nhập điểm | thẻ 02, 06 | Cùng lý do: thẻ này dành cho nhiều đối tượng, không được lộ điểm hoặc số bốc thăm (ràng buộc chống nội sinh, bất biến 2) |
| Hiển thị từng bước và hoàn tác khi chạy lỗi | thẻ 01 | Bất biến 5 (thứ tự sao lưu, kiểm tra, khoá seed, giải, ghi một giao dịch, xuất; lỗi thì rollback). Chỉ thu gọn lúc thành công |
| Thẻ "Lịch sử sắp xếp" (ở dạng thu gọn) | thẻ 01 | Bất biến 4: `run_history` không bao giờ bị ghi đè hay xoá; người dùng cần đường xem lại |
| Chấm "• Chưa lưu" ở phiếu kiosk | thẻ 04 | Ngăn mất dữ liệu khi chuyển học sinh |
| Cảnh báo "Bỏ chọn một CLB đã chấm điểm thì điểm đó bị xoá khi bấm Lưu" | thẻ 04 bước 1 | Hành động có thể xoá dữ liệu chấm |
| Bảng "Học sinh chưa có CLB nào" (32 học sinh, màu cảnh báo) | thẻ 03 | Việc quản trị phải xử lý tiếp; là con số hành động duy nhất của thẻ |
| Xem trước khi nhập ("Sẵn sàng nhập: 10 CLB · 1 buổi · 120 học sinh ...") | thẻ 01 | Cho người dùng nhận ra tệp đúng trước khi ghi (P3) |
| Trạng thái "mất kết nối dữ liệu" khi có sự cố | chân thanh bên | An toàn vận hành (A13.11, N3); chỉ nên ẩn khi bình thường |
| Chữ "dữ liệu MÔ PHỎNG" ở mọi báo cáo và tài liệu | tài liệu, báo cáo | Liêm chính học thuật của đề tài (`CLAUDE.md`). Chưa thấy câu này trong giao diện; nên thêm một dòng nhỏ ở chân thanh bên khi workspace là bộ mẫu (đề xuất mới, không đụng báo cáo của học sinh) |
| Số "Được nguyện vọng 1" và "trong 3 nguyện vọng đầu" (và tỉ lệ tương ứng) | thẻ 03, ô tóm tắt | Là con số chính của báo cáo đề tài. Có thể CHUYỂN xuống thẻ chi tiết, không nên xoá hẳn (T3-24) |
| Các bộ cột CSV, chế độ đối chứng, dữ liệu trong `match_results` | backend | Bất biến 1, 6, 7; mọi đề xuất trong tệp này chỉ đổi hiển thị |

## 8. Gợi ý thứ tự làm (nếu Truong duyệt)

0. Lô 0, lỗi sản phẩm (mục 0): B1 (T3-26), B2 (T3-01), B3 (T3-42). Cần mã mục trong sổ đăng ký trước khi làm.
1. Lô 1, chữ và hiển thị nhỏ, rủi ro thấp (khoảng 1 ngày): T3-05 (ẩn seed), T3-08, T3-13, T3-37 đến T3-40, T3-43, và đổi chữ ở mục 5.1 đến 5.3 (trừ tên thẻ "Dữ liệu khác" và nhãn thẻ 05, T3-27).
2. Lô 2, hiển thị tên buổi, bớt khối và gom nút (2 đến 3 ngày): T3-14, T3-02, T3-03, T3-04, T3-06, T3-07, T3-20 đến T3-25, T3-32 đến T3-35, T3-12.
3. Lô 3, cần Truong quyết định trước: tên thẻ "Dữ liệu khác" (Truong đặt ở T2), T3-16 (mặc định tầng 1 khi chưa có lớp, hoặc ẩn "Theo lớp"), T3-17 (hàng xếp thứ hai), T3-18 (cột "Thứ tự"), T3-19 (nút tải ở thẻ 02), T3-22 (giữ Điểm chuẩn ở đâu), T3-27 (gộp từ vựng "dự trữ" thành "ưu tiên"), T3-11 (trình hướng dẫn một bước), T3-31 (bỏ biểu đồ), T3-41 (ký tự ô trống).
4. Mỗi mục sửa phải gắn mã mục trong sổ đăng ký trước khi làm (`CLAUDE.md` quy tắc 1), và chạy các test được ghi ở cột Rủi ro.

Ghi chú trung thực: toàn bộ số liệu trong tệp này lấy từ các lần chạy thử trên dữ liệu mô phỏng ngày 2026-11-03; không có số đo thời gian thật hay khảo sát người dùng thật nào.
