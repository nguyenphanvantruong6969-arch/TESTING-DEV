# Báo cáo đêm 2026-11-11: giảm việc IT bằng giao diện (vòng 2)

> Báo cáo vận hành, không phải báo cáo đề tài. Chưa thử trên Microsoft/Google thật (**TH**). Mọi số liệu trong test là **MÔ PHỎNG**.

**Xong 1/4** (FA-M7, gồm phần nền G0). Ba mục còn lại chưa làm vì hai cộng tác viên B và C không chạy (nhánh không bao giờ được đẩy lên sau 4 giờ chờ).

| Mục | Việc (1 câu dễ hiểu) | Kết quả | Commit |
|---|---|---|---|
| FA-M7 (+ G0) | Thẻ "Chuẩn bị đợt": nhập CLB một lần, nạp đề thi bằng một tệp Excel | Xong, đã gộp vào `claude/forms-gop` | c7b5d1d, d5a303e, 414a94c, db76ea9 (gộp: xem handoff) |
| FA-M9 | Kéo tệp xuất Forms/List vào phần mềm | Chưa làm (B/C không chạy) | — |
| FA-M8 | Nút "Tạo bộ biểu mẫu" | Chưa làm (B/C không chạy) | — |
| FA-M10 | Nút sau khi xếp (danh sách chưa đăng ký, so sánh List) | Chưa làm (B/C không chạy) | — |

## Việc của IT: trước và sau (chỉ phần FA-M7 thay đổi)
- CLB: trước, gõ CLB ở nhiều nơi (phiếu CLB, rồi lại trong `de_thi.json`); sau, nạp tệp Phiếu thiết lập CLB **một lần** ở bước 1.
- Đề thi: trước, sửa tay `de_thi.json`; sau, tải một tệp Excel mẫu (đã điền sẵn CLB), gõ câu hỏi, nạp lại. Lỗi được liệt kê một lần, chưa lưu gì khi còn lỗi.
- Chưa đổi: các bước 3-5 (tạo biểu mẫu, nạp bài làm, việc sau khi xếp) vẫn gõ lệnh Python như trong `T4M_VAN_HANH_MOT_DOT.md`.

## Vẫn phải làm tay trên Forms
- Dán bộ câu hỏi (Quick Import) và rẽ nhánh: Microsoft không có API. Phần này thuộc FA-M8, chưa làm.
- Tick đáp án trên Forms: chưa bỏ được (FA-M8 chưa làm).

## Kiểm
- Test liên quan (Chromium chạy thật, không ca nào bị bỏ qua): 161 ca qua, 0 lỗi (tệp FA-M7, tài liệu, nhãn, văn phòng tự nhiên, lớp, mẫu Forms).
- `ruff check .` sạch. `kiem_nhanh --co-so origin/main`: 7/7 (15 ca trùng khít).
- Số liệu toàn bộ test và CI: xem `docs/phien/IT_UI_STATUS.md` (người điều phối thêm sau vòng xanh).
- Đột biến đã thử (bỏ đối chiếu CLB của đề với bước 1): 3 ca đỏ.
- Soát mã (chỉ báo cáo): không có phát hiện mức cao hoặc trung. Một điểm nhỏ: các hàm API của thẻ vẫn gọi được khi chế độ huy chương tắt (giao diện chỉ ẩn thẻ); chỉ ghi vào thư mục `forms/`, không đụng app.db, nên không sửa.

## Câu hỏi cho Truong
1. Chạy lại B và C (`PROMPT_B.md`, `PROMPT_C.md`, nhánh từ `claude/forms-gop` đã có G0 + FA-M7), hay chạy tự động một phiên cho FA-M9 → FA-M8 → FA-M10?
2. Nhánh `claude/forms-gop` gộp vào đâu (chưa mở PR)?
