# Dashboard Analisis Bike Sharing 🚲

Dashboard interaktif untuk analisis Bike Sharing Dataset (Capital Bikeshare, Washington D.C., 2011–2012) yang menjawab dua pertanyaan bisnis:
1. Pada jam berapa puncak penyewaan terjadi pada hari kerja dibandingkan akhir pekan/libur?
2. Seberapa besar pengaruh cuaca dan musim terhadap rata-rata penyewaan harian?

## Struktur Direktori

```
submission
├───dashboard
│   ├───main_data.csv
│   ├───day_data.csv
│   └───dashboard.py
├───data
│   ├───day.csv
│   └───hour.csv
├───notebook.ipynb
├───README.md
├───requirements.txt
└───url.txt
```

## Cara Menjalankan Dashboard

1. Buka terminal dan masuk ke folder proyek:
   ```
   cd submission
   ```
2. (Opsional) Buat dan aktifkan virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # macOS/Linux
   ```
3. Install library yang dibutuhkan:
   ```
   pip install -r requirements.txt
   ```
4. Jalankan dashboard:
   ```
   streamlit run dashboard/dashboard.py
   ```
5. Dashboard akan terbuka di browser pada alamat `http://localhost:8501`.
