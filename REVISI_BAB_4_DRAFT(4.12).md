
---

## 4.12  Hasil Perancangan Sistem

Perancangan sistem SIKEDAT (*Sistem Klasifikasi Kepadatan*) dilakukan menggunakan Use Case Diagram dan Activity Diagram untuk memvisualisasikan interaksi antara pengguna dengan sistem serta alur aktivitas yang terjadi di dalamnya secara terstruktur.

### 4.12.1  Use Case Diagram

Use Case Diagram sistem SIKEDAT menggambarkan fungsionalitas sistem dari perspektif pengguna. Sistem memiliki **empat aktor** yang dihubungkan melalui relasi *generalization* (pewarisan UML): **Masyarakat** sebagai pengguna publik tanpa autentikasi; **Staff** sebagai peran dasar pengguna terautentikasi; **Analis** yang mewarisi seluruh kemampuan Staff dan memiliki tambahan akses ke fitur pengelolaan data; serta **Admin** yang mewarisi seluruh kemampuan Analis dan memiliki hak eksklusif atas manajemen akun pengguna. Relasi *generalization* antar aktor ditandai dengan panah segitiga kosong yang mengarah dari aktor khusus (*child*) ke aktor umum (*parent*): Staff ← Analis ← Admin, yang berarti setiap aktor yang lebih khusus mewarisi seluruh *use case* dari aktor yang lebih umum. Gambar 4.18 menyajikan diagram *use case* sistem secara keseluruhan.

![Gambar 4.18 Diagram Use Case Sistem SIKEDAT](diagram_usecase.png)

**Gambar 4.18**  Diagram *use case* sistem SIKEDAT.

Terdapat sepuluh *use case* dalam sistem ini yang terdistribusi sesuai peran masing-masing aktor. **Login** merupakan *use case* gerbang akses bagi Staff, Analis, dan Admin ke seluruh fitur operasional sistem, sementara Masyarakat dapat langsung menggunakan fitur prediksi tanpa autentikasi. **Melihat prediksi kepadatan lalu lintas** dapat diakses oleh Masyarakat tanpa *login*, menyajikan estimasi tingkat kepadatan berdasarkan input hari, jam, dan menit. **Melihat dashboard statistik kepadatan lalu lintas** menyediakan visualisasi analitik multidimensi bagi seluruh pengguna terautentikasi (Staff, Analis, dan Admin), mencakup pola kepadatan per jam, komposisi kendaraan, dan perbandingan *weekday* vs *weekend*. **Melihat data observasi** memungkinkan seluruh pengguna terautentikasi mengakses tabel rekaman data hasil klasifikasi beserta status validasinya dengan fitur filter dan paginasi. **Mengupload dan mengklasifikasikan data CSV** memungkinkan Analis dan Admin mengunggah hasil ekstraksi dari *pipeline* YOLOv8+DeepSORT untuk diklasifikasikan secara *batch* oleh model. **Memvalidasi dan mengoreksi hasil klasifikasi** memungkinkan Analis dan Admin meninjau, mengonfirmasi, atau mengoreksi label prediksi model sebelum data dinyatakan valid. **Menyimpan data** mencatat hasil klasifikasi beserta status validasinya ke dalam basis data secara permanen. **Melatih ulang model** memungkinkan Analis dan Admin memperbarui model menggunakan seluruh data yang telah tervalidasi, sehingga akurasi sistem dapat terus meningkat seiring bertambahnya data. **Melihat log aktivitas** memungkinkan Analis dan Admin memantau riwayat seluruh aktivitas sistem — klasifikasi, validasi, dan *retrain* — secara kronologis dalam satu halaman terpadu. **Mengelola akun pengguna** merupakan *use case* eksklusif Admin untuk membuat, mengedit, serta mengaktifkan atau menonaktifkan akun pengguna sistem.

### 4.12.2  Activity Diagram

Activity Diagram menggambarkan alur proses bisnis sistem SIKEDAT secara keseluruhan berdasarkan masing-masing peran pengguna. Gambar 4.19 menyajikan activity diagram sistem dengan empat *swimlane* yang merepresentasikan keempat peran yang ada: Public (tanpa login), Staff, Analis, dan Admin.

`[TODO: Insert Gambar 4.19 — Activity Diagram Sistem SIKEDAT]`

**Gambar 4.19**  Activity diagram sistem SIKEDAT per peran pengguna.

Dari Gambar 4.19 terlihat bahwa alur sistem dimulai dari *decision point* apakah pengguna melakukan *login* atau tidak. Pengguna tanpa *login* (Public) hanya dapat mengakses beranda dan fitur prediksi kepadatan secara langsung. Pengguna yang berhasil *login* diarahkan ke alur yang sesuai dengan perannya: Staff dapat mengakses *dashboard* analitik, data observasi, dan log aktivitas; Analis memiliki semua akses Staff ditambah kemampuan mengupload data CSV, menjalankan klasifikasi *batch*, memvalidasi dan mengoreksi hasil prediksi, menyimpan data ke basis data, serta menjalankan *retrain* model; sementara Admin memiliki seluruh akses Analis ditambah fitur khusus pengelolaan akun pengguna. Seluruh alur berkonvergensi ke *end node* setelah masing-masing peran menyelesaikan aktivitasnya.

### 4.12.3  Fitur Dashboard Statistik

Fitur dashboard statistik dalam sistem ini bertujuan untuk mentransformasi data mentah hasil klasifikasi menjadi informasi analitis yang aplikatif bagi pengguna. Melalui fitur ini, sistem menyajikan empat kategori insight utama yang diekstraksi dari hasil pemrosesan data, yaitu:

1. **Distribusi Volume Kendaraan per Jenis**: Memberikan informasi mendetail mengenai jumlah setiap jenis kendaraan (motor, mobil, bus, dan truk) yang melintasi Jalan Diponegoro setiap harinya.
2. **Pola Temporal Kepadatan (Harian dan Jam)**: Memvisualisasikan tren fluktuasi kepadatan lalu lintas untuk mengidentifikasi jam puncak (*peak hours*) pada setiap hari, sehingga dapat dipetakan secara akurat kapan kemacetan mulai terbentuk dan berakhir.
3. **Analisis Rasio Kendaraan Berat (*Heavy Vehicle Mix*)**: Menyajikan persentase kendaraan besar (bus dan truk) terhadap total volume kendaraan. Data ini krusial mengingat kendaraan berat memiliki nilai Satuan Mobil Penumpang (SMP) yang lebih tinggi dan berdampak signifikan terhadap degradasi kapasitas jalan.
4. **Komparasi Karakteristik Lalu Lintas (Weekday vs Weekend)**: Menyediakan analisis perbandingan perilaku lalu lintas antara hari kerja dan akhir pekan guna mengidentifikasi pergeseran pola aktivitas masyarakat di pusat kota.

Seluruh informasi analitis tersebut dikemas dalam bentuk visualisasi grafik yang interaktif, yang memberikan manfaat nyata berupa: optimalisasi manajemen lalu lintas, efisiensi alokasi sumber daya, pendukung keputusan infrastruktur, dan mitigasi dampak sosial serta ekonomi.

---
