## SG-5 — Câu huy chương học sinh hiểu được (H3)
CHANGELOG: SG-5 · `mau_forms_thi_clb/bieu_mau.py` (`MO_TA_HUY_CHUONG`, `so_clb_nhan_huy_chuong`, `cau_vang_fa` có dòng mô tả,
`cac_phan_fa` chỉ phát câu đổi bạc/đồng khi ngày có >= 3 CLB không Tự do), `chuyen_forms_sang_phan_mem.py`
(`dat_huy_chuong_duong_b(..., so_clb_nhan)`: ngày < 3 CLB nhận huy chương thì bỏ qua ô đổi, không báo; tệp cũ vẫn đọc được),
`tao_mau_forms.py` (CAI_DAT_FORMS_DANG_KY.md) · test mới `tests/test_sg5_huy_chuong.py` (6 test).
TIEN_DO: SG-5 xong; chỉ đầu ra `--fa-daa*` đổi (m2, m3), sáu chế độ còn lại giống từng byte.
Ghi chú: dòng mô tả nằm trong câu vàng (Quick Import không có ô mô tả riêng cho phần; chưa thử trên Forms thật).
