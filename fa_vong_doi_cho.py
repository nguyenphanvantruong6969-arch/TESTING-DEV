"""GAP-13 (V§8.8): chu trình cải thiện ổn định (stable improvement cycles, Erdil & Ergin 2008) — CHẾ ĐỘ ĐO.

Sau DA với bốc thăm phá hoà, có thể còn những vòng đổi chỗ mà MỌI em trong vòng đều được CLB thích hơn và không vượt
qua ai có ưu tiên (giữ chỗ, điểm, huy chương) cao hơn: chỉ vượt thứ tự bốc thăm. Mô-đun này chỉ TÌM và ĐO các vòng đó:
không hàm nào ghi `match_results` hay `fa_dieu_chinh`, và mọi kết quả mang nhãn `NHAN_KHONG_BAO_DAM` (bất biến 8:
chưa chứng minh tính chất với bộ xếp thật, nên không đưa vào đường xếp).

`khoa_tho[club][sid]`: khoá ưu tiên KHÔNG có phần bốc thăm (nhỏ hơn = ưu tiên hơn); em không có khoá ở CLB đó thì
không được xét ở CLB đó. Không bao giờ đọc thứ hạng nguyện vọng làm khoá (bất biến 2): thứ hạng chỉ dùng để biết em
muốn CLB nào hơn chỗ hiện tại.
"""

NHAN_KHONG_BAO_DAM = "không bảo đảm ổn định"


def _hang(prefs, s, c):
    ds = prefs.get(s) or []
    return ds.index(c) if c in ds else len(ds)


def _cung(asg, prefs, khoa_tho):
    """{s: [t…]}: s -> t khi s muốn CLB của t hơn chỗ của mình và s có khoá TỐT NHẤT (cho phép hoà) trong những em muốn
    CLB đó hơn chỗ của mình (Erdil & Ergin 2008). Em có khoá kém hơn ai đó cũng muốn CLB đó thì không bao giờ được vượt;
    chỉ thứ tự bốc thăm giữa những em hoà khoá bị bỏ qua."""
    giu: dict = {}
    for t, c in asg.items():
        if c is not None:
            giu.setdefault(c, []).append(t)
    muon: dict = {}
    for s in asg:
        for c in prefs.get(s) or []:
            if c in giu and s in (khoa_tho.get(c) or {}) and _hang(prefs, s, c) < _hang(prefs, s, asg[s]):
                muon.setdefault(c, []).append(s)
    ra: dict = {}
    for c, ds in muon.items():
        k = khoa_tho[c]
        tot = min(k[s] for s in ds)
        for s in sorted(ds):
            if k[s] != tot:
                continue
            for t in sorted(giu[c]):
                if t != s:
                    ra.setdefault(s, []).append(t)
    return ra


def tim_chu_trinh(asg, prefs, khoa_tho):
    """Một chu trình [(sid, club_from, club_to)] (em nhận CLB của em kế tiếp), hoặc [] nếu không có. Tất định:
    duyệt theo mã. Hàm thuần."""
    cung = _cung(asg, prefs, khoa_tho)
    xong = set()
    for goc in sorted(cung):
        if goc in xong:
            continue
        duong, vi_tri, ngan = [goc], {goc: 0}, [iter(cung.get(goc, []))]
        while ngan:
            t = next(ngan[-1], None)
            if t is None:                                  # hết cạnh: lùi một bước
                u = duong.pop()
                ngan.pop()
                del vi_tri[u]
                xong.add(u)
                continue
            if t in vi_tri:
                vong = duong[vi_tri[t]:]
                return [(s, asg[s], asg[vong[(i + 1) % len(vong)]]) for i, s in enumerate(vong)]
            if t in xong:
                continue
            vi_tri[t] = len(duong)
            duong.append(t)
            ngan.append(iter(cung.get(t, [])))
    return []


def chay_chu_trinh(asg, prefs, khoa_tho, toi_da=10000):
    """Áp lần lượt mọi chu trình tới khi hết. Trả (chỗ mới, [chu trình]). Không sửa đầu vào. Mỗi chu trình làm mọi em
    trong đó được CLB thích hơn, nên vòng lặp dừng."""
    moi = dict(asg)
    ds = []
    for _ in range(toi_da):
        ct = tim_chu_trinh(moi, prefs, khoa_tho)
        if not ct:
            return moi, ds
        for s, _cu, c in ct:
            moi[s] = c
        ds.append(ct)
    raise RuntimeError("chay_chu_trinh: quá %d chu trình" % toi_da)


def khoa_tho_fa(clubs: dict, prefs: dict, diem: dict, huy_chuong: dict, giu_cho) -> dict:
    """Khoá thô theo FA-DAA (V§8.2) bỏ phần bốc thăm: Giới hạn (giữ chỗ, -huy chương); Tuyển chọn (giữ chỗ, -điểm,
    -huy chương), chỉ em có điểm và đạt điểm sàn. Tự do không xét (nhận mọi em). `clubs[c]` có `loai`, `diem_san`."""
    from fa_daa import dat_diem_san                      # FA-D7L: đạt sàn = điểm làm tròn nửa lên >= sàn
    giu = {(c, s) for c, s in giu_cho}
    ra: dict = {}
    for s, ds in prefs.items():
        for c in ds:
            loai = (clubs.get(c) or {}).get("loai")
            hc = (huy_chuong.get(s) or {}).get(c, 0) or 0
            g = 0 if (c, s) in giu else 1
            if loai == "GIOI_HAN":
                ra.setdefault(c, {})[s] = (g, -hc)
            elif loai == "TUYEN_CHON":
                d = (diem.get(c) or {}).get(s)
                if d is not None and dat_diem_san(d, (clubs.get(c) or {}).get("diem_san")):
                    ra.setdefault(c, {})[s] = (g, -d, -hc)
    return ra
