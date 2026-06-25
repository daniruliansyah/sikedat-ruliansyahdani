# HANDOFF SESSION 5 → SESSION 6
# Role-Based Access Control + Update Dokumen Skripsi

**Tanggal session ini:** 2026-06-20
**Branch aktif:** `dani/main/integrasi-model`
**Status:** Semua perubahan selesai dieksekusi.

---

## RINGKASAN SESSION INI

Session ini membaca dan memahami handoff 1–4, lalu mengerjakan satu perubahan besar:
**implementasi role-based access control (RBAC) secara eksplisit per route**, menggantikan
mekanisme lama yang berbasis flag boolean `akses_penuh` di tabel `roles`.

Perubahan dibagi menjadi dua kelompok:
1. **Perubahan kode** — 3 file Python/HTML
2. **Perubahan dokumen skripsi** — 2 file Markdown

---

## PERUBAHAN KODE

### A. `models.py` — property `has_full_access`

Sebelumnya property ini membaca `role.akses_penuh` (boolean dari DB).
Sekarang mengecek `role.nama` langsung:

```python
# SEBELUM
@property
def has_full_access(self):
    return self.role.akses_penuh if self.role else False

# SESUDAH
@property
def has_full_access(self):
    return bool(self.role and self.role.nama in ['admin', 'analis'])
```

Kolom `akses_penuh` di tabel `roles` **tetap ada** (tidak dihapus dari DB/schema) —
keputusan Mas karena sudah ada di rancangan database di bab lain skripsi.
Kolom tersebut sekarang tidak dipakai oleh kode, tapi schema tidak berubah.

### B. `app.py` — dua perubahan

**1. Decorator `full_access_required`** (baris ~43–51):
```python
# SEBELUM
if not current_user.has_full_access:

# SESUDAH
if not (current_user.role and current_user.role.nama in ['admin', 'analis']):
```

**2. Route `/aktivitas`** — ganti decorator:
```python
# SEBELUM
@app.route('/aktivitas')
@login_required_only
def aktivitas():

# SESUDAH
@app.route('/aktivitas')
@full_access_required
def aktivitas():
```

### C. `templates/base.html` — sidebar

Dua perubahan:
1. Komentar sidebar diperbarui mencerminkan akses per role yang baru
2. Menu **Log Aktivitas** dipindah dari luar ke **dalam** blok `{% if current_user.has_full_access %}`
   sehingga Staff tidak lagi melihat menu ini

Struktur sidebar baru:
```
{% if current_user.is_authenticated %}
  Dashboard & Analitik         ← semua role (Staff, Analis, Admin)

  {% if current_user.has_full_access %}  ← hanya Analis & Admin
    [label] Manajemen Data
    Klasifikasi Data
    Validasi Data
    Retrain Model
    Log Aktivitas              ← DIPINDAH KE SINI (sebelumnya di luar)
  {% endif %}

  Data Observasi               ← semua role (Staff, Analis, Admin)

  {% if role == 'admin' %}
    [label] Administrasi
    Manajemen User
  {% endif %}
{% endif %}
```

---

## PEMETAAN AKSES ROUTE (FINAL)

| Route | Decorator | Akses |
|---|---|---|
| `/` | — | Public |
| `/prediksi` | — | Public |
| `/auth/login` | — | Public |
| `/auth/logout` | `@login_required` | Semua login |
| `/dashboard` | `@login_required_only` | Admin, Analis, Staff |
| `/data-observasi` | `@login_required_only` | Admin, Analis, Staff |
| `/aktivitas` | `@full_access_required` | **Admin, Analis** ← BERUBAH |
| `/classifier` | `@full_access_required` | Admin, Analis |
| `/classifier/run` | `@full_access_required` | Admin, Analis |
| `/classifier/download` | `@full_access_required` | Admin, Analis |
| `/validasi` | `@full_access_required` | Admin, Analis |
| `/validasi/save` | `@full_access_required` | Admin, Analis |
| `/validasi/import` | `@full_access_required` | Admin, Analis |
| `/retrain` | `@full_access_required` | Admin, Analis |
| `/retrain/activate/<v>` | `@full_access_required` | Admin, Analis |
| `/users` | `@admin_required` | Admin |
| `/users/create` | `@admin_required` | Admin |
| `/users/edit/<id>` | `@admin_required` | Admin |
| `/users/toggle/<id>` | `@admin_required` | Admin |

---

## PERUBAHAN DOKUMEN SKRIPSI

### A. `REVISI_JAWABAN_4.13_5.5(1).md` — tiga titik

**1. Tabel 4.31 (route table), baris `/aktivitas`:**
- Sebelum: `Admin, Analis, dan Staff`
- Sesudah: `Admin dan Analis`

**2. Paragraf penjelasan setelah Tabel 4.31:**
- Ditulis ulang dari "tiga tingkatan" menjadi "empat tingkatan akses" yang lebih akurat:
  Public → Staff → Admin+Analis → Admin-only

**3. Deskripsi Gambar 4.18 (Login page):**
- Dihapus: referensi ke `akses_penuh` dan "dua tingkat hak akses"
- Diganti: deskripsi 3 role eksplisit (Admin, Analis, Staff) + penjelasan sidebar adaptif

### B. `REVISI_BAB_4_DRAFT(4.12).md` — sub-bab 4.12.1 Use Case Diagram

Teks ditulis ulang sepenuhnya:

| Aspek | Sebelum | Sesudah |
|---|---|---|
| Jumlah aktor | 2 (Staff Dishub + Masyarakat) | **4** (Masyarakat, Staff, Analis, Admin) |
| Relasi antar aktor | Tidak ada | **Generalization** (Staff ← Analis ← Admin) |
| Jumlah use case | 7 | **10** |

Use case baru yang ditambahkan:
- **Melihat data observasi** (Staff, Analis, Admin)
- **Melihat log aktivitas** (Analis, Admin)
- **Mengelola akun pengguna** (Admin saja)

Teks sekarang juga menjelaskan notasi generalization UML: panah segitiga kosong dari
aktor khusus (child) ke aktor umum (parent), bukan `«extend»`.

---

## STATE SISTEM SAAT INI

### Database
```
Tabel dataset        : 878 baris (877 real + 1 dari testing)
Tabel retrain_history: 1 record (v1.0, duration_seconds = NULL)
Tabel users          : 3 user (admin, analis_dishub, staff_dishub)
Kolom akses_penuh    : masih ada di tabel roles (tidak dipakai kode, tidak dihapus)
```

### Model Aktif
```
File       : models/model_aktif.pkl
Algoritma  : Random Forest — Skenario 1
Accuracy   : 73.30% | F1-weighted: 72.99%
Fitur (14) : Jam, Menit, Hari_Jumat..Hari_Senin, Motor, Mobil, Bus, Truk, Total_Kendaraan
Dilatih    : 2026-06-18 (877 baris)
```

### Akun Login
```
admin        / admin123   → role: admin
analis_dishub/ analis123  → role: analis
staff_dishub / staff123   → role: staff
```

---

## YANG BELUM DIKERJAKAN / PERLU DICEK

1. **Gambar use case diagram harus digambar ulang** — file `diagram_usecase.png` di folder
   `modelling/draft/` masih mencerminkan struktur lama (2 aktor, 7 use case). Perlu dibuat
   ulang dengan 4 aktor + relasi generalization + 10 use case sesuai teks yang sudah diupdate.

2. **Test visual setelah perubahan RBAC** — login sebagai `staff_dishub` dan pastikan:
   - Menu Log Aktivitas **tidak muncul** di sidebar
   - Akses langsung ke `http://localhost:5000/aktivitas` menghasilkan **403**
   - Menu Data Observasi **tetap muncul**

3. **Screenshot untuk BAB 4.13.2** — semua `[TODO: Insert Gambar 4.18–4.23]` di
   `REVISI_JAWABAN_4.13_5.5(1).md` masih perlu diisi. URL untuk setiap gambar:
   | Gambar | URL |
   |---|---|
   | 4.18 — Login | `http://localhost:5000/auth/login` (form kosong) |
   | 4.19 — Klasifikasi | `http://localhost:5000/classifier` (login sebagai analis/admin) |
   | 4.20 — Dashboard | `http://localhost:5000/dashboard` (tanpa filter) |
   | 4.21 — Validasi | `http://localhost:5000/validasi` (pastikan ada data pending) |
   | 4.22 — Prediksi | `http://localhost:5000/prediksi` (isi form lalu submit) |
   | 4.23 — Retrain | `http://localhost:5000/retrain` (tampil normal) |

4. **Nomor tabel placeholder** — `Tabel 4.X` di `REVISI_JAWABAN_4.13_5.5(1).md` perlu
   disesuaikan dengan nomor tabel aktual di skripsi Mas.

5. **Baris ke-878 di DB** — satu baris ekstra dari testing session 2. Opsional dihapus:
   `DELETE FROM dataset WHERE id = 878`

6. **Script satu kali jalan** boleh dihapus jika sudah tidak diperlukan:
   - `train_initial_model.py`
   - `import_initial_dataset.py`

---

## CARA JALANKAN WEB

```bash
cd c:/laragon/www/skripsi
python app.py
```

Login: `admin` / `admin123`, `analis_dishub` / `analis123`, `staff_dishub` / `staff123`
