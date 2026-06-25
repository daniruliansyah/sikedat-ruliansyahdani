"""
train_models.py
===============
Training ulang Random Forest (Skenario 1 — fixed params) dari
dataset yang sudah divalidasi. Dipanggil oleh app.py saat retrain.

Input : dataset_tervalidasi.csv  (diekspor oleh app.py dari DB)
Output: models/model_aktif.pkl
        models/metadata.json
"""

import os, json
import pandas as pd
import joblib
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import (accuracy_score, precision_score,
                             recall_score, f1_score, classification_report)

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
CSV_PATH   = os.path.join(BASE_DIR, 'dataset_tervalidasi.csv')
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'model_aktif.pkl')
META_PATH  = os.path.join(BASE_DIR, 'models', 'metadata.json')

HARI_COLS = ['Hari_Jumat', 'Hari_Kamis', 'Hari_Minggu', 'Hari_Rabu',
             'Hari_Sabtu', 'Hari_Selasa', 'Hari_Senin']
FITUR     = ['Jam', 'Menit'] + HARI_COLS + ['Motor', 'Mobil', 'Bus', 'Truk', 'Total_Kendaraan']

RF_PARAMS = {
    'n_estimators'     : 200,
    'max_depth'        : 10,
    'min_samples_split': 2,
    'min_samples_leaf' : 1,
    'class_weight'     : 'balanced',
    'random_state'     : 42,
}


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # Kolom dari DB export sudah lowercase; rename ke Title case yang dibutuhkan FITUR
    df.columns = df.columns.str.strip().str.lower()
    col_map = {
        'jam': 'Jam', 'menit': 'Menit',
        'motor': 'Motor', 'mobil': 'Mobil', 'bus': 'Bus',
        'truk': 'Truk', 'total_kendaraan': 'Total_Kendaraan',
        'tingkat_kepadatan': 'Tingkat_Kepadatan',
    }
    df = df.rename(columns=col_map)

    # OHE untuk kolom hari (nilai sudah Title case dari DB: Senin, Selasa, dst.)
    hari_series = df['hari'].str.strip().str.title()
    for col in HARI_COLS:
        nama_hari = col.replace('Hari_', '')
        df[col] = (hari_series == nama_hari).astype(int)

    return df


# ============================================================
# Cek keberadaan file CSV (dipanggil oleh subprocess dari app.py)
# ============================================================
if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(
        f"File {CSV_PATH} tidak ditemukan.\n"
        "Pastikan ada data yang sudah divalidasi sebelum retrain."
    )

df = pd.read_csv(CSV_PATH)
print(f'[RETRAIN] Dataset: {len(df)} baris')
print(df['tingkat_kepadatan'].value_counts().to_string()
      if 'tingkat_kepadatan' in df.columns
      else df['Tingkat_Kepadatan'].value_counts().to_string())

df = preprocess(df)

X = df[FITUR].values
y = df['Tingkat_Kepadatan'].values

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
print(f'[RETRAIN] Split: {len(X_train)} train | {len(X_test)} test')

model = RandomForestClassifier(**RF_PARAMS)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
acc  = accuracy_score(y_test, y_pred)
prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
rec  = recall_score(y_test, y_pred, average='weighted', zero_division=0)
f1   = f1_score(y_test, y_pred, average='weighted', zero_division=0)

cv    = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_f1 = cross_val_score(model, X, y, cv=cv, scoring='f1_weighted').mean()

print(f'[RETRAIN] Accuracy : {acc:.4f}')
print(f'[RETRAIN] F1       : {f1:.4f}')
print(f'[RETRAIN] CV F1    : {cv_f1:.4f}')
print(classification_report(y_test, y_pred))

os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
joblib.dump(model, MODEL_PATH)

metadata = {
    'best_algo'    : 'Random Forest',
    'model_type'   : 'Random Forest',
    'scenario'     : 'S1',
    'n_train'      : len(X_train),
    'n_test'       : len(X_test),
    'n_total'      : len(df),
    'features'     : FITUR,
    'params'       : RF_PARAMS,
    'rf': {
        'accuracy' : round(acc,   4),
        'precision': round(prec,  4),
        'recall'   : round(rec,   4),
        'f1_score' : round(f1,    4),
        'cv_f1'    : round(cv_f1, 4),
    },
    'label_classes': sorted(list(set(y))),
    'trained_at'   : datetime.now().isoformat(),
}
with open(META_PATH, 'w') as f:
    json.dump(metadata, f, indent=2)

print(f'[RETRAIN] Model disimpan  : {MODEL_PATH}')
print(f'[RETRAIN] Metadata disimpan: {META_PATH}')
