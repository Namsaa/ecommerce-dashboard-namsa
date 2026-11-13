# Proyek Analisis Data: E-Commerce Public Dataset (Olist)

Analisis data transaksi *marketplace* Olist (Brasil), mencakup proses *data wrangling*, *EDA*, visualisasi, analisis lanjutan (RFM & Geoanalisis), serta *dashboard* Streamlit interaktif.

## Pertanyaan Bisnis

1. Bagaimana karakteristik pelanggan terbaik (Top Customers) berdasarkan parameter RFM (Recency, Frequency, Monetary)?
2. Wilayah (state) manakah yang memberikan kontribusi pendapatan (revenue) tertinggi?
3. Bagaimana tingkat efisiensi performa pengiriman pesanan kepada pelanggan (Actual vs Estimated Delivery)?

## Struktur Direktori

submission
├── dashboard
│   ├── main_data.csv
│   └── dashboard.py
├── data
│   └── *.csv (E-Commerce raw datasets)
├── notebook.ipynb
├── README.md
├── requirements.txt
└── url.txt

## Setup Environment

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

## Menjalankan Notebook

jupyter notebook notebook.ipynb

Jalankan seluruh sel (Run All) untuk memastikan seluruh analisis tereksekusi dengan baik dan menghasilkan file main_data.csv terbaru di dalam folder dashboard.

## Menjalankan Dashboard

Masuk ke dalam folder dashboard melalui terminal, lalu jalankan perintah berikut:

cd dashboard
python -m streamlit run dashboard.py

Atau jalankan langsung dari folder utama:
python -m streamlit run dashboard/dashboard.py

Dashboard akan terbuka secara otomatis di browser pada alamat http://localhost:8501.