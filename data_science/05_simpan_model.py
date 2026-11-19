"""
LANGKAH 5 - Menyimpan model untuk aplikasi
Tujuan : menyimpan model terbaik supaya bisa dipakai dasbor dan dikirim ke Kesya/Tengku.
Input  : hasil/01_nota_asli.csv, hasil/perbandingan_model.csv
Output : hasil/model_estimasi.joblib
"""
import joblib
import pandas as pd

nota = pd.read_csv("hasil/01_nota_asli.csv")
perb = pd.read_csv("hasil/perbandingan_model.csv")
terbaik = perb.sort_values("MAE_hari").iloc[0]["model"]
print("Model terbaik dari langkah 4:", terbaik)

BATAS_KECIL = 15
if terbaik == "Baseline median":
    # median lama pengerjaan per produk
    paket = {"jenis": "median",
             "median_per_produk": nota.groupby("kategori")["lama_hari"].median().to_dict(),
             "median_global": float(nota["lama_hari"].median())}
elif terbaik == "Median per ukuran pesanan":
    # median lama pengerjaan pesanan kecil (15 pcs ke bawah) dan besar (di atas 15 pcs), beserta kisaran biasanya (kuartil 1 sampai 3)
    kecil = nota[nota["jumlah"] <= BATAS_KECIL]["lama_hari"]
    besar = nota[nota["jumlah"] > BATAS_KECIL]["lama_hari"]
    paket = {"jenis": "median_ukuran", "batas": BATAS_KECIL,
             "median_kecil": float(kecil.median()), "kisaran_kecil": [float(kecil.quantile(.25)), float(kecil.quantile(.75))],
             "median_besar": float(besar.median()), "kisaran_besar": [float(besar.quantile(.25)), float(besar.quantile(.75))],
             "median_per_produk": nota.groupby("kategori")["lama_hari"].median().to_dict(),
             "median_global": float(nota["lama_hari"].median())}
else:
    # Regresi Linear atau Random Forest: latih pada semua nota asli
    from sklearn.compose import ColumnTransformer
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.linear_model import LinearRegression
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder
    est = LinearRegression() if terbaik == "Regresi Linear" else RandomForestRegressor(n_estimators=200, min_samples_leaf=2, random_state=42)
    pre = ColumnTransformer([("kat", OneHotEncoder(handle_unknown="ignore"), ["kategori"])], remainder="passthrough")
    model = Pipeline([("pre", pre), ("model", est)]).fit(nota[["kategori", "jumlah"]], nota["lama_hari"])
    paket = {"jenis": terbaik, "model": model}
print("Isi model:", {k: v for k, v in paket.items() if k != "model"})

joblib.dump(paket, "hasil/model_estimasi.joblib")
print("Tersimpan: hasil/model_estimasi.joblib")
