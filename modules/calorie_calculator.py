class DiabetesCalorieCalculator:
    def __init__(self):
        # Konstanta Kalori Basal per kg BBI (Standar PERKENI)
        self.KALORI_PRIA = 30
        self.KALORI_WANITA = 25

    def hitung_bbi(self, tinggi_badan_cm, jenis_kelamin):
        """
        Menghitung Berat Badan Idaman (BBI) dengan Rumus Broca (Modifikasi).
        Rumus: (TB - 100) - 10% * (TB - 100)
        Note: Untuk pria < 160cm dan wanita < 150cm, tidak dikurangi 10%.
        """
        berat_ideal_kotor = tinggi_badan_cm - 100
        
        # Cek batas tinggi badan untuk pengurangan 10%
        if jenis_kelamin.lower() == 'pria':
            if tinggi_badan_cm < 160:
                return berat_ideal_kotor
        elif jenis_kelamin.lower() == 'wanita':
            if tinggi_badan_cm < 150:
                return berat_ideal_kotor
        
        # Rumus standar
        bbi = berat_ideal_kotor - (0.10 * berat_ideal_kotor)
        return bbi

    def hitung_kebutuhan_kalori(self, profil_pasien):
        """
        Menghitung Total Kebutuhan Energi (TKE) harian.
        Faktor: Usia, Aktivitas, Berat Badan saat ini (Status Gizi).
        """
        tb = profil_pasien['tinggi_badan']
        jk = profil_pasien['jenis_kelamin']
        usia = profil_pasien['usia']
        aktivitas = profil_pasien['aktivitas'] # Ringan/Sedang/Berat
        bb_aktual = profil_pasien['berat_badan']

        # 1. Hitung BBI (Berat Badan Idaman)
        bbi = self.hitung_bbi(tb, jk)

        # 2. Hitung Kalori Basal (KKB)
        # Pria: 30 kkal/kg BBI, Wanita: 25 kkal/kg BBI
        faktor_basal = self.KALORI_PRIA if jk.lower() == 'pria' else self.KALORI_WANITA
        kalori_basal = bbi * faktor_basal

        # 3. Koreksi USIA
        # >40 tahun: kurangi 5% per dekade, kita simplifikasi -5% jika >40, -10% jika >60
        koreksi_usia = 0
        if usia > 60:
            koreksi_usia = -0.10 * kalori_basal
        elif usia > 40:
            koreksi_usia = -0.05 * kalori_basal

        # 4. Koreksi AKTIVITAS FISIK
        # Ringan +10-20%, Sedang +30%, Berat +50%
        faktor_aktivitas = 0
        if aktivitas.lower() == 'istirahat': # Bedrest
            faktor_aktivitas = 0.10 * kalori_basal
        elif aktivitas.lower() == 'ringan': # Pegawai kantor, IRT
            faktor_aktivitas = 0.20 * kalori_basal
        elif aktivitas.lower() == 'sedang': # Mahasiswa, jalan cepat
            faktor_aktivitas = 0.30 * kalori_basal
        elif aktivitas.lower() == 'berat': # Buruh, atlet
            faktor_aktivitas = 0.50 * kalori_basal

        # 5. Koreksi BERAT BADAN (Status Gizi)
        # Gemuk: kurangi 20-30%, Kurus: tambah 20-30%
        # Kita gunakan IMT untuk menentukan ini secara otomatis
        imt = bb_aktual / ((tb/100) ** 2)
        koreksi_berat = 0
        
        if imt > 25: # Overweight/Obesitas -> Defisit Kalori
            koreksi_berat = -0.20 * kalori_basal
            status_gizi = "Gemuk (Perlu Diet)"
        elif imt < 18.5: # Kurus -> Surplus Kalori
            koreksi_berat = 0.20 * kalori_basal
            status_gizi = "Kurus (Perlu Tambah BB)"
        else:
            status_gizi = "Normal"

        # === TOTAL KALORI ===
        total_kalori = kalori_basal + koreksi_usia + faktor_aktivitas + koreksi_berat

        return {
            "bbi": round(bbi, 1),
            "imt": round(imt, 1),
            "status_gizi": status_gizi,
            "kalori_basal": round(kalori_basal),
            "total_kalori": round(total_kalori)
        }

