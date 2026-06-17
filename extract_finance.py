import pandas as pd
import os

excel_path = "4. BlueRock_Healthcheck_Prototype (Converted).xlsm"
# Pastikan folder 'data' sudah ada dari sesi sebelumnya
output_path = os.path.join("data", "finance_questions.csv")

def extract_to_csv():
    try:
        # Baca sheet Inputs
        df = pd.read_excel(excel_path, sheet_name="Inputs")
        
        # Buang baris yang tidak memiliki QID atau Question (baris kosong/header ganda)
        df = df.dropna(subset=['QID', 'Question'])
        
        # Simpan menjadi CSV bersih
        df.to_csv(output_path, index=False)
        
        print(f"✅ BERHASIL! Data diekstrak ke: {output_path}")
        print(f"Total Pertanyaan yang ditemukan: {len(df)}")
    except Exception as e:
        print(f"❌ Gagal mengekstrak data: {e}")

if __name__ == "__main__":
    extract_to_csv()