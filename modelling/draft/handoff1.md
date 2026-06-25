# HANDOFF 1 — Ringkasan Status Skripsi
**Dari:** Chat sesi pertama (Claude Sonnet 4.6)
**Untuk:** Chat sesi lanjutan
**Tanggal:** Juni 2026
**Mahasiswa:** Dani Ruliansyah — NIM 434221059
**Judul:** Klasifikasi Kepadatan Lalu Lintas Menggunakan Random Forest dan SVM Berbasis Computer Vision YOLOv8 di Jalan Diponegoro Surabaya
**Program:** D-IV Teknik Informatika, Fakultas Vokasi, Universitas Airlangga

---

## 1. FILE-FILE DI PROJECT INI

| File | Keterangan |
|---|---|
| `SKRIPSI_SEMPRO.pdf` | Draft Bab 1–3 (sudah selesai sempro) |
| `progress_also_prompt.md` | Catatan lengkap progress penelitian dari mahasiswa |
| `panduan_bab_4-6_kampus.txt` | Panduan penulisan Bab 4–6 dari kampus |
| `output_gabungan_frekuensinq1__catatan.csv` | Dataset utama (877 baris, 10 kolom + kolom Catatan) |
| `BAB_4_DRAFT.md` | Draft Bab 4 lengkap (889 baris) |
| `BAB_5_DRAFT.md` | Draft Bab 5 lengkap (326 baris) |
| `BAB_6_DRAFT.md` | Draft Bab 6 lengkap (42 baris) |
| `handoff1.md` | File ini |

---

## 2. STATUS PENELITIAN SAAT INI

### Yang Sudah Selesai Dikerjakan
- ✅ Bab 1–3 (selesai sempro)
- ✅ Pengumpulan data CCTV (21 hari × 8 jam dari DISHUB SITS Surabaya)
- ✅ Training YOLOv8 custom (dataset Vehicle Detection 1.000 img Roboflow)
- ✅ Ekstraksi data CCTV → 877 baris CSV
- ✅ Labeling manual (frekuensi cycle failure Nq1, acuan PKJI 2023 + HCM)
- ✅ Validasi pakar (Pak Tommi Firman, DISHUB Surabaya, 9 Juni 2026)
- ✅ EDA + Preprocessing (script Python `01_eda.py` dan `02_preprocessing.py`)
- ✅ Modelling: GridSearchCV RF + SVM × 2 skenario (script `03_modelling.py`)
- ✅ Evaluasi + Komparasi 4 model (script `04_comparison.py`)
- ✅ Draft Bab 4, 5, 6 sudah ada (lihat file di project)
- ✅ Sistem web Flask sudah berjalan (masih dummy data)

### Yang Masih TODO / Belum Dikerjakan
- ⏳ Sub-bab 4.1–4.3 perlu diisi (data video, YOLO training, MAPE)
- ⏳ Sub-bab 4.9 perlu diisi (screenshot web Flask)
- ⏳ Pengujian SUS belum dilakukan
- ⏳ Integrasi model terbaik ke web Flask (saat ini masih dummy)
- ⏳ Revisi Tabel 3.10 & 3.11 di Bab 3 (grid hyperparameter dikecilkan ke Opsi B-Slim)
- ⏳ MAPE evaluasi YOLOv8 belum dihitung formal

---

## 3. KEPUTUSAN TEKNIS YANG SUDAH FINAL

### Dataset & Labeling
- **Kolom target:** `Tingkat_Kepadatan` (Nq1: 0–10) dikonversi ke 3 kelas
- **Skema konversi:** 0 = Rendah, 1–2 = Sedang, ≥3 = Tinggi
- **Skenario 1:** Semua Nq1=0 → Rendah (463/205/209)
- **Skenario 2:** Nq1=0 + catatan "ramai lancar" → Sedang (305/363/209)
- **158 baris** ditandai "ramai lancar" di kolom `Catatan`
- Outlier terdeteksi (Bus: 5 baris, Truk: 43 baris) → **tidak dihapus** (sesuai arahan dospem)

### Preprocessing
- **Encoding:** One-Hot Encoding pada kolom `Hari` → 7 kolom binary
- **Fitur waktu:** `Jam` dan `Menit` sebagai 2 fitur numeric terpisah
- **Scaling:** StandardScaler dimasukkan ke dalam Pipeline SVM saja (RF tidak perlu)
- **Dataset final:** 877 baris × 16 kolom (14 fitur + 2 label)

### Modelling
- **Split:** 80:20 stratified, `random_state=42`
- **Cross-validation:** StratifiedKFold k=5
- **Scoring GridSearch:** `f1_weighted` (multi-metric: accuracy, precision, recall, f1)
- **class_weight:** `'balanced'` untuk kedua algoritma
- **Grid RF (Opsi B-Slim, 16 kombinasi):**
  - `n_estimators`: [100, 200]
  - `max_depth`: [10, None]
  - `min_samples_split`: [2, 5]
  - `min_samples_leaf`: [1, 2]
- **Grid SVM (Opsi B-Slim, 18 kombinasi):**
  - `kernel`: ['linear', 'rbf', 'poly']
  - `C`: [0.1, 1, 10]
  - `gamma`: ['scale', 0.1]

### Hasil Modelling (Ringkasan)

| Model | Skenario | Test Accuracy | Test F1 (weighted) | Test F1 (macro) |
|---|---|---|---|---|
| **Random Forest** | **1** | **73,30%** | **0,7299** | 0,6873 |
| Random Forest | 2 | 63,64% | 0,6399 | 0,6365 |
| SVM | 1 | 65,34% | 0,6538 | 0,6072 |
| SVM | 2 | 60,23% | 0,6056 | 0,6027 |

**Model terbaik: Random Forest Skenario 1**
- `n_estimators=200, max_depth=10, min_samples_split=2, min_samples_leaf=1`
- `class_weight='balanced', random_state=42`
- Disimpan sebagai `model.pkl` untuk integrasi ke web Flask

### Best Params Per Model
- **RF S1:** n_estimators=200, max_depth=10, min_samples_split=2, min_samples_leaf=1
- **RF S2:** n_estimators=200, max_depth=None, min_samples_split=5, min_samples_leaf=1
- **SVM S1:** kernel=rbf, C=10, gamma=0.1
- **SVM S2:** kernel=rbf, C=1, gamma=0.1

---

## 4. TEMUAN PENTING (Untuk Bab 5 Pembahasan)

1. **Korelasi negatif fitur volume vs Tingkat_Kepadatan** — Motor: -0,44; Total: -0,37; Bus: -0,32; Truk: -0,26; Mobil: ≈0. Penyebab: *confounding factor* antara waktu (jam malam) dan limitasi deteksi YOLOv8 pada low-light. Jam 6 pagi: 97% data = Rendah (deteksi optimal). Jam 19 malam: 61% data = Tinggi (deteksi melemah). Analisis ini dibahas di sub-bab 5.2.2 draft Bab 5.

2. **Feature importance RF S1:** Mobil (0,190) > Motor (0,177) > Total_Kendaraan (0,170) > Jam (0,168) >> Hari_* (<0,04). Fitur Hari sangat tidak penting — kandidat untuk di-drop di penelitian lanjutan.

3. **Trade-off Skenario 1 vs 2:** S1 unggul accuracy/F1-weighted; S2 unggul F1-macro dan recall kelas Sedang. S2 lebih "adil" per kelas berkat saran pakar Pak Tommi.

4. **Kelas Sedang paling sulit** — recall Sedang hanya 46,34% di RF S1. Konsisten di semua 4 model.

---

## 5. INFORMASI PENELITIAN PENTING

### Narasumber & Kontak
- **Data CCTV:** Bu Nina — SITS (Surabaya Intelligent Transport System), Bidang Lalu Lintas DISHUB Surabaya
- **Validasi pakar:** Bapak Tommi Firman — Seksi Manajemen Rekayasa Lalu Lintas, Bidang Lalu Lintas, DISHUB Surabaya. Tanggal: 9 Juni 2026, Kantor DISHUB Surabaya, Dukuh Menanggal No. 1

### Dataset & Tools
- **Dataset YOLO:** Vehicle Detection Computer Vision Model, 1.000 img, Roboflow
  URL: https://universe.roboflow.com/skripsi-1qzlz/vehicle-detection-ckrxi
- **Dataset malam (eksperimen, TIDAK dipakai — hasilnya lebih buruk):** Traffic Night, 5.400 img, Roboflow
  URL: https://universe.roboflow.com/univ-kqors/traffic-night/dataset/1
- **Lokasi rekaman:** Jl. Diponegoro Musi Utara, Surabaya
- **Durasi data:** 21 hari × 8 jam (06.00–09.00 & 15.00–20.00 WIB)
- **Pemotongan video:** menggunakan CapCut
- **Training model malam:** Kaggle Notebooks, YOLOv8s, 50 epoch, batch=32, workers=4

### Konfigurasi Training YOLOv8 (Vehicle Detection, model utama)
- Base model: `yolov8m.pt`
- Dataset config: `Vehicle-Detection-2/data.yaml`
- epochs=50, batch=8, imgsz=640, device=0 (GPU)
- patience=10 (early stopping)
- Output folder: `model_hasil/kendaraan_indonesia/`
- **best.pt berasal dari epoch ke-23** (bukan epoch terakhir/33)
- Metrik best.pt: Precision=88,79%, Recall=90,57%, mAP@0.5=93,49%, mAP@0.5:0.95=84,89%
- File results tersedia di project: `results.csv` dan `results.png`

### Konfigurasi Training YOLOv8 (Traffic Night, eksperimen malam)
- Base model: `yolov8s.pt`
- Dataset config: `Traffic-night-1/data.yaml`
- epochs=50, batch=32, imgsz=640, device=0 (GPU Kaggle), workers=4
- patience=10 (early stopping)
- Output folder: `model_hasil/training_malam/`
- **Hasil: lebih buruk dari model utama** — Truk=168 dalam 10 menit (tidak realistis)
- Perbandingan: best.pt → Motor=9, Mobil=103, Total=113 vs best-malam.pt → Motor=4, Mobil=265, Truk=168, Total=466

### Kolom Dataset Utama (output_gabungan_frekuensinq1__catatan.csv)
`Hari, Jam, Menit, Motor, Mobil, Bus, Truk, Total_Kendaraan, Tingkat_Kepadatan, Catatan`
- `Tingkat_Kepadatan` = frekuensi Nq1 (0–10), **bukan** label kelas final
- `Catatan` = "ramai lancar" untuk 158 baris, kosong untuk sisanya

---

## 6. STRUKTUR OUTPUT FILES (Ada di Komputer Mahasiswa)

Semua file output ada di folder `skripsi_output.zip` yang sudah didownload dari chat ini.

```
skripsi_bab4_eda/
├── BAB_4_DRAFT.md          ← 889 baris (sudah diupload ke project)
├── BAB_5_DRAFT.md          ← 326 baris (sudah diupload ke project)
├── BAB_6_DRAFT.md          ← 42 baris (sudah diupload ke project)
├── PANDUAN_FILE_OUTPUT.md  ← mapping gambar/tabel → nama file → script
├── scripts/
│   ├── 01_eda.py           ← EDA → output: 01_eda/
│   ├── 02_preprocessing.py ← Preprocessing → output: 02_preprocessing/
│   ├── 03_modelling.py     ← GridSearchCV RF+SVM → output: 03_modelling/
│   └── 04_comparison.py    ← Komparasi 4 model → output: 04_comparison/
├── 01_eda/                 ← 9 PNG + 2 CSV (plot EDA)
├── 02_preprocessing/       ← dataset_preprocessed.csv
├── 03_modelling/           ← model.pkl (×4), gridsearch CSV, CM PNG, dll
└── 04_comparison/          ← grouped bar, CM 4 panel, metrik per kelas
```

Untuk mereproduksi output, jalankan urutan:
```bash
python3 scripts/01_eda.py
python3 scripts/02_preprocessing.py
python3 scripts/03_modelling.py
python3 scripts/04_comparison.py
```
Sesuaikan `INPUT_PATH` / `DATA_PATH` di setiap script dengan lokasi file di komputer Anda.

---

## 6b. REVISI DRAFT BAB 4 YANG SUDAH DILAKUKAN (di chat ini)

1. **Sub-bab 4.2.1 — Konfigurasi training:** Tabel konfigurasi Vehicle Detection dan Traffic Night sudah diisi dengan data aktual dari kode Python.
2. **Sub-bab 4.2.1 — Metrik evaluasi YOLO:** Tabel 4.3 baru berisi metrik best.pt dari epoch 23 (bukan last row). mAP@0.5=93,49%, mAP@0.5:0.95=84,89%.
3. **Sub-bab 4.2.1 — Traffic Night:** Narasi diubah dari "tidak dipakai karena waktu" → "sudah dicoba, hasilnya lebih buruk (Truk=168), diputuskan tidak dipakai". Tabel perbandingan best.pt vs best-malam.pt disertakan.
4. **Sub-bab 4.2.1 — Model COCO:** Poin keterbatasan diperjelas dengan angka konkret (Bus=111 vs Bus=24). Tabel perbandingan COCO vs Vehicle Detection disertakan.
5. **Sub-bab 4.2.2 — Interval 10 menit:** Kalimat "didasarkan pada PKJI/HCM" diubah → pertimbangan praktis pengamatan, PKJI/HCM ditemukan belakangan sebagai validasi teoritis.
6. **Sub-bab 4.4 — Labeling:** Narasi diubah sesuai kronologi sebenarnya: bingung dengan Tabel 3.8 → kembangkan pendekatan sendiri → temukan Nq1/cycle failure di PKJI/HCM → divalidasi Pak Tommi Firman.
7. **Penomoran tabel:** Dirapikan ulang total. Sekarang urut Tabel 4.1–4.29 tanpa duplikat.

## 7. YANG PERLU DIKERJAKAN DI CHAT BARU

Prioritas yang disarankan (berurutan):

1. **Lengkapi TODO di Bab 4** (sub-bab 4.1–4.3 dan 4.9) setelah data YOLO/MAPE/screenshot web siap
2. **Lakukan pengujian SUS** → isi sub-bab 5.5 di draft Bab 5
3. **Integrasikan model.pkl ke web Flask** (ganti dummy data)
4. **Revisi Bab 3** — update Tabel 3.10 & 3.11 dengan grid Opsi B-Slim + paragraf justifikasi
5. **Convert markdown → docx** untuk semua Bab 4–6 setelah review final

---

## 8. CATATAN UNTUK CLAUDE DI SESI BARU

- Semua keputusan teknis di bagian 3 sudah **final dan tidak perlu didiskusikan ulang**
- Draft Bab 4–6 sudah tersedia di project — jangan tulis ulang dari nol, cukup revisi/lengkapi
- Korelasi negatif di EDA bukan kesalahan — sudah dianalisis dan dijelaskan di Bab 5
- `Tingkat_Kepadatan` di kolom CSV = angka Nq1 (numerik), bukan label kelas. Label kelas ada di `Label_S1` dan `Label_S2` (hanya ada di `dataset_preprocessed.csv`)
- Grid hyperparameter yang dipakai adalah Opsi B-Slim (lebih kecil dari Bab 3 asli) — ini perlu direvisi di Bab 3 nanti
- Model terbaik = RF Skenario 1, disimpan di `03_modelling/rf_scenario1/model.pkl`
