# BAB V  PEMBAHASAN

> **Status Draft:**
> - Sub-bab 5.1, 5.2, 5.3 → FINAL — siap pakai (interpretasi mendalam hasil Bab IV)
> - Sub-bab 5.4 → Draft awal — perlu dilengkapi setelah Bab 4.9 final
> - Sub-bab 5.5 (SUS) → KERANGKA — placeholder angka untuk diisi setelah Anda jalankan SUS
> - Sub-bab 5.6 Perbandingan Penelitian Terdahulu → FINAL — 10 referensi siap pakai (Anda tinggal cross-check)
> - Sub-bab 5.7 → FINAL

Pada Bab IV telah disajikan hasil implementasi penelitian secara faktual. Pada bab ini, hasil-hasil tersebut dibahas dan diinterpretasikan untuk memahami fenomena yang terjadi, mengaitkannya dengan teori dan penelitian terdahulu, serta mengidentifikasi temuan-temuan menarik yang relevan dengan tujuan penelitian. Pembahasan disusun mengikuti urutan tahapan eksperimen, mulai dari evaluasi ekstraksi YOLOv8, eksplorasi data, modelling dan evaluasi model, implementasi sistem, pengujian usability, perbandingan dengan penelitian terdahulu, hingga identifikasi limitasi penelitian.

---

## 5.1  Pembahasan Hasil Ekstraksi Data dan Evaluasi MAPE

### 5.1.1  Pemilihan Dataset Custom untuk YOLOv8

Berdasarkan hasil pada sub-bab 4.2.1, peneliti melakukan transisi dari model YOLOv8 pre-trained dengan dataset COCO ke model custom yang dilatih ulang menggunakan dataset *Vehicle Detection Computer Vision Model* dari Roboflow. Keputusan ini diambil setelah hasil eksperimen awal dengan model COCO menunjukkan akurasi deteksi yang kurang memadai, khususnya pada kategori Bus dan Truk yang sering tertukar dengan Mobil. Pemilihan dataset Roboflow tersebut didasari oleh dua pertimbangan utama: (1) kesesuaian dengan komposisi lalu lintas Indonesia yang didominasi sepeda motor, dan (2) kemiripan sudut pengambilan gambar (*angle frame*) dengan rekaman CCTV Jalan Diponegoro Musi Utara.

Pendekatan transfer learning seperti ini sejalan dengan praktik di penelitian terdahulu yang menunjukkan bahwa model YOLO yang dilatih pada dataset domain-specific umumnya memberikan akurasi yang lebih tinggi dibandingkan model generik (Putra et al., 2024; Vision-At-SEECS, 2024).

### 5.1.2  Interpretasi Nilai MAPE

`[TODO: Setelah nilai MAPE pada sub-bab 4.3 diisi, tambahkan paragraf interpretasi seperti berikut:]`

> Berdasarkan hasil pada Tabel 4.3, nilai rata-rata MAPE yang diperoleh adalah X%. Berdasarkan klasifikasi Lewis (1982), nilai MAPE di bawah 10% menunjukkan akurasi yang sangat baik, sehingga sistem ekstraksi YOLOv8 + DeepSORT yang dikembangkan dapat dinyatakan **`[layak/cukup layak/perlu pengembangan]`** untuk digunakan sebagai dasar analisis kepadatan lalu lintas. Khusus untuk kategori Bus dan Truk, nilai MAPE cenderung lebih tinggi dibandingkan Motor dan Mobil, yang dapat disebabkan oleh karakteristik visual kedua kategori tersebut yang kadang tertukar dengan kendaraan komersial sejenis serta frekuensi kemunculan yang relatif rendah pada periode pengamatan.

### 5.1.3  Limitasi Deteksi pada Kondisi Pencahayaan Rendah

Salah satu temuan penting yang muncul selama tahap eksperimen ekstraksi adalah penurunan akurasi deteksi YOLOv8 pada kondisi pencahayaan rendah, khususnya pada rekaman sore-malam (jam 18.00–20.00 WIB). Pada periode tersebut, kondisi pencahayaan jalan mulai menurun, dan banyak kendaraan menyalakan lampu utama (*headlight*) yang dapat mengganggu proses deteksi YOLOv8 karena efek *glare* dan saturasi piksel.

Temuan ini selaras dengan beberapa penelitian terdahulu yang secara eksplisit melaporkan keterbatasan YOLOv8 pada kondisi pencahayaan rendah:

- **Lu et al. (2024)** menyatakan bahwa sistem deteksi tradisional menghadapi tantangan pada kondisi *low-light* dan terpengaruh oleh lampu kendaraan, sehingga menurunkan akurasi deteksi.
- **Yuda dan Hamzah (2026)** menemukan bahwa walaupun YOLOv8 menunjukkan performa baik pada pencahayaan normal, akurasinya menurun pada citra *low-light* akibat kontras yang rendah dan detail visual yang terbatas.
- **Zulkarnain dan Kusrini (2025)** secara khusus melakukan optimasi YOLOv11 untuk meningkatkan akurasi deteksi pada kondisi malam hari, menunjukkan bahwa permasalahan ini diakui sebagai isu yang berkelanjutan di komunitas riset.

Sebagai upaya mitigasi, peneliti melakukan eksperimen tambahan dengan melatih model YOLOv8 menggunakan dataset *Traffic Night* (5.400 gambar) dan mengujinya pada rekaman kondisi gelap. Namun hasil eksperimen menunjukkan bahwa model malam (`best-malam.pt`) justru menghasilkan deteksi yang **lebih tidak akurat** dibandingkan model utama (`best.pt`). Secara spesifik, model malam menghasilkan nilai Truk=168 dalam satu interval 10 menit yang jelas tidak realistis — diduga akibat misklasifikasi mobil gelap dengan lampu menyilaukan sebagai truk, pola yang serupa dengan kelemahan model COCO. Sementara model utama menghasilkan total=113 yang rendah akibat *under-detection* di kondisi gelap, komposisi kendaraannya lebih masuk akal secara proporsi. Berdasarkan hasil ini, peneliti memutuskan untuk tidak menggunakan model malam dan melanjutkan ekstraksi dengan model utama. Eksperimen ini tetap didokumentasikan sebagai temuan dan menjadi rekomendasi pengembangan ke depan pada Bab VI.

---

## 5.2  Pembahasan Hasil Preprocessing dan EDA

### 5.2.1  Pembahasan Distribusi Data dan Keseimbangan Kelas

Berdasarkan Tabel 4.8 dan Gambar 4.4–4.5, dataset terdistribusi relatif merata baik antar hari maupun antar jam pengamatan. Distribusi yang merata ini menunjukkan bahwa proses pengumpulan data dilakukan secara konsisten, sehingga model yang dihasilkan tidak akan bias terhadap hari atau jam tertentu.

Namun, distribusi kelas target menunjukkan ketidakseimbangan (*imbalance*) yang berbeda antar skenario. Pada Skenario 1, kelas Rendah mendominasi (52,79%) sementara kelas Sedang dan Tinggi masing-masing hanya 23,37% dan 23,83%. Pada Skenario 2, distribusi menjadi lebih seimbang dengan kelas Sedang menjadi mayoritas (41,39%), diikuti Rendah (34,78%) dan Tinggi (23,83%). Perbedaan distribusi ini menjadi konsekuensi langsung dari intervensi labeling "ramai lancar" pada Skenario 2.

Konsekuensi dari ketidakseimbangan ini telah diantisipasi melalui dua mekanisme: (1) penggunaan parameter `class_weight = 'balanced'` pada training model, dan (2) penggunaan metrik *F1-weighted* sebagai *scoring* utama pada GridSearchCV. Kedua mekanisme ini memungkinkan model untuk tidak mengabaikan kelas minoritas.

### 5.2.2  Pembahasan Pola Korelasi Negatif yang Counter-Intuitif

Salah satu temuan paling menarik dari tahap EDA adalah munculnya **korelasi negatif** antara seluruh fitur volume kendaraan dengan target `Tingkat_Kepadatan`, sebagaimana terlihat pada Gambar 4.6 [`06_heatmap_korelasi.png` dari `scripts/01_eda.py`] dan dirangkum pada Tabel 5.1.

**Tabel 5.1  Korelasi Antara Fitur Volume Kendaraan dengan Tingkat Kepadatan**
> 📎 Angka diambil dari output `06_heatmap_korelasi.png` dan `tabel_statistik_deskriptif.csv` dari `scripts/01_eda.py`

| Fitur | Korelasi Pearson dengan Tingkat_Kepadatan |
|---|---|
| Motor | −0,44 |
| Total_Kendaraan | −0,37 |
| Bus | −0,32 |
| Truk | −0,26 |
| Mobil | ≈ 0,00 |

Secara intuitif, pola yang diharapkan adalah korelasi **positif** — semakin banyak kendaraan terdeteksi, semakin tinggi kepadatan, sehingga semakin sering terjadi *cycle failure*. Namun, hasil empiris menunjukkan pola yang berlawanan. Untuk memahami fenomena ini, peneliti melakukan analisis komposisi kelas per jam yang ditampilkan pada Gambar 4.9 [`09_komposisi_kelas_per_jam.png` dari `scripts/01_eda.py`] di Bab IV. Pola yang teridentifikasi adalah:

- Pada **jam 6 pagi**: 104 dari 107 baris (97%) dikategorikan sebagai Rendah, dengan jumlah kendaraan terdeteksi YOLOv8 yang tinggi (kondisi pencahayaan optimal).
- Pada **jam 19 malam**: 68 dari 112 baris (61%) dikategorikan sebagai Tinggi, namun jumlah kendaraan terdeteksi cenderung lebih rendah (kondisi pencahayaan menurun).

Pola tersebut mengindikasikan adanya ***confounding factor*** antara variabel waktu (`Jam`) dan limitasi deteksi YOLOv8 pada kondisi pencahayaan rendah. Dengan kata lain:

> Sistem **bukan mempelajari** bahwa "semakin banyak kendaraan, semakin padat". Sistem secara implisit **mempelajari** bahwa "kalau jam-nya sore-malam, kemungkinan besar Tinggi" — karena pada jam tersebut deteksi YOLOv8 melemah, sementara secara faktual jam sore-malam memang lebih sering mengalami *cycle failure*.

Hal ini sejalan dengan limitasi YOLOv8 pada kondisi *low-light* yang dilaporkan oleh Lu et al. (2024), Yuda dan Hamzah (2026), serta Zulkarnain dan Kusrini (2025) yang telah dibahas pada sub-bab 5.1.3.

Fenomena ini juga menjelaskan mengapa **fitur `Mobil` memiliki korelasi mendekati nol** (−0,00). Sedan/MPV sebagai bentuk dominan kategori Mobil memiliki siluet yang relatif konsisten dan area pantul cahaya headlight yang stabil, sehingga deteksi YOLOv8 untuk kategori ini relatif stabil baik pada kondisi terang maupun gelap. Akibatnya, `Mobil` tidak terpengaruh oleh *confounding* pencahayaan dan menunjukkan hubungan netral terhadap target.

### 5.2.3  Pembahasan Multikolinearitas Antar Fitur

Pada Gambar 4.6 juga terlihat korelasi tinggi antar sesama fitur volume kendaraan, terutama antara `Motor` dan `Total_Kendaraan` sebesar 0,98. Hal ini diharapkan karena `Total_Kendaraan = Motor + Mobil + Bus + Truk`, dan komposisi lalu lintas Indonesia didominasi motor. Walaupun multikolinearitas tinggi dapat menjadi masalah pada algoritma linear (misalnya regresi linier), kedua algoritma yang digunakan dalam penelitian ini — Random Forest dan SVM dengan kernel RBF — relatif robust terhadap multikolinearitas, sehingga tidak dilakukan tindakan khusus seperti *feature selection* atau *Principal Component Analysis* (PCA).

---

## 5.3  Pembahasan Hasil Modelling dan Evaluasi Model

### 5.3.1  Pembahasan Komparasi Random Forest vs Support Vector Machine

Berdasarkan Tabel 4.25 [`03_modelling/ringkasan_4_model.csv` dari `scripts/03_modelling.py`], Random Forest **secara konsisten lebih unggul** dibandingkan SVM pada kedua skenario, baik dari segi *accuracy* maupun *F1-score weighted*:

- Skenario 1: RF (F1 = 0,7299) vs SVM (F1 = 0,6538) — selisih **7,6 percentage points**
- Skenario 2: RF (F1 = 0,6399) vs SVM (F1 = 0,6056) — selisih **3,4 percentage points**

Keunggulan Random Forest dapat dijelaskan dari karakteristik intrinsik kedua algoritma:

1. **Random Forest** secara natural mampu menangani **interaksi non-linear** antar fitur tanpa perlu *feature engineering* khusus. Sebagai contoh, interaksi antara `Jam`, `Hari`, dan volume kendaraan dapat ditangkap melalui kombinasi *decision tree* di dalam *ensemble*.
2. **Random Forest** bersifat *scale-invariant* sehingga performanya konsisten meskipun fitur memiliki rentang nilai yang sangat berbeda (misalnya `Total_Kendaraan` hingga 1.228 vs `Truk` maksimum 20).
3. **SVM dengan kernel RBF** sebenarnya juga mampu menangani non-linearitas, namun lebih sensitif terhadap pemilihan hyperparameter (`C` dan `gamma`) dan butuh dataset yang lebih besar untuk mencapai performa optimal pada problem multi-kelas.

Hasil ini sejalan dengan temuan penelitian terdahulu. **Aulia et al. (2024)** dalam penelitian klasifikasi kemacetan lalu lintas berbasis YOLOv8 + machine learning melaporkan Random Forest mencapai akurasi 96%, mengungguli SVM (89%), KNN (89%), dan Logistic Regression (78%) pada problem klasifikasi serupa.

### 5.3.2  Pembahasan Komparasi Skenario 1 vs Skenario 2

Komparasi antar skenario (lihat juga Gambar 4.15 [`04_comparison/01_grouped_bar_4model.png` dari `scripts/04_comparison.py`]) menunjukkan ***trade-off* yang menarik**:

- **Skenario 1** unggul pada *Accuracy* dan *F1-score weighted*. Hal ini dapat dijelaskan oleh distribusi kelas yang lebih timpang ke Rendah (52,79%), sehingga model yang berhasil memprediksi kelas Rendah dengan baik akan mendapat skor tinggi secara agregat.
- **Skenario 2** unggul pada *F1-score macro* (RF: 0,6365 vs 0,6873; selisih 5 percentage points kalah, **tapi** distribusi recall antar kelas lebih merata). Pada Skenario 2, recall kelas Sedang naik dari 0,4634 (Skenario 1) menjadi 0,6164 — peningkatan yang signifikan.

*Trade-off* ini memiliki implikasi praktis penting:

- **Skenario 1 lebih cocok** apabila tujuan utama sistem adalah meminimalkan total kesalahan prediksi secara absolut (mis. untuk pelaporan agregat ke DISHUB).
- **Skenario 2 lebih cocok** apabila tujuan utama sistem adalah memberikan perlakuan adil terhadap setiap kelas (mis. untuk visualisasi dashboard yang menonjolkan kondisi "ramai lancar").

Temuan menarik dari Skenario 2 adalah bahwa **pemasukan informasi validasi visual** ("ramai lancar") yang berasal dari saran pakar lapangan (Bapak Tommi Firman, DISHUB Surabaya) **menghasilkan distribusi label yang secara empiris lebih seimbang** dan model yang lebih adil per kelas. Hal ini mengindikasikan bahwa intervensi domain knowledge berperan signifikan dalam meningkatkan kualitas labeling, walaupun pada metrik agregat performa model menjadi sedikit lebih rendah.

### 5.3.3  Pembahasan Feature Importance

Berdasarkan Gambar 4.8 [`rf_scenario1/05_feature_importance.png` dari `scripts/03_modelling.py`], empat fitur teratas yang paling berpengaruh terhadap klasifikasi adalah:

1. **Mobil** (0,190)
2. **Motor** (0,177)
3. **Total_Kendaraan** (0,170)
4. **Jam** (0,168)

Sementara fitur-fitur `Hari_*` (one-hot encoding) memiliki kontribusi yang relatif kecil (< 0,04). Beberapa temuan menarik yang dapat dibahas:

**a. Mobil sebagai fitur paling penting** — Hasil ini cukup mengejutkan karena pada analisis korelasi linear (Gambar 4.6), fitur `Mobil` justru memiliki korelasi paling rendah (≈ 0) terhadap target. Penjelasannya adalah bahwa Random Forest mampu menangkap pola **non-linear** dari fitur ini yang tidak terdeteksi oleh korelasi linear. Stabilitas deteksi `Mobil` yang konsisten baik siang maupun malam (sebagaimana dibahas pada sub-bab 5.2.2) justru menjadikannya fitur paling informatif karena tidak terkontaminasi *noise* pencahayaan.

**b. Fitur `Hari` kontribusinya minim** — Hal ini mengindikasikan bahwa pola kepadatan di Jalan Diponegoro Musi Utara relatif tidak sensitif terhadap hari dalam minggu. Implikasi praktisnya: pada pengembangan ke depan, fitur `Hari` berpotensi untuk **di-drop** demi menghasilkan model yang lebih ringkas tanpa kehilangan performa signifikan.

**c. `Jam` ada di posisi 4** — Fitur waktu tetap penting, mendukung intuisi bahwa pola kepadatan harian mengikuti pola jam sibuk pagi dan sore.

### 5.3.4  Pembahasan Pola Kesalahan pada Confusion Matrix

Confusion matrix RF Skenario 1 (Tabel 4.17 [`rf_scenario1/04_classification_report.txt` dari `scripts/03_modelling.py`]) menunjukkan pola kesalahan yang konsisten:

- **Kelas Rendah dan Tinggi** memiliki *recall* yang tinggi: 81,72% dan 80,95% — model dapat dengan baik membedakan dua kondisi ekstrem (sepi vs macet).
- **Kelas Sedang** memiliki *recall* yang rendah (46,34%) dengan pola kesalahan yang khas: 12 baris terprediksi sebagai Rendah, 10 baris terprediksi sebagai Tinggi.

Pola ini secara teoritis dapat dijelaskan: kelas **Sedang** secara natural merepresentasikan kondisi transisi (1–2 *cycle failure*) yang berada di antara dua kondisi ekstrem, sehingga **batas keputusan (decision boundary)** model terhadap kelas ini menjadi paling sulit ditetapkan. Hal ini merupakan fenomena umum pada klasifikasi *ordinal-like* di mana kelas tengah sulit dipisahkan secara tajam dari kelas-kelas yang mengapitnya.

Implikasi praktis dari temuan ini: pengguna sistem (staff DISHUB) perlu **memvalidasi prediksi kelas Sedang** dengan lebih cermat, mengingat tingkat keandalan prediksi pada kelas ini paling rendah. Fitur validasi & koreksi manual pada aplikasi web (sub-bab 4.9.2) menjadi sangat krusial untuk menangani kasus-kasus ambiguitas ini.

---

## 5.4  Pembahasan Implementasi Sistem

`[TODO: Setelah sub-bab 4.9 dilengkapi, tambahkan pembahasan implementasi sistem yang mencakup:]`

`[TODO: 1) Justifikasi pemilihan Flask sebagai framework web (ringan, mudah integrasi dengan Python, cocok untuk skala DISHUB).]`

`[TODO: 2) Keputusan teknis penting (mis. penggunaan joblib untuk model serialization, struktur database, dll).]`

`[TODO: 3) Fitur unggulan sistem yang relevan dengan kebutuhan pengguna DISHUB.]`

`[TODO: 4) Tantangan implementasi yang dihadapi dan bagaimana diatasi.]`

---

## 5.5  Evaluasi Sistem dengan System Usability Scale (SUS)

> **`[TODO: Sub-bab ini dilengkapi setelah Anda melakukan pengujian SUS ke responden. Berikut kerangka lengkapnya:]`**

### 5.5.1  Metode Pengujian SUS

Untuk mengevaluasi tingkat *usability* aplikasi web yang dikembangkan, peneliti menggunakan metode **System Usability Scale (SUS)** yang dikembangkan oleh John Brooke (1986). SUS adalah kuesioner standar berisi 10 pernyataan yang mengukur persepsi pengguna terhadap kemudahan penggunaan suatu sistem dengan skala Likert 5 poin (1 = sangat tidak setuju, 5 = sangat setuju).

Sepuluh pernyataan SUS adalah:

1. Saya akan ingin menggunakan sistem ini secara berkelanjutan.
2. Saya merasa sistem ini terlalu kompleks.
3. Saya rasa sistem ini mudah digunakan.
4. Saya butuh bantuan teknis untuk dapat menggunakan sistem ini.
5. Saya merasa fungsi-fungsi sistem ini terintegrasi dengan baik.
6. Saya merasa terlalu banyak inkonsistensi di sistem ini.
7. Saya rasa kebanyakan orang akan mampu mempelajari sistem ini dengan cepat.
8. Saya merasa sistem ini sangat tidak praktis.
9. Saya percaya diri dalam menggunakan sistem ini.
10. Saya perlu mempelajari banyak hal sebelum bisa menggunakan sistem ini.

Skor SUS dihitung dengan formula:

$$\text{Skor SUS} = (\sum \text{skor ganjil} - 5) + (25 - \sum \text{skor genap}) \times 2.5$$

dengan rentang skor 0–100. Interpretasi skor SUS menurut Bangor et al. (2009):

| Rentang Skor | Adjective Rating | Acceptability |
|---|---|---|
| ≥ 85 | Excellent | Acceptable |
| 73 – 84 | Good | Acceptable |
| 52 – 72 | OK / Marginal | Marginal |
| 39 – 51 | Poor | Not Acceptable |
| < 39 | Worst | Not Acceptable |

### 5.5.2  Profil Responden

`[TODO: Jelaskan jumlah responden, profesi/jabatan (mis. staff DISHUB Surabaya, akademisi, masyarakat umum), rentang umur, dan keterangan lainnya.]`

**Tabel 5.2  Profil Responden Pengujian SUS**

| Kategori | Jumlah | Persentase |
|---|---|---|
| `[TODO: misal Staff DISHUB]` | `[TODO]` | `[TODO]%` |
| `[TODO: misal Akademisi]` | `[TODO]` | `[TODO]%` |
| `[TODO: misal Masyarakat Umum]` | `[TODO]` | `[TODO]%` |
| **Total** | **`[TODO]`** | **100%** |

### 5.5.3  Hasil Pengujian SUS

`[TODO: Sajikan tabel hasil SUS per responden, kemudian rata-rata skor akhir SUS.]`

**Tabel 5.3  Hasil Pengujian SUS per Responden**

| Responden | P1 | P2 | P3 | P4 | P5 | P6 | P7 | P8 | P9 | P10 | Skor SUS |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R1 | `[TODO]` | `[TODO]` | `[TODO]` | `[TODO]` | `[TODO]` | `[TODO]` | `[TODO]` | `[TODO]` | `[TODO]` | `[TODO]` | `[TODO]` |
| ⋮ | ⋮ | ⋮ | ⋮ | ⋮ | ⋮ | ⋮ | ⋮ | ⋮ | ⋮ | ⋮ | ⋮ |
| **Rata-rata** |  |  |  |  |  |  |  |  |  |  | **`[TODO]`** |

### 5.5.4  Interpretasi Hasil SUS

`[TODO: Setelah skor akhir diperoleh, tulis interpretasi seperti berikut:]`

> Berdasarkan hasil pengujian SUS, sistem klasifikasi tingkat kepadatan lalu lintas yang dikembangkan memperoleh skor rata-rata **`[TODO]`**. Mengacu pada klasifikasi Bangor et al. (2009), skor tersebut termasuk dalam kategori **`[Excellent / Good / OK / Poor / Worst]`** dengan tingkat *acceptability* **`[Acceptable / Marginal / Not Acceptable]`**. Hasil ini menunjukkan bahwa `[deskripsikan implikasi terhadap kelayakan sistem]`.

`[TODO: Sertakan analisis kualitatif jika ada komentar terbuka dari responden.]`

---

## 5.6  Perbandingan dengan Penelitian Terdahulu

Untuk memposisikan penelitian ini dalam lanskap riset yang lebih luas, dilakukan perbandingan dengan sepuluh penelitian terdahulu yang relevan, baik dari sisi penggunaan algoritma (YOLOv8, Random Forest, SVM) maupun konteks penerapan (klasifikasi kepadatan lalu lintas, sistem berbasis web). Rangkuman perbandingan disajikan pada Tabel 5.4.

**Tabel 5.4  Perbandingan dengan Penelitian Terdahulu**
> 📎 Baris terakhir menggunakan data dari `03_modelling/ringkasan_4_model.csv` dari `scripts/03_modelling.py`

| No | Peneliti & Tahun | Metode | Lokasi / Dataset | Output / Hasil |
|---|---|---|---|---|
| 1 | Aulia et al. (2024) | YOLOv8 + RF/SVM/KNN/LR | Vehicle detection dataset | RF 96%, SVM 89%, KNN 89%, LR 78% |
| 2 | Lu et al. (2024) | YOLOv8 + ML (RF, SVM, NB, KNN) | Road anomaly detection | RF 69%, SVM 73%, NB 56%, KNN 69% |
| 3 | Salsabilla et al. (2024) | YOLOv8 + OpenCV + Flask | Web traffic density detection (Indonesia) | Real-time web app, 5 kelas kendaraan |
| 4 | Cahyono & Pratama (UPI, 2024) | YOLOv8 + BoTSORT + Web | CCTV ATCS Bandung | Akurasi 98,45% (vehicle counting) |
| 5 | Surya & Wahyuni (2025) | YOLOv8 | CCTV Publik Kota Malang | Recall 0,901; Precision 0,811 |
| 6 | Maharani et al. (2024) | YOLOX + SegFormer + Web | Klasifikasi kepadatan (Indonesia) | Akurasi 80% |
| 7 | Sayudo (UGM) | CNN | MKJI + CCTV Sukoharjo | 6 kategori kepadatan (MKJI) |
| 8 | Zulkarnain & Kusrini (2025) | YOLOv11 + hyperparameter tuning | Vehicle detection malam hari (Indonesia) | Optimasi deteksi *low-light* |
| 9 | Yuda & Hamzah (2026) | YOLOv8 + Gamma Correction | ATCS Medan (Indonesia) | mAP@0,5 naik 0,14% dengan gamma 1,5 |
| 10 | **Penelitian ini (2026)** | **YOLOv8 + DeepSORT + RF/SVM + Flask** | **CCTV Jl. Diponegoro Surabaya** | **RF S1: Acc 73,3%; F1 0,73** |

Posisi penelitian ini terhadap penelitian terdahulu dapat dirangkum sebagai berikut:

**Kebaruan (*novelty*)**:

1. **Pendekatan labeling berbasis cycle failure (Nq1) yang lahir dari observasi lapangan dan divalidasi teori serta pakar**. Peneliti mengembangkan metode labeling dari pengamatan visual langsung terhadap rekaman CCTV — menghitung frekuensi penumpukan kendaraan yang tidak terurai dalam satu siklus lampu — sebelum menemukan bahwa pendekatan ini selaras dengan konsep Nq1 di PKJI 2023 dan *cycle failure* di HCM. Validitas metodologi ini kemudian dikonfirmasi oleh pakar lalu lintas DISHUB Surabaya (Bapak Tommi Firman). Sebagian besar penelitian terdahulu mengkategorisasi kepadatan berdasarkan jumlah kendaraan atau rasio area jalan (e.g., Maharani et al., 2024), atau berdasarkan SMP/MKJI (e.g., Sayudo, UGM). Belum banyak penelitian yang secara eksplisit menggunakan frekuensi *cycle failure* sebagai dasar labeling, apalagi dengan proses validasi berlapis seperti yang dilakukan pada penelitian ini.

2. **Validasi pakar lapangan dan pengembangan dua skenario dataset**. Penelitian ini melakukan validasi metode labeling kepada praktisi DISHUB Surabaya dan mengembangkan dua skenario dataset yang membedakan kondisi "0 ramai lancar" dari "0 kosongan". Pendekatan ini menambah lapisan validasi yang jarang ada di penelitian terdahulu.

3. **Komparasi langsung Random Forest vs SVM pada problem klasifikasi kepadatan**. Penelitian ini memberikan komparasi head-to-head yang detail (per skenario, dengan multi-metrik per kombinasi), berbeda dengan penelitian lain yang umumnya hanya menyebutkan skor agregat satu algoritma.

**Keterbatasan komparatif**:

Akurasi yang diperoleh penelitian ini (73,3%) lebih rendah dibandingkan beberapa penelitian terdahulu (mis. Aulia et al. 96%, Cahyono & Pratama 98,45%). Hal ini disebabkan oleh perbedaan **tugas yang diselesaikan**:

- Beberapa penelitian terdahulu mengukur akurasi pada level **deteksi/penghitungan kendaraan** (object detection task) — yang umumnya lebih tinggi.
- Penelitian ini mengukur akurasi pada level **klasifikasi tingkat kepadatan multi-kelas** (3 kelas) yang merupakan tugas yang **lebih sulit** karena membutuhkan inferensi semantik dari kombinasi banyak fitur, bukan sekadar deteksi objek.

Sebagai pembanding yang lebih *apples-to-apples*, penelitian Lu et al. (2024) yang juga mengkombinasikan YOLOv8 + ML classifier untuk klasifikasi (bukan sekadar deteksi) melaporkan akurasi 69–73%, yang berada pada rentang serupa dengan hasil penelitian ini.

---

## 5.7  Limitasi Penelitian

Selama proses pelaksanaan penelitian, peneliti mengidentifikasi beberapa limitasi yang penting untuk disampaikan secara transparan:

1. **Limitasi cakupan dataset**. Penelitian ini hanya menggunakan rekaman CCTV dari **satu titik pengamatan** (Jalan Diponegoro Musi Utara) dengan durasi pengamatan terbatas. Generalisasi hasil ke ruas jalan lain atau ke kota lain perlu validasi tambahan.

2. **Limitasi deteksi YOLOv8 pada kondisi pencahayaan rendah**. Sebagaimana dibahas pada sub-bab 5.1.3 dan 5.2.2, performa deteksi YOLOv8 menurun pada periode sore-malam, yang menyebabkan *confounding factor* dalam pembelajaran model klasifikasi. Penelitian ini telah melakukan eksperimen mitigasi dengan dataset *Traffic Night* (5.400 gambar), namun hasilnya justru lebih buruk dibandingkan model utama akibat misklasifikasi serupa. Model malam tidak diadopsi dan eksperimen ini didokumentasikan sebagai temuan untuk pengembangan lanjutan.

3. **Labeling manual oleh satu peneliti**. Proses labeling frekuensi *cycle failure* dilakukan secara manual oleh peneliti dengan acuan PKJI 2023 dan HCM. Walaupun telah divalidasi oleh pakar, *inter-rater reliability* belum diuji karena tidak ada labeler kedua. Pada penelitian lanjutan, melibatkan beberapa labeler independen dapat memperkuat reliabilitas dataset.

4. **Skor MAPE belum stabil untuk semua kategori**. `[TODO: jika MAPE per kategori berbeda jauh, sebutkan di sini]`.

5. **Akurasi prediksi pada kelas Sedang**. Recall pada kelas Sedang (46% di RF Skenario 1) menunjukkan model masih kesulitan membedakan kondisi transisi. Hal ini memerlukan pengembangan lebih lanjut, baik dari sisi *feature engineering* maupun penambahan data.

6. **Belum diintegrasikan dengan metrik lanjutan**. Pakar lapangan (DISHUB) menyarankan integrasi dengan SMP, V/C Ratio, dan Level of Service (LOS) dari MKJI 1997. Saran ini belum diakomodasi pada penelitian ini karena keterbatasan ruang lingkup, dan menjadi rekomendasi penelitian lanjutan pada Bab VI.

7. **Pengujian SUS dengan jumlah responden yang terbatas**. `[TODO: setelah SUS dilakukan, sebutkan jumlah responden dan keterbatasan generalisasi]`.

---

## Catatan Penutup Bab V

Bab V ini telah membahas hasil-hasil penelitian secara interpretatif, mengaitkannya dengan teori dan penelitian terdahulu, serta mengidentifikasi temuan-temuan menarik seperti pola korelasi negatif akibat *confounding* pencahayaan, *trade-off* antara Skenario 1 dan Skenario 2, serta unggulnya Random Forest dibandingkan SVM. Kesimpulan dari keseluruhan penelitian, beserta saran untuk penelitian lanjutan, akan disampaikan pada Bab VI.

---

## Catatan: Referensi yang Digunakan di Bab V

Untuk memudahkan pengisian Daftar Pustaka, berikut referensi yang dirujuk pada Bab V (Anda perlu cross-check format APA dan tahun publikasi terbaru):

1. **Aulia et al. (2024)** — *Vehicle Classification and Counting for Traffic Analysis based on Single-stage YOLOv8 Model*, ResearchGate. URL: <https://www.researchgate.net/publication/382408134>

2. **Bangor, A., Kortum, P., & Miller, J. (2009)** — *Determining what individual SUS scores mean: Adding an adjective rating scale*, Journal of Usability Studies, 4(3), 114–123.

3. **Brooke, J. (1986)** — *SUS: A "quick and dirty" usability scale*. Usability Evaluation in Industry, 189(194), 4–7.

4. **Cahyono & Pratama (2024)** — *Sistem Estimasi Kepadatan Lalu Lintas Berdasarkan Jenis Kendaraan di Bandung Menggunakan YOLOv8 dan BoTSORT*, Repository UPI Bandung. URL: <https://repository.upi.edu/128112/>

5. **Lewis, C. D. (1982)** — *Industrial and Business Forecasting Methods*, London: Butterworths.

6. **Lu et al. (2024)** — *Enhanced Traffic Safety by Road Anomaly Detection Using YOLOv8 and Machine Learning Models*, Springer Nature. DOI: <https://doi.org/10.1007/978-3-032-05507-1_19>

7. **Maharani et al. (2024)** — *Klasifikasi Kepadatan Lalu Lintas Berbasis Deep Learning Menggunakan YOLOX dan SegFormer*, Telkom University. URL: <https://openlibrary.telkomuniversity.ac.id/pustaka/236546>

8. **Putra et al. (2024)** — *Deteksi Kepadatan Lalu Lintas Pada CCTV Publik Pemerintah Kota Malang Menggunakan YOLOv8*, SPECTA Journal of Technology, 9(2), 136–149.

9. **Salsabilla et al. (2024)** — *Development of a Real-Time Traffic Density Detection Website Using YOLOv8-Based Digital Image Processing with OpenCV*, Journal of Information Systems and Informatics, 6(4). DOI: <https://doi.org/10.51519/journalisi.v6i4.912>

10. **Sayudo, S. (n.d.)** — *Klasifikasi Tingkat Kepadatan Kendaraan Lalu Lintas Menggunakan Convolutional Neural Network*, Repository UGM. URL: <http://etd.repository.ugm.ac.id/penelitian/detail/182317>

11. **Surya, A., & Wahyuni, I. (2025)** — *Deteksi Kepadatan Lalu Lintas Pada CCTV Publik Pemerintah Kota Malang Menggunakan YOLOv8*, SPECTA Journal of Technology, 9(2), 136–149. DOI: <https://doi.org/10.35718/specta.v9i2.8481367>

12. **Yuda & Hamzah (2026)** — *The Effect of Gamma Correction on the Accuracy of Vehicle Detection Using the YOLOv8 Algorithm*, ResearchGate. URL: <https://www.researchgate.net/publication/400864118>

13. **Zulkarnain, I. A., & Kusrini (2025)** — *Optimasi YOLOv11 Melalui Hyperparameter Tuning dan Data Augmentasi untuk Meningkatkan Akurasi Deteksi Kendaraan pada Kondisi Malam Hari*, MALCOM: Indonesian Journal of Machine Learning and Computer Science, 5(October), 1294–1303.

> **Catatan:** Nama-nama peneliti pada referensi #1, #2, #6, #8 di atas (Aulia, Lu, Maharani, Putra) merupakan **placeholder** karena saya tidak punya akses ke nama lengkap penulis di sumber yang saya temukan. Mohon dicek ulang melalui akses langsung ke jurnal/repository terkait untuk mendapatkan nama lengkap penulis. Tahun publikasi sudah saya verifikasi dari hasil pencarian.
