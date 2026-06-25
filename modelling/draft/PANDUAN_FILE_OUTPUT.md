# PANDUAN FILE OUTPUT — SKRIPSI BAB 4 & BAB 5
# Mapping: Gambar/Tabel di Draft → Nama File → Script Python Penghasil

Semua file PNG dan CSV di bawah ini dihasilkan OTOMATIS saat Anda menjalankan
script Python yang tercantum. Tidak ada yang dibuat secara manual.

Cara menjalankan script (urutan WAJIB diikuti):
  1. python3 scripts/01_eda.py
  2. python3 scripts/02_preprocessing.py
  3. python3 scripts/03_modelling.py
  4. python3 scripts/04_comparison.py

Sebelum menjalankan, pastikan path di bagian atas setiap script
sudah Anda sesuaikan dengan lokasi file di komputer Anda:
  - 01_eda.py        → INPUT_PATH (CSV catatan), OUTPUT_DIR
  - 02_preprocessing.py → INPUT_PATH, OUTPUT_DIR
  - 03_modelling.py  → DATA_PATH (dataset preprocessed), OUT_BASE
  - 04_comparison.py → OUT_BASE (folder 03_modelling)

================================================================================
BAB 4 — PEMETAAN GAMBAR & TABEL
================================================================================

────────────────────────────────────────────────────────
SUB-BAB 4.2 — Hasil Ekstraksi Data
────────────────────────────────────────────────────────
Tabel 4.2  Contoh Hasil Ekstraksi Data per 10 Menit
  → Bukan file terpisah. Data diambil langsung dari
    output_gabungan_frekuensinq1__catatan.csv (baris Senin).
  → Ditulis manual di draft berdasarkan data asli Anda.

────────────────────────────────────────────────────────
SUB-BAB 4.5 — Hasil Preprocessing Data
────────────────────────────────────────────────────────
Tabel 4.6  Hasil Deteksi Outlier (IQR)
  → File  : 01_eda/tabel_deteksi_outlier_iqr.csv
  → Script: scripts/01_eda.py

Gambar 4.3  Boxplot Deteksi Outlier
  → File  : 01_eda/05_boxplot_outlier.png
  → Script: scripts/01_eda.py

Tabel 4.8  Statistik Deskriptif Fitur Volume Kendaraan
  → File  : 01_eda/tabel_statistik_deskriptif.csv
  → Script: scripts/01_eda.py

Gambar 4.4  Distribusi Jumlah Baris per Hari
  → File  : 01_eda/02_distribusi_per_hari.png
  → Script: scripts/01_eda.py

Gambar 4.5  Distribusi Jumlah Baris per Jam
  → File  : 01_eda/03_distribusi_per_jam.png
  → Script: scripts/01_eda.py

Gambar 4.6  Matriks Korelasi Antar Fitur
  → File  : 01_eda/06_heatmap_korelasi.png
  → Script: scripts/01_eda.py

────────────────────────────────────────────────────────
SUB-BAB 4.4 — Hasil Labeling Data
────────────────────────────────────────────────────────
Gambar 4.2  Distribusi Label Dua Skenario
  → File  : 01_eda/01_distribusi_label_2skenario.png
  → Script: scripts/01_eda.py

────────────────────────────────────────────────────────
SUB-BAB 4.7 — Hasil Modelling (Hyperparameter Tuning)
────────────────────────────────────────────────────────
Tabel 4.11  Hasil GridSearch RF Skenario 1 (16 kombinasi)
  → File  : 03_modelling/rf_scenario1/01_gridsearch_all_combinations.csv
  → Script: scripts/03_modelling.py
  → Kolom : Rank, n_estimators, max_depth, min_samples_split,
            min_samples_leaf, CV_Accuracy, CV_Precision,
            CV_Recall, CV_F1_weighted (+ std masing-masing)

Tabel 4.12  Hasil GridSearch RF Skenario 2 (16 kombinasi)
  → File  : 03_modelling/rf_scenario2/01_gridsearch_all_combinations.csv
  → Script: scripts/03_modelling.py

Tabel 4.14  Hasil GridSearch SVM Skenario 1 (18 kombinasi)
  → File  : 03_modelling/svm_scenario1/01_gridsearch_all_combinations.csv
  → Script: scripts/03_modelling.py
  → Kolom : Rank, kernel, C, gamma, CV_Accuracy, CV_Precision,
            CV_Recall, CV_F1_weighted (+ std masing-masing)

Tabel 4.15  Hasil GridSearch SVM Skenario 2 (18 kombinasi)
  → File  : 03_modelling/svm_scenario2/01_gridsearch_all_combinations.csv
  → Script: scripts/03_modelling.py

────────────────────────────────────────────────────────
SUB-BAB 4.8 — Hasil Evaluasi Model
────────────────────────────────────────────────────────
Tabel 4.17  Confusion Matrix RF Skenario 1 (angka)
  → Bukan file CSV terpisah. Angka diambil dari:
    03_modelling/rf_scenario1/04_classification_report.txt
  → Script: scripts/03_modelling.py

Gambar 4.7  Confusion Matrix RF Skenario 1 (visualisasi)
  → File  : 03_modelling/rf_scenario1/03_confusion_matrix.png
  → Script: scripts/03_modelling.py

Tabel 4.18  Metrik per Kelas RF Skenario 1
  → File  : 03_modelling/rf_scenario1/04_classification_report.txt
  → Script: scripts/03_modelling.py

Gambar 4.8  Feature Importance RF Skenario 1
  → File  : 03_modelling/rf_scenario1/05_feature_importance.png
  → Script: scripts/03_modelling.py

Tabel 4.19  Confusion Matrix RF Skenario 2 (angka)
  → File  : 03_modelling/rf_scenario2/04_classification_report.txt
  → Script: scripts/03_modelling.py

Gambar 4.9  Confusion Matrix RF Skenario 2 (visualisasi)
  → File  : 03_modelling/rf_scenario2/03_confusion_matrix.png
  → Script: scripts/03_modelling.py

Tabel 4.20  Metrik per Kelas RF Skenario 2
  → File  : 03_modelling/rf_scenario2/04_classification_report.txt
  → Script: scripts/03_modelling.py

Gambar 4.10  Feature Importance RF Skenario 2
  → File  : 03_modelling/rf_scenario2/05_feature_importance.png
  → Script: scripts/03_modelling.py

Tabel 4.21  Confusion Matrix SVM Skenario 1 (angka)
  → File  : 03_modelling/svm_scenario1/04_classification_report.txt
  → Script: scripts/03_modelling.py

Gambar 4.11  Confusion Matrix SVM Skenario 1 (visualisasi)
  → File  : 03_modelling/svm_scenario1/03_confusion_matrix.png
  → Script: scripts/03_modelling.py

Tabel 4.22  Metrik per Kelas SVM Skenario 1
  → File  : 03_modelling/svm_scenario1/04_classification_report.txt
  → Script: scripts/03_modelling.py

Gambar 4.12  Permutation Importance SVM Skenario 1
  → File  : 03_modelling/svm_scenario1/05_permutation_importance.png
  → Script: scripts/03_modelling.py

Tabel 4.23  Confusion Matrix SVM Skenario 2 (angka)
  → File  : 03_modelling/svm_scenario2/04_classification_report.txt
  → Script: scripts/03_modelling.py

Gambar 4.13  Confusion Matrix SVM Skenario 2 (visualisasi)
  → File  : 03_modelling/svm_scenario2/03_confusion_matrix.png
  → Script: scripts/03_modelling.py

Tabel 4.24  Metrik per Kelas SVM Skenario 2
  → File  : 03_modelling/svm_scenario2/04_classification_report.txt
  → Script: scripts/03_modelling.py

Gambar 4.14  Permutation Importance SVM Skenario 2
  → File  : 03_modelling/svm_scenario2/05_permutation_importance.png
  → Script: scripts/03_modelling.py

Tabel 4.25  Ringkasan Komparasi 4 Model
  → File  : 03_modelling/ringkasan_4_model.csv
  → Script: scripts/03_modelling.py

Gambar 4.15  Grouped Bar Chart Komparasi 4 Model
  → File  : 04_comparison/01_grouped_bar_4model.png
  → Script: scripts/04_comparison.py

Gambar 4.16  Confusion Matrix 4 Panel (komparasi)
  → File  : 04_comparison/02_confusion_matrix_4panel.png
  → Script: scripts/04_comparison.py

Gambar 4.17  Metrik per Kelas 4 Model
  → File  : 04_comparison/03_metrik_per_kelas.png
  → Script: scripts/04_comparison.py

================================================================================
BAB 5 — PEMETAAN GAMBAR & TABEL
================================================================================

────────────────────────────────────────────────────────
SUB-BAB 5.2 — Pembahasan Preprocessing & EDA
────────────────────────────────────────────────────────
Tabel 5.1  Korelasi Fitur vs Tingkat_Kepadatan
  → Bukan file terpisah. Angka diambil dari:
    01_eda/06_heatmap_korelasi.png dan
    tabel_statistik_deskriptif.csv (korelasi dihitung di script 01_eda.py)
  → Script: scripts/01_eda.py
  → Angka ditulis manual di draft berdasarkan output script.

Gambar 5.1 (opsional, jika ingin ditambahkan)
  Komposisi kelas per jam (mendukung analisis confounding)
  → File  : 01_eda/09_komposisi_kelas_per_jam.png
  → Script: scripts/01_eda.py

────────────────────────────────────────────────────────
SUB-BAB 5.6 — Perbandingan Penelitian Terdahulu
────────────────────────────────────────────────────────
Tabel 5.4  Perbandingan 10 Penelitian Terdahulu
  → Bukan file output script. Tabel ini disusun manual
    berdasarkan hasil pencarian literatur di:
    - ResearchGate
    - Repository UPI Bandung
    - Repository UGM
    - OpenLibrary Telkom University
    - IEEEXplore
    - Springer Nature
    - Journal of Information Systems and Informatics

================================================================================
FILE TAMBAHAN (tidak dirujuk di draft tapi tersedia di folder)
================================================================================

01_eda/04_histogram_fitur.png
  → Histogram distribusi 5 fitur volume kendaraan
  → Script: scripts/01_eda.py
  → Bisa digunakan sebagai gambar pendukung di sub-bab 4.5.5 jika perlu

01_eda/07_boxplot_fitur_per_kelas_S1.png
01_eda/08_boxplot_fitur_per_kelas_S2.png
  → Boxplot fitur per kelas untuk Skenario 1 dan 2
  → Script: scripts/01_eda.py
  → Berguna untuk mendukung analisis di sub-bab 5.3.2 (trade-off S1 vs S2)

04_comparison/tabel_metrik_per_kelas.csv
  → Tabel metrik (Precision, Recall, F1) per kelas untuk 4 model
  → Script: scripts/04_comparison.py
  → Data yang sama dengan Tabel 4.18, 4.20, 4.22, 4.24 — versi CSV gabungan

03_modelling/*/02_best_params.txt  (4 file)
  → Ringkasan best params + metrik test set per model dalam format teks
  → Script: scripts/03_modelling.py

03_modelling/*/model.pkl  (4 file)
  → File model terlatih dalam format pickle
  → Script: scripts/03_modelling.py
  → Digunakan untuk integrasi ke aplikasi web Flask (sub-bab 4.9.4)
  → Load dengan: import pickle; model = pickle.load(open('model.pkl','rb'))

02_preprocessing/dataset_preprocessed.csv
  → Dataset hasil preprocessing (877 baris × 16 kolom)
  → Script: scripts/02_preprocessing.py
  → Input untuk scripts/03_modelling.py

================================================================================
RINGKASAN CEPAT: SCRIPT → OUTPUT
================================================================================

scripts/01_eda.py
  OUTPUT (11 file di folder 01_eda/):
  ├── 01_distribusi_label_2skenario.png   → Gambar 4.2
  ├── 02_distribusi_per_hari.png          → Gambar 4.4
  ├── 03_distribusi_per_jam.png           → Gambar 4.5
  ├── 04_histogram_fitur.png              → (pendukung)
  ├── 05_boxplot_outlier.png              → Gambar 4.3
  ├── 06_heatmap_korelasi.png             → Gambar 4.6
  ├── 07_boxplot_fitur_per_kelas_S1.png   → (pendukung)
  ├── 08_boxplot_fitur_per_kelas_S2.png   → (pendukung)
  ├── 09_komposisi_kelas_per_jam.png      → (Gambar 5.1 opsional)
  ├── tabel_statistik_deskriptif.csv      → Tabel 4.8
  └── tabel_deteksi_outlier_iqr.csv       → Tabel 4.6

scripts/02_preprocessing.py
  OUTPUT (1 file di folder 02_preprocessing/):
  └── dataset_preprocessed.csv           → input untuk 03_modelling.py

scripts/03_modelling.py
  OUTPUT (di folder 03_modelling/):
  ├── ringkasan_4_model.csv              → Tabel 4.25
  ├── results_raw.pkl                    → input untuk 04_comparison.py
  ├── rf_scenario1/
  │   ├── 01_gridsearch_all_combinations.csv → Tabel 4.11
  │   ├── 02_best_params.txt             → (pendukung)
  │   ├── 03_confusion_matrix.png        → Gambar 4.7
  │   ├── 04_classification_report.txt   → Tabel 4.17 & 4.18
  │   ├── 05_feature_importance.png      → Gambar 4.8
  │   └── model.pkl                      → untuk deploy Flask
  ├── rf_scenario2/  [struktur sama]     → Gambar 4.9, 4.10 & Tabel 4.19, 4.20, 4.12
  ├── svm_scenario1/ [struktur sama]     → Gambar 4.11, 4.12 & Tabel 4.21, 4.22, 4.14
  └── svm_scenario2/ [struktur sama]     → Gambar 4.13, 4.14 & Tabel 4.23, 4.24, 4.15

scripts/04_comparison.py
  OUTPUT (di folder 04_comparison/):
  ├── 01_grouped_bar_4model.png          → Gambar 4.15
  ├── 02_confusion_matrix_4panel.png     → Gambar 4.16
  ├── 03_metrik_per_kelas.png            → Gambar 4.17
  ├── tabel_metrik_per_kelas.csv         → (pendukung)
  └── RINGKASAN_KOMPARASI.txt            → (pendukung)
