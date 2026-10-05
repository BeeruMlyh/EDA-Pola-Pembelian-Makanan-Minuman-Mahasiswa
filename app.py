import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from itertools import combinations
from collections import Counter

# Konfigurasi Tampilan Halaman Web
st.set_page_config(page_title="EDA Pola Pembelian", layout="wide")

st.title("📊 Dashboard EDA: Pola Pembelian Kantin Mahasiswa")
st.write("Visualisasi interaktif ini dirancang agar mudah dibaca untuk menemukan wawasan (insight) bisnis dari data transaksi mahasiswa.")
st.divider()

# --- PROSES LOAD & CLEANING DATA ---
@st.cache_data
def load_and_clean_data():
    df = pd.read_csv("dataset_transaksi_mahasiswa-1.csv")
    df = df.drop_duplicates()
    transactions = df['Item_Dibeli'].apply(lambda x: [item.strip().title() for item in str(x).split(',')])
    
    for i in range(len(transactions)):
        transactions.iloc[i] = ['Gorengan' if item == 'Gorengn' else item for item in transactions.iloc[i]]
    
    encoded_vals = []
    all_items = sorted(list(set([item for sublist in transactions for item in sublist])))
    for trans in transactions:
        row = {item: 0 for item in all_items}
        for item in trans:
            row[item] = 1
        encoded_vals.append(row)
        
    df_trans = pd.DataFrame(encoded_vals)
    return transactions, df_trans

transactions, df_trans = load_and_clean_data()

# --- BAGIAN VISUALISASI EDA (VERSI MUDAH DIBACA) ---

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Item Apa Saja yang Paling Laris?")
    item_counts = df_trans.sum().sort_values(ascending=False)
    
    fig1, ax1 = plt.subplots(figsize=(8, 6))
    # Menggunakan warna biru gradasi agar bersih
    sns.barplot(x=item_counts.values, y=item_counts.index, palette="Blues_r", ax=ax1)
    
    # Menambahkan label angka di sebelah kanan bar
    for p in ax1.patches:
        ax1.annotate(f'{int(p.get_width())}', 
                     (p.get_width(), p.get_y() + p.get_height() / 2.), 
                     ha='left', va='center', xytext=(5, 0), textcoords='offset points', fontsize=10)
        
    ax1.set_xlabel("Jumlah Terjual (Transaksi)")
    ax1.set_ylabel("") # Label Y dihilangkan agar lebih bersih
    
    # Melebarkan batas kanan sedikit agar angka tidak terpotong
    ax1.set_xlim(0, item_counts.max() + 2) 
    st.pyplot(fig1)

with col2:
    st.subheader("2. Berapa Item yang Dibeli dalam 1 Struk?")
    jumlah_item = transactions.apply(len).value_counts().sort_index()
    
    fig2, ax2 = plt.subplots(figsize=(8, 6))
    sns.barplot(x=jumlah_item.index, y=jumlah_item.values, palette="Set2", ax=ax2)
    
    # Menambahkan label angka di atas bar
    for p in ax2.patches:
        ax2.annotate(f'{int(p.get_height())} struk', 
                     (p.get_x() + p.get_width() / 2., p.get_height()), 
                     ha='center', va='bottom', xytext=(0, 5), textcoords='offset points')
        
    ax2.set_xlabel("Jumlah Item dalam 1 Transaksi")
    ax2.set_ylabel("Jumlah Transaksi")
    
    # Melebarkan batas atas sedikit agar teks tidak terpotong
    ax2.set_ylim(0, jumlah_item.max() + 5)
    st.pyplot(fig2)

st.divider()

st.subheader("3. Top 10 Pasangan Item yang Sering Dibeli Bersamaan")
st.write("Grafik ini menyoroti menu apa saja yang paling berpotensi untuk dijadikan **Paket Bundling/Promo**.")

# Logic untuk menghitung pasangan (Kombinasi 2 item)
pairs = []
for t in transactions:
    if len(t) > 1:
        t_sorted = sorted(t) # Diurutkan agar (A,B) sama dengan (B,A)
        pairs.extend(list(combinations(t_sorted, 2)))

pair_counts = Counter(pairs)
# Ubah ke DataFrame agar mudah di-plot
pair_df = pd.DataFrame([{"Pasangan Menu": f"{p[0]} + {p[1]}", "Jumlah": c} for p, c in pair_counts.items()])
pair_df = pair_df.sort_values(by="Jumlah", ascending=False).head(10)

fig3, ax3 = plt.subplots(figsize=(10, 5))
sns.barplot(x=pair_df["Jumlah"], y=pair_df["Pasangan Menu"], palette="magma", ax=ax3)

# Menambahkan label angka di sebelah kanan bar
for p in ax3.patches:
    ax3.annotate(f'{int(p.get_width())} kali', 
                 (p.get_width(), p.get_y() + p.get_height() / 2.), 
                 ha='left', va='center', xytext=(5, 0), textcoords='offset points', fontsize=11, fontweight='bold')

ax3.set_xlabel("Jumlah Transaksi yang Memuat Pasangan Ini")
ax3.set_ylabel("")
ax3.set_xlim(0, pair_df["Jumlah"].max() + 1.5)
st.pyplot(fig3)
