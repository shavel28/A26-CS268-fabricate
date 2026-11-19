# 🧵 Fabricate: Smart Order and Digital Catalog for Ageng Konveksi

🎓 Tim A26-CS268 · Asah 2026

## 📌 Tentang Proyek

Fabricate adalah aplikasi web untuk UMKM **Ageng Konveksi** (Ibu Dintje, Kota Kediri).

**⚠️ Masalah yang dihadapi**
- Pesanan hanya diingat, sehingga jadwal sering terlambat atau berubah.
- Promosi hanya dari mulut ke mulut.

**✨ Gunanya Fabricate**
- Mencatat pesanan secara digital (tanggal, status, jumlah) supaya tidak ada yang terlewat.
- Memberi saran tenggat pesanan baru berdasarkan data pesanan sebelumnya.
- Menampilkan katalog produk secara digital untuk promosi.
- Menampilkan dasbor analitik: berapa lama pengerjaan tiap produk, produk terlaris, dan kapan pesanan menumpuk.

## 📁 Struktur Folder

```
fabricate/
├── README.md
├── data/            # data mentah dan hasil pemrosesan data
├── data_science/    # kode analisis, model, dasbor, beserta data yang dipakainya
├── ai/              # model AI, API, dan fitur draf caption promosi
└── web/
    ├── frontend/    # tampilan aplikasi
    └── backend/     # server dan basis data
```

| Folder | Isinya | Dikerjakan oleh |
|---|---|---|
| `data/` | Data mentah dan hasil pemrosesan data | Tim Data Science (Varel) |
| `data_science/` | Analisis, perbandingan model, dasbor Streamlit, dan data yang dipakainya (dataset bersih, foto nota, kamus data) | Tim Data Science (Shava) |
| `ai/` | Model yang dipakai aplikasi, API model, draf caption | Tim AI |
| `web/frontend/` | Halaman dan tampilan yang dilihat pengguna | Tim Full-Stack |
| `web/backend/` | Server, basis data, dan penghubung ke model | Tim Full-Stack |

## 👥 Tim dan Pembagian Tugas

> 📝 Tiap anggota mengisi bagian "Yang dikerjakan" sendiri.

---

### 📊 Tim Data Science
Menyiapkan data dan menggali informasi dari data pesanan: apa yang bisa dipelajari dan apa yang bisa diprediksi.

#### 👩‍💻 Shava: Analisis dan Pemodelan
Yang dikerjakan:
- Merumuskan pertanyaan bisnis dan menganalisis 24 nota asli: lama pengerjaan tiap produk, pengaruh jumlah pesanan, produk terlaris, dan hari antrean padat.
- Menemukan bahwa pesanan 15 pcs ke bawah rata-rata selesai dalam 10 hari dan pesanan di atas 15 pcs dalam 13 hari.
- Membandingkan 4 model dengan Leave-One-Out CV. Hasil terbaik: median per ukuran pesanan (MAE 1,81 hari), lalu median per produk (1,98), Random Forest (2,16), dan Regresi Linear (2,52).
- Membuat model saran tenggat (`model_estimasi.joblib`) yang diserahkan ke tim Full-Stack untuk dipasang di aplikasi.
- Membuat dasbor Streamlit: indikator, grafik, antrean, saran tenggat, filter, dan unggah CSV.
- Menyusun kamus data dan panduan menjalankan kode (`data_science/README.md`).
- Data asli diutamakan; data dummy hanya untuk uji kode dan selalu diberi label.
- Keterbatasan: nota asli baru 24, sehingga hasil perlu dikonfirmasi dengan nota baru.

#### 🧑‍💻 Varel: Pemrosesan Data
Yang dikerjakan:
-

---

### 🤖 Tim AI (Next-Gen AI)
Membuat model dan fitur kecerdasan buatan yang dipakai di aplikasi.

#### 👩‍💻 Kesya: Next-Gen AI
Yang dikerjakan:
-

#### 👩‍💻 Natasya: Next-Gen AI
Yang dikerjakan:
-

---

### 💻 Tim Full-Stack
Membuat aplikasi web yang dipakai Ibu Dintje, dari tampilan sampai server.

#### 🧑‍💻 Tengku: Full-Stack
Yang dikerjakan:
-

#### 👩‍💻 Caroline: Full-Stack
Yang dikerjakan:
-
