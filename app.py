import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Konfigurasi Tampilan Halaman Web
st.set_page_config(page_title="EDA Pola Pembelian", layout="wide")

st.title("📊 Dashboard EDA: Pola Pembelian Kantin Mahasiswa")
st.write("Visualisasi ini merupakan bagian Exploratory Data Analysis (EDA) dari data transaksi pembelian makanan dan minuman mahasiswa.")

# --- PROSES LOAD & CLEANING DATA ---
@st.cache_data
def load_and_clean_data():
    # 1. Load Data
    df = pd.read_csv("dataset_transaksi_mahasiswa-1.csv")
    
    # 2. Hapus Duplikat (62 baris menjadi 60)
    df = df.drop_duplicates()
    
    # 3. Cleaning teks: split berdasarkan koma, hapus spasi, buat awalan huruf kapital
    transactions = df['Item_Dibeli'].apply(lambda x: [item.strip().title() for item in str(x).split(',')])
    
    # 4. Perbaiki typo manual (Gorengn -> Gorengan)
    for i in range(len(transactions)):
        transactions.iloc[i] = ['Gorengan' if item == 'Gorengn' else item for item in transactions.iloc[i]]
    
    # 5. Transformasi ke Matrix (One-Hot Encoding)
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

# --- BAGIAN VISUALISASI EDA ---

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Bar Chart: Jumlah Transaksi per Item")
    item_counts = df_trans.sum().sort_values(ascending=False)
    
    fig1, ax1 = plt.subplots(figsize=(8, 6))
    sns.barplot(x=item_counts.values, y=item_counts.index, palette="viridis", ax=ax1)
    ax1.set_xlabel("Jumlah Transaksi")
    ax1.set_ylabel("Nama Item")
    st.pyplot(fig1)

with col2:
    st.subheader("2. Histogram: Sebaran Jumlah Item per Transaksi")
    jumlah_item_per_transaksi = transactions.apply(len).value_counts().sort_index()
    
    fig2, ax2 = plt.subplots(figsize=(8, 6))
    sns.barplot(x=jumlah_item_per_transaksi.index, y=jumlah_item_per_transaksi.values, palette="muted", ax=ax2)
    ax2.set_xlabel("Jumlah Item (dalam satu keranjang/transaksi)")
    ax2.set_ylabel("Jumlah Transaksi")
    
    # Tambahkan angka di atas bar
    for p in ax2.patches:
        ax2.annotate(f'{int(p.get_height())}', 
                     (p.get_x() + p.get_width() / 2., p.get_height()), 
                     ha='center', va='center', xytext=(0, 5), textcoords='offset points')
    st.pyplot(fig2)

st.divider()

st.subheader("3. Heatmap: Pasangan Item yang Paling Sering Muncul")
st.write("Menampilkan jumlah transaksi yang memuat dua item sekaligus (khusus 8 item teratas). Angka pada garis diagonal adalah jumlah transaksi total untuk item tersebut.")

# Ambil Top 8 sesuai slide presentasi
top_8_items = ['Es Teh Manis', 'Kopi Susu', 'Nasi Ayam Geprek', 'Boba', 
               'Gorengan', 'Roti Bakar', 'Mie Goreng', 'Batagor']
df_top8 = df_trans[top_8_items]

# Hitung perkalian matrix untuk mendapatkan nilai kemunculan bersama (co-occurrence)
co_occurrence = df_top8.T.dot(df_top8)

fig3, ax3 = plt.subplots(figsize=(10, 8))
sns.heatmap(co_occurrence, annot=True, cmap="YlGnBu", fmt='d', linewidths=.5, ax=ax3)
st.pyplot(fig3)