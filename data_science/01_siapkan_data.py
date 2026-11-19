"""
LANGKAH 1 - Memuat dan memeriksa data
Tujuan : membaca nota, memilih yang asli, menghitung lama pengerjaan.
Input  : data/data_nota_ageng_konveksi_bersih.csv
Output : hasil/01_nota_asli.csv
"""
import pandas as pd

# 1. Baca file. parse_dates mengubah teks tanggal menjadi tanggal sungguhan
d = pd.read_csv("data/data_nota_ageng_konveksi_bersih.csv",
                parse_dates=["tanggal_pesan", "tanggal_selesai"])
print("Jumlah baris di file :", len(d))
print("Per sumber data      :\n", d["sumber_data"].value_counts(), "\n")

# 2. Ambil hanya nota ASLI. Dummy tidak dipakai untuk hasil proyek.
nota = d[d["sumber_data"] == "Asli"].copy()

# 3. Hitung lama pengerjaan (target yang mau diprediksi) = tanggal selesai - tanggal pesan
nota["lama_hari"] = (nota["tanggal_selesai"] - nota["tanggal_pesan"]).dt.days

# 4. Pemeriksaan sederhana: ada yang kosong? lama pengerjaan masuk akal?
print("Data kosong per kolom:\n", nota.isna().sum()[nota.isna().sum() > 0], "(kosong = tidak ada masalah)\n")
print("Ringkasan lama_hari  :\n", nota["lama_hari"].describe().round(1), "\n")
print("5 baris pertama      :\n", nota[["kategori", "jumlah", "tanggal_pesan", "tanggal_selesai", "lama_hari"]].head())

# 5. Simpan untuk langkah berikutnya
nota.to_csv("hasil/01_nota_asli.csv", index=False)
print("\nTersimpan: hasil/01_nota_asli.csv (", len(nota), "nota asli )")
