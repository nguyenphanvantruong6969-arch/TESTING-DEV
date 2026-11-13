# Báo cáo 2026-11-12: giảm việc IT bằng giao diện (vòng 2), ghép đủ và vòng xanh

> Báo cáo vận hành, không phải báo cáo đề tài. Chưa thử trên Microsoft/Google thật (**TH**). Mọi số liệu trong test là **MÔ PHỎNG**.
> Báo cáo này thay phần "chưa làm" của `2026-11-11_it_giao_dien.md`.

**Xong 4/4** (FA-M7 gồm nền G0, FA-M8, FA-M9, FA-M10). Nhánh `claude/forms-gop`, không mở PR.

| Mục | Việc (1 câu dễ hiểu) | Kết quả | Commit |
|---|---|---|---|
| FA-M7 (+ G0) | Thẻ "Chuẩn bị đợt": nhập CLB một lần, nạp đề thi bằng một tệp Excel | Xong (người A) | c7b5d1d, d5a303e, 414a94c, db76ea9 |
| FA-M8 | Nút "Tạo bộ biểu mẫu": một tệp zip cho đường đã chọn, không phải tick đáp án trên Forms | Xong (người C) | 57f4631, b641d89 |
| FA-M9 | Kéo thả tệp xuất Forms/List vào phần mềm, tự nhận loại tệp và đề A/B | Xong (người B) | 934d031, e7c5a1f |
| FA-M10 | Ba nút sau khi xếp: kết quả kèm email, ai chưa đăng ký, đối chiếu hai lần xuất List | Xong (người B) | b43953c |
| Ghép | Gộp B và C vào nhánh chung, sổ sách, sửa số tệp test trong bản đồ mã | Xong | f809e2b, d06d2d8, e1a2ba5, d60d221 |

## Việc của IT: trước → sau
- Lệnh Python phải gõ trong một đợt: trước khoảng 6–8 lệnh → sau **0** (mọi bước ở thẻ "Chuẩn bị đợt").
- Tick đáp án và điểm trên Forms: trước 50–100 lượt (bộ đề mẫu) → sau **0**; giáo viên soát đáp án bằng `XEM_LAI_DAP_AN.xlsx`.
- Khai CLB: trước hai nơi (phiếu CLB và `de_thi.json`) → sau một lần (bước 1).
- Vẫn phải làm tay trên Forms: Quick Import và cài rẽ nhánh (Microsoft không có cách tạo biểu mẫu bằng chương trình).

## Kiểm (trên `d60d221`)
- Toàn bộ test, Chromium chạy thật: **5.972 đạt, 0 hỏng**; 4 bỏ qua, không ca giao diện nào (1 ca D1 hoãn kỳ 2, 2 ca thiếu numpy trên máy này, 1 ca cần người dùng POSIX thường). Độ phủ **93,52 %** (sàn 85 %).
- Vòng 1 có 1 ca hỏng (bản đồ mã ghi tên hàm mà test tài liệu không thấy được); Sonnet sửa (FIX-1, chỉ bỏ dấu backtick, không đổi test), vòng 2 xanh.
- `kiem_nhanh --co-so origin/main --so-seed 20`: 7/7, **60/60 ca trùng khít**. `ruff check .` sạch.
- Đầu ra bộ sinh biểu mẫu (7 chế độ) và bộ chuyển đổi (3 bộ demo, so từng ô) giống hệt bản gốc `fe37349`.
- CI *Tests (rbda-kiosk)* run 43231302370: **xanh**. Bản build Windows run 43239577277: **xanh** (bộ test trên Windows đạt, PyInstaller đóng gói có `mau_forms_thi_clb`, đã đăng lên Releases `ban-moi-nhat`).

## Ghi nhận
- Ba người chạy lệch giờ: A chờ 4 giờ rồi ghép riêng phần của mình; B và C chạy sau, B bị kẹt vì chờ A sửa một con số trong tệp thuộc quyền A. Lần sau: cho phép người ghép sửa con số bản đồ mã, hoặc chạy CHU_TRI một phiên.
- Phiên điều phối của B chạy bằng Sonnet, không phải Opus (đã ghi cảnh báo trong tệp bàn giao của B).

## Câu hỏi cho Truong
1. Nhánh `claude/forms-gop` gộp vào đâu (chưa mở PR)?
2. Có thử một đợt nhỏ trên Microsoft Forms thật (bỏ nhãn TH) trước khi dùng cho học sinh không?
