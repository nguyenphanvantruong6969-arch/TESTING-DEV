/* ==========================================================================
   13_chuan_bi_bo.js — bước 3 "Tạo bộ biểu mẫu" của thẻ "Chuẩn bị đợt" (FA-M8, worker C).
   Tuỳ chọn: "Một biểu mẫu cho mọi buổi" (mặc định tích), "Hai đề cho CLB Tuyển chọn" (chỉ bật khi đề có biến thể).
   Nút tạo -> API `tao_bo_bieu_mau_api` -> thông báo có tên tệp zip + nút "Mở thư mục" (mo_thu_muc). TH = chưa thử Microsoft.
   ========================================================================== */
"use strict";

(() => {
  let zipGhi = null;          // kết quả lần tạo gần nhất (chỉ giữ trong trang; bộ nằm ở thư mục dữ liệu của đợt)
  let moMotBieuMau = true;
  let moBienThe = false;

  function mot(tag, lop, chu) {
    const n = document.createElement(tag);
    if (lop) n.className = lop;
    if (chu !== undefined) n.textContent = chu;
    return n;
  }

  function oChon(id, khoa, tich, khoa_bat, doi) {
    const nhan = mot("label", "cb-bo-tuy-chon");
    const o = mot("input");
    o.type = "checkbox";
    o.id = id;
    o.checked = tich;
    o.disabled = !khoa_bat;
    o.addEventListener("change", () => doi(o.checked));
    nhan.appendChild(o);
    nhan.appendChild(mot("span", "", " " + t(khoa)));
    return nhan;
  }

  function trangThai(trang, chu) {
    const n = mot("div", "cb-trang-thai", chu);
    n.dataset.trangThai = trang;
    return n;
  }

  function tao() {
    callApi("tao_bo_bieu_mau_api", { mot_bieu_mau: moMotBieuMau, bien_the: moBienThe }).then((res) => {
      if (!res.ok) { showErrorToast(res.errors); return; }
      zipGhi = res.data;
      showToast(t("cb_bo_xong", { n: zipGhi.n_tep, ten: zipGhi.ten_zip }), "success");
      ChuanBi.lamMoi();
    });
  }

  function veBuoc3(khung, tt) {
    khung.appendChild(mot("p", "hint-text", t("cb_bo_ghi")));
    const san_sang = tt.co_de && !!tt.duong;
    if (!tt.duong) khung.appendChild(trangThai("chua", t("cb_bo_can_duong")));
    else if (!tt.co_de) khung.appendChild(trangThai("chua", t("cb_bo_can_de")));
    if (!tt.co_bien_the) moBienThe = false;
    const tuyChon = mot("div", "cb-bo-tuy-chon-hang");
    tuyChon.appendChild(oChon("cb-bo-mot", "cb_bo_mot", moMotBieuMau, tt.duong !== "A", (v) => { moMotBieuMau = v; }));
    tuyChon.appendChild(oChon("cb-bo-bien-the", "cb_bo_bien_the", moBienThe, tt.co_bien_the, (v) => { moBienThe = v; }));
    khung.appendChild(tuyChon);
    if (!tt.co_bien_the && tt.co_de) {
      const g = mot("p", "hint-text", t("cb_bo_bien_the_khong"));
      g.id = "cb-bo-bien-the-ghi";
      khung.appendChild(g);
    }
    const hang = mot("div", "cb-nut-hang");
    const nut = mot("button", "btn btn-secondary", t("cb_bo_nut"));
    nut.type = "button";
    nut.id = "cb-bo-tao";
    nut.disabled = !san_sang;
    nut.addEventListener("click", tao);
    hang.appendChild(nut);
    if (zipGhi) {
      const mo = mot("button", "btn btn-secondary", t("cb_bo_mo"));
      mo.type = "button";
      mo.id = "cb-bo-mo";
      mo.addEventListener("click", () => callApi("mo_thu_muc", zipGhi.path));
      hang.appendChild(mo);
    }
    khung.appendChild(hang);
    if (zipGhi) {
      const k = trangThai("xanh", t("cb_bo_xong", { n: zipGhi.n_tep, ten: zipGhi.ten_zip }));
      k.id = "cb-bo-ket-qua";
      khung.appendChild(k);
    }
  }

  ChuanBi.dangKyBuoc(3, (khung) => {
    callApi("get_bo_bieu_mau").then((res) => {
      if (!res.ok) { showErrorToast(res.errors); return; }
      clear(khung);
      veBuoc3(khung, res.data);
    });
  });
})();
