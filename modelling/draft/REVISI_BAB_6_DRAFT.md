# BAB VI  KESIMPULAN DAN SARAN

## 6.1  Kesimpulan

Berdasarkan hasil penelitian yang telah dilakukan, dapat ditarik kesimpulan sebagai berikut sesuai dengan rumusan masalah yang ditetapkan:

**1. Implementasi YOLOv8 untuk Ekstraksi Fitur Volume dan Komposisi Kendaraan**

Sistem *Computer Vision* berbasis YOLOv8 + DeepSORT berhasil diimplementasikan untuk mengekstraksi volume dan komposisi kendaraan (Motor, Mobil, Bus, Truk) secara otomatis dari rekaman CCTV Jalan Diponegoro Musi Utara Surabaya. Model YOLOv8 dilatih ulang menggunakan dataset *Vehicle Detection Computer Vision Model* (1.000 gambar) dari platform Roboflow untuk menggantikan model generik COCO yang menghasilkan deteksi tidak akurat pada konteks lalu lintas Indonesia. Hasil ekstraksi menghasilkan dataset berisi 877 baris data dengan interval agregasi 10 menit, yang selanjutnya menjadi masukan proses klasifikasi. Nilai MAPE yang diperoleh menunjukkan akurasi ekstraksi yang `[TODO: isi kategori — sangat baik/baik/cukup]`, dengan catatan penurunan performa deteksi pada kondisi pencahayaan rendah (jam 17.30–20.00 WIB). Upaya mitigasi telah dilakukan melalui eksperimen tambahan menggunakan dataset *Traffic Night* (5.400 gambar), namun hasilnya menunjukkan misklasifikasi yang lebih parah sehingga model utama tetap digunakan untuk seluruh proses ekstraksi.

**2. Perbandingan Performa Random Forest dan SVM**

Dari empat model yang diuji (Random Forest dan SVM masing-masing pada dua skenario dataset), hasil komparasi menunjukkan bahwa **Random Forest secara konsisten mengungguli SVM** pada kedua skenario. Model terbaik adalah **Random Forest Skenario 1** dengan konfigurasi `n_estimators=200`, `max_depth=10`, `min_samples_split=2`, dan `min_samples_leaf=1`, yang mencapai:

- *Accuracy*: **73,30%**
- *Precision* (weighted): **73,18%**
- *Recall* (weighted): **73,30%**
- *F1-score* (weighted): **72,99%**

Keunggulan Random Forest dapat dikaitkan dengan kemampuannya menangani interaksi non-linear antar fitur dan sifatnya yang *scale-invariant*, sehingga lebih cocok untuk dataset volume kendaraan yang berdistribusi tidak normal dan memiliki fitur dengan rentang nilai yang heterogen.

**3. Penyajian Hasil Klasifikasi sebagai Bahan Pertimbangan DISHUB**

Model klasifikasi terbaik (Random Forest Skenario 1) berhasil diintegrasikan ke dalam aplikasi web berbasis Flask yang dapat digunakan oleh staf DISHUB Surabaya untuk melakukan klasifikasi tingkat kepadatan lalu lintas secara mandiri. Sistem ini mampu mengklasifikasikan kondisi lalu lintas ke dalam tiga kelas (Rendah, Sedang, Tinggi) beserta visualisasi dashboard berupa distribusi volume kendaraan per jenis dan pola kepadatan per jam, yang dapat dijadikan dasar pengambilan keputusan taktis pengelolaan lalu lintas. Pengujian *usability* dengan metode SUS memperoleh skor rata-rata `[TODO: isi skor SUS]`, yang termasuk dalam kategori `[TODO: isi kategori SUS]`.

---

## 6.2  Saran

Berdasarkan hasil dan keterbatasan penelitian yang telah diidentifikasi, berikut adalah saran untuk penelitian dan pengembangan selanjutnya:

1. **Peningkatan akurasi deteksi pada kondisi malam hari.** Penelitian ini mengidentifikasi penurunan signifikan akurasi deteksi YOLOv8 pada jam 17.30–20.00 WIB. Penelitian lanjutan dapat menggunakan teknik *image enhancement* seperti koreksi gamma atau CLAHE pada frame sebelum diproses YOLOv8, atau melakukan training ulang model dengan dataset yang mencakup kondisi *low-light* dan pencahayaan lampu kendaraan secara representatif.

2. **Penerapan metrik analisis kapasitas jalan yang lebih komprehensif.** Sebagaimana disarankan oleh pakar lapangan DISHUB Surabaya, pengembangan ke depan dapat mengintegrasikan *Satuan Mobil Penumpang* (SMP), *Volume to Capacity Ratio* (V/C Ratio), dan *Level of Service* (LOS) sesuai MKJI 1997, untuk memperoleh label tingkat kepadatan yang lebih akurat secara teknis rekayasa lalu lintas.

3. **Perluasan cakupan data dan lokasi pengamatan.** Penelitian ini hanya menggunakan satu titik CCTV pada satu ruas jalan. Pengembangan ke depan dapat memperluas cakupan ke beberapa ruas jalan strategis di Kota Surabaya dengan variasi karakteristik jalan yang berbeda, sehingga model yang dihasilkan memiliki generalisasi yang lebih baik.

4. **Penyempurnaan metode labeling dengan *multi-rater agreement*.** Proses labeling frekuensi *cycle failure* pada penelitian ini dilakukan oleh satu peneliti. Penelitian lanjutan disarankan melibatkan beberapa labeler independen dengan pengukuran *inter-rater reliability* (misalnya *Cohen's Kappa*) untuk meningkatkan objektivitas dan keandalan label data.

5. **Eksplorasi algoritma machine learning lainnya.** Penelitian ini membandingkan dua algoritma (Random Forest dan SVM). Penelitian lanjutan dapat mengeksplorasi algoritma lain seperti *Gradient Boosting* (XGBoost, LightGBM) atau *deep learning* berbasis LSTM untuk menangkap pola temporal pada data time-series lalu lintas, mengingat data per 10 menit memiliki karakteristik runtun waktu yang dapat dimanfaatkan.

6. **Integrasi sistem dengan data CCTV secara *real-time*.** Sistem yang dikembangkan saat ini berjalan dengan data historis (upload CSV). Pengembangan ke depan dapat mengintegrasikan pipeline YOLOv8 secara langsung dengan feed CCTV SITS DISHUB Surabaya untuk memungkinkan klasifikasi kepadatan secara *real-time*.
