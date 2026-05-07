
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Dashboard Kependudukan Sumbar", layout="wide")

KOORDINAT_SUMBAR = {
    'Kepulauan Mentawai': [-2.2415, 99.5826], 'Pesisir Selatan': [-1.3541, 100.5694],
    'Kab.Solok': [-0.9419, 100.6710], 'Sijunjung': [-0.6934, 101.2001],
    'Tanah Datar': [-0.4705, 100.5815], 'Padang Pariaman': [-0.6276, 100.2831],
    'Agam': [-0.2762, 100.1065], 'Lima Puluh Kota': [0.1174, 100.6033],
    'Pasaman': [0.1770, 100.1654], 'Solok Selatan': [-1.1557, 101.3543],
    'Dharmasraya': [-1.0267, 101.5997], 'Pasaman Barat': [0.1607, 99.7186],
    'Padang': [-0.9492, 100.3543], 'Kota Solok': [-0.7937, 100.6625],
    'Sawahlunto': [-0.6811, 100.7766], 'Padang Panjang': [-0.4632, 100.4026],
    'Bukittinggi': [-0.3051, 100.3692], 'Payakumbuh': [-0.2263, 100.6300],
    'Pariaman': [-0.6256, 100.1187]
}

@st.cache_data
def load_data():
    file_path = 'Perkembangan Penduduk Sumatera Barat.xlsx'
    
    df = pd.read_excel(file_path, header=2) 
    
    df = df.rename(columns={df.columns[0]: 'Wilayah'})
    
    df = df.dropna(subset=['Wilayah'])
    df['Wilayah'] = df['Wilayah'].astype(str).str.strip()
    df = df[~df['Wilayah'].str.contains('Catatan', case=False, na=False)]

    tahun_kolom = [col for col in df.columns if isinstance(col, (int, float)) or str(col).isdigit()]

    for col in tahun_kolom:
        df[col] = pd.to_numeric(df[col].replace('-', np.nan), errors='coerce')

    return df, sorted(list(tahun_kolom), reverse=True)

try:
    df, list_tahun = load_data()
except Exception as e:
    st.error(f"Gagal memuat file Excel. Pastikan file 'Perkembangan Penduduk Sumatera Barat.xlsx' sudah ada. Error: {e}")
    st.stop()

st.sidebar.title("Navigasi Dashboard")
halaman = st.sidebar.radio("Pilih Halaman:", [
    "Dataset Bersih",
    "Penjelasan Dataset",
    "Peta Leaflet Interaktif",
    "Visualisasi Dinamis"
])

if halaman == "Dataset Bersih":
    st.title("Tabel Data Penduduk")
    st.write("Tabel ini menampilkan data jumlah penduduk Sumatera Barat yang telah dibersihkan.")
    st.dataframe(df, use_container_width=True)

elif halaman == "Penjelasan Dataset":
    st.title("Eksplorasi Komponen & Informasi Data")
    teks_penjelasan = """
    Dataset ini merupakan kumpulan data historis jumlah penduduk di berbagai wilayah Provinsi Sumatera Barat.
    * **Cakupan Wilayah**: 19 Kabupaten/Kota di Sumatera Barat.
    * **Rentang Waktu**: Data mencakup tahun 1971 hingga 2022.
    * **Struktur**: Mencakup era sensus lama (1971-1999) hingga data terbaru (2010-2022).
    """
    st.divider()
    if st.checkbox("Klik untuk melihat Penjelasan Dataset"):
        st.info("**Informasi Dataset Penduduk**")
        st.markdown(teks_penjelasan)
    if st.button("Saya Sudah Membaca Penjelasan"):
        st.success("Terima kasih!")
        st.balloons()

elif halaman == "Peta Leaflet Interaktif":
    st.title("Peta Sebaran Penduduk")
    tahun_pilihan = st.select_slider("Pilih Tahun:", options=sorted([int(t) for t in list_tahun]))

    m = folium.Map(location=[-0.9492, 100.3543], zoom_start=8, tiles='CartoDB positron')
    for _, row in df.iterrows():
        wilayah = row['Wilayah']
        populasi = row[tahun_pilihan]
        if wilayah in KOORDINAT_SUMBAR and pd.notna(populasi):
            folium.CircleMarker(
                location=KOORDINAT_SUMBAR[wilayah],
                radius=int(populasi) / 30000,
                popup=f"<b>{wilayah}</b><br>Tahun {tahun_pilihan}: {int(populasi):,} jiwa",
                color="#FF4B4B", fill=True, fill_opacity=0.6
            ).add_to(m)
    st_folium(m, width=900, height=500)

elif halaman == "Visualisasi Dinamis":
    st.title("Analisis Grafik Dinamis")
    col1, col2 = st.columns(2)
    with col1:
        pilih_tahun = st.selectbox("Pilih Tahun", list_tahun)
    with col2:
        pilih_wilayah = st.multiselect("Pilih Wilayah", sorted(df['Wilayah'].unique()), default=sorted(df['Wilayah'].unique())[:5])

    data_filt = df[df['Wilayah'].isin(pilih_wilayah)][['Wilayah', pilih_tahun]].dropna()

    if not data_filt.empty:
        fig1 = px.pie(data_filt, names='Wilayah', values=pilih_tahun, title=f"Distribusi Penduduk Tahun {pilih_tahun}")
        st.plotly_chart(fig1, use_container_width=True)

        fig2 = px.bar(data_filt, x='Wilayah', y=pilih_tahun, text_auto=True, title="Perbandingan Jumlah Penduduk")
        st.plotly_chart(fig2, use_container_width=True)
