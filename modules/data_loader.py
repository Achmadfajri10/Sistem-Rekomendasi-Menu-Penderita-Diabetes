import json
import os

def load_json_file(filepath):
    """
    Fungsi utilitas untuk memuat file JSON dengan aman.
    Mengembalikan data Dictionary atau List.
    """
    # Cek apakah file ada
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"CRITICAL ERROR: File database tidak ditemukan di path: {filepath}")
    
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
            return data
    except json.JSONDecodeError:
        raise ValueError(f"CRITICAL ERROR: Format JSON di file {filepath} rusak/tidak valid.")
    except Exception as e:
        raise Exception(f"Terjadi kesalahan tak terduga saat memuat {filepath}: {str(e)}")

