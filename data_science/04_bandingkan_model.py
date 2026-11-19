"""
LANGKAH 4 - Membandingkan model
Tujuan : mencari tahu cara menebak lama pengerjaan yang paling akurat.
Input  : hasil/01_nota_asli.csv
Output : hasil/perbandingan_model.csv
"""
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import LeaveOneOut
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

nota = pd.read_csv("hasil/01_nota_asli.csv")
X, y = nota[["kategori", "jumlah"]], nota["lama_hari"]


def buat_model(estimator):
    """Pipeline = ubah kategori jadi 0/1, lalu pakai model."""
    pre = ColumnTransformer([("kat", OneHotEncoder(handle_unknown="ignore"), ["kategori"])],
                            remainder="passthrough")        # kolom jumlah dibawa apa adanya
    return Pipeline([("pre", pre), ("model", estimator)])


BATAS_KECIL = 15  # pesanan 15 pcs ke bawah = kecil, di atasnya = besar
tebakan = {"Baseline median": [], "Median per ukuran pesanan": [], "Regresi Linear": [], "Random Forest": []}
for latih, uji in LeaveOneOut().split(X):
    # Model 1: baseline = median lama pengerjaan produk yang sama di data latih
    med = y.iloc[latih].groupby(X.iloc[latih]["kategori"]).median()
    k = X.iloc[uji[0]]["kategori"]
    tebakan["Baseline median"].append(med.get(k, y.iloc[latih].median()))
    # Model 1b: median lama pengerjaan pesanan seukuran (15 pcs ke bawah atau di atas 15 pcs)
    kecil_latih = X.iloc[latih]["jumlah"].values <= BATAS_KECIL
    seukuran = y.iloc[latih][kecil_latih == (X.iloc[uji[0]]["jumlah"] <= BATAS_KECIL)]
    tebakan["Median per ukuran pesanan"].append(seukuran.median() if len(seukuran) else y.iloc[latih].median())
    # Model 2 dan 3: dilatih di data latih, menebak satu nota uji
    for nama, est in [("Regresi Linear", LinearRegression()),
                      ("Random Forest", RandomForestRegressor(n_estimators=200, min_samples_leaf=2, random_state=42))]:
        m = buat_model(est).fit(X.iloc[latih], y.iloc[latih])
        tebakan[nama].append(m.predict(X.iloc[uji])[0])

# Catatan: batas 15 pcs dipilih dari pengamatan di langkah 2 pada data yang sama, jadi keunggulannya perlu dikonfirmasi dengan data baru.
# MAE = rata-rata selisih tebakan dengan kenyataan (hari). Makin kecil makin baik.
hasil = pd.DataFrame([{"model": n, "MAE_hari": round(mean_absolute_error(y, p), 2), "n_uji": len(y)}
                      for n, p in tebakan.items()])
print(hasil.to_string(index=False))
print("\nModel terbaik:", hasil.sort_values("MAE_hari").iloc[0]["model"])
hasil.to_csv("hasil/perbandingan_model.csv", index=False)
print("Tersimpan: hasil/perbandingan_model.csv")
