"""A13.8 lỗi 2.4: `phong_wharton_hang_loat` làm cả lượt trong MỘT giao dịch; đọc lại điểm hiện tại
của từng em và bỏ qua em đã đổi so với ảnh chụp (`da_doi`); lỗi giữa chừng rollback toàn bộ mà vẫn
trả `backup_path`; đang khoá thì từ chối trước khi sao lưu. Dữ liệu MÔ PHỎNG."""

import os

import api_quan_ly
from test_wharton_hang_loat import _khoa, _nk, w  # noqa: F401
from _wharton import dong_bids


def test_loi_giua_chung_rollback_toan_bo_va_van_tra_backup(w, monkeypatch):  # noqa: F811
    truoc, nk = dong_bids(w), _nk(w)
    goc = api_quan_ly.QuanLyMixin._luu_wharton_cur
    dem = {"n": 0}

    def hong(self, cur, luat, sid, w1, w2, nguon):
        dem["n"] += 1
        kq = goc(self, cur, luat, sid, w1, w2, nguon)       # em này ĐÃ ghi vào giao dịch
        if dem["n"] == 2:
            raise RuntimeError("hong giua chung")
        return kq
    monkeypatch.setattr(api_quan_ly.QuanLyMixin, "_luu_wharton_cur", hong)
    kq = w.phong_wharton_hang_loat("PHONG")
    assert kq["ok"] is False
    assert dem["n"] == 2
    assert dong_bids(w) == truoc and _nk(w) == nk          # không em nào bị đổi
    assert os.path.isfile(kq["data"]["backup_path"])


def test_em_vua_sua_diem_thi_bi_bo_qua_khong_bi_ghi_de(w, monkeypatch):  # noqa: F811
    """Giữa lúc tính kế hoạch và lúc ghi, HS2 tự sửa điểm: bản phóng (tính từ điểm cũ) phải bỏ qua."""
    goc = api_quan_ly.QuanLyMixin._ke_hoach_phong

    def chen(ho_so):
        ra = goc(ho_so)
        with w._ket_noi_ghi() as cur:
            cur.execute("UPDATE wharton_bids SET points = 10 WHERE student_id = 'HS2' AND club_id = 'A'")
        return ra
    monkeypatch.setattr(api_quan_ly.QuanLyMixin, "_ke_hoach_phong", staticmethod(chen))
    kq = w.phong_wharton_hang_loat("PHONG")
    assert kq["ok"], kq
    bo_qua = {b["student_id"]: b["ly_do"] for b in kq["data"]["bo_qua"]}
    assert bo_qua["HS2"] == "da_doi"
    assert kq["data"]["n_phong"] == 2                       # HS3, HS6 vẫn phóng
    bids = {(s, c): p for s, c, t, p in dong_bids(w)}
    assert bids[("HS2", "A")] == 10 and bids[("HS2", "B")] == 20


def test_dang_khoa_tu_choi_truoc_khi_sao_luu(w):  # noqa: F811
    _khoa(w)
    truoc = dong_bids(w)
    kq = w.phong_wharton_hang_loat("PHONG")
    assert [e["code"] for e in kq["errors"]] == ["wharton_da_khoa"]
    assert dong_bids(w) == truoc
