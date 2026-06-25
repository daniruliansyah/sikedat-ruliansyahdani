"""
================================================================================
SKRIPSI - DATA PREPROCESSING
================================================================================

Input  : output_gabungan_frekuensinq1__catatan.csv (raw, 877 baris × 10 kolom)
Output : dataset_preprocessed.csv (877 baris × 16 kolom) di 02_preprocessing/

Tahapan:
1. Labeling 2 skenario (Label_S1, Label_S2) dari frekuensi Nq1 + catatan
2. Penanganan missing values (hasil cek: 0, tidak perlu imputasi)
3. Deteksi outlier IQR (tidak dihapus, hanya dilaporkan di EDA)
4. One-Hot Encoding kolom 'Hari' (7 kolom binary)
5. Susun dataset final: Jam, Menit, 7 Hari_*, 5 fitur volume, 2 label
6. Normalisasi TIDAK diterapkan di sini:
   - StandardScaler dimasukkan ke dalam sklearn Pipeline saat training SVM
     (mencegah data leakage selama cross-validation)
   - Random Forest tidak memerlukan scaling (tree-based, scale-invariant)

Author: Skripsi Dani Ruliansyah, Universitas Airlangga, 2026
================================================================================
"""

import os
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# ============ KONFIGURASI ============
INPUT_PATH = '/mnt/project/output_gabungan_frekuensinq1__catatan.csv'
OUTPUT_DIR = '/home/claude/skripsi/02_preprocessing'
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============ FUNGSI LABELING ============
def label_s1(x):
    """Skenario 1: 0=Rendah, 1-2=Sedang, >=3=Tinggi."""
    if x == 0: return 'Rendah'
    if x <= 2: return 'Sedang'
    return 'Tinggi'

def label_s2(row):
    """Skenario 2: 0+ramai lancar=Sedang (sesuai validasi pakar)."""
    f, c = row['Tingkat_Kepadatan'], row['Catatan']
    if f == 0 and c == 'kosong': return 'Rendah'
    if f == 0 and c == 'ramai lancar': return 'Sedang'
    if f <= 2: return 'Sedang'
    return 'Tinggi'


# ============ MAIN ============
print("="*70)
print("PREPROCESSING DATA")
print("="*70)

# [1] Load + normalisasi kolom Catatan
df = pd.read_csv(INPUT_PATH)
df['Catatan'] = df['Catatan'].fillna('').replace('', 'kosong')
print(f"\n[1] Loaded: {df.shape[0]} baris × {df.shape[1]} kolom")

# [2] Labeling 2 skenario
df['Label_S1'] = df['Tingkat_Kepadatan'].apply(label_s1)
df['Label_S2'] = df.apply(label_s2, axis=1)
print(f"\n[2] Labeling selesai")
print(f"    Skenario 1: {df['Label_S1'].value_counts().to_dict()}")
print(f"    Skenario 2: {df['Label_S2'].value_counts().to_dict()}")

# [3] Missing values check
mv = df.isnull().sum().sum()
print(f"\n[3] Missing values: {mv} → tidak perlu imputasi")

# [4] Outlier handling - DETEKSI SAJA, tidak dihapus
print(f"\n[4] Outlier handling: deteksi IQR di EDA, TIDAK DIHAPUS")
print(f"    (Mempertahankan informasi kondisi ekstrem lalu lintas)")

# [5] One-Hot Encoding 'Hari'
hari_dummies = pd.get_dummies(df['Hari'], prefix='Hari', dtype=int)
print(f"\n[5] One-Hot Encoding 'Hari' → {hari_dummies.shape[1]} kolom: {list(hari_dummies.columns)}")

# [6] Susun dataset final
df_pre = pd.concat([
    df[['Jam', 'Menit']],
    hari_dummies,
    df[['Motor', 'Mobil', 'Bus', 'Truk', 'Total_Kendaraan']],
    df[['Label_S1', 'Label_S2']]
], axis=1)
print(f"\n[6] Dataset preprocessed shape: {df_pre.shape}")

# [7] Normalisasi (tidak dilakukan, dijelaskan)
print(f"\n[7] StandardScaler: dimasukkan ke sklearn Pipeline saat training SVM")
print(f"    (RF tidak perlu scaling)")

# Save
output_path = os.path.join(OUTPUT_DIR, 'dataset_preprocessed.csv')
df_pre.to_csv(output_path, index=False)
print(f"\n✓ Saved: {output_path}")
print(f"  Shape: {df_pre.shape[0]} rows × {df_pre.shape[1]} cols")
print(f"  Fitur (14): {[c for c in df_pre.columns if c not in ['Label_S1','Label_S2']]}")
print(f"  Target (2): ['Label_S1', 'Label_S2']")

print(f"\n=== PREPROCESSING SELESAI ===")
