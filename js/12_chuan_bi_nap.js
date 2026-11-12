/* ==========================================================================
   12_chuan_bi_nap.js — worker B (FA-M9, FA-M10): bước 4 và 5 của thẻ "Chuẩn bị đợt".

   Bước 4 "Nạp kết quả từ biểu mẫu" (FA-M9, TH = chưa thử trên Microsoft thật): thả các tệp Forms / List,
   mỗi tệp hiện loại + ô chọn đề (đoán sẵn), bấm "Chuyển" -> (nếu cần) xác nhận lệch giữa các đề / bỏ câu
   -> xem trước Sổ nhập -> "Nhập sổ" (đường nhập CÓ SẴN import_so_nhap, không có đường thứ hai).

   Bước 5 "Sau khi xếp" (FA-M10): ba nút — xuất kết quả cho List KetQua, ai chưa đăng ký (nạp CSV danh sách lớp),
   đối chiếu hai lần xuất List (đường A; nạp CSV cũ + mới). Tệp ra rơi vào thư mục Tải xuống.
   ========================================================================== */
"use strict";

(() => {
  const S = {
    khoiTao: false,        // đã hỏi backend các tệp đã tải lên chưa
    tep: [],               // [{ten, base64|null, loai, bien_the_doan, loi, chu}]
    moi: false,            // true = tệp mới chọn, chưa gửi lên forms/nap/tai_len
    canDe: false,          // đề của đợt có biến thể
    kq: null,              // kết quả chuyển gần nhất (trang_thai "xong")
    choXN: null,           // {clb, thong_bao, bao_cao} khi đang chờ xác nhận
    dieuChinh: "",         // "" | "ap_dung" | "giu"
    boCau: [],             // [[clb, de, cau]]
    nhap: null,            // {n_hoc_sinh} sau khi nhập
    dang: false,
  };

  const khung = () => el("cb-buoc-4");

  function mot(tag, lop, chu) {
    const n = document.createElement(tag);
    if (lop) n.className = lop;
    if (chu !== undefined) n.textContent = chu;
    return n;
  }

  function nut(id, khoa, bamVao, lop) {
    const n = mot("button", lop || "btn btn-secondary", t(khoa));
    n.type = "button";
    n.id = id;
    n.addEventListener("click", bamVao);
    return n;
  }

  function trangThai(trang, chu) {
    const n = mot("div", "cb-trang-thai", chu);
    n.dataset.trangThai = trang;
    return n;
  }

  function doiRoiVe() { const k = khung(); if (k) { clear(k); ve(k); } }

  /* ---------- gọi backend ---------- */
  function docTep(file) {
    return new Promise((xong, hong) => {
      const doc = new FileReader();
      doc.onload = () => xong({ ten: file.name, base64: bufferSangBase64(doc.result) });
      doc.onerror = () => hong(doc.error);
      doc.readAsArrayBuffer(file);
    });
  }

  function nhanTep(danhSachFile) {
    const ds = Array.from(danhSachFile || []);
    if (!ds.length) return;
    Promise.all(ds.map(docTep)).then((files) =>
      callApi("nhan_dien_tep_forms", files).then((res) => {
        if (!res.ok) { showErrorToast(res.errors); return; }
        S.tep = res.data.tep.map((x, i) => Object.assign({}, x, { base64: files[i].base64, chu: x.bien_the_doan || "" }));
        S.canDe = res.data.can_chon_de;
        S.moi = true;
        S.kq = null; S.choXN = null; S.dieuChinh = ""; S.boCau = []; S.nhap = null;
        doiRoiVe();
      }));
  }

  function bienThe() {
    const kq = {};
    S.tep.forEach((x) => { if (x.loai === "bai_thi" && x.chu) kq[x.ten] = x.chu; });
    return kq;
  }

  function luaChon() {
    const lc = {};
    if (S.dieuChinh) lc.dieu_chinh = S.dieuChinh;
    if (S.boCau.length) lc.bo_cau = S.boCau;
    return lc;
  }

  function chuyen() {
    if (S.dang) return;
    S.dang = true;
    const files = S.moi ? S.tep.map((x) => ({ ten: x.ten, base64: x.base64 })) : null;
    callApi("chuyen_tep_forms", files, bienThe(), luaChon()).then((res) => {
      S.dang = false;
      if (!res.ok) { showErrorToast(res.errors); doiRoiVe(); return; }
      S.moi = false;
      S.nhap = null;
      if (res.data.trang_thai === "cho_xac_nhan") { S.choXN = res.data.cho_xac_nhan; S.kq = null; }
      else { S.choXN = null; S.kq = res.data; }
      doiRoiVe();
    });
  }

  function chonDieuChinh(gia_tri) { S.dieuChinh = gia_tri; chuyen(); }

  function chamLai() {
    S.boCau = Array.from(document.querySelectorAll("#cb-nap-bo-cau input:checked")).map((o) => JSON.parse(o.value));
    chuyen();
  }

  function nhapSo() {
    callApi("lay_so_nhap_nap").then((so) => {
      if (!so.ok) { showErrorToast(so.errors); return; }
      callApi("import_so_nhap", so.data.base64).then((res) => {
        if (!res.ok || !res.data) { showErrorToast(res.errors); return; }
        S.nhap = { n_hoc_sinh: res.data.n_hoc_sinh };
        doiRoiVe();
      });
    });
  }

  /* ---------- vẽ ---------- */
  function veKhungTha(k) {
    const o = mot("input");
    o.type = "file"; o.id = "cb-nap-tep"; o.multiple = true; o.accept = ".xlsx,.csv"; o.hidden = true;
    o.addEventListener("change", () => { nhanTep(o.files); o.value = ""; });
    k.appendChild(o);
    const tha = mot("div", "drop-zone cb-nap-tha");
    tha.id = "cb-nap-tha"; tha.tabIndex = 0; tha.setAttribute("role", "button");
    tha.appendChild(mot("div", "drop-zone-main", t("cb_nap_tha")));
    tha.appendChild(mot("div", "drop-zone-sub", t("cb_nap_tha_phu")));
    tha.addEventListener("click", () => o.click());
    tha.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); o.click(); } });
    tha.addEventListener("dragover", (e) => { e.preventDefault(); tha.classList.add("is-dragover"); });
    tha.addEventListener("dragleave", () => tha.classList.remove("is-dragover"));
    tha.addEventListener("drop", (e) => {
      e.preventDefault(); tha.classList.remove("is-dragover");
      nhanTep(e.dataTransfer && e.dataTransfer.files);
    });
    k.appendChild(tha);
  }

  function veBangTep(k) {
    const cuon = mot("div", "scroll-x");
    const bang = mot("table", "data-table");
    bang.id = "cb-nap-bang";
    const dau = bang.createTHead().insertRow();
    ["cb_nap_cot_tep", "cb_nap_cot_loai", "cb_nap_cot_de"].forEach((khoa) => {
      const th = mot("th", "", t(khoa)); th.scope = "col"; dau.appendChild(th);
    });
    const tb = bang.createTBody();
    S.tep.forEach((x, i) => {
      const tr = tb.insertRow();
      tr.dataset.ten = x.ten;
      tr.insertCell().textContent = x.ten;
      const oLoai = tr.insertCell();
      oLoai.className = "cb-nap-loai";
      oLoai.textContent = x.loi ? trErrs([x.loi]).join(" ") : t("cb_nap_loai_" + x.loai);
      if (x.loi) tr.classList.add("cb-nap-tep-loi");
      const oDe = tr.insertCell();
      if (x.loai === "bai_thi" && !x.loi && S.canDe) {
        const sel = mot("select");
        sel.id = "cb-nap-de-" + i;
        sel.setAttribute("aria-label", t("cb_nap_cot_de"));
        [["", t("cb_nap_de_chon")], ["A", "A"], ["B", "B"], ["C", "C"]].forEach(([v, chu]) => {
          const op = mot("option", "", chu); op.value = v; sel.appendChild(op);
        });
        sel.value = x.chu || "";
        sel.addEventListener("change", () => { x.chu = sel.value; capNhatNutChuyen(); });
        oDe.appendChild(sel);
        if (x.bien_the_doan) oDe.appendChild(mot("span", "hint-text", " " + t("cb_nap_de_doan", { chu: x.bien_the_doan })));
      }
    });
    cuon.appendChild(bang);
    k.appendChild(cuon);
  }

  function duocChuyen() {
    return S.tep.length > 0 && !S.dang && S.tep.every((x) => !x.loi && (x.loai !== "bai_thi" || !S.canDe || x.chu));
  }

  function capNhatNutChuyen() {
    const n = el("cb-nap-chuyen");
    if (n) n.disabled = !duocChuyen();
  }

  function veXacNhan(k) {
    const hop = mot("div", "cb-nap-xac-nhan");
    hop.id = "cb-nap-xac-nhan";
    hop.appendChild(trangThai("do", t("cb_nap_cho", { clb: S.choXN.clb.join(", ") })));
    hop.appendChild(mot("p", "hint-text", t("cb_nap_cho_ghi", { path: S.choXN.bao_cao })));
    const hang = mot("div", "cb-nut-hang");
    hang.appendChild(nut("cb-nap-ap-dung", "cb_nap_ap_dung", () => chonDieuChinh("ap_dung")));
    hang.appendChild(nut("cb-nap-giu", "cb_nap_giu", () => chonDieuChinh("giu")));
    hop.appendChild(hang);
    k.appendChild(hop);
  }

  function veKetQua(k) {
    const kq = S.kq;
    k.appendChild(trangThai("xanh", t("cb_nap_xong", { hs: kq.n_hoc_sinh, thi: kq.n_bai_thi })));
    if (kq.cau_co_co.length) {
      k.appendChild(mot("strong", "", t("cb_nap_bo_cau_tieu_de")));
      const ul = mot("ul", "cb-nap-bo-cau");
      ul.id = "cb-nap-bo-cau";
      kq.cau_co_co.forEach((c, i) => {
        const khoa = [c.club_id, c.bien_the, c.cau];
        const li = mot("li");
        const nhan = mot("label");
        const o = mot("input");
        o.type = "checkbox"; o.id = "cb-nap-bo-" + i; o.value = JSON.stringify(khoa);
        o.checked = S.boCau.some((b) => b[0] === khoa[0] && b[1] === khoa[1] && b[2] === khoa[2]);
        nhan.appendChild(o);
        nhan.appendChild(document.createTextNode(" " + t("cb_nap_bo_cau_dong", {
          clb: c.club_id, de: c.bien_the, cau: c.cau, co: c.co.join("; "), ti_le: Math.round(100 * c.ti_le_dung) })));
        li.appendChild(nhan);
        ul.appendChild(li);
      });
      k.appendChild(ul);
      k.appendChild(nut("cb-nap-cham-lai", "cb_nap_cham_lai", chamLai));
    }
    if (kq.canh_bao.length) {
      k.appendChild(mot("strong", "", t("cb_nap_canh_bao", { n: kq.canh_bao.length })));
      const ul = mot("ul", "cb-dong-loi");
      ul.id = "cb-nap-canh-bao";
      kq.canh_bao.slice(0, 30).forEach((c) => ul.appendChild(mot("li", "", (c.ma ? c.ma + ": " : "") + c.noi_dung)));
      k.appendChild(ul);
    }
    const xt = kq.xem_truoc;
    if (xt) {
      const p = mot("p", "", t("cb_nap_xem_truoc", { clb: xt.n_clb, hs: xt.n_hoc_sinh, nv: xt.n_nguyen_vong, thi: xt.n_thi }));
      p.id = "cb-nap-xem-truoc";
      k.appendChild(p);
    }
    if (kq.loi_xem_truoc.length || (xt && xt.loi.length)) {
      const ul = mot("ul", "cb-dong-loi");
      ul.id = "cb-nap-loi-so";
      trErrs(kq.loi_xem_truoc.concat(xt ? xt.loi : [])).forEach((x) => ul.appendChild(mot("li", "", x)));
      k.appendChild(ul);
    }
    kq.ghi_chu.forEach((g) => k.appendChild(mot("p", "hint-text", g)));
    k.appendChild(mot("p", "hint-text", t("cb_nap_nhac_quyet_tam")));
    if (S.nhap) {
      k.appendChild(trangThai("xanh", t("cb_nap_nhap_xong", { hs: S.nhap.n_hoc_sinh })));
    } else if (xt && !xt.loi.length && !kq.loi_xem_truoc.length) {
      k.appendChild(nut("cb-nap-nhap", "cb_nap_nhap", nhapSo, "btn btn-primary"));
    }
  }

  function ve(k) {
    if (!S.khoiTao) {
      S.khoiTao = true;
      callApi("get_forms_nap").then((res) => {
        if (res.ok && !S.tep.length && res.data.tep.length) {
          S.tep = res.data.tep.map((x) => Object.assign({}, x, { base64: null, chu: x.bien_the_doan || "" }));
          S.canDe = res.data.can_chon_de;
        }
        doiRoiVe();
      });
      return;
    }
    const duong = window.ChuanBi.duong();
    k.appendChild(mot("p", "hint-text", t("cb_nap_ghi")));
    if (!duong) { k.appendChild(trangThai("chua", t("cb_nap_chua_duong"))); return; }
    k.appendChild(mot("p", "hint-text", t(duong === "A" ? "cb_nap_ghi_a" : "cb_nap_ghi_b")));
    veKhungTha(k);
    if (!S.tep.length) { k.appendChild(trangThai("chua", t("cb_nap_chua_tep"))); return; }
    veBangTep(k);
    const hang = mot("div", "cb-nut-hang");
    const n = nut("cb-nap-chuyen", "cb_nap_chuyen", chuyen, "btn btn-primary");
    n.disabled = !duocChuyen();
    hang.appendChild(n);
    k.appendChild(hang);
    if (S.choXN) veXacNhan(k);
    else if (S.kq) veKetQua(k);
  }

  window.ChuanBi.dangKyBuoc(4, ve);
})();

/* ===================== Bước 5 "Sau khi xếp" (FA-M10) ===================== */
(() => {
  const S5 = { xuat: null, ai: null, dc: null, lop: null, cu: null, moi: null, dang: "" };

  const khung = () => el("cb-buoc-5");

  function mot(tag, lop, chu) {
    const n = document.createElement(tag);
    if (lop) n.className = lop;
    if (chu !== undefined) n.textContent = chu;
    return n;
  }

  function nut(id, khoa, bamVao) {
    const n = mot("button", "btn btn-secondary", t(khoa));
    n.type = "button"; n.id = id;
    n.addEventListener("click", bamVao);
    return n;
  }

  function trangThai(trang, chu) {
    const n = mot("div", "cb-trang-thai", chu);
    n.dataset.trangThai = trang;
    return n;
  }

  function veLai() { const k = khung(); if (k) { clear(k); ve(k); } }

  function docTep(file) {
    return new Promise((xong, hong) => {
      const doc = new FileReader();
      doc.onload = () => xong({ ten: file.name, base64: bufferSangBase64(doc.result) });
      doc.onerror = () => hong(doc.error);
      doc.readAsArrayBuffer(file);
    });
  }

  /* Ô chọn một tệp CSV; nhớ tệp trong S5[khoa] và bật / tắt nút liên quan. */
  function oChonTep(k, id, khoaNhan, khoa, nutId) {
    const nhan = mot("label", "cb-nap5-chon");
    nhan.appendChild(mot("span", "", t(khoaNhan) + " "));
    const o = mot("input");
    o.type = "file"; o.id = id; o.accept = ".csv";
    o.addEventListener("change", () => {
      const f = o.files && o.files[0];
      if (!f) { S5[khoa] = null; return; }
      docTep(f).then((x) => { S5[khoa] = x; capNhatNut(nutId); });
    });
    nhan.appendChild(o);
    if (S5[khoa]) nhan.appendChild(mot("span", "hint-text", " " + S5[khoa].ten));
    k.appendChild(nhan);
  }

  const DIEU_KIEN = {
    "cb-nap5-ai": () => !!S5.lop && !S5.dang,
    "cb-nap5-dc": () => !!S5.cu && !!S5.moi && !S5.dang,
    "cb-nap5-xuat": () => !S5.dang,
  };

  function capNhatNut(id) { const n = el(id); if (n) n.disabled = !DIEU_KIEN[id](); }

  function goi(ten, args, khoa) {
    if (S5.dang) return;
    S5.dang = ten;
    callApi.apply(null, [ten].concat(args)).then((res) => {
      S5.dang = "";
      if (!res.ok) { S5[khoa] = null; showErrorToast(res.errors); veLai(); return; }
      S5[khoa] = res.data;
      veLai();
    });
  }

  function phan(k, tieuDe, ghi) {
    const p = mot("div", "cb-nap5-phan");
    p.appendChild(mot("strong", "", t(tieuDe)));
    p.appendChild(mot("p", "hint-text", t(ghi)));
    k.appendChild(p);
    return p;
  }

  function veXuat(k) {
    const p = phan(k, "cb_nap_s5_xuat", "cb_nap_s5_xuat_ghi");
    const n = nut("cb-nap5-xuat", "cb_nap_s5_xuat_nut", () => goi("xuat_ket_qua_list", [], "xuat"));
    n.disabled = !DIEU_KIEN["cb-nap5-xuat"]();
    p.appendChild(n);
    const r = S5.xuat;
    if (r) {
      const o = trangThai("xanh", t("cb_nap_s5_xuat_xong", { n: r.n_rows, path: r.path }));
      o.id = "cb-nap5-xuat-kq";
      p.appendChild(o);
      const cb = r.canh_bao.concat(trErrs(r.canh_bao_ly_do || []));
      if (cb.length) {
        const ul = mot("ul", "cb-dong-loi");
        cb.slice(0, 30).forEach((c) => ul.appendChild(mot("li", "", c)));
        p.appendChild(ul);
      }
    }
  }

  function veAi(k) {
    const p = phan(k, "cb_nap_s5_ai", "cb_nap_s5_ai_ghi");
    oChonTep(p, "cb-nap5-lop", "cb_nap_s5_chon_lop", "lop", "cb-nap5-ai");
    const n = nut("cb-nap5-ai", "cb_nap_s5_ai_nut", () => goi("ai_chua_dang_ky", [S5.lop.base64], "ai"));
    n.disabled = !DIEU_KIEN["cb-nap5-ai"]();
    p.appendChild(n);
    const r = S5.ai;
    if (r) {
      const o = trangThai("xanh", t("cb_nap_s5_ai_xong", { lop: r.n_lop, duoi: r.n_duoi, email: r.n_email, path: r.thu_muc }));
      o.id = "cb-nap5-ai-kq";
      p.appendChild(o);
      if (r.vuot_gioi_han) p.appendChild(trangThai("do", t("cb_nap_s5_vuot")));
    }
  }

  function veDoiChieu(k) {
    const p = phan(k, "cb_nap_s5_dc", "cb_nap_s5_dc_ghi");
    oChonTep(p, "cb-nap5-cu", "cb_nap_s5_cu", "cu", "cb-nap5-dc");
    oChonTep(p, "cb-nap5-moi", "cb_nap_s5_moi", "moi", "cb-nap5-dc");
    const n = nut("cb-nap5-dc", "cb_nap_s5_dc_nut", () => goi("doi_chieu_hai_lan", [S5.cu.base64, S5.moi.base64], "dc"));
    n.disabled = !DIEU_KIEN["cb-nap5-dc"]();
    p.appendChild(n);
    const r = S5.dc;
    if (r) {
      const o = trangThai("xanh", t("cb_nap_s5_dc_xong", {
        moi: r.dem.moi, rut: r.dem.rut, nv: r.dem.doi_nv, lop: r.dem.doi_lop, co_so: r.dem.doi_co_so, path: r.path }));
      o.id = "cb-nap5-dc-kq";
      p.appendChild(o);
      if (r.n_clb_la) p.appendChild(trangThai("do", t("cb_nap_s5_dc_la", { n: r.n_clb_la })));
    }
  }

  function ve(k) {
    const duong = window.ChuanBi.duong();
    k.appendChild(mot("p", "hint-text", t("cb_nap_s5_ghi")));
    if (!duong) { k.appendChild(trangThai("chua", t("cb_nap_chua_duong"))); return; }
    veXuat(k);
    veAi(k);
    if (duong === "A") veDoiChieu(k);
  }

  window.ChuanBi.dangKyBuoc(5, ve);
})();
