"""
LANGKAH 2 - Menjawab pertanyaan bisnis
Input  : hasil/01_nota_asli.csv
Output : hasil/p1_..., p1b_..., p2_..., p3_... (.csv) dan hasil/grafik_analisis.png
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

nota = pd.read_csv("hasil/01_nota_asli.csv", parse_dates=["tanggal_pesan", "tanggal_selesai"])

# PERTANYAAN 1: berapa lama tiap produk dikerjakan?
p1 = nota.groupby("kategori")["lama_hari"].agg(jumlah_pesanan="count", median="median",
                                              rata_rata="mean", min="min", maks="max").round(1)
print("P1 Lama pengerjaan per produk:\n", p1, "\n")
p1.to_csv("hasil/p1_lama_pengerjaan_per_produk.csv")

# PERTANYAAN 1b: apakah jumlah pcs mempengaruhi lama pengerjaan?
nota["kelompok_jumlah"] = np.where(nota["jumlah"] <= 15, "<= 15 pcs", "> 15 pcs")
p1b = nota.groupby("kelompok_jumlah")["lama_hari"].agg(["count", "median"])
korelasi = nota[["jumlah", "lama_hari"]].corr().iloc[0, 1]   # -1 .. 1, makin dekat 0 makin lemah
print("P1b Jumlah vs lama:\n", p1b, "\nKorelasi:", round(korelasi, 2), "(0,35 = hubungan lemah)\n")
p1b.to_csv("hasil/p1b_lama_per_kelompok_jumlah.csv")

# PERTANYAAN 2: produk apa yang paling laku?
p2 = (nota.assign(nilai=nota["jumlah"] * nota["harga_satuan"])
          .groupby("kategori").agg(jumlah_nota=("no", "count"), total_pcs=("jumlah", "sum"), nilai=("nilai", "sum"))
          .sort_values("jumlah_nota", ascending=False))
print("P2 Produk terlaris:\n", p2, "\n")
p2.to_csv("hasil/p2_produk_terlaris.csv")

# PERTANYAAN 3: kapan pesanan menumpuk? (pesanan 'aktif' = sudah dipesan tapi belum selesai)
hari = pd.date_range(nota["tanggal_pesan"].min(), nota["tanggal_selesai"].max())
aktif = pd.Series({h: int(((nota["tanggal_pesan"] <= h) & (nota["tanggal_selesai"] >= h)).sum()) for h in hari})
ambang = int(np.ceil(aktif.mean() + aktif.std()))     # padat = di atas rata-rata + 1 simpangan baku
print("P3 Pesanan aktif rata-rata:", round(aktif.mean(), 1), "| ambang padat:", ambang,
      "| hari padat:", int((aktif >= ambang).sum()), "\n")
aktif.rename("pesanan_aktif").to_csv("hasil/p3_pesanan_aktif_per_hari.csv")

# GRAFIK
fig, ax = plt.subplots(1, 3, figsize=(16, 4.5))
nota.boxplot(column="lama_hari", by="kategori", ax=ax[0]); ax[0].set_title("Lama pengerjaan per produk (hari)")
ax[1].scatter(nota["jumlah"], nota["lama_hari"]); ax[1].set_title("Jumlah pcs vs lama pengerjaan")
aktif.plot(ax=ax[2]); ax[2].axhline(ambang, color="red", ls="--"); ax[2].set_title("Pesanan aktif per hari")
plt.suptitle(""); plt.tight_layout(); plt.savefig("hasil/grafik_analisis.png", dpi=130)
print("Tersimpan: 4 tabel CSV + hasil/grafik_analisis.png")
