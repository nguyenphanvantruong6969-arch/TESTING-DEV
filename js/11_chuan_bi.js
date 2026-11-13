/* ==========================================================================
   11_chuan_bi.js — thẻ "Chuẩn bị đợt" (FA-M7 G0): chọn đường A / B và khung năm bước.

   Hợp đồng dùng chung (worker A viết, B và C vẽ vào các khung):
     window.ChuanBi = { duong(), dangKyBuoc(so, veFn), lamMoi() }
       duong()            -> "A" | "B" | null (chưa chọn), theo `rules.fa_duong`
       dangKyBuoc(so, fn) -> đăng ký hàm vẽ cho khung #cb-buoc-<so> (1..5); fn(khung) được gọi mỗi lần thẻ mở,
                             mỗi lần đổi đường, và mỗi lần lamMoi(); fn tự xoá và vẽ lại nội dung khung.
       lamMoi()           -> đọc lại đường từ backend rồi vẽ lại mọi khung đã đăng ký.
   Thẻ chỉ hiện khi `FA_BAT` (rules.fa_daa, đặt ở wsApDungCauHinh).
   ========================================================================== */
"use strict";

window.ChuanBi = (() => {
  const SO_BUOC = 5;
  let duongHienTai = null;
  const veBuoc = {};

  function duong() { return duongHienTai; }

  function dangMo() { return currentTabName() === "chuan_bi"; }

  function veMotBuoc(so) {
    const khung = el("cb-buoc-" + so);
    if (!khung || !veBuoc[so]) return;
    clear(khung);
    veBuoc[so](khung);
  }

  function veMoiBuoc() {
    Object.keys(veBuoc).forEach((so) => veMotBuoc(Number(so)));
  }

  function dangKyBuoc(so, veFn) {
    if (!Number.isInteger(so) || so < 1 || so > SO_BUOC || typeof veFn !== "function") return;
    veBuoc[so] = veFn;
    if (dangMo()) veMotBuoc(so);
  }

  function chonONhap() {
    document.querySelectorAll('input[name="cbDuong"]').forEach((o) => {
      o.checked = o.value === duongHienTai;
    });
  }

  function lamMoi() {
    return callApi("get_fa_duong").then((res) => {
      if (!res.ok) { showErrorToast(res.errors); return res; }
      duongHienTai = res.data.duong || null;
      chonONhap();
      veMoiBuoc();
      return res;
    });
  }

  function datDuong(gia_tri) {
    return callApi("dat_fa_duong", gia_tri).then((res) => {
      if (!res.ok) { showErrorToast(res.errors); chonONhap(); return res; }
      duongHienTai = res.data.duong;
      veMoiBuoc();
      return res;
    });
  }

  /* Thẻ hiện khi FA-DAA bật; tắt mà đang đứng ở thẻ này thì về thẻ đầu. */
  function capNhatThe() {
    const nut = document.querySelector('.nav-item[data-tab="chuan_bi"]');
    if (!nut) return;
    nut.hidden = !FA_BAT;
    el("cbGhiChuTat").hidden = FA_BAT;
    el("cbDuongPanel").hidden = !FA_BAT;
    if (!FA_BAT && dangMo()) switchTab("pipeline");
  }

  TAB_LOADERS.chuan_bi = () => { capNhatThe(); if (FA_BAT) lamMoi(); };

  document.querySelectorAll('input[name="cbDuong"]').forEach((o) => {
    o.addEventListener("change", () => { if (o.checked) datDuong(o.value); });
  });

  /* wsApDungCauHinh (js/075_workspace.js) đặt FA_BAT mỗi lần mở / đổi không gian làm việc: móc vào đó để thẻ
     theo cờ, không sửa tệp của người khác. Mọi lời gọi tìm hàm theo tên toàn cục nên thấy bản bọc. */
  const goc = window.wsApDungCauHinh;
  if (typeof goc === "function") {
    window.wsApDungCauHinh = function (cfg) {
      const kq = goc.apply(this, arguments);
      capNhatThe();
      return kq;
    };
  }

  /* ----- FA-M7: bước "1. CLB" và "2. Đề thi" (TH = chưa thử trên Microsoft / Google thật) ----- */
  function mot(tag, lop, chu) {
    const n = document.createElement(tag);
    if (lop) n.className = lop;
    if (chu !== undefined) n.textContent = chu;
    return n;
  }

  function nut(id, khoa, bamVao) {
    const n = mot("button", "btn btn-secondary", t(khoa));
    n.type = "button";
    n.id = id;
    n.addEventListener("click", bamVao);
    return n;
  }

  /* Ô chọn tệp ẩn + nút mở nó; `nap(b64, tep)` nhận nội dung tệp. */
  function nutChonTep(khung, idTep, idNut, khoa, nap) {
    const o = mot("input");
    o.type = "file";
    o.id = idTep;
    o.accept = ".xlsx";
    o.hidden = true;
    o.addEventListener("change", () => {
      const tep = o.files && o.files[0];
      if (!tep) return;
      const doc = new FileReader();
      doc.onload = () => { nap(bufferSangBase64(doc.result), tep); o.value = ""; };
      doc.readAsArrayBuffer(tep);
    });
    khung.appendChild(o);
    return nut(idNut, khoa, () => o.click());
  }

  function trangThai(trang, chu) {
    const n = mot("div", "cb-trang-thai", chu);
    n.dataset.trangThai = trang;
    return n;
  }

  function danhSach(id, dong) {
    const ul = mot("ul", "cb-dong-loi");
    ul.id = id;
    dong.forEach((d) => ul.appendChild(mot("li", "", d)));
    return ul;
  }

  function bangClb(clubs) {
    const cuon = mot("div", "scroll-x");
    const bang = mot("table", "data-table");
    bang.id = "cb-b1-bang";
    const dau = bang.createTHead().insertRow();
    /* SG-6: hai cột Giờ / Địa điểm chỉ khi có CLB đã khai; không thì bảng y như cũ. */
    const coGio = clubs.some((c) => c.gio || c.dia_diem);
    ["cb_cot_ten", "cb_cot_buoi", "cb_cot_loai", "cb_cot_chi_tieu"].concat(coGio ? ["cb_cot_gio", "cb_cot_dia_diem"] : []).forEach((k) => {
      const th = mot("th", "", t(k));
      th.scope = "col";
      dau.appendChild(th);
    });
    const tb = bang.createTBody();
    clubs.forEach((c) => {
      const tr = tb.insertRow();
      [c.name, c.buoi_nhan, c.loai_nhan, c.chi_tieu].concat(coGio ? [c.gio, c.dia_diem] : []).forEach((v) => {
        tr.insertCell().textContent = v === null || v === undefined ? "" : String(v);
      });
    });
    cuon.appendChild(bang);
    return cuon;
  }

  const tomLoai = (theo) => Object.keys(theo || {}).map((k) => k + " " + theo[k]).join(", ");
  const noiDung = (x) => x.clb + ": " + x.noi_dung;

  function veBuoc1(khung, tt) {
    const b1 = tt.clb;
    khung.appendChild(mot("p", "hint-text", t("cb_b1_ghi")));
    const hang = mot("div", "cb-nut-hang");
    hang.appendChild(nutChonTep(khung, "cb-b1-tep", "cb-b1-nap", "cb_b1_nut", (b64) => {
      callApi("nap_phieu_clb", b64, "").then((res) => {
        if (!res.ok) { showErrorToast(res.errors); return; }
        lamMoi();
      });
    }));
    khung.appendChild(hang);
    if (!b1.co) { khung.appendChild(trangThai("chua", t("cb_b1_chua"))); return; }
    const sach = !b1.loi.length && !b1.chan.length;
    const p = { n: b1.n_clb, loai: tomLoai(b1.theo_loai) };
    khung.appendChild(trangThai(sach ? "xanh" : "do", t(sach ? "cb_b1_xanh" : "cb_b1_do", p)));
    khung.appendChild(bangClb(b1.clubs));
    [["cb_b1_loi", "cb-b1-loi", b1.loi.map(noiDung)], ["cb_b1_canh_bao", "cb-b1-canh-bao", b1.canh_bao.map(noiDung)],
      ["cb_b1_chan", "cb-b1-chan", b1.chan]].forEach(([khoa, id, ds]) => {
      if (!ds.length) return;
      khung.appendChild(mot("strong", "", t(khoa)));
      khung.appendChild(danhSach(id, ds));
    });
  }

  let loiDeThi = [];          // lỗi của lần nạp đề gần nhất (chỉ giữ trong trang; đề hỏng thì không có gì để lưu)
  let tepMauGhi = "";

  function veBuoc2(khung, tt) {
    const de = tt.de;
    khung.appendChild(mot("p", "hint-text", t("cb_b2_ghi")));
    const hang = mot("div", "cb-nut-hang");
    hang.appendChild(nut("cb-b2-tai-mau", "cb_b2_tai_mau", () => {
      callApi("tai_mau_de_thi", "").then((res) => {
        if (!res.ok) { showErrorToast(res.errors); return; }
        tepMauGhi = res.data.path;
        lamMoi();
      });
    }));
    hang.appendChild(nutChonTep(khung, "cb-b2-tep", "cb-b2-nap", "cb_b2_nap", (b64) => {
      callApi("nap_de_thi", b64).then((res) => {
        if (res.ok) { loiDeThi = []; lamMoi(); return; }
        const chiTiet = res.errors.filter((e) => e.code === "de_thi_tep_sai" && e.params && e.params.detail)
          .map((e) => e.params.detail);
        if (!chiTiet.length) { showErrorToast(res.errors); return; }
        loiDeThi = chiTiet;
        lamMoi();
      });
    }));
    khung.appendChild(hang);
    if (tepMauGhi) {
      const g = mot("p", "hint-text", t("cb_b2_mau_ghi", { path: tepMauGhi }));
      g.id = "cb-b2-mau-ghi";
      khung.appendChild(g);
    }
    if (loiDeThi.length) {
      khung.appendChild(trangThai("do", t("cb_b2_do", { n: loiDeThi.length })));
      khung.appendChild(danhSach("cb-b2-loi", loiDeThi));
    } else if (!tt.clb.co) khung.appendChild(trangThai("chua", t("cb_b2_can_b1")));
    else if (!de.co) khung.appendChild(trangThai("chua", t("cb_b2_chua")));
    else if (!de.khop) khung.appendChild(trangThai("cu", t("cb_b2_cu")));
    else khung.appendChild(trangThai("xanh", t("cb_b2_xanh", { thi: de.n_clb_thi, cau: de.n_cau })));
  }

  /* Một lần đọc trạng thái cho cả hai khung; mỗi khung đăng ký riêng với `dangKyBuoc`. */

  function docRoiVe(khung, ve) {
    callApi("get_forms_buoc_12").then((res) => {
      if (!res.ok) { showErrorToast(res.errors); return; }
      clear(khung);
      ve(khung, res.data);
    });
  }

  dangKyBuoc(1, (khung) => docRoiVe(khung, veBuoc1));
  dangKyBuoc(2, (khung) => docRoiVe(khung, veBuoc2));

  return { duong, dangKyBuoc, lamMoi };
})();
