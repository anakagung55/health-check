import streamlit as st
import os
from datetime import datetime
from dotenv import load_dotenv

# Load konfigurasi environment
load_dotenv()

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title=f"{os.getenv('CLIENT_NAME', 'BlueRock')} Health Check", 
    page_icon="📊", 
    layout="centered"
)

# --- INISIALISASI SESSION STATE ---
# Untuk mengingat apakah user sudah mengisi form awal atau belum
if "assessment_started" not in st.session_state:
    st.session_state.assessment_started = False
if "user_data" not in st.session_state:
    st.session_state.user_data = {}

# --- HEADER APLIKASI ---
st.title(f"🏢 {os.getenv('CLIENT_NAME', 'BlueRock')} Diagnostic")
st.markdown("Welcome to the interactive assessment tool. Please provide your details to begin.")

# --- TAMPILAN FORM LEAD GENERATION ---
if not st.session_state.assessment_started:
    with st.form("lead_capture_form"):
        st.subheader("1. Your Details")
        
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Full Name *")
            company_name = st.text_input("Company Name *")
        with col2:
            email = st.text_input("Work Email *")
            role = st.text_input("Job Title")
        
        st.markdown("---")
        st.subheader("2. Assessment Configuration")
        
        # Pilihan Asesmen
        assessment_type = st.radio(
            "Which health check would you like to complete?",
            options=["Finance Function Health Check", "Business Value Accelerator (BVA)"]
        )
        
        # Dropdown Goal khusus untuk BVA (karena bobot skor bergantung pada ini)
        bva_goal = st.selectbox(
            "If taking BVA, what is your primary business goal?",
            options=["Grow", "Improve Profitability", "Exit / Transition", "All / Undecided"],
            help="This helps us tailor the scoring weights to your specific business trajectory."
        )
        
        submit_button = st.form_submit_button("Start Diagnostic 🚀")
        
        # Validasi Form
        if submit_button:
            if full_name and email and company_name:
                # Simpan data lead ke dalam memori aplikasi
                st.session_state.user_data = {
                    "name": full_name,
                    "email": email,
                    "company": company_name,
                    "role": role,
                    "assessment_type": assessment_type,
                    "bva_goal": bva_goal
                }
                st.session_state.assessment_started = True
                st.rerun() # Refresh halaman untuk masuk ke sesi chat
            else:
                st.error("Please fill in all mandatory fields (*) to proceed.")

# --- TAMPILAN SESI CHAT ---
else:
    import google.generativeai as genai
    import json
    from scoring_config import load_bva_logic # <-- Tambahkan ini untuk memanggil otak data kita
    
    # Load data pertanyaan
    bva_logic = load_bva_logic()
    
    # Buat daftar pertanyaan untuk dibaca Gemini
    # Mengambil 5 pertanyaan pertama dulu untuk PoC agar Gemini fokus
    question_bank = "\n".join([f"{q_id}: {data['text']}" for q_id, data in list(bva_logic['question_weights'].items())])
    
    # Konfigurasi Gemini
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    
    # System Prompt yang sudah di-upgrade dengan konteks
    # System Prompt yang sudah di-upgrade dengan konteks A/B/C/D
    system_instruction = f"""
    You are a professional Business Consultant from BlueRock.
    You are conducting a business assessment interview with the user to determine their Business Value.
    
    Here is the Question Bank you need to extract answers for:
    {question_bank}
    
    CRITICAL RULE: You MUST always respond in perfectly valid JSON format. 
    Do NOT include markdown formatting like ```json or anything else outside the JSON brackets.
    
    Your JSON must always contain exactly these 3 keys:
    {{
        "agent_reply": "Your conversational, empathetic, and professional response to the user.",
        "next_question": "The next assessment question you want to ask from the Question Bank.",
        "extracted_answers": {{"Q1": "A"}} 
    }}
    
    Instructions for 'extracted_answers':
    - The assessment uses a 4-point spectrum. You MUST map the user's answer to one of these:
      'A' = Strongest / Best practice / Highly positive
      'B' = Good / Mostly / Above average
      'C' = Fair / Somewhat / Below average
      'D' = Weakest / Poor / Negative / None
    - Only extract the answer AFTER you have asked the question.
    - If they haven't answered a specific question yet, leave it out.
    - Keep accumulating the answers as the chat progresses (e.g., if you have Q1 and Q2, output both).
    """
    
    # Inisialisasi Model Gemini
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=system_instruction,
        generation_config={"response_mime_type": "application/json"}
    )
    
    st.success(f"Welcome, {st.session_state.user_data['name']}! Let's start your {st.session_state.user_data['assessment_type']}.")
    
    with st.expander("View Your Configuration"):
        st.write(f"**Company:** {st.session_state.user_data['company']}")
        st.write(f"**Primary Goal:** {st.session_state.user_data['bva_goal']}")

    # Inisialisasi history chat
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Pesan pembuka dari sistem
        st.session_state.messages.append({
            "role": "assistant", 
            "content": "Hi there! I'm your BlueRock diagnostic assistant. I'll be asking you a few questions about your business to calculate your health score. Are you ready to begin?"
        })
        
    if "extracted_data" not in st.session_state:
        st.session_state.extracted_data = {}

    # Render history chat
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # Tampilkan live data extraction (hanya untuk debugging PoC)
    st.sidebar.markdown("### 🔍 Live Extracted Data")
    st.sidebar.json(st.session_state.extracted_data)

    # Input User
    if user_input := st.chat_input("Type your response here..."):
        # 1. Tampilkan pesan user
        st.chat_message("user").markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # 2. Siapkan history untuk Gemini (konversi ke format yang dimengerti Gemini)
        gemini_history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages]
        
        # 3. Panggil Gemini
        with st.spinner("Analyzing..."):
            try:
                chat = model.start_chat(history=gemini_history[:-1]) 
                response = chat.send_message(user_input)
                
                # --- PERBAIKAN JSON PARSER (ANTI-CRASH) ---
                raw_text = response.text.strip()
                # Bersihkan formatting markdown jika Gemini 'bandel'
                if raw_text.startswith("```json"):
                    raw_text = raw_text[7:]
                if raw_text.startswith("```"):
                    raw_text = raw_text[3:]
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]
                    
                response_data = json.loads(raw_text.strip())
                # ------------------------------------------
                
                agent_reply = response_data.get("agent_reply", "")
                next_question = response_data.get("next_question", "")
                extracted = response_data.get("extracted_answers", {})
                
                # Gabungkan reply dan pertanyaan untuk ditampilkan
                full_bot_response = f"{agent_reply}\n\n**{next_question}**"
                
                # 4. Tampilkan balasan bot
                st.chat_message("assistant").markdown(full_bot_response)
                st.session_state.messages.append({"role": "assistant", "content": full_bot_response})
                
                # 5. Update state extracted data
                if extracted:
                    st.session_state.extracted_data.update(extracted)
                st.rerun() 
                
            except Exception as e:
                # Menampilkan log error yang lebih rapi tanpa membuat aplikasi crash
                st.error(f"Failed to process AI response. Please try answering again. (Log: {e})")

    # --- TOMBOL SELESAI & KALKULASI ---
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Reset Form & Chat"):
            st.session_state.clear()
            st.rerun()
    with col2:
        if st.button("Finish & Calculate Score 📊", type="primary"):
            from scoring_engine import calculate_bva_score 
            from streamlit_gsheets import GSheetsConnection
            import pandas as pd
            from datetime import datetime
            
            if not st.session_state.extracted_data:
                st.warning("No data extracted yet. Please answer a few questions first!")
            else:
                with st.spinner("Calculating your BVA Score & Saving Data..."):
                    # 1. Panggil scoring engine
                    result = calculate_bva_score(
                        extracted_answers=st.session_state.extracted_data,
                        user_goal=st.session_state.user_data['bva_goal']
                    )
                    
                    # 2. Simpan ke Google Sheets (Pakai cara Ticketverse)
                    try:
                        conn = st.connection("gsheets", type=GSheetsConnection)
                        sheet_url = os.getenv("GSHEET_URL")
                        
                        # Siapkan data baru
                        new_data_dict = {
                            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "Name": st.session_state.user_data.get('name', ''),
                            "Email": st.session_state.user_data.get('email', ''),
                            "Company": st.session_state.user_data.get('company', ''),
                            "Role": st.session_state.user_data.get('role', ''),
                            "Assessment Type": st.session_state.user_data.get('assessment_type', ''),
                            "Goal": st.session_state.user_data.get('bva_goal', ''),
                            "Score (%)": f"{result['score_percentage']}%",
                            "Band": result['band'],
                            "Raw Answers": str(st.session_state.extracted_data)
                        }
                        
                        # Baca data lama, hindari cache (ttl=0), dan buang baris kosong
                        existing_data = conn.read(spreadsheet=sheet_url, usecols=list(range(10)), ttl=0)
                        existing_data = existing_data.dropna(how="all")
                        
                        # Gabungkan dan Update
                        new_data_df = pd.DataFrame([new_data_dict])
                        updated_data = pd.concat([existing_data, new_data_df], ignore_index=True)
                        conn.update(spreadsheet=sheet_url, data=updated_data)
                        
                    except Exception as e:
                        st.error(f"Gagal menyimpan ke database. Pastikan GSHEET_URL di .env sudah benar. Error: {e}")

                    # 3. Tampilkan Hasil Secara Visual
                    st.markdown("---")
                    st.subheader("🎯 Your Assessment Results")
                    
                    st.metric(
                        label="Overall Business Health Score", 
                        value=f"{result['score_percentage']}%"
                    )
                    
                    st.markdown(f"### Classification: :{result['color']}[**{result['band']}**]")
                    
                    with st.expander("View Technical Breakdown"):
                        st.json(result['details'])
                        st.write("Raw Extracted Answers:", st.session_state.extracted_data)