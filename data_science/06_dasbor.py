"""
Dasbor Fabricate - Ageng Konveksi (bagian Shava)
Jalankan:  py -m streamlit run 06_dasbor.py
Data bawaan: data/data_nota_ageng_konveksi_bersih.csv. Data baru diunggah di tab "Data".
"""
from datetime import date, timedelta
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Fabricate - Dasbor Ageng Konveksi", layout="wide", initial_sidebar_state="collapsed")

FILE_BAWAAN = Path("data/data_nota_ageng_konveksi_bersih.csv")
FILE_MODEL = Path("hasil/model_estimasi.joblib")
BATAS_KECIL = 15  # pesanan 15 pcs ke bawah dianggap kecil

# Hanya dua warna: biru untuk data, oranye khusus untuk tanda "padat". Biru muda = data masih sedikit.
BIRU, BIRU_MUDA, ORANYE = "#2a78d6", "#9ec5f4", "#eb6834"
BULAN = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
FILTER_KEYS = ["f_jenis", "f_produk", "f_status", "f_tgl"]

# Penjelasan format file CSV (dipakai di tab Data)
FORMAT_CSV = pd.DataFrame([
    ["kategori", "Wajib", "Nama produk", "Jersey"],
    ["jumlah", "Wajib", "Banyaknya pcs, angka saja", "42"],
    ["harga_satuan", "Wajib", "Harga per pcs dalam rupiah, angka saja (tanpa Rp dan titik)", "75000"],
    ["tanggal_pesan", "Wajib", "Tanggal pelanggan memesan, format TAHUN-BULAN-TANGGAL", "2026-08-18"],
    ["tanggal_selesai", "Wajib", "Tanggal pesanan selesai. Kosongkan jika belum selesai", "2026-09-02"],
    ["status", "Wajib", "Tulis Selesai atau Proses", "Selesai"],
    ["total_harga", "Boleh kosong", "Jumlah x harga satuan. Dihitung otomatis jika tidak ada", "3150000"],
    ["sumber_data", "Boleh kosong", "Asli (dari nota) atau Dummy (data uji)", "Asli"],
], columns=["Nama kolom", "Wajib?", "Isinya", "Contoh"])
KOLOM_WAJIB = list(FORMAT_CSV.loc[FORMAT_CSV["Wajib?"] == "Wajib", "Nama kolom"])
CONTOH_CSV = (
    "kategori,jumlah,harga_satuan,tanggal_pesan,tanggal_selesai,status,total_harga,sumber_data\n"
    "Jersey,11,85000,2026-08-25,2026-09-05,Selesai,935000,Asli\n"
    "Kaos,20,75000,2026-08-20,2026-09-03,Selesai,1500000,Asli\n"
    "Kaos,15,40000,2026-10-10,,Proses,600000,Asli\n")


def tgl_id(d):
    return f"{d.day} {BULAN[d.month - 1]} {d.year}"


def koma(x, desimal=1):
    return f"{x:.{desimal}f}".replace(".", ",")


def hari_str(x):
    return koma(x, 0 if float(x).is_integer() else 1) + " hari"


def rupiah(x):
    return "Rp " + f"{x:,.0f}".replace(",", ".")


def rupiah_singkat(x):
    return f"Rp {koma(x / 1e6)} jt" if x >= 1e6 else rupiah(x)


def rapikan(fig, tinggi=340):
    fig.update_layout(height=tinggi, margin=dict(l=10, r=20, t=24, b=10), showlegend=False,
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(family="Inter, Segoe UI, sans-serif", size=15), title=dict(text=""))
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor="rgba(128,128,128,0.4)")
    fig.update_yaxes(gridcolor="rgba(128,128,128,0.18)", zeroline=False, showline=False)
    return fig


def reset_filter():
    for k in FILTER_KEYS:
        st.session_state.pop(k, None)


def bersihkan(key, opsi, awal=None):
    """Isi pilihan awal, dan buang pilihan lama yang sudah tidak ada di opsi (misal setelah ganti data)."""
    awal = list(opsi) if awal is None else awal
    if key not in st.session_state:
        st.session_state[key] = awal
    else:
        st.session_state[key] = [x for x in st.session_state[key] if x in opsi]


@st.cache_data
def baca_csv(sumber):
    d = pd.read_csv(sumber)
    for k in ("tanggal_pesan", "tanggal_selesai"):
        if k in d.columns:
            d[k] = pd.to_datetime(d[k], errors="coerce")  # teks yang bukan tanggal menjadi kosong
    return d


def siapkan(d):
    d = d.copy()
    if "total_harga" not in d:
        d["total_harga"] = np.nan
    d["total_harga"] = d["total_harga"].fillna(d["jumlah"] * d["harga_satuan"])
    d["lama_hari"] = (d["tanggal_selesai"] - d["tanggal_pesan"]).dt.days
    return d


def muat_data(berkas):
    """Kembalikan (data, pesan). Data bawaan selalu ada; file unggahan ditambahkan sebagai jenis data "Unggahan: nama_file"."""
    bawaan = siapkan(baca_csv(FILE_BAWAAN))
    if berkas is None:
        return bawaan, None
    try:
        baru = baca_csv(berkas)
        kurang = [k for k in KOLOM_WAJIB if k not in baru.columns]
        if kurang:
            return bawaan, ("error", "Kolom belum lengkap: " + ", ".join(kurang) + ". File tidak dipakai.")
        if baru["tanggal_pesan"].isna().any():
            baris = int(baru["tanggal_pesan"].isna().idxmax()) + 2
            return bawaan, ("error", f"Ada tanggal_pesan yang tidak terbaca (misalnya di baris {baris} file). Tulis seperti 2026-09-02. File tidak dipakai.")
        for k in ("jumlah", "harga_satuan"):
            if pd.to_numeric(baru[k], errors="coerce").isna().any():
                return bawaan, ("error", f"Kolom {k} harus berisi angka saja (tanpa Rp atau titik). File tidak dipakai.")
        baru = siapkan(baru)
        baru["sumber_data"] = f"Unggahan: {berkas.name}"
        return pd.concat([bawaan, baru], ignore_index=True), ("ok", f"Berhasil memuat {len(baru)} baris. Di kotak Jenis data (atas halaman) sekarang ada pilihan \"Unggahan: {berkas.name}\".")
    except Exception:
        return bawaan, ("error", "File tidak bisa dibaca. Pastikan formatnya CSV dan sesuai petunjuk di bawah. File tidak dipakai.")


# =====================================================  DATA  =====================================================
berkas = st.session_state.get("unggah")
semua, pesan_data = muat_data(berkas)

# Kalau data diganti (unggah atau hapus file), pilihan filter lama dikosongkan supaya tidak ada yang nyangkut.
tanda = (berkas.name, berkas.size) if berkas is not None else None
if st.session_state.get("_tanda_data", "belum") != tanda:
    if "_tanda_data" in st.session_state:
        reset_filter()
    st.session_state["_tanda_data"] = tanda

st.title("Fabricate: Dasbor Ageng Konveksi")
st.caption("Memantau pesanan, lama pengerjaan, dan antrean, serta memberi saran tenggat untuk pesanan baru.")

# =====================================================  FILTER (di atas halaman)  =====================================================
with st.container(border=True):
    baris1 = st.columns([1.2, 2.4, 1.6])
    baris2 = st.columns([1.6, 1.2, 1.2], vertical_alignment="bottom")
    if "sumber_data" in semua.columns:
        opsi_jenis = sorted(semua["sumber_data"].dropna().unique())
        unggahan = [x for x in opsi_jenis if str(x).startswith("Unggahan")]
        bersihkan("f_jenis", opsi_jenis, unggahan or [x for x in ["Asli"] if x in opsi_jenis] or opsi_jenis)
        jenis = baris1[0].multiselect("Jenis data", opsi_jenis, key="f_jenis",
                                      help="Asli = dari nota Ibu Dintje. Dummy = data buatan untuk uji tampilan. Unggahan = file CSV yang kamu unggah.")
        data = semua[semua["sumber_data"].isin(jenis)]
    else:
        baris1[0].markdown("**Jenis data**  \nSemua")
        jenis, data = [], semua
    if data.empty:
        st.warning("Belum ada jenis data yang dipilih. Pilih minimal satu jenis data di kotak \"Jenis data\", atau tekan Atur ulang.")
        st.stop()
    opsi_produk = sorted(data["kategori"].unique())
    bersihkan("f_produk", opsi_produk)
    produk = baris1[1].multiselect("Produk", opsi_produk, key="f_produk")
    opsi_status = sorted(data["status"].unique())
    bersihkan("f_status", opsi_status)
    status = baris1[2].multiselect("Status pesanan", opsi_status, key="f_status")
    tmin, tmax = data["tanggal_pesan"].min().date(), data["tanggal_pesan"].max().date()
    rentang = baris2[0].date_input("Tanggal pesan", (tmin, tmax), key="f_tgl")
    baris2[1].button("Atur ulang", on_click=reset_filter, width="stretch")
    if "Dummy" in jenis:
        st.warning("Data dummy ikut dipilih. Angka yang tampil bukan hasil sebenarnya.")

f = data[data["kategori"].isin(produk) & data["status"].isin(status)]
if isinstance(rentang, tuple) and len(rentang) == 2:
    f = f[(f["tanggal_pesan"].dt.date >= rentang[0]) & (f["tanggal_pesan"].dt.date <= rentang[1])]
if f.empty:
    st.warning("Tidak ada pesanan yang cocok dengan filter. Klik **Atur ulang**.")
    st.stop()
st.caption(f"Menampilkan {len(f)} pesanan, dipesan {tgl_id(f['tanggal_pesan'].min())} sampai {tgl_id(f['tanggal_pesan'].max())}.")

selesai = f[f["status"] == "Selesai"].dropna(subset=["lama_hari"])
# pesanan yang belum selesai dianggap masih dikerjakan sampai tanggal terakhir yang tercatat
tanggal_terakhir = pd.concat([f["tanggal_pesan"], f["tanggal_selesai"].dropna()]).max()
akhir = f["tanggal_selesai"].fillna(tanggal_terakhir)
hari = pd.date_range(f["tanggal_pesan"].min(), akhir.max())
aktif = pd.Series({h: int(((f["tanggal_pesan"] <= h) & (akhir >= h)).sum()) for h in hari})
ambang = int(np.ceil(aktif.mean() + aktif.std())) if len(aktif) > 1 else 1

k1, k2, k3, k4 = st.columns(4)
k1.metric("Jumlah pesanan", len(f), border=True)
k2.metric("Total nilai pesanan", rupiah_singkat(f["total_harga"].sum()), border=True)
k3.metric("Lama pengerjaan (median)", hari_str(selesai["lama_hari"].median()) if len(selesai) else "-", border=True,
          help="Nilai tengah. Separuh pesanan selesai lebih cepat, separuh lebih lama.")
k4.metric("Hari antrean padat", int((aktif >= ambang).sum()), border=True, help=f"Hari dengan {ambang} pesanan aktif atau lebih.")

tab1, tab2, tab3, tab4 = st.tabs(["Ringkasan", "Antrean", "Saran tenggat", "Data dan unggah"])

# =====================================================  TAB 1: RINGKASAN  =====================================================
with tab1:
    if len(selesai):
        g = selesai.groupby("kategori")["lama_hari"].agg(median="median", cepat="min", lama="max", n="count").sort_values("median")
        kalimat = f"**{g.index[0]}** paling cepat dikerjakan ({hari_str(g.iloc[0]['median'])})"
        if len(g) > 1:
            kalimat += f", **{g.index[-1]}** paling lama ({hari_str(g.iloc[-1]['median'])})"
        st.info(kalimat + ".")

    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.subheader("Berapa lama tiap produk dikerjakan?")
            if len(selesai):
                fig = go.Figure(go.Bar(
                    x=[f"{p}<br>({n} nota)" for p, n in zip(g.index, g["n"])], y=g["median"],
                    marker_color=[BIRU_MUDA if n < 3 else BIRU for n in g["n"]],
                    text=[hari_str(m) for m in g["median"]], textposition="outside", cliponaxis=False,
                    customdata=np.stack([g["cepat"], g["lama"]], axis=-1),
                    hovertemplate="<b>%{x}</b><br>Median %{y} hari<br>Tercepat %{customdata[0]}, terlama %{customdata[1]} hari<extra></extra>"))
                fig.update_yaxes(title="Hari", range=[0, g["median"].max() * 1.25])
                fig.update_xaxes(automargin=True)
                st.plotly_chart(rapikan(fig), width="stretch")
                st.caption("Tinggi batang = lama pengerjaan tengah (median). Warna muda = baru 1 sampai 2 nota, belum bisa dipegang kuat.")
            else:
                st.info("Belum ada pesanan selesai pada filter ini.")
    with c2:
        with st.container(border=True):
            st.subheader("Produk apa yang paling laku?")
            lr = (f.groupby("kategori").agg(nilai=("total_harga", "sum"), pcs=("jumlah", "sum"), nota=("kategori", "size"))
                  .sort_values("nilai", ascending=False))
            fig = go.Figure(go.Bar(
                x=[f"{p}<br>({n} nota)" for p, n in zip(lr.index, lr["nota"])], y=lr["nilai"] / 1e6, marker_color=BIRU,
                text=[rupiah_singkat(v) for v in lr["nilai"]], textposition="outside", cliponaxis=False,
                customdata=lr["pcs"], hovertemplate="<b>%{x}</b><br>Nilai: Rp %{y:.1f} juta<br>%{customdata} pcs<extra></extra>"))
            fig.update_yaxes(title="Nilai penjualan (juta Rp)", range=[0, lr["nilai"].max() / 1e6 * 1.2])
            fig.update_xaxes(automargin=True)
            st.plotly_chart(rapikan(fig), width="stretch")
            st.caption("Diurutkan dari nilai penjualan terbesar (jumlah x harga satuan).")

    with st.container(border=True):
        st.subheader("Apakah pesanan yang lebih banyak dikerjakan lebih lama?")
        kecil, besar = selesai[selesai["jumlah"] <= BATAS_KECIL], selesai[selesai["jumlah"] > BATAS_KECIL]
        grup = [(f"{BATAS_KECIL} pcs ke bawah<br>({len(kecil)} nota)", kecil), (f"Di atas {BATAS_KECIL} pcs<br>({len(besar)} nota)", besar)]
        grup = [(n, d) for n, d in grup if len(d)]
        if len(selesai) > 3 and len(grup) == 2:
            fig = go.Figure(go.Bar(
                x=[n for n, _ in grup], y=[d["lama_hari"].median() for _, d in grup], marker_color=BIRU, width=0.4,
                text=[hari_str(d["lama_hari"].median()) for _, d in grup], textposition="outside", cliponaxis=False,
                hovertemplate="%{x}<br>Median %{y} hari<extra></extra>"))
            fig.update_yaxes(title="Hari", range=[0, max(d["lama_hari"].median() for _, d in grup) * 1.25])
            fig.update_xaxes(automargin=True)
            col_a, col_b = st.columns([3, 2])
            with col_a:
                st.plotly_chart(rapikan(fig, 320), width="stretch")
            with col_b:
                korel = selesai[["jumlah", "lama_hari"]].corr().iloc[0, 1]
                med_k, med_b = grup[0][1]["lama_hari"].median(), grup[1][1]["lama_hari"].median()
                selisih = med_b - med_k
                st.markdown("**Artinya**")
                if selisih >= 1:
                    st.write(f"Pesanan {BATAS_KECIL} pcs ke bawah rata-rata selesai dalam **{hari_str(med_k)}**, "
                             f"sedangkan pesanan di atas {BATAS_KECIL} pcs **{hari_str(med_b)}**. "
                             f"Jadi pesanan besar sekitar **{hari_str(selisih)} lebih lama**.")
                else:
                    st.write("Pesanan kecil dan besar selesai dalam waktu yang hampir sama.")
                st.caption("Ini kecenderungan, bukan aturan pasti: ada pesanan besar yang selesai cepat dan pesanan kecil yang lama. "
                           f"(Kekuatan hubungannya {koma(korel, 2)} dari skala 0 sampai 1, tergolong " + ("lemah." if korel < 0.5 else "cukup kuat.") + ")")
        else:
            st.info("Perbandingan ini butuh pesanan selesai yang kecil maupun besar.")

# =====================================================  TAB 2: ANTREAN  =====================================================
with tab2:
    with st.container(border=True):
        st.subheader("Pesanan yang sedang dikerjakan tiap hari")
        padat = aktif[aktif >= ambang]
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=aktif.index, y=aktif.values, mode="lines", line=dict(color=BIRU, width=2.4),
                                 customdata=[tgl_id(d) for d in aktif.index],
                                 hovertemplate="%{customdata}<br>%{y} pesanan aktif<extra></extra>"))
        fig.add_trace(go.Scatter(x=padat.index, y=padat.values, mode="markers", marker=dict(size=8, color=ORANYE),
                                 customdata=[tgl_id(d) for d in padat.index],
                                 hovertemplate="%{customdata}<br>%{y} pesanan aktif (padat)<extra></extra>"))
        fig.add_hline(y=ambang, line_dash="dash", line_color="rgba(128,128,128,0.7)", line_width=1.5)
        langkah = max(len(aktif) // 8, 1)
        fig.update_xaxes(tickvals=list(aktif.index[::langkah]), ticktext=[f"{d.day} {BULAN[d.month - 1]}" for d in aktif.index[::langkah]])
        fig.update_yaxes(title="Jumlah pesanan", dtick=1 if aktif.max() <= 12 else None, range=[0, aktif.max() + 1])
        st.plotly_chart(rapikan(fig, 380), width="stretch")
        st.caption(f"Garis putus-putus = batas padat ({ambang} pesanan). Titik oranye = hari padat, saat pesanan yang sedang dikerjakan mencapai batas itu atau lebih.")

    periode, mulai, akh = [], None, None
    for h, v in aktif.items():
        if v >= ambang:
            mulai = mulai or h
            akh = h
        elif mulai is not None:
            periode.append((mulai, akh)); mulai = None
    if mulai is not None:
        periode.append((mulai, akh))
    with st.container(border=True):
        st.subheader("Periode antrean padat")
        if periode:
            tabel = pd.DataFrame({"Mulai": [tgl_id(a) for a, _ in periode], "Sampai": [tgl_id(b) for _, b in periode],
                                  "Lama (hari)": [(b - a).days + 1 for a, b in periode]})
            st.table(tabel.set_index("Mulai"))
            st.caption("Pada periode ini, hindari menerima pesanan besar atau beri tenggat lebih longgar.")
        else:
            st.success("Tidak ada hari antrean padat pada filter ini.")

# =====================================================  TAB 3: SARAN TENGGAT  =====================================================
with tab3:
    with st.container(border=True):
        st.subheader("Saran tenggat untuk pesanan baru")
        st.caption("Isi tiga kolom di bawah ini, hasilnya langsung muncul.")
        if FILE_MODEL.exists():
            m = joblib.load(FILE_MODEL)
            a, b, c = st.columns(3)
            pilih = a.selectbox("Produk", sorted(data["kategori"].unique()))
            jml = b.number_input("Jumlah (pcs)", min_value=1, value=10, step=1)
            tgl = c.date_input("Tanggal pesan", date.today(), key="tgl_pesan_baru")
            kisaran = None
            if m["jenis"] == "median_ukuran":
                kecil_ = jml <= m["batas"]
                est = m["median_kecil"] if kecil_ else m["median_besar"]
                kisaran = m["kisaran_kecil"] if kecil_ else m["kisaran_besar"]
            elif m["jenis"] == "median":
                est = m["median_per_produk"].get(pilih, m["median_global"])
            else:
                est = float(m["model"].predict(pd.DataFrame({"kategori": [pilih], "jumlah": [jml]}))[0])
            x1, x2, x3 = st.columns(3)
            x1.metric(f"Perkiraan untuk {int(jml)} pcs", hari_str(est), border=True)
            x2.metric("Biasanya antara", (f"{koma(kisaran[0], 0 if float(kisaran[0]).is_integer() else 1)}-{hari_str(kisaran[1])}" if kisaran else "-"), border=True,
                      help="Separuh pesanan seukuran ini selesai di dalam kisaran ini.")
            x3.metric("Tenggat yang disarankan", tgl_id(tgl + timedelta(days=round(est))), border=True)

            dasar = data[data["status"] == "Selesai"].dropna(subset=["lama_hari"])
            per_produk = dasar[dasar["kategori"] == pilih]["lama_hari"]
            if len(per_produk) >= 3:
                st.info(f"**Pembanding menurut produk:** {pilih} biasanya {hari_str(per_produk.median())} (dari {len(per_produk)} pesanan, semua ukuran).")
            st.caption("Perkiraan memakai median lama pengerjaan pesanan seukuran (15 pcs ke bawah atau di atas 15 pcs). "
                       "Rata-rata tebakan meleset sekitar 2 hari. Ini patokan awal dan bisa diubah Ibu Dintje.")
            kecil_sekali = dasar[dasar["jumlah"] <= 5].sort_values("jumlah")
            if jml <= 5 and len(kecil_sekali):
                daftar = ", ".join(f"{int(a)} pcs: {int(b)} hari" for a, b in zip(kecil_sekali["jumlah"], kecil_sekali["lama_hari"]))
                st.warning(f"Pesanan sekecil ini sangat jarang di data ({len(kecil_sekali)} nota: {daftar}). "
                           "Di data, pesanan kecil pun belum tentu cepat. Tanyakan ke Ibu Dintje apakah ada waktu tunggu tetap, lalu sesuaikan tenggatnya.")
            if pilih not in set(dasar["kategori"]):
                st.warning("Produk ini belum punya data pesanan selesai, jadi perkiraan kurang andal. Isi tenggat manual.")
        else:
            st.info("Model belum dibuat. Jalankan 05_simpan_model.py terlebih dahulu.")

# =====================================================  TAB 4: DATA DAN UNGGAH  =====================================================
with tab4:
    with st.container(border=True):
        st.subheader("Ganti atau tambah data")
        st.write("Data bawaan (nota Ageng Konveksi) selalu ada. File CSV yang diunggah di sini ditambahkan sebagai pilihan baru di kotak Jenis data.")
        st.file_uploader("Pilih file CSV", type="csv", key="unggah")
        if pesan_data:
            (st.success if pesan_data[0] == "ok" else st.error)(pesan_data[1])
        st.caption("Untuk kembali ke data bawaan, klik tanda x di sebelah nama file.")

    with st.container(border=True):
        st.subheader("Format file CSV")
        st.write("Siapkan file dengan baris pertama berisi nama kolom persis seperti di bawah, lalu satu baris untuk satu pesanan.")
        st.table(FORMAT_CSV.set_index("Nama kolom"))
        st.markdown(
            "- Simpan dari Excel lewat **Save As, CSV (Comma delimited)**.\n"
            "- Tanggal ditulis **2026-09-02** (tahun-bulan-tanggal).\n"
            "- Angka ditulis polos: **75000**, bukan Rp 75.000.\n"
            "- Pesanan yang belum selesai: kosongkan `tanggal_selesai` dan tulis status **Proses**.")
        st.download_button("Unduh contoh file CSV", CONTOH_CSV.encode("utf-8"), "contoh_format_pesanan.csv", "text/csv")

    with st.container(border=True):
        st.subheader("Data yang ditampilkan")
        tampil = f[[c for c in ["kategori", "jumlah", "harga_satuan", "total_harga", "tanggal_pesan", "tanggal_selesai", "status", "lama_hari"] if c in f.columns]].copy()
        tampil.columns = [c.replace("_", " ").capitalize() for c in tampil.columns]
        st.dataframe(tampil, hide_index=True, width="stretch",
                     column_config={"Tanggal pesan": st.column_config.DateColumn(format="DD-MM-YYYY"),
                                    "Tanggal selesai": st.column_config.DateColumn(format="DD-MM-YYYY")})
        st.download_button("Unduh data ini (CSV)", f.to_csv(index=False).encode("utf-8"), "data_terfilter.csv", "text/csv")
