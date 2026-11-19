# Fabricate: Data Science (Bagian Shava)

Saran tenggat dan pemantau pesanan untuk Ageng Konveksi (Ibu Dintje, Kediri). Tim A26-CS268.

**Hasil:** dari 24 nota asli, pesanan 15 pcs ke bawah selesai rata-rata **10 hari** (biasanya 9 sampai 11,5) dan pesanan di atas 15 pcs **13 hari** (biasanya 11 sampai 15).

## Isi folder

| File | Fungsi |
|---|---|
| `data/data_nota_ageng_konveksi_bersih.csv` | Dataset utama: 24 baris Asli (nota Ibu Dintje) + 284 Dummy (uji kode) |
| `data/kamus_data.csv` | Arti tiap kolom dan isi model |
| `data/` foto nota dan `.xlsx` | Bukti dan arsip nota asli (tidak dibaca kode) |
| `01_siapkan_data.py` | Ambil baris Asli, hitung `lama_hari` |
| `02_analisis_bisnis.py` | Jawab 4 pertanyaan bisnis, buat grafik |
| `03_fitur_dan_uji.py` | Siapkan fitur dan target model |
| `04_bandingkan_model.py` | Adu 4 model dengan Leave-One-Out CV |
| `05_simpan_model.py` | Simpan model terbaik |
| `06_dasbor.py` | Dasbor Streamlit |
| `hasil/` | Keluaran kode (terisi saat dijalankan) |

## Cara menjalankan

Di terminal VS Code (folder yang berisi `06_dasbor.py`). Windows pakai `py`; Mac/Linux `python3`.

```
py -m pip install -r requirements.txt
py 01_siapkan_data.py
py 02_analisis_bisnis.py
py 03_fitur_dan_uji.py
py 04_bandingkan_model.py
py 05_simpan_model.py
py -m streamlit run 06_dasbor.py
```

Jalankan berurutan; langkah 5 harus selesai sebelum dasbor. Berhenti dengan Ctrl+C.

## Hasil model

| Model | MAE (hari) |
|---|---|
| Median per ukuran pesanan (dipakai) | **1,81** |
| Median per produk | 1,98 |
| Random Forest | 2,16 |
| Regresi Linear | 2,52 |

MAE = rata-rata selisih tebakan dengan kenyataan. Diuji dengan Leave-One-Out: tiap nota diuji oleh model yang tidak melihatnya.

## Temuan utama

- Rata-rata lama pengerjaan sekitar 11,5 hari (median 11,5).
- Jersey tercepat (median 10 hari); Kaos dan Katun lebih lama (12 sampai 12,5).
- Pesanan di atas 15 pcs median 13 hari, pesanan 15 pcs ke bawah 10 hari. Pesanan besar sekitar 3 hari lebih lama.
- Jersey produk paling laku (berdasarkan nilai pesanan).
- 10 hari antrean padat (7 pesanan aktif atau lebih), terutama 10 sampai 18 Oktober.
- Saran tenggat: median pesanan seukuran (10 atau 13 hari).

## Yang dikerjakan (tugas Data Science)

**Analisis data**
- Merumuskan 4 pertanyaan bisnis: lama per produk, pengaruh jumlah, produk terlaris, hari antrean padat (`02_analisis_bisnis.py`).
- Menyiapkan dan membersihkan data nota, menghitung `lama_hari` (`01_`, `03_`).
- Menganalisis dan menyajikan temuan beserta saran tenggat (bagian Temuan, dasbor).
- Memeriksa data: cek data kosong, status nota, dan uji model.

**Dasbor pemantau bisnis**
- Dasbor Streamlit dengan indikator, grafik, antrean, dan saran tenggat (`06_dasbor.py`).
- Filter data dan unggah CSV untuk memperbarui data.
- Data asli diutamakan; data dummy diberi label dan hanya untuk uji.

**Penyediaan data untuk model AI**
- Transformasi dan feature engineering: kategori jadi 0/1, kelompok ukuran pesanan (`03_`, `04_`).
- Kamus data (`data/kamus_data.csv`).
- Pembagian data latih dan uji dengan Leave-One-Out, tanpa kebocoran data.

**Model prediksi**
- Membuat dan membandingkan 4 model, mengevaluasi pengaruh fitur, dan menjelaskan keterbatasannya (`04_`, `perbandingan_model.csv`).
- Menyimpan model terbaik untuk dipakai aplikasi (`05_`, `model_estimasi.joblib`).

**Diserahkan ke tim lain (dikerjakan bersama)**
- Integrasi dasbor dan prediksi ke aplikasi web: Tengku dan Caroline (Full-stack), memakai `06_dasbor.py` dan `model_estimasi.joblib`.
- Kesepakatan format data untuk model AI: Kesya dan Natasya (Gen AI), memakai `data_nota_ageng_konveksi_bersih.csv` dan `kamus_data.csv`.

## Untuk tim lain

| Untuk | Ambil |
|---|---|
| Tengku dan Caroline (Full-stack) | `06_dasbor.py`, `hasil/model_estimasi.joblib`, `requirements.txt` |
| Kesya dan Natasya (Gen AI) | `data/data_nota_ageng_konveksi_bersih.csv`, `data/kamus_data.csv`, `hasil/03_fitur_model.csv` |

Memakai model (cek `jenis` dulu, saat ini `median_ukuran`):

```python
import joblib
m = joblib.load("hasil/model_estimasi.joblib")

def estimasi(jumlah):
    kecil = jumlah <= m["batas"]
    hari = m["median_kecil"] if kecil else m["median_besar"]
    bawah, atas = m["kisaran_kecil"] if kecil else m["kisaran_besar"]
    return hari, bawah, atas
```

Tenggat = tanggal pesan + perkiraan hari.

## Aturan dan keterbatasan

- Hasil hanya dari data **Asli**. Dummy hanya untuk uji kode dan diberi label.
- Di dasbor, CSV yang diunggah muncul sebagai pilihan baru di "Jenis data".
- Nota asli baru 24, jadi estimasi per produk belum andal.
- Batas 15 pcs dipilih dari data yang sama; perlu dikonfirmasi dengan nota baru.

## Masalah umum

| Masalah | Solusi |
|---|---|
| `python` tidak dikenali | Pakai `py` |
| Dasbor minta `model_estimasi.joblib` | Jalankan langkah 5 |
| Library tidak ada | `py -m pip install -r requirements.txt` |
| Dasbor menampilkan 284 pesanan | Filter masih Dummy; klik Atur ulang |