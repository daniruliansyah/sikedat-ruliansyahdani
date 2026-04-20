"""
ml_utils.py
===========
Helper functions untuk:
- Memuat model yang sudah ditraining
- Klasifikasi batch dari DataFrame CSV
- Prediksi single input (dari halaman prediksi)
"""

import os
import json
import joblib
import numpy as np
import pandas as pd

MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')

FITUR = ['hari_enc', 'jam', 'menit', 'motor', 'mobil', 'bus', 'truk', 'total_kendaraan']


def _load(filename):
    path = os.path.join(MODEL_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"File {path} tidak ditemukan. "
            "Jalankan train_models.py terlebih dahulu."
        )
    return joblib.load(path)


def load_model():
    return _load('model_aktif.pkl')


def load_scaler():
    return _load('scaler.pkl')


def load_encoders():
    le_hari  = _load('le_hari.pkl')
    le_label = _load('le_label.pkl')
    return le_hari, le_label


def load_metadata():
    path = os.path.join(MODEL_DIR, 'metadata.json')
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)


# ============================================================
# KLASIFIKASI BATCH — dari DataFrame CSV yang diupload user
# ============================================================
def classify_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Menerima DataFrame hasil upload CSV (tanpa kolom tingkat_kepadatan),
    mengembalikan DataFrame yang sama ditambah kolom:
    - tingkat_kepadatan  : prediksi label
    - confidence         : probabilitas kelas yang diprediksi (%)
    - proba_rendah/sedang/tinggi : probabilitas per kelas

    Raises ValueError jika kolom yang dibutuhkan tidak lengkap.
    """
    KOLOM_WAJIB = ['hari', 'jam', 'menit', 'motor', 'mobil', 'bus', 'truk', 'total_kendaraan']
    missing = [c for c in KOLOM_WAJIB if c not in df.columns]
    if missing:
        raise ValueError(f"Kolom tidak lengkap: {missing}")

    model    = load_model()
    scaler   = load_scaler()
    le_hari, le_label = load_encoders()

    df = df.copy()

    # Handle hari yang tidak dikenal dengan transform aman
    known_hari = list(le_hari.classes_)
    df['hari_clean'] = df['hari'].apply(
        lambda h: h if h in known_hari else known_hari[0]
    )
    df['hari_enc'] = le_hari.transform(df['hari_clean'])

    X = df[FITUR].values
    X_scaled = scaler.transform(X)

    y_pred  = model.predict(X_scaled)
    y_proba = model.predict_proba(X_scaled)  # shape (n, 3)

    classes = list(le_label.classes_)  # ['Rendah', 'Sedang', 'Tinggi']

    df['tingkat_kepadatan'] = le_label.inverse_transform(y_pred)
    df['confidence']        = (np.max(y_proba, axis=1) * 100).round(1)

    for i, cls in enumerate(classes):
        df[f'proba_{cls.lower()}'] = (y_proba[:, i] * 100).round(1)

    # Buang kolom helper
    df.drop(columns=['hari_clean', 'hari_enc'], errors='ignore', inplace=True)

    return df


# ============================================================
# PREDIKSI SINGLE — dari halaman prediksi (input manual)
# ============================================================
def predict_single(hari: str, jam: int, menit: int) -> dict:
    """
    Prediksi kepadatan berdasarkan hari, jam, menit saja.
    Nilai motor/mobil/bus/truk diestimasi dari rata-rata historis
    (karena user tidak menginput volume kendaraan di halaman prediksi publik).

    Returns dict:
    {
        'label'     : 'Sedang',
        'confidence': 78.5,
        'proba'     : {'Rendah': 12.0, 'Sedang': 78.5, 'Tinggi': 9.5}
    }
    """
    # Nilai rata-rata historis per jam (estimasi kasar)
    avg_per_jam = {
        6:  {'motor':28, 'mobil':9,  'bus':3, 'truk':2},
        7:  {'motor':72, 'mobil':22, 'bus':6, 'truk':4},
        8:  {'motor':48, 'mobil':15, 'bus':4, 'truk':3},
        15: {'motor':38, 'mobil':12, 'bus':4, 'truk':3},
        16: {'motor':55, 'mobil':17, 'bus':5, 'truk':3},
        17: {'motor':78, 'mobil':24, 'bus':7, 'truk':4},
        18: {'motor':52, 'mobil':16, 'bus':5, 'truk':3},
        19: {'motor':32, 'mobil':10, 'bus':3, 'truk':2},
    }

    avg = avg_per_jam.get(int(jam), {'motor':40, 'mobil':12, 'bus':4, 'truk':3})
    total = avg['motor'] + avg['mobil'] + avg['bus'] + avg['truk']

    df_single = pd.DataFrame([{
        'hari': hari, 'jam': int(jam), 'menit': int(menit),
        'motor': avg['motor'], 'mobil': avg['mobil'],
        'bus': avg['bus'],     'truk': avg['truk'],
        'total_kendaraan': total
    }])

    result = classify_dataframe(df_single)
    row    = result.iloc[0]
    label_classes = list(load_encoders()[1].classes_)

    proba = {cls: float(row[f'proba_{cls.lower()}']) for cls in label_classes}

    return {
        'label'     : row['tingkat_kepadatan'],
        'confidence': float(row['confidence']),
        'proba'     : proba,
        'hari'      : hari,
        'jam'       : str(jam).zfill(2),
        'menit'     : str(menit).zfill(2),
    }