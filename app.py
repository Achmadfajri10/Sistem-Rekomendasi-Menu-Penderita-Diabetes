import streamlit as st
import pandas as pd
from modules.calorie_calculator import DiabetesCalorieCalculator
from modules.inference_engine import DiabetesInferenceEngine
from modules.meal_planner import DiabetesMealPlanner

# === KONFIGURASI HALAMAN ===
st.set_page_config(
    page_title="Sistem Rekomendasi Menu Makanan untuk Penderita Diabetes",
    page_icon="🍎",
    layout="wide"
)

# === INISIALISASI MODUL ===
try:
    engine = DiabetesInferenceEngine(food_db_path='data/food_database.json', rules_path='data/medical_rules.json')
    calculator = DiabetesCalorieCalculator()
    planner = DiabetesMealPlanner()
except Exception as e:
    st.error(f"Terjadi kesalahan saat memuat modul: {e}")
    st.stop()

# === HEADER ===
st.title("🍎 Sistem Rekomendasi Menu Makanan untuk Penderita Diabetes")
st.markdown("""
Aplikasi ini membantu penderita diabetes menentukan **kebutuhan kalori harian** dan memilih **menu makanan yang aman**.
*Referensi: Pedoman PERKENI 2024 & ADA Standards of Care 2023*
""")
st.divider()

# === INPUT ===
col_input, col_result = st.columns([1, 2])

with col_input:
    st.subheader("📋 Data Pasien")
    with st.form("form_pasien"):
        nama = st.text_input("Nama Pasien", "Pasien A")
        c1, c2 = st.columns(2)
        usia = c1.number_input("Usia (tahun)", 10, 100, 45)
        jk = c2.selectbox("Jenis Kelamin", ["Pria", "Wanita"])
        c3, c4 = st.columns(2)
        tb = c3.number_input("Tinggi Badan (cm)", 100, 250, 170)
        bb = c4.number_input("Berat Badan (kg)", 30, 200, 80)
        aktivitas = st.selectbox("Tingkat Aktivitas", ["Istirahat (Bedrest)", "Ringan (Kantor/IRT)", "Sedang (Jalan Cepat)", "Berat (Buruh/Atlet)"])
        st.markdown("---")
        gula_darah = st.number_input("Gula Darah Puasa (mg/dL)", 50, 500, 200)
        penyakit = st.multiselect("Komplikasi", ["Hipertensi", "Kolesterol Tinggi", "Gangguan Ginjal", "Asam Urat"], default=["Hipertensi"])
        submit = st.form_submit_button("🔍 Analisis", type="primary")

# === HASIL ===
if submit:
    profil_input = {
        "tinggi_badan": tb, "berat_badan": bb, "jenis_kelamin": jk, "usia": usia,
        "aktivitas": aktivitas.split(" ")[0], "gula_darah": gula_darah,
        "penyakit_penyerta": penyakit, "bmi": bb / ((tb/100)**2)
    }
    
    hasil_kalori = calculator.hitung_kebutuhan_kalori(profil_input)
    rekomendasi_aman, rekomendasi_dilarang = engine.generate_recommendations(profil_input)
    
    # Simpan hasil analisis ke session state agar tidak hilang saat rerun tombol acak
    st.session_state['hasil_kalori'] = hasil_kalori
    st.session_state['rekomendasi_aman'] = rekomendasi_aman
    st.session_state['rekomendasi_dilarang'] = rekomendasi_dilarang
    st.session_state['profil_input'] = profil_input # Simpan input juga
    st.session_state['submitted'] = True

if 'submitted' in st.session_state and st.session_state['submitted']:
    # Ambil data dari session state
    hasil_kalori = st.session_state['hasil_kalori']
    rekomendasi_aman = st.session_state['rekomendasi_aman']
    rekomendasi_dilarang = st.session_state['rekomendasi_dilarang']
    
    with col_result:
        # Tampilkan Hasil Diagnosa
        st.success(f"Analisis Selesai untuk Pasien")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("IMT", f"{hasil_kalori['imt']}", hasil_kalori['status_gizi'])
        m2.metric("BBI", f"{hasil_kalori['bbi']} kg")
        m3.metric("Target Kalori", f"{hasil_kalori['total_kalori']} kkal")
        # Status Gula darah perlu logika sedikit untuk warna
        status_gula = "Tinggi" if st.session_state['profil_input']['gula_darah'] > 140 else "Normal"
        m4.metric("Status Gula Darah", f"{st.session_state['profil_input']['gula_darah']} mg/dL", status_gula, delta_color="inverse")
        
        st.info(f"💡 **Target:** {hasil_kalori['total_kalori']} kkal/hari. Porsi menu di bawah ini telah **disesuaikan otomatis** (dalam gram) untuk mencapai target tersebut.")
        st.divider()

        # === TABS NAVIGASI UTAMA ===
        tab_aman, tab_bahaya, tab_menu = st.tabs(["✅ Menu Makanan Aman", "⚠️ Pantangan", "🍽️ Menu Harian"])
        
        # --- TAB 1: Menu MAKANAN AMAN ---
        with tab_aman:
            if rekomendasi_aman:
                df_aman = pd.DataFrame(rekomendasi_aman)
                tampilan_aman = df_aman[['nama', 'kategori', 'tags']]
                tampilan_aman['IG'] = df_aman['metrik_diabetes'].apply(lambda x: x['indeks_glikemik'])
                st.dataframe(tampilan_aman, use_container_width=True)
            else:
                st.warning("Tidak ada makanan yang lolos seleksi.")

        # --- TAB 2: PANTANGAN ---
        with tab_bahaya:
            if rekomendasi_dilarang:
                st.error(f"{len(rekomendasi_dilarang)} Makanan Dilarang:")
                for item in rekomendasi_dilarang:
                    with st.expander(f"🚫 {item['nama']}"):
                        st.write(item['alasan_medis'])
            else:
                st.success("Tidak ada pantangan.")

        # --- TAB 3: MEAL PLANNER ---
        with tab_menu:
            col_btn, col_txt = st.columns([1, 4])
            with col_btn:
                st.button("🔄 Acak Ulang") 
            
            if rekomendasi_aman:
                # Ini akan dipanggil setiap kali script jalan (termasuk saat tombol ditekan)
                plan = planner.generate_meal_plan(hasil_kalori['total_kalori'], rekomendasi_aman)
                
                # Helper Display Card (Menampilkan Gram dan Kalori)
                def show_card(col, title, icon, items):
                    col.markdown(f"##### {icon} {title}")
                    if items:
                        for x in items:
                            # x['berat'] didapat dari meal_planner.py
                            if isinstance(x['berat'], int) or isinstance(x['berat'], float):
                                berat_display = f"{x['berat']} gr"
                            else:
                                berat_display = x['berat'] # Jika string "Sesuai selera"
                                
                            col.info(f"**{x['nama']}**\n\n⚖️ {berat_display} | 🔥 {x['kalori']} kkal")
                    else:
                        col.caption("-")

                # Grid Layout 4 Kolom
                c1, c2, c3, c4 = st.columns(4)
                show_card(c1, "Pagi", "🌅", plan['Pagi'])
                show_card(c2, "Siang", "☀️", plan['Siang'])
                show_card(c3, "Malam", "🌙", plan['Malam'])
                show_card(c4, "Snack", "🍿", plan['Snack'])

                # Total Real & Selisih
                selisih = plan['Total_Kalori'] - hasil_kalori['total_kalori']
                
                # Warna Indikator: Hijau jika selisih < 150 kkal, Oranye jika lebih
                warna = "green" if abs(selisih) < 150 else "orange"
                
                st.markdown(f"""
                <div style="background-color:#f0f2f6; padding:15px; border-radius:10px; text-align:center; margin-top:20px;">
                    <h3 style="color:{warna}; margin:0;">Total: {plan['Total_Kalori']} kkal</h3>
                    <p style="margin:0;">(Target: {hasil_kalori['total_kalori']} kkal | Selisih: {selisih} kkal)</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("Gagal menyusun menu.")

else:
    with col_result:
        st.info("👈 Masukkan data pasien untuk memulai.")