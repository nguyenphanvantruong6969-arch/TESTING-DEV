# Bộ thử chương trình — trường 3 buổi (dữ liệu MÔ PHỎNG)

`SO_NHAP_CLB.xlsx`: 12 CLB (4 CLB × Thứ 2, Thứ 4, Thứ 6), 180 học sinh, 235 ô điểm,
có suất dự trữ. Mọi tên đều bịa. Có nhiều buổi nên thẻ Kết quả hiện đủ
**Thời khoá biểu tuần**, **Độ phủ** và **Số bốc thăm**.

Sinh lại (tất định):

    python .claude/skills/sinh-du-lieu-clb/scripts/sinh_du_lieu.py ngau \
        --ra du_lieu_test/bo_thu_chuong_trinh --hoc-sinh 180 \
        --buoi thu_2,thu_4,thu_6 --clb-moi-buoi 4 --seed 2026 --do-choi 1.3

Đã kiểm bằng phần mềm thật (`seed=42`): nhập 0 cảnh báo; sức khoẻ dữ liệu chỉ có
`health_oversubscribed_buoi` (cố ý chật chỗ); chạy được; 40/180 em không có CLB nào cả tuần.
