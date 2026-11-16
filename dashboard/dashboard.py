import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

st.set_page_config(
    page_title="E-Commerce Business Analytics Dashboard",
    page_icon="🛒",
    layout="wide"
)

sns.set_theme(style="whitegrid")

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("dashboard/main_data.csv")
    except FileNotFoundError:
        df = pd.read_csv("main_data.csv")
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    return df

main_df = load_data()

# Sidebar Filter Rentang Waktu
with st.sidebar:
    st.title("🛒 E-Commerce Analytics")
    st.markdown("Filter rentang waktu transaksi untuk mengeksplorasi performa bisnis secara interaktif.")
    
    min_date = main_df["order_purchase_timestamp"].min().date()
    max_date = main_df["order_purchase_timestamp"].max().date()
    
    date_range = st.date_input(
        label="Pilih Rentang Tanggal",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    
    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

filtered_df = main_df[
    (main_df["order_purchase_timestamp"].dt.date >= start_date) &
    (main_df["order_purchase_timestamp"].dt.date <= end_date)
]

# Header Dashboard
st.title("📊 E-Commerce Public Dataset Dashboard")
st.markdown(f"**Periode Analisis:** `{start_date}` s.d. `{end_date}` | **Oleh:** Zidny Ilman Nafi")
st.divider()

# KPI Metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    total_orders = filtered_df["order_id"].nunique()
    st.metric("Total Pesanan Unik", f"{total_orders:,}")
with col2:
    total_revenue = filtered_df["price"].sum()
    st.metric("Total Revenue Produk", f"BRL {total_revenue:,.2f}")
with col3:
    unique_customers = filtered_df["customer_unique_id"].nunique()
    st.metric("Total Pelanggan Unik", f"{unique_customers:,}")
with col4:
    avg_delivery = filtered_df["delivery_days"].mean()
    st.metric("Rata-rata Waktu Kirim", f"{avg_delivery:.2f} Hari")

st.divider()

# Pertanyaan 1: Top 5 vs Bottom 5 Kategori Produk
st.subheader("🏆 Pertanyaan 1: Kategori Produk dengan Pendapatan (Revenue) Tertinggi & Terendah")
cat_df = (
    filtered_df[filtered_df["product_category_name_english"] != "unknown"]
    .groupby("product_category_name_english")
    .agg(
        total_orders=("order_id", "nunique"),
        total_items_sold=("order_id", "count"),
        total_revenue=("price", "sum")
    )
    .reset_index()
)
top5_cat = cat_df.sort_values(by="total_revenue", ascending=False).head(5)
bottom5_cat = cat_df.sort_values(by="total_revenue", ascending=True).head(5)

fig_cat, ax_cat = plt.subplots(nrows=1, ncols=2, figsize=(18, 6))
sns.barplot(
    x="total_revenue",
    y="product_category_name_english",
    hue="product_category_name_english",
    data=top5_cat,
    palette=["#0055A5", "#B0C4DE", "#B0C4DE", "#B0C4DE", "#B0C4DE"],
    legend=False,
    ax=ax_cat[0]
)
ax_cat[0].set_title("5 Kategori Produk dengan Revenue Tertinggi (BRL)", fontsize=14, fontweight="bold")
ax_cat[0].set_xlabel("Total Revenue (BRL)")
ax_cat[0].set_ylabel(None)

sns.barplot(
    x="total_revenue",
    y="product_category_name_english",
    hue="product_category_name_english",
    data=bottom5_cat,
    palette=["#D9534F", "#E6B8B7", "#E6B8B7", "#E6B8B7", "#E6B8B7"],
    legend=False,
    ax=ax_cat[1]
)
ax_cat[1].invert_xaxis()
ax_cat[1].yaxis.set_label_position("right")
ax_cat[1].yaxis.tick_right()
ax_cat[1].set_title("5 Kategori Produk dengan Revenue Terendah (BRL)", fontsize=14, fontweight="bold")
ax_cat[1].set_xlabel("Total Revenue (BRL)")
ax_cat[1].set_ylabel(None)
plt.tight_layout()
st.pyplot(fig_cat)

st.divider()

# Pertanyaan 2: Tren Bulanan & Demografi Negara Bagian
st.subheader("📈 Pertanyaan 2: Tren Pertumbuhan Pesanan Bulanan & 10 Negara Bagian Tertinggi")
monthly_df = filtered_df.groupby("order_month").agg(
    total_orders=("order_id", "nunique"),
    total_revenue=("price", "sum")
).reset_index()

state_df = (
    filtered_df.groupby("customer_state")
    .agg(total_orders=("order_id", "nunique"))
    .sort_values(by="total_orders", ascending=False)
    .head(10)
    .reset_index()
)

fig_q2, ax_q2 = plt.subplots(nrows=1, ncols=2, figsize=(18, 6))
ax_q2[0].plot(
    monthly_df["order_month"],
    monthly_df["total_orders"],
    marker="o",
    linewidth=2.5,
    color="#0055A5"
)
ax_q2[0].set_title("Tren Jumlah Pesanan Bulanan", fontsize=14, fontweight="bold")
ax_q2[0].set_xlabel("Bulan Transaksi")
ax_q2[0].set_ylabel("Jumlah Pesanan Unik")
ax_q2[0].tick_params(axis="x", rotation=45)

sns.barplot(
    x="total_orders",
    y="customer_state",
    hue="customer_state",
    data=state_df,
    palette=["#0055A5"] + ["#B0C4DE"] * (len(state_df) - 1),
    legend=False,
    ax=ax_q2[1]
)
ax_q2[1].set_title("10 Negara Bagian (State) dengan Pesanan Tertinggi", fontsize=14, fontweight="bold")
ax_q2[1].set_xlabel("Jumlah Pesanan Unik")
ax_q2[1].set_ylabel("Kode Negara Bagian (State)")
plt.tight_layout()
st.pyplot(fig_q2)

st.divider()

# Analisis Lanjutan: RFM & Manual Grouping
st.subheader("👥 Analisis Lanjutan: Segmentasi Pelanggan (RFM & Manual Grouping)")
ref_date = filtered_df["order_purchase_timestamp"].max() + pd.Timedelta(days=1)
rfm = filtered_df.groupby("customer_unique_id", as_index=False).agg(
    last_purchase=("order_purchase_timestamp", "max"),
    frequency=("order_id", "nunique"),
    monetary=("total_item_value", "sum")
)
rfm["recency"] = (ref_date - rfm["last_purchase"]).dt.days

def segment_func(row):
    if row["monetary"] >= 300 and row["recency"] <= 180:
        return "High-Value & Active"
    elif row["monetary"] >= 300 and row["recency"] > 180:
        return "High-Value At Risk"
    elif row["monetary"] >= 100:
        return "Medium-Value Customer"
    else:
        return "Low-Value / Entry Customer"

rfm["customer_segment"] = rfm.apply(segment_func, axis=1)
seg_counts = rfm["customer_segment"].value_counts().reset_index()
seg_counts.columns = ["customer_segment", "customer_count"]

fig_rfm, ax_rfm = plt.subplots(nrows=1, ncols=2, figsize=(18, 6))
sns.barplot(
    x="customer_count",
    y="customer_segment",
    hue="customer_segment",
    data=seg_counts,
    palette=["#0055A5", "#4A90E2", "#90B4DE", "#C5D8F0"][:len(seg_counts)],
    legend=False,
    ax=ax_rfm[0]
)
ax_rfm[0].set_title("Distribusi Segmen Pelanggan (Manual Grouping RFM)", fontsize=14, fontweight="bold")
ax_rfm[0].set_xlabel("Jumlah Pelanggan Unik")
ax_rfm[0].set_ylabel(None)

sns.histplot(rfm["recency"], bins=30, color="#0055A5", kde=True, ax=ax_rfm[1])
ax_rfm[1].set_title("Distribusi Recency Pelanggan (Hari Sejak Pembelian Terakhir)", fontsize=14, fontweight="bold")
ax_rfm[1].set_xlabel("Recency (Hari)")
ax_rfm[1].set_ylabel("Jumlah Pelanggan")
plt.tight_layout()
st.pyplot(fig_rfm)

st.caption("Copyright © 2026 Zidny Ilman Nafi - Proyek Akhir Belajar Analisis Data dengan Python")