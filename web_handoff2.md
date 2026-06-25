# HANDOFF SESSION 2 → SESSION 3
# Integrasi Model Selesai — Perbaikan UX Validasi

**Tanggal session ini:** 2026-06-18
**Branch aktif:** `dani/main/integrasi-model`
**Status:** Integrasi model selesai penuh. Web berjalan dengan data real dan model RF S1.

---

## RINGKASAN SESSION INI

Dua pekerjaan utama diselesaikan:

1. **Integrasi model RF S1 ke web** — seluruh 9 step dari handoff sebelumnya dieksekusi:
   - File dummy lama dihapus, preprocessing diubah ke OHE, model dilatih ulang dari data real
   - DB dibersihkan dan diisi 877 baris data real (semua `status_validasi='validated'`)

2. **Perbaikan halaman validasi** — 3 perubahan:
   - Tampilan antrian batch (warna teks + info classifier)
   - Bugfix: label yang dikoreksi kini otomatis bisa disimpan
   - Tambah tombol `✓ Valid` per baris

---

## STATE SISTEM SAAT INI

### Model Aktif
```
File       : models/model_aktif.pkl
Algoritma  : Random Forest — Skenario 1
Params     : n_estimators=200, max_depth=10, min_samples_split=2,
             min_samples_leaf=1, class_weight='balanced', random_state=42
Accuracy   : 73.30%
F1-weighted: 72.99%
CV F1      : 71.38%
Dilatih    : 2026-06-18 (dari dataset_real_berlabel.csv, 877 baris)
Fitur (14) : Jam, Menit, Hari_Jumat, Hari_Kamis, Hari_Minggu, Hari_Rabu,
             Hari_Sabtu, Hari_Selasa, Hari_Senin, Motor, Mobil, Bus, Truk,
             Total_Kendaraan
```

### Database (`sikedat.db`)
```
Total baris : 878  (877 real + 1 dari testing validasi)
validated   : 877
corrected   : 1   (dari testing sesi ini)
pending     : 0
Rendah      : 464
Sedang      : 205
Tinggi      : 209
RetrainHistory: 0 record (retrain belum pernah dijalankan dari web)
```

### File Penting
```
models/
  model_aktif.pkl     ← model RF S1 aktif
  metadata.json       ← params + metrik model aktif

dataset_real_berlabel.csv  ← 877 baris sumber data real (sudah ada di disk)

train_initial_model.py     ← script sekali jalan (sudah dijalankan, bisa dihapus)
import_initial_dataset.py  ← script sekali jalan (sudah dijalankan, bisa dihapus)
train_models.py            ← dipakai web saat retrain
ml_utils.py                ← preprocessing + prediksi
app.py                     ← Flask routes
```

---

## PERUBAHAN FILE SESSION INI

### Dihapus
```
models/le_hari.pkl
models/le_label.pkl
models/scaler.pkl
models/rf_model.pkl
models/svm_model.pkl
generate_dummy_data.py
migrate_db.py
data/dataset_dummy_berlabel.csv
data/dataset_dummy_input.csv
```

### Dibuat Baru
```
train_initial_model.py      ← script sekali jalan, bisa dihapus
import_initial_dataset.py   ← script sekali jalan, bisa dihapus
```

### Ditulis Ulang
```
ml_utils.py
  - Hapus load_scaler(), load_encoders()
  - OHE untuk Hari (7 kolom binary, prefix Hari_)
  - 14 fitur (urutan wajib dijaga)
  - predict_single(): avg_per_jam dari data real (bukan dummy)
  - Tidak ada MinMaxScaler

train_models.py
  - Input: dataset_tervalidasi.csv (bukan dataset_dummy_berlabel.csv)
  - RF S1 fixed params, tanpa GridSearchCV, tanpa SVM
  - OHE untuk Hari (kolom lowercase dari DB → Title case → OHE)
  - Output: model_aktif.pkl + metadata.json
```

### Diedit
```
app.py:
  - /classifier route: tambah df.columns = df.columns.str.lower() setelah pd.read_csv()
  - _do_retrain(): ganti 'dataset_dummy_berlabel.csv' → 'dataset_tervalidasi.csv'
  - _do_retrain(): sederhanakan metadata reading (chosen = meta.get('rf', {}))
  - /validasi route: tambah classified_by_id ke query antrian, lookup nama user

templates/validasi.html:
  - Antrian batch: warna teks conditional (heading untuk batch aktif, muted untuk menunggu)
  - Antrian batch: tambah "Oleh: <nama_lengkap>" dari classified_by
  - onLabelChange(): bugfix — koreksi label otomatis masuk approvedSet
  - bulkSetujui(): badge emoji konsisten, disable btnValid per baris
  - submitValidasi(): update pesan alert
  - Tabel: tambah kolom "Aksi" + tombol "✓ Valid" per baris
  - Tambah fungsi approveRow(id)
  - Empty state: colspan 14 → 15
```

---

## DETAIL TEKNIS PENTING

### Preprocessing (OHE)

Urutan 14 fitur WAJIB dijaga persis — model pkl sudah di-fit dengan urutan ini:
```python
HARI_COLS = ['Hari_Jumat', 'Hari_Kamis', 'Hari_Minggu', 'Hari_Rabu',
             'Hari_Sabtu', 'Hari_Selasa', 'Hari_Senin']
FITUR = ['Jam', 'Menit'] + HARI_COLS + ['Motor', 'Mobil', 'Bus', 'Truk', 'Total_Kendaraan']
```

### Alur Retrain

1. User klik Retrain di web → `_do_retrain()` di app.py
2. Export data `validated`+`corrected` dari DB → simpan ke `dataset_tervalidasi.csv`
3. Jalankan `train_models.py` via subprocess
4. `train_models.py` baca `dataset_tervalidasi.csv`, normalisasi kolom lowercase→Title case, OHE, train RF S1
5. Simpan `model_aktif.pkl` + `metadata.json`

### Label yang Dipakai Retrain

`_do_retrain()` mengekspor kolom `tingkat_kepadatan` (bukan `label_final`).
Keduanya selalu sama nilainya setelah validasi, karena `save_validated()` mengupdate kedua kolom sekaligus.

### Format Metadata JSON

```json
{
  "best_algo": "Random Forest",
  "scenario": "S1",
  "n_train": 701,
  "n_test": 176,
  "features": [...14 fitur...],
  "params": { RF S1 params },
  "rf": {
    "accuracy": 0.733,
    "precision": 0.7318,
    "recall": 0.733,
    "f1_score": 0.7299,
    "cv_f1": 0.7138
  },
  "label_classes": ["Rendah", "Sedang", "Tinggi"],
  "trained_at": "ISO timestamp"
}
```

app.py membaca: `meta.get('best_algo')`, `meta.get('n_train')`, `meta.get('n_test')`, `meta.get('rf', {})`.

---

## FLOW VALIDASI (SUDAH DIPERBAIKI)

Ada 3 cara untuk menandai baris siap disimpan:

| Cara | Mekanisme | Badge |
|------|-----------|-------|
| Klik `✓ Valid` per baris | `approveRow(id)` | ✅ Valid |
| Ubah label dropdown | `onLabelChange()` auto-add | ✏️ Dikoreksi |
| Checklist + "Setujui Terpilih" | `bulkSetujui()` | ✅ Valid |

Klik "Simpan Terpilih" → POST ke `/validasi/save` → simpan ke DB.

---

## YANG BELUM DIKERJAKAN / PERLU DICEK

1. **Test retrain dari web** — belum pernah dijalankan dengan data real.
   - Pastikan tombol Retrain di `/retrain` berhasil menghasilkan `dataset_tervalidasi.csv` dan memanggil `train_models.py`
   - RetrainHistory saat ini masih 0 record

2. **Script satu kali jalan** bisa dihapus jika sudah tidak diperlukan:
   - `train_initial_model.py`
   - `import_initial_dataset.py`

3. **Halaman `/prediksi` publik** — fungsional, tapi belum ditest secara menyeluruh dengan semua kombinasi hari/jam.

4. **Data baris ke-878** (dari testing validasi sesi ini) — asalnya dari upload CSV testing. Jika ingin DB bersih hanya 877 baris asli, bisa dihapus manual.

---

## CARA JALANKAN WEB

```bash
cd c:/laragon/www/skripsi
python app.py
```

Login: `admin` / `admin123`, `analis_dishub` / `analis123`, `staff_dishub` / `staff123`

---

## REFERENSI FILE OUTPUT_EKSTRAKSI

File CSV siap untuk testing classifier ada di:
```
modelling/output_ekstraksi/
  *.csv   ← format: No_Hari_JamAwal-JamAkhir.csv
            kolom: Hari, Jam, Menit, Motor, Mobil, Bus, Truk, Total_Kendaraan
```
Format kolom sudah lowercase sesuai yang diharapkan web (app.py sudah lowercase semua kolom CSV upload).
