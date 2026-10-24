# Bộ thử workspace — "Công ty Bình Minh" (dữ liệu MÔ PHỎNG)

Phân 54 nhân viên vào 8 dự án nội bộ trong hai ngày (Thứ 3, Thứ 5). Mọi tên đều bịa.

| Tệp | Dùng để |
|---|---|
| `cong-ty-binh-minh.zip` | **Chỉ cần tệp này.** Workspace đã gắn cấu hình và nạp sẵn dữ liệu → **Nhập workspace**, mở, bấm chạy |
| `SO_NHAP_DU_AN.xlsx` | Sổ nhập đã nạp trong zip (sheet `1. Dự án`, `2. Nhân viên`). Chỉ nạp được vào workspace có đúng nhãn này |
| `cau_hinh_workspace.json` | Cấu hình để đối chiếu, hoặc gõ tay vào trình tạo 4 bước |
| `tao_bo_workspace.py` | Sinh lại cả ba tệp (tất định, `SEED = 2026`) |

Nhãn: Học sinh → **Nhân viên**, Câu lạc bộ → **Dự án**, Buổi → **Ngày**,
Nhóm ưu tiên → **Diện ưu tiên** (`tan_tuyen`, `noi_bat`), Điểm → **Điểm phỏng vấn**.
Luật: ≤ 5 nguyện vọng và ≤ 2 dự án phỏng vấn mỗi ngày, điểm theo từng dự án.

Đã kiểm bằng phần mềm thật (`seed=42`): nhập 0 cảnh báo; sức khoẻ dữ liệu chỉ có
`health_oversubscribed_buoi` (cố ý chật chỗ); chạy được; thời khoá biểu 2 ngày × 54 dòng.
