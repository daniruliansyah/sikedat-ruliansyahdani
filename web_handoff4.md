# HANDOFF SESSION 4 → SESSION 5
# Bug Fix, Fitur Baru, dan Penulisan Dokumen Skripsi

**Tanggal session ini:** 2026-06-20
**Branch aktif:** `dani/main/integrasi-model`
**Status:** Semua perubahan selesai dieksekusi. Web berjalan normal.

---

## RINGKASAN SESSION INI

Session ini melanjutkan dari handoff3. Pekerjaan terbagi menjadi empat kelompok:

1. **Penyelesaian item "YANG BELUM DIKERJAKAN" dari handoff3** — 3 bug fix + 1 tambahan
2. **Fitur baru** — Log Aktivitas default "Hari Ini" + halaman Data Observasi baru
3. **Revisi kecil** — greeting beranda dinamis + logout redirect
4. **Dokumen skripsi** — mengisi BAB 4.13 dan BAB 5.5

---

## PERUBAHAN PER FILE

### `templates/base.html`
- **Fix layout Log Aktivitas** (baris flash messages): tambah `flex: none` ke div flash messages.
  - Root cause: dua elemen `class="page-content"` keduanya punya `flex: 1`, menyebabkan flash div yang kosong menelan 50% tinggi viewport → konten halaman dimulai dari tengah.
  - Fix: `style="padding-bottom: 0; padding-top: 0; flex: none;"` pada div flash messages.
- **Tambah menu "Data Observasi"** di sidebar (di atas "Log Aktivitas"), hanya muncul untuk `{% if current_user.is_authenticated %}`.

### `templates/dashboard.html`
- **Fix heatmap warna sel tidak sesuai legend**: formula warna lama interpolasi 2-titik (gelap → oranye langsung), sekarang interpolasi 3-titik sesuai legend:
  - ratio 0.0 → `#0F2240` (biru gelap)
  - ratio 0.5 → `#1A6FFF` (biru terang)
  - ratio 1.0 → `#EF4444` (merah)
- **Fix teks heatmap semua putih**: sebelumnya `color` hanya putih jika `ratio > 0.45`, sekarang selalu `#fff` jika `val != null`.

### `templates/index.html`
- **Fix card "Menunggu Validasi" tampil ke public**: wrapped dengan `{% if current_user.is_authenticated %}`.
- **Grid stat cards kondisional**: `grid-3` jika login, `grid-2` jika tidak (agar layout tetap rapi tanpa card ke-3).
- **Greeting beranda dinamis**:
  - Public (tidak login): `Selamat Datang 👋`
  - Admin: `Selamat Datang, Admin [nama_lengkap] 👋`
  - Analis: `Selamat Datang, Analis [nama_lengkap] 👋`
  - Staff: `Selamat Datang, Staff [nama_lengkap] 👋`
  - Menggunakan `current_user.role.nama | capitalize` + `current_user.nama_lengkap`.

### `templates/aktivitas.html`
- **Toggle filter periode** di header card: dua pill "Hari Ini" dan "Semua". Pill aktif diberi background `var(--primary)`.
- **Judul card dinamis**: "Aktivitas Hari Ini" atau "Semua Aktivitas" sesuai filter aktif.
- **Empty state berbeda**: jika "Hari Ini" kosong → pesan ramah + link cepat ke "Semua".

### `app.py`
- **Route `/aktivitas`**: tambah `periode = request.args.get('periode', 'hari_ini')`. Jika `hari_ini`, filter masing-masing query (klasifikasi, validasi, retrain) by `func.date(...) == date.today()`. Pass `periode` ke template.
- **Route `/data-observasi` (BARU)**:
  - Decorator: `@login_required_only`
  - Filter: `?status=semua|pending|tervalidasi` (default `semua`)
  - Pagination: 50 baris/halaman via `.paginate()`
  - Count cards: total_all, count_pending, count_tervalidasi (`validated` + `corrected`)
  - User lookup: `classified_by` dan `validated_by` → `nama_lengkap` via `user_map`

### `templates/data_observasi.html` — **FILE BARU**
- 3 card filter (Semua Data, Pending, Tervalidasi) — card aktif diberi border highlight warna sesuai state.
- Tabel 15 kolom: No, Hari, Jam, Menit, Motor, Mobil, Bus, Truk, Total, Kepadatan, Status, Nama File, Diklasifikasi Oleh, Divalidasi Oleh, Tanggal.
- Badge status: Pending=warning, Validated=success, Corrected=info.
- `classified_by` / `validated_by` ditampilkan sebagai `nama_lengkap` (bukan ID).
- Pagination dengan `iter_pages()` — navigasi Prev/Next + nomor halaman.

### `auth.py`
- **Logout redirect**: sebelumnya ke `url_for('auth.login')`, sekarang ke `url_for('index')` (beranda publik).

---

## FILE BARU YANG DIBUAT

| File | Keterangan |
|---|---|
| `templates/data_observasi.html` | Halaman Data Observasi dengan filter + tabel + pagination |
| `JAWABAN_4.13_5.5.md` | Draft isi BAB 4.13 dan BAB 5.5 untuk skripsi |

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

### Sidebar (setelah session ini)
```
Menu Utama (semua)   : Beranda, Prediksi Kepadatan
Login (semua role)   : Dashboard & Analitik, Data Observasi, Log Aktivitas
Akses Penuh          : Klasifikasi Data, Validasi Data, Retrain Model
Admin Only           : Manajemen User
```

### Halaman & Route Lengkap
```
/                    → Beranda (publik)
/prediksi            → Prediksi Kepadatan (publik)
/auth/login          → Login (publik)
/auth/logout         → Logout → redirect ke /  (login required)
/dashboard           → Dashboard & Analitik (login)
/data-observasi      → Data Observasi (login)
/aktivitas           → Log Aktivitas (login, default: hari ini)
/classifier          → Klasifikasi Data (akses penuh)
/classifier/run      → Jalankan klasifikasi (akses penuh)
/classifier/download → Download hasil CSV (akses penuh)
/validasi            → Validasi & Koreksi (akses penuh)
/validasi/save       → Simpan validasi (akses penuh)
/validasi/import     → Import batch ke validasi (akses penuh)
/retrain             → Retrain Model (akses penuh)
/retrain/activate/v  → Aktifkan versi model (akses penuh)
/users               → Manajemen User (admin)
/users/create        → Buat user baru (admin)
/users/edit/<id>     → Edit user (admin)
/users/toggle/<id>   → Toggle aktif/nonaktif (admin)
```

---

## DOKUMEN SKRIPSI (JAWABAN_4.13_5.5.md)

File `JAWABAN_4.13_5.5.md` sudah dibuat di root project (sejajar `app.py`).

### Isi BAB 4.13 yang sudah ditulis:
- **4.13.1 Arsitektur Sistem**: penjelasan 3 lapisan MVC + alur data 8 tahap + tabel 19 route + tabel tumpukan teknologi
- **4.13.2 Implementasi UI**: 6 gambar (4.18–4.23) masing-masing dengan catatan URL screenshot + paragraf sebelum placeholder + `[TODO: Insert Gambar]` + paragraf deskripsi sesudah
- **4.13.3 Struktur Database**: 4 tabel lengkap (roles, users, dataset, retrain_history) dengan semua kolom + penjelasan relasi
- **4.13.4 Integrasi Model**: snippet kode load_model(), _ohe_hari(), classify_dataframe(), RF_PARAMS + penjelasan pipeline + alur retrain + kesimpulan

### Isi BAB 5.5 yang sudah ditulis:
- **5.5.1** Justifikasi Flask (4 alasan: integrasi Python ML, fleksibilitas, skala DISHUB, ekosistem extension)
- **5.5.2** Keputusan teknis: joblib vs pickle, pemisahan modul ML, retrain via subprocess, OHE manual, SQLite
- **5.5.3** 3 fitur unggulan dikaitkan Rumusan Masalah 3: Human-in-the-Loop, retrain terotomasi, dashboard multidimensi
- **5.5.4** 4 tantangan & solusi: preprocessing mismatch, skala data dummy vs real, GridSearchCV → fixed params, pengelolaan versi model

### Screenshot yang masih perlu diambil Mas untuk 4.13.2:
| Gambar | URL |
|---|---|
| Gambar 4.18 — Login | `http://localhost:5000/auth/login` (form kosong) |
| Gambar 4.19 — Klasifikasi | `http://localhost:5000/classifier` (form upload siap) |
| Gambar 4.20 — Dashboard | `http://localhost:5000/dashboard` (tanpa filter) |
| Gambar 4.21 — Validasi | `http://localhost:5000/validasi` (pastikan ada data pending) |
| Gambar 4.22 — Prediksi | `http://localhost:5000/prediksi` (isi form lalu submit, tangkap saat hasil tampil) |
| Gambar 4.23 — Retrain | `http://localhost:5000/retrain` (tampil normal) |

---

## YANG BELUM DIKERJAKAN / PERLU DICEK

1. **Screenshot untuk BAB 4.13.2** — semua placeholder `[TODO: Insert Gambar X.XX]` di `JAWABAN_4.13_5.5.md` masih perlu diisi screenshot oleh Mas. URL untuk setiap gambar sudah tercantum di tabel di atas.

2. **Nomor tabel di JAWABAN_4.13_5.5.md** — tabel route dan tabel teknologi masih menggunakan placeholder `Tabel 4.X`. Perlu disesuaikan dengan nomor tabel aktual di skripsi Mas.

3. **Baris ke-878 di DB** — satu baris ekstra dari testing session sebelumnya. Jika ingin DB bersih 877 baris, bisa dihapus manual (`DELETE FROM dataset WHERE id = 878`).

4. **`train_initial_model.py` dan `import_initial_dataset.py`** — kedua script "satu kali jalan" ini sudah tidak diperlukan lagi. Boleh dihapus untuk membersihkan direktori.

5. **Halaman `/data-observasi`** — belum ditest visual di browser apakah pagination dan filter card bekerja dengan benar.

---

## CARA JALANKAN WEB

```bash
cd c:/laragon/www/skripsi
python app.py
```

Login: `admin` / `admin123`, `analis_dishub` / `analis123`, `staff_dishub` / `staff123`
