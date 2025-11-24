from modules.data_loader import load_json_file

class DiabetesInferenceEngine:
    def __init__(self, food_db_path='data/food_database.json', rules_path='data/medical_rules.json'):
        try:
            self.foods = load_json_file(food_db_path)
            self.rules = load_json_file(rules_path)
        except Exception as e:
            print(f"Error Init Engine: {e}")
            self.foods = []
            self.rules = {}

    def generate_recommendations(self, profil_pasien):
        rekomendasi = []
        dilarang = []
        
        # Ambil variabel pasien
        gula_darah = profil_pasien.get('gula_darah', 0)
        penyakit_penyerta = profil_pasien.get('penyakit_penyerta', [])
        bmi = profil_pasien.get('bmi', 0)

        # Ambil Batasan
        batas_hiperglikemia = self.rules['batas_gula_darah']['hiperglikemia_waspada']
        batas_obesitas = self.rules['batas_imt']['obesitas_batas']

        # === MULAI PROSES INFERENCE ===
        for food in self.foods:
            alasan_penolakan = []
            is_aman = True
            
            # --- ATURAN 0: FILTER ABSOLUT (TIDAK NEGOSIASI) ---
            # Makanan/Minuman dengan label berbahaya HARUS DILARANG untuk SEMUA penderita diabetes
            # Tidak peduli gula darahnya sedang normal atau tidak.
            tags_absolut_bahaya = [
                "Sangat Tinggi Gula", 
                "Minuman Manis", 
                "Tinggi Gula", 
                "Gorengan", 
                "Lemak Jenuh",
                "Hindari"
            ]
            
            for tag in tags_absolut_bahaya:
                if tag in food.get('tags', []):
                    is_aman = False
                    alasan_penolakan.append(f"PANTANGAN DIABETES: Mengandung '{tag}'. Wajib dihindari meski gula darah normal untuk mencegah lonjakan.")
            
            # Jika sudah kena filter absolut, skip aturan lain (biar efisien)
            if not is_aman:
                food_copy = food.copy()
                food_copy['alasan_medis'] = "; ".join(alasan_penolakan)
                dilarang.append(food_copy)
                continue # Lanjut ke makanan berikutnya

            # --- ATURAN 1: KONTROL GULA DARAH (KONDISIONAL) ---
            # Jika gula darah sedang tinggi, perketat lagi (misal IG Sedang pun dilarang)
            if gula_darah > batas_hiperglikemia:
                if food['metrik_diabetes']['kategori_ig'] == 'Tinggi':
                    is_aman = False
                    alasan_penolakan.append(f"Gula darah tinggi ({gula_darah} mg/dL). Hindari makanan IG Tinggi.")

            # --- ATURAN 2: KOMPLIKASI (Input User) ---
            for penyakit in penyakit_penyerta:
                # Cek batasan nutrisi spesifik
                if penyakit in self.rules['aturan_komplikasi']:
                    aturan_khusus = self.rules['aturan_komplikasi'][penyakit]
                    zat = aturan_khusus['zat_pantangan']
                    batas = aturan_khusus['batas_aman_per_menu']
                    
                    if food['nutrisi'].get(zat, 0) > batas:
                        is_aman = False
                        alasan_penolakan.append(f"Bahaya untuk {penyakit}: Mengandung {zat} tinggi.")

                # Cek kontraindikasi eksplisit di database makanan
                if penyakit in food.get('kontraindikasi', []):
                    is_aman = False
                    alasan_penolakan.append(f"Makanan ini dilarang medis untuk penderita {penyakit}.")

            # --- ATURAN 3: MANAJEMEN BERAT BADAN ---
            if bmi > batas_obesitas:
                # Filter Kalori Snack Ketat
                if food['kategori'] == 'Snack' and food['nutrisi']['kalori'] > 200:
                     is_aman = False
                     alasan_penolakan.append(f"Obesitas (IMT {round(bmi,1)}): Kalori snack terlalu tinggi.")
                
                # Filter IG untuk Obesitas
                if food['metrik_diabetes']['kategori_ig'] == 'Tinggi':
                    is_aman = False
                    alasan_penolakan.append("Pencegahan: Obesitas memicu resistensi insulin. Hindari IG Tinggi.")

            # === KEPUTUSAN AKHIR ===
            if is_aman:
                rekomendasi.append(food)
            else:
                food_copy = food.copy()
                food_copy['alasan_medis'] = "; ".join(alasan_penolakan)
                dilarang.append(food_copy)

        return rekomendasi, dilarang