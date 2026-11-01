# CLAUDE.md — Chương trình phân bổ RB-DA (kiosk phân bổ câu lạc bộ)

> Tệp này nạp vào mọi phiên. Bối cảnh đầy đủ ở `docs/ke_hoach/` — **đọc trước khi sửa mã** (xem mục "Tài liệu cần đọc"; **chỉ đọc phần liên quan tới mục đang làm**, không đọc cả thư mục).
> Trả lời người dùng bằng **tiếng Việt**. Tên hàm, tên biến giữ nguyên như trong mã.

## Dự án là gì
- Phần mềm Windows (kiosk, chạy ngoại tuyến) phân bổ ~800 học sinh vào ~20 câu lạc bộ ở một trường phổ thông, là đề tài nghiên cứu khoa học kỹ thuật của một học sinh.
- Thuật toán: **RB-DA** = Deferred Acceptance (Gale–Shapley, học sinh đề nghị) + **dự trữ mềm** hai lượt (Kominers & Sönmez 2016) + **bốc thăm một lần dùng chung** (STB, single tie-breaking) + ưu tiên hai tầng (Tầng 1 có điểm thi: −điểm rồi STB; Tầng 2 không thi: STB).
- Ngăn xếp: Python 3.11 + SQLite (`app.db`), giao diện HTML/JS chạy trong pywebview (WebView2), có chế độ dự phòng mở bằng trình duyệt (`browser_host.py`). Đóng gói bằng PyInstaller qua GitHub Actions (workflow *Build Windows executable (rbda-kiosk)*; build tay: `build_windows.bat`).
- **Mục tiêu hiện tại của chủ dự án:** tổng quát hoá chương trình để bán cho các ngành khác ngoài CLB trường học (12 ngành đã đánh giá), và thêm khả năng xử lý thay đổi theo thời gian (em đến muộn, rút lui). Mô hình kinh doanh để sau.

## Bản đồ mã
Bảng tệp → vai trò → hàm then chốt: xem `docs/ke_hoach/CLAUDE_CHI_TIET.md` (mục "Bản đồ mã"). Định vị theo TÊN HÀM, không ghi số dòng; muốn số dòng: `grep -n "^def <tên>" <tệp>`.

## Lệnh
- Chạy test (mặc định chỉ test liên quan, xem quy tắc 2): `python -m pytest -q <tệp hoặc -k ...>` trong venv của dự án (tài liệu ghi `./.venv/bin/python -m pytest -q`; trên Windows: `.venv\Scripts\python -m pytest -q`). Toàn bộ ~22 phút trên máy 4 nhân kèm test giao diện Chromium (BAN_GIAO.md ghi ~3,5 phút; chưa giải thích được, xem `docs/ke_hoach/DOI_CHIEU_KHO_MA.md`). Lint: `ruff check .`; CI đòi phủ ≥ 85 %.
- Sinh lại thông báo lỗi JS sau khi sửa `i18n_errors.py`: `python tao_i18n_js.py`.
- Kiểm verify nhanh (tham khảo): `pip install numpy` (chỉ cho kịch bản tham khảo, KHÔNG thêm vào requirements) rồi `python docs/ke_hoach/tham_khao/kiem_verify_nhanh.py <thư mục chứa rbda_priority_pipeline.py>`. Test `tests/test_tham_khao_verify_nhanh.py` (không cần numpy) canh `verify_stability_nhanh`, `exp_resume.resume_da` / `kiem_tien_de`, `_chung.nap_rb` (thư mục: nạp thẳng tệp .py, cùng bản, bản khác, tiến trình mới, mô-đun anh em lạ; tệp không phải PyInstaller); `_chung.gen` chỉ được kiểm khi có numpy; đường nạp `.exe` được kiểm bằng một tệp PyInstaller tối thiểu dựng trong test (không có bản build thật trong kho).

## Bất biến — KHÔNG được phá
1. Cấu hình mặc định phải cho kết quả TRÙNG KHÍT với trước khi sửa (cùng dữ liệu, cùng seed): so từng dòng match_results trên 3 bộ dữ liệu × 20 seed.
2. compute_club_priority KHÔNG được nhận thứ hạng nguyện vọng hay kết cục buổi trước (ràng buộc chống nội sinh); thêm tiêu chí mới cũng không được đọc chúng.
3. Cơ chế số bốc thăm (STB): khoá sau lần chạy đầu, seed khoá cùng bộ số, sinh bằng crc32 (không dùng hash()), em đến muộn chèn ngẫu nhiên đều nhưng giữ thứ tự tương đối của em cũ.
4. run_history không bao giờ bị ghi đè hay xoá; mọi lần chạy ghi thêm một dòng.
5. Pipeline giữ nguyên thứ tự: sao lưu → kiểm dữ liệu → khoá seed/STB → giải → sanity/verify → ghi trong MỘT giao dịch → xuất; lỗi thì rollback.
6. Hợp đồng giữa giao diện và backend là {ok, data, errors} với errors = [{code, params}]; thông báo lỗi chỉ có một nguồn (i18n_errors.py → tao_i18n_js.py).
7. Hợp đồng cột CSV (club_id, student_id, test_club_k, score_k, pref_k, <buoi>_pref_k) chỉ đổi khi mục tương ứng ghi rõ; di_tru_schema phải chạy lặp an toàn và có sao lưu.
8. Mọi hàm lựa chọn mới phải qua test thay thế được (substitutability) và luật tổng cầu trước khi đăng ký; nếu không thoả, phải báo rõ 'không bảo đảm ổn định'.

## Quy tắc làm việc
1. Mỗi thay đổi gắn với **một mã mục** trong sổ đăng ký (Z1…G5). Không làm việc ngoài sổ khi chưa hỏi.
2. **Test trước**: viết test thất bại theo trường `kiem_nhan`, rồi sửa tối thiểu, rồi chạy **chỉ các test liên quan** tới mục đang làm (`python -m pytest -q tests/test_<tên>.py` hoặc `-k <từ khoá>`). KHÔNG chạy toàn bộ bộ test (~22 phút) trừ khi Truong yêu cầu rõ; CI trên GitHub sẽ chạy toàn bộ.
3. Tham số mới phải có **mặc định = hành vi cũ**; cấu hình mặc định phải cho kết quả **trùng khít** (so từng dòng `match_results`, 3 bộ dữ liệu × 20 seed).
4. Không xoá các chế độ đối chứng (`stb_tuan`, `stb_co_bu`, A1/A3 trong TN7): script đo trong `du_lieu_test/` cần chúng để tái lập số liệu.
5. Hàm lựa chọn mới phải qua test **thay thế được** và **luật tổng cầu**; không qua thì ghi rõ "không bảo đảm ổn định" và dùng chế độ đo lường (mục A12).
6. Sau mỗi mục: cập nhật `CHANGELOG.md` (mã mục, tệp, test mới) và đánh dấu tiến độ trong `docs/ke_hoach/TIEN_DO.md`.
7. Dừng và hỏi khi: một bất biến xung đột với mục; số dòng/hiện trạng trong sổ lệch hẳn so với kho; cần thêm thư viện; cần đổi hợp đồng cột CSV hay schema ngoài phạm vi mục.
8. Trước khi push: chạy skill `soat-ma` (`.claude/skills/soat-ma/`): một lệnh `kiem_nhanh.py` cho phần máy làm được, rồi soát theo bốn tầng trong `SKILL.md`. Không subagent; chỉ báo cáo trừ khi được giao sửa.
9. **Bàn giao theo nhánh**: mỗi nhánh (tính năng) có một tệp `docs/phien/<nhánh>.md` (mẫu: `docs/phien/_TEMPLATE.md`, tiếng Anh, tối đa 150 dòng). Khi ngữ cảnh vượt ~400k token, SAU KHI xong lượt hiện tại, phiên ghi lại trạng thái vào tệp đó rồi dừng để mở phiên mới; hook Stop `.claude/hooks/handoff_khi_day_ngu_canh.py` nhắc việc này.
10. **NO SUBAGENT**: không tự gọi subagent / Agent tool (mỗi subagent khởi động nguội, tốn token). Tự dùng Read/Grep/Bash trực tiếp. Chỉ dùng khi Truong nói rõ.
11. **Vai trò mô hình** (mỗi vai một phiên riêng, cầu nối là tệp bàn giao): Opus lập kế hoạch (ghi vào mục Plan), Sonnet viết mã và đánh dấu Plan, Haiku chỉ đọc / tìm / tóm tắt, không sửa tệp. Phiên Opus đầu tiên của nhánh mới tạo `docs/phien/<nhánh>.md` từ `_TEMPLATE.md` và điền Goal + Plan.

## Liêm chính học thuật (đây là đề tài của học sinh)
- **Mọi số liệu kiểm chứng là dữ liệu MÔ PHỎNG.** Không bao giờ viết như thể là khảo sát thật.
- Các phần **nhận xét, diễn giải, kết luận** trong báo cáo đề tài do **học sinh tự viết** — không soạn hộ những phần đó. Tài liệu vận hành, mã, test thì được.
- Trợ giúp của AI được ghi trong nhật ký AI của dự án; ghi thêm khi làm việc lớn.
- Tên đúng là **Gale–Shapley** (báo cáo gốc có chỗ viết "Sharpley").

## 12 ngành đích và thứ tự làm chung
Bảng 12 ngành (DT, KTX, SK, NT, YT, VL, KT, HP, TS, NS, LG, TC) và chuỗi Z6 → … → G5: xem `docs/ke_hoach/CLAUDE_CHI_TIET.md`. Thứ tự riêng từng ngành lấy từ `nganh[].ke_hoach` trong `ke_hoach_thay_doi.json` — làm theo, không tự sắp lại.

## Tài liệu cần đọc (theo thứ tự)
0. `docs/phien/<tên nhánh, "/" thay bằng "__">.md` — **đọc đầu tiên nếu có**: việc đang dở, việc tiếp theo, quyết định cần nhớ (bàn giao theo nhánh, tiếng Anh).
1. `docs/ke_hoach/BOI_CANH_DU_AN.md` — toàn bộ bối cảnh: lịch sử phân tích, phát hiện, số đo, lý thuyết, câu hỏi mở.
2. `docs/ke_hoach/SO_DANG_KY_33_MUC.md` — 33 mục sửa: hiện trạng, thay đổi, rủi ro, kiểm nhận, áp dụng cho ngành nào.
3. `docs/ke_hoach/ke_hoach_thay_doi.json` — cùng dữ liệu, dạng máy đọc; `nganh[].ke_hoach` là thứ tự làm đã tính phụ thuộc — **làm theo, không tự sắp lại**.
4. Chỉ khi cần: danh sách tài liệu trong kho và tệp tham khảo — xem cuối `docs/ke_hoach/CLAUDE_CHI_TIET.md`.
