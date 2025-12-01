import random

class DiabetesMealPlanner:
    def __init__(self):
        # Distribusi Kalori Harian
        # Pagi: 20%, Siang: 40%, Malam: 25%, Snack: 15%
        self.DISTRIBUSI = {
            "Pagi": 0.20,
            "Siang": 0.40,
            "Malam": 0.25,
            "Snack": 0.15
        }

    def _filter_by_category(self, food_list, category):
        """Helper untuk mengambil makanan berdasarkan kategori"""
        return [f for f in food_list if f['kategori'] == category]

    def _calculate_portion(self, food_item, target_cal, is_veggie=False):
        """
        Menghitung gramasi makanan agar sesuai target kalori.
        """
        cal_per_100g = food_item['nutrisi']['kalori']
        
        # Cegah error jika data kalori 0 atau negatif (misal air putih)
        if cal_per_100g <= 0:
            return {
                "nama": food_item['nama'],
                "berat": "Sesuai selera",
                "kalori": 0,
                "original": food_item
            }

        if is_veggie:
            # PENGECUALIAN SAYUR:
            # Sayur sangat rendah kalori. Jangan dipaksa mengejar target kalori 
            # (nanti porsinya jadi tidak masuk akal seperti 1 kg). Kita set porsi standar sehat saja.
            grams = 100 
        else:
            # Rumus: (Target Kalori / Kalori per 100g) * 100
            grams = (target_cal / cal_per_100g) * 100
            
            # Rounding ke kelipatan 10 terdekat agar rapi (misal 134g -> 130g)
            grams = round(grams / 10) * 10

            # CONSTRAINT REALISTIS (Agar porsi masuk akal manusiawi)
            # Min: 50g (biar gak terlalu sedikit), Max: 300g (biar gak terlalu banyak dalam satu piring)
            grams = max(50, min(grams, 300))

        # Hitung kalori final berdasarkan gram yang sudah dibulatkan
        final_cal = (grams / 100) * cal_per_100g

        return {
            "nama": food_item['nama'],
            "berat": grams, # Integer gram
            "kalori": int(final_cal),
            "original": food_item
        }

    def generate_meal_plan(self, calorie_target, safe_foods_list):
        """
        Fungsi Utama: Membuat menu seharian berdasarkan target kalori
        dan daftar makanan yang SUDAH DIFILTER (Aman).
        """
        menu_plan = {
            "Pagi": [],
            "Siang": [],
            "Malam": [],
            "Snack": [],
            "Total_Kalori": 0
        }

        # Pisahkan makanan berdasarkan kategori
        carbs = self._filter_by_category(safe_foods_list, "Karbohidrat")
        proteins = self._filter_by_category(safe_foods_list, "Protein")
        veggies = self._filter_by_category(safe_foods_list, "Sayuran")
        snacks = self._filter_by_category(safe_foods_list, "Snack") + \
                 self._filter_by_category(safe_foods_list, "Buah") # Buah bisa jadi snack

        # === LOOPING UNTUK MAKAN BESAR (Pagi, Siang, Malam) ===
        for waktu in ["Pagi", "Siang", "Malam"]:
            # Jika salah satu kategori kosong (misal tidak ada karbo aman), skip sesi ini
            if not (carbs and proteins and veggies): 
                continue 

            target_sesi = calorie_target * self.DISTRIBUSI[waktu]
            
            # Alokasi Proporsi Kalori dalam Piring Makan:
            # Karbo 45%, Protein 40%, Sayur 15% (Sayur kalorinya kecil jadi targetnya kecil)
            target_karbo = target_sesi * 0.45
            target_lauk = target_sesi * 0.40
            
            # Pilih Makanan Acak dari daftar aman
            carb_item = random.choice(carbs)
            prot_item = random.choice(proteins)
            veg_item = random.choice(veggies)

            # Hitung Porsi Dinamis (Gramasi)
            res_carb = self._calculate_portion(carb_item, target_karbo)
            res_prot = self._calculate_portion(prot_item, target_lauk)
            res_veg = self._calculate_portion(veg_item, 0, is_veggie=True) # Target 0 karena veggie fixed 100g

            items = [res_carb, res_prot, res_veg]
            menu_plan[waktu] = items
            
            # Akumulasi Total Kalori
            for x in items: 
                menu_plan["Total_Kalori"] += x['kalori']

        # === LOOPING SNACK ===
        # Hitung kekurangan kalori setelah makan besar disusun
        current_total = menu_plan["Total_Kalori"]
        deficit = calorie_target - current_total

        # Jika masih kurang banyak (>100 kkal), tambahkan snack untuk menutup defisit
        if deficit > 100 and snacks:
            # Cari snack yang bisa menutup defisit
            snack_target = deficit
            snack_item = random.choice(snacks)
            
            # Hitung porsi snack
            res_snack = self._calculate_portion(snack_item, snack_target)
            
            menu_plan["Snack"].append(res_snack)
            menu_plan["Total_Kalori"] += res_snack['kalori']

        return menu_plan