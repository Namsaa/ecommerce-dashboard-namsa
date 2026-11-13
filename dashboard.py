import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="E-Commerce Dashboard", layout="wide")
sns.set(style='dark')

def create_rfm_df(df):
    recent_date = df["order_purchase_timestamp"].max() + pd.Timedelta(days=1)
    rfm_df = df.groupby("customer_unique_id", as_index=False).agg({
        "order_purchase_timestamp": lambda x: (recent_date - x.max()).days,
        "order_id": "nunique",
        "payment_value": "sum"
    })
    rfm_df.columns = ["customer_unique_id", "recency", "frequency", "monetary"]
    rfm_df['short_id'] = rfm_df['customer_unique_id'].str[:8]
    return rfm_df

def create_state_revenue_df(df):
    state_revenue_df = df.groupby(by="customer_state").agg({
        "payment_value": "sum"
    }).sort_values(by="payment_value", ascending=False).reset_index()
    return state_revenue_df

def create_delivery_status_df(df):
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    df["order_delivered_customer_date"] = pd.to_datetime(df["order_delivered_customer_date"])
    df["order_estimated_delivery_date"] = pd.to_datetime(df["order_estimated_delivery_date"])
    
    delivery_df = df.dropna(subset=["order_delivered_customer_date", "order_estimated_delivery_date"]).copy()
    
    delivery_df["delivery_status"] = delivery_df.apply(
        lambda row: "Lebih Cepat" if row["order_delivered_customer_date"] < row["order_estimated_delivery_date"] 
        else ("Terlambat" if row["order_delivered_customer_date"] > row["order_estimated_delivery_date"] else "Tepat Waktu"),
        axis=1
    )
    
    delivery_stats = delivery_df["delivery_status"].value_counts().reset_index()
    delivery_stats.columns = ["Status Pengiriman", "Jumlah Pesanan"]
    return delivery_stats

all_df = pd.read_csv("main_data.csv")
all_df["order_purchase_timestamp"] = pd.to_datetime(all_df["order_purchase_timestamp"])

min_date = all_df["order_purchase_timestamp"].min()
max_date = all_df["order_purchase_timestamp"].max()

with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png") 
    st.title("E-Commerce Dashboard")
    
    st.subheader("Filter Data")
    start_date, end_date = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    
    state_list = all_df['customer_state'].unique().tolist()
    selected_states = st.multiselect(
        label="Pilih State Pelanggan",
        options=state_list,
        default=state_list
    )

main_df = all_df[
    (all_df["order_purchase_timestamp"] >= str(start_date)) & 
    (all_df["order_purchase_timestamp"] <= str(end_date)) &
    (all_df["customer_state"].isin(selected_states))
]

rfm_df = create_rfm_df(main_df)
state_revenue_df = create_state_revenue_df(main_df)
delivery_stats_df = create_delivery_status_df(main_df)

st.title('Dashboard E-Commerce (Analisis Performa Pelanggan, Geoanalisis Wilayah, dan Performa Pengiriman)')
st.write("---")

col1, col2, col3 = st.columns(3)
with col1:
    total_orders = main_df['order_id'].nunique()
    st.metric("Total Pesanan", value=f"{total_orders:,}")
with col2:
    total_revenue = main_df['payment_value'].sum()
    st.metric("Total Pendapatan (BRL)", value=f"{total_revenue:,.2f}")
with col3:
    total_customers = main_df['customer_unique_id'].nunique()
    st.metric("Total Pelanggan", value=f"{total_customers:,}")

st.write("---")

tab1, tab2, tab3 = st.tabs(["🎯 Performa Pelanggan (RFM)", "🗺️ Geoanalisis Wilayah", "📦 Performa Pengiriman"])

with tab1:
    st.subheader("Best Customers Based on RFM Parameters")
    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 10))
    colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

    if not rfm_df.empty:
        sns.barplot(y="recency", x="short_id", data=rfm_df.sort_values(by="recency", ascending=True).head(5), palette=colors, ax=ax[0])
        ax[0].set_ylabel(None)
        ax[0].set_xlabel("Customer ID", fontsize=20)
        ax[0].set_title("By Recency (days)", loc="center", fontsize=30)
        ax[0].tick_params(axis='x', labelsize=15, rotation=45)
        ax[0].tick_params(axis='y', labelsize=15)

        sns.barplot(y="frequency", x="short_id", data=rfm_df.sort_values(by="frequency", ascending=False).head(5), palette=colors, ax=ax[1])
        ax[1].set_ylabel(None)
        ax[1].set_xlabel("Customer ID", fontsize=20)
        ax[1].set_title("By Frequency", loc="center", fontsize=30)
        ax[1].tick_params(axis='x', labelsize=15, rotation=45)
        ax[1].tick_params(axis='y', labelsize=15)

        sns.barplot(y="monetary", x="short_id", data=rfm_df.sort_values(by="monetary", ascending=False).head(5), palette=colors, ax=ax[2])
        ax[2].set_ylabel(None)
        ax[2].set_xlabel("Customer ID", fontsize=20)
        ax[2].set_title("By Monetary", loc="center", fontsize=30)
        ax[2].tick_params(axis='x', labelsize=15, rotation=45)
        ax[2].tick_params(axis='y', labelsize=15)

        st.pyplot(fig, use_container_width=True)
        
        with st.expander("Lihat Penjelasan & Rekomendasi Bisnis (RFM)"):
            st.write("""
            **Insight Analisis:**
            - **Recency:** Pelanggan pada grafik paling kiri adalah mereka yang transaksinya paling baru. Semakin kecil angkanya (dalam hari), semakin baik karena pelanggan masih aktif.
            - **Frequency:** Pelanggan dengan grafik tertinggi di tengah adalah pelanggan paling setia. Mayoritas pelanggan hanya bertransaksi satu kali, sehingga mereka yang bertransaksi lebih dari 5 kali merupakan aset berharga.
            - **Monetary:** Distribusi pendapatan sangat terpusat. Segelintir pelanggan VIP di puncak grafik kanan menyumbang total pengeluaran secara individu yang sangat masif dibanding rata-rata pelanggan lain.
            
            **Rekomendasi Action Item:**
            - Terapkan program loyalitas dengan memberikan penawaran eksklusif kepada kelompok *Top Customers* (Frequency dan Monetary tinggi) agar mereka tidak berpindah ke kompetitor.
            """)
    else:
        st.warning("Tidak ada data untuk kombinasi filter ini.")

with tab2:
    st.subheader("Pendapatan Tertinggi Berdasarkan State")
    num_states = st.slider("Tentukan jumlah state yang ingin ditampilkan:", min_value=3, max_value=20, value=10)
    
    if not state_revenue_df.empty:
        fig2, ax2 = plt.subplots(figsize=(15, 8))
        colors_state = ["#72BCD4"] + ["#D3D3D3"] * (num_states - 1)

        sns.barplot(
            x="payment_value", 
            y="customer_state", 
            data=state_revenue_df.head(num_states), 
            palette=colors_state, 
            ax=ax2
        )
        ax2.set_ylabel(None)
        ax2.set_xlabel("Total Revenue (BRL)")
        ax2.tick_params(axis='y', labelsize=12)
        ax2.ticklabel_format(style='plain', axis='x')
        st.pyplot(fig2, use_container_width=True)
        
        with st.expander("Lihat Penjelasan & Rekomendasi Bisnis (Geoanalisis)"):
            st.write("""
            **Insight Analisis:**
            - **Dominasi Wilayah:** Negara bagian **Sao Paulo (SP)** merupakan pasar paling krusial, menyumbang total pendapatan (*revenue*) tertinggi secara mutlak.
            - **Kesenjangan Pasar:** Meskipun Rio de Janeiro (RJ) dan Minas Gerais (MG) menempati posisi kedua dan ketiga, margin pendapatannya terlampau sangat jauh di bawah SP.
            
            **Rekomendasi Action Item:**
            - **Fokus Logistik Utama:** Optimalkan dan pertahankan efisiensi infrastruktur pengiriman di wilayah Sao Paulo (SP) sebagai basis pendapatan utama.
            - **Ekspansi Pasar:** Rancang subsidi ongkos kirim atau promo pemasaran khusus untuk menstimulasi pertumbuhan penjualan di wilayah menengah seperti RJ dan MG.
            """)
    else:
        st.warning("Tidak ada data untuk kombinasi filter ini.")

with tab3:
    st.subheader("Performa Pengiriman Pesanan (Actual vs Estimated)")
    
    if not delivery_stats_df.empty:
        # Layout 2 kolom untuk Bar Chart dan Pie Chart di Tab 3
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            st.markdown("##### Jumlah Pesanan Berdasarkan Status")
            fig3, ax3 = plt.subplots(figsize=(8, 6))
            colors_delivery = ["#72BCD4", "#D9534F", "#D3D3D3"]

            sns.barplot(
                x="Status Pengiriman",
                y="Jumlah Pesanan",
                data=delivery_stats_df,
                palette=colors_delivery,
                ax=ax3
            )
            ax3.set_ylabel("Jumlah Pesanan", fontsize=12)
            ax3.set_xlabel("Status Pengiriman", fontsize=12)
            st.pyplot(fig3, use_container_width=True)
            
        with col_c2:
            st.markdown("##### Persentase Ketepatan Waktu Pengiriman")
            fig_pie, ax_pie = plt.subplots(figsize=(8, 6))
            colors_pie = ["#72BCD4", "#FF7276", "#D3D3D3"]
            
            ax_pie.pie(
                delivery_stats_df['Jumlah Pesanan'], 
                labels=delivery_stats_df['Status Pengiriman'], 
                autopct='%1.1f%%', 
                colors=colors_pie[:len(delivery_stats_df)], 
                startangle=90
            )
            ax_pie.axis('equal')
            st.pyplot(fig_pie, use_container_width=True)
        
        with st.expander("Lihat Penjelasan & Rekomendasi Bisnis (Performa Pengiriman)"):
            st.write("""
            **Insight Analisis:**
            - **Tingkat Ketepatan Waktu Tinggi:** Sebagian besar pesanan (mendominasi lebih dari 90%) tiba dengan status **"Lebih Cepat"** dari tanggal estimasi yang dijanjikan kepada pelanggan. Ini menunjukkan bahwa sistem operasional dan logistik e-commerce berjalan dengan sangat efisien.
            - **Kasus Keterlambatan:** Meskipun demikian, masih terdapat sejumlah kecil pesanan yang berstatus **"Terlambat"**. Angka ini dapat menjadi acuan evaluasi bagi tim logistik atau pihak kurir rekanan agar tingkat kepuasan pelanggan (*Customer Satisfaction*) tetap terjaga.
            
            **Rekomendasi Action Item:**
            - **Evaluasi Ekspedisi:** Lakukan evaluasi berkala terhadap rute pengiriman dan performa ekspedisi pada wilayah yang sering mengalami keterlambatan untuk menekan angka komplain pelanggan.
            """)
    else:
        st.warning("Tidak ada data untuk kombinasi filter ini.")