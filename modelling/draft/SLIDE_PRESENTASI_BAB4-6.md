# PANDUAN SLIDE PRESENTASI SKRIPSI — BAB 4–6
**Judul:** Klasifikasi Kepadatan Lalu Lintas Menggunakan Random Forest dan SVM Berbasis Computer Vision YOLOv8 di Jalan Diponegoro Surabaya
**Mahasiswa:** Dani Ruliansyah — D-IV Teknik Informatika, Universitas Airlangga

---

> **Cara membaca file ini:**
> - `🖼️ Gambar` = file gambar yang perlu disisipkan ke slide
> - `📝 Catatan Pembicara` = yang Anda ucapkan secara lisan, tidak perlu tampil di slide
> - `[TODO]` = isi setelah data SUS tersedia
> - Konten dalam slide dibuat ringkas — **slide hanya memuat poin-poin kunci**, detail disampaikan lisan

---

---
# VERSI A — RINGKAS (20 Slide)
### Cocok untuk: Sidang dengan waktu presentasi ±15–20 menit
---

## SLIDE 1 — Cover

**Judul Slide:**
> HASIL, PEMBAHASAN, DAN KESIMPULAN
> BAB IV – BAB VI

**Isi:**
- Nama: Dani Ruliansyah
- NIM: 434221059
- Program Studi: D-IV Teknik Informatika
- Fakultas Vokasi, Universitas Airlangga
- Tahun: 2026

🖼️ **Gambar:** Logo Universitas Airlangga (sertakan sendiri)

📝 **Catatan Pembicara:** Pembuka singkat, perkenalkan bahwa Anda akan memaparkan hasil, pembahasan, dan kesimpulan penelitian.

---

## SLIDE 2 — Outline Presentasi

**Judul Slide:**
> ALUR PRESENTASI

**Isi:**
1. BAB IV — Hasil: 12 tahapan penelitian
2. BAB V — Pembahasan: Interpretasi & Perbandingan
3. BAB VI — Kesimpulan & Saran

🖼️ **Gambar:** `metode_penelitian.png` (flowchart alur penelitian dari BAB 3) sebagai visual pendukung konteks

📝 **Catatan Pembicara:** Ingatkan bahwa presentasi ini fokus pada BAB 4–6. Flowchart ditampilkan agar dewan penguji bisa memposisikan di mana tahapan yang akan dibahas.

---

## SLIDE 3 — Pengumpulan Data & Ekstraksi YOLOv8

**Judul Slide:**
> PENGUMPULAN DATA & EKSTRAKSI YOLOv8

**Isi (2 kolom):**

*Kiri — Pengumpulan Data:*
- Sumber: CCTV SITS DISHUB Kota Surabaya
- Lokasi: Jl. Diponegoro Musi Utara, Surabaya
- Durasi: 21 hari × 8 jam/hari
- Sesi: Pagi 06.00–09.00 & Sore–Malam 15.00–20.00 WIB
- Narahubung: Bu Nina (SITS DISHUB)

*Kanan — Hasil Ekstraksi:*
- Model: YOLOv8m + DeepSORT
- Interval agregasi: per 10 menit
- Total data: **877 baris**
- Kolom: Hari, Jam, Menit, Motor, Mobil, Bus, Truk, Total_Kendaraan

🖼️ **Gambar:** Tidak ada file gambar tersedia — gunakan ikon kamera/CCTV sederhana atau screenshot hasil CSV (contoh beberapa baris dari `output_gabungan_frekuensinq1__catatan.csv`)

📝 **Catatan Pembicara:** Jelaskan bahwa video dipotong per jam menggunakan CapCut, lalu diekstraksi dengan YOLOv8+DeepSORT. 877 baris ini adalah dataset utama seluruh penelitian.

---

## SLIDE 4 — Training YOLOv8 Custom

**Judul Slide:**
> TRAINING MODEL YOLOv8 CUSTOM

**Isi:**

*Mengapa perlu custom training?*
- Model COCO generik → misklasifikasi parah di konteks Indonesia
- Contoh: Bus COCO = **111** unit vs Vehicle Detection = **24** unit (data sama)

*Konfigurasi Training:*
| Parameter | Nilai |
|---|---|
| Base model | YOLOv8m |
| Dataset | Vehicle Detection Roboflow (1.000 img) |
| Epoch | 50 (berhenti di epoch 33, best di epoch 23) |
| Batch size | 8 |

*Hasil model `best.pt` (Epoch 23):*
- mAP@0,5 = **93,49%**
- mAP@0,5:0,95 = **84,89%**
- Precision = 88,79% | Recall = 90,57%

🖼️ **Gambar:** `results.png` (grafik loss & mAP selama training — sudah ada di project)

📝 **Catatan Pembicara:** Tekankan bahwa pemilihan epoch 23 bukan epoch terakhir — mekanisme early stopping YOLOv8 menyimpan bobot terbaik, bukan bobot akhir. Juga sebutkan bahwa eksperimen dataset Traffic Night (5.400 img) dicoba tapi hasilnya lebih buruk (Truk=168 tidak realistis), sehingga ditinggalkan.

---

## SLIDE 5 — Evaluasi Ekstraksi: MAPE

**Judul Slide:**
> EVALUASI AKURASI EKSTRAKSI (MAPE)

**Isi:**

*2 sampel evaluasi manual:*

| Kondisi | Sampel | MAPE |
|---|---|---|
| Pagi (Senin, 08:20–08:30) | Motor 935→624, Mobil 192→189, Truk 1→2 | **44,94%** *(Cukup)* |
| Malam (Sabtu, 19:20–19:30) | Motor 662→14, Mobil 234→107, Truk 1→0 | **84,05%** *(Tidak Akurat)* |
| **Gabungan** | | **64,50%** |

*Catatan:* Bus (aktual=0) dikecualikan dari perhitungan (pembagi nol)

*Interpretasi:*
- Siang: Mobil sangat akurat (APE 1,56%), Motor terbatas akibat oklusi kepadatan
- Malam: Degradasi drastis — hanya 14 dari 662 motor terdeteksi
- MAPE mencerminkan *worst-case* — 2 kondisi ekstrem yang disengaja

🖼️ **Gambar:** Tidak ada file gambar tersedia — tampilkan tabel di atas sebagai isi slide utama

📝 **Catatan Pembicara:** Tekankan bahwa ini evaluasi pada 2 kondisi ekstrem, bukan sampel acak representatif. APE Truk 100% adalah artefak matematis (aktual=1 unit), bukan kegagalan sistemik.

---

## SLIDE 6 — Labeling & Preprocessing

**Judul Slide:**
> LABELING DATA & PREPROCESSING

**Isi (2 kolom):**

*Kiri — Labeling (Nq1):*
- Metode: Hitung frekuensi *cycle failure* per interval 10 menit
- Acuan: PKJI 2023 + HCM (*cycle failure* = Nq1)
- Validasi: Pak Tommi Firman (DISHUB Surabaya, 9 Juni 2026)
- Hasil label:
  - Skenario 1: Rendah 463 | Sedang 205 | Tinggi 209
  - Skenario 2: Rendah 305 | Sedang 363 | Tinggi 209

*Kanan — Preprocessing:*
- Missing values: tidak ditemukan
- Outliers: dibiarkan (arahan dosen pembimbing)
- Encoding: One-Hot Encoding untuk kolom `Hari`
- Normalisasi: StandardScaler (hanya untuk SVM)
- Total fitur: **14 kolom** (2 numerik + 7 OHE hari + 5 volume)

🖼️ **Gambar:** Tidak ada file tersedia — gunakan diagram sederhana alur Nq1 atau tabel distribusi kelas

📝 **Catatan Pembicara:** Jelaskan perbedaan Skenario 1 vs 2: pada Skenario 2, nilai Nq1=0 dengan catatan "ramai lancar" diubah labelnya ke Sedang (bukan Rendah), menghasilkan distribusi kelas yang lebih seimbang.

---

## SLIDE 7 — Hyperparameter Tuning

**Judul Slide:**
> HYPERPARAMETER TUNING (GridSearchCV)

**Isi:**

*Metode:* GridSearchCV + 5-Fold Stratified Cross-Validation, scoring: F1-weighted

| Algoritma | Skenario | Best Parameters | CV F1-weighted |
|---|---|---|---|
| Random Forest | 1 | n_estimators=200, max_depth=10, min_split=2, min_leaf=1 | 0,7166 |
| Random Forest | 2 | n_estimators=200, max_depth=None, min_split=5, min_leaf=1 | 0,7118 |
| SVM | 1 | kernel=rbf, C=10, gamma=0,1 | 0,6539 |
| SVM | 2 | kernel=rbf, C=1, gamma=0,1 | 0,6591 |

*Total eksperimen:* 32 model RF + 36 model SVM = **68 kombinasi** (× 5-fold = 340 fits)

🖼️ **Gambar:** Tidak ada file tersedia — tampilkan tabel di atas sebagai konten utama

📝 **Catatan Pembicara:** Tunjukkan bahwa RF konsisten menghasilkan CV F1 lebih tinggi dari SVM di skenario yang sama. Juga jelaskan mengapa class_weight='balanced' dipakai — karena distribusi kelas tidak seimbang.

---

## SLIDE 8 — Komparasi & Pemilihan Model Terbaik

**Judul Slide:**
> KOMPARASI 4 MODEL & PEMILIHAN TERBAIK

**Isi:**

| Model | Accuracy | F1-weighted | F1-macro |
|---|---|---|---|
| **RF Skenario 1** ✅ | **73,30%** | **0,7299** | 0,6873 |
| SVM Skenario 1 | 65,34% | 0,6538 | 0,6072 |
| RF Skenario 2 | 63,64% | 0,6399 | 0,6365 |
| SVM Skenario 2 | 60,23% | 0,6056 | 0,6027 |

*Confusion Matrix RF S1 (Testing Set):*
- Rendah: 76/93 benar (81,72%)
- Sedang: 19/41 benar (46,34%) ← terlemah
- Tinggi: 34/42 benar (80,95%)

🖼️ **Gambar:** Pilih salah satu dari folder output Anda:
- `04_comparison/01_grouped_bar_4model.png` (bar chart komparasi)
- `03_modelling/rf_scenario1/03_confusion_matrix.png` (confusion matrix RF S1)

📝 **Catatan Pembicara:** Tekankan RF S1 mengungguli di seluruh 5 metrik sekaligus, sehingga tidak ada trade-off dalam pemilihan. Kelas Sedang paling sulit karena merupakan kondisi transisi — recall hanya 46%.

---

## SLIDE 9 — Perancangan Sistem (Use Case)

**Judul Slide:**
> PERANCANGAN SISTEM SIKEDAT

**Isi:**

*4 Aktor (relasi generalization):*
- Masyarakat → akses publik (prediksi tanpa login)
- Staff → akses dashboard & data observasi
- Analis → Staff + klasifikasi, validasi, retrain
- Admin → Analis + kelola akun pengguna

*10 Use Case utama:*
Login | Prediksi kepadatan | Dashboard statistik | Data observasi | Upload & klasifikasi CSV | Validasi & koreksi | Simpan data | Retrain model | Log aktivitas | Kelola akun

🖼️ **Gambar:** `diagram_usecase.png` (sudah ada di project)

📝 **Catatan Pembicara:** Jelaskan relasi generalization — Admin mewarisi seluruh kemampuan Analis, Analis mewarisi Staff. Masyarakat bisa akses prediksi tanpa login.

---

## SLIDE 10 — Sistem Web SIKEDAT

**Judul Slide:**
> SISTEM WEB SIKEDAT — ARSITEKTUR & TAMPILAN

**Isi (2 kolom):**

*Kiri — Arsitektur MVC:*
- Framework: Flask (Python)
- Database: SQLite via Flask-SQLAlchemy
- Model: Random Forest (.pkl via joblib)
- Frontend: HTML5 + CSS3 + Chart.js 4.4.0
- Auth: Flask-Login + Flask-Bcrypt
- 18 route HTTP, 4 tabel database

*Kanan — Fitur Utama:*
1. Upload & klasifikasi batch CSV
2. Validasi Human-in-the-Loop
3. Dashboard analitik 8 visualisasi
4. Retrain model terotomasi
5. Prediksi publik (tanpa login)

🖼️ **Gambar:** Screenshot halaman Dashboard atau Classifier (ambil sendiri dari `http://localhost:5000`) — **[TODO: sisipkan screenshot]**

📝 **Catatan Pembicara:** Tekankan alur data: upload CSV → OHE Hari → prediksi RF → tampil + import ke antrian validasi → validator koreksi → data tervalidasi → retrain. Sebutkan bahwa retrain menggunakan fixed hyperparameter (bukan GridSearchCV ulang) agar selesai dalam hitungan detik.

---

## SLIDE 11 — Evaluasi Sistem (SUS)

**Judul Slide:**
> EVALUASI SISTEM — SYSTEM USABILITY SCALE (SUS)

**Isi:**
- Metode: Kuesioner SUS 10 pertanyaan, skala Likert 1–5
- Responden: [TODO — isi jumlah & jabatan setelah data SUS lengkap]
- Skor SUS rata-rata: **[TODO]**
- Kategori (Bangor et al., 2009): **[TODO]**

*Interpretasi SUS (Bangor et al., 2009):*
| Rentang | Kategori |
|---|---|
| ≥ 85 | Excellent |
| 73–84 | Good |
| 52–72 | OK |
| < 52 | Poor/Worst |

🖼️ **Gambar:** Tabel hasil SUS per responden — [TODO: sisipkan setelah data tersedia]

📝 **Catatan Pembicara:** [TODO: isi setelah SUS selesai]

---

## SLIDE 12 — Pembatas: BAB V Pembahasan

**Judul Slide:**
> BAB V
> PEMBAHASAN

**Isi:** *(slide transisi — minimal teks)*
- Interpretasi hasil
- Analisis temuan
- Perbandingan dengan penelitian terdahulu

🖼️ **Gambar:** Background slide gelap atau motif grafis sederhana (tidak perlu gambar khusus)

---

## SLIDE 13 — Jawaban Rumusan Masalah

**Judul Slide:**
> JAWABAN RUMUSAN MASALAH

**Isi:**

**RM 1 — Implementasi YOLOv8:**
→ Berhasil. mAP@0,5 = 93,49%. MAPE: Pagi 44,94% (Cukup), Malam 84,05% (Tidak Akurat). Degradasi malam hari terkonfirmasi.

**RM 2 — RF vs SVM:**
→ RF unggul konsisten. RF S1: Accuracy 73,30%, F1 0,7299 — terbaik di antara 4 model.

**RM 3 — Penyajian untuk DISHUB:**
→ Model RF S1 diintegrasikan ke web SIKEDAT: klasifikasi batch, dashboard 8 visualisasi, validasi human-in-the-loop, retrain terotomasi. SUS: [TODO]

📝 **Catatan Pembicara:** Ini slide paling penting di BAB 5. Jawaban harus tegas dan langsung — tidak bertele-tele. Slide ini menjawab secara eksplisit ketiga rumusan masalah yang ditetapkan di Bab 1.

---

## SLIDE 14 — Temuan Menarik: Korelasi Negatif

**Judul Slide:**
> TEMUAN MENARIK: KORELASI NEGATIF VOLUME vs KEPADATAN

**Isi:**

*Temuan:* Korelasi Pearson Motor–Kepadatan = **−0,44** (berlawanan intuisi)

*Mengapa?* → *Confounding factor* pencahayaan:
- Pagi (cahaya baik) → YOLOv8 mendeteksi banyak kendaraan → sering berlabel Rendah
- Malam (cahaya buruk) → YOLOv8 mendeteksi sedikit kendaraan → sering berlabel Tinggi

*Implikasi:* Model tidak belajar "banyak kendaraan = padat" — melainkan belajar pola temporal jam secara implisit. Ini adalah limitasi sekaligus temuan yang jujur dari penelitian ini.

🖼️ **Gambar:** `01_eda/06_heatmap_korelasi.png` dari folder output skrip Anda (jika tersedia)

📝 **Catatan Pembicara:** Ini adalah temuan yang paling menarik secara ilmiah. Jelaskan bahwa ini bukan kesalahan — justru ini bukti bahwa data mencerminkan realita: jam malam memang lebih sering padat, dan YOLOv8 memang lemah di malam hari. Kedua fakta ini berkorelasi dan menciptakan pola negatif yang sebenarnya logis.

---

## SLIDE 15 — Keunggulan RF atas SVM

**Judul Slide:**
> MENGAPA RANDOM FOREST LEBIH UNGGUL DARI SVM?

**Isi:**

| Aspek | Random Forest | SVM |
|---|---|---|
| Interaksi non-linear | Ditangani natural oleh ensemble pohon | Butuh kernel tuning yang tepat |
| Skala fitur | Scale-invariant (tidak perlu normalisasi) | Sensitif terhadap skala → perlu StandardScaler |
| Dataset kecil (<1.000) | Stabil | Lebih sensitif terhadap pilihan C & gamma |
| Interpretabilitas | Feature importance tersedia | Black box (kernel RBF) |

*Selisih F1-weighted Skenario 1:* RF (0,7299) vs SVM (0,6538) = **+7,6 poin persentase**

*Sejalan dengan:* Saputra et al. (2025): RF 96% vs SVM 64% pada klasifikasi diabetik retinopati — pola keunggulan RF konsisten lintas domain

📝 **Catatan Pembicara:** Tekankan bahwa keunggulan RF bukan kebetulan — ada alasan teknis yang dapat dijelaskan. Fitur volume kendaraan berdistribusi tidak normal dan heterogen (Motor bisa 14–866, Truk 0–20) — kondisi ini lebih cocok untuk RF yang scale-invariant.

---

## SLIDE 16 — Perbandingan Penelitian Terdahulu

**Judul Slide:**
> POSISI PENELITIAN DALAM LANSKAP RISET

**Isi:**

| Peneliti | Metode | Hasil | Konteks |
|---|---|---|---|
| Dhake et al. (2026) | YOLOv8 + RF/SVM | RF 69%, SVM 73% | Deteksi anomali jalan |
| Neamah & Karim (2024) | YOLOv8 | Deteksi 96,58% | Penghitungan kendaraan |
| Surya & Wahyuni (2025) | YOLOv8 | Recall 0,901 | CCTV Kota Malang |
| **Penelitian ini** | **YOLOv8+DeepSORT+RF** | **Accuracy 73,30%** | **Jl. Diponegoro Surabaya** |

*Kebaruan penelitian ini:*
1. Labeling berbasis Nq1/cycle failure + validasi pakar DISHUB
2. Dua skenario dataset (perbedaan perlakuan Nq1=0)
3. Komparasi head-to-head RF vs SVM dengan multi-metrik per skenario

📝 **Catatan Pembicara:** Perbedaan akurasi dengan Neamah/IRJMETS (96%+) wajar — mereka mengukur akurasi deteksi kendaraan (object detection), bukan klasifikasi kepadatan multi-kelas. Tugas yang berbeda tidak bisa dibandingkan langsung. Dhake et al. (2026) adalah pembanding paling apples-to-apples karena juga mengkombinasikan YOLOv8 + ML classifier.

---

## SLIDE 17 — Limitasi Penelitian

**Judul Slide:**
> LIMITASI PENELITIAN

**Isi:**
1. **Cakupan data:** 1 titik CCTV, 1 ruas jalan — generalisasi terbatas
2. **Deteksi malam hari:** MAPE malam 84,05% — model malam (Traffic Night) justru lebih buruk
3. **Labeling satu peneliti:** Inter-rater reliability belum diuji
4. **MAPE tidak stabil antar kategori:** Mobil 27,92% vs Truk 100% (artefak denominator kecil)
5. **Recall kelas Sedang rendah:** 46,34% — kondisi transisi sulit diklasifikasi
6. **Belum integrasikan SMP/V-C Ratio/LOS** dari MKJI 1997

📝 **Catatan Pembicara:** Sampaikan limitasi ini secara terbuka dan percaya diri — dewan penguji menghargai kejujuran akademis. Setiap limitasi sudah ada rencana pengembangannya di Bab 6.

---

## SLIDE 18 — Pembatas: BAB VI

**Judul Slide:**
> BAB VI
> KESIMPULAN DAN SARAN

**Isi:** *(slide transisi)*

🖼️ **Gambar:** Background berbeda (gelap atau motif)

---

## SLIDE 19 — Kesimpulan

**Judul Slide:**
> KESIMPULAN

**Isi:**

**1. Implementasi YOLOv8:**
Berhasil menghasilkan 877 baris data. mAP@0,5 = 93,49%. MAPE: pagi 44,94% (Cukup), malam 84,05% (Tidak Akurat), gabungan 64,50%.

**2. Perbandingan RF vs SVM:**
RF Skenario 1 terbaik → Accuracy **73,30%**, F1-score **0,7299**. RF unggul konsisten atas SVM di kedua skenario berkat kemampuan menangani interaksi non-linear dan sifat scale-invariant.

**3. Sistem SIKEDAT untuk DISHUB:**
Model RF S1 berhasil diintegrasikan ke web Flask. Fitur: klasifikasi batch, dashboard 8 visualisasi, validasi human-in-the-loop, retrain terotomasi. Skor SUS: **[TODO]** (kategori **[TODO]**).

📝 **Catatan Pembicara:** Jawab ketiga rumusan masalah secara berurutan dan tegas. Ini adalah slide penutup yang paling diingat dewan penguji.

---

## SLIDE 20 — Saran & Penutup

**Judul Slide:**
> SARAN & TERIMA KASIH

**Isi:**

*Saran Pengembangan:*
1. Teknik *image enhancement* (gamma correction / CLAHE) untuk deteksi malam
2. Integrasi SMP, V/C Ratio, LOS (MKJI 1997) untuk label lebih akurat
3. Perluasan ke beberapa ruas jalan Surabaya
4. Multi-rater labeling + Cohen's Kappa
5. Eksplorasi algoritma lain: XGBoost, LightGBM, LSTM
6. Integrasi real-time dengan feed CCTV SITS DISHUB

---

*Terima kasih atas perhatiannya.*
*Saya siap menerima pertanyaan dari Bapak/Ibu Dewan Penguji.*

🖼️ **Gambar:** Logo Universitas Airlangga atau foto Jl. Diponegoro Surabaya

---
---

# VERSI B — LENGKAP (28 Slide)
### Cocok untuk: Presentasi komprehensif ±20–25 menit
### Perbedaan dari Versi A: Setiap sub-bab besar mendapat slide sendiri, tidak ada penggabungan

---

## SLIDE 1 — Cover

*(Sama dengan Versi A Slide 1)*

---

## SLIDE 2 — Outline

**Judul Slide:**
> ALUR PRESENTASI

**Isi:**
- BAB IV Hasil: 14 tahapan (4.1–4.14)
- BAB V Pembahasan: Interpretasi, komparasi, limitasi
- BAB VI Kesimpulan & Saran

🖼️ **Gambar:** `metode_penelitian.png`

---

## SLIDE 3 — Pembatas BAB IV

**Judul Slide:**
> BAB IV
> HASIL

**Sub-judul:** 14 Tahapan Implementasi Penelitian

---

## SLIDE 4 — Pengumpulan Data

**Judul Slide:**
> 4.2 HASIL PENGUMPULAN DATA

**Isi:**
- Sumber: CCTV SITS DISHUB Surabaya (Bu Nina — narahubung)
- Lokasi: Jl. Diponegoro Musi Utara, Surabaya
- Periode: 21 hari pengamatan
- Sesi pagi: 06.00–09.00 WIB (morning peak)
- Sesi sore–malam: 15.00–20.00 WIB (evening peak)
- Video dipotong per jam → format MP4

*Hasil akhir setelah ekstraksi:*
→ **877 baris data** CSV, interval 10 menit

🖼️ **Gambar:** Tidak tersedia — gunakan ikon/ilustrasi CCTV atau peta lokasi Jl. Diponegoro

📝 **Catatan Pembicara:** Sebutkan bahwa pemilihan jam pagi dan sore-malam didasarkan pada karakteristik aktivitas perkantoran, sekolah, dan pusat perbelanjaan di sekitar Jl. Diponegoro.

---

## SLIDE 5 — Training YOLOv8: Konfigurasi

**Judul Slide:**
> 4.3.1 TRAINING MODEL YOLOv8 CUSTOM — KONFIGURASI

**Isi:**

*Masalah model COCO:*
- Bus COCO = 111 unit | Bus Vehicle Detection = 24 unit (rekaman sama)
- Misklasifikasi sistematis pada konteks lalu lintas Indonesia

*Solusi: Custom Training dengan dataset Roboflow*
- Dataset: Vehicle Detection Computer Vision Model
- 1.000 gambar, 4 kelas: Motor, Mobil, Bus, Truk

| Parameter | Nilai |
|---|---|
| Base model | YOLOv8m (`yolov8m.pt`) |
| Epoch | 50 (early stopping, berhenti di 33) |
| Batch size | 8 |
| Image size | 640×640 px |
| Device | GPU (device=0) |

🖼️ **Gambar:** `results.png` (grafik training loss & mAP)

📝 **Catatan Pembicara:** Tekankan pemilihan YOLOv8m (medium) — tidak terlalu ringan tapi tidak terlalu berat. Sebutkan juga eksperimen Traffic Night yang gagal (Truk=168) sehingga model utama tetap dipakai.

---

## SLIDE 6 — Training YOLOv8: Hasil & Perbandingan

**Judul Slide:**
> 4.3.1 HASIL MODEL YOLOv8 & PERBANDINGAN COCO vs CUSTOM

**Isi:**

*Metrik `best.pt` (Epoch 23):*

| Metrik | Nilai |
|---|---|
| Precision | 88,79% |
| Recall | 90,57% |
| mAP@0,5 | **93,49%** |
| mAP@0,5:0,95 | **84,89%** |

*Perbandingan pada rekaman yang sama (Senin, 15:10):*

| Model | Motor | Mobil | Bus | Truk |
|---|---|---|---|---|
| COCO | 291 | 186 | **111** | **27** |
| Vehicle Detection | 567 | 266 | **24** | **6** |

📝 **Catatan Pembicara:** best.pt bukan bobot epoch terakhir (epoch 33) melainkan epoch 23 — YOLOv8 menyimpan bobot terbaik secara otomatis. Epoch 33 hanya menghasilkan mAP@0,5 = 84,66% — lebih rendah dari epoch 23.

---

## SLIDE 7 — Evaluasi MAPE: Per Kondisi

**Judul Slide:**
> 4.4 EVALUASI EKSTRAKSI — MAPE PER KONDISI

**Isi:**

*Prosedur:* Hitung manual (ground truth) vs YOLO pada 2 segmen 10 menit

*Kondisi Pagi — Senin, 08:20–08:30:*

| Kategori | Manual | YOLO | APE |
|---|---|---|---|
| Motor | 935 | 624 | 33,26% |
| Mobil | 192 | 189 | 1,56% |
| Bus | 0 | 10 | N/A |
| Truk | 1 | 2 | 100% |
| **MAPE Pagi** | | | **44,94%** *(Cukup)* |

*Kondisi Malam — Sabtu, 19:20–19:30:*

| Kategori | Manual | YOLO | APE |
|---|---|---|---|
| Motor | 662 | 14 | 97,89% |
| Mobil | 234 | 107 | 54,27% |
| Bus | 0 | 1 | N/A |
| Truk | 1 | 0 | 100% |
| **MAPE Malam** | | | **84,05%** *(Tidak Akurat)* |

**MAPE Gabungan: 64,50%**

📝 **Catatan Pembicara:** Evaluasi ini sengaja pada 2 kondisi ekstrem untuk memotret rentang performa. APE Truk 100% adalah artefak matematis dari denominator kecil (aktual=1), bukan kegagalan sistemik.

---

## SLIDE 8 — Labeling Data (Nq1)

**Judul Slide:**
> 4.5 LABELING DATA BERBASIS CYCLE FAILURE (Nq1)

**Isi:**

*Pendekatan:* Hitung frekuensi penumpukan kendaraan yang tidak terurai saat hijau dalam interval 10 menit

*Acuan Teoritis (ditemukan setelah pendekatan dikembangkan):*
- PKJI 2023: Nq1 = kendaraan tersisa dari siklus sebelumnya
- Highway Capacity Manual (HCM): cycle failure

*Kriteria Labeling (Skenario 1):*
| Label | Nq1 |
|---|---|
| Rendah | 0 |
| Sedang | 1–2 |
| Tinggi | ≥ 3 |

*Validasi:* Pak Tommi Firman, DISHUB Surabaya — 9 Juni 2026

🖼️ **Gambar:** Tidak tersedia — buat diagram sederhana siklus lampu dengan ilustrasi cycle failure

📝 **Catatan Pembicara:** Ceritakan kronologinya: peneliti mengembangkan pendekatan dari observasi visual, LALU menemukan bahwa ini selaras dengan Nq1 di PKJI 2023 — bukan sebaliknya. Ini poin kebaruan yang penting.

---

## SLIDE 9 — Preprocessing & Pembagian Data

**Judul Slide:**
> 4.6–4.7 PREPROCESSING & PEMBAGIAN DATA

**Isi (2 kolom):**

*Kiri — Preprocessing:*
- Missing values: tidak ada
- Outliers: tidak ditangani (sesuai arahan dosen)
- Encoding: One-Hot Encoding (Hari → 7 kolom biner)
- Normalisasi: StandardScaler (pipeline SVM saja)
- Total fitur akhir: **14 kolom**

*Kanan — Pembagian Data (80:20):*

| Set | Skenario 1 | Skenario 2 |
|---|---|---|
| Training | 701 baris | 701 baris |
| Testing | 176 baris | 176 baris |
| **Total** | **877** | **877** |

*random_state = 42 → fair comparison antar algoritma*

📝 **Catatan Pembicara:** Jelaskan mengapa OHE manual (bukan sklearn OneHotEncoder) — untuk menghilangkan kebutuhan menyimpan objek encoder terpisah saat deployment ke web. Ini keputusan teknis yang konsisten dari modelling ke produksi.

---

## SLIDE 10 — Hyperparameter Tuning RF

**Judul Slide:**
> 4.9.1 HYPERPARAMETER TUNING — RANDOM FOREST

**Isi:**

*Grid yang diuji:*
- n_estimators: 100, 200
- max_depth: 10, None
- min_samples_split: 2, 5
- min_samples_leaf: 1, 2
- Total: **16 kombinasi × 2 skenario = 32 model**

*Best Parameters:*

| Skenario | n_est | max_depth | min_split | min_leaf | CV F1-w |
|---|---|---|---|---|---|
| S1 | 200 | 10 | 2 | 1 | **0,7166** |
| S2 | 200 | None | 5 | 1 | 0,7118 |

*Temuan:* max_depth=10 (terbatas) mendominasi peringkat atas Skenario 1 → regularisasi penting untuk dataset <1.000 baris

📝 **Catatan Pembicara:** Jelaskan mengapa Opsi B-Slim (bukan grid lengkap dari Bab 3) — efisiensi waktu komputasi tanpa kehilangan cakupan eksplorasi parameter utama.

---

## SLIDE 11 — Hyperparameter Tuning SVM

**Judul Slide:**
> 4.9.2 HYPERPARAMETER TUNING — SVM

**Isi:**

*Grid yang diuji:*
- kernel: linear, rbf, poly
- C: 0,1; 1; 10
- gamma: scale, 0,1
- Total: **18 kombinasi × 2 skenario = 36 model**

*Best Parameters:*

| Skenario | Kernel | C | Gamma | CV F1-w |
|---|---|---|---|---|
| S1 | rbf | 10 | 0,1 | 0,6539 |
| S2 | rbf | 1 | 0,1 | 0,6591 |

*Pola:* Kernel RBF dominan — data tidak linear separable. C lebih kecil di S2 karena distribusi kelas lebih seimbang

📝 **Catatan Pembicara:** SVM diintegrasikan dalam sklearn Pipeline bersama StandardScaler untuk mencegah data leakage saat cross-validation. Ini praktik yang benar secara metodologi.

---

## SLIDE 12 — Evaluasi Model: RF

**Judul Slide:**
> 4.10.1 EVALUASI RANDOM FOREST (Testing Set)

**Isi:**

*RF Skenario 1 — Confusion Matrix:*

| Aktual \ Prediksi | Rendah | Sedang | Tinggi |
|---|---|---|---|
| Rendah | **76** | 10 | 7 |
| Sedang | 12 | **19** | 10 |
| Tinggi | 2 | 6 | **34** |

*Metrik per kelas:*

| Kelas | Precision | Recall | F1 |
|---|---|---|---|
| Rendah | 0,8444 | 0,8172 | 0,8306 |
| Sedang | 0,5429 | 0,4634 | 0,5000 |
| Tinggi | 0,6667 | 0,8095 | 0,7313 |
| **Weighted avg** | **0,7318** | **0,7330** | **0,7299** |

🖼️ **Gambar:** `03_modelling/rf_scenario1/03_confusion_matrix.png`

📝 **Catatan Pembicara:** Kelas Sedang paling lemah (recall 46%) karena merupakan kondisi transisi. 12 dari 41 Sedang terprediksi Rendah, 10 terprediksi Tinggi — model kesulitan di perbatasan kelas.

---

## SLIDE 13 — Evaluasi Model: SVM

**Judul Slide:**
> 4.10.2 EVALUASI SVM (Testing Set)

**Isi:**

*SVM Skenario 1 — Best Model:*

| Kelas | Precision | Recall | F1 |
|---|---|---|---|
| Rendah | 0,8545 | 0,7634 | 0,8065 |
| Sedang | 0,4681 | 0,5366 | 0,5000 |
| Tinggi | 0,6078 | 0,7381 | 0,6667 |
| **Weighted avg** | **0,6604** | **0,6534** | **0,6538** |

*SVM Skenario 2 — Weighted avg:*
Accuracy 0,6023 | F1-weighted 0,6056

*Pola:* SVM S2 lebih seimbang antar kelas (F1-macro 0,6027 vs 0,6072 di S1) tapi kalah di metrik weighted

📝 **Catatan Pembicara:** Kernel RBF pada SVM dengan C=10 mengindikasikan model cenderung overfit pada data training. Sifat SVM yang sensitif terhadap skala terbukti dari perlunya StandardScaler untuk mendapat performa optimal.

---

## SLIDE 14 — Komparasi 4 Model & Pemilihan Terbaik

**Judul Slide:**
> 4.10.3–4.11 KOMPARASI 4 MODEL & MODEL TERPILIH

**Isi:**

| Model | Accuracy | F1-w | F1-macro |
|---|---|---|---|
| **RF S1** ✅ | **73,30%** | **0,7299** | 0,6873 |
| SVM S1 | 65,34% | 0,6538 | 0,6072 |
| RF S2 | 63,64% | 0,6399 | 0,6365 |
| SVM S2 | 60,23% | 0,6056 | 0,6027 |

*Model terpilih: RF Skenario 1*
- Unggul di seluruh 5 metrik sekaligus — tidak ada trade-off
- Hyperparameter final: n_estimators=200, max_depth=10, min_split=2, min_leaf=1, class_weight='balanced'

🖼️ **Gambar:** `04_comparison/01_grouped_bar_4model.png` (bar chart komparasi)

📝 **Catatan Pembicara:** Sebutkan bahwa model ini disimpan dalam format `.pkl` dan menjadi model yang diintegrasikan ke sistem web SIKEDAT.

---

## SLIDE 15 — Perancangan Sistem

**Judul Slide:**
> 4.12 PERANCANGAN SISTEM — USE CASE DIAGRAM

**Isi:**

*4 Aktor dengan relasi generalization:*
Masyarakat ← Staff ← Analis ← Admin

*10 Use Case:*
- Publik: Prediksi kepadatan
- Staff+: Login, Dashboard, Data observasi
- Analis+: Upload CSV, Klasifikasi, Validasi, Simpan, Retrain, Log aktivitas
- Admin eksklusif: Kelola akun pengguna

🖼️ **Gambar:** `diagram_usecase.png` (sudah ada di project)

📝 **Catatan Pembicara:** Tekankan perbedaan 4 peran. Relasi generalization berarti Admin bisa melakukan segalanya yang Analis bisa, Analis bisa melakukan segalanya yang Staff bisa.

---

## SLIDE 16 — Arsitektur Web SIKEDAT

**Judul Slide:**
> 4.13.1 ARSITEKTUR SISTEM WEB SIKEDAT (MVC)

**Isi:**

*Tumpukan Teknologi:*

| Lapisan | Teknologi |
|---|---|
| Frontend (View) | HTML5, CSS3 kustom, JavaScript, Chart.js 4.4.0 |
| Backend (Controller) | Flask 2.x, Flask-Login, Flask-Bcrypt |
| Model/Database | SQLite, Flask-SQLAlchemy, scikit-learn, joblib |

*Alur Data Klasifikasi Batch:*
Upload CSV → Validasi 8 kolom → OHE Hari → RF predict → Hasil tampil + download → Import ke antrian → Validasi human-in-the-loop → Data valid → Retrain

*18 route HTTP | 4 tabel database | 4 peran pengguna*

📝 **Catatan Pembicara:** Jelaskan mengapa Flask dipilih: (1) Python — langsung terintegrasi dengan scikit-learn tanpa perantara, (2) lightweight sesuai skala operasional DISHUB, (3) ekosistem extension Flask-Login/Bcrypt/SQLAlchemy siap pakai.

---

## SLIDE 17 — Tampilan UI SIKEDAT

**Judul Slide:**
> 4.13.2 IMPLEMENTASI ANTARMUKA PENGGUNA

**Isi:**

*5 Halaman Utama:*
1. **Login** — autentikasi 3 peran (Admin/Analis/Staff)
2. **Klasifikasi** — upload CSV, prediksi batch, download hasil
3. **Dashboard** — 8 visualisasi: heatmap, pola per jam, weekday vs weekend, rasio kendaraan berat, dll.
4. **Validasi** — antrian per batch_id, koreksi label, bulk approve
5. **Prediksi Publik** — input Hari/Jam/Menit → output kelas kepadatan (tanpa login)

*Fitur unggulan:* Dark theme profesional | Sidebar adaptif per peran | Chart.js interaktif

🖼️ **Gambar:** Screenshot halaman Dashboard atau Klasifikasi
**→ [TODO: sisipkan screenshot dari `http://localhost:5000`]**

📝 **Catatan Pembicara:** Tekankan 3 fitur kritis untuk DISHUB: (1) Human-in-the-loop validation, (2) retrain terotomasi dengan fixed hyperparameter (selesai dalam detik, bukan jam), (3) dashboard multidimensi 8 visualisasi.

---

## SLIDE 18 — Evaluasi Sistem SUS

*(Sama dengan Versi A Slide 11 — masih TODO)*

---

## SLIDE 19 — Pembatas BAB V

*(Sama dengan Versi A Slide 12)*

---

## SLIDE 20 — Jawaban Rumusan Masalah

*(Sama dengan Versi A Slide 13)*

---

## SLIDE 21 — Pembahasan MAPE

**Judul Slide:**
> 5.2 PEMBAHASAN EVALUASI MAPE

**Isi:**

*Temuan kunci:*

| Kondisi | MAPE | Kategori | Kontributor Error Terbesar |
|---|---|---|---|
| Pagi | 44,94% | Cukup | Motor: APE 33,26% (oklusi kepadatan) |
| Malam | 84,05% | Tidak Akurat | Motor: APE 97,89% (hanya 14/662 terdeteksi) |
| Gabungan | 64,50% | Tidak Akurat | — |

*Insight:*
- Mobil paling stabil (rata-rata APE 27,92%) — siluet konsisten di segala kondisi
- Motor paling rentan — kepadatan tinggi + pencahayaan rendah → deteksi gagal
- MAPE gabungan mencerminkan *worst-case*, bukan performa rata-rata

📝 **Catatan Pembicara:** Sambungkan ke slide berikutnya: mengapa Motor sering gagal di malam hari ternyata menciptakan pola korelasi negatif yang menarik di EDA.

---

## SLIDE 22 — Korelasi Negatif & Confounding Factor

*(Sama dengan Versi A Slide 14 — lebih detail)*

---

## SLIDE 23 — RF vs SVM: Analisis Keunggulan

*(Sama dengan Versi A Slide 15)*

---

## SLIDE 24 — Trade-off Skenario 1 vs Skenario 2

**Judul Slide:**
> 5.4.2 TRADE-OFF SKENARIO 1 vs SKENARIO 2

**Isi:**

| Aspek | Skenario 1 | Skenario 2 |
|---|---|---|
| F1-weighted (RF) | **0,7299** ✅ | 0,6399 |
| F1-macro (RF) | 0,6873 | **0,6365** |
| Recall kelas Sedang (RF) | 0,4634 | **0,6164** ✅ |
| Distribusi kelas | Timpang (Rendah dominan 52,79%) | Lebih seimbang |

*Implikasi praktis:*
- **S1 lebih cocok** untuk pelaporan agregat ke DISHUB (total akurasi lebih tinggi)
- **S2 lebih cocok** jika tujuan mendeteksi kondisi transisi (Sedang) secara khusus

*Pilihan final: S1* — karena F1-weighted lebih tinggi dan tidak ada ketidakseimbangan recall yang signifikan pada kelas kritis (Tinggi)

📝 **Catatan Pembicara:** Ini menunjukkan bahwa desain dataset (definisi label) punya dampak besar pada performa model — bukan hanya pilihan algoritma.

---

## SLIDE 25 — Perbandingan Penelitian Terdahulu

*(Sama dengan Versi A Slide 16 — lebih detail)*

---

## SLIDE 26 — Limitasi Penelitian

*(Sama dengan Versi A Slide 17)*

---

## SLIDE 27 — Pembatas BAB VI & Kesimpulan

**Judul Slide:**
> BAB VI
> KESIMPULAN DAN SARAN

*(Slide transisi)*

---

## SLIDE 28 — Kesimpulan + Saran + Penutup

*(Sama dengan Versi A Slide 19–20, digabung dalam 1 slide)*

**Judul Slide:**
> KESIMPULAN, SARAN & PENUTUP

**Isi Kesimpulan:**

1. YOLOv8+DeepSORT berhasil ekstraksi 877 baris data. mAP@0,5 93,49%. MAPE: Pagi 44,94%, Malam 84,05%, Gabungan 64,50%.
2. RF S1 terbaik: Accuracy 73,30%, F1-weighted 0,7299 — unggul konsisten atas SVM.
3. Sistem web SIKEDAT berhasil diintegrasikan. SUS: **[TODO]** (kategori **[TODO]**).

**Isi Saran:**
1. Image enhancement untuk deteksi malam (gamma correction/CLAHE)
2. Integrasi SMP, V/C Ratio, LOS (MKJI 1997)
3. Perluasan ke beberapa ruas jalan Surabaya
4. Multi-rater labeling + Cohen's Kappa
5. Eksplorasi XGBoost, LightGBM, LSTM
6. Integrasi real-time dengan feed CCTV SITS DISHUB

---

*Terima kasih atas perhatiannya.*
*Saya siap menerima pertanyaan dari Bapak/Ibu Dewan Penguji.*

---

---

# RINGKASAN PERBANDINGAN DUA VERSI

| Aspek | Versi A (Ringkas) | Versi B (Lengkap) |
|---|---|---|
| Jumlah slide | **20 slide** | **28 slide** |
| Estimasi durasi | ±15–20 menit | ±20–25 menit |
| Gaya | Padat, gabungkan sub-bab terkait | Setiap sub-bab penting dapat slide sendiri |
| Cocok untuk | Sidang dengan waktu ketat | Seminar kemajuan / presentasi panjang |
| Sub-bab yang digabung (A) | Pengumpulan+Ekstraksi, Preprocessing+Split, RF+SVM Tuning, Kesimpulan+Saran | Semua dipisah |

**Rekomendasi saya:** Gunakan **Versi A** untuk sidang skripsi — 20 slide cukup ideal karena dewan penguji umumnya lebih tertarik pada sesi tanya jawab daripada slide yang terlalu panjang. Versi B bisa dipakai jika ada sesi seminar hasil sebelum sidang.

---

# GAMBAR YANG PERLU DISIAPKAN

| No | Nama File | Tersedia? | Keterangan |
|---|---|---|---|
| 1 | `results.png` | ✅ Ada di project | Grafik training loss & mAP YOLOv8 |
| 2 | `diagram_usecase.png` | ✅ Ada di project | Use Case Diagram SIKEDAT |
| 3 | `metode_penelitian.png` | ✅ Ada di project | Flowchart alur penelitian |
| 4 | `03_confusion_matrix.png` (RF S1) | ⚠️ Ada di komputer Anda | Folder `03_modelling/rf_scenario1/` |
| 5 | `01_grouped_bar_4model.png` | ⚠️ Ada di komputer Anda | Folder `04_comparison/` |
| 6 | `06_heatmap_korelasi.png` | ⚠️ Ada di komputer Anda | Folder `01_eda/` |
| 7 | Screenshot web SIKEDAT | ❌ Belum ada | Ambil dari `http://localhost:5000` |
| 8 | Tabel SUS | ❌ Belum ada | Isi setelah pengujian SUS selesai |
