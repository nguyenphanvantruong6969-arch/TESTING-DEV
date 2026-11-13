/* ==========================================================================
   10_theo_doi.js — theo dõi sau khi xếp (FA gaps, V§9.3), thẻ "Chi tiết và xuất tệp".

   GAP-1: điểm danh 3 buổi đầu. Khung `#diemDanhPanel` chỉ hiện khi `rules.fa_diem_danh` bật
   (get_diem_danh trả bat: false thì ẩn). Đổi một ô -> luu_diem_danh; đủ 2/3 buổi vắng không phép thì
   backend ghi một dòng giải phóng chỗ (không sửa kết quả xếp) và dòng hiện "Đã giải phóng chỗ".

   GAP-2: lời mời vào chỗ trống. Khung `#moiPanel` liệt kê mọi lời mời (mới nhất trước); lời mời đang chờ có ba
   nút Nhận / Từ chối / Hết hạn -> tra_loi_moi; backend tự mời người kế tiếp.

   GAP-3: khiếu nại lỗi dữ liệu. Khung `#khieuNaiPanel`: biểu mẫu gửi + danh sách; khiếu nại đang chờ có nút
   Chấp nhận / Từ chối. Không có nút nào chạy xếp hay sửa kết quả: sửa dữ liệu rồi chạy lại như thường.

   GAP-4: vòng 2. Khung `#vong2Panel`: mỗi học sinh cần vòng 2 một ô chọn CLB còn chỗ; "Chạy vòng 2" chạy MỘT lượt.

   GAP-5/6: ba câu phản hồi một chạm ở thẻ "Kết quả" (`#phanHoiPanel`) và khung tổng hợp + nạp tệp Forms ở thẻ này
   (`#phanHoiTongPanel`).

   GAP-8: bảng điều khiển quản trị (`#dashboardPanel`, thẻ Quản lý), chỉ đọc; thiếu dữ liệu ghi "chưa có dữ liệu".

   Mọi khung: `bat: false` -> ẩn; lời gọi lỗi (ok=false) -> ẩn VÀ báo lỗi (không im lặng).
   ========================================================================== */

/* `res` của get_* sau khi xếp: true khi khung phải hiện. Lỗi thật thì báo, không coi là "tính năng tắt". */
function batKhung(idKhung, res) {
  const bat = !!(res && res.ok && res.data.bat);
  el(idKhung).hidden = !bat;
  if (res && !res.ok) showErrorToast(res.errors);
  return bat;
}

const DD_TRANG_THAI = [["", ""], ["CO_MAT", "dd_co_mat"], ["VANG_CO_PHEP", "dd_vang_co_phep"],
  ["VANG_KHONG_PHEP", "dd_vang_khong_phep"]];
let ddClbDangChon = "";

function veDiemDanh(d) {
  const chon = el("diemDanhClb");
  clear(chon);
  d.clubs.forEach((c) => {
    const o = document.createElement("option");
    o.value = c.club_id;
    o.textContent = c.buoi ? c.name + " · " + nhanBuoi(c.buoi) : c.name;
    chon.appendChild(o);
  });
  chon.value = d.club_id;
  ddClbDangChon = d.club_id;
  document.querySelectorAll("#diemDanhPanel .dd-cot-buoi").forEach((th) => {
    th.textContent = t("dd_buoi_n", { n: th.dataset.so });
  });
  const body = el("diemDanhBang");
  clear(body);
  const manh = document.createDocumentFragment();
  d.hoc_sinh.forEach((h) => {
    const tr = document.createElement("tr");
    tr.dataset.studentId = h.student_id;
    const oMa = document.createElement("td");
    oMa.textContent = h.student_id;
    const oTen = document.createElement("td");
    oTen.textContent = h.name;
    if (h.da_giai_phong) {
      const tag = document.createElement("span");
      tag.className = "club-tag is-empty dd-giai-phong";
      tag.textContent = t("dd_da_giai_phong");
      oTen.append(" ", tag);
    }
    tr.append(oMa, oTen);
    [1, 2, 3].forEach((so) => {
      const td = document.createElement("td");
      const s = document.createElement("select");
      s.className = "text-input text-input-sm dd-o";
      s.dataset.studentId = h.student_id;
      s.dataset.buoiSo = String(so);
      s.setAttribute("aria-label", h.student_id + " · " + t("dd_buoi_n", { n: so }));
      DD_TRANG_THAI.forEach(([gt, khoa]) => {
        const o = document.createElement("option");
        o.value = gt;
        o.textContent = khoa ? t(khoa) : "";
        s.appendChild(o);
      });
      s.value = h["buoi_" + so] || "";
      td.appendChild(s);
      tr.appendChild(td);
    });
    const oDem = document.createElement("td");
    oDem.textContent = String(h.so_vang_khong_phep);
    tr.appendChild(oDem);
    manh.appendChild(tr);
  });
  body.appendChild(manh);
}

function taiDiemDanh(clubId) {
  return callApi("get_diem_danh", clubId === undefined ? ddClbDangChon : clubId).then((res) => {
    if (batKhung("diemDanhPanel", res)) veDiemDanh(res.data);
  }).then(() => (el("diemDanhPanel").hidden ? (el("moiPanel").hidden = true) : taiMoi()))
    .then(taiKhieuNai).then(() => taiVong2()).then(taiPhanHoi);
}

function veMoi(ds) {
  const ul = el("moiDanhSach");
  clear(ul);
  if (!ds.length) {
    const li = document.createElement("li");
    li.className = "hint";
    li.textContent = t("moi_trong");
    ul.appendChild(li);
    return;
  }
  ds.forEach((m) => {
    const li = document.createElement("li");
    li.dataset.moiId = String(m.id);
    li.textContent = t("moi_dong", { name: m.name, student_id: m.student_id, club: m.club_name,
      buoi: nhanBuoi(m.buoi) }) + " — " + t("moi_trang_thai_" + m.trang_thai);
    if (m.trang_thai === "CHO") {
      [["nhan", "moi_nhan"], ["tu_choi", "moi_tu_choi"], ["het_han", "moi_het_han"]].forEach(([kq, khoa]) => {
        const b = document.createElement("button");
        b.type = "button";
        b.className = "btn btn-ghost moi-tra-loi";
        b.dataset.moiId = String(m.id);
        b.dataset.ketQua = kq;
        b.textContent = t(khoa);
        li.append(" ", b);
      });
    }
    ul.appendChild(li);
  });
}

function taiMoi() {
  return callApi("get_moi_cho_trong").then((res) => {
    if (batKhung("moiPanel", res)) veMoi(res.data.moi);
  });
}

let knSoNgay = 3;

function veKhieuNai(d) {
  knSoNgay = d.so_ngay;
  el("knGoiY").textContent = t("kn_goi_y", { n: d.so_ngay });
  const chon = el("knBuoi");
  const cu = chon.value;
  clear(chon);
  d.ds_buoi.forEach((b) => {
    const o = document.createElement("option");
    o.value = b;
    o.textContent = nhanBuoi(b);
    chon.appendChild(o);
  });
  if (d.ds_buoi.includes(cu)) chon.value = cu;
  const ul = el("knDanhSach");
  clear(ul);
  if (!d.khieu_nai.length) {
    const li = document.createElement("li");
    li.className = "hint";
    li.textContent = t("kn_trong");
    ul.appendChild(li);
    return;
  }
  d.khieu_nai.forEach((k) => {
    const li = document.createElement("li");
    let chu = t("kn_dong", { name: k.name, student_id: k.student_id, buoi: nhanBuoi(k.buoi), ghi_chu: k.ghi_chu || "" })
      + " — " + t("kn_trang_thai_" + k.trang_thai);
    if (k.trang_thai === "CHAP_NHAN") {
      chu += " (" + (k.da_chay_lai ? t("kn_da_chay_lai", { n: k.dieu_chinh_cu.length }) : t("kn_can_chay_lai")) + ")";
    }
    li.textContent = chu;
    if (k.trang_thai === "CHO") {
      [["1", "kn_chap_nhan"], ["0", "kn_tu_choi"]].forEach(([gt, khoa]) => {
        const b = document.createElement("button");
        b.type = "button";
        b.className = "btn btn-ghost kn-xu-ly";
        b.dataset.knId = String(k.id);
        b.dataset.chapNhan = gt;
        b.textContent = t(khoa);
        li.append(" ", b);
      });
    }
    ul.appendChild(li);
  });
}

function taiKhieuNai() {
  return callApi("get_khieu_nai").then((res) => {
    if (batKhung("khieuNaiPanel", res)) veKhieuNai(res.data);
  });
}

let v2Buoi = "";

function veVong2(d) {
  v2Buoi = d.buoi;
  const chon = el("v2Buoi");
  clear(chon);
  d.ds_buoi.forEach((b) => {
    const o = document.createElement("option");
    o.value = b;
    o.textContent = nhanBuoi(b);
    chon.appendChild(o);
  });
  chon.value = d.buoi;
  const body = el("v2Bang");
  clear(body);
  d.hoc_sinh.forEach((h) => {
    const tr = document.createElement("tr");
    const a = document.createElement("td");
    a.textContent = h.student_id;
    const b = document.createElement("td");
    b.textContent = h.name;
    const c = document.createElement("td");
    const s = document.createElement("select");
    s.className = "text-input text-input-sm v2-chon";
    s.dataset.studentId = h.student_id;
    s.setAttribute("aria-label", h.student_id + " · " + t("v2_chon"));
    const o0 = document.createElement("option");
    o0.value = "";
    o0.textContent = t("v2_khong_chon");
    s.appendChild(o0);
    d.cho_con_lai.forEach((k) => {
      const o = document.createElement("option");
      o.value = k.club_id;
      o.textContent = t("v2_cho", { name: k.name, n: k.con });
      s.appendChild(o);
    });
    s.disabled = d.da_chay;
    c.appendChild(s);
    tr.append(a, b, c);
    body.appendChild(tr);
  });
  el("btnChayVong2").disabled = d.da_chay || !d.hoc_sinh.length;
  if (d.da_chay) el("v2KetQua").textContent = t("v2_da_chay");
  else if (!d.hoc_sinh.length) el("v2KetQua").textContent = t("v2_trong");
}

function taiVong2(buoi) {
  return callApi("get_vong_2", buoi === undefined ? v2Buoi : buoi).then((res) => {
    if (batKhung("vong2Panel", res)) veVong2(res.data);
  });
}

const phChon = {};

function tyLe(x) {
  return x === null || x === undefined ? t("ph_chua_co") : Math.round(x * 100) + "%";
}

function taiPhanHoi() {
  return callApi("get_phan_hoi_tong_hop").then((res) => {
    const bat = batKhung("phanHoiTongPanel", res);
    el("phanHoiPanel").hidden = !bat;
    if (!bat) return;
    const k = res.data.ket_qua;
    const w = res.data.tuan_3;
    let chu = t("ph_tong_hop", { n: k.n, tb: k.hai_long_tb === null ? t("ph_chua_co") : k.hai_long_tb.toFixed(2),
      hieu: tyLe(k.hieu_ly_do_ty_le) });
    if (w.n) chu += " " + t("ph_tong_tuan_3", { n: w.n, con_di: tyLe(w.con_di_ty_le), muon_doi: tyLe(w.muon_doi_ty_le) });
    el("phTongHop").textContent = chu;
  });
}

function khoiTaoPhanHoi() {
  [["ph-hai-long", "hai_long"], ["ph-hieu", "hieu"], ["ph-kho", "kho"]].forEach(([lop, khoa]) => {
    document.querySelectorAll("#phanHoiPanel button." + lop).forEach((b) => {
      b.addEventListener("click", () => {
        phChon[khoa] = b.dataset.giaTri;
        document.querySelectorAll("#phanHoiPanel button." + lop).forEach((x) => {
          x.setAttribute("aria-pressed", x === b ? "true" : "false");
        });
      });
    });
  });
  el("btnGuiPhanHoi").addEventListener("click", (e) => {
    const ma = el("phMa").value.trim();
    if (!ma || !phChon.hai_long || !phChon.hieu || !phChon.kho) {
      el("phKetQua").textContent = t("ph_thieu");
      return;
    }
    khiBan(e.currentTarget, () => callApi("gui_phan_hoi", ma, Number(phChon.hai_long), phChon.hieu === "1",
      phChon.kho)).then((res) => {
      if (!res.ok) {
        showErrorToast(res.errors);
        el("phKetQua").textContent = trErrs(res.errors).join(" ");
        return;
      }
      el("phKetQua").textContent = t("ph_cam_on");
      Object.keys(phChon).forEach((k) => delete phChon[k]);
      document.querySelectorAll("#phanHoiPanel button[aria-pressed]").forEach((x) => {
        x.setAttribute("aria-pressed", "false");
      });
      el("phMa").value = "";
    });
  });
  el("btnXuatPhanHoi").addEventListener("click", () => {
    chayXuat([["xuat_muc_phan_hoi", "export_phan_hoi", [""],
      (d) => t("xuat_kq_tep_csv", { n: d.n_rows, path: d.path })]], el("phNhapKetQua"));
  });
  el("btnNhapPhanHoi").addEventListener("click", () => el("phTep").click());
  el("phTep").addEventListener("change", (e) => {
    const tep = e.target.files && e.target.files[0];
    if (!tep) return;
    const doc = new FileReader();
    doc.onload = () => {
      callApi("nhap_phan_hoi_forms", bufferSangBase64(doc.result)).then((res) => {
        e.target.value = "";
        if (!res.ok) {
          showErrorToast(res.errors);
          return;
        }
        el("phNhapKetQua").textContent = t("ph_nhap_xong", { n: res.data.n_ket_qua, m: res.data.n_tuan_3,
          b: res.data.bo_qua });
        taiPhanHoi();
      });
    };
    doc.readAsArrayBuffer(tep);
  });
  /* FA-M6b: MỘT tệp "Sau khi xem kết quả" (phản hồi + khiếu nại) -> một thông báo có số đếm và các khiếu nại không nhận. */
  el("btnNhapSauKetQua").addEventListener("click", () => el("phTepSauKetQua").click());
  el("phTepSauKetQua").addEventListener("change", (e) => {
    const tep = e.target.files && e.target.files[0];
    if (!tep) return;
    const doc = new FileReader();
    doc.onload = () => {
      callApi("nhap_sau_ket_qua_forms", bufferSangBase64(doc.result)).then((res) => {
        e.target.value = "";
        if (!res.ok) {
          showErrorToast(res.errors);
          return;
        }
        const d = res.data;
        const dongLoi = (d.khieu_nai_loi || []).map((x) => {
          const buoi = nhanBuoi(x.buoi);
          return t("ssk_loi_dong", { student_id: x.student_id, buoi, loi: trErr({ code: x.code,
            params: { student_id: x.student_id, buoi, so_ngay: knSoNgay } }) });
        });
        const canhBao = (d.canh_bao || []).map(trErr);
        const chu = [t("ssk_nap_xong", { n: d.n_ket_qua, m: d.n_khieu_nai, b: d.bo_qua })]
          .concat(dongLoi, canhBao).join(" ");
        el("phNhapKetQua").textContent = chu;
        showToast(chu, dongLoi.length || canhBao.length ? "warn" : "success");
        taiPhanHoi().then(taiKhieuNai);
      });
    };
    doc.readAsArrayBuffer(tep);
  });
}

/* GAP-8: giá trị một chỉ số — tỉ lệ thành %, số đếm giữ nguyên, None -> "chưa có dữ liệu" (không bao giờ 0). */
const DB_SO_DEM = ["khong_co_clb", "thua_boc_tham_1_lan"];
function giaTriChiSo(c) {
  if (c.gia_tri === null || c.gia_tri === undefined) return t("db_chua_co");
  if (DB_SO_DEM.includes(c.ma)) return String(c.gia_tri);
  if (c.ma === "hai_long_tb" || c.ma === "do_lech_cham") return c.gia_tri.toFixed(2);
  return Math.round(c.gia_tri * 1000) / 10 + "%";
}

function taiDashboard() {
  return callApi("get_dashboard").then((res) => {
    if (!batKhung("dashboardPanel", res)) return;
    const body = el("dbBangBody");
    clear(body);
    res.data.chi_so.forEach((c) => {
      const tr = document.createElement("tr");
      tr.dataset.ma = c.ma;
      const dat = c.dat === null ? "" : t(c.dat ? "db_dat" : "db_chua_dat");
      [t("db_" + c.ma), giaTriChiSo(c), t("db_mt_" + c.muc_tieu), dat].forEach((chu) => {
        const td = document.createElement("td");
        td.textContent = chu;
        tr.appendChild(td);
      });
      body.appendChild(tr);
    });
  });
}

function khoiTaoTheoDoi() {
  khoiTaoPhanHoi();
  el("btnXuatDashboard").addEventListener("click", () => {
    chayXuat([["xuat_muc_dashboard", "export_dashboard", [""],
      (d) => t("xuat_kq_tep_csv", { n: d.n_rows, path: d.path })]], el("dbFeedback"));
  });
  el("v2Buoi").addEventListener("change", (e) => {
    el("v2KetQua").textContent = "";
    taiVong2(e.target.value);
  });
  /* khiBan mở lại nút khi xong; sau một lượt thành công thì khoá lại (vòng 2 chỉ chạy một lượt). */
  el("btnChayVong2").addEventListener("click", (e) => {
    const nut = e.currentTarget;
    khiBan(nut, () => {
      const chon = {};
      document.querySelectorAll("#v2Bang select.v2-chon").forEach((s) => {
        if (s.value) chon[s.dataset.studentId] = [s.value];
      });
      return callApi("chay_vong_2_api", v2Buoi, chon);
    }).then((res) => {
      if (!res.ok) {
        showErrorToast(res.errors);
        return null;
      }
      /* taiDiemDanh nạp lại mọi khung (cả vòng 2); ghi kết quả SAU cùng để không bị câu "đã chạy" đè. */
      return taiDiemDanh().then(() => {
        nut.disabled = true;
        el("v2KetQua").textContent = t("v2_ket_qua", { n: res.data.xep.length, m: res.data.bo_qua.length });
      });
    });
  });
  el("btnGuiKhieuNai").addEventListener("click", (e) => khiBan(e.currentTarget, () =>
    callApi("gui_khieu_nai", el("knMa").value.trim(), el("knBuoi").value, el("knGhiChu").value).then((res) => {
      if (!res.ok) {
        showErrorToast(res.errors);
        return null;
      }
      el("knGhiChu").value = "";
      return taiKhieuNai();
    })));
  el("knDanhSach").addEventListener("click", (e) => {
    const b = e.target.closest("button.kn-xu-ly");
    if (!b) return;
    b.disabled = true;
    callApi("xu_ly_khieu_nai", Number(b.dataset.knId), b.dataset.chapNhan === "1", "").then((res) => {
      if (!res.ok) showErrorToast(res.errors);
      return taiKhieuNai();
    });
  });
  el("btnXuatKhieuNai").addEventListener("click", () => {
    chayXuat([["xuat_muc_khieu_nai", "export_khieu_nai", [""],
      (d) => t("xuat_kq_tep_csv", { n: d.n_rows, path: d.path })]], el("knFeedback"));
  });
  el("moiDanhSach").addEventListener("click", (e) => {
    const b = e.target.closest("button.moi-tra-loi");
    if (!b) return;
    b.disabled = true;
    callApi("tra_loi_moi", Number(b.dataset.moiId), b.dataset.ketQua).then((res) => {
      if (!res.ok) showErrorToast(res.errors);
      return taiDiemDanh();
    });
  });
  el("diemDanhClb").addEventListener("change", (e) => taiDiemDanh(e.target.value));
  el("diemDanhBang").addEventListener("change", (e) => {
    const s = e.target.closest("select.dd-o");
    if (!s) return;
    callApi("luu_diem_danh", ddClbDangChon, s.dataset.studentId, Number(s.dataset.buoiSo), s.value)
      .then((res) => {
        if (!res.ok) showErrorToast(res.errors);
        return taiDiemDanh();
      });
  });
  el("btnXuatDiemDanh").addEventListener("click", () => {
    chayXuat([["xuat_muc_diem_danh", "export_diem_danh", [""],
      (d) => t("xuat_kq_diem_danh", { n: d.n_clb, path: d.path })]], el("diemDanhFeedback"));
  });
}

khoiTaoTheoDoi();
