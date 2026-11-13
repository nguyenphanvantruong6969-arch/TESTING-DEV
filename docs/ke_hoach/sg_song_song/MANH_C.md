## SG-5 — Câu huy chương học sinh hiểu được (H3)
CHANGELOG: SG-5 · `mau_forms_thi_clb/bieu_mau.py` (`MO_TA_HUY_CHUONG`, `so_clb_nhan_huy_chuong`, `cau_vang_fa` có dòng mô tả,
`cac_phan_fa` chỉ phát câu đổi bạc/đồng khi ngày có >= 3 CLB không Tự do), `chuyen_forms_sang_phan_mem.py`
(`dat_huy_chuong_duong_b(..., so_clb_nhan)`: ngày < 3 CLB nhận huy chương thì bỏ qua ô đổi, không báo; tệp cũ vẫn đọc được),
`tao_mau_forms.py` (CAI_DAT_FORMS_DANG_KY.md) · test mới `tests/test_sg5_huy_chuong.py` (6 test).
TIEN_DO: SG-5 xong; chỉ đầu ra `--fa-daa*` đổi (m2, m3), sáu chế độ còn lại giống từng byte.
Ghi chú: dòng mô tả nằm trong câu vàng (Quick Import không có ô mô tả riêng cho phần; chưa thử trên Forms thật).

## SG-7 — Hết "bức tường cảnh báo" (H4, M1)
- CHANGELOG: SG-7 — bước 4 (`js/12_chuan_bi_nap.js`) và khung cảnh báo của thẻ Nhập (`js/02_van_hanh.js`, `veCanhBaoNhap`) dùng MỘT hàm `veCanhBaoGom` (`js/00_nen.js`): gom theo mã, số đếm, tối đa 5 ví dụ, "và N trường hợp nữa". Bỏ kiểu nút "Xem 5 dòng đầu" (T3-02) và `slice(0, 30)` + tiền tố mã nội bộ của bước 4. Chuỗi mới `canh_bao_gom_dau`, `canh_bao_gom_nua` (vi + en, khối SG-C); CSS trong khối SG-C. Test mới: `tests/test_giao_dien_sg7_canh_bao_gom.py`; sửa 2 test T3-02 trong `tests/test_giao_dien_t3_l2_van_hanh.py`.
- TIEN_DO: SG-7 xong. Khoá cũ `canh_bao_gom`, `canh_bao_xem_dau`, `canh_bao_thu_gon` (i18n.js, ngoài khối SG-C) nay không dùng; để nguyên, người A dọn khi tích hợp.
