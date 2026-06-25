## 4.13  Hasil Pengembangan Web

Sub-bab ini memaparkan hasil implementasi sistem web SIKEDAT (*Sistem Klasifikasi Kepadatan*) sebagai realisasi dari tahap perancangan yang telah diuraikan pada sub-bab 3.3.12. Sistem web dibangun menggunakan kerangka kerja Flask berbasis Python dan dirancang untuk dioperasikan oleh petugas Dinas Perhubungan Kota Surabaya dalam mengelola, memvalidasi, dan menganalisis data kepadatan lalu lintas Jalan Diponegoro Musi Utara secara berkelanjutan. Implementasi mencakup empat aspek utama yang dibahas secara berurutan pada sub-bab berikut, yaitu arsitektur sistem, antarmuka pengguna, struktur basis data, serta integrasi model *machine learning* ke dalam lingkungan web.

### 4.13.1  Arsitektur Sistem

Arsitektur sistem web SIKEDAT mengikuti pola *Model-View-Controller* (MVC) yang secara alami difasilitasi oleh kerangka kerja Flask. Pemisahan tanggung jawab antara ketiga lapisan tersebut memudahkan pemeliharaan kode, pengujian komponen secara independen, serta pengembangan fitur di masa mendatang tanpa mengganggu bagian sistem yang sudah berjalan. Berikut adalah penjelasan masing-masing lapisan beserta teknologi yang digunakan, alur data utama, dan daftar seluruh *endpoint* yang telah diimplementasikan.

**Lapisan Frontend (View)**

Lapisan *frontend* dibangun menggunakan HTML5 dan CSS3 dengan *style sheet* kustom yang menerapkan tema gelap (*dark theme*) berbasis palet warna biru-abu profesional. Seluruh halaman mewarisi tata letak dari template induk `base.html` yang menyediakan sidebar navigasi adaptif, *topbar* dengan jam digital, dan sistem *flash message* untuk umpan balik aksi pengguna. Sidebar bersifat dinamis—menu yang ditampilkan disesuaikan secara otomatis berdasarkan status autentikasi dan peran pengguna yang sedang aktif. Interaktivitas halaman ditangani oleh JavaScript tanpa *framework* eksternal (*vanilla JS*), sedangkan seluruh visualisasi data menggunakan library Chart.js versi 4.4.0 untuk menghasilkan grafik batang, garis, *doughnut*, dan heatmap. Tipografi menggunakan font DM Mono dari Google Fonts untuk konsistensi tampilan data numerik di seluruh halaman.

**Lapisan Backend (Controller)**

Flask berperan sebagai *controller* yang menangani *routing* HTTP, manajemen sesi, autentikasi berbasis Flask-Login dengan enkripsi kata sandi menggunakan Flask-Bcrypt, serta komunikasi antara lapisan *frontend* dan lapisan model. Seluruh logika bisnis utama—termasuk pemrosesan data, pemanggilan model prediksi, manajemen alur validasi, dan pengelolaan *retrain*—diimplementasikan dalam `app.py` yang mendefinisikan 18 *route* HTTP, serta dua modul pendukung terpisah: `ml_utils.py` untuk operasi prediksi dan `train_models.py` untuk pelatihan ulang model.

**Lapisan Model (Database & ML)**

Basis data dikelola menggunakan SQLite melalui ORM Flask-SQLAlchemy yang mendefinisikan empat tabel utama: `roles`, `users`, `dataset`, dan `retrain_history`. Pemilihan SQLite mempertimbangkan skala operasional DISHUB yang tidak memerlukan sistem basis data berbasis server, sekaligus menyederhanakan proses instalasi dan pemeliharaan. Model *machine learning* disimpan dalam format `.pkl` dan dimuat menggunakan library `joblib`. Pemisahan logika ML ke dalam modul tersendiri (`ml_utils.py` dan `train_models.py`) memastikan bahwa kode *routing* Flask tidak bercampur dengan kode domain ML, sehingga pergantian atau pembaruan model dapat dilakukan tanpa menyentuh kode infrastruktur web.

**Alur Data Klasifikasi Batch**

Alur data utama sistem SIKEDAT dimulai dari unggahan file CSV oleh pengguna hingga data tersimpan sebagai rekaman tervalidasi yang siap digunakan untuk pelatihan ulang model. Secara rinci, alur tersebut berjalan melalui delapan tahap berikut:

1. Pengguna (Analis atau Admin) mengunggah file CSV hasil ekstraksi pipeline YOLOv8+DeepSORT melalui halaman `/classifier`.
2. Sistem memvalidasi keberadaan delapan kolom wajib: `hari`, `jam`, `menit`, `motor`, `mobil`, `bus`, `truk`, dan `total_kendaraan`. Nama kolom dinormalisasi otomatis ke huruf kecil untuk mengakomodasi variasi format dari sumber yang berbeda.
3. Fungsi `classify_dataframe()` pada `ml_utils.py` melakukan *One-Hot Encoding* (OHE) terhadap kolom `hari` menjadi tujuh kolom biner, kemudian menyusun matriks fitur berukuran 14 kolom sesuai urutan yang digunakan saat pelatihan.
4. Model Random Forest aktif (`model_aktif.pkl`) menghasilkan prediksi label (`Rendah`/`Sedang`/`Tinggi`) beserta probabilitas per kelas untuk setiap baris data.
5. Hasil klasifikasi ditampilkan kepada pengguna dan dapat diunduh sebagai file CSV.
6. Pengguna mengimpor hasil ke sistem; setiap baris tersimpan di tabel `dataset` dengan `status_validasi = 'pending'` dan dikelompokkan dalam satu `batch_id` unik.
7. Validator membuka halaman `/validasi` untuk menelaah, mengonfirmasi, atau mengoreksi hasil prediksi model secara baris per baris.
8. Data yang telah divalidasi (status `validated` atau `corrected`) menjadi dataset latih pada proses *retrain* model yang dijalankan melalui halaman `/retrain`.

**Daftar Route Flask yang Diimplementasikan**

Tabel 4.31 berikut merangkum seluruh *endpoint* HTTP yang tersedia pada sistem SIKEDAT beserta fungsi dan aksesnya.

| Route | Metode | Fungsi | *Roles* |
|---|---|---|---|
| `/` | GET | Beranda — statistik ringkas dan grafik komposisi kendaraan | — |
| `/prediksi` | GET, POST | Prediksi kepadatan berdasarkan input hari, jam, dan menit | — |
| `/auth/login` | GET, POST | Autentikasi pengguna dengan *username* dan kata sandi | — |
| `/auth/logout` | GET | Mengakhiri sesi pengguna yang aktif | Admin, Analis, dan Staff |
| `/dashboard` | GET | *Dashboard* analitik: heatmap, grafik per jam, *weekday vs weekend* | Admin, Analis, dan Staff |
| `/data-observasi` | GET | Tabel seluruh data observasi dengan filter status validasi dan paginasi | Admin, Analis, dan Staff |
| `/aktivitas` | GET | Log aktivitas sistem (klasifikasi, validasi, *retrain*) | Admin dan Analis |
| `/classifier` | GET, POST | Halaman unggah file CSV untuk diklasifikasikan | Admin dan Analis |
| `/classifier/run` | POST | Menjalankan proses klasifikasi *batch* | Admin dan Analis |
| `/classifier/download` | GET | Mengunduh hasil klasifikasi sebagai file CSV | Admin dan Analis |
| `/validasi` | GET | Antarmuka validasi dan koreksi label per *batch* | Admin dan Analis |
| `/validasi/save` | POST | Menyimpan hasil validasi ke basis data | Admin dan Analis |
| `/validasi/import` | POST | Mengimpor hasil klasifikasi ke antrian validasi | Admin dan Analis |
| `/retrain` | GET, POST | Halaman manajemen dan pemantauan *retrain* model | Admin dan Analis |
| `/retrain/activate/<version>` | POST | Mengaktifkan versi model tertentu dari riwayat | Admin dan Analis |
| `/users` | GET | Daftar manajemen akun pengguna sistem | Admin |
| `/users/create` | GET, POST | Membuat akun pengguna baru | Admin |
| `/users/edit/<id>` | GET, POST | Mengedit informasi akun pengguna | Admin |
| `/users/toggle/<id>` | POST | Mengaktifkan atau menonaktifkan akun pengguna | Admin |

Dari Tabel 4.31 terlihat bahwa sistem SIKEDAT menerapkan kontrol akses berbasis peran (*role-based access control*) dengan empat tingkatan yang berbeda. *Endpoint* publik (tanpa autentikasi) hanya mencakup beranda, prediksi, dan autentikasi — halaman yang dirancang agar dapat diakses oleh seluruh pengguna termasuk masyarakat umum. *Endpoint* yang memerlukan *login* namun dapat diakses oleh seluruh peran terautentikasi mencakup *dashboard* analitik dan data observasi — halaman informatif yang membantu petugas Dishub memantau kondisi data secara visual. *Endpoint* yang dibatasi untuk peran Admin dan Analis mencakup seluruh operasi pengelolaan data dan model: klasifikasi, validasi, *retrain*, serta log aktivitas sistem — sesuai dengan tanggung jawab operasional kedua peran tersebut dalam alur kerja SIKEDAT. Khusus untuk *endpoint* manajemen akun pengguna (`/users`), akses hanya diberikan kepada Admin karena menyangkut keamanan seluruh sistem.

**Tumpukan Teknologi**

Tabel 4.32 berikut merangkum seluruh teknologi yang digunakan dalam pengembangan sistem web SIKEDAT.

| Kategori | Teknologi / Library | Keterangan |
|---|---|---|
| Bahasa pemrograman | Python 3.x | *Backend* utama |
| *Framework* web | Flask 2.x | *Routing*, *templating*, manajemen sesi |
| ORM & basis data | Flask-SQLAlchemy + SQLite | Abstraksi basis data relasional |
| Autentikasi | Flask-Login, Flask-Bcrypt | Manajemen sesi, *hash* kata sandi |
| *Machine learning* | scikit-learn | Random Forest, metrik evaluasi |
| Serialisasi model | joblib | *Load/dump* file `.pkl` |
| Manipulasi data | pandas, numpy | Preprocessing, OHE, operasi array |
| *Frontend* | HTML5, CSS3 kustom | Struktur dan tampilan halaman |
| Interaktivitas | JavaScript *vanilla* | Toggle, validasi form, update grafik |
| Visualisasi | Chart.js 4.4.0 | Grafik batang, garis, *doughnut*, heatmap |
| Tipografi | DM Mono (Google Fonts) | Font monospace untuk data numerik |

Pemilihan tumpukan teknologi pada Tabel 4.32 didasarkan pada prinsip kesesuaian ekosistem dan kemudahan integrasi. Seluruh lapisan — dari Flask sebagai *framework* web, SQLite melalui ORM Flask-SQLAlchemy sebagai basis data, hingga scikit-learn dan joblib sebagai mesin prediksi — berbasis Python, sehingga tidak ada hambatan lintas bahasa dalam komunikasi antar komponen. Chart.js dipilih untuk visualisasi karena ringan, tidak memerlukan *server-side rendering*, dan mendukung semua jenis grafik yang dibutuhkan sistem secara langsung di sisi klien. Pembahasan lebih mendalam mengenai pertimbangan pemilihan teknologi ini diuraikan pada sub-bab 5.5.1.

### 4.13.2  Implementasi User Interface

Antarmuka pengguna SIKEDAT dirancang dengan mempertimbangkan dua kelompok pengguna utama: masyarakat umum yang mengakses layanan prediksi kepadatan tanpa memerlukan akun, serta petugas Dinas Perhubungan yang memerlukan autentikasi untuk mengoperasikan fitur pengelolaan data dan model. Desain menerapkan tema gelap dengan aksen biru untuk menghasilkan tampilan yang profesional sekaligus nyaman digunakan dalam operasional sehari-hari. Navigasi antar halaman dilakukan melalui *sidebar* yang bersifat adaptif—menu yang ditampilkan menyesuaikan diri secara otomatis berdasarkan peran dan status *login* pengguna yang sedang aktif, sehingga setiap pengguna hanya melihat fitur yang memang tersedia baginya. Berikut adalah tangkapan layar beserta penjelasan halaman-halaman utama yang telah diimplementasikan.

---

**Gambar 4.18  Halaman Login**

Halaman ini merupakan pintu masuk bagi seluruh pengguna internal Dinas Perhubungan untuk mengakses fitur-fitur operasional sistem SIKEDAT yang bersifat terbatas.

*(📸 Screenshot: buka `http://localhost:5000/auth/login` pada browser dalam kondisi form kosong sebelum diisi)*

`[TODO: Insert Gambar 4.18 — Screenshot Halaman Login]`

Gambar 4.18 menampilkan halaman autentikasi SIKEDAT yang dapat diakses melalui alamat `/auth/login`. Halaman ini menyajikan formulir *login* yang meminta *username* dan kata sandi, dengan tombol "Login Dishub" sebagai pemicu verifikasi identitas. Sistem menggunakan Flask-Login untuk manajemen sesi aktif dan Flask-Bcrypt untuk memverifikasi kata sandi yang tersimpan dalam bentuk *hash* bcrypt di basis data. Sistem menerapkan kontrol akses berbasis peran dengan tiga tingkatan: Admin yang dapat mengakses seluruh fitur termasuk manajemen akun pengguna; Analis yang dapat mengakses fitur pengelolaan data dan model (klasifikasi, validasi, *retrain*, dan log aktivitas); serta Staff yang hanya dapat mengakses halaman informatif (*dashboard* analitik dan data observasi). Setelah *login*, *sidebar* navigasi secara otomatis menampilkan hanya menu yang sesuai dengan peran pengguna yang sedang aktif.

---

**Gambar 4.19  Halaman Klasifikasi Data**

Halaman klasifikasi data merupakan halaman inti tempat dimulainya alur pengolahan data observasi lalu lintas dari video CCTV Jalan Diponegoro menjadi label tingkat kepadatan yang terstruktur.

*(📸 Screenshot: buka `http://localhost:5000/classifier` setelah login sebagai analis atau admin, tampilkan halaman dalam kondisi form upload CSV siap diisi)*

`[TODO: Insert Gambar 4.19 — Screenshot Halaman Klasifikasi Data (Upload CSV)]`

Gambar 4.19 memperlihatkan halaman klasifikasi data yang dapat diakses melalui `/classifier` oleh pengguna dengan akses penuh. Pada halaman ini, pengguna mengunggah file CSV hasil ekstraksi dari *pipeline* YOLOv8+DeepSORT yang memuat delapan kolom wajib: `Hari`, `Jam`, `Menit`, `Motor`, `Mobil`, `Bus`, `Truk`, dan `Total_Kendaraan`. Sistem secara otomatis menormalisasi nama kolom ke huruf kecil sebelum pemrosesan untuk mengakomodasi variasi format file dari sumber yang berbeda. Setelah proses klasifikasi dijalankan, hasil prediksi label (`Rendah`, `Sedang`, atau `Tinggi`) beserta probabilitas kepercayaan per kelas ditampilkan dalam tabel dan dapat diunduh sebagai file CSV atau langsung diimpor ke antrian validasi dengan sekali klik.

---

**Gambar 4.20  Halaman Dashboard & Analitik**

*Dashboard* analitik merupakan halaman ringkasan visual yang membantu petugas Dishub memahami pola kepadatan lalu lintas secara menyeluruh dari seluruh data yang telah tersimpan di sistem.

*(📸 Screenshot: buka `http://localhost:5000/dashboard` setelah login, pastikan tidak ada filter aktif agar semua grafik tampil dengan data penuh)*

`[TODO: Insert Gambar 4.20 — Screenshot Halaman Dashboard & Analitik]`

Gambar 4.20 menampilkan halaman *dashboard* analitik yang dapat diakses pada `/dashboard` oleh seluruh pengguna yang telah terautentikasi. Halaman ini menyajikan delapan elemen visualisasi secara terpadu: (1) empat *stat card* yang menampilkan total observasi serta jumlah dan persentase data per kelas kepadatan; (2) grafik batang rata-rata dan volume tertinggi kendaraan per jam pengamatan (dapat beralih antara dua mode); (3) *doughnut chart* distribusi proporsi kelas kepadatan; (4) grafik garis perbandingan rata-rata volume *weekday* (Senin–Jumat) versus *weekend* (Sabtu–Minggu); (5) grafik batang bertumpuk (*stacked bar*) komposisi jenis kendaraan per jam; (6) *gauge chart* rasio kendaraan berat (Bus + Truk) terhadap total; (7) tabel sepuluh interval dengan volume tertinggi; dan (8) heatmap matriks 7 hari × 8 jam yang menggambarkan pola intensitas volume kendaraan dengan gradasi warna dari biru gelap (volume rendah) melalui biru terang (volume sedang) hingga merah (volume tinggi). Seluruh visualisasi merespons filter hari dan kategori kepadatan yang dipilih pengguna melalui formulir di bagian atas halaman.

---

**Gambar 4.21  Halaman Validasi & Koreksi**

Halaman validasi merupakan implementasi mekanisme *Human-in-the-Loop* yang memungkinkan pakar domain menelaah dan mengonfirmasi setiap hasil prediksi model sebelum data dianggap valid untuk digunakan dalam pelatihan ulang.

*(📸 Screenshot: buka `http://localhost:5000/validasi` setelah login sebagai analis atau admin, pastikan ada data dengan status `pending` agar tabel antrian dan tabel data tampil)*

`[TODO: Insert Gambar 4.21 — Screenshot Halaman Validasi & Koreksi]`

Gambar 4.21 menampilkan halaman validasi yang dapat diakses melalui `/validasi` oleh pengguna dengan akses penuh. Sistem mengadopsi mekanisme antrian berbasis `batch_id`—satu sesi unggah CSV yang belum selesai divalidasi harus diselesaikan terlebih dahulu sebelum *batch* berikutnya muncul, untuk menjaga integritas urutan pemrosesan data. Tersedia tiga mekanisme yang dapat dipilih validator untuk menandai baris sebagai tervalidasi: (1) tombol "✓ Valid" per baris untuk persetujuan individual; (2) perubahan *dropdown* label yang secara otomatis menandai baris sebagai "Dikoreksi" apabila label dipilih berbeda dari prediksi model; dan (3) fitur *bulk* menggunakan *checkbox* dengan tombol "Setujui Terpilih" untuk persetujuan massal. Ketika pengguna menekan "Simpan Terpilih", sistem mengubah `status_validasi` baris yang bersangkutan menjadi `validated` atau `corrected`, serta mencatat identitas validator dan *timestamp* ke kolom `validated_by` dan `validated_at` secara otomatis.

---

**Gambar 4.22  Halaman Prediksi Kepadatan**

Halaman prediksi kepadatan merupakan fitur yang dapat diakses oleh masyarakat umum tanpa perlu *login*, yang memungkinkan siapa pun untuk memperoleh perkiraan tingkat kepadatan lalu lintas Jalan Diponegoro berdasarkan waktu yang ditentukan.

*(📸 Screenshot: buka `http://localhost:5000/prediksi`, isi contoh input (mis. Hari: Selasa, Jam: 8, Menit: 0), tekan tombol Prediksi, lalu tangkap layar saat hasil prediksi tampil)*

`[TODO: Insert Gambar 4.22 — Screenshot Halaman Prediksi Kepadatan]`

Gambar 4.22 menunjukkan halaman prediksi kepadatan yang dapat diakses tanpa autentikasi melalui alamat `/prediksi`. Halaman ini menyediakan formulir sederhana dengan tiga masukan: hari dalam seminggu, jam pengamatan, dan menit. Karena pengguna publik tidak memiliki data hitungan kendaraan aktual dari CCTV, sistem menggunakan estimasi rata-rata historis per jam yang diperoleh dari 877 baris data real (contoh: Jam 08 → rata-rata Motor=471, Mobil=140, Bus=7, Truk=2) sebagai nilai pengganti fitur numerik. Hasil prediksi ditampilkan dalam bentuk label tingkat kepadatan (Rendah, Sedang, atau Tinggi) disertai persentase probabilitas per kelas, sehingga pengguna dapat memahami tingkat keyakinan model terhadap estimasi yang diberikan dan menggunakannya sebagai referensi sebelum melakukan perjalanan.

---

**Gambar 4.23  Halaman Retrain Model**

Halaman *retrain* model merupakan antarmuka yang memungkinkan sistem terus berkembang seiring bertambahnya data tervalidasi baru, sehingga akurasi klasifikasi dapat ditingkatkan secara berkala tanpa memerlukan intervensi teknis dari pengembang.

*(📸 Screenshot: buka `http://localhost:5000/retrain` setelah login sebagai analis atau admin, tampilkan halaman dalam kondisi normal dengan tabel riwayat retrain terisi)*

`[TODO: Insert Gambar 4.23 — Screenshot Halaman Retrain Model]`

Gambar 4.23 menampilkan halaman manajemen *retrain* model yang dapat diakses melalui `/retrain` oleh pengguna dengan akses penuh. Halaman ini terbagi menjadi tiga bagian utama: (1) ringkasan data yang menampilkan jumlah data tervalidasi yang tersedia sebagai bahan latih; (2) panel konfigurasi algoritma yang menampilkan informasi model aktif beserta seluruh *hyperparameter* Random Forest Skenario 1 yang diterapkan secara tetap (n\_estimators=200, max\_depth=10, min\_samples\_split=2, min\_samples\_leaf=1, class\_weight='balanced'); dan (3) tabel riwayat *retrain* yang mencatat secara lengkap setiap versi model yang pernah dilatih, termasuk metrik evaluasi (akurasi dan F1-*score*), jumlah data latih dan uji, durasi proses dalam satuan detik, tanggal pelatihan, identitas operator, dan status aktif. Ketika tombol *retrain* ditekan, sistem mengekspor data `validated` dan `corrected` dari basis data ke file sementara `dataset_tervalidasi.csv`, menjalankan pelatihan melalui *subprocess* Python, lalu memperbarui file model dan metadata secara otomatis tanpa memerlukan interaksi tambahan dari pengguna.

---

### 4.13.3  Struktur Database

Basis data SIKEDAT diimplementasikan menggunakan SQLite sebagai sistem manajemen basis data relasional yang ringan dan tidak memerlukan proses server terpisah, sehingga instalasi dan pemeliharaan sistem menjadi lebih sederhana. Seluruh definisi skema tabel dikelola melalui ORM Flask-SQLAlchemy yang didefinisikan dalam file `models.py`, memungkinkan pembuatan tabel, pengelolaan relasi, dan penulisan kueri dilakukan sepenuhnya menggunakan sintaks Python tanpa perlu menulis SQL secara langsung. Basis data terdiri dari empat tabel yang saling berelasi dan dirancang untuk mendukung seluruh alur kerja sistem: manajemen peran dan akun pengguna, penyimpanan rekaman data observasi beserta status validasinya, hingga pencatatan historis setiap proses pelatihan ulang model.

**Tabel 4.33 Struktur Tabel `roles`**

Tabel `roles` menyimpan definisi peran yang tersedia dalam sistem. Kolom `nama` menjadi satu-satunya penentu hak akses karena setiap *route* yang memerlukan hak operasional penuh mengecek nilai `role.nama` secara eksplisit di dalam *decorator* masing-masing — bukan membaca kolom `akses_penuh`. Kolom `akses_penuh` tetap dipertahankan di skema basis data sesuai rancangan awal, namun tidak lagi dibaca oleh kode aplikasi setelah mekanisme otorisasi diubah menjadi pengecekan nama peran secara langsung di setiap *route*.

| Kolom | Tipe Data | Keterangan |
|---|---|---|
| `id` | INTEGER (PK) | Kunci primer, *auto-increment* |
| `nama` | VARCHAR(50) | Nama peran (admin, analis, staff) |
| `deskripsi` | VARCHAR(200) | Deskripsi singkat peran |
| `akses_penuh` | BOOLEAN | Ada di skema DB; tidak aktif dipakai kode (digantikan pengecekan `role.nama` di *route decorator*) |

Tabel 4.33 menunjukkan bahwa tabel `roles` dirancang minimalis dengan hanya empat kolom. Kontrol akses dalam sistem ditentukan oleh nilai kolom `nama` — setiap *decorator* seperti `@full_access_required` dan `@admin_required` mengecek `role.nama` secara eksplisit (`'admin'`, `'analis'`, `'staff'`) tanpa membaca kolom `akses_penuh`. Pendekatan ini membuat aturan akses per *route* menjadi eksplisit dan dapat ditelusuri langsung dari kode, tanpa bergantung pada nilai kolom basis data yang berpotensi berubah di luar kendali aplikasi.

**Tabel 4.34 Struktur Tabel `users`**

Tabel `users` menyimpan data akun seluruh pengguna sistem. Kata sandi tidak disimpan dalam bentuk *plaintext*, melainkan dalam bentuk *hash* bcrypt untuk menjaga keamanan. Kolom `role_id` berelasi ke tabel `roles` dengan hubungan *many-to-one*, sehingga satu peran dapat dimiliki oleh banyak pengguna.

| Kolom | Tipe Data | Keterangan |
|---|---|---|
| `id` | INTEGER (PK) | Kunci primer, *auto-increment* |
| `username` | VARCHAR(80) | *Username* unik untuk *login* |
| `password` | VARCHAR(200) | *Hash* bcrypt kata sandi |
| `nama_lengkap` | VARCHAR(150) | Nama lengkap untuk ditampilkan di UI |
| `role_id` | INTEGER (FK → roles.id) | Referensi ke tabel `roles` |
| `is_active` | BOOLEAN | Status aktif/nonaktif akun |
| `created_at` | DATETIME | *Timestamp* pembuatan akun |

Tabel `users` mengadopsi praktik keamanan standar dengan menyimpan kata sandi dalam bentuk *hash* bcrypt — nilai asli tidak pernah tersimpan di basis data. Kolom `is_active` memungkinkan Admin untuk menonaktifkan akun sementara tanpa menghapus riwayat aktivitas pengguna tersebut, yang penting untuk keperluan audit.

**Tabel 4.35 Struktur Tabel `dataset`**

Tabel `dataset` merupakan tabel inti yang menyimpan seluruh rekaman data observasi lalu lintas. Setiap baris merepresentasikan satu interval pengamatan 10 menit pada lokasi pemantauan. Kolom `status_validasi` menjadi indikator posisi data dalam alur *Human-in-the-Loop*: `pending` (belum divalidasi), `validated` (disetujui pakar tanpa perubahan label), atau `corrected` (label dikoreksi oleh pakar). Kolom `batch_id` mengelompokkan baris-baris yang berasal dari satu sesi unggah CSV yang sama, memfasilitasi sistem antrian validasi per sesi.

| Kolom | Tipe Data | Keterangan |
|---|---|---|
| `id` | INTEGER (PK) | Kunci primer, *auto-increment* |
| `hari` | VARCHAR(10) | Hari pengamatan (Senin–Minggu) |
| `jam` | INTEGER | Jam pengamatan (6–19) |
| `menit` | INTEGER | Menit interval (0, 10, 20, ..., 50) |
| `motor` | INTEGER | Jumlah sepeda motor per interval |
| `mobil` | INTEGER | Jumlah mobil per interval |
| `bus` | INTEGER | Jumlah bus per interval |
| `truk` | INTEGER | Jumlah truk per interval |
| `total_kendaraan` | INTEGER | Total seluruh kendaraan per interval |
| `tingkat_kepadatan` | VARCHAR(10) | Hasil prediksi model: Rendah/Sedang/Tinggi |
| `status_validasi` | VARCHAR(15) | `pending` / `validated` / `corrected` |
| `label_final` | VARCHAR(10) | Label akhir setelah validasi pakar |
| `nama_file` | VARCHAR(200) | Nama file CSV asal data diunggah |
| `tanggal` | DATE | Tanggal rekaman video CCTV |
| `batch_id` | VARCHAR(40) | ID unik satu sesi unggah/klasifikasi |
| `classified_by` | INTEGER (FK → users.id) | Pengguna yang mengunggah dan mengklasifikasi |
| `validated_by` | INTEGER (FK → users.id) | Pengguna yang memvalidasi |
| `created_at` | DATETIME | *Timestamp* saat klasifikasi dilakukan |
| `validated_at` | DATETIME | *Timestamp* saat validasi dilakukan |

Tabel `dataset` merupakan tabel dengan struktur paling kompleks karena harus merekam seluruh siklus hidup satu rekaman data: dari saat diklasifikasikan (`classified_by`, `created_at`) hingga saat divalidasi (`validated_by`, `validated_at`, `label_final`). Kolom `batch_id` dan `nama_file` memastikan data dapat ditelusuri kembali ke sesi unggah dan file CSV asalnya, yang penting untuk keperluan audit dan *debugging* di lingkungan operasional DISHUB.

**Tabel 4.36 Struktur Tabel `retrain_history`**

Tabel `retrain_history` mencatat setiap proses pelatihan ulang model yang dijalankan melalui sistem, termasuk metrik evaluasi, konfigurasi data, dan durasi proses. Kolom `is_active` menandai model versi mana yang saat ini aktif digunakan untuk klasifikasi, memungkinkan pengelolaan versi model secara historis dan pemulihan ke versi sebelumnya apabila diperlukan.

| Kolom | Tipe Data | Keterangan |
|---|---|---|
| `id` | INTEGER (PK) | Kunci primer, *auto-increment* |
| `versi` | VARCHAR(20) | Versi model (v1.0, v1.1, v1.2, dst.) |
| `algoritma` | VARCHAR(50) | Nama algoritma (Random Forest) |
| `tanggal` | DATETIME | *Timestamp* proses *retrain* |
| `n_train` | INTEGER | Jumlah data latih (80% dari total) |
| `n_test` | INTEGER | Jumlah data uji (20% dari total) |
| `accuracy` | FLOAT | Akurasi pada data uji (0.0–1.0) |
| `precision` | FLOAT | Presisi *weighted* |
| `recall` | FLOAT | *Recall weighted* |
| `f1_score` | FLOAT | F1-*score weighted* |
| `split_ratio` | FLOAT | Rasio *split* data (0.8 = 80/20) |
| `cv_fold` | INTEGER | Jumlah *fold cross-validation* (5) |
| `model_path` | VARCHAR(300) | *Path* file `.pkl` model yang disimpan |
| `is_active` | BOOLEAN | `True` = model ini aktif digunakan |
| `duration_seconds` | FLOAT | Durasi proses *retrain* dalam detik |
| `catatan` | TEXT | Keterangan tambahan |
| `user_id` | INTEGER (FK → users.id) | Pengguna yang menjalankan *retrain* |

Tabel `retrain_history` dirancang untuk mendukung pengelolaan versi model secara historis. Kombinasi kolom metrik evaluasi (`accuracy`, `precision`, `recall`, `f1_score`) dan kolom `is_active` memungkinkan operator DISHUB membandingkan performa antar versi model secara kuantitatif sebelum memutuskan untuk mengaktifkan atau mengembalikan ke versi sebelumnya, tanpa perlu keterlibatan pengembang.

**Relasi Antar Tabel**

Keempat tabel tersebut membentuk hubungan relasional sebagai berikut. Tabel `roles` berelasi *one-to-many* ke tabel `users` melalui `role_id`. Tabel `users` berelasi ke tabel `dataset` melalui dua *foreign key* berbeda: `classified_by` yang mencatat siapa yang melakukan klasifikasi, dan `validated_by` yang mencatat siapa yang melakukan validasi. Tabel `users` juga berelasi ke `retrain_history` melalui `user_id` untuk mencatat operator yang menjalankan setiap proses *retrain*. Relasi ganda antara `users` dan `dataset` ini memungkinkan sistem melacak secara granular siapa melakukan apa dan kapan pada setiap rekaman data.

### 4.13.4  Integrasi Model ke Sistem

Integrasi model *machine learning* ke dalam sistem web SIKEDAT dirancang dengan prinsip modularitas dan kemudahan pembaruan. Model dapat diganti secara transparan—cukup dengan menimpa file `model_aktif.pkl`—tanpa perlu mengubah satu baris pun kode di `app.py`. Seluruh logika yang berhubungan dengan model dienkapsulasi dalam dua modul terpisah: `ml_utils.py` untuk pemuatan model dan eksekusi prediksi, serta `train_models.py` untuk pelatihan ulang. Pemisahan ini memastikan bahwa kode *routing* Flask tidak bercampur dengan kode domain *machine learning*, sehingga kedua sisi dapat dikembangkan dan diuji secara independen.

**Pemuatan Model**

Model Random Forest disimpan dalam format `.pkl` menggunakan library `joblib` dan dimuat melalui fungsi `load_model()` pada `ml_utils.py`. Penggunaan `joblib` dipilih karena kemampuannya menangani objek Python berukuran besar—termasuk array NumPy yang menjadi komponen internal *estimator* Random Forest—secara lebih efisien dibandingkan modul `pickle` bawaan Python. Penamaan file model secara konsisten sebagai `model_aktif.pkl` memastikan bahwa pergantian model setelah *retrain* tidak memerlukan perubahan kode apapun.

```python
# ml_utils.py — fungsi pemuatan model
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')

def load_model():
    path = os.path.join(MODEL_DIR, 'model_aktif.pkl')
    return joblib.load(path)
```

**Pipeline Preprocessing**

Sebelum data dikirimkan ke model untuk prediksi, `ml_utils.py` menjalankan dua tahap preprocessing yang wajib dilakukan dalam urutan yang tepat:

*Tahap 1 — Normalisasi nama kolom:* Kolom dari file CSV yang diunggah pengguna dikonversi ke huruf kecil menggunakan `df.columns.str.lower()` untuk mengakomodasi variasi kapitalisasi dari sumber data yang berbeda.

*Tahap 2 — One-Hot Encoding (OHE) untuk kolom `Hari`:* Kolom `hari` yang berisi nilai teks (Senin, Selasa, ..., Minggu) dikonversi menjadi tujuh kolom biner dengan nama dan urutan alfabetis yang baku: `Hari_Jumat`, `Hari_Kamis`, `Hari_Minggu`, `Hari_Rabu`, `Hari_Sabtu`, `Hari_Selasa`, `Hari_Senin`. Urutan ketujuh kolom ini harus persis sama dengan urutan yang digunakan saat model dilatih, karena model Random Forest yang telah di-*fit* mengharapkan matriks fitur dengan urutan kolom yang identik.

```python
# ml_utils.py — konstanta urutan fitur dan fungsi OHE
HARI_COLS = ['Hari_Jumat', 'Hari_Kamis', 'Hari_Minggu', 'Hari_Rabu',
             'Hari_Sabtu', 'Hari_Selasa', 'Hari_Senin']

FITUR = ['Jam', 'Menit'] + HARI_COLS + ['Motor', 'Mobil', 'Bus', 'Truk', 'Total_Kendaraan']
# Total: 14 fitur

def _ohe_hari(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    hari_series = df['hari'].str.strip().str.title()
    for col in HARI_COLS:
        nama_hari = col.replace('Hari_', '')
        df[col] = (hari_series == nama_hari).astype(int)
    return df
```

Perlu dicatat bahwa karena model terpilih adalah Random Forest—algoritma berbasis pohon keputusan yang bersifat *scale-invariant*—tidak diperlukan normalisasi skala fitur numerik menggunakan StandardScaler maupun MinMaxScaler. Nilai hitungan kendaraan (motor, mobil, bus, truk, total) dapat langsung digunakan sebagai masukan tanpa transformasi apapun.

**Fungsi Klasifikasi Batch**

*Endpoint* `/classifier/run` memanggil fungsi `classify_dataframe()` yang menerima DataFrame hasil pembacaan CSV dan mengembalikan DataFrame yang sama dengan tambahan kolom hasil prediksi beserta probabilitasnya:

```python
# ml_utils.py — klasifikasi batch (disederhanakan)
def classify_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    model  = load_model()
    df     = _ohe_hari(df)

    rename_map = {
        'jam': 'Jam', 'menit': 'Menit', 'motor': 'Motor',
        'mobil': 'Mobil', 'bus': 'Bus', 'truk': 'Truk',
        'total_kendaraan': 'Total_Kendaraan',
    }
    df_feat = df.rename(columns=rename_map)

    X       = df_feat[FITUR].values
    y_pred  = model.predict(X)
    y_proba = model.predict_proba(X)       # probabilitas per kelas

    classes = list(model.classes_)         # ['Rendah', 'Sedang', 'Tinggi']

    df['tingkat_kepadatan'] = y_pred
    df['confidence']        = (np.max(y_proba, axis=1) * 100).round(1)
    for i, cls in enumerate(classes):
        df[f'proba_{cls.lower()}'] = (y_proba[:, i] * 100).round(1)

    return df
```

**Proses Retrain Model**

Ketika pengguna memulai proses *retrain* melalui halaman `/retrain`, fungsi `_do_retrain()` pada `app.py` mengekspor seluruh data dengan status `validated` dan `corrected` dari tabel `dataset` ke file `dataset_tervalidasi.csv`, kemudian memanggil `train_models.py` melalui *subprocess* Python. `train_models.py` menjalankan pelatihan Random Forest dengan *hyperparameter* tetap (*fixed params*) dari Skenario 1 terbaik hasil proses *modelling*—tanpa GridSearchCV—untuk menjamin *reproducibility* dan efisiensi waktu proses:

```python
# train_models.py — hyperparameter fixed Random Forest Skenario 1
RF_PARAMS = {
    'n_estimators'     : 200,
    'max_depth'        : 10,
    'min_samples_split': 2,
    'min_samples_leaf' : 1,
    'class_weight'     : 'balanced',
    'random_state'     : 42,
}
```

Setelah pelatihan selesai dengan pembagian data 80% latih dan 20% uji serta validasi silang *Stratified K-Fold* (k=5), `train_models.py` menyimpan model baru ke `models/model_aktif.pkl` dan memperbarui `models/metadata.json` yang memuat metrik evaluasi lengkap. Hasil *retrain* dicatat secara otomatis ke tabel `retrain_history` termasuk durasi proses dalam satuan detik, dan pengguna mendapatkan notifikasi ringkas melalui *flash message* yang menampilkan versi model, akurasi, dan waktu yang diperlukan.

Secara keseluruhan, sistem web SIKEDAT telah berhasil diimplementasikan dengan seluruh komponen berfungsi sebagaimana yang dirancang: unggah CSV dan klasifikasi *batch*, validasi *human-in-the-loop* dengan sistem antrian, visualisasi analitik multidimensi, pengelolaan data observasi, pencatatan log aktivitas, serta *retrain* model yang terotomasi. Sistem siap untuk diuji secara fungsional pada sub-bab 4.14 guna memverifikasi kesesuaian antara spesifikasi kebutuhan dan perilaku aktual sistem di lingkungan operasional.

---

## 5.5  Pembahasan Implementasi Sistem

Sub-bab ini membahas dasar pertimbangan teknis di balik setiap keputusan desain yang diambil selama pengembangan sistem web SIKEDAT, mengaitkannya dengan kebutuhan nyata Dinas Perhubungan Kota Surabaya serta tantangan implementasi yang dihadapi. Pembahasan mencakup empat aspek utama: justifikasi pemilihan teknologi, keputusan-keputusan teknis kritis, relevansi fitur terhadap rumusan masalah ketiga penelitian ini, dan cara-cara yang ditempuh untuk mengatasi kendala implementasi yang ditemui.

**5.5.1  Justifikasi Pemilihan Flask sebagai Framework Web**

Pemilihan Flask sebagai kerangka kerja pengembangan web bukan semata-mata keputusan teknis, melainkan keputusan yang mempertimbangkan secara holistik konteks penggunaan, skala operasional, dan ekosistem teknologi yang sudah ada. Pertama, Flask berbasis Python sehingga dapat berinteraksi secara langsung—tanpa lapisan perantara—dengan library *machine learning* seperti scikit-learn, pandas, numpy, dan joblib yang digunakan dalam modul prediksi dan pelatihan. Integrasi ini tidak mungkin se-mulus ini apabila menggunakan framework dari bahasa yang berbeda, seperti Node.js atau PHP. Kedua, sifat Flask yang *micro-framework* memberikan kebebasan penuh dalam menentukan arsitektur aplikasi; tidak ada konvensi direktori atau modul yang diwajibkan, sehingga pengembang dapat merancang struktur kode yang paling sesuai dengan kebutuhan spesifik sistem SIKEDAT. Ketiga, skala operasional DISHUB Surabaya untuk lokasi pemantauan Jalan Diponegoro—yang hanya melibatkan puluhan hingga ratusan baris data per sesi unggah—tidak memerlukan infrastruktur web yang berat seperti Django atau Spring Boot. Flask dengan SQLite sudah lebih dari cukup untuk menangani beban kerja tersebut tanpa overhead yang tidak perlu. Keempat, ekosistem *extension* Flask (Flask-Login, Flask-Bcrypt, Flask-SQLAlchemy) menyediakan solusi siap pakai untuk kebutuhan standar seperti autentikasi, enkripsi, dan ORM, sehingga waktu pengembangan dapat difokuskan pada logika bisnis yang bersifat domain-spesifik.

**5.5.2  Keputusan Teknis Penting**

Sejumlah keputusan teknis kritis dibuat selama proses implementasi yang masing-masing memiliki implikasi langsung terhadap keandalan dan kemudahan pemeliharaan sistem.

*Penggunaan joblib untuk serialisasi model.* Library `joblib` dipilih untuk menyimpan dan memuat model Random Forest (format `.pkl`) dibandingkan modul `pickle` bawaan Python. Keunggulan utamanya adalah efisiensi dalam menangani objek NumPy berukuran besar—komponen utama yang menyusun internal *estimator* Random Forest dengan 200 *estimator* pohon. Selain itu, penamaan file model secara konsisten sebagai `model_aktif.pkl` memungkinkan pergantian model setelah *retrain* dilakukan cukup dengan menimpa satu file, tanpa mengubah kode `app.py` sama sekali.

*Pemisahan modul ML dari kode Flask.* Seluruh logika *machine learning*—preprocessing, prediksi, dan pelatihan—dienkapsulasi dalam dua modul terpisah (`ml_utils.py` dan `train_models.py`) yang tidak mengimpor Flask sama sekali. Pendekatan ini memungkinkan pengujian modul ML secara mandiri dan memudahkan penggantian algoritma di masa mendatang tanpa menyentuh kode infrastruktur web.

*Retrain melalui subprocess Python.* Proses *retrain* dijalankan menggunakan `subprocess.run()` yang memanggil `train_models.py` sebagai proses terpisah, bukan dieksekusi langsung dalam *thread* Flask. Keputusan ini menghindari potensi *blocking* pada server web selama proses pelatihan yang berlangsung beberapa detik hingga menit, sekaligus memisahkan log output pelatihan dari log aplikasi web.

*One-Hot Encoding manual alih-alih sklearn.preprocessing.OneHotEncoder.* OHE untuk kolom `Hari` diimplementasikan secara manual menggunakan operasi perbandingan string, bukan menggunakan `OneHotEncoder` dari scikit-learn. Keputusan ini menghilangkan kebutuhan untuk menyimpan objek encoder sebagai file `.pkl` terpisah, menyederhanakan pipeline inferensi, dan menghilangkan risiko *version mismatch* antara encoder yang disimpan dengan versi scikit-learn yang terinstal.

*SQLite sebagai basis data.* Meskipun SQLite memiliki keterbatasan dalam konkurensi *write* yang tinggi, pilihan ini didasarkan pada pola penggunaan SIKEDAT yang bersifat *sequential*: satu pengguna mengklasifikasikan, kemudian satu pengguna memvalidasi, kemudian *retrain* dijalankan. Tidak ada skenario di mana banyak pengguna menulis ke basis data secara bersamaan dalam volume tinggi. SQLite menyederhanakan instalasi, *backup*, dan *deployment* karena seluruh basis data tersimpan dalam satu file `sikedat.db`.

**5.5.3  Fitur Unggulan Sistem yang Relevan dengan Kebutuhan DISHUB**

Rumusan masalah ketiga penelitian ini berfokus pada bagaimana membangun sistem web yang dapat mengintegrasikan model klasifikasi dan mendukung kebutuhan operasional Dinas Perhubungan Kota Surabaya secara berkelanjutan. Tiga fitur yang paling relevan dengan rumusan masalah tersebut adalah sebagai berikut.

*Pertama, mekanisme validasi Human-in-the-Loop.* Sistem tidak serta-merta mempercayai seluruh output model sebagai kebenaran. Setiap hasil klasifikasi harus melewati konfirmasi pakar (Analis atau Admin Dishub) sebelum dianggap valid. Mekanisme ini krusial mengingat model saat ini memiliki akurasi 73,30% dan F1-*score* 72,99%—artinya sekitar seperempat prediksi berpotensi tidak tepat. Dengan adanya tahap validasi, data yang digunakan untuk *retrain* berikutnya terjamin kualitasnya, sehingga model dapat terus meningkat seiring waktu dalam siklus yang berkelanjutan. Sistem antrian berbasis `batch_id` juga memastikan validator tidak melewatkan satu pun sesi klasifikasi.

*Kedua, fitur retrain model terotomasi.* Sistem dirancang agar model tidak bersifat statis. Ketika data tervalidasi terakumulasi dalam jumlah yang signifikan, operator Dishub dapat memulai proses pelatihan ulang langsung dari antarmuka web tanpa perlu keterlibatan pengembang. Sistem secara otomatis mengekspor data terbaru, melatih model baru dengan *hyperparameter* yang sudah dioptimalkan, menyimpan hasilnya, dan mencatat seluruh metrik evaluasi ke riwayat *retrain*. Fitur ini menjawab kebutuhan jangka panjang DISHUB yang memerlukan model yang dapat beradaptasi dengan perubahan pola lalu lintas dari waktu ke waktu.

*Ketiga, dashboard analitik multidimensi.* Di luar fungsi klasifikasi, sistem menyediakan delapan jenis visualisasi data yang memberikan wawasan operasional bagi petugas Dishub: pola kepadatan per jam, perbandingan hari kerja versus akhir pekan, rasio kendaraan berat, distribusi kelas kepadatan, dan heatmap hari × jam yang memperlihatkan jam-jam kritis secara sekilas. Informasi ini dapat digunakan sebagai bahan pengambilan keputusan operasional terkait penempatan petugas, pengaturan sinyal lalu lintas, atau perencanaan rekayasa jalan di Jalan Diponegoro Musi Utara Surabaya.

**5.5.4  Tantangan Implementasi dan Cara Mengatasinya**

Beberapa tantangan teknis ditemui selama proses implementasi dan diselesaikan melalui penyesuaian desain yang tepat.

*Tantangan 1: Ketidaksesuaian preprocessing antara fase modelling dan fase web.* Ditemukan bahwa web versi awal menggunakan LabelEncoder (1 kolom integer) untuk encoding hari dan MinMaxScaler untuk normalisasi fitur numerik, sementara model terbaik dari fase *modelling* dilatih menggunakan One-Hot Encoding (7 kolom biner) tanpa scaler. Ketidaksesuaian ini menyebabkan hasil prediksi web menjadi tidak valid secara statistik. Solusinya adalah menulis ulang seluruh pipeline preprocessing di `ml_utils.py` dan `train_models.py` agar konsisten dengan pipeline yang digunakan saat *modelling*, serta menetapkan konstanta `FITUR` dan `HARI_COLS` sebagai sumber kebenaran tunggal yang dirujuk di seluruh basis kode.

*Tantangan 2: Skala data dummy versus data real berbeda 10–15 kali lipat.* Data dummy yang digunakan selama pengembangan awal memiliki rentang nilai motor 28–78, sedangkan data real dari lapangan memiliki rentang 300–866. Hal ini menyebabkan beberapa komponen visual, seperti heatmap dan ambang warna grafik, yang dikalibrasi berdasarkan data dummy menjadi tidak informatif ketika diisi data real (semua sel heatmap tampak berwarna sama). Solusinya adalah mengganti nilai-nilai *hardcoded* dengan nilai yang dihitung secara dinamis dari data aktual yang tersimpan di basis data, termasuk nilai `maxV` pada heatmap yang kini dihitung sebagai `Math.max(...allVals)`.

*Tantangan 3: Retrain menggunakan GridSearchCV yang tidak efisien.* Implementasi awal fungsi *retrain* menjalankan kembali GridSearchCV penuh setiap kali dipanggil, yang berarti waktu *retrain* bisa mencapai puluhan menit untuk setiap iterasi. Hal ini tidak praktis dalam konteks operasional Dishub. Solusinya adalah mengganti GridSearchCV dengan pelatihan langsung menggunakan *fixed hyperparameter* terbaik dari Skenario 1 (hasil eksperimen *modelling*), sehingga proses *retrain* kini selesai dalam hitungan belasan detik.

*Tantangan 4: Pengelolaan versi model.* Seiring bertambahnya iterasi *retrain*, diperlukan mekanisme untuk melacak sejarah model dan memungkinkan pemulihan ke versi sebelumnya apabila model baru ternyata berperforma lebih buruk. Solusinya adalah tabel `retrain_history` yang mencatat setiap versi beserta metrik evaluasinya secara lengkap, ditambah fitur "Aktifkan Model" yang memungkinkan operator memilih versi model mana yang aktif digunakan untuk klasifikasi tanpa perlu manipulasi file secara manual.

Secara keseluruhan, proses implementasi sistem web SIKEDAT menghasilkan aplikasi yang tidak hanya berfungsi sebagai alat klasifikasi otomatis, tetapi juga sebagai sistem manajemen pengetahuan yang memungkinkan Dinas Perhubungan Kota Surabaya untuk terus membangun dan memperbaiki kapabilitas prediktif mereka secara mandiri dan berkelanjutan.
