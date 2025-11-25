# 📊 Dashboard Sertifikasi - Data Visualization

Dashboard interaktif untuk visualisasi dan analisis data sertifikasi menggunakan Streamlit dan Supabase.

![Python](https://img.shields.io/badge/Python-3.14-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.51-red)
![Supabase](https://img.shields.io/badge/Supabase-Cloud-green)

## 📋 Deskripsi Project

Dashboard ini dibuat untuk menganalisis data sertifikasi dengan berbagai visualisasi interaktif. Dashboard menyediakan insight mendalam tentang:
- Jumlah pendaftar sertifikasi
- Status proses sertifikasi (Selesai, On Progress, Dibatalkan)
- Perbandingan antar instansi
- Trend sertifikasi per bulan
- Completion rate per instansi

## ✨ Fitur Utama

Dashboard ini memiliki 4 tab utama dengan berbagai visualisasi:

### 📈 Tab 1: Overview
- Statistik umum (Total Pendaftar, Pengajuan Awal, On Progress, Dibatalkan, Selesai)
- Filter berdasarkan tanggal, jenis sertifikasi, dan instansi
- Bar chart pendaftar per bulan

### 🏆 Tab 2: Top 5 Institutions
- Analisis mendalam Top 5 instansi berdasarkan jumlah pendaftar
- Average completion rate
- Horizontal bar chart jumlah pendaftar
- Stacked bar chart distribusi status (Selesai, On Progress, Dibatalkan)
- Tabel detail dengan completion rate

### 📊 Tab 3: Trends & Analytics
- Multi-line chart trend sertifikasi per bulan
- Pie chart distribusi berdasarkan jenis sertifikasi
- Pie chart success rate keseluruhan
- Horizontal bar chart completion rate Top 10 instansi

### 🎯 Tab 4: Status Distribution
- Statistik detail untuk setiap status
- Grouped bar chart status per jenis sertifikasi
- Funnel chart untuk visualisasi conversion
- Tabel summary Top 15 instansi dengan completion rate

## 🛠️ Tech Stack

- **Python 3.14**: Bahasa pemrograman utama
- **Streamlit**: Framework untuk membuat web dashboard interaktif
- **Pandas**: Library untuk manipulasi dan analisis data
- **Plotly Express**: Library untuk visualisasi data interaktif
- **Supabase**: Backend database cloud PostgreSQL

## 📦 Dependencies

```txt
streamlit==1.51.0
pandas==2.3.3
plotly==6.5.0
supabase==2.24.0
pyarrow==22.0.0
```

## 🚀 Instalasi

### 1. Clone Repository

```bash
git clone <repository-url>
cd dashboard-sertifikasi
```

### 2. Install Dependencies

Pastikan Python 3.14 sudah terinstall di sistem Anda.

```bash
# Menggunakan pip
python -m pip install streamlit pandas plotly supabase

# Atau install pyarrow secara terpisah jika ada masalah
python -m pip install pyarrow --only-binary=:all:
```

### 3. Konfigurasi Supabase

1. Buat project di [Supabase](https://supabase.com/)
2. Import data CSV ke tabel bernama `DataVisualisation1`
3. Pastikan tabel memiliki kolom berikut:
   - `id` (int8, Primary Key)
   - `created_at` (timestamptz)
   - `nama_sertifikasi` (text)
   - `jenis_sertifikasi` (text)
   - `tanggal_sertifikasi` (date)
   - `instansi` (text)
   - `pendaftar` (int8)
   - `pengajuan_awal` (int8)
   - `dibatalkan` (int8)
   - `on_progress` (int8)
   - `selesai` (int8)
   - `no` (int8)

4. **Nonaktifkan RLS (Row Level Security)** untuk tabel:
   ```sql
   ALTER TABLE "DataVisualisation1" DISABLE ROW LEVEL SECURITY;
   ```

5. Dapatkan kredensial Supabase:
   - Buka **Project Settings** → **API**
   - Copy **Project URL** dan **anon (public) key**

6. Update kredensial di file `dashboard_sertifikasi.py`:
   ```python
   SUPABASE_URL = "https://your-project.supabase.co"
   SUPABASE_KEY = "your-anon-key-here"
   ```

## 🎮 Cara Menjalankan

### Metode 1: Command Line

```bash
python -m streamlit run dashboard_sertifikasi.py
```

### Metode 2: Dengan Custom Port

```bash
python -m streamlit run dashboard_sertifikasi.py --server.port 8080
```

### Metode 3: Headless Mode (untuk server)

```bash
python -m streamlit run dashboard_sertifikasi.py --server.headless=true
```

Dashboard akan otomatis terbuka di browser pada:
- **Local URL**: http://localhost:8501
- **Network URL**: http://[your-ip]:8501

## 📁 Struktur Project

```
dashboard-sertifikasi/
│
├── dashboard_sertifikasi.py    # File utama dashboard
├── test_supabase.py            # Script untuk testing koneksi Supabase
├── disable_rls.sql             # SQL untuk disable RLS
├── README.md                   # Dokumentasi project
└── requirements.txt            # (opsional) Daftar dependencies
```

## 🔧 Troubleshooting

### Error: `pip not recognized`
Gunakan:
```bash
python -m pip install <package>
```

### Error: `pyarrow build failed`
Install versi pre-built:
```bash
python -m pip install pyarrow --only-binary=:all:
```

### Error: `No data found in table`
1. Cek apakah RLS sudah dinonaktifkan
2. Pastikan nama tabel sudah benar (`DataVisualisation1`)
3. Jalankan `python test_supabase.py` untuk test koneksi

### Error: `illegal request line`
Restart dashboard dengan mematikan semua proses Python:
```bash
# Windows
python -c "import os; os.system('TASKKILL /F /IM python.exe')"

# Kemudian jalankan ulang
python -m streamlit run dashboard_sertifikasi.py
```

## 📊 Format Data

Data yang digunakan harus dalam format CSV dengan struktur kolom sebagai berikut:

| Kolom | Tipe Data | Deskripsi |
|-------|-----------|-----------|
| id | Integer | ID unik |
| nama_sertifikasi | Text | Nama program sertifikasi |
| jenis_sertifikasi | Text | Jenis/kategori sertifikasi (Online/Offline) |
| tanggal_sertifikasi | Date | Tanggal pelaksanaan |
| instansi | Text | Nama instansi penyelenggara |
| pendaftar | Integer | Jumlah pendaftar |
| pengajuan_awal | Integer | Jumlah pengajuan awal |
| dibatalkan | Integer | Jumlah yang dibatalkan |
| on_progress | Integer | Jumlah yang sedang berjalan |
| selesai | Integer | Jumlah yang selesai |

## 👥 Kontributor

- **Developer**: [Nama Anda]
- **Project Type**: Tugas Kampus - Data Visualization

## 📝 Lisensi

Project ini dibuat untuk keperluan akademik/internal.

## 🤝 Kontribusi

Jika Anda ingin berkontribusi pada project ini:

1. Fork repository
2. Buat branch baru (`git checkout -b feature/AmazingFeature`)
3. Commit perubahan (`git commit -m 'Add some AmazingFeature'`)
4. Push ke branch (`git push origin feature/AmazingFeature`)
5. Buat Pull Request

## 📞 Kontak

Untuk pertanyaan atau diskusi lebih lanjut, silakan hubungi:
- Email: [email-anda@example.com]
- GitHub: [@username-anda]

---

**Last Updated**: November 2025

**Status**: ✅ Production Ready
