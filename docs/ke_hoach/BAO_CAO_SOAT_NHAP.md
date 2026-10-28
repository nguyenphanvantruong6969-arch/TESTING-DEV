# Báo cáo soát HỆ THỐNG NHẬP (mức medium)

- Ngày: 28/10/2026 · Nhánh: `claude/wizardly-lovelace-rfd5h2` (đỉnh `93ccb49`)
- Phương pháp: `/code-review medium` chạy lần lượt cho 4 nhóm; sau đó soát tay thêm các điểm bảo mật nhấn mạnh (zip slip, zip bomb, SQL ghép chuỗi, CSV injection, XSS) và tái hiện bằng script tạm (không commit).
- **Chỉ báo cáo, không sửa mã.** Dữ liệu đo là MÔ PHỎNG.
- Quy ước "Mức": **chặn** (làm hỏng chạy thật hoặc mất dữ liệu) / **nên sửa** / **nhỏ**. "Đã tái hiện?": Có = chạy script tạm thấy đúng lỗi; Không = đọc mã, chưa dựng được tình huống (thường do lỗi nằm ở JS cần giao diện thật).
- Lưu ý phạm vi: phần JS chỉ soát bằng đọc mã (không chạy giao diện Chromium cho từng ca). XSS: lấy mẫu mọi chỗ `innerHTML` ở `js/04_nhap_tai_cho.js` đều đi qua `esc()` — không thấy lỗ; chưa soát hết `js/03`, `js/05`, `js/06`.

## Tổng quan

| Nhóm | Chặn | Nên sửa | Nhỏ | Tổng |
|---|---|---|---|---|
| 1. Nạp Sổ nhập / CSV / Excel / tải tệp | 1 | 7 | 2 | 10 |
| 2. Kiosk học sinh nhập | 0 | 4 | 5 | 9 |
| 3. Nhập tay ở Quản lý | 0 | 5 | 5 | 10 |
| 4. Chấm điểm mù + workspace | 0 | 5 | 5 | 10 |
| **Cộng** | **1** | **21** | **17** | **39** |

---

## Nhóm 1 — Nạp Sổ nhập / CSV / Excel / tải tệp

`api_nhap.py`, `so_nhap.py`, `so_excel.py`, `browser_host.py`, `js/04_nhap_tai_cho.js`

| # | Mức | Tệp:dòng | Vấn đề | Đầu vào cụ thể → kết quả sai | Đề xuất | Đã tái hiện? |
|---|---|---|---|---|---|---|
| 1.1 | **chặn** | `browser_host.py:154` | Trình xử lý `pagehide` gửi `/__closed__` mỗi lần trang bị dỡ, kể cả tải lại; chỉ đường đổi workspace đặt cờ `__DANG_TAI_LAI`. | Chế độ dự phòng (trình duyệt): bấm F5 → máy chủ `shutdown()` → trang mới nhận `ERR_CONNECTION_REFUSED`, mọi lời gọi sau đó lỗi. | Không tắt ngay khi `pagehide`; chỉ đánh dấu "có thể đóng" rồi chờ lưu hiệu `/__alive__` vắng mặt hết ngưỡng (đã có sẵn cơ chế này), hoặc phân biệt bằng `event.persisted`/`performance.navigation`. | **Có** (Chromium headless: tải trang, `reload()`, sau 2 s máy chủ từ chối kết nối). Lưu ý: chưa cô lập riêng yếu tố "token" nên cần xác nhận lại trên cửa sổ `--app` thật. |
| 1.2 | nên sửa | `browser_host.py:266` (và các dòng `_send_json` khác) | Trả lỗi HTTP bằng chuỗi trần (`["forbidden"]`, `["unknown endpoint"]`, `["payload too large"]`), có chỗ thiếu `data`. Trái bất biến 6 (`errors=[{code,params}]`, nguồn `i18n_errors.py`). | Token sai → `{"ok": false, "errors": ["forbidden"]}`; giao diện đọc `.code` → `undefined` → toast trống. Tệp xlsx base64 quá lớn → `payload too large` không dịch được. | Dùng `err()`/`phan_hoi_loi` cho mọi nhánh lỗi, thêm mã vào `i18n_errors.py` rồi `tao_i18n_js.py`. | **Có** (đọc thân phản hồi 403). |
| 1.3 | nên sửa | `browser_host.py:191` (cũng `_token_trong_url` ~L195) | `secrets.compare_digest` với `str` chứa ký tự không phải ASCII ném `TypeError`. | Tiêu đề `X-Kiosk-Token: é` (hoặc `?t=é`) → ngoại lệ trong luồng xử lý, kết nối bị ngắt không có 403. | So sánh trên `bytes` (`.encode('utf-8')`) hoặc bắt `TypeError` rồi trả 403. | **Có** (`RemoteDisconnected`, log `TypeError`). Tác động bảo mật thấp (chỉ từ chối dịch vụ cục bộ, vẫn chặn được truy cập). |
| 1.4 | nên sửa | `so_nhap.py:443` | Cột cuối của nhóm cuối = cột cuối cùng có chữ ở hàng 2; cột "Ghi chú"/cột phụ ở bên phải bị tính vào nhóm. | Sổ hai hàng tiêu đề, thêm "Ghi chú" ở hàng 2 sau cột cuối → `so_nhap_cot_lech_nhom` (cột AW, NV 15), `students=[]`: **cả sổ bị từ chối**. | Dừng nhóm cuối khi gặp tiêu đề hàng 2 không thuộc `_loai_cot_nhom` liên tiếp sau cột nhóm hợp lệ cuối, hoặc coi cột lạ ngoài nhóm là cảnh báo bỏ qua. | **Có**. |
| 1.5 | nên sửa | `so_nhap.py:1260` (`diem_w_o`) | `str.isdigit()` đúng với chữ số Unicode (`²`, `٣`) nhưng `int()` ném `ValueError`; không có `try`. | Ô điểm quyết tâm `"²"` → `ghi_so_nhap` sụp → cả thao tác "xuất dữ liệu đầu vào" thất bại, trái docstring "giữ chuỗi gốc để người nhập thấy ô sai". | `re.fullmatch(r"[0-9]+", ...)` như phía nhập (hoặc `try/except ValueError`). | **Có** (`ValueError: invalid literal for int(): '²'`). |
| 1.6 | nên sửa | `js/04_nhap_tai_cho.js:280` | Xoá em cuối của trang → danh sách rỗng, ẩn phân trang, `fallbackStudentPage` không giảm; backend không kẹp `page`. | 17 em, 8 em/trang, đang ở trang 3 (1 em), xoá em đó → "không tìm thấy", không có nút về trang 2. | Kẹp `page` về `total_pages` ở backend (`list_students_admin`), hoặc ở JS lùi trang khi `rows` rỗng và `page>1`. Dùng chung cho `js/05_quan_ly.js` (xem 3.3). | **Có** (backend: `page=5, page_size=2, total=5` → `rows=0`). |
| 1.7 | nên sửa | `js/04_nhap_tai_cho.js:163` | Callback lưu (`submit_test_selection`, Wharton) ghi mốc "đã lưu" từ trạng thái giao diện LÚC PHẢN HỒI về, không kiểm `sid === currentFallbackStudent`. | Bấm Lưu em A, trong lúc chờ bấm em B → `daLuuNv = currentRanking.slice()` lấy xếp hạng của B; cờ "chưa lưu" của B sai, mất cảnh báo thoát khi B có thay đổi thật. | Chụp `sid` + bản sao dữ liệu lúc bấm; trong callback bỏ qua nếu `sid` không còn là em đang chọn, và đặt mốc từ bản chụp. | Không (JS, cần giao diện). |
| 1.8 | nên sửa | `js/04_nhap_tai_cho.js:625` (cũng `:531`) | Ô Wharton tự điền "100" cho khung chỉ có một CLB nhưng mốc `daLuu[quy\|cid]` là `daCo` (''), nên chuỗi hiện tại ≠ mốc. | Em có đúng một CLB không thi, chưa lưu điểm, workspace bật `tu_dien_mot_clb` → vừa chọn em đã hiện "Chưa lưu"; "Xuất em này" bị từ chối `fallback_xuat_chua_luu`; workspace `chiDoc` thì không có cách lưu để gỡ. | Đặt mốc bằng đúng giá trị tự điền, hoặc loại ô khoá khỏi `whartonChuoi()`. | Không (JS). |
| 1.9 | nhỏ | `js/04_nhap_tai_cho.js:254` (cũng `:262`) | Nhánh xoá thành công không gọi `boChonHocSinhDuPhong()`, để sót `whartonState`, `currentRanking`, `daLuu*` và hẹn giờ `choRoiDi`. | Xoá em A đang mở rồi chọn em khác bị lỗi → xếp hạng/Bước 3 của em đã xoá còn trong DOM. | Gọi hàm dọn có sẵn, một đường dọn duy nhất. | Không (JS). |
| 1.10 | nhỏ | `api_nhap.py:766` | `_doc_diem`, `_o_excel_thanh_chu`, logic bóc dấu nháy của `_parse_csv_rows` là bản sao của `so_nhap.doc_diem`/`o_thanh_chu`. | Sửa dấu phẩy thập phân/inf/nan ở một bản → xem trước báo "sẵn sàng" nhưng nạp thật báo `csv_score_not_a_number`. | Gọi thẳng hàm của `so_nhap` (đã được import). | Không (chỉ rủi ro bảo trì). |

> Ghi chú ngoài bảng: mục "ô gộp" và "sổ một hàng vs hai hàng" của đề bài đã được các test hiện có và tiêu đề hai hàng xử lý; riêng cột phụ ở cuối là lỗi 1.4.

---

## Nhóm 2 — Kiosk học sinh nhập (chọn CLB thi, nguyện vọng, điểm quyết tâm)

`api.py` (`submit_*`), `api_quan_ly.py` (`submit_preferences`, `submit_wharton`), `api_chung.py`, `js/04_nhap_tai_cho.js`

| # | Mức | Tệp:dòng | Vấn đề | Đầu vào cụ thể → kết quả sai | Đề xuất | Đã tái hiện? |
|---|---|---|---|---|---|---|
| 2.1 | nên sửa (cần bàn) | `api_quan_ly.py:1237` | `submit_preferences` xoá `wharton_bids` của CLB bị bỏ khỏi nguyện vọng mà không kiểm `_wharton_dang_khoa`; `submit_wharton`/`clear_wharton` thì chặn khi khoá. | Sau khi chạy xếp (điểm quyết tâm đã khoá), kiosk lưu lại nguyện vọng và bỏ một CLB → điểm đã khoá của CLB đó bị xoá; kết quả không tái lập từ dữ liệu đã khoá. | Chặn theo khoá, hoặc nếu cố ý ("các cửa XOÁ vẫn chạy") thì cảnh báo rõ trên giao diện + ghi `wharton_nhat_ky`. | Không (đọc mã). |
| 2.2 | nên sửa | `js/04_nhap_tai_cho.js:440` | `whartonThuThapTu` đọc cả ô bị khoá (disabled) nên "100" tự điền được gửi lên và ghi vào `wharton_bids`, trái thiết kế "cách A" (ô tự điền không ghi). | Em một CLB X bấm Lưu → `{X:100}` vào DB; sau đó thêm CLB Y cùng quỹ → X mang 100, Y trống, tổng đã đủ nên `kiem_ho_so_wharton` không nhắc; Y nhận 0 điểm. | Bỏ qua ô `disabled` khi thu thập. | Không (JS). |
| 2.3 | nên sửa | `js/04_nhap_tai_cho.js:207` | Như 1.7 cho `submit_preferences`/`submit_test_selection`: mốc "đã lưu" lấy từ trạng thái lúc phản hồi; nếu vẫn là em A mà bấm thêm CLB khi đang chờ, CLB thêm sau bị tính đã lưu. | Xem 1.7. | Xem 1.7. | Không (JS). |
| 2.4 | nên sửa | `js/04_nhap_tai_cho.js:625` | Cùng gốc với 1.8 (cờ "Chưa lưu" giả ở khung một CLB). | Xem 1.8. | Xem 1.8. | Không (JS). |
| 2.5 | nhỏ | `js/04_nhap_tai_cho.js:400` | `selectFallbackStudent` không xoá `testSelectionFeedback`, `preferencesFeedback` của em trước. | Lưu nguyện vọng em A, chọn em B → dòng xanh "Đã lưu n nguyện vọng" vẫn hiện dưới màn hình em B; người vận hành có thể bỏ bước lưu cho B. | Xoá cả hai khi đổi em. | Không (JS). |
| 2.6 | nhỏ | `js/04_nhap_tai_cho.js:262` | Như 1.9. | Xem 1.9. | Xem 1.9. | Không (JS). |
| 2.7 | nhỏ | `api_chung.py:53` | Bộ bọc `_nho_trong_luc_xuat.boc(self, *args)` không nhận keyword, khoá nhớ chỉ có `args`. | Gọi `self.bao_cao(page=2)` → `TypeError` ngay cả ngoài lúc xuất. Hiện chưa nơi nào gọi bằng keyword. | Nhận `**kwargs` và đưa vào khoá nhớ. | Không. |
| 2.8 | nhỏ | `api_chung.py:148` | `duong_dan_khong_de` dừng ở `n < 1000`, rồi trả đường dẫn đã tồn tại → ghi đè im lặng. | Thư mục có `x (2).csv … x (1000).csv` → trả `x (1000).csv`. Hiếm. | Tăng trần hoặc báo lỗi thay vì trả tên đã có. | Không. |
| 2.9 | nhỏ | `api_chung.py:170` | `_an_toan_cho_excel` thêm `'` cho mọi chuỗi bắt đầu `-`/`+`, kể cả số âm dạng chuỗi (`_so_vn` → `"-1,5"`). | Cột chênh lệch âm trong CSV xuất ra `'-1,5` → Excel coi là chữ. | Bỏ qua chuỗi khớp mẫu số, chỉ chặn công thức thật. | Không (đọc mã). |

---

## Nhóm 3 — Nhập tay ở Quản lý

`api_quan_ly.py`, `js/05_quan_ly.js`

| # | Mức | Tệp:dòng | Vấn đề | Đầu vào cụ thể → kết quả sai | Đề xuất | Đã tái hiện? |
|---|---|---|---|---|---|---|
| 3.1 | nên sửa | `api_quan_ly.py:1251` | `create_student_if_missing` không kiểm tra/chuẩn hoá `student_id`, `name` (khác `create_or_update_club`). | Gọi với `student_id=""` hoặc `"  A01 "`, `name=None` → hàng được chèn nguyên văn; `"A01"` và `"  A01 "` thành hai em khác nhau; mã rỗng khó xoá/tìm. | `strip`, từ chối rỗng, chuẩn NFC, `name` mặc định `""`; dùng cùng bộ chuẩn hoá với nạp Sổ. | **Có** (đọc lại bảng: `('', 'ten')`, `('  A01 ', None)`). |
| 3.2 | nên sửa | `api_quan_ly.py:244` (`delete_club`) | Chỉ chặn khi còn `preferences`/`match_results`, rồi xoá `club_scores` và `club_test_selection` không báo, không sao lưu. | CLB đã có em tick thi và điểm đã chấm, chưa ai xếp vào nguyện vọng → bấm Xoá: điểm giáo viên chấm mất, kết quả chỉ báo `deleted`. | Sao lưu trước + trả `n_scores_removed`, hoặc chặn khi còn điểm đã chấm. | Không (đọc mã). |
| 3.3 | nên sửa | `js/05_quan_ly.js:582` | Hai danh sách phân trang (học sinh, bảng Wharton) không kẹp trang và ẩn thanh phân trang khi trang rỗng. | Bộ lọc "chỉ hồ sơ có vấn đề" ở trang 2, sửa xong em cuối của trang → `rows` rỗng, không có nút quay về. | Như 1.6. | **Có** phần backend (xem 1.6); phần JS chưa chạy giao diện. |
| 3.4 | nên sửa | `js/05_quan_ly.js:649` | `loadAdminWharton(true)` khôi phục chữ đang gõ (`giu`) từ khung đang mở, đè dữ liệu server vừa đổi. | Khung sửa em X đang 40/40, bấm "Phóng hàng loạt" (server ghi 50/50) → màn hình lại điền 40/40 "chưa lưu"; bấm Lưu ghi đè kết quả phóng. | Chỉ khôi phục khi người dùng thực sự đã gõ (so với mốc), hoặc huỷ `giu` sau thao tác hàng loạt. | Không (JS). |
| 3.5 | nên sửa | `api_quan_ly.py:952` (`phong_wharton_hang_loat`) | Ghi từng em trong giao dịch riêng; gặp `wharton_da_khoa` hoặc lỗi giữa vòng thì chỉ trả lỗi, mất số liệu những em đã ghi. | 200 em, lỗi ở em 120 → 119 em đã ghi vĩnh viễn nhưng phản hồi không có `n_phong`/`backup_path`; người vận hành tưởng chưa có gì đổi. | Một giao dịch cho cả mẻ (rollback toàn bộ) hoặc trả kết quả từng phần kèm đường dẫn sao lưu. | Không (đọc mã). |
| 3.6 | nhỏ | `js/05_quan_ly.js:367` | `loadThoiKhoaBieu` ẩn cả panel khi kết quả tìm không có em nào, mà ô tìm nằm trong panel. | Gõ chuỗi không khớp → panel và ô tìm biến mất đến khi tải lại thẻ. | Chỉ ẩn bảng, giữ ô tìm. | Không (JS). |
| 3.7 | nhỏ | `api_quan_ly.py:672` | `_ngu_canh_diem_chuan` nói đọc "trong MỘT giao dịch" nhưng thực tế ba lần đọc riêng. | Lần chạy xếp chen giữa → `clubs`/`tested_scores` cũ, `match` mới → điểm chuẩn lệch. Chỉ đọc, không ghi. | Dùng một kết nối đọc. | Không. |
| 3.8 | nhỏ | `js/05_quan_ly.js:512` (cùng `get_diem_chuan_clb`) | Mỗi lần mở/làm mới thẻ Quản lý đọc lại toàn bộ dữ liệu nhiều lần; `get_diem_chuan_clb` tính lại điểm chuẩn mọi CLB để lấy một dòng. | ~800 em × 20 CLB: thao tác nhỏ sau mỗi lần lưu/khoá/xoá có thể chậm. | Cache một ngữ cảnh, hoặc truyền sẵn dòng. | Không đo (nạp Sổ 800×20 chỉ 0,2–0,4 s, xem Điểm tốt; chưa đo thẻ Quản lý). |
| 3.9 | nhỏ | `js/05_quan_ly.js:1833` | `loadChiTietDiemChuan` dùng `callApi` thường, không `callApiMoiNhat`. | Đổi nhanh CLB A→B, phản hồi A về sau → hiện số CLB A dưới nhãn B. | Dùng `callApiMoiNhat`. | Không (JS). |
| 3.10 | nhỏ | `js/05_quan_ly.js:1162` | Lưu/xoá CLB không làm mới bảng tải theo buổi, lịch tuần, gợi ý buổi. | Thêm CLB buổi mới → bảng cũ cho tới khi đổi thẻ. | Gọi lại `loadBuoiOptions/loadTaiTheoBuoi/loadLichTuan`. | Không (JS). |

---

## Nhóm 4 — Chấm điểm mù + workspace

`api_cham_diem.py`, `api_workspace.py`, `workspace.py`, `cau_hinh_ws.py`, `nhan_ws.py`, `js/06_cham_diem.js`, `js/075_workspace.js`

| # | Mức | Tệp:dòng | Vấn đề | Đầu vào cụ thể → kết quả sai | Đề xuất | Đã tái hiện? |
|---|---|---|---|---|---|---|
| 4.1 | nên sửa | `api_workspace.py:239` | `delete_workspace` kiểm "đang mở" TRƯỚC khi lấy `_khoa_ghi`, không kiểm lại sau; `open_workspace` đồng thời có thể chen vào. | Workspace tạm (chưa chọn) bị xoá cùng lúc người dùng mở nó ở luồng khác → thư mục đang dùng bị chuyển vào `_trash`, `db_path` đổi ngầm; Windows thì lỗi vì tệp đang mở. | Kiểm lại trong khoá. | Không (đua luồng, khó dựng). |
| 4.2 | nên sửa | `api_workspace.py:248` | Xoá workspace cuối cùng (placeholder khởi động) không cập nhật `db_path` (thiếu `else` của `if con_lai`). | Còn ≥2 workspace, chưa chọn; xoá hết rồi xoá cả placeholder → `db_path` trỏ vào thư mục đã vào `_trash`; các lời gọi sau đọc/ghi đường dẫn không tồn tại. | Đặt `db_path` về trạng thái chưa chọn hoặc tạo workspace mặc định. | Không (đọc mã). |
| 4.3 | nên sửa | `api_cham_diem.py:49` | `submit_person_scores` chỉ kiểm `score_scope == per_person`; nhận và báo "đã lưu" cả khi `priority == 'tier'` (thuật toán bỏ qua điểm). `submit_club_scores` thì từ chối đúng ca này. | Workspace `tier`+`per_person`, gọi API trực tiếp → `ok`, `n_saved=N`, nhưng không ảnh hưởng kết quả: "lưu mà bị bỏ qua". | Dùng chung bộ chắn với `submit_club_scores`. | Không (đọc mã). |
| 4.4 | nên sửa | `api_cham_diem.py:113` | `get_club_applicants_for_scoring`, `get_scoring_overview` không áp bộ chắn per_person/tier như `submit_club_scores`; đọc và ghi bất đồng. | Workspace per_person: tải được danh sách, gõ điểm, chỉ khi Lưu mới báo `scoring_not_per_slot` → mất công nhập. | Áp cùng bộ chắn ở các hàm đọc. | Không (đọc mã). |
| 4.5 | nên sửa | `api_cham_diem.py:88` (cũng `:177`) | `student_id` không băm được (list/dict) làm `sid not in co` ném `TypeError` → cả mẻ bị từ chối thay vì bỏ qua mục sai. | `[{'student_id':['x'],'score':5},{'student_id':'HS1','score':9}]` → `error_saving_scores`, HS1 không được lưu. | Kiểm `isinstance(sid, str)` từng mục, bỏ qua và đếm `n_skipped`. | Không (đọc mã). |
| 4.6 | nhỏ | `api_workspace.py:265` | `export_workspace` rơi về thư mục của workspace ĐANG MỞ (không phải workspace được xuất); `output_path` tuyệt đối dùng nguyên văn và ghi đè không kiểm trùng. | Downloads không ghi được, mở B, xuất A → `A.zip` nằm trong `workspaces/B/`. | Dùng `duong_dan_khong_de`, thư mục dự phòng trung tính. | Không. |
| 4.7 | nhỏ | `cau_hinh_ws.py:124` | Chắn công thức Excel (`= + - @`) chỉ áp cho `labels`, không áp cho `name`, và không bắt tab/CR đứng đầu. | Zip nhập có `name` = `=HYPERLINK(...)` → tên lọt vào tiêu đề cửa sổ/báo cáo. Hiện xuất xlsx của repo lưu chuỗi dạng text nên chưa khai thác được (xem Điểm tốt), CSV thì có `_an_toan_cho_excel`. | Áp cùng bộ chuẩn cho `name`; bỏ khoảng trắng/tab/CR đầu rồi mới kiểm. | Không. |
| 4.8 | nhỏ | `js/075_workspace.js:693` | `wsTaoWorkspace` tạo xong, nếu `open_workspace` lỗi thì wizard vẫn ở bước cuối, danh sách không làm mới. | Bấm "Tạo" lại → `name-2`, workspace trùng chồng chất. | Làm mới danh sách và khoá nút sau khi tạo thành công. | Không (JS). |
| 4.9 | nhỏ | `js/075_workspace.js:168` | `list_workspaces` lỗi thì chỉ toast; màn chọn bắt buộc (`wsCoTheDong=false`) còn lại lớp rỗng không đóng được; `list_templates` lỗi thì nút "Tạo mới" không làm gì (`if (!mau) return`). | Lỗi tạm thời lúc khởi động nhiều workspace → kẹt sau lớp trống. | Vẽ trạng thái lỗi kèm nút "Thử lại". | Không (JS). |
| 4.10 | nhỏ | `js/075_workspace.js:436` | Wizard không kiểm luật "nhãn không bắt đầu bằng `= + - @`" của backend; lỗi chỉ hiện ở bước cuối dưới dạng `ws_du_lieu_sai`. | Nhãn `-Nhân viên` qua bước 2–4, "Tạo" mới báo lỗi chung, không chỉ ô sai. | Kiểm ở `wsLoiBuoc`. | Không (JS). |

---

## Điểm tốt

1. **Giải nén workspace `.zip` chặt** (`workspace.py:nhap_zip`): kiểm tên MỌI mục (zip slip), từ chối liên kết tượng trưng và mục mã hoá, kiểm lại `commonpath` trên đường dẫn thật, đếm **byte thật** khi chép (không tin `file_size` khai trong tiêu đề → chống zip bomb), bỏ tệp phụ SQLite (`-journal/-wal/-shm`) để tránh phát lại nhật ký cài sẵn, giải vào thư mục tạm rồi `os.replace` (hỏng giữa chừng không để lại workspace dở), nghiêm ngặt khi đọc cấu hình để không ghi đè nhãn thật.
2. **Nạp `.xlsx`** (`api_nhap.py:_soat_co_xlsx`): soát cỡ tệp và tổng cỡ giải nén bằng mục lục zip trước khi mở bằng openpyxl.
3. **Máy chủ dự phòng**: chỉ nghe `127.0.0.1`, kiểm `Host` chống DNS rebinding, token cho cả `/__api__/` và `/__closed__`, chặn gọi phương thức bắt đầu bằng `_`.
4. **Xuất `.xlsx` không gây công thức**: đã thử xuất Sổ với tên CLB `=HYPERLINK(...)` và tên em `+cmd|' /C calc'!A0` → mọi ô đọc lại là kiểu chuỗi (`data_type='s'`), không phải công thức. CSV xuất đi qua `_an_toan_cho_excel`, và nạp lại có bước gỡ lớp bảo vệ đó (`api_nhap.py:89`).
5. **SQL**: các chỗ ghép chuỗi (`%s` ở `api_quan_ly.py:1387/1403`, `rbda_priority_pipeline.py` PRAGMA/ALTER) chỉ ghép tên bảng/cột lấy từ danh sách cố định (`_RESET_BANG`, schema); dữ liệu người dùng đều qua tham số `?`. `api_quan_ly.py:808` ghép `dk` là hằng số.
6. **XSS**: các chỗ `innerHTML` lấy mẫu ở `js/04_nhap_tai_cho.js` đều qua `esc()` (tên, mã, tên CLB).
7. **Hiệu năng nạp Sổ 800 em × 20 CLB (mỗi em 10 nguyện vọng)**: xem trước 0,23 s; nạp 0,30 s; **nạp lặp lần hai** 0,39 s, đều `ok` (không lỗi mã trùng ở lần lặp). Nạp Sổ qua đường hai hàng tiêu đề hoạt động.
8. **Sao lưu trước thao tác phá** (`reset`, xoá hàng loạt): kiểm xác nhận TRƯỚC, sao lưu SAU, để không đẻ tệp rác khi gọi nhầm; `delete_workspace` chuyển vào `_trash` chứ không xoá thẳng.

## Chưa kiểm hoặc ngoài khả năng của đợt này

- Chưa chạy giao diện Chromium cho từng lỗi JS (1.7, 1.8, 1.9, 2.2, 2.5, 3.4, 3.6…): các mục đó ghi "Không" ở cột tái hiện.
- Chưa thử hồi quy "nạp giữa chừng lỗi có rollback", BOM/NFC-NFD/ô gộp bằng tệp độc hại riêng; chỉ dựa vào bộ test hiện có (chưa chạy lại toàn bộ test trong đợt này).
- 1.1 nên được xác nhận lại trên cửa sổ `--app` thật (Chrome/Edge) trước khi sửa.

## Kết luận

| Nhóm | Kết luận |
|---|---|
| 1. Nạp Sổ / CSV / Excel | **Cần sửa** (1.1 chặn ở chế độ dự phòng; 1.4, 1.5 làm hỏng nạp/xuất với đầu vào hợp lý) |
| 2. Kiosk học sinh | **Cần bàn** (2.1: có cho kiosk xoá điểm quyết tâm đã khoá qua `submit_preferences` hay không) |
| 3. Nhập tay ở Quản lý | **Cần sửa** (3.1, 3.2, 3.5, và kẹp trang chung với 1.6) |
| 4. Chấm điểm mù + workspace | **Cần sửa** (4.1–4.5; phần giải nén zip: **Đạt**) |
