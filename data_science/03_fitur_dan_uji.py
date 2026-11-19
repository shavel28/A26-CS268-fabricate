"""
LANGKAH 3 - Feature engineering dan cara menguji
Tujuan : mengubah data jadi angka yang bisa dibaca model, dan memahami cara menguji (Leave-One-Out).
Input  : hasil/01_nota_asli.csv
Output : hasil/03_fitur_model.csv (hanya untuk dilihat)
"""
import pandas as pd
from sklearn.model_selection import LeaveOneOut

nota = pd.read_csv("hasil/01_nota_asli.csv")

# FITUR (bahan tebakan) dan TARGET (yang ditebak)
fitur = nota[["kategori", "jumlah"]]
target = nota["lama_hari"]
print("Fitur: kategori (teks) dan jumlah (angka). Target: lama_hari.\n")

# Model hanya mengerti angka. Kategori diubah jadi kolom 0/1 (one-hot encoding).
x = pd.get_dummies(fitur, columns=["kategori"], dtype=int)
print("Setelah one-hot encoding:\n", x.head(), "\n")
pd.concat([x, target], axis=1).to_csv("hasil/03_fitur_model.csv", index=False)

# CARA MENGUJI: Leave-One-Out
# Data cuma 24 nota, jadi tidak cukup dibagi 80/20. Tiap nota bergantian jadi data uji,
# sisanya (23 nota) jadi data latih. Diulang 24 kali.
loo = LeaveOneOut()
print("Jumlah putaran uji :", loo.get_n_splits(nota))
latih, uji = next(iter(loo.split(nota)))
print("Putaran 1          : latih =", len(latih), "nota, uji = nota nomor", int(nota.iloc[uji[0]]["no"]))
