"""
================================================================================
SKRIPSI - EXPLORATORY DATA ANALYSIS (EDA)
================================================================================

Input  : output_gabungan_frekuensinq1__catatan.csv (877 baris, 10 kolom)
Output : 9 plot PNG + 2 tabel CSV di folder 01_eda/

Yang dilakukan:
1. Statistik deskriptif (count, mean, std, min, Q1, median, Q3, max, skew, kurt)
2. Visualisasi distribusi target (2 skenario labeling)
3. Distribusi data per Hari dan per Jam
4. Histogram fitur volume kendaraan + boxplot deteksi outlier
5. Deteksi outlier metode IQR (deteksi saja, tidak dihapus)
6. Matriks korelasi antar fitur
7. Boxplot fitur per kelas (untuk masing-masing skenario)
8. Komposisi kelas per jam (insight pola lalu lintas)

Author: Skripsi Dani Ruliansyah, Universitas Airlangga, 2026
================================================================================
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# ============ KONFIGURASI ============
INPUT_PATH = '/mnt/project/output_gabungan_frekuensinq1__catatan.csv'
OUTPUT_DIR = '/home/claude/skripsi/01_eda'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Plot style — print-friendly untuk skripsi
sns.set_style("whitegrid")
plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 11,
    'axes.titlesize': 13, 'axes.labelsize': 11,
    'xtick.labelsize': 10, 'ytick.labelsize': 10,
    'figure.dpi': 110, 'savefig.dpi': 200,
    'savefig.bbox': 'tight'
})

NUM_COLS = ['Motor', 'Mobil', 'Bus', 'Truk', 'Total_Kendaraan']
CLASS_ORDER = ['Rendah', 'Sedang', 'Tinggi']
PALETTE_CLASS = {'Rendah': '#2E86AB', 'Sedang': '#F18F01', 'Tinggi': '#C73E1D'}
ORDER_HARI = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']


# ============ FUNGSI LABELING (sama dengan preprocessing) ============
def label_s1(x):
    """Skenario 1: 0=Rendah, 1-2=Sedang, >=3=Tinggi."""
    if x == 0: return 'Rendah'
    if x <= 2: return 'Sedang'
    return 'Tinggi'

def label_s2(row):
    """Skenario 2: 0+ramai lancar=Sedang, sisanya sama dengan S1."""
    f, c = row['Tingkat_Kepadatan'], row['Catatan']
    if f == 0 and c == 'kosong': return 'Rendah'
    if f == 0 and c == 'ramai lancar': return 'Sedang'
    if f <= 2: return 'Sedang'
    return 'Tinggi'


# ============ MAIN ============
print("="*70)
print("EXPLORATORY DATA ANALYSIS")
print("="*70)

# --- Load data ---
df = pd.read_csv(INPUT_PATH)
df['Catatan'] = df['Catatan'].fillna('').replace('', 'kosong')
df['Label_S1'] = df['Tingkat_Kepadatan'].apply(label_s1)
df['Label_S2'] = df.apply(label_s2, axis=1)

print(f"\nDataset: {df.shape[0]} baris × {df.shape[1]} kolom")
print(f"Missing values: {df.isnull().sum().sum()}")

# --- Statistik deskriptif ---
print("\n--- Statistik deskriptif fitur volume kendaraan ---")
stat = df[NUM_COLS].describe().round(2).T
stat['skewness'] = df[NUM_COLS].skew().round(2)
stat['kurtosis'] = df[NUM_COLS].kurtosis().round(2)
print(stat)
stat.to_csv(os.path.join(OUTPUT_DIR, 'tabel_statistik_deskriptif.csv'))
print(f"✓ tabel_statistik_deskriptif.csv")

# --- Plot 1: Distribusi target 2 skenario ---
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
for ax, col, judul in [(axes[0], 'Label_S1', 'Skenario 1\n(0 = Rendah)'),
                         (axes[1], 'Label_S2', 'Skenario 2\n(0 ramai lancar = Sedang)')]:
    counts = df[col].value_counts().reindex(CLASS_ORDER)
    bars = ax.bar(counts.index, counts.values,
                   color=[PALETTE_CLASS[k] for k in counts.index],
                   edgecolor='black', linewidth=0.5)
    for bar, v in zip(bars, counts.values):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+5,
                f'{v}\n({v/len(df)*100:.1f}%)', ha='center', va='bottom', fontsize=10)
    ax.set_title(judul); ax.set_ylabel('Jumlah baris'); ax.set_xlabel('Kelas Tingkat Kepadatan')
    ax.set_ylim(0, max(counts.values)*1.18)
plt.suptitle('Distribusi Label pada Dua Skenario Dataset', fontsize=14, y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, '01_distribusi_label_2skenario.png'))
plt.close()
print("✓ 01_distribusi_label_2skenario.png")

# --- Plot 2: Distribusi per Hari ---
fig, ax = plt.subplots(figsize=(9, 4))
counts = df['Hari'].value_counts().reindex(ORDER_HARI)
bars = ax.bar(counts.index, counts.values, color='#4A6FA5', edgecolor='black', linewidth=0.5)
for bar, v in zip(bars, counts.values):
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+1, str(v),
            ha='center', va='bottom', fontsize=10)
ax.set_title('Distribusi Jumlah Baris Data per Hari'); ax.set_ylabel('Jumlah baris'); ax.set_xlabel('Hari')
ax.set_ylim(0, max(counts.values)*1.12)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, '02_distribusi_per_hari.png'))
plt.close()
print("✓ 02_distribusi_per_hari.png")

# --- Plot 3: Distribusi per Jam ---
fig, ax = plt.subplots(figsize=(9, 4))
counts = df['Jam'].value_counts().sort_index()
bars = ax.bar(counts.index.astype(str), counts.values, color='#4A6FA5', edgecolor='black', linewidth=0.5)
for bar, v in zip(bars, counts.values):
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+1, str(v),
            ha='center', va='bottom', fontsize=10)
ax.set_title('Distribusi Jumlah Baris Data per Jam Pengamatan'); ax.set_ylabel('Jumlah baris'); ax.set_xlabel('Jam (WIB)')
ax.set_ylim(0, max(counts.values)*1.12)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, '03_distribusi_per_jam.png'))
plt.close()
print("✓ 03_distribusi_per_jam.png")

# --- Plot 4: Histogram fitur ---
fig, axes = plt.subplots(2, 3, figsize=(13, 7))
axes = axes.flatten()
for i, col in enumerate(NUM_COLS):
    axes[i].hist(df[col], bins=30, color='#4A6FA5', edgecolor='black', alpha=0.8)
    axes[i].set_title(f'Distribusi {col}'); axes[i].set_xlabel(col); axes[i].set_ylabel('Frekuensi')
    axes[i].axvline(df[col].mean(), color='#C73E1D', ls='--', lw=1.5, label=f'Mean: {df[col].mean():.1f}')
    axes[i].axvline(df[col].median(), color='#1D7C3E', ls='--', lw=1.5, label=f'Median: {df[col].median():.0f}')
    axes[i].legend(fontsize=9)
axes[5].axis('off')
plt.suptitle('Distribusi Fitur Volume Kendaraan', fontsize=14, y=1.0)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, '04_histogram_fitur.png'))
plt.close()
print("✓ 04_histogram_fitur.png")

# --- Plot 5: Boxplot deteksi outlier ---
fig, axes = plt.subplots(1, 5, figsize=(15, 4.5))
for i, col in enumerate(NUM_COLS):
    axes[i].boxplot(df[col], patch_artist=True,
                    boxprops=dict(facecolor='#A8C5E5', edgecolor='black'),
                    medianprops=dict(color='#C73E1D', linewidth=2),
                    flierprops=dict(marker='o', markerfacecolor='#C73E1D', markersize=4, alpha=0.6))
    axes[i].set_title(col); axes[i].set_xticks([])
plt.suptitle('Boxplot Fitur Volume Kendaraan untuk Deteksi Outlier', fontsize=13, y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, '05_boxplot_outlier.png'))
plt.close()
print("✓ 05_boxplot_outlier.png")

# --- Deteksi outlier IQR ---
print("\n--- DETEKSI OUTLIER (METODE IQR) ---")
outlier_summary = []
for col in NUM_COLS:
    q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
    iqr = q3 - q1
    lower, upper = q1 - 1.5*iqr, q3 + 1.5*iqr
    n = ((df[col] < lower) | (df[col] > upper)).sum()
    outlier_summary.append({
        'Fitur': col, 'Q1': round(q1,2), 'Q3': round(q3,2), 'IQR': round(iqr,2),
        'Batas_Bawah': round(lower,2), 'Batas_Atas': round(upper,2),
        'Jumlah_Outlier': int(n), 'Persentase': f'{n/len(df)*100:.2f}%'
    })
od = pd.DataFrame(outlier_summary)
print(od.to_string(index=False))
od.to_csv(os.path.join(OUTPUT_DIR, 'tabel_deteksi_outlier_iqr.csv'), index=False)
print("✓ tabel_deteksi_outlier_iqr.csv")
print("Catatan: Outlier tidak dihapus (mempertahankan info kondisi ekstrem)")

# --- Plot 6: Heatmap korelasi ---
fig, ax = plt.subplots(figsize=(7, 5.5))
corr = df[NUM_COLS + ['Tingkat_Kepadatan']].corr()
mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
sns.heatmap(corr, annot=True, fmt='.2f', cmap='RdBu_r', center=0, vmin=-1, vmax=1,
            square=True, linewidths=0.5, cbar_kws={'shrink': 0.7}, mask=mask, ax=ax)
ax.set_title('Matriks Korelasi Antar Fitur', pad=12)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, '06_heatmap_korelasi.png'))
plt.close()
print("✓ 06_heatmap_korelasi.png")

# --- Plot 7 & 8: Boxplot fitur per kelas (2 skenario) ---
for skenario, lbl_col in [(1, 'Label_S1'), (2, 'Label_S2')]:
    fig, axes = plt.subplots(1, 5, figsize=(16, 4.5))
    for i, col in enumerate(NUM_COLS):
        data_to_plot = [df[df[lbl_col]==k][col].values for k in CLASS_ORDER]
        bp = axes[i].boxplot(data_to_plot, labels=CLASS_ORDER, patch_artist=True,
                              medianprops=dict(color='black', linewidth=1.5))
        for patch, k in zip(bp['boxes'], CLASS_ORDER):
            patch.set_facecolor(PALETTE_CLASS[k]); patch.set_alpha(0.75)
        axes[i].set_title(col); axes[i].set_xlabel('')
    plt.suptitle(f'Sebaran Fitur Volume Kendaraan per Kelas — Skenario {skenario}', fontsize=13, y=1.02)
    plt.tight_layout()
    suffix = '07_boxplot_fitur_per_kelas_S1.png' if skenario==1 else '08_boxplot_fitur_per_kelas_S2.png'
    plt.savefig(os.path.join(OUTPUT_DIR, suffix))
    plt.close()
    print(f"✓ {suffix}")

# --- Plot 9: Komposisi kelas per jam ---
fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
for ax, lbl_col, judul in [(axes[0], 'Label_S1', 'Skenario 1'), (axes[1], 'Label_S2', 'Skenario 2')]:
    pivot = df.pivot_table(index='Jam', columns=lbl_col, values='Total_Kendaraan',
                            aggfunc='count', fill_value=0)
    pivot = pivot.reindex(columns=CLASS_ORDER, fill_value=0)
    pivot.plot(kind='bar', stacked=True, ax=ax,
                color=[PALETTE_CLASS[k] for k in CLASS_ORDER],
                edgecolor='black', linewidth=0.5, width=0.78)
    ax.set_title(f'Komposisi Kelas per Jam — {judul}')
    ax.set_xlabel('Jam'); ax.set_ylabel('Jumlah baris')
    ax.legend(title='Kelas', loc='upper right'); ax.tick_params(axis='x', rotation=0)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, '09_komposisi_kelas_per_jam.png'))
plt.close()
print("✓ 09_komposisi_kelas_per_jam.png")

print(f"\n=== EDA SELESAI. Semua hasil di: {OUTPUT_DIR} ===")
