import pandas as pd

excel_path = "4. BlueRock_Healthcheck_Prototype (Converted).xlsm"
sheets_to_inspect = ['Inputs', 'Data', 'Setup', 'Results']

def inspect_sheets():
    print("🔍 MEMULAI INSPEKSI KEDALAMAN EXCEL...")
    
    try:
        for sheet in sheets_to_inspect:
            print(f"\n{'='*40}")
            print(f"📄 MENGINTIP SHEET: {sheet}")
            print(f"{'='*40}")
            
            # Kita baca 5 baris pertama saja untuk melihat format datanya
            df = pd.read_excel(excel_path, sheet_name=sheet, nrows=5)
            
            print("📌 Daftar Kolom:\n", df.columns.tolist())
            print("\n📌 Contoh Isi Baris Pertama:")
            if not df.empty:
                # Menampilkan baris pertama dalam bentuk dictionary agar mudah dibaca
                print(df.iloc[0].dropna().to_dict()) 
            else:
                print("[Sheet Kosong atau bukan format tabel standard]")
                
    except Exception as e:
        print(f"❌ Gagal membaca file: {e}")

if __name__ == "__main__":
    inspect_sheets()