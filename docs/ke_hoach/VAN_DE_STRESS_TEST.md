# Các vấn đề tìm thấy khi stress test (sau A13.8)

> **Trạng thái: bản cuối của đợt stress test.** Số đo đầy đủ và bảng TRƯỚC / SAU A13.9 nằm ở `docs/ke_hoach/BAO_CAO_STRESS_TEST.md`. Các mục 1 – 10 bên dưới giữ nguyên mô tả **TRƯỚC A13.9** (đo trên đỉnh A13.8); cột "Hiện nay" cho biết trạng thái trên đỉnh A13.9 (`1fcef81`).
>
> Mọi dữ liệu là **MÔ PHỎNG** (seed cố định). Chỉ đo và báo cáo; không sửa mã sản phẩm. Không có lỗi mức **chặn** (sập, mất dữ liệu, phá bất biến) trong cả 8 nhóm.
>
> Mức: **nên sửa** / **nhỏ** / **cần Truong quyết** / **ghi nhận**.

## Tổng hợp

| # | Mức | Nhóm | Vấn đề ngắn | Hiện nay (A13.9) | Đã sửa ở commit |
|---|---|---|---|---|---|
| 1 | nên sửa | 3 | CSDL bị khoá: báo sai nguyên nhân và chờ 15 – 30 giây | **Hết** phần mã lỗi sai (`csdl_dang_ban`, 2,5 s); còn 15 – 17,6 s ở `list_students_admin`, `reset_data`, `run_pipeline` (N3) | 814b5d4 |
| 2 | nên sửa | 8 | Máy chủ dự phòng không timeout kết nối | **Hết** (thả sau 45 s) | 1dac117 |
| 3 | nhỏ | 8 | Token không ASCII: đóng kết nối, không trả phản hồi | **Hết** (403) | 1dac117 |
| 4 | nhỏ | 8 | `loi_ung_dung.txt` tăng không giới hạn | **Hết** (0,4 B/yêu cầu) | 1066456 |
| 5 | nhỏ | 8 | Phản hồi lỗi có thông điệp ngoại lệ Python nguyên văn | **Hết** (chỉ tên kiểu) | 1dac117 |
| 6 | cần Truong quyết | 8 | Đường xuất tuyệt đối ghi đè tệp có sẵn | **Hết** (không ghi đè, `x (2).ext`); phát sinh N1 | bf67701 |
| 7 | nhỏ | 8 | Zip workspace: không trần số tệp, nhận tên trùng | **Hết** phần chính; tên NUL còn (vô hại) | 4a94376 |
| 8 | ghi nhận | 2 | Sổ 0 học sinh được nhận không cảnh báo | **Hết** (cảnh báo `so_nhap_canh_bao_khong_co_hs`) | bc36bb7 |
| 9 | ghi nhận | công cụ | `sinh_ngau_nhien` chỉ có 20 chủ đề CLB | **Hết** ở phía skill | 30f6d82 |
| 10 | ghi nhận | mốc | 2 test bị bỏ qua vì môi trường đo thiếu `numpy` | Không đổi (đúng theo `CLAUDE.md`) | — |

**Phát hiện mới trên A13.9** (chi tiết ở báo cáo, mục 10): N1 nhỏ (xuất vào đường là thư mục → tệp `ngoai (2)` cạnh thư mục), N2 nhỏ (`wharton_nhat_ky` thêm 801 dòng mỗi vòng nạp → xoá → nạp; `app.db` 1,4 → 16,7 MB sau 100 vòng), N3 nhỏ (còn chờ 15 s ở `list_students_admin` / `reset_data` khi CSDL bị khoá), N4 nên xem (5.000 × 100: lần đầu mở thẻ Kết quả ≈ 13,6 s, ba lần lật trang đầu 8 – 20 s; lặp lại 3 / 3 lần).

**Cập nhật A13.11** (sửa N1 – N4; đo lại s3 / s5 / s6 / s8 sau sửa, số trước / sau ở `CHANGELOG.md`):

| # | Hiện nay (A13.11) | Đã sửa ở commit |
|---|---|---|
| N1 | **Hết** — lỗi `xuat_duong_la_thu_muc`, không đẻ tệp `ngoai (2)` | 902cb6b, 02c3089 |
| N2 | **Hết** — một dòng tóm tắt mỗi lần nạp; `app.db` 16,7 → 1,66 MB sau 100 vòng; còn 2 test cũ đỏ chờ Truong quyết | 442725f |
| N3 | **Hết** — mọi hàm báo `csdl_dang_ban` sau ≤ 3 s (trước 15 – 17,6 s); giao diện nói rõ "CSDL đang bận" | 49c7319 |
| N4 | **Hết** — nguyên nhân là 13 lời gọi đọc cùng lúc tranh GIL, không phải vẽ DOM; lần đầu mở Kết quả 13,6 → 1,06 s, trang chậm nhất 6,5 → 0,34 s; 800 × 20 không chậm đi | 2fb9680 |

---

## 1. CSDL bị khoá: thông báo sai nguyên nhân, chờ lâu — **nên sửa** (nhóm 3)

- **Hiện tượng.** Khi một kết nối khác giữ khoá độc quyền trên `app.db`, các lời gọi ghi trả lỗi `ws_cau_hinh_hong` ("cấu hình workspace hỏng") sau đúng 15 giây. Riêng `run_pipeline` mất 30 giây. Thực tế cấu hình không hỏng; CSDL chỉ đang bận.
- **Đo được (lần chạy thử).** `submit_preferences` 15,03 s; `import_so_nhap` 15,03 s; `run_pipeline` 30,08 s; `list_students_admin` 15,03 s (báo `error_reading_student_list`); `reset_data` 15,05 s (báo `error_resetting_data`). Cả hai thông báo kia đúng loại, riêng ba hàm đầu báo sai là "cấu hình hỏng".
- **Tốt.** Không ghi nửa chừng (CSDL giống hệt trước và sau), `integrity_check = ok`, mở khoá xong mọi thứ chạy lại bình thường.
- **Tái hiện.** Mở kết nối khác, `BEGIN EXCLUSIVE`, rồi gọi `api.submit_preferences(...)`. Script: `python du_lieu_test/stress/s3_dong_thoi.py` (phép D).
- **Đề xuất.** Khi `_luat_nghiem()` gặp `sqlite3.OperationalError: database is locked`, trả một mã riêng kiểu "CSDL đang bận, thử lại" thay vì gộp vào `ws_cau_hinh_hong`. Cân nhắc rút busy timeout cho thao tác đọc cấu hình.

## 2. Máy chủ dự phòng không có timeout kết nối — **nên sửa** (nhóm 8)

- **Hiện tượng.** `browser_host.py` dùng `ThreadingHTTPServer` nhưng không đặt timeout cho socket. Mỗi kết nối gửi dở tiêu đề (hoặc khai `Content-Length: 1000` mà không gửi đủ thân) giữ một luồng cho tới khi bên kia tự đóng.
- **Đo được.** 100 kết nối gửi dở tiêu đề: số luồng của máy chủ tăng 3 → 103 và vẫn 103 sau 30 giây. Máy chủ vẫn phục vụ được yêu cầu khác lúc đó. Yêu cầu có `Content-Length` lớn hơn thân thật không bao giờ được trả lời (treo tới khi client bỏ).
- **Mức ảnh hưởng.** Chỉ máy cục bộ nghe 127.0.0.1 và cần Host hợp lệ nên rủi ro thấp; nhưng một trình duyệt hay tiện ích lỗi cũng có thể gây rò luồng.
- **Tái hiện.** `python du_lieu_test/stress/s8_bao_mat.py` (phần "Kết nối treo", T3).
- **Đề xuất.** Đặt `timeout` cho handler (ví dụ 30–60 giây) để socket đọc dở bị cắt.

## 3. Token không phải ASCII làm máy chủ đóng kết nối không trả lời — **nhỏ** (nhóm 8)

- **Hiện tượng.** Tiêu đề `X-Kiosk-Token` chứa ký tự không phải ASCII (hoặc `?t=%C3%A9` trên URL `GET`) làm `secrets.compare_digest` ném `TypeError`. Ngoại lệ không được bắt trong `do_POST`/`do_GET`; kết nối bị đóng, không có phản hồi HTTP; `socketserver` in vết ngăn xếp ra stderr.
- **Đo được.** 4 biến thể (UTF-8 thô trong tiêu đề, byte 0xFF/0xFE/0x80, `GET /index.html?t=é`, `GET /__alive__?t=é`) đều "đóng kết nối không trả lời". Token sai thông thường trả 403 đúng.
- **Mức ảnh hưởng.** Không lộ gì, không sập; chỉ không đúng hợp đồng (phải trả 403) và để lại vết ngăn xếp trong stderr.
- **Tái hiện.** `python du_lieu_test/stress/s8_bao_mat.py` (T2).
- **Đề xuất.** So sánh token bằng `compare_digest` trên `bytes` (mã hoá `latin-1`/`utf-8` trước), hoặc bọc `_authorized`/`_token_trong_url` bằng `try/except TypeError → False`.

## 4. Nhật ký lỗi tăng không giới hạn — **nhỏ** (nhóm 8)

- **Hiện tượng.** Mỗi yêu cầu API gây ngoại lệ ghi một khối vào `loi_ung_dung.txt` cạnh `app.db`, không có trần kích thước hay xoay vòng.
- **Đo được.** 200 yêu cầu JSON hỏng: nhật ký tăng 6.280 → 167.080 byte (~804 byte/yêu cầu). 2.000 yêu cầu ≈ 1,6 MB. (Bản chạy đầy đủ dùng 2.000 yêu cầu.)
- **Mức ảnh hưởng.** Người giữ token (máy cục bộ) có thể làm đầy đĩa từ từ. Rủi ro thấp.
- **Tái hiện.** `python du_lieu_test/stress/s8_bao_mat.py` (T7).
- **Đề xuất.** Đặt trần (ví dụ cắt về 1 MB, giữ phần cuối) trong `chan_doan.ghi_ngoai_le_canh_db`, và bỏ qua bản ghi trùng liên tiếp.

## 5. Phản hồi lỗi chứa thông điệp ngoại lệ Python nguyên văn — **nhỏ** (nhóm 8)

- **Hiện tượng.** Lỗi bất ngờ trả `loi_ngoai_du_kien` với `detail = str(e)`. Ví dụ với `args` sai kiểu: `PipelineAPI.get_run_history() takes from 1 to 4 positional arguments ...`, `api.PipelineAPI.get_run_history() argument ...`; với JSON hỏng: `Expecting property name enclosed in double quotes...`; với byte rác: `'utf-16-le' codec can't decode byte ...`.
- **Không thấy** vết ngăn xếp hay đường dẫn máy trong phần `errors` của các phản hồi đã đo (đã quét `Traceback`, `File "`, `/home/`, thư mục cát, `.py", line`). Chỉ lộ tên lớp/hàm nội bộ.
- **Tái hiện.** `python du_lieu_test/stress/s8_bao_mat.py` (T3, T7).
- **Đề xuất.** Chỉ trả `detail` rút gọn (tên kiểu ngoại lệ), phần đầy đủ để trong nhật ký.

## 6. Đường xuất tuyệt đối được tôn trọng nguyên văn — **cần Truong quyết** (nhóm 8)

- **Hiện tượng.** `export_ket_qua` (và các hàm xuất khác) dùng `_duong_xuat`: đường **tương đối**, kể cả `../../x.xlsx`, bị ép vào thư mục Tải xuống bằng `basename` (kiểm: không tệp nào thoát khỏi thư mục cho phép). Đường **tuyệt đối** được ghi đúng nơi đó, **kể cả ghi đè tệp có sẵn**.
- **Đo được.** Tệp mẫu "nạn nhân" `NAN_NHAN.xlsx` đặt sẵn ngoài thư mục cho phép đã bị ghi đè qua `export_ket_qua("/…/NAN_NHAN.xlsx")`. Tệp mới ngoài thư mục cho phép: `ABS.xlsx`, `NAN_NHAN.xlsx` (đều do đường tuyệt đối).
- **Bối cảnh.** Mã ghi rõ đây là ý muốn của người chọn đường dẫn qua hộp thoại. Nhưng qua máy chủ dự phòng, mọi bên giữ token đều gọi được với đường tuyệt đối bất kỳ (ví dụ trang web độc hại không có token thì không gọi được; chỉ trang của chính phần mềm).
- **Tái hiện.** `python du_lieu_test/stress/s8_bao_mat.py` (T6).
- **Lựa chọn cho Truong.**
  1. Giữ nguyên (đường tuyệt đối là thiết kế); ghi vào tài liệu bảo mật.
  2. Từ chối đường tuyệt đối khi gọi qua máy chủ dự phòng, chỉ cho phép trong cửa sổ pywebview (có hộp thoại chọn tệp).
  3. Cho phép nhưng **không ghi đè** tệp có sẵn (đổi thành `x (2).xlsx` như đường tương đối).
  - Đề xuất: **3** (ít ảnh hưởng người dùng, chặn ghi đè âm thầm).

## 7. Nhập workspace `.zip`: không trần số tệp, trần dung lượng cao — **nhỏ** (nhóm 8)

- **Đã chặn đúng.** zip slip (`../`, `..\`), đường tuyệt đối, ổ đĩa, symlink, `app.db` không phải SQLite, thiếu `app.db`, thư mục lồng 2.000 cấp: đều bị từ chối; không tệp nào xuất hiện ngoài thư mục workspace.
- **Được nhận (cần biết).** Zip 4,9 MB chứa 50.000 tệp rỗng: nhận, mất 8,2 giây (RSS máy chủ 50 → 55 MB). Zip bom giải nén tới 100 MB (bản `--nhanh`) được nhận; bản đầy đủ thử 700 MB (trần 500 MB, kỳ vọng bị từ chối; kết quả sẽ có ở báo cáo cuối). Tên có byte NUL hoặc tên tệp trùng nhau cũng được nhận (vô hại: Python cắt tên tại NUL).
- **Tái hiện.** `python du_lieu_test/stress/s8_bao_mat.py` (T5).
- **Đề xuất.** Thêm trần số tệp (ví dụ 1.000) và cân nhắc hạ trần giải nén; từ chối tên trùng.

## 8. Sổ không có học sinh vẫn được nhận, không cảnh báo — **ghi nhận** (nhóm 2)

- **Quan sát (TRƯỚC A13.9).** Sổ 0 học sinh được nhận với `ok = true`, không cảnh báo. **Đính chính:** ghi nhận ban đầu của em nói cả 0 CLB cũng "được nhận"; thực ra sổ 0 CLB bị từ chối bằng danh sách lỗi `so_nhap_clb_khong_co` (bản xem trước trả `ok = true` kèm danh sách `loi`, em đã đọc nhầm là chấp nhận). Bộ phân loại của `s2` đã được sửa để coi "xem trước có `loi`" là từ chối.
- **Hiện nay.** 0 học sinh: nhận kèm cảnh báo `so_nhap_canh_bao_khong_co_hs`; `run_pipeline` sau đó `ok`.
- **Tái hiện.** `python du_lieu_test/stress/s2_du_lieu_ban.py --lai khong_em:0`.

## 9. Công cụ sinh dữ liệu giới hạn 20 chủ đề — **ghi nhận** (nhóm 1, 5, 7)

- `sinh_ngau_nhien` của kỹ năng `sinh-du-lieu-clb` chỉ có 20 chủ đề, nên không dựng được 50 hay 100 CLB. Script đo nối thêm chủ đề `CLB Mở rộng NNN` vào danh sách **trong bộ nhớ** của tiến trình đo (không sửa tệp kỹ năng). Nên biết khi đọc số đo ở các bậc 2.000×50 và 5.000×100: tên CLB là tên sinh thêm.

## 10. Hai test bị bỏ qua vì thiếu `numpy` — **ghi nhận** (mốc)

- Test toàn bộ có Chromium: **2859 passed, 3 skipped, 26 phút 10 giây** (máy 4 nhân, 15,7 GB RAM).
- 3 test bị bỏ qua: 2 do `.venv` không có `numpy` (đúng như `CLAUDE.md`: chỉ cài khi chạy kịch bản tham khảo, không thêm vào requirements); 1 do cần người dùng thường trên POSIX (môi trường đo chạy bằng root).

---

## Đã kiểm và **không** thấy vấn đề (xác nhận bằng bản đầy đủ, xem báo cáo)

- **Đồng thời (nhóm 3, phép A/B).** 4 và 16 luồng `submit_preferences` / `submit_wharton`: không ngoại lệ, không lỗi khoá, em ghi cùng lúc ra đúng một bản đã gửi. `run_pipeline` hai lần song song (cùng đối tượng, và hai tiến trình): đều ok, `run_history` thêm đúng 2 dòng, `integrity_check = ok`.
- **Đĩa đầy giả lập (phép E).** Ghi vượt giới hạn khiến `run_pipeline` rollback đúng (CSDL không đổi, không để lại bản sao lưu dở); `integrity_check = ok`.
- **Đúng đắn thuật toán (nhóm 4).** 14 bộ ngẫu nhiên đầu: 0 vấn đề. Bộ kiểm tự thử: phá cố ý một CSDL tạm thì bắt được lỗi vượt chỉ tiêu, dự trữ sai nhóm và cặp phá vỡ. Đổi seed sau khi khoá bị từ chối đúng (`hat_giong_da_khoa`), số bốc thăm không đổi.
- **Workspace (nhóm 7).** 8 cấu hình thử (điểm theo người, `priority = tier`, chế độ nhóm cứng, nhãn ngành khác): nạp, chạy, xuất đều ổn, 0 vấn đề kiểm.
- **Giao diện (nhóm 5, 800×20).** 0 lỗi console, 0 lỗi trang; vòng đổi tab / ngôn ngữ 10 lần không làm heap tăng đáng kể (+0,31 MB).
- **Máy chủ dự phòng.** Giữ nguyên danh sách trắng tệp tĩnh (`/app.db`, `/api.py`, `/.git/config`... đều 404); phương thức `_...`, dunder, thuộc tính không gọi được đều bị từ chối; slug workspace có `..` bị từ chối; thân > 32 MB trả 413; 1.000 yêu cầu/giây (đạt 537 rps ở bản thử): máy chủ còn sống.
