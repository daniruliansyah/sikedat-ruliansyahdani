"""
ml_utils.py
===========
Helper functions untuk:
- Memuat model yang sudah ditraining
- Klasifikasi batch dari DataFrame CSV
- Prediksi single input (dari halaman prediksi)
"""

import os, json
import joblib
import numpy as np
import pandas as pd

MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')

HARI_COLS = ['Hari_Jumat', 'Hari_Kamis', 'Hari_Minggu', 'Hari_Rabu',
             'Hari_Sabtu', 'Hari_Selasa', 'Hari_Senin']

FITUR = ['Jam', 'Menit'] + HARI_COLS + ['Motor', 'Mobil', 'Bus', 'Truk', 'Total_Kendaraan']


def _load(filename):
    path = os.path.join(MODEL_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"File {path} tidak ditemukan. "
            "Jalankan train_initial_model.py terlebih dahulu."
        )
    return joblib.load(path)


def load_model():
    return _load('model_aktif.pkl')


def load_metadata():
    path = os.path.join(MODEL_DIR, 'metadata.json')
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)


def _ohe_hari(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    hari_series = df['hari'].str.strip().str.title()
    for col in HARI_COLS:
        nama_hari = col.replace('Hari_', '')
        df[col] = (hari_series == nama_hari).astype(int)
    return df


# ============================================================
# KLASIFIKASI BATCH — dari DataFrame CSV yang diupload user
# ============================================================
def classify_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Menerima DataFrame hasil upload CSV (kolom lowercase),
    mengembalikan DataFrame yang sama ditambah kolom:
    - tingkat_kepadatan  : prediksi label
    - confidence         : probabilitas kelas yang diprediksi (%)
    - proba_rendah/sedang/tinggi : probabilitas per kelas
    """
    KOLOM_WAJIB = ['hari', 'jam', 'menit', 'motor', 'mobil', 'bus', 'truk', 'total_kendaraan']
    missing = [c for c in KOLOM_WAJIB if c not in df.columns]
    if missing:
        raise ValueError(f"Kolom tidak lengkap: {missing}")

    model = load_model()
    df    = _ohe_hari(df)

    # Rename kolom numerik ke Title case agar sesuai urutan FITUR
    rename_map = {
        'jam': 'Jam', 'menit': 'Menit',
        'motor': 'Motor', 'mobil': 'Mobil',
        'bus': 'Bus', 'truk': 'Truk',
        'total_kendaraan': 'Total_Kendaraan',
    }
    df_feat = df.rename(columns=rename_map)

    X       = df_feat[FITUR].values
    y_pred  = model.predict(X)
    y_proba = model.predict_proba(X)

    classes = list(model.classes_)  # ['Rendah', 'Sedang', 'Tinggi']

    df['tingkat_kepadatan'] = y_pred
    df['confidence']        = (np.max(y_proba, axis=1) * 100).round(1)

    for i, cls in enumerate(classes):
        df[f'proba_{cls.lower()}'] = (y_proba[:, i] * 100).round(1)

    return df


# ============================================================
# PREDIKSI SINGLE — dari halaman prediksi (input manual)
# ============================================================
def predict_single(hari: str, jam: int, menit: int) -> dict:
    """
    Prediksi kepadatan berdasarkan hari, jam, menit saja.
    Nilai motor/mobil/bus/truk diestimasi dari rata-rata historis
    data real (dataset_real_berlabel.csv, 877 baris).
    """
    avg_per_jam = {
        6:  {'motor': 369, 'mobil': 81,  'bus': 5, 'truk': 1},
        7:  {'motor': 434, 'mobil': 109, 'bus': 7, 'truk': 1},
        8:  {'motor': 471, 'mobil': 140, 'bus': 7, 'truk': 2},
        15: {'motor': 487, 'mobil': 229, 'bus': 8, 'truk': 4},
        16: {'motor': 462, 'mobil': 214, 'bus': 5, 'truk': 2},
        17: {'motor': 173, 'mobil': 180, 'bus': 3, 'truk': 1},
        18: {'motor': 21,  'mobil': 85,  'bus': 1, 'truk': 0},
        19: {'motor': 23,  'mobil': 97,  'bus': 1, 'truk': 0},
    }

    avg   = avg_per_jam.get(int(jam), {'motor': 302, 'mobil': 141, 'bus': 5, 'truk': 2})
    total = avg['motor'] + avg['mobil'] + avg['bus'] + avg['truk']

    df_single = pd.DataFrame([{
        'hari': hari, 'jam': int(jam), 'menit': int(menit),
        'motor': avg['motor'], 'mobil': avg['mobil'],
        'bus': avg['bus'],     'truk': avg['truk'],
        'total_kendaraan': total,
    }])

    result  = classify_dataframe(df_single)
    row     = result.iloc[0]
    model   = load_model()
    classes = list(model.classes_)

    proba = {cls: float(row.get(f'proba_{cls.lower()}', 0.0)) / 100 for cls in classes}

    return {
        'label'     : row['tingkat_kepadatan'],
        'confidence': float(row['confidence']),
        'proba'     : proba,
        'hari'      : hari,
        'jam'       : str(jam).zfill(2),
        'menit'     : str(menit).zfill(2),
    }
