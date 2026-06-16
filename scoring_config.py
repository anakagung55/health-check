import pandas as pd
import os

# Pastikan path ini menunjuk ke folder 'data'
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

def clean_percentage(val):
    """Mengubah teks persentase (15%) menjadi desimal (0.15)"""
    if pd.isna(val): return 0.0
    if isinstance(val, str): return float(val.replace('%', '').replace('<', '').strip()) / 100
    return float(val)

def load_bva_logic():
    """Memuat seluruh logika Excel BVA ke dalam satu Master Dictionary Python"""
    logic = {
        "question_weights": {},
        "section_weights": {},
        "gating_rules": [],
        "band_thresholds": {}
    }
    
    # 1. Parse Question Weights
    df_qw = pd.read_csv(os.path.join(DATA_DIR, 'question_weights.csv'), skiprows=2)
    current_section = "Unknown"
    for _, row in df_qw.iterrows():
        q_id = str(row['#']).strip()
        if pd.isna(row['Question']):
            if q_id != 'nan': current_section = q_id
            continue
        if not q_id.startswith('Q'): continue
        logic["question_weights"][q_id] = {
            "section": current_section,
            "text": row['Question'],
            "weights": {
                "Grow": clean_percentage(row['Grow']),
                "Improve Profitability": clean_percentage(row['Improve Profitability']),
                "Exit / Transition": clean_percentage(row['Exit / Transition']),
                "All / Undecided": clean_percentage(row['All / Undecided'])
            }
        }

    # 2. Parse Section Weights
    df_sw = pd.read_csv(os.path.join(DATA_DIR, 'section_weights.csv'), skiprows=2)
    for _, row in df_sw.iterrows():
        sec = str(row['Section']).strip()
        if sec == 'nan': continue
        logic["section_weights"][sec] = {
            "Grow": clean_percentage(row['Grow']),
            "Improve Profitability": clean_percentage(row['Improve Profitability']),
            "Exit / Transition": clean_percentage(row['Exit / Transition']),
            "All / Undecided": clean_percentage(row['All / Undecided'])
        }

    # 3. Parse Gating Rules (Pembatas Skor)
    df_gr = pd.read_csv(os.path.join(DATA_DIR, 'gating_rules.csv'), skiprows=2)
    for _, row in df_gr.iterrows():
        if pd.isna(row['Section']): continue
        logic["gating_rules"].append({
            "section": str(row['Section']).strip(),
            "question": str(row['Question']).strip(),
            "goal_applied": str(row['Goal applied']).strip(),
            "trigger_lte": clean_percentage(row['Trigger ≤']),
            "effect": str(row['Effect']).strip()
        })

    # 4. Parse Band Thresholds (Hasil Akhir)
    df_bt = pd.read_csv(os.path.join(DATA_DIR, 'band_thresholds.csv'), skiprows=2)
    for _, row in df_bt.iterrows():
        goal = str(row['Goal']).strip()
        if goal == 'nan': continue
        logic["band_thresholds"][goal] = {
            "Premium Asset": clean_percentage(row['Premium Asset']),
            "Strong Performer": clean_percentage(row['Strong Performer']),
            "Work in Progress": clean_percentage(row['Work in Progress'])
        }

    return logic

if __name__ == "__main__":
    # Test Run
    master_logic = load_bva_logic()
    print("✅ Master Logic BVA Berhasil Dimuat!")
    print(f"Total Pertanyaan (Q): {len(master_logic['question_weights'])}")
    print(f"Total Kategori (Section): {len(master_logic['section_weights'])}")
    print(f"Total Aturan Gating: {len(master_logic['gating_rules'])}")
    print(f"Total Kriteria Band: {len(master_logic['band_thresholds'])}")