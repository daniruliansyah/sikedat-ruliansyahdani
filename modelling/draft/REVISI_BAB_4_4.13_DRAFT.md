## 4.13  Hasil Pengembangan Web

`[TODO: Sub-bab ini merupakan hasil implementasi dari tahap 3.3.12 Pengembangan Web pada Bab III. Berikut adalah panduan TODO yang terperinci agar dapat dikirimkan ke Claude Code yang sudah membaca dan memahami program web Anda:]`

### 4.13.1  Arsitektur Sistem

`[TODO — untuk Claude Code: Jelaskan arsitektur sistem web Flask yang sudah Anda bangun secara lengkap, mencakup:]`

- `[TODO: Diagram arsitektur sistem — komponen frontend (HTML/CSS/JS/Bootstrap), backend (Flask + model RF .pkl), dan database (SQLite/PostgreSQL via SQLAlchemy)]`
- `[TODO: Penjelasan singkat masing-masing komponen dan peran teknisnya]`
- `[TODO: Alur data lengkap: dari user upload CSV → preprocessing → prediksi model RF → hasil klasifikasi ditampilkan]`
- `[TODO: Daftar endpoint/route Flask yang telah diimplementasikan beserta fungsinya]`
- `[TODO: Teknologi yang digunakan: Flask, Python, HTML, CSS, JavaScript, Bootstrap, Chart.js/Plotly, SQLite/PostgreSQL, SQLAlchemy]`

### 4.13.2  Implementasi User Interface

> **📸 INSTRUKSI SCREENSHOT — untuk Claude Code (VSCode):**
> Baca kode web Flask Anda, lalu identifikasi route/URL untuk setiap halaman di bawah ini. Beritahu Dani (peneliti) halaman mana saja yang perlu di-screenshot dengan menyebutkan URL atau nama file template HTML-nya, agar Dani bisa membuka browser dan mengambil screenshot sendiri. Setelah screenshot tersedia, Claude Code mengisi deskripsi 2–3 kalimat per gambar di bawah ini.

Berikut halaman-halaman utama aplikasi web yang diimplementasikan:

**Gambar 4.18  Halaman Login**

> **📸 untuk Claude Code:** Identifikasi route login (kemungkinan `/login` atau `/`) dan nama template HTML-nya. Informasikan ke Dani untuk screenshot halaman ini dalam kondisi form login kosong (tampilan awal). Setelah screenshot ada, isi deskripsi: jelaskan mekanisme autentikasi, perbedaan hak akses Staff Dishub vs Masyarakat, dan elemen UI yang terlihat.

`[TODO: Insert Gambar 4.18 — Screenshot Halaman Login]`

**Gambar 4.19  Halaman Upload Data CSV**

> **📸 untuk Claude Code:** Identifikasi route upload CSV (kemungkinan `/upload` atau `/data/upload`) dan nama template-nya. Informasikan ke Dani untuk screenshot halaman ini. Setelah screenshot ada, isi deskripsi: jelaskan komponen form upload, validasi format file yang dilakukan sistem, dan feedback yang ditampilkan ke pengguna.

`[TODO: Insert Gambar 4.19 — Screenshot Halaman Upload Data CSV]`

**Gambar 4.20  Halaman Dashboard Statistik Kepadatan**

> **📸 untuk Claude Code:** Identifikasi route dashboard (kemungkinan `/dashboard` atau `/`) dan nama template-nya. Informasikan ke Dani untuk screenshot halaman ini dalam kondisi sudah ada data (agar chart/grafik terisi). Setelah screenshot ada, isi deskripsi: jelaskan jenis chart yang ditampilkan (distribusi per jenis kendaraan, pola per jam, heavy vehicle mix, weekday vs weekend), library yang digunakan (Chart.js/Plotly), dan manfaatnya bagi DISHUB.

`[TODO: Insert Gambar 4.20 — Screenshot Halaman Dashboard Statistik]`

**Gambar 4.21  Halaman Validasi & Koreksi Hasil Klasifikasi**

> **📸 untuk Claude Code:** Identifikasi route validasi (kemungkinan `/validasi` atau `/klasifikasi/validasi`) dan nama template-nya. Informasikan ke Dani untuk screenshot halaman ini. Setelah screenshot ada, isi deskripsi: jelaskan alur validasi oleh Staff Dishub, bagaimana Staff bisa mengoreksi hasil prediksi model, dan bagaimana koreksi disimpan ke database.

`[TODO: Insert Gambar 4.21 — Screenshot Halaman Validasi & Koreksi]`

**Gambar 4.22  Halaman Hasil Klasifikasi / Prediksi**

> **📸 untuk Claude Code:** Identifikasi route hasil prediksi (kemungkinan `/hasil` atau `/prediksi`) dan nama template-nya. Informasikan ke Dani untuk screenshot halaman ini dalam kondisi ada hasil klasifikasi yang tampil. Setelah screenshot ada, isi deskripsi: jelaskan bagaimana output klasifikasi (Rendah/Sedang/Tinggi) ditampilkan, informasi pendukung apa yang disertakan, dan bagaimana pengguna dapat mengakses hasilnya.

`[TODO: Insert Gambar 4.22 — Screenshot Halaman Hasil Klasifikasi]`

**Gambar 4.23  Halaman Retraining Model** *(jika diimplementasikan)*

> **📸 untuk Claude Code:** Jika ada fitur retraining model, identifikasi route-nya dan nama template-nya. Informasikan ke Dani untuk screenshot. Jika fitur ini belum diimplementasikan, hapus sub-bagian ini dan sesuaikan catatan di sub-bab 4.13. Setelah screenshot ada, isi deskripsi: jelaskan alur retraining, kapan fitur ini digunakan, dan bagaimana hasilnya divalidasi.

`[TODO: Insert Gambar 4.23 — Screenshot Halaman Retraining Model (hapus jika belum ada)]`

### 4.13.3  Struktur Database

`[TODO — untuk Claude Code: Jelaskan skema database SQLite yang digunakan, mencakup:]`

- `[TODO: Tabel-tabel yang ada beserta kolom dan tipe datanya]`
- `[TODO: Relasi antar tabel (ERD jika ada)]`
- `[TODO: Tabel untuk menyimpan: data hasil ekstraksi yang diunggah, hasil klasifikasi, riwayat validasi/koreksi, data pengguna (admin, staff Dishub, masyarakat)]`

### 4.13.4  Integrasi Model ke Sistem

`[TODO — untuk Claude Code: Jelaskan secara teknis bagaimana model RF (.pkl) diintegrasikan ke Flask, mencakup:]`

- `[TODO: Cara load model menggunakan library joblib/pickle]`
- `[TODO: Pipeline preprocessing yang diterapkan pada data baru sebelum prediksi (OHE untuk Hari, StandardScaler untuk SVM — namun karena model terpilih adalah RF, normalisasi tidak diperlukan)]`
- `[TODO: Endpoint Flask yang menangani prediksi]`
- `[TODO: Snippet kode yang relevan untuk load model dan prediksi]`
- `[TODO: Berikan kesimpulan singkat di akhir sub-bab bahwa sistem sudah berjalan dengan baik dan siap diuji secara fungsional pada sub-bab 4.14]`
