# HANDOFF SESSION 1 → SESSION 2
# Integrasi Hasil Modelling ke Web SIKEDAT

**Tanggal session ini:** 2026-06-18
**Branch aktif:** `dani/main/integrasi-model`
**Status:** Analisis selesai — belum ada eksekusi kode apapun.

---

## KONTEKS PROYEK

Sistem web SIKEDAT (Sistem Klasifikasi Kepadatan Data) untuk Dinas Perhubungan Surabaya.
Skripsi: klasifikasi tingkat kepadatan lalu lintas (Rendah/Sedang/Tinggi) dari video CCTV
Jalan Diponegoro Musi Utara, Surabaya.

**Stack:** Flask, SQLite, scikit-learn (RF + SVM), pandas, joblib
**Pipeline data:** Video CCTV → YOLOv8 + DeepSORT → CSV counts → Web (classify → validasi → retrain)

---

## KONDISI SAAT INI

Web sudah berjalan dengan **data dummy** (672 baris, skala Motor 28-78).
Tahap modelling sudah selesai, menghasilkan model terbaik: **RF Skenario 1**.
Goal session ini: selaraskan web dengan hasil modelling yang sudah ada.

---

## TEMUAN ANALISIS (3 MASALAH KRITIS)

### Masalah 1 — Fitur & Preprocessing Berbeda Total

| Aspek | Web sekarang (SALAH) | Modelling (BENAR) |
|---|---|---|
| Encoding Hari | LabelEncoder → 1 kolom integer | One-Hot Encoding → 7 kolom binary |
| Jumlah fitur | 8 | 14 |
| Scaling RF | MinMaxScaler (salah, RF tidak butuh) | Tidak pakai scaler |
| Scaling SVM | MinMaxScaler terpisah | StandardScaler di dalam Pipeline |

Urutan 14 fitur yang WAJIB dijaga persis (dari dataset_preprocessed.csv):
```
Jam, Menit, Hari_Jumat, Hari_Kamis, Hari_Minggu, Hari_Rabu,
Hari_Sabtu, Hari_Selasa, Hari_Senin, Motor, Mobil, Bus, Truk, Total_Kendaraan
```

### Masalah 2 — Skala Data Dummy vs Real Berbeda 10-15x

- Dummy: Motor 28–78, Total_Kendaraan 42–113
- Real:  Motor 300–866, Total_Kendaraan 376–1017

### Masalah 3 — Retrain Pakai GridSearchCV Ulang (Salah)

`_do_retrain()` di app.py memanggil `train_models.py` yang menjalankan GridSearchCV penuh.
Harusnya pakai **fixed best params** dari hasil modelling.

---

## KEPUTUSAN YANG SUDAH DITETAPKAN

1. **Model aktif** = RF Skenario 1 (best model overall)
   - Source: `modelling/3_modelling/output/rf_scenario1/model.pkl`
   - Params: `n_estimators=200, max_depth=10, min_samples_split=2, min_samples_leaf=1, class_weight='balanced'`
   - Performa: Accuracy 73.30%, F1-weighted 72.99% (test set, 877 baris real)

2. **Preprocessing**: OHE untuk Hari, tidak pakai scaler untuk RF

3. **Retrain**: Fixed params RF S1, tanpa GridSearchCV, OHE untuk Hari

4. **Initial dataset**: 877 baris dari data real (bukan dummy) dimasukkan ke DB sebagai `status_validasi='validated'`

5. **Database schema**: TIDAK BERUBAH — schema sudah sesuai, cukup hapus data dummy

---

## SEMUA FILE YANG AKAN DIUBAH

### DIHAPUS:
```
models/le_hari.pkl          ← diganti OHE
models/le_label.pkl         ← tidak diperlukan (RF prediksi string langsung)
models/scaler.pkl           ← RF tidak butuh scaler
models/rf_model.pkl         ← dilatih dari dummy, tidak valid
models/svm_model.pkl        ← dilatih dari dummy, tidak valid
generate_dummy_data.py      ← tidak dipakai lagi
dataset_dummy_berlabel.csv  ← diganti dataset_tervalidasi.csv
dataset_dummy_input.csv     ← tidak dipakai
migrate_db.py               ← kolom sudah ada di schema, tidak relevan
```

### DIBUAT/DIGANTI ISINYA:
```
models/model_aktif.pkl      ← COPY dari modelling/3_modelling/output/rf_scenario1/model.pkl
models/metadata.json        ← TULIS ULANG (RF S1: params, 14 fitur, metrik)
```

### DITULIS ULANG:
```
ml_utils.py                 ← OHE untuk Hari, 14 fitur, hapus scaler/encoder lama
train_models.py             ← Fixed params RF S1, OHE, tanpa GridSearchCV, tanpa MinMaxScaler
```

### DIEDIT (perubahan kecil):
```
app.py:
  - setelah pd.read_csv() di route /classifier:
    tambah: df.columns = df.columns.str.lower()
  - _do_retrain(): ganti nama file 'dataset_dummy_berlabel.csv' → 'dataset_tervalidasi.csv'
  - _do_retrain(): sederhanakan logika ambil metrik dari metadata (struktur berubah)
```

### DIBUAT BARU:
```
import_initial_dataset.py   ← script satu kali, import 877 baris ke DB
```

---

## DATABASE

**Schema tabel dataset:** TIDAK BERUBAH (sudah sesuai)

**Yang perlu dilakukan:**
1. Hapus semua data dummy: `DELETE FROM dataset`
2. Jalankan `import_initial_dataset.py` untuk masukkan 877 baris real

**Format kolom tabel dataset (ringkasan):**
```
id, hari, jam, menit, motor, mobil, bus, truk, total_kendaraan,
tingkat_kepadatan, status_validasi, label_final, nama_file,
tanggal, batch_id, classified_by, validated_by, created_at, validated_at
```

---

## STATUS SAAT HANDOFF INI DIBUAT

User sedang **membuat CSV initial dataset** dengan format:
```
hari,jam,menit,motor,mobil,bus,truk,total_kendaraan,tingkat_kepadatan
```

File akan diletakkan di: `c:\laragon\www\skripsi\dataset_real_berlabel.csv`

**Sumber data:**
- File: `modelling/labeled_frekuensi-cyclefailure/output_gabungan_frekuensi(S2).csv`
- Kolom `Tingkat_Kepadatan` di file itu adalah nilai Nq1 (integer), sudah dikonversi
  ke label S1 oleh user sebelum disimpan ke CSV:
  - Nq1 = 0          → 'Rendah'
  - Nq1 = 1 atau 2   → 'Sedang'
  - Nq1 >= 3         → 'Tinggi'

**Kolom yang TIDAK perlu ada di CSV** (import script set otomatis):
- `label_final` → copy dari `tingkat_kepadatan`
- `status_validasi` → 'validated'
- `batch_id` → NULL (batch_id untuk seri upload web, bukan data awal)
- `classified_by`, `validated_by` → NULL
- `created_at`, `validated_at` → timestamp saat import

---

## URUTAN EKSEKUSI SESSION BERIKUTNYA

Setelah user selesai membuat `dataset_real_berlabel.csv`:

```
STEP 1  — Hapus file lama yang tidak terpakai (pkl, csv dummy, py dummy)
STEP 2  — Copy rf_scenario1/model.pkl → models/model_aktif.pkl
STEP 3  — Tulis ulang ml_utils.py (OHE, 14 fitur, tanpa scaler/encoder lama)
STEP 4  — Tulis ulang train_models.py (fixed params RF S1, OHE, tanpa GridSearchCV)
STEP 5  — Edit 3 titik di app.py (lowercase CSV, rename file dataset, fix metadata)
STEP 6  — Buat models/metadata.json baru
STEP 7  — Buat import_initial_dataset.py
STEP 8  — Jalankan: hapus data dummy dari DB, lalu jalankan import_initial_dataset.py
STEP 9  — Test end-to-end: upload CSV dari output_ekstraksi/ → klasifikasi → validasi
```

---

## REFERENSI FILE MODELLING PENTING

```
modelling/3_modelling/output/rf_scenario1/
  model.pkl                      ← MODEL YANG DIPAKAI
  02_best_params.txt             ← params lengkap RF S1
  04_classification_report.txt   ← Rendah: F1=0.83, Sedang: F1=0.50, Tinggi: F1=0.73

modelling/3_modelling/output/ringkasan_4_model.csv
  ← perbandingan semua 4 model (RF S1 terbaik)

modelling/4_evaluasi/output/RINGKASAN_KOMPARASI.txt
  ← RF S1: Test Acc=0.7330, Test F1_weighted=0.7299, CV F1=0.7166

modelling/2_preprocessing/output/dataset_preprocessed.csv
  ← referensi urutan 14 fitur dan nama kolom OHE yang harus diikuti

modelling/labeled_frekuensi-cyclefailure/output_gabungan_frekuensi(S2).csv
  ← sumber 877 baris data real (Nq1 + Catatan)
```

---

## CATATAN TEKNIS PENTING

1. **Nama kolom OHE harus persis**: `Hari_Jumat`, `Hari_Kamis`, `Hari_Minggu`, `Hari_Rabu`,
   `Hari_Sabtu`, `Hari_Selasa`, `Hari_Senin` (urutan alfabetis, prefix kapital `Hari_`)

2. **Retrain export dari DB**: `_do_retrain()` mengekspor kolom lowercase (`hari`, bukan `Hari`).
   `train_models.py` baru harus normalisasi ke Title case sebelum OHE.

3. **Halaman Prediksi publik** (`/prediksi`): `predict_single()` pakai nilai rata-rata
   hardcoded untuk motor/mobil/bus/truk. Nilai ini masih dari dummy — perlu diupdate
   ke rata-rata dari data real (dari dataset_preprocessed.csv atau output_gabungan).

4. **Model dari modelling pakai `pickle`**, bukan `joblib`. Di ml_utils.py saat ini pakai
   `joblib.load()`. Perlu dicek format model.pkl dari rf_scenario1 dan sesuaikan loader.

5. **Jam yang dicover data real**: 6,7,8 (pagi) + 15,16,17,18,19 (sore-malam)
   — sama dengan dummy, tidak perlu ubah filter jam di app.py.
