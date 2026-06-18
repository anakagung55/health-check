from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader
import os
from datetime import datetime

def create_healthcheck_pdf(user_data, score_percentage, answers, ai_data=None):
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    pdf_path = os.path.join(output_dir, f"BlueRock_Report_{user_data.get('company', 'Company').replace(' ', '_')}.pdf")

    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('report_template.html')

    score_val = float(score_percentage.replace('%', ''))
    if score_val >= 75:
        band = "Premium Asset"
    elif score_val >= 50:
        band = "Strong Performer"
    else:
        band = "Action Required"

    # FALLBACK: Jika API Gemini gagal/timeout, kita pakai data darurat agar PDF tetap terbuat
    if not ai_data:
        ai_data = {
            "executive_summary_paragraphs": [
                "A strong business relies on a solid foundation.",
                "This report reviews your operational and financial health based on your recent assessment.",
                "It highlights areas of strength and uncovers specific opportunities to increase value."
            ],
            "highlights": [
                {"title": "System Connectivity", "status": "Review Needed"}
            ],
            "pillars": [
                {
                    "name": "Standard Analysis",
                    "description": "General observations based on your input.",
                    "details": [
                        {"question": "Operational Metric", "insight": "Maintain current monitoring practices to ensure stability.", "score_text": "Average", "color_class": "med"}
                    ]
                }
            ]
        }

    # Masukkan data Gemini ke dalam variabel Jinja2
    template_vars = {
        "client_name": user_data.get("company", "Valued Client"),
        "date": datetime.now().strftime("%d %B %Y"),
        "final_score": score_percentage,
        "band": band,
        "ai": ai_data  # Ini kunci utamanya! Seluruh JSON Gemini masuk ke sini
    }

    rendered_html = template.render(template_vars)
    HTML(string=rendered_html).write_pdf(pdf_path)
    
    return pdf_path