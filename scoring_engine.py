from scoring_config import load_bva_logic

def calculate_bva_score(extracted_answers, user_goal):
    """
    Mesin kalkulator deterministik untuk BVA.
    Mengambil JSON jawaban dari Gemini, dan menghitung skor berdasarkan Excel Thomas.
    """
    logic = load_bva_logic()
    
    # Asumsi nilai standar: A=4 (Terbaik), B=3, C=2, D=1 (Terburuk)
    point_map = {"A": 4, "B": 3, "C": 2, "D": 1}
    
    # Fallback jika goal user tidak ada di database (pake All / Undecided)
    goal = user_goal if user_goal in logic["band_thresholds"] else "All / Undecided"
    
    raw_score = 0.0
    section_scores = {}
    
    # 1. Hitung Skor per Pertanyaan (Question Weights)
    for q_id, answer_letter in extracted_answers.items():
        if q_id not in logic["question_weights"]:
            continue
            
        q_data = logic["question_weights"][q_id]
        section = q_data["section"]
        
        # Ambil poin jawaban (1-4)
        points = point_map.get(answer_letter.upper(), 0)
        
        # Ambil bobot pertanyaan berdasarkan Goal
        q_weight = q_data["weights"].get(goal, 0.0)
        
        # Hitung skor terbobot untuk pertanyaan ini
        weighted_points = points * q_weight
        
        # Tambahkan ke total section
        if section not in section_scores:
            section_scores[section] = 0.0
        section_scores[section] += weighted_points

    # 2. Kalikan dengan Bobot Section (Section Weights)
    final_score = 0.0
    for section, score in section_scores.items():
        if section in logic["section_weights"]:
            sec_weight = logic["section_weights"][section].get(goal, 0.0)
            final_score += (score * sec_weight)
            
    # Catatan: Di PoC ini kita menyederhanakan perhitungan maksimal ke persentase 0-100%
    score_percentage = (final_score / 4.0) if final_score > 0 else 0.0
    
    # 3. Tentukan Band/Kategori (Thresholds)
    thresholds = logic["band_thresholds"][goal]
    band_result = "Action Required"
    color = "red"
    
    if score_percentage >= thresholds.get("Premium Asset", 0.9):
        band_result = "Premium Asset"
        color = "green"
    elif score_percentage >= thresholds.get("Strong Performer", 0.7):
        band_result = "Strong Performer"
        color = "blue"
    elif score_percentage >= thresholds.get("Work in Progress", 0.4):
        band_result = "Work in Progress"
        color = "orange"

    return {
        "score_percentage": round(score_percentage * 100, 2),
        "band": band_result,
        "color": color,
        "details": section_scores
    }