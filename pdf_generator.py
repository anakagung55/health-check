from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader
import os
from datetime import datetime

def create_healthcheck_pdf(user_data, score_percentage, answers):
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    pdf_path = os.path.join(output_dir, f"BlueRock_Report_{user_data.get('company', 'Company').replace(' ', '_')}.pdf")

    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('report_template.html')

    # Menentukan klasifikasi berdasarkan skor
    score_val = float(score_percentage.replace('%', ''))
    if score_val >= 75:
        band = "Premium Asset"
    elif score_val >= 50:
        band = "Strong Performer"
    else:
        band = "Action Required"

    # STRUKTUR DATA MULTI-HALAMAN (Membuat halaman dinamis)
    # Ini dikondisikan: Jika asesmen Finance, pilarnya SWOT. Jika BVA, pilarnya fungsi bisnis.
    if user_data.get('assessment_type') == "Finance Function Health Check":
        pillars = [
            {
                "name": "Strengths & Weaknesses",
                "description": "Internal factors currently impacting your finance team's efficiency and reliability.",
                "items": [
                    {"question": "System Productivity", "insight": "Analysis of current financial software stack.", "score_text": "Based on input", "color_class": "high"},
                    {"question": "Key Person Risk", "insight": "Dependency on individual team members.", "score_text": "Based on input", "color_class": "low"},
                ]
            },
            {
                "name": "Opportunities & Threats",
                "description": "External factors and future improvements for the finance function.",
                "items": [
                    {"question": "Automation Value", "insight": "Potential for measurable efficiency gains.", "score_text": "Based on input", "color_class": "high"},
                    {"question": "Cybersecurity", "insight": "Protection of sensitive financial data.", "score_text": "Based on input", "color_class": "med"},
                ]
            }
        ]
    else:
        pillars = [
            {
                "name": "Financial & Strategic Health",
                "description": "Review of your underlying profitability, records, and strategic growth plan.",
                "items": [
                    {"question": "Revenue Trend", "insight": "Evaluation of revenue trajectory over 3 years.", "score_text": "Recorded", "color_class": "high"},
                    {"question": "Strategic Plan", "insight": "Clarity of documented goals and metrics.", "score_text": "Recorded", "color_class": "med"},
                ]
            }
        ]

    template_vars = {
        "client_name": user_data.get("company", "Valued Client"),
        "date": datetime.now().strftime("%d %B %Y"),
        "final_score": score_percentage,
        "band": band,
        "highlights": [
            {"title": "Financial Operations", "status": "Stable"},
            {"title": "Risk Management", "status": "Needs Review"},
            {"title": "Scalability & Systems", "status": "Optimized"}
        ],
        "pillars": pillars # Data pilar ini yang akan mencetak halaman ke-2, ke-3 dst!
    }

    rendered_html = template.render(template_vars)
    HTML(string=rendered_html).write_pdf(pdf_path)
    
    return pdf_path