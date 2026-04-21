# 🚦 SIKEDAT — Sistem Klasifikasi Kepadatan Lalu Lintas

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-black?style=flat-square&logo=flask)
![Machine Learning](https://img.shields.io/badge/Scikit--Learn-Machine%20Learning-orange?style=flat-square&logo=scikit-learn)

SIKEDAT adalah aplikasi berbasis *web* yang dirancang untuk mengklasifikasikan tingkat kepadatan lalu lintas (studi kasus: Jalan Diponegoro, Surabaya). Sistem ini menerima input data berupa *file* CSV hasil ekstraksi pendeteksian objek kendaraan (motor, mobil, bus, truk) menggunakan algoritma **YOLOv8 & DeepSORT**, lalu mengklasifikasikannya menjadi kategori **Rendah, Sedang, atau Tinggi** menggunakan *Machine Learning*.

Aplikasi ini juga dilengkapi fitur **Human-in-the-Loop (HITL)**, di mana pakar/validator dapat mengoreksi hasil prediksi, dan data hasil koreksi tersebut dapat digunakan untuk men-*training* ulang (*retrain*) model agar semakin akurat.

---

## ✨ Fitur Utama

- **📊 Dashboard Analitik:** Visualisasi komposisi jumlah kendaraan per hari.
- **📁 Upload & Auto-Classification:** Unggah CSV hasil YOLOv8 dan dapatkan hasil prediksi kepadatan secara otomatis.
- **✅ Validasi Pakar (HITL):** Fitur bagi analis untuk memvalidasi atau mengoreksi label hasil prediksi *machine learning*.
- **🧠 Retrain Model:** Latih ulang model klasifikasi menggunakan dataset terbaru yang sudah divalidasi langsung dari antarmuka *web*.

---

## 🛠️ Teknologi yang Digunakan

- **Backend:** Python (Flask, Flask-SQLAlchemy, Flask-Login, Flask-Bcrypt)
- **Data Science & ML:** Pandas, NumPy, Scikit-Learn, Joblib
- **Database:** SQLite (Default) / MySQL
- **Frontend:** HTML5, CSS3, JavaScript murni, Jinja2 Templating

---

## 🚀 Panduan Instalasi & Menjalankan Aplikasi

Ikuti langkah-langkah di bawah ini untuk menjalankan aplikasi di komputer lokal Anda.

### 1. Clone Repository

Buka terminal Anda dan *clone repository* ini:

```bash
git clone https://github.com/username-anda/sikedat-skripsi.git
cd sikedat-skripsi
```

> *(Opsional tapi disarankan)* Buat dan aktifkan Virtual Environment:

```bash
python -m venv .venv

# Untuk Windows:
.venv\Scripts\activate

# Untuk Linux/Mac:
source .venv/bin/activate
```

### 2. Install Dependensi

Instal semua library Python yang dibutuhkan oleh sistem:

```bash
pip install flask flask-sqlalchemy flask-login flask-bcrypt scikit-learn pandas numpy joblib
```

### 3. Training Model Awal

Sebelum aplikasi Flask dinyalakan, kita perlu men-*training* model *Machine Learning* untuk pertama kalinya agar file `.pkl` (model klasifikasi) terbentuk di dalam folder `models/`.

```bash
python train_models.py
```

### 4. Jalankan Server Flask

Jalankan file utama aplikasi. Sistem akan secara otomatis membuat database `sikedat.db` dan mengisi data user bawaan (Admin & Staff).

```bash
python app.py
```

Aplikasi sekarang berjalan lokal! Buka browser Anda dan akses:

```
http://127.0.0.1:5000
```

---

## 🔐 Akun Bawaan (Default Login)

Gunakan kredensial berikut untuk masuk ke dalam sistem:

| Role | Username | Password | Hak Akses |
|---|---|---|---|
| Admin / Analis | `admin` | `admin123` | Akses penuh (Klasifikasi, Validasi, Retrain Model) |
| Staff Dishub | `staff_dishub` | `staff123` | Akses terbatas (Hanya lihat Dashboard & Prediksi) |

> ⚠️ **Catatan:** Segera ganti password akun admin setelah aplikasi berhasil di-*deploy* ke server produksi!

---

## 📸 Tangkapan Layar (Screenshots)

| Halaman Login | Halaman Classifier |
|---|---|
| ![Login](static/img/screens/login.png) | ![Classifier](static/img/screens/classifier.png) |

---

<p align="center">
  © 2026 <strong>Dani Ruliansyah</strong> — D-IV Teknik Informatika, Universitas Airlangga
</p>
