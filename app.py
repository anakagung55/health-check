import streamlit as st
import os
import pandas as pd
import google.generativeai as genai
import json
import time
import threading
from datetime import datetime
from dotenv import load_dotenv

# Load konfigurasi environment
load_dotenv()

def generate_ai_report_insights(answers, score, company_name, assessment_type):
    """Melempar data ke Gemini untuk meracik isi laporan PDF kelas atas"""
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    
    system_prompt = f"""
    You are a Senior Partner at a top-tier management consulting firm (like McKinsey or BlueRock Advisory) advising a client named '{company_name}'.
    They just completed the '{assessment_type}' and achieved a score of {score}.
    
    Here is their raw assessment data (answers to diagnostic questions):
    {answers}
    
    Based on these specific answers, perform a deep diagnostic analysis and generate the report content in STRICT, valid JSON format.
    
    The JSON MUST exactly match this structure and keys:
    {{
        "executive_summary_paragraphs": [
            "Paragraph 1: Executive overview of their score, what it means, and their overall business posture.",
            "Paragraph 2: The most critical systemic risk, bottleneck, or weakness identified from their low scores.",
            "Paragraph 3: The immediate strategic mandate or primary opportunity they must act on."
        ],
        "highlights": [
            {{"title": "Name of Biggest Strength", "status": "Optimized"}},
            {{"title": "Name of Core Weakness", "status": "Critical Risk"}},
            {{"title": "Name of Key Opportunity", "status": "Growth Potential"}}
        ],
        "pillars": [
            {{
                "name": "Operational Risks & Bottlenecks",
                "description": "A dense 2-sentence professional explanation of why resolving these specific bottlenecks is critical for their business value.",
                "bottom_line": "A powerful concluding paragraph (3-4 sentences) summarizing the ultimate strategic action they must take in this area to mitigate risks.",
                "details": [
                    {{
                        "question": "Name of the specific weak area/metric based on data",
                        "observation": "What the specific data/answer tells us about their current state (2 sentences).",
                        "recommendation": "Highly actionable, tactical step to fix or improve this (2 sentences).",
                        "score_text": "Action Required",
                        "impact_level": "High",
                        "color_class": "low"
                    }},
                    {{
                        "question": "Name of another specific weak area",
                        "observation": "Observation based on data (2 sentences).",
                        "recommendation": "Tactical recommendation (2 sentences).",
                        "score_text": "Review Needed",
                        "impact_level": "Medium",
                        "color_class": "low"
                    }}
                ]
            }},
            {{
                "name": "Strategic Growth Capabilities",
                "description": "A dense 2-sentence explanation of how they can leverage their existing strengths to scale.",
                "bottom_line": "A powerful concluding paragraph (3-4 sentences) on how to capitalize on these strengths for market advantage.",
                "details": [
                    {{
                        "question": "Name of their strongest area/metric",
                        "observation": "What their high score indicates about their capability (2 sentences).",
                        "recommendation": "Strategic advice on how to scale or protect this capability (2 sentences).",
                        "score_text": "Strong",
                        "impact_level": "High",
                        "color_class": "high"
                    }}
                ]
            }}
        ]
    }}
    
    CRITICAL INSTRUCTIONS:
    1. Be highly specific to the data provided. Do not use generic filler.
    2. Use dense, authoritative, and realistic consulting language (e.g., 'capitalize on operational leverage', 'mitigate key-person dependency').
    3. "color_class" must ONLY be 'low' (for weaknesses/risks), 'med' (for average areas), or 'high' (for strengths).
    4. Return ONLY valid JSON.
    """
    
    try:
        # MAGIC TRICK: Memaksa Gemini 100% selalu mengeluarkan JSON murni tanpa markdown
        model = genai.GenerativeModel(
            model_name='gemini-2.5-flash',
            generation_config={"response_mime_type": "application/json"}
        )
        response = model.generate_content(system_prompt)
        
        raw_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(raw_text)
    except Exception as e:
        print(f"Gemini Analysis Error: {e}")
        return None

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title=f"{os.getenv('CLIENT_NAME', 'BlueRock')} Health Check", 
    page_icon="📊", 
    layout="centered"
)

# --- INISIALISASI SESSION STATE ---
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
        
        assessment_type = st.radio(
            "Which health check would you like to complete?",
            options=["Finance Function Health Check", "Business Value Accelerator (BVA)"]
        )
        
        bva_goal = st.selectbox(
            "If taking BVA, what is your primary business goal?",
            options=["Grow", "Improve Profitability", "Exit / Transition", "All / Undecided"],
            help="This helps us tailor the scoring weights to your specific business trajectory."
        )
        
        submit_button = st.form_submit_button("Start Diagnostic 🚀")
        
        if submit_button:
            if full_name and email and company_name:
                st.session_state.user_data = {
                    "name": full_name,
                    "email": email,
                    "company": company_name,
                    "role": role,
                    "assessment_type": assessment_type,
                    "bva_goal": bva_goal
                }
                st.session_state.assessment_started = True
                st.rerun() 
            else:
                st.error("Please fill in all mandatory fields (*) to proceed.")

# --- TAMPILAN SESI CHAT ATAU FORM GENERIC (A/B TESTING ROUTER) ---
else:
    st.success(f"Welcome, {st.session_state.user_data['name']}! Let's start your {st.session_state.user_data['assessment_type']}.")
    
    with st.expander("View Your Configuration"):
        st.write(f"**Company:** {st.session_state.user_data['company']}")
        if st.session_state.user_data['assessment_type'] == "Business Value Accelerator (BVA)":
            st.write(f"**Primary Goal:** {st.session_state.user_data['bva_goal']}")

    st.markdown("---")

    # ==========================================
    # ROUTE A: FINANCE FUNCTION (GENERIC FORM)
    # ==========================================
    if st.session_state.user_data['assessment_type'] == "Finance Function Health Check":
        st.markdown("### 📊 Finance Function Diagnostic")
        st.write("Please rate the following aspects of your finance function on a scale of 1 (Lowest) to 5 (Highest).")
        
        try:
            finance_df = pd.read_csv("data/finance_questions.csv")
            
            with st.form("finance_generic_form"):
                finance_answers = {}
                
                for index, row in finance_df.iterrows():
                    st.markdown(f"**{row['QID']} ({row['Quadrant']}):** {row['Question']}")
                    answer = st.radio(
                        label=f"Score for {row['QID']}",
                        options=[1, 2, 3, 4, 5],
                        horizontal=True,
                        label_visibility="collapsed",
                        key=f"fin_{row['QID']}"
                    )
                    finance_answers[row['QID']] = answer
                    st.markdown("<br>", unsafe_allow_html=True)
                
                submit_finance = st.form_submit_button("Submit Assessment 🚀", type="primary")
                
            if submit_finance:
                with st.spinner("Saving your responses to database..."):
                    from streamlit_gsheets import GSheetsConnection
                    
                    total_score = sum(finance_answers.values())
                    max_score = len(finance_df) * 5
                    score_percentage = round((total_score / max_score) * 100, 2)
                    
                    try:
                        conn = st.connection("gsheets", type=GSheetsConnection)
                        sheet_url = os.getenv("GSHEET_URL")
                        existing_data = conn.read(spreadsheet=sheet_url, usecols=list(range(10)), ttl=0).dropna(how="all")
                        
                        new_row_values = [
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            st.session_state.user_data.get('name', ''),
                            st.session_state.user_data.get('email', ''),
                            st.session_state.user_data.get('company', ''),
                            st.session_state.user_data.get('role', ''),
                            "Finance Function Health Check",
                            "N/A",
                            f"{score_percentage}%",
                            "Generic Webpage Submission",
                            str(finance_answers)
                        ]
                        
                        new_data_df = pd.DataFrame([new_row_values], columns=existing_data.columns)
                        updated_data = pd.concat([existing_data, new_data_df], ignore_index=True)
                        conn.update(spreadsheet=sheet_url, data=updated_data)
                        st.success(f"✅ Assessment submitted successfully! Your preliminary score is {score_percentage}%.")
                    except Exception as e:
                        st.error(f"Failed to save data. Error: {e}")

                # --- ROUTE A: PROGRESS BAR & AI GENERATION ---
                my_bar = st.progress(0, text="Preparing your custom Finance PDF Report... Please wait.")
                
                # Container untuk menangkap hasil dari thread
                ai_result = {"data": None, "done": False, "error": None}
                
                # EKSTRAK DATA KE VARIABEL LOKAL DULU DI SINI
                current_company = st.session_state.user_data['company']
                current_assessment = st.session_state.user_data['assessment_type']
                
                def fetch_ai_insights():
                    try:
                        ai_result["data"] = generate_ai_report_insights(
                            answers=finance_answers,
                            score=f"{score_percentage}%",
                            company_name=current_company,      # Pakai variabel lokal
                            assessment_type=current_assessment # Pakai variabel lokal
                        )
                    except Exception as e:
                        ai_result["error"] = e
                    finally:
                        ai_result["done"] = True

                # 1. Mulai proses AI di background thread
                ai_thread = threading.Thread(target=fetch_ai_insights)
                ai_thread.start()
                
                # 2. Loop untuk animasi progress bar selama thread berjalan
                progress_val = 10
                my_bar.progress(progress_val, text="Crunching financial metrics...")
                
                while not ai_result["done"]:
                    if progress_val < 85:  # Mentok di 85% sambil nunggu AI selesai
                        progress_val += 1
                        my_bar.progress(progress_val, text=f"AI Consultant is writing deep analysis pages... ({progress_val}%)")
                    time.sleep(0.3)  # Kecepatan majunya progress bar
                
                # 3. Setelah AI selesai, lanjut bikin PDF
                if ai_result["error"]:
                    my_bar.empty()
                    st.error(f"Failed to generate AI insights. Error: {ai_result['error']}")
                else:
                    my_bar.progress(90, text="Compiling A4 landscape layout...")
                    try:
                        from pdf_generator import create_healthcheck_pdf
                        pdf_path = create_healthcheck_pdf(
                            user_data=st.session_state.user_data,
                            score_percentage=f"{score_percentage}%",
                            answers=finance_answers,
                            ai_data=ai_result["data"]
                        )
                        
                        my_bar.progress(100, text="Report generated successfully! 🎉")
                        time.sleep(0.5)
                        my_bar.empty()
                        
                        with open(pdf_path, "rb") as pdf_file:
                            st.download_button(
                                label="📥 Download Your Full Report (PDF)",
                                data=pdf_file,
                                file_name=f"BlueRock_Finance_Report_{st.session_state.user_data['company'].replace(' ', '_')}.pdf",
                                mime="application/pdf",
                                type="primary"
                            )
                    except Exception as e:
                        my_bar.empty()
                        st.error(f"Failed to generate PDF. Error: {e}")

        except Exception as e:
            st.error(f"Cannot load Finance questions. Error: {e}")
            
        if st.button("Reset Form"):
            st.session_state.clear()
            st.rerun()

    # ==========================================
    # ROUTE B: BVA (AI CONVERSATIONAL INTERVIEW)
    # ==========================================
    else:
        from scoring_config import load_bva_logic
        
        bva_logic = load_bva_logic()
        question_bank = "\n".join([f"{q_id}: {data['text']}" for q_id, data in list(bva_logic['question_weights'].items())])
        
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
        """
        
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=system_instruction,
            generation_config={"response_mime_type": "application/json"}
        )

        if "messages" not in st.session_state:
            st.session_state.messages = []
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "Hi there! I'm your BlueRock diagnostic assistant. I'll be asking you a few questions about your business to calculate your health score. Are you ready to begin?"
            })
            
        if "extracted_data" not in st.session_state:
            st.session_state.extracted_data = {}

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
        st.sidebar.markdown("### 🔍 Live Extracted Data")
        st.sidebar.json(st.session_state.extracted_data)

        if user_input := st.chat_input("Type your response here..."):
            st.chat_message("user").markdown(user_input)
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            gemini_history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages]
            
            with st.spinner("Analyzing..."):
                try:
                    chat = model.start_chat(history=gemini_history[:-1]) 
                    response = chat.send_message(user_input)
                    
                    raw_text = response.text
                    raw_text = raw_text.replace("```json", "").replace("```", "").strip()
                    response_data = json.loads(raw_text)
                    
                    agent_reply = response_data.get("agent_reply", "")
                    next_question = response_data.get("next_question", "")
                    extracted = response_data.get("extracted_answers", {})
                    
                    full_bot_response = f"{agent_reply}\n\n**{next_question}**"
                    st.chat_message("assistant").markdown(full_bot_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_bot_response})
                    
                    if extracted:
                        st.session_state.extracted_data.update(extracted)
                    st.rerun() 
                    
                except Exception as e:
                    st.error(f"Failed to process AI response. (Log: {e})")

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
                
                if not st.session_state.extracted_data:
                    st.warning("No data extracted yet. Please answer a few questions first!")
                else:
                    with st.spinner("Calculating your BVA Score & Saving Data..."):
                        result = calculate_bva_score(
                            extracted_answers=st.session_state.extracted_data,
                            user_goal=st.session_state.user_data['bva_goal']
                        )
                        
                        try:
                            conn = st.connection("gsheets", type=GSheetsConnection)
                            sheet_url = os.getenv("GSHEET_URL")
                            existing_data = conn.read(spreadsheet=sheet_url, usecols=list(range(10)), ttl=0).dropna(how="all")
                            
                            new_row_values = [
                                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                st.session_state.user_data.get('name', ''),
                                st.session_state.user_data.get('email', ''),
                                st.session_state.user_data.get('company', ''),
                                st.session_state.user_data.get('role', ''),
                                st.session_state.user_data.get('assessment_type', ''),
                                st.session_state.user_data.get('bva_goal', ''),
                                f"{result['score_percentage']}%",
                                result['band'],
                                str(st.session_state.extracted_data)
                            ]
                            
                            new_data_df = pd.DataFrame([new_row_values], columns=existing_data.columns)
                            updated_data = pd.concat([existing_data, new_data_df], ignore_index=True)
                            conn.update(spreadsheet=sheet_url, data=updated_data)
                            
                        except Exception as e:
                            st.error(f"Gagal menyimpan ke database. Error: {e}")

                        st.markdown("---")
                        st.subheader("🎯 Your Assessment Results")
                        st.metric(label="Overall Business Health Score", value=f"{result['score_percentage']}%")
                        st.markdown(f"### Classification: :{result['color']}[**{result['band']}**]")

                    # --- ROUTE B: PROGRESS BAR & AI GENERATION ---
                    my_bar = st.progress(0, text="Preparing your custom BVA PDF Report... Please wait.")
                    
                    ai_result = {"data": None, "done": False, "error": None}
                    
                    # EKSTRAK DATA KE VARIABEL LOKAL DULU DI SINI
                    current_company = st.session_state.user_data['company']
                    current_assessment = st.session_state.user_data['assessment_type']
                    
                    def fetch_ai_insights_bva():
                        try:
                            ai_result["data"] = generate_ai_report_insights(
                                answers=st.session_state.extracted_data,
                                score=result['score_percentage'],
                                company_name=current_company,      # Pakai variabel lokal
                                assessment_type=current_assessment # Pakai variabel lokal
                            )
                        except Exception as e:
                            ai_result["error"] = e
                        finally:
                            ai_result["done"] = True

                    # 1. Mulai proses AI di background thread
                    ai_thread = threading.Thread(target=fetch_ai_insights_bva)
                    ai_thread.start()
                    
                    # 2. Animasi progress bar
                    progress_val = 10
                    my_bar.progress(progress_val, text="Analyzing conversational logs...")
                    
                    while not ai_result["done"]:
                        if progress_val < 85:
                            progress_val += 1
                            my_bar.progress(progress_val, text=f"AI Consultant is writing deep evaluation pages... ({progress_val}%)")
                        time.sleep(0.3)
                    
                    # 3. Selesaikan PDF
                    if ai_result["error"]:
                        my_bar.empty()
                        st.error(f"Failed to generate AI insights. Error: {ai_result['error']}")
                    else:
                        my_bar.progress(90, text="Compiling A4 landscape layout...")
                        try:
                            from pdf_generator import create_healthcheck_pdf
                            pdf_path = create_healthcheck_pdf(
                                user_data=st.session_state.user_data,
                                score_percentage=result['score_percentage'],
                                answers=st.session_state.extracted_data,
                                ai_data=ai_result["data"]
                            )
                            
                            my_bar.progress(100, text="Report generated successfully! 🎉")
                            time.sleep(0.5)
                            my_bar.empty()
                            
                            with open(pdf_path, "rb") as pdf_file:
                                st.download_button(
                                    label="📥 Download Your Full Report (PDF)",
                                    data=pdf_file,
                                    file_name=f"BlueRock_BVA_Report_{st.session_state.user_data['company'].replace(' ', '_')}.pdf",
                                    mime="application/pdf",
                                    type="primary"
                                )
                        except Exception as e:
                            my_bar.empty()
                            st.error(f"Failed to generate PDF. Error: {e}")