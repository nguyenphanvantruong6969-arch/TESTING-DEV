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

## SG-9 — Trạng thái bận và đường lỗi cho mọi nút gọi API
- CHANGELOG: SG-9 — `js/00_nen.js`: ba hàm dùng chung `chayNut` (khoá nút + nhãn "Đang xử lý…", lỗi -> thông báo chung, `finally` mở lại nút và trả nhãn; bấm đúp chỉ gọi API một lần), `chayTai` (tải/làm mới không do nút: lỗi hiện thông báo), `noiTiep` (chuỗi bước tuần tự). Mọi `.then(` của `js/05_quan_ly.js` (33), `10_theo_doi.js`, `11_chuan_bi.js` (chỉ ở chỗ gọi), `12_chuan_bi_nap.js`, `13_chuan_bi_bo.js` đi qua hai hàm này; `napTepForms` (FG-4) nay là người dùng mỏng của `chayNut` (giữ khoá đến hết `khiXong`, nhãn "Đang nạp…", ô tệp được xoá). Chuỗi mới `dang_xu_ly` (vi + en, khối SG-C). Không đổi API / hợp đồng `{ok, data, errors}`. Test mới: `tests/test_giao_dien_sg9_nut_ban.py` (5 nút x 2 + kiểm tĩnh).
- TIEN_DO: SG-9 xong. Hành vi khác trước: nút mở lại ngay khi API trả về (như `khiBan`), trừ `napTepForms`; lỗi trong một bước tải riêng lẻ nay hiện thông báo thay vì chỉ nằm trong console.
- Ghi chú cho người A: `khiBan` (00_nen.js) vẫn còn dùng ở các tệp khác (không thuộc 5 tệp này).
