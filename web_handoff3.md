# HANDOFF SESSION 3 → SESSION 4
# Perbaikan UI/UX & Bug Fix Multi-Halaman

**Tanggal session ini:** 2026-06-19
**Branch aktif:** `dani/main/integrasi-model`
**Status:** Semua perubahan selesai dieksekusi. Web berjalan normal (import OK).

---

## RINGKASAN SESSION INI

Session ini tidak menambah fitur baru yang fundamental — fokus pada **perbaikan bug, cleanup UI, dan penambahan informasi yang lebih akurat** di seluruh halaman web SIKEDAT.

Dua fase pekerjaan:
1. **Analisis & diskusi** — semua poin dianalisis dulu sebelum eksekusi
2. **Eksekusi 18 poin perubahan** di 9 file (1 file baru dibuat)

---

## PERUBAHAN PER HALAMAN

### A. Halaman Prediksi (`ml_utils.py`)

**Bug fix: Probabilitas tampil 7490%**

Root cause: `classify_dataframe()` menyimpan proba dalam % (×100), lalu `predict_single()` mengembalikan nilai tersebut apa adanya, sedangkan template mengalikan ×100 lagi.

**File:** `ml_utils.py` baris 132
```python
# SEBELUM
proba = {cls: float(row.get(f'proba_{cls.lower()}', 0.0)) for cls in classes}

# SESUDAH
proba = {cls: float(row.get(f'proba_{cls.lower()}', 0.0)) / 100 for cls in classes}
```

---

### B. Halaman Dashboard (`templates/dashboard.html`)

**Bug fix: Heatmap semua sel berwarna oranye**

Root cause: `maxV = 120` hardcoded dari era data dummy (total kendaraan ~113). Data real bernilai 376–1017, sehingga semua sel dapat ratio = 1.0 → semua merah/oranye.

**File:** `templates/dashboard.html`
```javascript
// SEBELUM
const maxV = 120;

// SESUDAH
const allVals = Object.values(heatValues).filter(v => v != null);
const maxV = allVals.length > 0 ? Math.max(...allVals) : 1000;
```

---

### C. Halaman Retrain (`templates/retrain_model.html` + `app.py` + `models.py` + DB)

#### C1. Template — Section "Data untuk Retrain"
- **Dihapus:** Card "Penambahan Data Baru" (`n_new_data` = data `pending` yang belum divalidasi — tidak relevan di konteks retrain)
- **Tetap:** Card "Data Tervalidasi" dan "Total Dataset"

#### C2. Template — Section "Konfigurasi Retrain"
- **Dihapus:** 2 info box "Split Data (80/20)" dan "Cross-Validation (5-Fold)" — tidak perlu ditampilkan
- **Tetap:** Algoritma (Random Forest) + chip hyperparameter RF S1
- **Fix:** Fallback nama algoritma dari "Model Terbaik" → "Random Forest"

Catatan: dropdown split/CV sudah dihapus di session sebelumnya (awal session ini), diganti info box; session ini info box itu juga dihapus.

#### C3. Template — Tabel Riwayat Retrain (4 bug sekaligus)

| Bug | Sebelum | Sesudah |
|---|---|---|
| F1-Score kosong | `h.f1` (tidak ada) | `h.f1_score` |
| Badge status salah | `h.active` (tidak ada) | `h.is_active` |
| Tombol Aktifkan salah | `h.active` | `h.is_active` |
| Nilai float mentah | `0.733` | `73.30%` |
| Tanggal mentah | datetime object | `18 Jun 2026, 12:30` |
| Kolom Durasi | tidak ada | `h.duration_seconds` → `12.4 dtk` |
| colspan empty state | `8` | `9` (sesuai jumlah kolom baru) |

#### C4. Model (`models.py`)
```python
# Tambah di class RetrainHistory:
duration_seconds = db.Column(db.Float, nullable=True)
```

#### C5. Migrasi DB
```sql
ALTER TABLE retrain_history ADD COLUMN duration_seconds FLOAT;
```
Sudah dijalankan. Kolom ada di DB. Record retrain sebelumnya (v1.0) masih NULL — akan terisi otomatis saat retrain berikutnya.

#### C6. Logic retrain (`app.py` — fungsi `_do_retrain()`)
- Tambah `import time`
- Hitung durasi: `t_start = time.time()` sebelum subprocess, `duration_seconds = round(time.time() - t_start, 1)` sesudah
- Simpan ke `RetrainHistory.duration_seconds`
- Flash message sekarang: `"Retrain berhasil! Model v1.1 (Random Forest) — Akurasi: 73.30% — Selesai dalam 14.2 detik"`

---

### D. Halaman Beranda (`templates/index.html`)

**Dihapus dua section:**
1. **"Pola Kepadatan — Data Terakhir Diproses"** — chart ini selalu kosong karena 877 baris data awal diimport tanpa `batch_id`, sehingga query `filter(batch_id.isnot(None))` tidak menemukan apa-apa. Script chart `chartTerakhir` juga dihapus dari block JS.
2. **"Log Aktivitas Terbaru"** — dipindah ke halaman tersendiri (lihat poin E). Isinya sebelumnya adalah data dummy/hardcoded bukan dari DB.

Layout beranda sekarang: Stat cards → Komposisi Kendaraan Harian → Distribusi Kepadatan → Aksi Cepat.

---

### E. Halaman Log Aktivitas (BARU)

**File baru:** `templates/aktivitas.html`
**Route baru di `app.py`:** `@app.route('/aktivitas')` dengan decorator `@login_required_only`
**Sidebar:** Tambah menu "Log Aktivitas" di `base.html` — hanya muncul jika `current_user.is_authenticated`

Data aktivitas diambil real dari DB, tanpa tabel baru:

| Tipe | Sumber Data | Info yang Ditampilkan |
|---|---|---|
| Klasifikasi | `Dataset` group by `batch_id` | Nama file, jumlah baris, oleh siapa |
| Validasi | `Dataset` group by `validated_by` + tanggal | Jumlah baris, berapa yang dikoreksi, oleh siapa |
| Retrain | `RetrainHistory` | Versi, algoritma, data latih, akurasi, durasi, oleh siapa |

Semua diurutkan by waktu terbaru. Maksimal 20 entri klasifikasi, 20 entri validasi, 10 entri retrain.

---

## FILE YANG BERUBAH

| File | Jenis Perubahan |
|---|---|
| `ml_utils.py` | Fix bug (1 baris) |
| `templates/dashboard.html` | Fix bug (1 baris JS) |
| `templates/retrain_model.html` | Hapus 2 section, fix 7 bug di tabel |
| `models.py` | Tambah 1 kolom |
| `sikedat.db` | Migrasi (tambah kolom `duration_seconds`) |
| `app.py` | Fix `activate_model` decorator, tambah durasi di `_do_retrain()`, tambah route `/aktivitas` |
| `templates/index.html` | Hapus 2 section + script JS |
| `templates/base.html` | Tambah menu sidebar Log Aktivitas |
| `templates/aktivitas.html` | **DIBUAT BARU** |

---

## STATE SISTEM SAAT INI

### Database
```
Tabel dataset        : 878 baris (877 real + 1 dari testing)
Tabel retrain_history: 1 record (v1.0, duration_seconds = NULL)
Tabel users          : 3 user (admin, analis_dishub, staff_dishub)
```

### Model Aktif
```
File       : models/model_aktif.pkl
Algoritma  : Random Forest — Skenario 1
Accuracy   : 73.30% | F1-weighted: 72.99%
Fitur (14) : Jam, Menit, Hari_Jumat..Hari_Senin, Motor, Mobil, Bus, Truk, Total_Kendaraan
Dilatih    : 2026-06-18 (877 baris)
```

### Sidebar (setelah perubahan session ini)
```
Menu Utama     : Beranda, Prediksi Kepadatan
Login (semua)  : Dashboard & Analitik, Log Aktivitas
Akses Penuh    : Klasifikasi Data, Validasi Data, Retrain Model
Admin Only     : Manajemen User
```

---

## YANG BELUM DIKERJAKAN / PERLU DICEK

1. **Record retrain v1.0 `duration_seconds` = NULL** — normal, karena dibuat sebelum fitur ini. Akan terisi otomatis saat retrain berikutnya. Di tabel riwayat akan tampil "—" untuk record lama.

2. **Test visual halaman Log Aktivitas** — belum ditest langsung di browser. Pastikan query berjalan dan data tampil benar.

3. **Test probabilitas prediksi** — fix sudah diterapkan (`/100`), tapi belum diverifikasi di browser bahwa angka sekarang benar (harusnya: Rendah ~17%, Sedang ~74%, Tinggi ~9% untuk contoh Selasa 08:50).

4. **Test heatmap dashboard** — fix sudah diterapkan (maxV dinamis), tapi belum diverifikasi visual bahwa gradasi warna kini benar (biru gelap → merah).

5. **Beranda: layout card "Komposisi Kendaraan"** — sebelumnya ada di kiri (grid-2), sekarang full-width (grid-1) karena chart sebelah kiri dihapus. Perlu dicek apakah tampilannya oke atau perlu penyesuaian lebar.

6. **Fitur "data belum diretrain" counter** — diputuskan tidak dikerjakan session ini. Perlu tambah kolom `dipakai_retrain BOOLEAN` + migrasi + update logic `_do_retrain()` jika suatu saat ingin diimplementasi.

---

## CARA JALANKAN WEB

```bash
cd c:/laragon/www/skripsi
python app.py
```

Login: `admin` / `admin123`, `analis_dishub` / `analis123`, `staff_dishub` / `staff123`

Halaman Log Aktivitas: `http://localhost:5000/aktivitas` (harus login)
