"""B6 (A14): `_trinh_duyet._tim` tìm được Chromium ở các bố cục thư mục Playwright đã gặp, để test
giao diện không bị bỏ qua im lặng khi thiếu biến môi trường."""

import os
import stat

import _trinh_duyet


def _chay_duoc(duong):
    os.makedirs(os.path.dirname(duong), exist_ok=True)
    with open(duong, "w") as f:
        f.write("#!/bin/sh\n")
    os.chmod(duong, os.stat(duong).st_mode | stat.S_IXUSR)
    return duong


def test_tim_bo_cuc_chrome_linux64(tmp_path, monkeypatch):
    monkeypatch.delenv("RBDA_TEST_CHROMIUM", raising=False)
    d = _chay_duoc(str(tmp_path / "chromium-1243" / "chrome-linux64" / "chrome"))
    assert _trinh_duyet._tim(str(tmp_path)) == d


def test_tim_bo_cuc_chrome_linux_cu(tmp_path, monkeypatch):
    monkeypatch.delenv("RBDA_TEST_CHROMIUM", raising=False)
    d = _chay_duoc(str(tmp_path / "chromium-1194" / "chrome-linux" / "chrome"))
    assert _trinh_duyet._tim(str(tmp_path)) == d


def test_tim_tep_chromium_chay_duoc_truc_tiep(tmp_path, monkeypatch):
    monkeypatch.delenv("RBDA_TEST_CHROMIUM", raising=False)
    d = _chay_duoc(str(tmp_path / "chromium"))
    assert _trinh_duyet._tim(str(tmp_path)) == d


def test_ban_moi_nhat_duoc_chon_truoc(tmp_path, monkeypatch):
    monkeypatch.delenv("RBDA_TEST_CHROMIUM", raising=False)
    _chay_duoc(str(tmp_path / "chromium-1100" / "chrome-linux" / "chrome"))
    moi = _chay_duoc(str(tmp_path / "chromium-1243" / "chrome-linux64" / "chrome"))
    assert _trinh_duyet._tim(str(tmp_path)) == moi


def test_bien_moi_truong_van_thang_khi_co_that(tmp_path, monkeypatch):
    chon = _chay_duoc(str(tmp_path / "rieng" / "chrome"))
    _chay_duoc(str(tmp_path / "chromium-1243" / "chrome-linux64" / "chrome"))
    monkeypatch.setenv("RBDA_TEST_CHROMIUM", chon)
    assert _trinh_duyet._tim(str(tmp_path)) == chon


def test_bien_moi_truong_tro_vao_tep_khong_co_thi_roi_ve_tim(tmp_path, monkeypatch):
    d = _chay_duoc(str(tmp_path / "chromium-1243" / "chrome-linux64" / "chrome"))
    monkeypatch.setenv("RBDA_TEST_CHROMIUM", str(tmp_path / "khong_co"))
    assert _trinh_duyet._tim(str(tmp_path)) == d


def test_may_nay_tim_thay_chromium_khi_khong_dat_bien():
    """Trên máy có /opt/pw-browsers (như môi trường này) thì không được rơi về None."""
    if not os.path.isdir("/opt/pw-browsers"):
        return
    assert _trinh_duyet.CHROMIUM or os.environ.get("RBDA_TEST_CHROMIUM")
