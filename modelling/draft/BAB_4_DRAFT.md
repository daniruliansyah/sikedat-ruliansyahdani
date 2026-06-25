# BAB IV  HASIL

> **Status Draft:**
> - Sub-bab 4.1, 4.2, 4.3 → KERANGKA + draft awal + placeholder `[TODO: ...]` yang perlu Anda lengkapi
> - Sub-bab 4.4 → Draft 80% (Anda lengkapi sedikit detail validasi pakar)
> - Sub-bab 4.5 hingga 4.9 → akan dilanjutkan pada blok berikutnya

Pada bab ini disajikan hasil implementasi penelitian sesuai dengan tahapan metode penelitian yang telah dijabarkan pada Bab III. Hasil setiap tahap dipresentasikan dalam bentuk teks, tabel, dan gambar untuk memberikan gambaran yang utuh mengenai proses dan luaran penelitian, mulai dari pengumpulan data hingga implementasi sistem pada aplikasi web berbasis Flask.

---

## 4.1  Hasil Pengumpulan Data

Pengumpulan data dilakukan pada periode `[TODO: tanggal mulai – tanggal selesai pengumpulan video CCTV]` dengan lokasi pengamatan di ruas **Jalan Diponegoro Musi Utara**, Kota Surabaya, Jawa Timur. Data utama yang digunakan dalam penelitian ini berupa rekaman video CCTV yang diperoleh secara resmi dari Dinas Perhubungan (DISHUB) Kota Surabaya melalui sistem *Intelligent Transportation System* (ITS) Surabaya, yang dikelola oleh Surabaya *Intelligent Transport System* (SITS). Penggunaan data dari sumber resmi ini bertujuan menjamin keandalan dan otentisitas data dasar yang dianalisis.

Rekaman video diambil pada `[TODO: jumlah hari total pengamatan, misalnya 21 hari]` dengan durasi pengamatan per hari dibagi menjadi dua sesi utama:

- **Sesi pagi**: pukul 06.00 – 09.00 WIB, mewakili jam sibuk pagi (*morning peak hour*).
- **Sesi sore – malam**: pukul 15.00 – 20.00 WIB, mewakili jam sibuk sore hingga awal malam (*evening peak hour*).

Pemilihan rentang waktu tersebut didasarkan pada karakteristik aktivitas masyarakat di sekitar Jalan Diponegoro yang dipengaruhi oleh aktivitas perkantoran, sekolah, dan pusat perbelanjaan, sehingga puncak kepadatan lalu lintas umumnya terjadi pada kedua sesi tersebut.

Data video kemudian dipotong menjadi segmen per jam menggunakan perangkat lunak CapCut untuk mempermudah proses ekstraksi data pada tahap selanjutnya. Total terkumpul `[TODO: jumlah file video total, misalnya 168 file]` file video dengan durasi keseluruhan `[TODO: total durasi, misalnya sekitar 168 jam rekaman]`. Ringkasan data rekaman yang berhasil dikumpulkan disajikan pada Tabel 4.1.

> **`[TODO: Buat Tabel 4.1 Ringkasan Data Rekaman yang Dikumpulkan]`**
> Disarankan dengan kolom: `No | Hari | Tanggal | Jumlah Jam Pagi | Jumlah Jam Sore-Malam | Total Durasi (jam) | Keterangan`. Tambahkan baris terakhir berupa total untuk masing-masing kolom angka. Jika ada hari yang rekamannya tidak lengkap, beri tanda pada kolom Keterangan.

Proses pengumpulan data ini melibatkan komunikasi resmi dengan pihak DISHUB Surabaya, khususnya Bu Nina dari Surabaya *Intelligent Transport System* (SITS), Bidang Lalu Lintas DISHUB Surabaya, yang berperan sebagai narahubung dalam penyediaan data rekaman CCTV.

Setelah proses ekstraksi data menggunakan algoritma YOLOv8 yang dijelaskan pada sub-bab 4.2, data ekstraksi disimpan dalam format Comma-Separated Values (CSV) dengan agregasi per interval 10 menit, sehingga setiap satu jam rekaman menghasilkan enam baris data. Total data tabular yang dihasilkan dari seluruh proses ekstraksi adalah **877 baris**, yang siap diolah pada tahap labeling dan preprocessing.

---

## 4.2  Hasil Ekstraksi Data dengan YOLOv8

Ekstraksi data kendaraan dari rekaman CCTV dilakukan menggunakan algoritma deteksi objek YOLOv8 (*You Only Look Once* versi 8) yang dipadukan dengan algoritma tracking DeepSORT. Tahap ini bertujuan mendeteksi dan menghitung jumlah kendaraan yang melintas pada ruas Jalan Diponegoro berdasarkan empat kategori kendaraan, yaitu Motor, Mobil, Bus, dan Truk.

### 4.2.1  Training Model YOLOv8 Custom

Pada eksperimen awal, peneliti menggunakan model YOLOv8 pre-trained dengan dataset COCO (*Common Objects in Context*) yang merupakan dataset standar dengan 80 kelas objek. Namun, hasil deteksi pada rekaman CCTV Jalan Diponegoro menunjukkan dua keterbatasan utama:

1. **Kategori kendaraan terlalu umum** — dataset COCO tidak memiliki kategori spesifik yang relevan dengan komposisi lalu lintas Indonesia, di mana motor merupakan moda dominan.
2. **Misklasifikasi antar kategori kendaraan yang signifikan** — khususnya Mobil yang sering terdeteksi sebagai Bus atau Truk. Sebagai ilustrasi, pada rekaman Senin pukul 15.10 model COCO menghasilkan Bus=111 dan Truk=27 yang tidak realistis, sedangkan model *Vehicle Detection* menghasilkan Bus=24 dan Truk=6 yang jauh lebih sesuai kondisi aktual (perbandingan lengkap disajikan pada Tabel 4.4).

Berdasarkan kondisi tersebut, peneliti melakukan training ulang model YOLOv8 menggunakan dataset custom dari platform Roboflow, yaitu dataset **"Vehicle Detection Computer Vision Model"** yang berisi 1.000 gambar dengan anotasi empat kelas kendaraan (Motor, Mobil, Bus, Truk) yang sesuai dengan kondisi lalu lintas Indonesia. Dataset ini dipilih karena memiliki kesamaan sudut pengambilan gambar (*angle frame*) dengan rekaman CCTV Jalan Diponegoro Musi Utara, sehingga diharapkan hasil deteksi lebih akurat. Dataset dapat diakses pada tautan berikut: <https://universe.roboflow.com/skripsi-1qzlz/vehicle-detection-ckrxi>.

Konfigurasi training model YOLOv8 custom adalah sebagai berikut:

**Tabel 4.2  Konfigurasi Training Model YOLOv8 Custom (Dataset Vehicle Detection)**

| Parameter | Nilai |
|---|---|
| *Base model* | YOLOv8m (`yolov8m.pt`) |
| Dataset | Vehicle Detection Computer Vision Model (Roboflow), 1.000 gambar |
| Pembagian dataset | `[TODO: cek file data.yaml untuk split train/val/test]` |
| File konfigurasi | `Vehicle-Detection-2/data.yaml` |
| Jumlah *epoch* | 50 |
| *Batch size* | 8 |
| *Image size* (`imgsz`) | 640 × 640 piksel |
| *Device* | GPU (device=0) |
| *Early stopping patience* | 10 epoch |
| Folder output | `model_hasil/kendaraan_indonesia/` |

> **`[TODO: Insert Gambar 4.1 Grafik Loss dan mAP Selama Training YOLOv8]`**
> File grafik training YOLOv8 biasanya bernama `results.png` pada folder output training. Insert sebagai Gambar 4.1.

Setelah proses training selesai selama 33 epoch (berhenti lebih awal dari maksimum 50 epoch karena *early stopping* patience=10 terpicu), model menghasilkan file `best.pt` yang menyimpan bobot dengan performa terbaik selama training. `best.pt` bukan merupakan bobot dari epoch terakhir, melainkan dari **epoch ke-23** yang mencatatkan nilai `metrics/mAP50-95(B)` tertinggi. Metrik evaluasi model `best.pt` pada *validation set* disajikan pada Tabel 4.3.

**Tabel 4.3  Metrik Evaluasi Model YOLOv8 Custom `best.pt` (Epoch 23)**

| Metrik | Nilai |
|---|---|
| *Precision* | 0,8879 (88,79%) |
| *Recall* | 0,9057 (90,57%) |
| mAP@0.5 | 0,9349 (93,49%) |
| mAP@0.5:0.95 | 0,8489 (84,89%) |
| *Val Box Loss* | 0,71333 |
| *Val Cls Loss* | 0,41742 |
| *Val DFL Loss* | 0,99748 |

*Sumber: `results.csv`, epoch ke-23 (nilai mAP@0.5:0.95 tertinggi selama training).*

Sebagai perbandingan, epoch terakhir (epoch 33) hanya mencapai mAP@0.5 sebesar 84,66% dan mAP@0.5:0.95 sebesar 77,31% — lebih rendah 8,83 dan 7,58 *percentage points* dibandingkan epoch 23. Hal ini mengonfirmasi bahwa mekanisme *early stopping* dan penyimpanan `best.pt` pada YOLOv8 bekerja sebagaimana mestinya: training dilanjutkan untuk memberikan kesempatan model berkembang, namun bobot terbaik tetap dipertahankan.

Untuk membuktikan peningkatan performa dari model COCO ke model *Vehicle Detection*, dilakukan perbandingan hasil ekstraksi pada rekaman yang sama (Senin, pukul 15.10). Hasilnya disajikan pada Tabel 4.4.

**Tabel 4.4  Perbandingan Hasil Ekstraksi Model COCO vs Vehicle Detection (Senin, Jam 15:10)**

| Model | Motor | Mobil | Bus | Truk | Total_Kendaraan |
|---|---|---|---|---|---|
| YOLOv8 + dataset COCO | 291 | 186 | **111** | **27** | 615 |
| YOLOv8 + dataset Vehicle Detection | 567 | 266 | **24** | **6** | 863 |

*Sumber: `hasil_10menit_COCO.csv` dan `hasil_10menit.csv`.*

Dari Tabel 4.4, nilai Bus=111 dan Truk=27 pada model COCO jelas tidak mencerminkan kondisi aktual Jalan Diponegoro Musi Utara yang bukan merupakan jalan arteri utama bus kota atau truk besar. Sebaliknya, model *Vehicle Detection* menghasilkan Bus=24 dan Truk=6 yang jauh lebih realistis. Selain itu, jumlah Motor pada model *Vehicle Detection* (567) juga lebih tinggi dan lebih representatif, karena model COCO kesulitan membedakan motor dari kategori kendaraan lainnya pada sudut pandang CCTV dari atas.

Guna mengatasi penurunan akurasi deteksi pada kondisi pencahayaan rendah (jam 17.30–20.00 WIB), peneliti melakukan eksperimen tambahan dengan melatih model YOLOv8 menggunakan dataset **"Traffic Night Computer Vision Dataset"** (5.400 gambar) dari Roboflow (<https://universe.roboflow.com/univ-kqors/traffic-night/dataset/1>). Training dilakukan menggunakan Kaggle Notebooks dengan konfigurasi yang disajikan pada Tabel 4.5.

**Tabel 4.5  Konfigurasi Training Model YOLOv8 Custom (Dataset Traffic Night)**

| Parameter | Nilai |
|---|---|
| *Base model* | YOLOv8s (`yolov8s.pt`) |
| Dataset | Traffic Night Computer Vision Dataset (Roboflow), 5.400 gambar |
| File konfigurasi | `Traffic-night-1/data.yaml` |
| Jumlah *epoch* | 50 |
| *Batch size* | 32 |
| *Image size* (`imgsz`) | 640 × 640 piksel |
| *Device* | GPU (device=0, Kaggle GPU) |
| *Workers* | 4 |
| *Early stopping patience* | 10 epoch |
| Folder output | `model_hasil/training_malam/` |

Setelah model `best-malam.pt` dihasilkan, dilakukan uji coba ekstraksi pada rekaman Senin pukul 17.00–18.00 (kondisi mulai gelap) untuk membandingkan hasilnya dengan model utama `best.pt`. Hasil perbandingan pada interval 10 menit yang sama disajikan pada Tabel 4.6.

**Tabel 4.6  Perbandingan Hasil Ekstraksi Model `best.pt` vs `best-malam.pt` (Senin, Jam 17:60)**

| Model | Motor | Mobil | Bus | Truk | Total_Kendaraan |
|---|---|---|---|---|---|
| `best.pt` (Vehicle Detection, 1.000 img) | 9 | 103 | 1 | 0 | **113** |
| `best-malam.pt` (Traffic Night, 5.400 img) | 4 | 265 | 29 | 168 | **466** |

*Sumber: `16_Senin_1760_model_best_pt.csv` dan `16_Senin_1760_model_bestmalam_pt.csv`.*

Dari Tabel 4.6, hasil ekstraksi `best-malam.pt` justru menghasilkan nilai yang tidak realistis, khususnya Truk=168 dalam 10 menit yang tidak mungkin terjadi pada kondisi aktual Jalan Diponegoro Musi Utara. Model malam mengalami misklasifikasi serupa dengan model COCO, di mana kendaraan gelap (terutama mobil dengan lampu menyilaukan) banyak terdeteksi sebagai Truk. Sementara itu, meskipun `best.pt` menghasilkan total yang lebih rendah (113) akibat keterbatasan deteksi di kondisi gelap, komposisi kendaraannya lebih masuk akal secara proporsi.

Berdasarkan hasil eksperimen ini, peneliti memutuskan untuk **tidak menggunakan** `best-malam.pt` dan melanjutkan seluruh proses ekstraksi dengan model `best.pt` dari dataset Vehicle Detection. Eksperimen ini tetap didokumentasikan sebagai temuan penelitian dan menjadi rekomendasi pengembangan lanjutan pada Bab VI.

### 4.2.2  Hasil Deteksi dan Tracking

Model YOLOv8 custom yang telah ditraining selanjutnya diintegrasikan dengan algoritma DeepSORT (*Deep Simple Online and Realtime Tracking*) untuk melakukan tracking kendaraan antar frame video. Penggunaan tracking ini memastikan bahwa satu unit kendaraan yang melintas hanya dihitung satu kali, meskipun terdeteksi pada banyak frame berurutan sepanjang lintasannya.

Setiap kendaraan yang melintasi garis virtual pada video dihitung dan dikategorikan ke dalam empat kelas: Motor, Mobil, Bus, dan Truk. Hasil deteksi kemudian diagregasi ke dalam interval per 10 menit untuk memperoleh representasi volume lalu lintas yang stabil.

Pemilihan interval 10 menit didasarkan pada pertimbangan praktis proses labeling manual yang akan dilakukan pada tahap berikutnya: interval tersebut cukup panjang untuk menangkap beberapa siklus lampu lalu lintas sekaligus cukup pendek untuk merepresentasikan perubahan kondisi lalu lintas secara granular. Setelah interval ini diterapkan dan proses labeling berjalan, peneliti menemukan bahwa konsep yang digunakan secara intuitif dalam pengamatan — yaitu menghitung frekuensi penumpukan kendaraan yang tidak terurai dalam satu siklus lampu — ternyata memiliki padanan dalam teori rekayasa lalu lintas, yaitu *cycle failure* (Nq1) dalam Pedoman Kapasitas Jalan Indonesia (PKJI) 2023 dan *Highway Capacity Manual* (HCM). Penjelasan lebih lanjut mengenai hal ini disampaikan pada sub-bab 4.4.

Contoh hasil ekstraksi data per 10 menit untuk salah satu hari pengamatan disajikan pada Tabel 4.7.

**Tabel 4.7  Contoh Hasil Ekstraksi Data per 10 Menit (Hari Senin)**

| Hari | Jam | Menit | Motor | Mobil | Bus | Truk | Total_Kendaraan |
|---|---|---|---|---|---|---|---|
| Senin | 6 | 40 | 676 | 153 | 5 | 1 | 835 |
| Senin | 6 | 50 | 866 | 141 | 9 | 1 | 1.017 |
| Senin | 7 | 10 | 647 | 118 | 7 | 5 | 777 |
| Senin | 7 | 20 | 687 | 137 | 12 | 0 | 836 |
| Senin | 7 | 30 | 300 | 69 | 4 | 3 | 376 |
| Senin | 8 | 20 | 821 | 146 | 6 | 4 | 977 |
| Senin | 8 | 30 | 624 | 189 | 10 | 2 | 825 |
| Senin | 15 | 10 | 587 | 262 | 24 | 10 | 883 |
| Senin | 15 | 20 | 680 | 264 | 10 | 6 | 960 |
| Senin | 15 | 30 | 733 | 290 | 7 | 8 | 1.038 |

*Sumber: Hasil ekstraksi YOLOv8 + DeepSORT (10 baris pertama Hari Senin).*

Dari proses ekstraksi keseluruhan dataset, diperoleh **877 baris data** yang masing-masing mewakili interval pengamatan 10 menit dengan struktur kolom: `Hari`, `Jam`, `Menit`, `Motor`, `Mobil`, `Bus`, `Truk`, dan `Total_Kendaraan`. Karakteristik lengkap distribusi data ini akan dianalisis lebih lanjut pada sub-bab 4.5.

---

## 4.3  Hasil Evaluasi Ekstraksi (MAPE)

Untuk memvalidasi keakuratan hasil ekstraksi YOLOv8 + DeepSORT terhadap kondisi aktual di lapangan, dilakukan evaluasi menggunakan metrik *Mean Absolute Percentage Error* (MAPE). Evaluasi ini bertujuan memastikan jumlah kendaraan terdeteksi oleh model tidak berbeda signifikan dari jumlah kendaraan yang teramati secara manual sebagai *ground truth*.

Prosedur pelaksanaan evaluasi MAPE adalah sebagai berikut:

1. Dipilih `[TODO: jumlah sample, misalnya 10 segmen 10 menit]` secara acak dari kumpulan rekaman.
2. Untuk setiap sample, dilakukan perhitungan manual jumlah kendaraan per kategori (Motor, Mobil, Bus, Truk) dengan menonton ulang rekaman dan mencatat hasilnya secara visual. Hasil hitungan manual ini menjadi *ground truth*.
3. Hasil hitungan manual kemudian dibandingkan dengan hasil ekstraksi YOLOv8 + DeepSORT pada segmen rekaman yang sama.
4. Nilai MAPE dihitung menggunakan persamaan `[TODO: nomor persamaan MAPE di Bab II, misalnya (2.8)]` yang telah dijelaskan pada Bab II.

> **`[TODO: Buat Tabel 4.7 Hasil Perhitungan MAPE per Kategori Kendaraan]`**
> Disarankan dengan kolom: `No | Sample (Hari/Jam/Menit) | Kategori | Hitung Manual | Hitung YOLO | Absolute Percentage Error (%)`. Tambahkan baris ringkasan rata-rata MAPE per kategori (Motor, Mobil, Bus, Truk) dan rata-rata MAPE keseluruhan di bagian akhir tabel.

`[TODO: Setelah tabel di atas siap, tambahkan paragraf interpretasi dengan format seperti berikut:]`

> Berdasarkan hasil perhitungan, diperoleh nilai MAPE sebesar X% untuk kategori Motor, Y% untuk kategori Mobil, Z% untuk kategori Bus, dan W% untuk kategori Truk, dengan rata-rata MAPE keseluruhan sebesar V%. Mengacu pada klasifikasi MAPE menurut Lewis (1982), nilai MAPE di bawah 10% dikategorikan sangat baik, 10–20% baik, 20–50% cukup baik, dan di atas 50% buruk. Dengan demikian, hasil ekstraksi yang diperoleh dapat dikategorikan `[sangat baik / baik / cukup baik]` dan layak digunakan sebagai dasar analisis pada tahap selanjutnya.

---

## 4.4  Hasil Labeling Data

Tahap labeling data bertujuan menentukan kelas Tingkat Kepadatan Lalu Lintas (Rendah, Sedang, atau Tinggi) untuk setiap baris data ekstraksi. Labeling dilakukan secara manual oleh peneliti melalui pengamatan visual rekaman CCTV.

Pada awalnya, peneliti mencoba melabeli data berdasarkan Tabel 3.8 (standar pelabelan di Bab III), namun menghadapi kesulitan karena kondisi lalu lintas dalam satu interval 10 menit sering menunjukkan karakteristik yang ambigu — terkadang dalam interval yang sama terjadi arus lancar, arus padat, dan penumpukan secara bergantian. Hal ini mendorong peneliti untuk mencari indikator yang lebih objektif dan dapat dihitung secara konsisten.

Peneliti kemudian mengembangkan pendekatan berbasis **penghitungan frekuensi penumpukan kendaraan** pada setiap siklus lampu lalu lintas: setiap kali terjadi kondisi di mana antrian kendaraan tidak habis terurai saat lampu hijau dan kendaraan yang berhenti di belakang terkena lampu merah berikutnya, peneliti menghitung kejadian tersebut sebagai +1 dalam interval 10 menit yang bersangkutan. Pendekatan ini menghasilkan indikator yang konsisten dan dapat direplikasi antar interval.

Setelah pendekatan ini diterapkan, peneliti melakukan verifikasi teoritis dan menemukan bahwa konsep yang digunakan tersebut **selaras dengan teori yang sudah diakui** dalam rekayasa lalu lintas, yaitu konsep *cycle failure* (Nq1) dalam Pedoman Kapasitas Jalan Indonesia (PKJI) 2023 dan *Highway Capacity Manual* (HCM). Validitas pendekatan ini kemudian diperkuat lebih lanjut melalui konsultasi dengan pakar lalu lintas dari DISHUB Surabaya, Bapak Tommi Firman, yang memberikan persetujuan atas metode labeling yang digunakan. Proses validasi pakar tersebut diuraikan secara lengkap pada sub-bab 4.4.4.

### 4.4.1  Penentuan Frekuensi Cycle Failure (Nq1)

Acuan utama yang digunakan dalam proses labeling adalah konsep *cycle failure* dari PKJI 2023 dan HCM. *Cycle failure* didefinisikan sebagai kondisi ketika antrian kendaraan pada satu siklus lampu lalu lintas (*traffic signal cycle*) tidak habis terurai pada fase hijau yang sama, sehingga kendaraan yang masih dalam antrian harus menunggu hingga siklus berikutnya. Notasi yang digunakan dalam pedoman tersebut adalah **Nq1**, yang merepresentasikan jumlah *cycle failure* yang terjadi dalam suatu interval pengamatan tertentu.

Pada penelitian ini, peneliti menghitung jumlah *cycle failure* (Nq1) yang terjadi pada setiap interval 10 menit dengan langkah-langkah berikut:

1. Menonton ulang rekaman CCTV pada interval 10 menit yang sedang dilabel.
2. Mengamati antrian kendaraan pada setiap siklus lampu lalu lintas di simpang Jalan Diponegoro.
3. Menghitung berapa kali antrian gagal terurai pada satu fase lampu hijau (*failed cycle*).
4. Mencatat angka tersebut sebagai nilai Nq1 untuk interval 10 menit terkait.

Pada dataset hasil ekstraksi, kolom `Tingkat_Kepadatan` awalnya berisi nilai frekuensi *cycle failure* (Nq1) dengan rentang 0 hingga 10. Sebanyak 463 baris atau 52,79% dari total data tercatat memiliki nilai Nq1 = 0 (tidak terjadi *cycle failure* sama sekali), sedangkan baris dengan Nq1 ≥ 3 sebanyak 209 baris atau 23,83%. Distribusi lengkap nilai Nq1 sebelum dikonversi ke kelas disajikan pada sub-bab 4.5 (EDA).

### 4.4.2  Konversi Frekuensi ke 3 Kelas Tingkat Kepadatan

Karena tujuan klasifikasi penelitian ini adalah membedakan tiga kelas kepadatan, yaitu Rendah, Sedang, dan Tinggi, nilai frekuensi *cycle failure* dikonversi menggunakan skema *threshold* yang disajikan pada Tabel 4.8.

**Tabel 4.8  Skema Konversi Nq1 ke Kelas Tingkat Kepadatan**

| Frekuensi Cycle Failure (Nq1) | Kelas Tingkat Kepadatan |
|---|---|
| 0 | Rendah |
| 1 – 2 | Sedang |
| ≥ 3 | Tinggi |

Pemilihan *threshold* tersebut didasarkan pada interpretasi HCM mengenai *cycle failure* yang dijabarkan sebagai berikut:

- **Nq1 = 0** menunjukkan bahwa kapasitas simpang masih mencukupi untuk volume kendaraan yang melintas, sehingga seluruh antrian berhasil terurai dalam satu siklus lampu hijau. Kondisi ini dikategorikan sebagai **Rendah**.
- **Nq1 = 1 – 2** menunjukkan kondisi mendekati kapasitas (*onset of congestion*) di mana terjadi kemacetan ringan dengan kegagalan antrian sesekali. Kondisi ini dikategorikan sebagai **Sedang**.
- **Nq1 ≥ 3** menunjukkan kondisi *oversaturated*, yaitu kemacetan yang berkelanjutan dengan kapasitas yang sudah jauh terlampaui. *Threshold* ≥ 3 dipilih karena pada interval 10 menit umumnya terdapat 3 – 4 siklus lampu, sehingga Nq1 ≥ 3 mengindikasikan hampir setiap siklus mengalami kegagalan urai antrian. Kondisi ini dikategorikan sebagai **Tinggi**.

### 4.4.3  Pengembangan Dua Skenario Dataset

Berdasarkan hasil bimbingan dengan dosen pembimbing dan validasi pakar lapangan, peneliti mengembangkan **dua skenario dataset** untuk dibandingkan performanya. Pengembangan dua skenario ini dilakukan karena pada pengamatan visual ditemukan kondisi lalu lintas tertentu yang memiliki nilai Nq1 = 0 (tidak terjadi *cycle failure*) namun secara visual menunjukkan karakteristik **"ramai lancar"**, yaitu volume kendaraan yang terlihat banyak tetapi pergerakannya masih lancar tanpa hambatan signifikan. Kondisi visual "ramai lancar" ini secara substansial berbeda dengan kondisi visual "kosongan" (sepi), meskipun keduanya memiliki nilai Nq1 = 0.

Dua skenario dataset yang dikembangkan adalah sebagai berikut:

**Skenario 1 — Berbasis Frekuensi Murni**

Pada skenario ini, semua baris data dengan Nq1 = 0 dikategorikan sebagai Rendah tanpa mempertimbangkan kondisi visual. Skenario ini merepresentasikan pendekatan klasifikasi yang sepenuhnya bergantung pada metrik kuantitatif PKJI/HCM.

**Skenario 2 — Berbasis Frekuensi + Validasi Visual**

Pada skenario ini, baris data dengan Nq1 = 0 dipecah menjadi dua sub-kategori berdasarkan pengamatan visual:

- Nq1 = 0 dengan kondisi visual "kosongan" → **Rendah**
- Nq1 = 0 dengan kondisi visual "ramai lancar" → **Sedang**

Untuk merealisasikan Skenario 2, peneliti menambahkan kolom `Catatan` pada dataset yang berisi keterangan kondisi visual hasil pengamatan. Sebanyak **158 baris** dari total 463 baris dengan Nq1 = 0 ditandai sebagai "ramai lancar" oleh peneliti.

Distribusi akhir kelas pada kedua skenario disajikan pada Tabel 4.9 dan diilustrasikan pada Gambar 4.2.

**Tabel 4.9  Distribusi Kelas pada Kedua Skenario Dataset**

| Kelas | Skenario 1 (baris) | Persentase | Skenario 2 (baris) | Persentase |
|---|---|---|---|---|
| Rendah | 463 | 52,79% | 305 | 34,78% |
| Sedang | 205 | 23,37% | 363 | 41,39% |
| Tinggi | 209 | 23,83% | 209 | 23,83% |
| **Total** | **877** | **100,00%** | **877** | **100,00%** |

![Gambar 4.2 Distribusi Label pada Dua Skenario Dataset](01_eda/01_distribusi_label_2skenario.png)
> 📎 `01_distribusi_label_2skenario.png` dari `scripts/01_eda.py`

**Gambar 4.2**  Distribusi label pada dua skenario dataset. Skenario 2 menunjukkan distribusi yang lebih seimbang dibandingkan Skenario 1.

Berdasarkan Tabel 4.9 dan Gambar 4.2, terlihat bahwa penerapan Skenario 2 menggeser sebanyak 158 baris (17,90% dari total data) dari kelas Rendah ke kelas Sedang, sehingga proporsi kelas Sedang meningkat dari 23,37% menjadi 41,39%. Pergeseran ini menghasilkan distribusi yang lebih merata antar kelas, di mana selisih proporsi antara kelas terbesar dan terkecil menyempit dari 29,42 poin persentase (Skenario 1) menjadi 17,61 poin persentase (Skenario 2). Sementara itu, distribusi kelas Tinggi tidak berubah pada kedua skenario karena perubahan hanya terjadi pada subset baris dengan nilai Nq1 = 0.

### 4.4.4  Validasi Pakar

Untuk memvalidasi metode labeling yang dilakukan, peneliti berkonsultasi dengan pakar lalu lintas dari Dinas Perhubungan Kota Surabaya, yaitu **Bapak Tommi Firman**, selaku **Seksi Manajemen Rekayasa Lalu Lintas, Bidang Lalu Lintas, DISHUB Surabaya**, pada **tanggal 9 Juni 2026** di **Kantor DISHUB Surabaya, Dukuh Menanggal No. 1**. Validasi pakar ini bertujuan memastikan bahwa metode labeling yang digunakan peneliti sudah selaras dengan praktik analisis lalu lintas di lapangan.

Beberapa poin penting hasil konsultasi dengan pakar adalah sebagai berikut:

1. **Persetujuan metode labeling**. Pakar memberikan persetujuan atas metode labeling yang digunakan peneliti, dengan acuan PKJI 2023 dan HCM yang dinilai sudah relevan dengan kondisi lalu lintas Kota Surabaya.

2. **Validasi kategori "ramai lancar"**. Pakar memberikan masukan bahwa kondisi visual "ramai lancar" — yaitu volume kendaraan terlihat banyak namun pergerakannya lancar tanpa hambatan — sebaiknya dikategorikan sebagai **Sedang**, bukan Rendah. Masukan ini menjadi dasar pengembangan Skenario 2 sebagaimana dijelaskan pada sub-bab 4.4.3.

3. **Saran tambahan untuk pengembangan lanjutan**. Pakar menyampaikan bahwa untuk analisis kepadatan yang lebih akurat secara teknis, dapat dipertimbangkan penggunaan metrik tambahan seperti *Satuan Mobil Penumpang* (SMP) dan perhitungan *Volume to Capacity Ratio* (V/C Ratio) untuk memperoleh *Level of Service* (LOS) dengan kategorisasi A–F, di mana LOS A–B dapat dikategorikan sebagai Rendah, C–D sebagai Sedang, dan E–F sebagai Tinggi. Pakar juga merekomendasikan bahwa untuk pengembangan ke depan dapat dipertimbangkan penyesuaian dengan pedoman MKJI 1997.

Saran pakar pada poin 3 di atas tidak diakomodasi pada penelitian ini karena keterbatasan ruang lingkup, namun dicantumkan sebagai bagian dari **Saran** pada Bab VI untuk penelitian lanjutan.

> **`[TODO: Lampirkan dokumentasi resmi validasi pakar di Lampiran skripsi, misalnya berita acara konsultasi atau notulensi pertemuan ditandatangani oleh pakar]`**

---

> **Catatan akhir blok 1:**
> Sub-bab berikutnya (4.5 Preprocessing, 4.6 Split Data, 4.7 Modelling, 4.8 Evaluasi Model, 4.9 Implementasi Web) akan dilanjutkan pada blok penulisan selanjutnya.

---

## 4.5  Hasil Preprocessing Data

Setelah tahap labeling selesai, dataset diolah melalui serangkaian tahapan preprocessing untuk memastikan kualitas dan kesesuaian data dengan algoritma machine learning yang akan digunakan. Tahapan preprocessing yang dilakukan dalam penelitian ini meliputi penanganan *missing values*, deteksi *outliers*, *data encoding*, dan normalisasi data, sebagaimana telah dijabarkan pada sub-bab 3.3.5.

### 4.5.1  Handling Missing Values

Pemeriksaan terhadap data yang hilang (*missing values*) dilakukan pada seluruh kolom dataset menggunakan fungsi `isnull().sum()` dari library pandas. Hasil pemeriksaan menunjukkan bahwa **tidak terdapat nilai yang hilang** pada seluruh 877 baris dan 10 kolom dataset, sehingga tidak diperlukan tahap imputasi data. Kondisi ini dapat tercapai karena seluruh proses ekstraksi YOLOv8 selalu menghasilkan nilai numerik (angka 0 menunjukkan tidak ada kendaraan terdeteksi pada interval tersebut, bukan *missing*).

### 4.5.2  Handling Outliers

Deteksi *outliers* dilakukan menggunakan metode *Interquartile Range* (IQR) sebagaimana dijelaskan pada sub-bab 2.5.2, dengan batas bawah `Q1 − 1.5 × IQR` dan batas atas `Q3 + 1.5 × IQR`. Deteksi dilakukan pada kelima fitur volume kendaraan: `Motor`, `Mobil`, `Bus`, `Truk`, dan `Total_Kendaraan`. Hasil deteksi disajikan pada Tabel 4.10.

**Tabel 4.10  Hasil Deteksi Outlier dengan Metode IQR**

| Fitur | Q1 | Q3 | IQR | Batas Bawah | Batas Atas | Jumlah Outlier | Persentase |
|---|---|---|---|---|---|---|---|
| Motor | 28,00 | 489,00 | 461,00 | −663,50 | 1.180,50 | 0 | 0,00% |
| Mobil | 87,00 | 194,00 | 107,00 | −73,50 | 354,50 | 0 | 0,00% |
| Bus | 1,00 | 7,00 | 6,00 | −8,00 | 16,00 | 5 | 0,57% |
| Truk | 0,00 | 2,00 | 2,00 | −3,00 | 5,00 | 43 | 4,90% |
| Total_Kendaraan | 145,00 | 666,00 | 521,00 | −636,50 | 1.447,50 | 0 | 0,00% |

*Sumber: `tabel_deteksi_outlier_iqr.csv` dari `scripts/01_eda.py`*

Dari hasil deteksi, ditemukan total 48 baris yang terdeteksi sebagai *outlier* pada fitur `Bus` (5 baris atau 0,57%) dan `Truk` (43 baris atau 4,90%). Tidak ditemukan *outlier* pada fitur `Motor`, `Mobil`, dan `Total_Kendaraan`. Outlier yang teridentifikasi pada `Bus` dan `Truk` muncul karena distribusi kedua fitur tersebut cenderung *right-skewed* (banyak nilai 0 atau kecil dengan beberapa nilai ekstrem), yang merupakan karakteristik alami dari komposisi lalu lintas di mana bus dan truk lebih jarang melintas dibandingkan motor dan mobil. Visualisasi boxplot kelima fitur ditampilkan pada Gambar 4.3.

![Gambar 4.3 Boxplot Deteksi Outlier pada Fitur Volume Kendaraan](01_eda/05_boxplot_outlier.png)
> 📎 `05_boxplot_outlier.png` dari `scripts/01_eda.py`

**Gambar 4.3**  Boxplot fitur volume kendaraan untuk deteksi outlier dengan metode IQR.

Dari Gambar 4.3 terlihat bahwa fitur `Motor`, `Mobil`, dan `Total_Kendaraan` memiliki distribusi yang relatif simetris dengan sebaran yang lebar, sehingga tidak ada *outlier* yang terdeteksi pada rentang IQR. Sebaliknya, fitur `Bus` dan `Truk` menampilkan banyak titik merah di atas batas atas (*upper fence*), mengindikasikan adanya beberapa interval 10 menit dengan volume bus/truk yang jauh di atas normal. Nilai-nilai ini tidak dihapus karena merepresentasikan kondisi aktual seperti jam keberangkatan bus kota atau pengiriman truk yang terjadi secara periodik.

Berdasarkan pertimbangan domain pengetahuan, *outliers* yang terdeteksi pada fitur `Bus` dan `Truk` **tidak dihapus** dari dataset. Keputusan ini diambil karena nilai-nilai *outlier* tersebut merepresentasikan kondisi lalu lintas ekstrem yang justru bersifat informatif untuk klasifikasi tingkat kepadatan, khususnya untuk membedakan kelas Tinggi dari kelas lainnya. Penghapusan *outlier* berisiko menghilangkan sinyal diskriminatif antar kelas dan menurunkan performa model klasifikasi. Pertimbangan ini juga selaras dengan arahan dosen pembimbing yang menyarankan untuk mempertahankan distribusi data apa adanya selama tidak terdapat kesalahan ekstraksi yang nyata.

### 4.5.3  Data Encoding

Pada tahap *data encoding*, fitur kategorikal pada dataset perlu dikonversi menjadi format numerik agar dapat diproses oleh algoritma machine learning. Pada penelitian ini, satu-satunya fitur kategorikal adalah kolom **`Hari`** yang berisi nilai nominal: Senin, Selasa, Rabu, Kamis, Jumat, Sabtu, dan Minggu.

Untuk fitur `Hari`, peneliti memilih menggunakan teknik **One-Hot Encoding** alih-alih *Label Encoding*. Pertimbangan pemilihan teknik ini adalah sebagai berikut:

- Variabel `Hari` bersifat **nominal**, yaitu tidak memiliki urutan atau hierarki antar kategori. Senin tidak "lebih besar" atau "lebih kecil" dari Selasa, demikian seterusnya.
- Jika digunakan *Label Encoding* (Senin = 1, Selasa = 2, …, Minggu = 7), algoritma machine learning akan menginterpretasikan adanya hubungan ordinal antar kategori, yang akan menyesatkan proses pembelajaran.
- One-Hot Encoding mengubah satu kolom kategorikal menjadi *N* kolom *binary* (0 atau 1), dengan masing-masing kolom merepresentasikan satu kategori. Pendekatan ini menjaga sifat nominal variabel sekaligus menghasilkan representasi numerik yang dapat diproses model.

Penerapan One-Hot Encoding pada kolom `Hari` menghasilkan **7 kolom baru**, yaitu `Hari_Senin`, `Hari_Selasa`, `Hari_Rabu`, `Hari_Kamis`, `Hari_Jumat`, `Hari_Sabtu`, dan `Hari_Minggu`. Tabel 4.11 memberikan ilustrasi transformasi data sebelum dan sesudah One-Hot Encoding.

**Tabel 4.11  Ilustrasi Transformasi `Hari` dengan One-Hot Encoding**

| Sebelum (`Hari`) | `Hari_Senin` | `Hari_Selasa` | `Hari_Rabu` | `Hari_Kamis` | `Hari_Jumat` | `Hari_Sabtu` | `Hari_Minggu` |
|---|---|---|---|---|---|---|---|
| Senin | **1** | 0 | 0 | 0 | 0 | 0 | 0 |
| Selasa | 0 | **1** | 0 | 0 | 0 | 0 | 0 |
| Sabtu | 0 | 0 | 0 | 0 | 0 | **1** | 0 |
| Minggu | 0 | 0 | 0 | 0 | 0 | 0 | **1** |

Dari Tabel 4.11 terlihat bahwa setiap baris hanya memiliki tepat satu nilai **1** pada kolom `Hari_*` yang sesuai, sementara kolom lainnya bernilai 0. Pendekatan ini memastikan tidak ada hubungan ordinal yang terimplisit antar kategori hari, karena setiap hari direpresentasikan sebagai dimensi independen dalam ruang fitur.

Setelah proses One-Hot Encoding, jumlah kolom fitur pada dataset menjadi 14 kolom: `Jam`, `Menit`, tujuh kolom `Hari_*`, `Motor`, `Mobil`, `Bus`, `Truk`, dan `Total_Kendaraan`. Fitur `Jam` dan `Menit` tetap dipertahankan sebagai *numeric* karena keduanya memiliki sifat ordinal dan dapat diolah langsung tanpa encoding tambahan.

### 4.5.4  Normalisasi Data

Normalisasi data dilakukan untuk menyamakan skala antar fitur numerik, sehingga fitur dengan rentang nilai besar (mis. `Total_Kendaraan` yang dapat mencapai ribuan) tidak mendominasi pengaruh terhadap model dibandingkan fitur dengan rentang nilai kecil (mis. `Bus` atau `Truk` yang umumnya bernilai kecil). Pada penelitian ini digunakan metode **Standardization** (Z-score normalization) dengan formula yang dijelaskan pada sub-bab 2.5.4, melalui class `StandardScaler` dari library `scikit-learn`.

Namun, terdapat perbedaan perlakuan normalisasi antara kedua algoritma yang diuji:

1. **Random Forest** — algoritma berbasis *decision tree* yang bersifat *scale-invariant*, artinya tidak terpengaruh oleh skala fitur. Oleh karena itu, normalisasi **tidak diterapkan** pada training Random Forest. Hal ini juga merupakan praktik standar yang direkomendasikan pada literatur machine learning.

2. **Support Vector Machine** — algoritma yang sangat sensitif terhadap skala fitur karena bergantung pada perhitungan jarak antar titik data (terutama pada kernel RBF dan polynomial). Untuk SVM, normalisasi **wajib diterapkan**. Pada penelitian ini, `StandardScaler` dimasukkan ke dalam *Pipeline* `scikit-learn` bersama dengan model SVM, sehingga normalisasi dilakukan secara terintegrasi pada setiap *fold* cross-validation. Penggunaan *Pipeline* ini penting untuk **mencegah *data leakage*** yang dapat terjadi apabila parameter normalisasi (mean dan standar deviasi) dihitung dari seluruh data sebelum pembagian *fold*.

Implementasi *Pipeline* SVM dapat diformulasikan sebagai berikut:

```python
Pipeline([
    ('scaler', StandardScaler()),
    ('svm', SVC(class_weight='balanced', random_state=42))
])
```

### 4.5.5  Hasil Eksplorasi Data (EDA)

Sebelum masuk ke tahap pemodelan, dilakukan eksplorasi data (*Exploratory Data Analysis*) untuk memahami karakteristik dataset. Statistik deskriptif fitur volume kendaraan disajikan pada Tabel 4.12.

**Tabel 4.12  Statistik Deskriptif Fitur Volume Kendaraan**

| Statistik | Motor | Mobil | Bus | Truk | Total_Kendaraan |
|---|---|---|---|---|---|
| Jumlah data | 877 | 877 | 877 | 877 | 877 |
| Rata-rata | 301,68 | 141,42 | 4,53 | 1,51 | 449,13 |
| Standar deviasi | 256,93 | 76,75 | 4,52 | 2,42 | 320,71 |
| Minimum | 0 | 0 | 0 | 0 | 0 |
| Kuartil 1 (Q1) | 28,00 | 87,00 | 1,00 | 0,00 | 145,00 |
| Median (Q2) | 280,00 | 145,00 | 3,00 | 1,00 | 432,00 |
| Kuartil 3 (Q3) | 489,00 | 194,00 | 7,00 | 2,00 | 666,00 |
| Maksimum | 924 | 349 | 24 | 20 | 1.228 |
| Skewness | 0,46 | −0,02 | 1,52 | 2,58 | 0,40 |
| Kurtosis | −0,86 | −0,12 | 3,02 | 12,08 | −0,87 |

*Sumber: `tabel_statistik_deskriptif.csv` dari `scripts/01_eda.py`*

Dari Tabel 4.12 dapat diamati bahwa rata-rata kendaraan Motor (301,68 unit per 10 menit) jauh lebih tinggi dibandingkan jenis kendaraan lainnya, konsisten dengan karakteristik lalu lintas Indonesia di mana motor merupakan moda transportasi dominan. Fitur `Truk` memiliki nilai skewness tertinggi (2,58) dengan kurtosis 12,08, menunjukkan distribusi yang sangat *right-skewed* dengan banyak nilai 0 dan beberapa nilai ekstrem.

Distribusi jumlah baris data per hari dan per jam pengamatan ditampilkan pada Gambar 4.4 dan Gambar 4.5.

![Gambar 4.4 Distribusi Jumlah Baris Data per Hari](01_eda/02_distribusi_per_hari.png)
> 📎 `02_distribusi_per_hari.png` dari `scripts/01_eda.py`

**Gambar 4.4**  Distribusi jumlah baris data per hari pengamatan.

Gambar 4.4 menunjukkan distribusi jumlah baris data relatif merata antar hari dalam seminggu, berkisar antara 105 hingga 143 baris per hari. Hari Rabu memiliki baris terbanyak sementara hari Senin sedikit lebih sedikit, kemungkinan karena ketidaklengkapan sebagian rekaman sebagaimana disebutkan pada sub-bab 4.1. Distribusi yang merata ini penting karena memastikan model tidak belajar dengan bias terhadap hari tertentu.

![Gambar 4.5 Distribusi Jumlah Baris Data per Jam](01_eda/03_distribusi_per_jam.png)
> 📎 `03_distribusi_per_jam.png` dari `scripts/01_eda.py`

**Gambar 4.5**  Distribusi jumlah baris data per jam pengamatan (WIB).

Gambar 4.5 memperlihatkan distribusi yang juga merata antar jam pengamatan (106–114 baris per jam), yang mencerminkan konsistensi pengambilan data di setiap sesi. Terlihat dua kelompok jam yang terpisah: sesi pagi (jam 6–8) dan sesi sore-malam (jam 15–19), sesuai dengan rancangan pengumpulan data pada sub-bab 4.1. Tidak ada jam yang terlalu mendominasi, sehingga model mendapatkan representasi yang proporsional untuk seluruh rentang waktu pengamatan.

Berdasarkan kedua gambar tersebut, jumlah data terdistribusi relatif merata baik antar hari (105–143 baris per hari) maupun antar jam pengamatan (106–114 baris per jam). Distribusi yang merata ini menunjukkan bahwa dataset cukup representatif untuk dimodelkan.

Selanjutnya, dilakukan analisis korelasi antar fitur untuk mengamati hubungan linear antar variabel. Matriks korelasi disajikan pada Gambar 4.6.

![Gambar 4.6 Matriks Korelasi Antar Fitur](01_eda/06_heatmap_korelasi.png)
> 📎 `06_heatmap_korelasi.png` dari `scripts/01_eda.py`

**Gambar 4.6**  Matriks korelasi antar fitur volume kendaraan dan target `Tingkat_Kepadatan`.

Catatan penting: analisis korelasi di atas menggunakan kolom `Tingkat_Kepadatan` yang merupakan representasi numerik frekuensi *cycle failure* (Nq1 = 0, 1, 2, …, 10), bukan label kelas final (Rendah/Sedang/Tinggi), karena korelasi Pearson hanya dapat dihitung pada variabel numerik. Dari Gambar 4.6, seluruh fitur volume kendaraan menunjukkan korelasi negatif terhadap `Tingkat_Kepadatan`, dengan Motor sebagai fitur berkorelasi paling kuat (−0,44) dan Mobil hampir tidak berkorelasi (≈ 0,00). Pola korelasi negatif yang *counter-intuitive* ini akan dianalisis lebih mendalam pada Bab V, karena memerlukan interpretasi kontekstual terkait limitasi deteksi YOLOv8 pada kondisi pencahayaan rendah. Korelasi antar sesama fitur volume juga terlihat tinggi, khususnya antara `Motor` dan `Total_Kendaraan` (0,98), yang merupakan konsekuensi alami dari dominasi motor pada komposisi lalu lintas Indonesia.

Dari matriks korelasi, dapat diamati pola hubungan yang menarik: seluruh fitur volume kendaraan menunjukkan **korelasi negatif** dengan target `Tingkat_Kepadatan` (Motor: −0,44; Total_Kendaraan: −0,37; Bus: −0,32; Truk: −0,26; Mobil: ≈ 0). Korelasi negatif ini akan dianalisis lebih lanjut pada Bab V (Pembahasan), karena memerlukan interpretasi kontekstual yang melibatkan limitasi sistem deteksi YOLOv8 pada kondisi pencahayaan tertentu.

---

## 4.6  Hasil Pembagian Data (Train-Test Split)

Dataset hasil preprocessing kemudian dibagi menjadi dua bagian, yaitu *training set* (80%) dan *testing set* (20%), menggunakan fungsi `train_test_split` dari library `scikit-learn` dengan parameter `random_state = 42` untuk menjamin **reproducibility**. Untuk menangani distribusi kelas yang tidak seimbang, dilakukan **stratified split** dengan parameter `stratify = y`, sehingga proporsi kelas Rendah, Sedang, dan Tinggi pada *training set* dan *testing set* tetap sama.

Pembagian data dilakukan secara terpisah untuk masing-masing skenario, dengan hasil yang disajikan pada Tabel 4.13.

**Tabel 4.13  Hasil Pembagian Data Train-Test untuk Kedua Skenario**

| Skenario | Set | Rendah | Sedang | Tinggi | Total |
|---|---|---|---|---|---|
| **Skenario 1** | Training (80%) | 370 | 164 | 167 | 701 |
|  | Testing (20%) | 93 | 41 | 42 | 176 |
|  | **Total** | **463** | **205** | **209** | **877** |
| **Skenario 2** | Training (80%) | 244 | 290 | 167 | 701 |
|  | Testing (20%) | 61 | 73 | 42 | 176 |
|  | **Total** | **305** | **363** | **209** | **877** |

Berdasarkan Tabel 4.13, hasil pembagian data menunjukkan bahwa proporsi kelas pada *training set* dan *testing set* sudah konsisten dengan distribusi asli dataset. Pembagian data yang sama (dengan `random_state = 42`) digunakan untuk training kedua algoritma (Random Forest dan SVM) pada masing-masing skenario, agar perbandingan performa antar algoritma menjadi adil (*fair comparison*).

---

## 4.7  Hasil Modelling

Tahap modelling dilakukan secara terpisah untuk kedua algoritma — Random Forest dan Support Vector Machine — pada masing-masing skenario dataset. Total terdapat **empat eksperimen modelling**, yaitu:

1. RF Skenario 1
2. RF Skenario 2
3. SVM Skenario 1
4. SVM Skenario 2

Untuk setiap eksperimen, dilakukan *hyperparameter tuning* menggunakan **GridSearchCV** dengan **5-fold Stratified Cross-Validation** dan metrik evaluasi `f1_weighted` sebagai *scoring*. Pemilihan metrik `f1_weighted` dilakukan dengan pertimbangan distribusi kelas yang tidak seimbang, di mana `f1_weighted` memberikan bobot proporsional terhadap jumlah baris setiap kelas, sehingga lebih representatif dibanding *accuracy* murni. Selain itu, parameter `class_weight = 'balanced'` diterapkan pada kedua algoritma untuk menyesuaikan bobot kelas terhadap distribusi yang tidak seimbang.

### 4.7.1  Random Forest

Random Forest diimplementasikan menggunakan class `RandomForestClassifier` dari `scikit-learn`. *Hyperparameter grid* yang diuji pada penelitian ini disajikan pada Tabel 4.14, merupakan versi yang telah direvisi dari Tabel 3.10 pada Bab III, dengan pertimbangan efisiensi waktu komputasi tanpa mengurangi cakupan eksplorasi parameter utama.

**Tabel 4.14  Hyperparameter Grid untuk Random Forest**

| Parameter | Nilai yang Diuji |
|---|---|
| `n_estimators` | 100, 200 |
| `max_depth` | 10, None |
| `min_samples_split` | 2, 5 |
| `min_samples_leaf` | 1, 2 |

Dari Tabel 4.14, pemilihan nilai-nilai parameter tersebut didasarkan pada pertimbangan berikut: `n_estimators` 100 dan 200 dipilih karena pada dataset dengan jumlah baris di bawah 1.000, penambahan pohon di atas 200 umumnya tidak memberikan peningkatan performa yang signifikan. `max_depth` None (tidak dibatasi) dan 10 dipilih untuk membandingkan model yang cenderung *overfit* vs model yang lebih terregularisasi. Nilai `min_samples_split` dan `min_samples_leaf` yang lebih kecil cenderung menghasilkan pohon yang lebih dalam dan kompleks, sementara nilai lebih besar berfungsi sebagai regularisasi.

Total kombinasi parameter yang diuji untuk Random Forest adalah **2 × 2 × 2 × 2 = 16 kombinasi** per skenario, atau **32 model RF** secara keseluruhan (untuk kedua skenario). Dengan 5-fold cross-validation, total *fits* yang dilakukan adalah 32 × 5 = 160 *fits*.

#### Hasil Hyperparameter Tuning RF — Skenario 1

Hasil GridSearchCV untuk Random Forest pada Skenario 1 ditampilkan pada Tabel 4.15 (16 kombinasi, diurutkan berdasarkan ranking F1-weighted).

**Tabel 4.15  Hasil Hyperparameter Tuning RF Skenario 1 (16 Kombinasi)**

| Rank | n_estimators | max_depth | min_samples_split | min_samples_leaf | CV Accuracy | CV Precision | CV Recall | CV F1-weighted |
|---|---|---|---|---|---|---|---|---|
| 1 | 200 | 10 | 2 | 1 | 0,7161 | 0,7218 | 0,7161 | 0,7166 |
| 2 | 100 | 10 | 2 | 1 | 0,7162 | 0,7209 | 0,7162 | 0,7162 |
| 3 | 100 | None | 5 | 1 | 0,7076 | 0,7167 | 0,7076 | 0,7093 |
| 4 | 100 | 10 | 5 | 1 | 0,7048 | 0,7161 | 0,7048 | 0,7077 |
| 5 | 200 | None | 5 | 1 | 0,7033 | 0,7102 | 0,7033 | 0,7040 |
| 6 | 100 | 10 | 2 | 2 | 0,6961 | 0,7111 | 0,6961 | 0,7001 |
| 7 | 100 | None | 2 | 2 | 0,6976 | 0,7085 | 0,6976 | 0,6999 |
| 8 | 200 | 10 | 5 | 1 | 0,6948 | 0,7056 | 0,6948 | 0,6976 |
| 9 | 200 | None | 5 | 2 | 0,6933 | 0,7081 | 0,6933 | 0,6965 |
| 10 | 200 | 10 | 5 | 2 | 0,6919 | 0,7065 | 0,6919 | 0,6957 |
| 11 | 100 | None | 5 | 2 | 0,6905 | 0,7035 | 0,6905 | 0,6938 |
| 12 | 200 | 10 | 2 | 2 | 0,6890 | 0,7042 | 0,6890 | 0,6930 |
| 13 | 200 | None | 2 | 1 | 0,6990 | 0,6926 | 0,6990 | 0,6922 |
| 14 | 100 | None | 2 | 1 | 0,6976 | 0,6908 | 0,6976 | 0,6921 |
| 15 | 100 | 10 | 5 | 2 | 0,6876 | 0,7021 | 0,6876 | 0,6919 |
| 16 | 200 | None | 2 | 2 | 0,6847 | 0,6986 | 0,6847 | 0,6872 |

*Sumber: `rf_scenario1/01_gridsearch_all_combinations.csv` dari `scripts/03_modelling.py`*

Dari Tabel 4.19 terlihat bahwa kombinasi dengan `max_depth=10` (model terbatas) konsisten mendominasi peringkat teratas, menunjukkan bahwa pembatasan kedalaman pohon justru menghasilkan generalisasi yang lebih baik pada dataset ini dibandingkan pohon tanpa batas (`max_depth=None`). Kombinasi dengan `min_samples_leaf=1` juga mendominasi posisi atas, mengindikasikan bahwa granularitas klasifikasi yang lebih tinggi pada *leaf node* lebih menguntungkan untuk dataset ini.

Dari hasil GridSearchCV pada Tabel 4.15, kombinasi parameter terbaik untuk Random Forest pada Skenario 1 adalah:

- `n_estimators = 200`
- `max_depth = 10`
- `min_samples_split = 2`
- `min_samples_leaf = 1`

dengan CV F1-weighted sebesar **0,7166**. Model RF Skenario 1 dengan kombinasi parameter terbaik ini selanjutnya dilatih ulang pada keseluruhan *training set* dan disimpan dalam format pickle (`model.pkl`) untuk digunakan pada tahap evaluasi (sub-bab 4.8).

#### Hasil Hyperparameter Tuning RF — Skenario 2

Hasil GridSearchCV untuk Random Forest pada Skenario 2 ditampilkan pada Tabel 4.16.

**Tabel 4.16  Hasil Hyperparameter Tuning RF Skenario 2 (16 Kombinasi)**

| Rank | n_estimators | max_depth | min_samples_split | min_samples_leaf | CV Accuracy | CV Precision | CV Recall | CV F1-weighted |
|---|---|---|---|---|---|---|---|---|
| 1 | 200 | None | 5 | 1 | 0,7104 | 0,7225 | 0,7104 | 0,7118 |
| 2 | 200 | 10 | 5 | 1 | 0,7090 | 0,7220 | 0,7090 | 0,7109 |
| 3 | 100 | None | 2 | 2 | 0,7090 | 0,7210 | 0,7090 | 0,7106 |
| 4 | 100 | 10 | 5 | 1 | 0,7062 | 0,7169 | 0,7062 | 0,7075 |
| 5 | 100 | None | 5 | 2 | 0,7047 | 0,7167 | 0,7047 | 0,7066 |
| 6 | 200 | None | 2 | 2 | 0,7048 | 0,7185 | 0,7048 | 0,7062 |
| 7 | 100 | 10 | 2 | 2 | 0,7019 | 0,7131 | 0,7019 | 0,7034 |
| 8 | 200 | 10 | 2 | 2 | 0,7004 | 0,7138 | 0,7004 | 0,7022 |
| 9 | 100 | None | 5 | 1 | 0,7004 | 0,7116 | 0,7004 | 0,7017 |
| 10 | 200 | None | 5 | 2 | 0,6990 | 0,7116 | 0,6990 | 0,7005 |
| 11 | 100 | None | 2 | 1 | 0,6990 | 0,7109 | 0,6990 | 0,6999 |
| 12 | 200 | 10 | 2 | 1 | 0,6976 | 0,7102 | 0,6976 | 0,6993 |
| 13 | 200 | None | 2 | 1 | 0,6947 | 0,7071 | 0,6947 | 0,6963 |
| 14 | 200 | 10 | 5 | 2 | 0,6919 | 0,7057 | 0,6919 | 0,6936 |
| 15 | 100 | 10 | 5 | 2 | 0,6904 | 0,7045 | 0,6904 | 0,6923 |
| 16 | 100 | 10 | 2 | 1 | 0,6776 | 0,6891 | 0,6776 | 0,6793 |

*Sumber: `rf_scenario2/01_gridsearch_all_combinations.csv` dari `scripts/03_modelling.py`*

Dari Tabel 4.24 terlihat perbedaan pola dibandingkan Skenario 1: kombinasi dengan `max_depth=None` justru mendominasi peringkat atas pada Skenario 2. Hal ini dapat dikaitkan dengan distribusi kelas yang lebih merata pada Skenario 2, sehingga model yang lebih kompleks (kedalaman tidak dibatasi) lebih mampu menangkap batas keputusan yang lebih halus antar kelas.

Kombinasi parameter terbaik untuk Random Forest pada Skenario 2 adalah:

- `n_estimators = 200`
- `max_depth = None`
- `min_samples_split = 5`
- `min_samples_leaf = 1`

dengan CV F1-weighted sebesar **0,7118**.

### 4.7.2  Support Vector Machine

Support Vector Machine diimplementasikan menggunakan class `SVC` dari `scikit-learn` yang dibungkus dalam *Pipeline* bersama `StandardScaler` untuk normalisasi fitur secara terintegrasi (lihat sub-bab 4.5.4). *Hyperparameter grid* yang diuji disajikan pada Tabel 4.17, merupakan versi revisi dari Tabel 3.11 pada Bab III.

**Tabel 4.17  Hyperparameter Grid untuk SVM**

| Parameter | Nilai yang Diuji |
|---|---|
| `kernel` | linear, rbf, poly |
| `C` | 0,1; 1; 10 |
| `gamma` | scale, 0,1 |

Dari Tabel 4.17, parameter `C` mengontrol keseimbangan antara memaksimalkan *margin* dan meminimalkan kesalahan klasifikasi — nilai kecil (0,1) menghasilkan *soft margin* yang lebih toleran terhadap *misclassification*, sementara nilai besar (10) menghasilkan batas yang lebih ketat. Parameter `gamma` mengontrol jangkauan pengaruh setiap titik data — nilai `scale` berarti gamma dihitung otomatis dari data, sementara nilai 0,1 ditetapkan secara manual untuk perbandingan. Tiga jenis kernel (linear, rbf, poly) dipilih untuk menguji kemampuan pemisahan linear, non-linear berbasis fungsi Gaussian, dan non-linear berbasis fungsi polinomial.

Total kombinasi parameter yang diuji untuk SVM adalah **3 × 3 × 2 = 18 kombinasi** per skenario, atau **36 model SVM** secara keseluruhan. Dengan 5-fold cross-validation, total *fits* yang dilakukan adalah 36 × 5 = 180 *fits*.

#### Hasil Hyperparameter Tuning SVM — Skenario 1

**Tabel 4.18  Hasil Hyperparameter Tuning SVM Skenario 1 (18 Kombinasi)**

| Rank | kernel | C | gamma | CV Accuracy | CV Precision | CV Recall | CV F1-weighted |
|---|---|---|---|---|---|---|---|
| 1 | rbf | 10,0 | 0,1 | 0,6419 | 0,6791 | 0,6419 | 0,6539 |
| 2 | rbf | 10,0 | scale | 0,6333 | 0,6732 | 0,6333 | 0,6463 |
| 3 | poly | 10,0 | 0,1 | 0,6305 | 0,6640 | 0,6305 | 0,6410 |
| 4 | rbf | 1,0 | 0,1 | 0,6305 | 0,6609 | 0,6305 | 0,6389 |
| 5 | rbf | 1,0 | scale | 0,6248 | 0,6531 | 0,6248 | 0,6314 |
| 6 | poly | 10,0 | scale | 0,6120 | 0,6497 | 0,6120 | 0,6236 |
| 7 | poly | 1,0 | 0,1 | 0,5934 | 0,6396 | 0,5934 | 0,6075 |
| 8 | poly | 1,0 | scale | 0,5792 | 0,6252 | 0,5792 | 0,5910 |
| 9 | rbf | 0,1 | 0,1 | 0,6263 | 0,6000 | 0,6263 | 0,5876 |
| 10 | rbf | 0,1 | scale | 0,6291 | 0,6245 | 0,6291 | 0,5808 |
| 11 | poly | 0,1 | 0,1 | 0,5620 | 0,6079 | 0,5620 | 0,5705 |
| 12 | linear | 1,0 | 0,1 | 0,5762 | 0,5738 | 0,5762 | 0,5574 |
| 12 | linear | 1,0 | scale | 0,5762 | 0,5738 | 0,5762 | 0,5574 |
| 14 | linear | 10,0 | scale | 0,5762 | 0,5734 | 0,5762 | 0,5571 |
| 14 | linear | 10,0 | 0,1 | 0,5762 | 0,5734 | 0,5762 | 0,5571 |
| 16 | linear | 0,1 | scale | 0,5748 | 0,5672 | 0,5748 | 0,5530 |
| 16 | linear | 0,1 | 0,1 | 0,5748 | 0,5672 | 0,5748 | 0,5530 |
| 18 | poly | 0,1 | scale | 0,4649 | 0,5832 | 0,4649 | 0,4700 |

*Sumber: `svm_scenario1/01_gridsearch_all_combinations.csv` dari `scripts/03_modelling.py`*

Dari Tabel 4.18 terlihat bahwa kernel RBF secara konsisten mendominasi peringkat teratas, mengindikasikan bahwa pola kepadatan lalu lintas pada dataset ini tidak dapat dipisahkan secara linear dan memerlukan fungsi kernel non-linear. Kernel linear menempati posisi bawah tabel, mengonfirmasi bahwa batas keputusan antar kelas bersifat non-linear.

Kombinasi parameter terbaik untuk SVM pada Skenario 1 adalah:

- `kernel = rbf`
- `C = 10`
- `gamma = 0,1`

dengan CV F1-weighted sebesar **0,6539**.

#### Hasil Hyperparameter Tuning SVM — Skenario 2

**Tabel 4.19  Hasil Hyperparameter Tuning SVM Skenario 2 (18 Kombinasi)**

| Rank | kernel | C | gamma | CV Accuracy | CV Precision | CV Recall | CV F1-weighted |
|---|---|---|---|---|---|---|---|
| 1 | rbf | 1,0 | 0,1 | 0,6591 | 0,6760 | 0,6591 | 0,6591 |
| 2 | rbf | 1,0 | scale | 0,6576 | 0,6769 | 0,6576 | 0,6571 |
| 3 | rbf | 10,0 | scale | 0,6405 | 0,6563 | 0,6405 | 0,6413 |
| 4 | rbf | 10,0 | 0,1 | 0,6377 | 0,6550 | 0,6377 | 0,6396 |
| 5 | rbf | 0,1 | 0,1 | 0,6148 | 0,6380 | 0,6148 | 0,6109 |
| 6 | poly | 1,0 | scale | 0,6149 | 0,6283 | 0,6149 | 0,6078 |
| 7 | poly | 1,0 | 0,1 | 0,6135 | 0,6327 | 0,6135 | 0,6078 |
| 8 | poly | 10,0 | scale | 0,6063 | 0,6175 | 0,6063 | 0,6036 |
| 9 | poly | 10,0 | 0,1 | 0,6049 | 0,6140 | 0,6049 | 0,6027 |
| 10 | rbf | 0,1 | scale | 0,6063 | 0,6281 | 0,6063 | 0,6000 |
| 11 | poly | 0,1 | 0,1 | 0,6091 | 0,6237 | 0,6091 | 0,5999 |
| 12 | poly | 0,1 | scale | 0,5849 | 0,6171 | 0,5849 | 0,5547 |
| 13 | linear | 10,0 | 0,1 | 0,5492 | 0,5532 | 0,5492 | 0,5235 |
| 13 | linear | 10,0 | scale | 0,5492 | 0,5532 | 0,5492 | 0,5235 |
| 15 | linear | 1,0 | scale | 0,5478 | 0,5518 | 0,5478 | 0,5225 |
| 15 | linear | 1,0 | 0,1 | 0,5478 | 0,5518 | 0,5478 | 0,5225 |
| 17 | linear | 0,1 | 0,1 | 0,5464 | 0,5503 | 0,5464 | 0,5214 |
| 17 | linear | 0,1 | scale | 0,5464 | 0,5503 | 0,5464 | 0,5214 |

*Sumber: `svm_scenario2/01_gridsearch_all_combinations.csv` dari `scripts/03_modelling.py`*

Dari Tabel 4.15 terlihat bahwa pola serupa dengan Skenario 1 di mana kernel RBF mendominasi. Perbedaan utama adalah nilai `C` terbaik menurun dari 10 (S1) menjadi 1 (S2), yang mengindikasikan bahwa dengan distribusi kelas yang lebih seimbang pada Skenario 2, model SVM yang lebih *soft* (toleran terhadap kesalahan) justru lebih generalisatif.

Kombinasi parameter terbaik untuk SVM pada Skenario 2 adalah:

- `kernel = rbf`
- `C = 1`
- `gamma = 0,1`

dengan CV F1-weighted sebesar **0,6591**.

### Ringkasan Best Model dari Tahap Modelling

Hasil ringkasan empat *best model* dari tahap modelling (sebelum evaluasi pada *testing set*) disajikan pada Tabel 4.20.

**Tabel 4.20  Ringkasan Best Model Hasil Hyperparameter Tuning**

| Algoritma | Skenario | Best Parameters | CV F1-weighted |
|---|---|---|---|
| Random Forest | 1 | `n_estimators=200, max_depth=10, min_samples_split=2, min_samples_leaf=1` | 0,7166 |
| Random Forest | 2 | `n_estimators=200, max_depth=None, min_samples_split=5, min_samples_leaf=1` | 0,7118 |
| SVM | 1 | `kernel=rbf, C=10, gamma=0,1` | 0,6539 |
| SVM | 2 | `kernel=rbf, C=1, gamma=0,1` | 0,6591 |

Dari Tabel 4.16 terlihat bahwa secara keseluruhan Random Forest menghasilkan CV F1-weighted lebih tinggi dibandingkan SVM pada masing-masing skenario yang sama, dengan selisih sekitar 6–5 poin persentase. Menariknya, nilai CV F1-weighted Skenario 1 (RF: 0,7166; SVM: 0,6539) lebih tinggi dibandingkan Skenario 2 (RF: 0,7118; SVM: 0,6591) untuk kedua algoritma, yang akan diverifikasi lebih lanjut pada evaluasi *testing set*.

Keempat *best model* di atas selanjutnya dievaluasi pada *testing set* untuk memperoleh gambaran performa model pada data yang belum pernah dilihat selama proses training, sebagaimana disajikan pada sub-bab 4.8.

---

> **Catatan akhir blok 2:**
> Sub-bab 4.8 (Hasil Evaluasi Model) dan 4.9 (Hasil Implementasi Sistem) akan dilanjutkan pada blok berikutnya.

---

## 4.8  Hasil Evaluasi Model

Pada sub-bab ini disajikan hasil evaluasi keempat *best model* yang telah diperoleh dari proses hyperparameter tuning pada sub-bab 4.7. Evaluasi dilakukan pada *testing set* (176 baris atau 20% dari dataset) yang belum pernah dilihat selama proses training. Hal ini bertujuan memperoleh gambaran objektif mengenai kemampuan generalisasi model pada data baru.

Metrik evaluasi yang digunakan meliputi *Accuracy*, *Precision*, *Recall*, dan *F1-score* dengan rata-rata terbobot (*weighted average*), sebagaimana telah dijelaskan pada sub-bab 2.10. Selain itu, dilaporkan pula metrik per kelas (Rendah, Sedang, Tinggi) dan *confusion matrix* untuk memberikan gambaran detail tentang pola kesalahan klasifikasi.

### 4.8.1  Evaluasi Random Forest

#### Evaluasi RF — Skenario 1

*Confusion matrix* hasil prediksi Random Forest pada *testing set* Skenario 1 disajikan pada Tabel 4.21.

**Tabel 4.21  Confusion Matrix Random Forest Skenario 1**

| Aktual \ Prediksi | Rendah | Sedang | Tinggi | Total |
|---|---|---|---|---|
| **Rendah** | **76** | 10 | 7 | 93 |
| **Sedang** | 12 | **19** | 10 | 41 |
| **Tinggi** | 2 | 6 | **34** | 42 |
| **Total** | 90 | 35 | 51 | 176 |

Visualisasi confusion matrix ditampilkan pada Gambar 4.7.

![Gambar 4.7 Confusion Matrix Random Forest Skenario 1](03_modelling/rf_scenario1/03_confusion_matrix.png)
> 📎 `rf_scenario1/03_confusion_matrix.png` dari `scripts/03_modelling.py`

**Gambar 4.7**  Confusion matrix Random Forest Skenario 1 (kiri: count, kanan: normalisasi per baris).

Dari Gambar 4.7 dan Tabel 4.21, terlihat bahwa model berhasil memprediksi dengan benar 76 dari 93 baris kelas Rendah (81,72%) dan 34 dari 42 baris kelas Tinggi (80,95%). Namun, kelas Sedang hanya berhasil diprediksi dengan benar 19 dari 41 baris (46,34%), dengan 12 baris terprediksi sebagai Rendah dan 10 baris sebagai Tinggi. Pola kesalahan ini konsisten dengan sifat kelas Sedang yang merupakan kondisi transisi di antara dua kondisi ekstrem.

Metrik evaluasi per kelas untuk RF Skenario 1 disajikan pada Tabel 4.22.

**Tabel 4.22  Metrik Evaluasi per Kelas — RF Skenario 1**

| Kelas | Precision | Recall | F1-score | Support |
|---|---|---|---|---|
| Rendah | 0,8444 | 0,8172 | 0,8306 | 93 |
| Sedang | 0,5429 | 0,4634 | 0,5000 | 41 |
| Tinggi | 0,6667 | 0,8095 | 0,7312 | 42 |
| **Accuracy** |  |  | **0,7330** | **176** |
| **Macro avg** | 0,6846 | 0,6967 | 0,6873 | 176 |
| **Weighted avg** | 0,7318 | 0,7330 | 0,7299 | 176 |

*Sumber: `rf_scenario1/04_classification_report.txt` dari `scripts/03_modelling.py`*

Dari Tabel 4.22, nilai *accuracy* keseluruhan sebesar 73,30% menunjukkan bahwa model berhasil mengklasifikasikan 129 dari 176 baris data *testing* dengan benar. Perbedaan yang mencolok antara F1-score kelas Rendah (0,8306), Tinggi (0,7312), dan Sedang (0,5000) mengindikasikan bahwa model lebih andal dalam membedakan kondisi ekstrem dibandingkan kondisi transisi. Nilai *macro avg* F1-score yang lebih rendah dari *weighted avg* (0,6873 vs 0,7299) mencerminkan adanya ketimpangan performa antar kelas.

*Feature importance* dari Random Forest Skenario 1 disajikan pada Gambar 4.8.

![Gambar 4.8 Feature Importance Random Forest Skenario 1](03_modelling/rf_scenario1/05_feature_importance.png)
> 📎 `rf_scenario1/05_feature_importance.png` dari `scripts/03_modelling.py`

**Gambar 4.8**  Feature importance Random Forest Skenario 1.

Dari Gambar 4.8, empat fitur teratas yang paling berpengaruh adalah `Mobil` (0,190), `Motor` (0,177), `Total_Kendaraan` (0,170), dan `Jam` (0,168), dengan kontribusi yang hampir setara. Sementara itu, seluruh fitur `Hari_*` (hasil one-hot encoding) berkontribusi sangat kecil (< 0,04), mengindikasikan bahwa pola kepadatan di Jalan Diponegoro Musi Utara tidak banyak dipengaruhi oleh hari dalam minggu.

#### Evaluasi RF — Skenario 2

**Tabel 4.23  Confusion Matrix Random Forest Skenario 2**

| Aktual \ Prediksi | Rendah | Sedang | Tinggi | Total |
|---|---|---|---|---|
| **Rendah** | **40** | 17 | 4 | 61 |
| **Sedang** | 9 | **45** | 19 | 73 |
| **Tinggi** | 2 | 13 | **27** | 42 |
| **Total** | 51 | 75 | 50 | 176 |

![Gambar 4.9 Confusion Matrix Random Forest Skenario 2](03_modelling/rf_scenario2/03_confusion_matrix.png)
> 📎 `rf_scenario2/03_confusion_matrix.png` dari `scripts/03_modelling.py`

**Gambar 4.9**  Confusion matrix Random Forest Skenario 2.

Dibandingkan Skenario 1, Gambar 4.9 menunjukkan peningkatan kemampuan model dalam mendeteksi kelas Sedang (recall meningkat dari 46,34% menjadi 61,64%), namun dengan trade-off penurunan recall pada kelas Rendah (81,72% menjadi 65,57%) dan Tinggi (80,95% menjadi 64,29%). Peningkatan pada kelas Sedang ini selaras dengan penambahan data berlabel Sedang akibat penerapan aturan "ramai lancar" pada Skenario 2.

**Tabel 4.24  Metrik Evaluasi per Kelas — RF Skenario 2**

| Kelas | Precision | Recall | F1-score | Support |
|---|---|---|---|---|
| Rendah | 0,7843 | 0,6557 | 0,7143 | 61 |
| Sedang | 0,6000 | 0,6164 | 0,6081 | 73 |
| Tinggi | 0,5400 | 0,6429 | 0,5870 | 42 |
| **Accuracy** |  |  | **0,6364** | **176** |
| **Macro avg** | 0,6414 | 0,6383 | 0,6365 | 176 |
| **Weighted avg** | 0,6496 | 0,6364 | 0,6399 | 176 |

*Sumber: `rf_scenario2/04_classification_report.txt` dari `scripts/03_modelling.py`*

Dari Tabel 4.24 terlihat bahwa *accuracy* RF Skenario 2 (63,64%) lebih rendah dibandingkan Skenario 1 (73,30%), namun distribusi F1-score antar kelas lebih merata: Rendah (0,7143), Sedang (0,6081), dan Tinggi (0,5870). Hal ini mengindikasikan bahwa Skenario 2 menghasilkan model yang lebih adil antar kelas meskipun secara agregat performanya sedikit lebih rendah.

![Gambar 4.10 Feature Importance Random Forest Skenario 2](03_modelling/rf_scenario2/05_feature_importance.png)
> 📎 `rf_scenario2/05_feature_importance.png` dari `scripts/03_modelling.py`

**Gambar 4.10**  Feature importance Random Forest Skenario 2.

Dari Gambar 4.10, pola feature importance pada Skenario 2 serupa dengan Skenario 1, di mana `Mobil`, `Motor`, `Total_Kendaraan`, dan `Jam` tetap menjadi empat fitur teratas. Konsistensi pola ini pada kedua skenario memperkuat temuan bahwa keempat fitur tersebut merupakan prediktor utama tingkat kepadatan, terlepas dari skema labeling yang digunakan.

### 4.8.2  Evaluasi Support Vector Machine

#### Evaluasi SVM — Skenario 1

**Tabel 4.25  Confusion Matrix SVM Skenario 1**

| Aktual \ Prediksi | Rendah | Sedang | Tinggi | Total |
|---|---|---|---|---|
| **Rendah** | **68** | 17 | 8 | 93 |
| **Sedang** | 11 | **16** | 14 | 41 |
| **Tinggi** | 6 | 5 | **31** | 42 |
| **Total** | 85 | 38 | 53 | 176 |

![Gambar 4.11 Confusion Matrix SVM Skenario 1](03_modelling/svm_scenario1/03_confusion_matrix.png)
> 📎 `svm_scenario1/03_confusion_matrix.png` dari `scripts/03_modelling.py`

**Gambar 4.11**  Confusion matrix SVM Skenario 1.

Dibandingkan RF Skenario 1 (Gambar 4.7), Gambar 4.11 menunjukkan pola kesalahan yang serupa namun dengan magnitud yang lebih besar, khususnya pada kelas Sedang yang hanya berhasil diprediksi benar sebanyak 16 dari 41 baris (39,02%). SVM juga menghasilkan lebih banyak *false positive* pada kelas Tinggi (53 prediksi Tinggi vs 42 aktual Tinggi), yang mengindikasikan model SVM lebih agresif dalam memprediksi kondisi Tinggi.

**Tabel 4.26  Metrik Evaluasi per Kelas — SVM Skenario 1**

| Kelas | Precision | Recall | F1-score | Support |
|---|---|---|---|---|
| Rendah | 0,8000 | 0,7312 | 0,7640 | 93 |
| Sedang | 0,4211 | 0,3902 | 0,4051 | 41 |
| Tinggi | 0,5849 | 0,7381 | 0,6526 | 42 |
| **Accuracy** |  |  | **0,6534** | **176** |
| **Macro avg** | 0,6020 | 0,6199 | 0,6072 | 176 |
| **Weighted avg** | 0,6604 | 0,6534 | 0,6538 | 176 |

*Sumber: `svm_scenario1/04_classification_report.txt` dari `scripts/03_modelling.py`*

Dari Tabel 4.26, *accuracy* SVM Skenario 1 (65,34%) lebih rendah dibandingkan RF Skenario 1 (73,30%), dengan perbedaan paling mencolok pada kelas Sedang di mana F1-score SVM (0,4051) jauh di bawah RF (0,5000). Nilai *macro avg* F1-score sebesar 0,6072 menunjukkan ketimpangan performa antar kelas yang lebih besar dibandingkan RF (0,6873).

Karena SVM dengan kernel RBF (kernel terbaik dari hyperparameter tuning) tidak memiliki *feature importance* native, peneliti menggunakan **Permutation Importance** untuk memperoleh estimasi kontribusi fitur. Permutation Importance dihitung dengan cara mengacak nilai satu fitur tertentu pada *testing set* dan mengukur penurunan performa model — semakin besar penurunan, semakin penting fitur tersebut. Hasil Permutation Importance untuk SVM Skenario 1 disajikan pada Gambar 4.12.

![Gambar 4.12 Permutation Importance SVM Skenario 1](03_modelling/svm_scenario1/05_permutation_importance.png)
> 📎 `svm_scenario1/05_permutation_importance.png` dari `scripts/03_modelling.py`

**Gambar 4.12**  Permutation importance SVM Skenario 1 (dengan error bar dari 10 iterasi).

Dari Gambar 4.12, pola permutation importance pada SVM Skenario 1 menunjukkan kemiripan dengan feature importance RF, di mana fitur-fitur volume kendaraan (`Mobil`, `Motor`, `Total_Kendaraan`) dan `Jam` mendominasi. Error bar yang cukup besar pada beberapa fitur mengindikasikan variabilitas kepentingan fitur antar iterasi pengacakan, yang merupakan karakteristik normal dari permutation importance pada dataset berukuran relatif kecil.

#### Evaluasi SVM — Skenario 2

**Tabel 4.27  Confusion Matrix SVM Skenario 2**

| Aktual \ Prediksi | Rendah | Sedang | Tinggi | Total |
|---|---|---|---|---|
| **Rendah** | **39** | 14 | 8 | 61 |
| **Sedang** | 11 | **39** | 23 | 73 |
| **Tinggi** | 3 | 11 | **28** | 42 |
| **Total** | 53 | 64 | 59 | 176 |

![Gambar 4.13 Confusion Matrix SVM Skenario 2](03_modelling/svm_scenario2/03_confusion_matrix.png)
> 📎 `svm_scenario2/03_confusion_matrix.png` dari `scripts/03_modelling.py`

**Gambar 4.13**  Confusion matrix SVM Skenario 2.

Gambar 4.13 menunjukkan pola yang serupa dengan RF Skenario 2, di mana kelas Sedang berhasil diprediksi lebih baik (39 benar dari 73) dibandingkan SVM Skenario 1 (16 benar dari 41). Namun kelas Rendah mengalami penurunan recall (39 benar dari 61, atau 63,93%), dan kelas Tinggi juga menurun (28 benar dari 42, atau 66,67%).

**Tabel 4.28  Metrik Evaluasi per Kelas — SVM Skenario 2**

| Kelas | Precision | Recall | F1-score | Support |
|---|---|---|---|---|
| Rendah | 0,7358 | 0,6393 | 0,6842 | 61 |
| Sedang | 0,6094 | 0,5342 | 0,5693 | 73 |
| Tinggi | 0,4746 | 0,6667 | 0,5545 | 42 |
| **Accuracy** |  |  | **0,6023** | **176** |
| **Macro avg** | 0,6066 | 0,6134 | 0,6027 | 176 |
| **Weighted avg** | 0,6210 | 0,6023 | 0,6056 | 176 |

*Sumber: `svm_scenario2/04_classification_report.txt` dari `scripts/03_modelling.py`*

Dari Tabel 4.28, *accuracy* SVM Skenario 2 (60,23%) merupakan yang terendah di antara keempat model. Namun distribusi F1-score antar kelas pada SVM Skenario 2 (Rendah: 0,6842; Sedang: 0,5693; Tinggi: 0,5545) relatif lebih merata dibandingkan SVM Skenario 1 (Rendah: 0,7640; Sedang: 0,4051; Tinggi: 0,6526), selaras dengan efek penyeimbangan distribusi dari Skenario 2.

![Gambar 4.14 Permutation Importance SVM Skenario 2](03_modelling/svm_scenario2/05_permutation_importance.png)
> 📎 `svm_scenario2/05_permutation_importance.png` dari `scripts/03_modelling.py`

**Gambar 4.14**  Permutation importance SVM Skenario 2.

Dari Gambar 4.14, pola permutation importance pada SVM Skenario 2 secara umum konsisten dengan SVM Skenario 1, mengonfirmasi bahwa perubahan skema labeling tidak mengubah fitur-fitur yang paling berpengaruh pada model.

### 4.8.3  Komparasi dan Pemilihan Model Terbaik

Ringkasan metrik evaluasi seluruh empat model pada *testing set* disajikan pada Tabel 4.29.

**Tabel 4.29  Ringkasan Komparasi Metrik Evaluasi 4 Model pada Testing Set**

| Model | Skenario | Accuracy | Precision (w) | Recall (w) | F1-score (w) | F1-score (macro) |
|---|---|---|---|---|---|---|
| **Random Forest** | **1** | **0,7330** | **0,7318** | **0,7330** | **0,7299** | 0,6873 |
| Random Forest | 2 | 0,6364 | 0,6496 | 0,6364 | 0,6399 | 0,6365 |
| SVM | 1 | 0,6534 | 0,6604 | 0,6534 | 0,6538 | 0,6072 |
| SVM | 2 | 0,6023 | 0,6210 | 0,6023 | 0,6056 | 0,6027 |

*Catatan: (w) = weighted average. Nilai tertinggi pada setiap kolom dicetak tebal.*
> 📎 `03_modelling/ringkasan_4_model.csv` dari `scripts/03_modelling.py`

Visualisasi komparasi keempat model pada lima metrik utama ditampilkan pada Gambar 4.15.

![Gambar 4.15 Komparasi Metrik Evaluasi 4 Model](04_comparison/01_grouped_bar_4model.png)
> 📎 `04_comparison/01_grouped_bar_4model.png` dari `scripts/04_comparison.py`

**Gambar 4.15**  Komparasi metrik evaluasi 4 model pada testing set.

Dari Gambar 4.15 terlihat secara visual bahwa RF Skenario 1 (batang paling kiri) secara konsisten memiliki nilai tertinggi pada seluruh lima metrik yang ditampilkan. Terdapat pola penurunan performa dari kiri ke kanan (RF S1 → SVM S1 → RF S2 → SVM S2) pada metrik *accuracy* dan F1-weighted, meskipun F1-macro menunjukkan pola yang sedikit berbeda.

Visualisasi confusion matrix keempat model secara berdampingan ditampilkan pada Gambar 4.16.

![Gambar 4.16 Confusion Matrix Komparasi 4 Model](04_comparison/02_confusion_matrix_4panel.png)
> 📎 `04_comparison/02_confusion_matrix_4panel.png` dari `scripts/04_comparison.py`

**Gambar 4.16**  Confusion matrix komparasi 4 model (count + normalisasi per baris).

Dari Gambar 4.16, perbandingan keempat confusion matrix mempertegas pola yang telah dijelaskan secara individual: kelas Sedang (baris tengah) secara konsisten memiliki nilai diagonal (recall) terendah di semua model, sementara kelas Rendah dan Tinggi menunjukkan recall yang lebih tinggi. Perbandingan RF S1 vs RF S2 (kolom kiri) secara visual memperlihatkan peningkatan diagonal kelas Sedang namun penurunan diagonal kelas Rendah dan Tinggi, yang merupakan trade-off utama antara kedua skenario.

Untuk perbandingan metrik per kelas antar model, visualisasi disajikan pada Gambar 4.17.

![Gambar 4.17 Metrik per Kelas 4 Model](04_comparison/03_metrik_per_kelas.png)
> 📎 `04_comparison/03_metrik_per_kelas.png` dari `scripts/04_comparison.py`

**Gambar 4.17**  Komparasi precision, recall, dan F1-score per kelas pada 4 model.

Dari Gambar 4.17, terlihat bahwa seluruh model memiliki performa terbaik pada kelas Rendah dan terlemah pada kelas Sedang, memperkuat temuan yang konsisten di seluruh eksperimen. RF Skenario 1 (batang biru) mendominasi pada kelas Rendah dan Tinggi, sementara pada kelas Sedang perbedaan antar model lebih kecil. Skenario 2 (RF S2 dan SVM S2) secara umum menghasilkan F1-score kelas Sedang yang lebih tinggi namun kelas Rendah yang lebih rendah dibandingkan Skenario 1.

Berdasarkan hasil komparasi pada Tabel 4.29 dan visualisasi pada Gambar 4.15–4.17, **Random Forest Skenario 1** terpilih sebagai **model terbaik** dalam penelitian ini, dengan capaian sebagai berikut:

- **Accuracy: 0,7330 (73,30%)**
- **Precision (weighted): 0,7318**
- **Recall (weighted): 0,7330**
- **F1-score (weighted): 0,7299**
- **F1-score (macro): 0,6873**

dengan konfigurasi *hyperparameter* terbaik:

- `n_estimators = 200`
- `max_depth = 10`
- `min_samples_split = 2`
- `min_samples_leaf = 1`
- `class_weight = 'balanced'`
- `random_state = 42`

Model RF Skenario 1 ini selanjutnya menjadi model yang diintegrasikan ke dalam aplikasi web berbasis Flask, sebagaimana dijelaskan pada sub-bab 4.9. Analisis lebih mendalam mengenai komparasi keempat model — termasuk *trade-off* antara Skenario 1 dan Skenario 2, perbedaan performa RF vs SVM, dan interpretasi pola pada *confusion matrix* — disajikan pada Bab V (Pembahasan).

---

## 4.9  Hasil Implementasi Sistem (Aplikasi Web Flask)

Tahap akhir penelitian adalah implementasi *best model* (Random Forest Skenario 1) ke dalam aplikasi web berbasis Flask yang dapat digunakan oleh pengguna dari DISHUB Surabaya untuk melakukan klasifikasi tingkat kepadatan lalu lintas secara mandiri.

### 4.9.1  Arsitektur Sistem

`[TODO: Buat sub-bab 4.9.1 yang menjelaskan arsitektur sistem secara high-level. Disarankan menyertakan:]`

`[TODO: 1) Diagram arsitektur sistem (komponen frontend Flask + backend model RF + database MySQL/SQLite).]`

`[TODO: 2) Penjelasan singkat masing-masing komponen.]`

`[TODO: 3) Alur data dari user upload CSV hingga hasil klasifikasi ditampilkan.]`

### 4.9.2  Implementasi User Interface

`[TODO: Lampirkan screenshot halaman-halaman utama aplikasi web:]`

`[TODO: Gambar 4.18 — Halaman Login]`

`[TODO: Gambar 4.19 — Halaman Upload Data CSV]`

`[TODO: Gambar 4.20 — Halaman Dashboard Statistik Kepadatan]`

`[TODO: Gambar 4.21 — Halaman Validasi & Koreksi Hasil Klasifikasi]`

`[TODO: Gambar 4.22 — Halaman Prediksi Real-time / Hasil Klasifikasi]`

`[TODO: Gambar 4.23 — Halaman Retraining Model (jika ada)]`

`[TODO: Setiap gambar diiringi 2-3 kalimat penjelasan fitur utamanya.]`

### 4.9.3  Struktur Database

`[TODO: Jelaskan skema database yang digunakan untuk menyimpan:]`
- `[TODO: Data hasil ekstraksi yang diunggah pengguna]`
- `[TODO: Hasil klasifikasi]`
- `[TODO: Riwayat validasi/koreksi oleh pengguna]`
- `[TODO: Data pengguna (admin, staff DISHUB, masyarakat)]`

`[TODO: Sertakan Entity-Relationship Diagram (ERD) jika sudah dibuat.]`

### 4.9.4  Integrasi Model ke Sistem

`[TODO: Jelaskan secara teknis bagaimana model RF (.pkl) diintegrasikan ke Flask:]`
- `[TODO: Penggunaan library joblib/pickle untuk load model]`
- `[TODO: Pipeline preprocessing yang harus diterapkan pada data baru sebelum prediksi]`
- `[TODO: Endpoint API yang digunakan untuk prediksi]`

`[TODO: Sertakan snippet kode yang relevan jika diperlukan.]`

`[TODO: Berikan kesimpulan singkat di akhir sub-bab 4.9 bahwa sistem sudah berjalan dengan baik dan siap diuji secara fungsional pada Bab V.]`

---

## Catatan Penutup Bab IV

Bab IV ini telah memaparkan keseluruhan hasil implementasi penelitian, mulai dari pengumpulan data video CCTV, ekstraksi data menggunakan YOLOv8 + DeepSORT, evaluasi keakuratan ekstraksi dengan MAPE, labeling data dengan acuan PKJI 2023 dan HCM, preprocessing data, modelling dengan Random Forest dan SVM, evaluasi keempat *best model* pada *testing set*, hingga implementasi *best model* (Random Forest Skenario 1) ke dalam aplikasi web berbasis Flask. Analisis lebih mendalam mengenai hasil yang diperoleh, termasuk interpretasi pola data, pembahasan limitasi sistem, dan perbandingan dengan penelitian terdahulu, akan dilanjutkan pada Bab V.
