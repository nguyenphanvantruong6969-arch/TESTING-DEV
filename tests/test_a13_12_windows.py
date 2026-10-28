"""A13.12 — lỗi CHỈ xảy ra trên Windows, giả lập bằng cách nào đó chạy được ở mọi máy (CI Windows báo đỏ):

  * tệp log mở ở chế độ văn bản trên Windows có xuống dòng \\r\\n, còn mục mới dựng bằng \\n — so sánh
    "trùng liên tiếp" của `chan_doan.ghi` không được lệch vì xuống dòng;
  * cửa sổ lệnh / ống dẫn Windows mặc định cp1252: script in tiếng Việt ("→", "ĐẠT") không được nổ
    UnicodeEncodeError, và đầu ra phải là UTF-8 để bên gọi (test, `subprocess` với encoding utf-8) đọc được.
"""

import io
import os
import sys

import chan_doan

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_muc_trung_van_bi_bo_khi_tep_log_co_xuong_dong_crlf(tmp_path):
    duong = chan_doan.duong_log(str(tmp_path), chan_doan.TEN_LOG_UNG_DUNG)
    with open(duong, "w", encoding="utf-8", newline="\r\n") as f:      # như Windows ghi chế độ văn bản
        f.write("[2026-01-01 00:00:00] Loi: cung mot loi\n")
    chan_doan.ghi(str(tmp_path), "Loi: cung mot loi", ten=chan_doan.TEN_LOG_UNG_DUNG)
    chan_doan.ghi(str(tmp_path), "Loi: cung mot loi", ten=chan_doan.TEN_LOG_UNG_DUNG)
    with open(duong, "rb") as f:
        assert f.read().decode("utf-8").count("cung mot loi") == 1


def _stdout_cp1252():
    return io.TextIOWrapper(io.BytesIO(), encoding="cp1252", errors="strict", write_through=True)


def _chay_voi_cp1252(monkeypatch, ham):
    ra, loi = _stdout_cp1252(), _stdout_cp1252()
    monkeypatch.setattr(sys, "stdout", ra)
    monkeypatch.setattr(sys, "stderr", loi)
    kq = ham()
    ra.flush()
    return kq, ra.buffer.getvalue()


def test_sinh_du_lieu_dqt_in_tieng_viet_khong_no_tren_cp1252(monkeypatch, tmp_path):
    sys.path.insert(0, os.path.join(GOC, "du_lieu_test"))
    try:
        import sinh_du_lieu_diem_quyet_tam as s
        kq, byte = _chay_voi_cp1252(monkeypatch, lambda: s.main(["--ra", str(tmp_path)]))
    finally:
        sys.path.pop(0)
    assert kq == 0
    assert "→".encode("utf-8") in byte           # đầu ra là UTF-8


def test_kiem_nhanh_in_dat_khong_dat_khong_no_tren_cp1252(monkeypatch):
    sys.path.insert(0, os.path.join(GOC, ".claude", "skills", "soat-ma", "scripts"))
    try:
        import kiem_nhanh as kn
        kq, byte = _chay_voi_cp1252(monkeypatch, lambda: kn.main(["--chi", "i18n_khoa"]))
    finally:
        sys.path.pop(0)
    assert kq == 0
    assert "ĐẠT".encode("utf-8") in byte


def test_kiem_nhanh_goi_con_voi_errors_replace():
    """Đầu ra con không phải UTF-8 (ruff / git trên Windows) không được làm luồng đọc nổ rồi trả None."""
    van = open(os.path.join(GOC, ".claude", "skills", "soat-ma", "scripts", "kiem_nhanh.py"),
               encoding="utf-8").read()
    import re
    for cau in re.findall(r"subprocess\.run\([^)]*text=True[^)]*\)", van, re.S):
        assert 'errors="replace"' in cau, cau
