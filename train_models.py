"""
train_models.py
===============
Training Random Forest dan SVM untuk klasifikasi kepadatan lalu lintas.
Hasil model terbaik disimpan sebagai model_aktif.pkl
Kedua model disimpan sebagai rf_model.pkl dan svm_model.pkl

Jalankan sekali sebelum menjalankan app.py:
    python train_models.py
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime

from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report

# ============================================================
# 1. MUAT DATASET
# ============================================================
CSV_PATH = 'dataset_dummy_berlabel.csv'
if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(
        f"File {CSV_PATH} tidak ditemukan.\n"
        "Jalankan generate_dummy_data.py terlebih dahulu."
    )

df = pd.read_csv(CSV_PATH)
print(f"Dataset dimuat: {len(df)} baris")
print(df['tingkat_kepadatan'].value_counts().to_string())

# ============================================================
# 2. PREPROCESSING
# ============================================================
# 2a. Label encoding kolom 'hari' (ordinal)
le_hari = LabelEncoder()
df['hari_enc'] = le_hari.fit_transform(df['hari'])

# 2b. Label encoding target
le_label = LabelEncoder()
df['label_enc'] = le_label.fit_transform(df['tingkat_kepadatan'])
# Pastikan urutan kelas: ['Rendah', 'Sedang', 'Tinggi']
label_classes = list(le_label.classes_)
print(f"\nKelas: {label_classes}")

# 2c. Fitur yang digunakan
FITUR = ['hari_enc', 'jam', 'menit', 'motor', 'mobil', 'bus', 'truk', 'total_kendaraan']
X = df[FITUR].values
y = df['label_enc'].values

# 2d. Normalisasi (penting untuk SVM)
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

# 2e. Split data: 80% train, 20% test (stratified)
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)
print(f"\nSplit: {len(X_train)} train | {len(X_test)} test")

# ============================================================
# 3. TRAINING RANDOM FOREST
# ============================================================
print("\n" + "="*50)
print("TRAINING RANDOM FOREST")
print("="*50)

rf_params = {
    'n_estimators': [100, 200],
    'max_depth':    [10, 20, None],
    'min_samples_split': [2, 5],
    'min_samples_leaf':  [1, 2],
}

rf_base = RandomForestClassifier(random_state=42)
rf_grid = GridSearchCV(rf_base, rf_params, cv=5, scoring='accuracy',
                       n_jobs=-1, verbose=0)
rf_grid.fit(X_train, y_train)
rf_best = rf_grid.best_estimator_

print(f"Best params RF : {rf_grid.best_params_}")

# Evaluasi RF
y_pred_rf  = rf_best.predict(X_test)
rf_acc     = accuracy_score(y_test, y_pred_rf)
rf_prec    = precision_score(y_test, y_pred_rf, average='weighted', zero_division=0)
rf_rec     = recall_score(y_test, y_pred_rf, average='weighted', zero_division=0)
rf_f1      = f1_score(y_test, y_pred_rf, average='weighted', zero_division=0)
rf_cv      = cross_val_score(rf_best, X_scaled, y, cv=5, scoring='accuracy').mean()

print(f"Akurasi Test  : {rf_acc:.4f} ({rf_acc*100:.2f}%)")
print(f"Precision     : {rf_prec:.4f}")
print(f"Recall        : {rf_rec:.4f}")
print(f"F1-Score      : {rf_f1:.4f}")
print(f"CV Score (5)  : {rf_cv:.4f}")
print("\nClassification Report RF:")
print(classification_report(y_test, y_pred_rf, target_names=label_classes))

# ============================================================
# 4. TRAINING SVM
# ============================================================
print("="*50)
print("TRAINING SVM")
print("="*50)

svm_params = {
    'kernel': ['rbf', 'linear'],
    'C':      [0.1, 1, 10],
    'gamma':  ['scale', 'auto'],
}

svm_base = SVC(probability=True, random_state=42)
svm_grid = GridSearchCV(svm_base, svm_params, cv=5, scoring='accuracy',
                        n_jobs=-1, verbose=0)
svm_grid.fit(X_train, y_train)
svm_best = svm_grid.best_estimator_

print(f"Best params SVM: {svm_grid.best_params_}")

y_pred_svm = svm_best.predict(X_test)
svm_acc    = accuracy_score(y_test, y_pred_svm)
svm_prec   = precision_score(y_test, y_pred_svm, average='weighted', zero_division=0)
svm_rec    = recall_score(y_test, y_pred_svm, average='weighted', zero_division=0)
svm_f1     = f1_score(y_test, y_pred_svm, average='weighted', zero_division=0)
svm_cv     = cross_val_score(svm_best, X_scaled, y, cv=5, scoring='accuracy').mean()

print(f"Akurasi Test  : {svm_acc:.4f} ({svm_acc*100:.2f}%)")
print(f"Precision     : {svm_prec:.4f}")
print(f"Recall        : {svm_rec:.4f}")
print(f"F1-Score      : {svm_f1:.4f}")
print(f"CV Score (5)  : {svm_cv:.4f}")
print("\nClassification Report SVM:")
print(classification_report(y_test, y_pred_svm, target_names=label_classes))

# ============================================================
# 5. TENTUKAN MODEL TERBAIK
# ============================================================
print("="*50)
print("PERBANDINGAN AKHIR")
print("="*50)
print(f"Random Forest : acc={rf_acc:.4f}  f1={rf_f1:.4f}")
print(f"SVM           : acc={svm_acc:.4f}  f1={svm_f1:.4f}")

if rf_f1 >= svm_f1:
    best_model     = rf_best
    best_algo      = 'Random Forest'
    best_acc       = rf_acc
    best_prec      = rf_prec
    best_rec       = rf_rec
    best_f1        = rf_f1
    best_cv        = rf_cv
    best_params    = rf_grid.best_params_
else:
    best_model     = svm_best
    best_algo      = 'SVM'
    best_acc       = svm_acc
    best_prec      = svm_prec
    best_rec       = svm_rec
    best_f1        = svm_f1
    best_cv        = svm_cv
    best_params    = svm_grid.best_params_

print(f"\nModel terbaik : {best_algo} (F1={best_f1:.4f})")

# ============================================================
# 6. SIMPAN SEMUA FILE
# ============================================================
os.makedirs('models', exist_ok=True)

# Simpan kedua model
joblib.dump(rf_best,  'models/rf_model.pkl')
joblib.dump(svm_best, 'models/svm_model.pkl')

# Simpan model terbaik sebagai model_aktif
joblib.dump(best_model, 'models/model_aktif.pkl')

# Simpan scaler dan encoder (dibutuhkan saat prediksi)
joblib.dump(scaler,   'models/scaler.pkl')
joblib.dump(le_hari,  'models/le_hari.pkl')
joblib.dump(le_label, 'models/le_label.pkl')

# Simpan metadata model (dibaca oleh Flask)
metadata = {
    'best_algo'  : best_algo,
    'rf': {
        'accuracy' : round(rf_acc, 6),
        'precision': round(rf_prec, 6),
        'recall'   : round(rf_rec, 6),
        'f1_score' : round(rf_f1, 6),
        'cv_score' : round(rf_cv, 6),
        'params'   : {str(k): str(v) for k, v in rf_grid.best_params_.items()},
    },
    'svm': {
        'accuracy' : round(svm_acc, 6),
        'precision': round(svm_prec, 6),
        'recall'   : round(svm_rec, 6),
        'f1_score' : round(svm_f1, 6),
        'cv_score' : round(svm_cv, 6),
        'params'   : {str(k): str(v) for k, v in svm_grid.best_params_.items()},
    },
    'n_train'    : len(X_train),
    'n_test'     : len(X_test),
    'total_data' : len(df),
    'label_classes': label_classes,
    'fitur'      : FITUR,
    'tanggal'    : datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
}
with open('models/metadata.json', 'w') as f:
    json.dump(metadata, f, indent=2)

print("\nFile tersimpan:")
print("  models/rf_model.pkl")
print("  models/svm_model.pkl")
print("  models/model_aktif.pkl  ← digunakan oleh Flask")
print("  models/scaler.pkl")
print("  models/le_hari.pkl")
print("  models/le_label.pkl")
print("  models/metadata.json")
print("\nSelesai! Sekarang jalankan: python app.py")