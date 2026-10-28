---
name: soat-ma
description: Soát mã trước khi push, bằng tay và bằng một lệnh tự kiểm — theo bốn tầng (lõi thuật toán, backend, giao diện, vệ sinh/tài liệu/test). Dùng khi Truong nói "soát mã", "kiểm trước khi push", "review", "code review", "tự kiểm", "soát lại diff", hoặc khi sắp push một mục đã làm xong. Không dùng subagent, chỉ báo cáo trừ khi được giao sửa.
---

# Soát mã trước khi push (`soat-ma`)

> **Đường dẫn lệnh.** Trong kho: `.claude/skills/soat-ma/scripts/kiem_nhanh.py`. Chạy từ thư mục gốc kho.
> Quy tắc làm việc trong `CLAUDE.md`: **trước khi push, chạy skill này.**

Mục đích: bắt lỗi TRƯỚC khi nó vào nhánh chung. Soát gồm hai phần: **máy làm được** (một lệnh, ĐẠT / KHÔNG ĐẠT) và
**mắt người làm** (checklist bốn tầng bên dưới). Phần máy không thay phần mắt.

## 1. Luật (không có ngoại lệ nếu Truong không nói khác)

1. **KHÔNG dùng subagent.** Không Agent / Task, không fork, không mở phiên con, không `/code-review` mức cao (nó dùng
   subagent). Tự đọc từng tệp.
2. **Chỉ báo cáo, không sửa mã.** Không đổi `.py`, `.js`, `.html`, `.css`, test khi đang soát. Chỉ được tạo / sửa báo
   cáo soát. Lỗi tìm được: Truong duyệt, rồi sửa ở vòng sau (có mục riêng trong sổ đăng ký).
   Ngoại lệ duy nhất: Truong **giao** việc sửa.
3. **Gây hỏng tạm để thử test thì phải hoàn tác** và kiểm `git status` sạch ngay sau (xem mục 5, tầng 4).
4. Dữ liệu thử là dữ liệu MÔ PHỎNG. Không viết nhận xét / kết luận hộ đề tài (xem `CLAUDE.md`, mục Liêm chính học thuật).
5. Không tạo PR. Không push khi chưa được phép; push thường, không `--force`; `git pull --rebase` trước khi push.
6. Soát lớn (nhiều tầng): **dừng sau mỗi tầng**, ghi báo cáo tầng đó, commit, rồi chờ Truong nói "tiếp".
7. Tiếng Việt. Tên hàm, biến giữ nguyên như trong mã.

## 2. Phạm vi

- Diff so với `main`: `git diff main...HEAD --stat`, rồi đọc từng tệp đổi (`git diff main...HEAD -- <tệp>`).
  (Bản sao chưa có `main` cục bộ thì dùng `origin/main`.)
- Thêm: mọi hàm CŨ mà mã mới gọi vào hoặc bị sửa (lần theo lời gọi **một bậc**). Lập danh sách này đầu báo cáo.
  Danh sách quá **40 hàm** thì hỏi Truong có thu hẹp không.
- Ngoài phạm vi: thấy lỗi lớn thì ghi MỘT dòng ở mục "Ngoài phạm vi", không đào sâu.

## 3. Phần máy: một lệnh

```bash
python .claude/skills/soat-ma/scripts/kiem_nhanh.py            # bảy mục, so với main
python .claude/skills/soat-ma/scripts/kiem_nhanh.py --co-so origin/main --chi ruff,i18n_khoa
```

| Mục | Kiểm gì |
|---|---|
| `ruff` | `ruff check .` sạch |
| `chu_cam` | chữ hiển thị (`i18n.js`, `i18n_errors.py`, `index.html` — chữ không phải dự phòng của `data-i18n`) không có xưng hô cấm ("bạn", "các em", "em"; "you", "your") và không lộ tên nội bộ "Wharton" |
| `ma_loi_js` | mọi mã lỗi JS nhắc tới (`code: "…"`) có trong `i18n_errors.py` (hoặc trùng một khoá UI của `i18n.js`) |
| `i18n_loi_khop` | `i18n_loi.js` khớp từng byte với bản sinh lại từ `i18n_errors.py` |
| `i18n_khoa` | `i18n.js`: tập khoá tiếng Việt = tập khoá tiếng Anh, không giá trị rỗng |
| `trung_khit` | cấu hình mặc định cho kết quả trùng khít với `main`: từng dòng `match_results` và số bốc thăm, 3 bộ dữ liệu × 5 seed (bất biến 1) |
| `khong_sua_nhat_ky` | không `UPDATE` / `DELETE` / `DROP` trên `run_history`, `wharton_nhat_ky` (kể cả tên bảng nằm trong danh sách `_RESET_BANG`-kiểu mà mã duyệt để xoá) (bất biến 4) |

- Mã thoát 0 khi mọi mục đã chạy đều ĐẠT.
- **Mục không chạy được (thiếu ruff, không tìm thấy nhánh so sánh) tính là KHÔNG ĐẠT kèm lý do**, không bỏ qua im lặng.
- `--bo-qua mục` chỉ dùng khi có lý do chính đáng, và lý do phải ghi vào báo cáo.
- KHÔNG ĐẠT thì: sửa (nếu được phép) hoặc ghi thành phát hiện. Không push khi còn KHÔNG ĐẠT chưa giải thích.

Ngoài bảy mục trên, chạy thêm:

```bash
python -m pytest -q                                  # toàn bộ test (kèm giao diện nếu có Chromium)
RBDA_TEST_CHROMIUM=$(ls /opt/pw-browsers/chromium-*/chrome-linux64/chrome | head -1) python -m pytest -q -rs
```

Ghi lại số đã qua / bỏ qua. Mọi ca `SKIPPED` phải biết lý do (thiếu `numpy` ở kịch bản tham khảo và quyền người dùng
trên POSIX là hai lý do đã biết; thiếu Chromium thì test giao diện bị bỏ qua — phải cài).

## 4. Cách ghi một phát hiện

Mỗi phát hiện một dòng:

`| # | Mức | Tệp:dòng | Hàm | Vấn đề | Đường xảy ra (đầu vào cụ thể → kết quả sai) | Đề xuất sửa | Chắc chắn? |`

- **Mức:** `chặn` (sai kết quả, mất dữ liệu, phá bất biến, lỗ hổng) · `nên sửa` (sai ở trường hợp hiếm, khó bảo trì có hại)
  · `nhỏ` (kiểu cách).
- **Chắc chắn?:** `đã tái hiện` (có lệnh hay đoạn thử chứng minh, dán vào báo cáo) · `suy luận`. Lỗi `chặn` phải cố tái hiện.
- Không ghi cảm nhận chung chung. **Không có đường xảy ra cụ thể thì không phải phát hiện.**
- Được viết script thử ở thư mục tạm (không commit) để tái hiện.
- Phát hiện `chặn` đã tái hiện: báo Truong ngay, kể cả giữa tầng.

## 5. Phần mắt: checklist bốn tầng

Mỗi mục là một câu hỏi phải trả lời bằng chứng cứ (lệnh, số đo, ảnh), không bằng "có vẻ ổn".

### Tầng 1 — Lõi thuật toán
1. **Bất biến 2:** thứ hạng nguyện vọng và kết cục buổi trước KHÔNG đi vào khoá ưu tiên, ở mọi nhánh. Thử hoán vị nguyện vọng,
   giữ nguyên dữ liệu khác: thứ tự ưu tiên của mọi CLB phải y nguyên.
2. Khoá ưu tiên đúng thứ tự mong đợi (tiêu chí mới đứng đúng chỗ so với số bốc thăm).
3. **Tắt tính năng → đường cũ, không đổi một phép so sánh** (`trung_khit` + một ca tay khi bật so với tính tay).
4. **Bất biến 8:** hàm lựa chọn mới vẫn là thứ tự chặt cố định (thay thế được, luật tổng cầu); không thì ghi rõ "không bảo đảm ổn định".
5. Bộ kiểm chứng ổn định (`verify_stability`) dùng CÙNG ưu tiên với lúc giải; thử ngẫu nhiên hàng trăm ca, có và không các
   chế độ phụ (nhóm cứng, bỏ dự trữ).
6. Biên: điểm 0, điểm bằng nhau, thiếu dòng, đổi tầng giữa chừng, vắng thi, nhiều buổi, số âm / không nguyên / `NaN` / `bool`.
7. **Bất biến 3:** không sinh lại / đổi số bốc thăm; em đến muộn vẫn chèn đúng.

### Tầng 2 — Backend
1. **Bất biến 5:** thứ tự sao lưu → kiểm → khoá → giải → verify → ghi MỘT giao dịch → xuất. Chứng minh rollback bằng
   **lỗi giả ném SAU lần ghi cuối** (sau mọi dòng ghi, ngay trước commit), rồi so ảnh chụp mọi bảng liên quan. Lỗi ném
   TRƯỚC dòng ghi không chứng minh gì về rollback.
2. **Bất biến 4:** `run_history` và mọi bảng nhật ký chỉ ghi thêm (`khong_sua_nhat_ky` + đọc tay).
3. **Bất biến 6:** mọi API trả `{ok, data, errors}`, `errors = [{code, params}]`; mã lỗi có trong `i18n_errors.py`,
   `i18n_loi.js` sinh lại.
4. **Bất biến 7:** `di_tru_schema` chạy hai lần an toàn, có sao lưu; DB tạo bằng mã cũ mở được (tạo bằng
   `git worktree` / `git archive` của nhánh cũ).
5. **Khoá:** liệt kê MỌI đường làm đổi dữ liệu được khoá, không chỉ cửa chính — cả đường "phụ" (tỉa theo thay đổi liên quan, nạp
   tệp, sửa ở Quản lý, đổi ô liên quan) — rồi thử từng đường khi đang khoá.
6. Thao tác hàng loạt: không nguyên tử thì đã sao lưu và ghi nhật ký chưa; có đọc ảnh chụp cũ rồi ghi đè không.
7. Nạp tệp: ô bẩn (chữ, số thực nguyên kiểu `100.0`, số âm, ô gộp, thiếu cột) không làm sập và không nuốt dữ liệu im lặng.
8. SQL luôn tham số hoá; đường dẫn tệp xuất / nạp (đường tương đối bị rút về tên tệp; đường tuyệt đối thì ai quyết).
9. **Quyền:** hàm ghi "chỉ cho quản trị" có xác thực thật không? Docstring nói "không có đường nào cho kiosk gọi" phải
   kiểm được (ở đây mọi phương thức công khai đều gọi được qua `browser_host`).
10. Xuất: từ chối khi chưa có kết quả; lỗi khi dựng một trang không được nuốt thành trang trống `ok`.

### Tầng 3 — Giao diện
Chạy giao diện THẬT (`browser_host` + Chromium, Playwright) với bộ mô phỏng hợp lệ, **ba vai** (học sinh ở kiosk, giáo viên,
quản trị). Dùng tên CLB / tên em chứa `<img src=x onerror=…>` để thử XSS. Chụp ảnh chỗ lỗi (không commit ảnh lớn).
1. Mọi lời gọi `window.pywebview.api.*` xử lý cả `ok=false`: chèn lỗi giả bằng `page.route` (JSON `ok=false`, HTTP 500,
   đứt mạng). Phải có thông báo dễ hiểu, không `undefined` / `[object Object]` / `NaN`.
   **`!res.ok` KHÔNG đồng nghĩa "tính năng tắt":** chỉ ẩn khi mã lỗi đúng là mã "chưa bật"; lỗi khác phải hiện.
2. Dữ liệu người dùng không vào `innerHTML` chưa thoát; `window.__xss` phải 0.
3. Tắt tính năng: không còn dấu vết (chữ, tab, **và lời gọi API thừa**). Đổi ngôn ngữ giữa chừng vẽ lại đủ ở mọi tab
   (kể cả khi đang mở một mục dữ liệu). Bấm đúp (`dblclick`) không gửi hai lần.
4. Kiosk học sinh: không lộ dữ liệu em khác (quét mã em khác trong DOM và phản hồi mạng); không xem được dữ liệu của người quản lý.
5. `localStorage` có `try/catch` (thử với kho ném `SecurityError`); `prefers-reduced-motion`; bàn phím (mũi tên, Home,
   End, Tab); tương phản biểu đồ (tính WCAG: đồ hoạ ≥ 3:1, chữ ≥ 4,5:1); không chỉ dựa vào màu.
6. Mọi chữ tiếng Anh: không còn chữ có dấu tiếng Việt ngoài tên dữ liệu; không còn `{tham_số}` chưa điền.

### Tầng 4 — Mã viết sai, vệ sinh, tài liệu, test
1. Mã chết, trùng lặp: hàm không ai gọi (grep `.py` và `.js`, kể cả tên API dạng chuỗi), import thừa, đoạn gần giống ≥ 10 dòng, `ruff`.
2. Chữ và i18n: `chu_cam`, `i18n_khoa`, `ma_loi_js`; khoá không ai dùng (nhớ tiền tố động kiểu `t("tien_to_" + x)`); chuỗi
   cứng trong JS.
3. Tài liệu lệch mã: `CHANGELOG.md`, sổ đăng ký, `TIEN_DO.md`, docstring, `CLAUDE.md` (**số dòng, số tệp / ca test**),
   README, các skill (câu kiểu "giống hệt …" phải còn đúng).
4. **Test yếu — gây hỏng tạm 3–5 chỗ then chốt** (đảo dấu điểm, bỏ kiểm khoá, thay `rollback()` bằng `commit()`, đảo luật
   hoà, tắt khoá xuất, đổi ranh giới `>` → `>=`/`+1`), mỗi lần chạy các test ĐÚNG CHỦ ĐỀ và cả nhóm rộng; test KHÔNG đỏ là
   phát hiện. Hoàn tác bằng ghi lại đúng nội dung gốc, rồi `git status`. `sleep` / `wait_for_timeout` cứng; chạy test giao
   diện 10 lần liền tìm chập chờn; test bỏ qua im lặng (có chốt trong CI không).

### Bốn khía cạnh — hỏi ở MỌI tầng
- **Bảo mật:** SQL injection, XSS, path traversal, bí mật trong mã, xác thực.
- **Hiệu năng:** truy vấn trong vòng lặp (N+1), O(n²) trên đường nóng ở cỡ thật (800 em × 20 CLB), truy vấn không giới hạn,
  tệp / kết nối không đóng. Đo, đừng đoán.
- **Đúng đắn:** biên rỗng / `None` / tràn, tranh chấp, xử lý lỗi, lệch một.
- **Bảo trì:** tên, trùng lặp, thiếu test, chỗ khó hiểu thiếu chú thích, chú thích nói khác mã.

## 6. Mẫu báo cáo

Tệp: `docs/ke_hoach/BAO_CAO_SOAT_MA_<MỤC>.md`. Đầu tệp: phạm vi (diff, hàm cũ bị chạm chia theo tầng), mốc test, lệnh
`kiem_nhanh.py` và kết quả. Mỗi tầng một mục gồm:

1. **Kết quả theo mục yêu cầu** (bảng: mục · ĐẠT / CẦN SỬA · bằng chứng).
2. **Phát hiện** (bảng ở mục 4); nếu không có thì nói thẳng "không có".
3. **Bốn khía cạnh.**
4. **Điểm tốt** (cụ thể, có bằng chứng; không khen chung).
5. **Kết luận tầng:** Đạt / Cần sửa / Cần bàn. Kèm tóm tắt số phát hiện theo mức.
6. Cuối báo cáo: **danh sách sửa đầy đủ**, mỗi việc ghi nguồn, trạng thái (Đã quyết / Đề xuất) và, với câu cần Truong
   quyết, 2–4 lựa chọn kèm lựa chọn em đề xuất.

Báo cáo trung thực: câu nào chưa đo thì viết "chưa đo", không viết như đã đo.
