# -*- coding: utf-8 -*-
"""FA-SC, bản THỬ ý tưởng P1 cho quyết định D-SC7 (KHÔNG phải mã sản phẩm, không sửa tệp nào).

Ý tưởng P1: khoá thứ tự bốc thăm THEO NGÀY ở lần chạy đầu; em thêm sau được CHÈN ngẫu nhiên đều vào từng ngày bằng chính
`chen_stb_cho_hoc_sinh_moi` (như bộ số gốc), nên thứ tự tương đối giữa các em cũ giữ nguyên ở MỌI ngày.

Cách thử: thay `rbda_priority_pipeline.sinh_stb_theo_buoi` TRONG TIẾN TRÌNH này bằng một hàm bọc nhớ thứ tự của lần
chạy đầu (trong bộ nhớ; bản thật sẽ cần một bảng trong `app.db`), rồi chạy lại hai diễn tập d12 và d16 và so với hiện
trạng. Lần chạy đầu gọi đúng hàm gốc nên kết quả lần đầu giống hệt hiện nay. Dữ liệu MÔ PHỎNG."""
import os

import chung as c

import d12_den_muon_sau_cong_bo as d12  # noqa: E402
import d16_den_muon_khong_tranh_cho as d16  # noqa: E402
import rbda_priority_pipeline as rb  # noqa: E402


def bo_boc_p1():
    """Hàm thay cho `sinh_stb_theo_buoi`, có bộ nhớ riêng {buoi: [mã theo thứ tự]}."""
    goc, da_khoa = rb.sinh_stb_theo_buoi, {}

    def sinh(stb_goc, ds_buoi, seed, che_do):
        if che_do != "stb_ngay" or len(ds_buoi) <= 1:
            return goc(stb_goc, ds_buoi, seed, che_do)
        ra = {}
        for buoi in ds_buoi:
            if buoi not in da_khoa:                                    # lần đầu: đúng cách tính hiện nay
                so = goc(stb_goc, [buoi, "_"], seed, che_do)[buoi]
            else:                                                      # lần sau: giữ em cũ, chèn đều em mới
                cu = [s for s in da_khoa[buoi] if s in stb_goc]
                moi = sorted(set(stb_goc) - set(cu))
                so = rb.chen_stb_cho_hoc_sinh_moi(cu, moi, rb._seed_cua_buoi(seed, buoi))
            da_khoa[buoi] = sorted(so, key=lambda s: (so[s], s))
            ra[buoi] = so
        return ra

    return goc, sinh


def _lay(kq, khoa):
    return next(v for k, v in kq["so_lieu"] if k.startswith(khoa))


def dien_tap(ra, seed=c.SEED, so_hs=c.SO_HS):
    dong = []
    for ten, mod in (("d12 (5 em muộn tranh chỗ thật)", d12), ("d16 (1 em muộn không tranh chỗ)", d16)):
        nay = mod.dien_tap(os.path.join(ra, mod.__name__ + "_nay"), seed, so_hs)
        goc, sinh = bo_boc_p1()
        rb.sinh_stb_theo_buoi = sinh
        try:
            p1 = mod.dien_tap(os.path.join(ra, mod.__name__ + "_p1"), seed, so_hs)
        finally:
            rb.sinh_stb_theo_buoi = goc
        dong.append((ten + ": em CŨ đổi CLB, hiện nay -> P1", "%s -> %s" % (_lay(nay, "em CŨ"), _lay(p1, "em CŨ"))))
    return c.in_bang("thử P1: khoá số bốc thăm theo ngày (seed %d)" % seed, dong)


if __name__ == "__main__":
    c.main(dien_tap, __doc__)
