# Trạng thái phiên (tệp bàn giao giữa các phiên Claude)

> **Mục đích:** một phiên Claude mới đọc tệp này (sau `CLAUDE.md`) là nắm được việc đang dở, KHÔNG cần nén / đọc lại lịch sử chat.
> **Quy tắc:** cuối MỖI phiên có thay đổi, Claude ghi đè các mục "Hiện tại" và THÊM một dòng vào "Nhật ký phiên" (không xoá dòng cũ). Hook Stop (`.claude/hooks/nhac_cap_nhat_trang_thai.py`) nhắc nếu quên.
> Chi tiết từng mục vẫn ở `CHANGELOG.md` và `TIEN_DO.md`; tệp này chỉ là bản tóm tắt để vào việc nhanh.

## Hiện tại (ghi đè mỗi phiên)

- **Cập nhật lần cuối:** 2026-11-01 · nhánh `claude/sleepy-sagan-ly5fx0`
- **Đang làm dở:** chưa có (phiên 2026-11-01 chỉ dựng cơ chế bàn giao này).
- **Trạng thái mã:** theo `TIEN_DO.md`: A13.6–A13.12 xong; còn biểu mẫu Google, VISEF, ngưỡng điểm, giải trình từng em (A13); các mục Z6, Z3, Z7, Z4, Z5, Z2, Z1 chưa làm.
- **Việc tiếp theo (theo thứ tự):**
  1. Truong chọn mục tiếp theo (gợi ý theo kế hoạch: Z6).
- **Quyết định / lưu ý cần nhớ:**
  - Trả lời bằng tiếng Việt; gọi người dùng là "Truong" / "em" theo sở thích cá nhân.
  - Bất biến và quy tắc làm việc: xem `CLAUDE.md`.
- **Lệnh kiểm trước khi push:** skill `soat-ma` (`kiem_nhanh.py`), `python -m pytest -q`, `ruff check .`.

## Nhật ký phiên (chỉ thêm, mới nhất ở cuối)

| Ngày | Việc đã làm | Tệp chính | Ghi chú |
|---|---|---|---|
| 2026-11-01 | Dựng cơ chế bàn giao: tệp này, quy tắc 9 trong `CLAUDE.md`, hook Stop | `.claude/settings.json`, `.claude/hooks/nhac_cap_nhat_trang_thai.py`, `CLAUDE.md` | Hook chỉ nhắc khi cây làm việc có thay đổi |
| 2026-11-01 | Giảm token: chỉ chạy test liên quan, không chạy toàn bộ bộ test | `CLAUDE.md` (quy tắc 2, mục Lệnh), `.claude/skills/soat-ma/SKILL.md` | CI vẫn chạy toàn bộ; Truong yêu cầu thì mới chạy toàn bộ cục bộ |
| 2026-11-01 | Thêm quy tắc 10 NO SUBAGENT vào CLAUDE.md | `CLAUDE.md` | Trước đó "Không subagent" chỉ áp cho skill soat-ma |
