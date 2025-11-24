import streamlit as st
import pandas as pd
from modules.calorie_calculator import DiabetesCalorieCalculator
from modules.inference_engine import DiabetesInferenceEngine

# === KONFIGURASI HALAMAN ===
st.set_page_config(
    page_title="Sistem Pakar Diabetes",
    page_icon="",
    layout="wide"
)

# === INISIALISASI MODUL ===
# Pastikan path database benar
try:
    engine = DiabetesInferenceEngine(food_db_path='data/food_database.json', rules_path='data/medical_rules.json')
    calculator = DiabetesCalorieCalculator()
except Exception as e:
    st.error(f"Terjadi kesalahan saat memuat modul: {e}")
    st.stop()

# === HEADER APLIKASI ===
st.title(" Sistem Rekomendasi Menu Diabetes")
st.markdown("""
Aplikasi ini membantu penderita diabetes menentukan **kebutuhan kalori harian** dan memilih **menu makanan yang aman** berdasarkan kondisi medis (Gula Darah, BMI, & Komplikasi).
*Referensi: Pedoman PERKENI 2021 & ADA Standards of Care 2023*
""")

st.divider()

# === LAYOUT DUA KOLOM (INPUT & HASIL) ===
col_input, col_result = st.columns([1, 2])

with col_input:
    st.subheader("📋 Data Pasien")
    with st.form("form_pasien"):
        nama = st.text_input("Nama Pasien", "Pasien A")
        
        c1, c2 = st.columns(2)
        usia = c1.number_input("Usia (tahun)", min_value=10, max_value=100, value=45)
        jk = c2.selectbox("Jenis Kelamin", ["Pria", "Wanita"])
        
        c3, c4 = st.columns(2)
        tb = c3.number_input("Tinggi Badan (cm)", min_value=100, max_value=250, value=170)
        bb = c4.number_input("Berat Badan (kg)", min_value=30, max_value=200, value=80)
        
        aktivitas = st.selectbox("Tingkat Aktivitas", ["Istirahat (Bedrest)", "Ringan (Kantor/IRT)", "Sedang (Jalan Cepat)", "Berat (Buruh/Atlet)"])
        
        st.markdown("---")
        st.markdown("**Kondisi Klinis Saat Ini**")
        gula_darah = st.number_input("Gula Darah Puasa (mg/dL)", min_value=50, max_value=500, value=200, help="Normal: <126 mg/dL")
        
        penyakit = st.multiselect(
            "Penyakit Penyerta (Komplikasi)",
            ["Hipertensi", "Kolesterol Tinggi", "Gangguan Ginjal", "Asam Urat"],
            default=["Hipertensi"]
        )
        
        submit = st.form_submit_button("🔍 Analisis & Cari Rekomendasi", type="primary")

# === LOGIKA SAAT TOMBOL DITEKAN ===
if submit:
    # 1. Hitung Profil & Kalori
    profil_input = {
        "tinggi_badan": tb,
        "berat_badan": bb,
        "jenis_kelamin": jk,
        "usia": usia,
        "aktivitas": aktivitas.split(" ")[0], # Ambil kata pertama saja
        "gula_darah": gula_darah,
        "penyakit_penyerta": penyakit,
        "bmi": bb / ((tb/100)**2) # Hitung kasar untuk passing ke engine
    }
    
    hasil_kalori = calculator.hitung_kebutuhan_kalori(profil_input)
    rekomendasi_aman, rekomendasi_dilarang = engine.generate_recommendations(profil_input)
    
    with col_result:
        # --- TAB 1: HASIL DIAGNOSA ---
        st.success(f"Analisis Selesai untuk: **{nama}**")
        
        # Tampilkan Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("IMT (Indeks Massa Tubuh)", f"{hasil_kalori['imt']}", hasil_kalori['status_gizi'])
        m2.metric("Berat Badan Idaman", f"{hasil_kalori['bbi']} kg")
        m3.metric("Total Kalori Harian", f"{hasil_kalori['total_kalori']} kkal")
        m4.metric("Status Gula Darah", f"{gula_darah} mg/dL", "Tinggi" if gula_darah > 140 else "Normal", delta_color="inverse")

        st.info(f"💡 **Saran Medis:** Anda membutuhkan **{hasil_kalori['total_kalori']} kkal/hari**. " 
                f"Karena status gizi **{hasil_kalori['status_gizi']}**, sistem telah menyesuaikan target kalori Anda.")

        # --- TAB 2 & 3: REKOMENDASI MAKANAN ---
        tab_aman, tab_bahaya = st.tabs(["✅ Menu Direkomendasikan", "⚠️ Menu Dilarang/Dibatasi"])
        
        with tab_aman:
            if rekomendasi_aman:
                st.markdown("Berikut adalah bahan makanan yang **aman** untuk kondisi Anda:")
                
                # Konversi ke DataFrame agar rapi
                df_aman = pd.DataFrame(rekomendasi_aman)
                
                # Pilih kolom yang relevan untuk ditampilkan
                tampilan_aman = df_aman[['nama', 'kategori', 'tags']]
                
                # Menambahkan kolom Indeks Glikemik dari nested dictionary
                tampilan_aman['Indeks Glikemik'] = df_aman['metrik_diabetes'].apply(lambda x: x['indeks_glikemik'])
                tampilan_aman['Kalori (per 100g)'] = df_aman['nutrisi'].apply(lambda x: x['kalori'])
                
                st.dataframe(
                    tampilan_aman, 
                    column_config={
                        "tags": st.column_config.ListColumn("Label"),
                        "Indeks Glikemik": st.column_config.ProgressColumn("IG", min_value=0, max_value=100, format="%d"),
                    },
                    use_container_width=True
                )
                
                # Tampilkan detail nutrisi untuk makanan pertama (contoh)
                st.caption("*Tips: Klik header kolom untuk mengurutkan (misal urutkan berdasarkan IG terendah).*")
            else:
                st.warning("Sangat ketat! Tidak ada makanan yang lolos filter kriteria medis Anda.")

        with tab_bahaya:
            if rekomendasi_dilarang:
                st.error(f"Ditemukan {len(rekomendasi_dilarang)} makanan yang **berisiko tinggi** bagi Anda:")
                
                for item in rekomendasi_dilarang:
                    with st.expander(f"🚫 {item['nama']} (Hindari!)"):
                        st.markdown(f"**Alasan Medis:** {item['alasan_medis']}")
                        st.markdown(f"**Nutrisi Berisiko:** IG = {item['metrik_diabetes']['indeks_glikemik']}, Natrium = {item['nutrisi']['natrium_mg']}mg")
            else:
                st.success("Hebat! Tidak ada pantangan spesifik untuk database makanan saat ini.")

else:
    with col_result:
        st.info("👈 Silakan isi data pasien di sebelah kiri lalu tekan tombol **Analisis**.")
        # Ilustrasi Edukasi
        st.markdown("### Mengapa Perhitungan Ini Penting?")
        st.markdown("""
        1. **Kontrol Gula Darah:** Mencegah hiperglikemia dengan membatasi karbohidrat sederhana.
        2. **Manajemen Berat Badan:** Obesitas meningkatkan resistensi insulin.
        3. **Pencegahan Komplikasi:** Hipertensi dan gangguan ginjal membutuhkan diet rendah garam/protein.
        """)