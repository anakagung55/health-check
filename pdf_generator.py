from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader
import os
from datetime import datetime

def create_healthcheck_pdf(user_data, score_percentage, answers):
    """
    Mengambil data user dan jawaban, memasukkannya ke template HTML,
    lalu mengubahnya menjadi file PDF menggunakan WeasyPrint.
    """
    # 1. Siapkan folder output
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    pdf_path = os.path.join(output_dir, f"BlueRock_Report_{user_data.get('company', 'Company').replace(' ', '_')}.pdf")

    # 2. Setup Jinja2 Environment
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('report_template.html')

    # 3. Siapkan Data Dinamis (Dummy data agar HTML tetap cantik)
    template_vars = {
        "client_name": user_data.get("company", "Valued Client"),
        "client_url": "Confidential Assessment",
        "report_date": datetime.now().strftime("%d %B %Y"),
        "audit_score": round(float(score_percentage.replace('%', '')) / 10, 1),
        "score_label": "Action Required" if float(score_percentage.replace('%', '')) < 50 else "Strong Performer",
        "monetization_text": "Based on your recent assessment, here is the breakdown of your operational health.",
        "google_rankings": [
            {"keyword": "Revenue Growth", "rank": "Stable"},
            {"keyword": "Cost Management", "rank": "Needs Review"},
            {"keyword": "Risk & Compliance", "rank": "Strong"}
        ],
        "findings": {
            "technical_seo_foundations": {"severity": "High", "display_status": "Critical", "title": "Financial Reporting", "finding": "Data shows potential bottlenecks in reporting.", "business_impact": "Delayed decision making.", "recommendation": "Implement automated dashboards.", "effort_label": "High Effort"},
            "on_page_meta_hierarchy": {"severity": "Medium", "display_status": "Warning", "title": "Cashflow Management", "finding": "Working capital can be optimized.", "business_impact": "Locked cash reserves.", "recommendation": "Review AP/AR cycles.", "effort_label": "Medium Effort"},
            "schema_markup_presence": {"severity": "Low", "display_status": "Good", "title": "Team Capability", "finding": "Strong foundational team.", "business_impact": "Operational stability.", "recommendation": "Maintain training.", "effort_label": "Low Effort"},
            "aeo_content_structure": {"severity": "Good", "display_status": "Excellent", "title": "Compliance", "finding": "All regulatory needs met.", "business_impact": "Zero penalties.", "recommendation": "Keep up the good work.", "effort_label": "Low Effort"},
            "faq_quality_and_formatting": {"severity": "Medium", "display_status": "Warning", "title": "Tech Stack", "finding": "Legacy systems in use.", "business_impact": "Slower processing.", "recommendation": "Cloud migration.", "effort_label": "High Effort"},
            "ai_visibility_signals": {"severity": "High", "display_status": "Critical", "title": "Key Person Risk", "finding": "Over-reliance on owner.", "business_impact": "Low transferability.", "recommendation": "Document standard operating procedures.", "effort_label": "Medium Effort"}
        },
        "count_critical": 2,
        "count_important": 2,
        "count_low": 2,
        "hero_img_path": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=800&q=80",
        "trust_img_path": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=800&q=80"
    }

    # 4. Render HTML dengan data
    rendered_html = template.render(template_vars)

    # 5. Konversi ke PDF
    HTML(string=rendered_html).write_pdf(pdf_path)
    
    return pdf_path