### Final Project Rekayasa Sistem Berbasis Pengetahuan C

### Kelompok 1:

- Achmad Fajri Sudrajab - 5025221104
- Wu Alfred Hardy - 5025221312

# 🍎 Sistem Rekomendasi Menu Makanan untuk Penderita Diabetes

Sistem pakar berbasis web untuk membantu penderita Diabetes Melitus Tipe 2 menentukan kebutuhan kalori harian dan mendapatkan rekomendasi menu makanan yang aman. Sistem ini dibangun berdasarkan standar medis resmi dari PERKENI 2024 dan ADA 2023.

## 📸 Dokumentasi

## 🌟 Fitur Unggulan

### 1. 🧮 Kalkulator Kalori Medis (Medical-Grade)

Menghitung Berat Badan Idaman (BBI) dan Total Kebutuhan Energi (TKE) secara otomatis menggunakan Rumus Broca Modifikasi.

Faktor Koreksi:

- 📉 Usia: Dikurangi 5% per dekade (jika usia > 40 tahun).

- 🏃 Aktivitas: Penambahan 10-50% sesuai intensitas (Istirahat s.d. Berat).

- ⚖️ Status Gizi: Pengurangan 20% jika pasien Obesitas (IMT > 25).

### 2. 🧠 Inference Engine Cerdas (5-Layer Rules)

Menggunakan logika bertingkat untuk memastikan keamanan rekomendasi:

- 🛡️ Aturan 0 (Safety First): Blokir mutlak makanan berbahaya (Gorengan, Minuman Manis, Lemak Jenuh) tanpa kompromi, meskipun gula darah normal.

- 🩸 Aturan 1 (Glikemik): Blokir makanan Indeks Glikemik (IG) Tinggi saat gula darah > 140 mg/dL.

- ⚠️ Aturan 2 (Komplikasi): Filter khusus untuk Hipertensi (Batas Natrium), Ginjal (Batas Protein), dan Kolesterol.

- ⚖️ Aturan 3 (Obesitas): Peringatan preventif resistensi insulin untuk pasien dengan IMT > 25 (blokir snack > 200 kkal).

- 🚨 Aturan 4 (Preventif): Peringatan dini untuk pasien dengan risiko resistensi insulin.

### 3. 🥗 Database Pangan Lokal

Mengutamakan kearifan lokal dengan data nutrisi yang valid:

- 🍚 Karbohidrat: Nasi Merah, Jagung Rebus, Singkong, Ubi.

- 🍗 Protein: Tempe Bacem, Tahu, Ikan Kembung.

- 🧋 Minuman: Deteksi gula tersembunyi pada Boba, Es Teh Manis, dan Jus Kemasan.

## 📚 Landasan Pengetahuan (Knowledge Base)

Sistem ini BUKAN sekadar mencocokkan data, melainkan menerapkan pedoman medis resmi. Berikut adalah alasan ilmiah di balik setiap fitur:

### 🩺 Mengapa Harus Input Berat & Tinggi Badan?

- Menurut PEDOMAN PERKENI 2024, langkah pertama manajemen diabetes adalah menentukan Berat Badan Idaman (BBI).

  ```
  Rumus: (Tinggi Badan - 100) - 10%.
  ```

- Alasan Medis: Kebutuhan kalori harus dihitung dari berat ideal, bukan berat aktual. Jika dihitung dari berat aktual pasien obesitas, mereka akan terus kelebihan kalori.

### ⚖️ Mengapa BMI (IMT) Sangat Penting?

- Menurut PEDOMAN PERKENI 2024:

  ```
  Obesitas (IMT > 25) adalah penyebab utama Resistensi Insulin (sel tubuh menolak insulin).
  ```

- Logika Sistem: Jika pasien terdeteksi Obesitas, sistem otomatis memotong jatah kalori 20-30% dan melarang makanan Indeks Glikemik Tinggi untuk mencegah resistensi insulin memburuk, meskipun gula darah saat ini normal.

### 🛡️ Berapa batas Indeks Glikemik makanan atau minuman yang dapat dikomsumsi oleh penderita?

- Menurut ADA Standards 2023: Indeks Glikemik (IG) Menggunakan klasifikasi IG Rendah (<55) dan Tinggi (>70) untuk menjaga stabilitas gula darah post-prandial.

### 🩸 Mengapa Batas Gula Darah 140 mg/dL?

- Berdasarkan Tabel 3 PEDOMAN PERKENI 2024, kadar gula darah puasa normal adalah < 100 mg/dL.

- Logika Sistem: Jika gula darah puasa > 140 mg/dL (Hiperglikemia), sistem memperketat aturan dengan memblokir semua sumber karbohidrat sederhana (IG Tinggi) untuk mencegah lonjakan drastis (Glucose Spike).

### 🚫 Mengapa Makanan dan Minuman tinngi gula dan lemak Dilarang Mutlak?

- Berdasarkan Asas Kehati-hatian Medis:

  ```
  Makanan dengan label "Lemak Jenuh" atau "Tinggi Gula" memiliki risiko jangka panjang yang pasti.
  ```

- Sumber ADA 2023: Sangat tegas merekomendasikan untuk membatasi lemak jenuh (saturated fat) dan lemak trans (gorengan) untuk mengurangi risiko kardiovaskular (jantung), yang merupakan pembunuh utama pasien diabetes.

- Logika Sistem (Aturan 0): Makanan ini diblokir tanpa syarat. Walaupun gula darah pasien normal hari ini, mengonsumsi Boba akan merusak kontrol gula darah di masa depan.

### 🚀 Cara Menjalankan (Local)

Ikuti langkah-langkah berikut untuk menjalankan aplikasi di komputer Anda:

### Clone Repositori:

Buka Terminal anda dan jalankan:

```bash
git clone https://github.com/Achmadfajri10/Sistem-Rekomendasi-Menu-Penderita-Diabetes.git
cd Sistem-Rekomendasi-Menu-Penderita-Diabetes
```

### Install Dependencies:

```bash
pip install -r requirements.txt
```

### Jalankan Aplikasi:

```bash
streamlit run app.py
```

(Akses di browser: http://localhost:8501)

## 📂 Struktur File Proyek

```
Sistem-Rekomendasi-Menu-Penderita-Diabetes/
├── data/ # BASIS PENGETAHUAN
│ ├── food_database.json # Database Nutrisi & IG Makanan dan Minuman
│ └── medical_rules.json # Parameter Medis (Batas Gula, Batas Obesitas)
│
├── modules/ # LOGIKA SISTEM (BACKEND)
│ ├── calorie_calculator.py # Rumus Broca & Perhitungan Kalori
│ ├── inference_engine.py # Logika IF-THEN & Filter Makanan
│ └── data_loader.py # Fungsi pembaca JSON
│
├── app.py # ANTARMUKA PENGGUNA (FRONTEND)
├── requirements.txt # Daftar Pustaka Python
└── README.md
```

## 📖 Referensi Utama

Sistem ini dikembangkan berdasarkan studi literatur dari dokumen berikut:

PERKENI (2024). Pedoman Pengelolaan dan Pencegahan Diabetes Melitus Tipe 2 di Indonesia. Jakarta: PB PERKENI.

American Diabetes Association (2023). Standards of Care in Diabetes—2023. Diabetes Care, 46(Supplement_1).

Soelistijo, S. A., et al. (2021). Pedoman Pengelolaan dan Pencegahan Diabetes Melitus Tipe 2 Dewasa di Indonesia 2021. PB PERKENI.

## 🔜 Rencana Pengembangan (Future Work)

[ ] Fitur Defisit Kalori Otomatis: Menghitung target penurunan berat badan spesifik per minggu, dikarenakan menurut pedoman PERKENI 2024 yang menjelaskan bahwa pasien yang mengalami obesitas disarankan untuk menurunkan berat badan.

[ ] Meal Planner: Menyusun menu pagi/siang/malam agar pas dengan total kalori penderita.

## 🔜 Dokumentasi

<i>Project ini disusun untuk memenuhi Tugas Akhir Mata Kuliah Rekayasa Sistem Berbasis Pengetahuan Kelas C.</i>
