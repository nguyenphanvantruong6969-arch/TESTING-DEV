/* ==========================================================================
   10_theo_doi.js — theo dõi sau khi xếp (FA gaps, V§9.3), thẻ "Chi tiết và xuất tệp".

   GAP-1: điểm danh 3 buổi đầu. Khung `#diemDanhPanel` chỉ hiện khi `rules.fa_diem_danh` bật
   (get_diem_danh trả bat: false thì ẩn). Đổi một ô -> luu_diem_danh; đủ 2/3 buổi vắng không phép thì
   backend ghi một dòng giải phóng chỗ (không sửa kết quả xếp) và dòng hiện "Đã giải phóng chỗ".

   GAP-2: lời mời vào chỗ trống. Khung `#moiPanel` liệt kê mọi lời mời (mới nhất trước); lời mời đang chờ có ba
   nút Nhận / Từ chối / Hết hạn -> tra_loi_moi; backend tự mời người kế tiếp.
   ========================================================================== */

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
    const panel = el("diemDanhPanel");
    const bat = !!(res && res.ok && res.data.bat);
    panel.hidden = !bat;
    if (!bat) return;
    veDiemDanh(res.data);
  }).then(() => (el("diemDanhPanel").hidden ? (el("moiPanel").hidden = true) : taiMoi()));
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
    const bat = !!(res && res.ok && res.data.bat);
    el("moiPanel").hidden = !bat;
    if (bat) veMoi(res.data.moi);
  });
}

function khoiTaoTheoDoi() {
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
