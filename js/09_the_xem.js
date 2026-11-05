/* js/09_the_xem.js — Thẻ 02 "Kết quả": màn XEM chỉ đọc cho Ban giám hiệu, người phụ trách CLB và
   giáo viên chủ nhiệm (gộp thẻ Kết quả cũ, Thành viên CLB và Theo lớp).

   Chỉ kết quả xếp: KHÔNG điểm thi, điểm quyết tâm, số bốc thăm hay diện trúng tuyển. Ba cách xem
   (tầng 1): Theo lớp | Theo CLB | Theo mã học sinh. Nút "Theo lớp" CHỈ hiện khi đã có ít nhất một
   lớp (T3-16); chưa có lớp thì mặc định xem Theo mã học sinh. Sắp hàng: bấm tiêu đề cột (T3-17,
   không còn hàng nút tầng 2; không có cột "Thứ tự", T3-18). Lựa chọn tầng 1, lớp, CLB nhớ theo máy
   (localStorage). "Tải bảng này (Excel)" (T3-19) xuất đúng bảng đang xem qua export_bang_dang_xem.
   Dùng lại các API có sẵn: get_thoi_khoa_bieu, get_danh_sach_clb, get_club_fill_stats,
   list_classes. Một phần của giao diện chính: script thường, dùng chung phạm vi với các tệp js/.
*/
"use strict";

const KHOA_KQ_XEM = "rbda_ket_qua_xem_v1";
const KQ_TANG1 = ["lop", "clb", "ma"];
const KQ_KHONG_NGAY = 9999;          // hàng chưa có CLB nào: xếp sau mọi ngày

const kq = {
  tang1: "lop",
  sapCot: null,        // cột đang sắp (chỉ số trong bảng); null = cột mã
  sapGiam: false,      // true = giảm dần
  bang: null,          // bảng vừa vẽ (để vẽ lại khi đổi cột sắp, không gọi lại API)
  lop: null,           // lớp đang chọn ("" là lớp thật: Chưa có lớp); null = chưa chọn
  clb: "",             // mã CLB đang chọn
  coKq: false,
  nLop: 0,
  nClb: 0,
  dsClb: [],           // CLB (đã sắp theo buổi theo ngày, rồi theo tên) cho ô chọn CLB
};

/* Nhớ lựa chọn hai tầng. Kho lưu trữ hỏng hay bị chặn thì dùng mặc định, KHÔNG làm hỏng thẻ. */
function docKqXem() {
  try {
    const raw = window.localStorage && window.localStorage.getItem(KHOA_KQ_XEM);
    if (!raw) return;
    const luu = JSON.parse(raw);
    if (luu && KQ_TANG1.includes(luu.tang1)) kq.tang1 = luu.tang1;
    /* Lớp và CLB đã chọn: nếu không còn tồn tại thì kqNapOLop / kqNapOClb tự lùi về mục đầu. */
    if (luu && typeof luu.lop === "string") kq.lop = luu.lop;
    if (luu && typeof luu.clb === "string") kq.clb = luu.clb;
  } catch (e) { /* dùng mặc định */ }
}

function luuKqXem() {
  try {
    if (window.localStorage) {
      window.localStorage.setItem(KHOA_KQ_XEM, JSON.stringify({ tang1: kq.tang1, lop: kq.lop, clb: kq.clb }));
    }
  } catch (e) { /* không ghi được thì thôi */ }
}

/* ---- Sắp hàng (bấm tiêu đề cột) ---- */

function kqSoMa(a, b) {
  return String(a.student_id).localeCompare(String(b.student_id), undefined,
    { numeric: true, sensitivity: "base" }) || (a.student_id < b.student_id ? -1 : a.student_id > b.student_id ? 1 : 0);
}

/* `dsLopHienCo` (js/04) giữ thứ tự tự nhiên của backend (10H2 trước 10H10); lớp trống xếp cuối. */
function kqHangLop(lop) {
  const i = lop ? dsLopHienCo.indexOf(lop) : -1;
  return i < 0 ? KQ_KHONG_NGAY : i;
}

/* Sắp theo cột `cot` (chỉ số trong `k` của hàng). Cột mã: số tự nhiên; cột lớp: thứ tự lớp của
   backend; còn lại so chữ theo tiếng Việt. Ô trống luôn nằm cuối, giữ nguyên chiều tăng/giảm. */
function kqSapHang(hang, cot, cotLop, giam) {
  const dau = giam ? -1 : 1;
  const so = (a, b) => {
    if (cot === 0) return dau * kqSoMa(a, b);
    if (cot === cotLop) {
      if (!a.class_id !== !b.class_id) return a.class_id ? -1 : 1;
      return dau * (kqHangLop(a.class_id) - kqHangLop(b.class_id)) || kqSoMa(a, b);
    }
    const x = String(a.k[cot] || ""), y = String(b.k[cot] || "");
    if (!x !== !y) return x ? -1 : 1;
    return dau * x.localeCompare(y, "vi") || kqSoMa(a, b);
  };
  return hang.slice().sort(so);
}

/* ---- Khung chung ---- */

function kqBaoRong(khoaChu, thamSo) {
  el("kqRong").textContent = t(khoaChu, thamSo);
  el("kqRong").hidden = false;
  el("kqBang").hidden = true;
}

function kqDongBoDieuKhien() {
  document.querySelectorAll("#kqTang1 .kq-seg-nut").forEach((n) => {
    const on = n.dataset.kq === kq.tang1;
    n.classList.toggle("is-on", on);
    n.setAttribute("aria-pressed", on ? "true" : "false");
  });
  /* T3-16: chưa có lớp nào thì không có nút "Theo lớp" (chỉ hiện khi có ít nhất một lớp). */
  document.querySelector('#kqTang1 [data-kq="lop"]').hidden = !kq.nLop;
  el("kqChonLopHang").hidden = kq.tang1 !== "lop";
  el("kqChonClbHang").hidden = kq.tang1 !== "clb";
  el("kqTimHang").hidden = kq.tang1 !== "ma";
  el("btnKqTaiBang").disabled = !kq.coKq || (kq.tang1 === "lop" && kq.lop === null) || (kq.tang1 === "clb" && !kq.nClb);
}

function kqNapOLop(d) {
  const sel = el("kqChonLop");
  clear(sel);
  d.classes.forEach((c) => themOption(sel, c.class_id, c.class_id + " (" + c.n + ")"));
  if (d.n_khong_lop) themOption(sel, "", t("lop_chua_co") + " (" + d.n_khong_lop + ")");
  const co = (v) => Array.from(sel.options).some((o) => o.value === v);
  if (kq.lop === null || !co(kq.lop)) kq.lop = sel.options.length ? sel.options[0].value : null;
  if (kq.lop !== null) sel.value = kq.lop;
  sel.disabled = !d.classes.length;
}

/* Buổi giữ thứ tự backend (đã theo ngày trong tuần); trong một buổi sắp theo tên. */
function kqSapClb(ds) {
  const nhom = new Map();
  ds.forEach((c) => {
    if (!nhom.has(c.buoi)) nhom.set(c.buoi, []);
    nhom.get(c.buoi).push(c);
  });
  const ra = [];
  nhom.forEach((cac) => {
    cac.sort((a, b) => String(a.name || a.club_id).localeCompare(String(b.name || b.club_id), "vi"));
    ra.push(...cac);
  });
  return ra;
}

/* Ô chọn CLB: nhóm theo buổi (thứ tự ngày), mỗi buổi một nhóm. Trường một buổi thì danh sách phẳng. */
function kqNapOClb(ds) {
  const sel = el("kqChonClb");
  clear(sel);
  const nhieuBuoi = new Set(ds.map((c) => c.buoi)).size > 1;
  const ten = (c) => c.name || c.club_id;
  if (nhieuBuoi) {
    const nhom = new Map();
    ds.forEach((c) => {
      if (!nhom.has(c.buoi)) {
        const g = document.createElement("optgroup");
        g.label = nhanBuoi(c.buoi);
        sel.appendChild(g);
        nhom.set(c.buoi, g);
      }
      const o = document.createElement("option");
      o.value = c.club_id;
      o.textContent = ten(c);
      nhom.get(c.buoi).appendChild(o);
    });
  } else {
    ds.forEach((c) => themOption(sel, c.club_id, ten(c)));
  }
  const co = (v) => Array.from(sel.options).some((o) => o.value === v);
  if (!co(kq.clb)) kq.clb = sel.options.length ? sel.options[0].value : "";
  sel.value = kq.clb;
  sel.disabled = !ds.length;
}

function loadKetQuaTab() {
  Promise.all([callApi("get_trang_thai_ket_qua"), layDsLop(), callApi("get_club_fill_stats")])
    .then(([tt, dsLop, clbRes]) => {
      kq.coKq = !!(tt.ok && tt.data.co_ket_qua);
      el("kqCuBanner").hidden = !(tt.ok && tt.data.ket_qua_cu);
      const dsClb = clbRes.ok ? kqSapClb(clbRes.data) : [];
      kq.nLop = dsLop.classes.length;
      kq.nClb = dsClb.length;
      kq.dsClb = dsClb;
      kqNapOLop(dsLop);
      if (!kq.nLop && kq.tang1 === "lop") kq.tang1 = "ma";     // chưa có lớp: mở bảng có dữ liệu
      veKetQua();
    });
}

function veKetQua() {
  kqDongBoDieuKhien();
  kqNapOClb(kq.dsClb);       // rẻ: vài chục CLB
  el("kqRong").hidden = true;
  if (!kq.coKq) { kqBaoRong("the_xem_chua_co_ket_qua"); return Promise.resolve(); }
  if (kq.tang1 === "lop") return veKqTheoLop();
  if (kq.tang1 === "clb") return veKqTheoClb();
  return veKqTheoMa();
}

/* ---- Bảng ---- */

/* `soCotCoDinh` cột đầu (mã, họ tên, lớp nếu có) không xuống dòng: tên CLB dài chỉ được làm ô CLB
   xuống dòng. Tiêu đề cột là nút: bấm để sắp theo cột đó, bấm lần nữa để đảo chiều (T3-17).
   `cotLop` = chỉ số cột lớp trong `k` của hàng (-1 nếu bảng không có cột lớp). */
function kqVeBang(cot, hang, dem, soCotCoDinh, cotLop) {
  kq.bang = { cot, hang, dem, soCotCoDinh, cotLop };
  const dang = kq.sapCot === null || kq.sapCot >= cot.length ? 0 : kq.sapCot;
  el("kqDau").innerHTML = cot.map((c, i) => {
    const sapNay = i === dang;
    return `<th class="${i < soCotCoDinh ? "kq-cd" : "cot-buoi-tieu-de"}" aria-sort="${sapNay ? (kq.sapGiam ? "descending" : "ascending") : "none"}">`
      + `<button type="button" class="kq-sx-cot" data-cot="${i}" title="${esc(t("kq_sx_cot", { cot: c }))}">${esc(c)}`
      + `<span class="kq-sx-mui" aria-hidden="true">${sapNay ? (kq.sapGiam ? "▼" : "▲") : ""}</span></button></th>`;
  }).join("");
  const than = el("kqThan");
  clear(than);
  const manh = document.createDocumentFragment();
  kqSapHang(hang, dang, cotLop, kq.sapGiam).forEach((h) => {
    const tr = document.createElement("tr");
    if (h.chuaCo) tr.className = "dong-do";
    tr.innerHTML = `<td class="kq-cd">${esc(h.student_id)}</td><td class="kq-cd">${esc(h.name || "")}</td>` + h.o.join("");
    manh.appendChild(tr);
  });
  than.appendChild(manh);
  el("kqDem").textContent = dem;
  el("kqRong").hidden = true;
  el("kqBang").hidden = false;
}

/* Mã theo đúng thứ tự đang hiện trên màn hình (cùng cột/chiều sắp với kqVeBang): gửi cho tệp xuất (T3-L4). */
function kqThuTuMan() {
  const b = kq.bang;
  if (!b) return [];
  const dang = kq.sapCot === null || kq.sapCot >= b.cot.length ? 0 : kq.sapCot;
  return kqSapHang(b.hang, dang, b.cotLop, kq.sapGiam).map((h) => h.student_id);
}

/* Bấm tiêu đề cột: cột mới sắp tăng dần; cùng cột thì đảo chiều. Vẽ lại từ bảng đã có, không gọi API. */
function kqBamCot(i) {
  if (!kq.bang) return;
  const dang = kq.sapCot === null ? 0 : kq.sapCot;
  kq.sapGiam = i === dang ? !kq.sapGiam : false;
  kq.sapCot = i;
  const b = kq.bang;
  kqVeBang(b.cot, b.hang, b.dem, b.soCotCoDinh, b.cotLop);
}

/* Hàng thời khoá biểu của một em. `k` = giá trị từng cột (để sắp); `o` = ô HTML từ cột họ tên trở đi. */
function kqHangLich(em, dsBuoi, coLop) {
  const tenBuoi = dsBuoi.map((b) => {
    const x = em.theo_buoi[b];
    return x && x.club_id ? (x.club_name || x.club_id) : "";
  });
  const oBuoi = tenBuoi.map((ten) => (ten ? `<td>${esc(ten)}</td>` : `<td class="o-trong">-</td>`));
  return {
    student_id: em.student_id, name: em.name, class_id: em.class_id || "",
    chuaCo: !em.so_clb,
    k: [em.student_id, em.name || ""].concat(coLop ? [em.class_id || ""] : []).concat(tenBuoi),
    o: (coLop ? [`<td class="kq-cd">${esc(em.class_id || "")}</td>`] : []).concat(oBuoi),
  };
}

function kqCotLich(dsBuoi, coLop) {
  return [t("th_student_id"), t("th_name")]
    .concat(coLop ? [t("th_cohort")] : [])
    .concat(dsBuoi.length > 1 ? dsBuoi.map(nhanBuoi) : [t("th_club")]);
}

function veKqTheoLop() {
  if (!kq.nLop || kq.lop === null) { el("kqBang").hidden = true; return Promise.resolve(); }
  return callApiMoiNhat("kq", "get_thoi_khoa_bieu", "", kq.lop).then((res) => {
    if (!res.ok) { el("kqBang").hidden = true; showErrorToast(res.errors); return; }
    const dsBuoi = res.data.ds_buoi;
    const hang = res.data.hoc_sinh.map((e) => kqHangLich(e, dsBuoi, false));
    kqVeBang(kqCotLich(dsBuoi, false), hang,
      t(hang.length === 1 ? "theolop_dem" : "theolop_dem_nhieu", { n: hang.length, m: hang.filter((h) => h.chuaCo).length }), 2, -1);
  });
}

function veKqTheoClb() {
  if (!kq.nClb) { kqBaoRong("kq_khong_co_clb"); return Promise.resolve(); }
  return callApiMoiNhat("kq", "get_danh_sach_clb", kq.clb).then((res) => {
    if (!res.ok) { el("kqBang").hidden = true; showErrorToast(res.errors); return; }
    const d = res.data;
    const hang = d.thanh_vien.map((m) => ({
      student_id: m.student_id, name: m.name, class_id: m.class_id || "", chuaCo: false,
      k: [m.student_id, m.name || "", m.class_id || ""],
      o: [`<td class="kq-cd">${esc(m.class_id || "")}</td>`],
    }));
    if (!hang.length) { kqBaoRong("members_rong"); return; }
    kqVeBang([t("th_student_id"), t("th_name"), t("th_cohort")], hang,
      t("members_dem", { x: hang.length, y: d.capacity }), 3, 2);
  });
}

function veKqTheoMa() {
  const tim = (el("kqTimKiem").value || "").trim();
  return callApiMoiNhat("kq", "get_thoi_khoa_bieu", tim).then((res) => {
    if (!res.ok) { el("kqBang").hidden = true; showErrorToast(res.errors); return; }
    const dsBuoi = res.data.ds_buoi;
    const hang = res.data.hoc_sinh.map((e) => kqHangLich(e, dsBuoi, true));
    if (!hang.length) { kqBaoRong(tim ? "kq_tim_khong_thay" : "kq_khong_co_hs"); return; }
    kqVeBang(kqCotLich(dsBuoi, true), hang, t(hang.length === 1 ? "kq_dem_ma" : "kq_dem_ma_nhieu", { n: hang.length }), 3, 2);
  });
}

function initKetQuaHandlers() {
  docKqXem();
  document.querySelectorAll("#kqTang1 .kq-seg-nut").forEach((n) => {
    n.addEventListener("click", () => {
      kq.tang1 = n.dataset.kq; kq.sapCot = null; kq.sapGiam = false; luuKqXem(); veKetQua();
    });
  });
  el("kqDau").addEventListener("click", (ev) => {
    const nut = ev.target.closest(".kq-sx-cot");
    if (nut) kqBamCot(Number(nut.dataset.cot));
  });
  el("kqChonLop").addEventListener("change", (ev) => { kq.lop = ev.target.value; luuKqXem(); veKetQua(); });
  el("kqChonClb").addEventListener("change", (ev) => { kq.clb = ev.target.value; luuKqXem(); veKetQua(); });
  el("kqTimKiem").addEventListener("input", debounce(() => veKetQua(), 250));
  el("btnKqTaiBang").addEventListener("click", () => {
    const gia = kq.tang1 === "lop" ? kq.lop : kq.tang1 === "clb" ? kq.clb : (el("kqTimKiem").value || "").trim();
    chayXuat([["xuat_muc_bang_xem", "export_bang_dang_xem", [kq.tang1, gia, "", kqThuTuMan()],
      (d) => t("kq_tai_bang_xong", { n: d.n_dong, path: d.path })]], el("kqXuatPhanHoi"));
  });
  kqDongBoDieuKhien();
}
