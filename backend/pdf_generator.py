from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import os

class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.output_dir = "static/pdfs"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_report(self, username, data):
        filename = f"{username}_audit_{data['timestamp']}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#FF0050')
        )
        story.append(Paragraph(f"TikTok Audit Report: @{username}", title_style))
        story.append(Spacer(1, 20))
        
        # Summary
        story.append(Paragraph(f"<b>Overall Score:</b> {100 - data['shadowban_score']}/100", self.styles["Normal"]))
        story.append(Paragraph(f"<b>Shadowban Risk:</b> {data['shadowban_score']}%", self.styles["Normal"]))
        story.append(Spacer(1, 20))
        
        # Metrics Table
        metrics = [
            ["Metric", "Value", "Status"],
            ["Followers", f"{data['followers']:,}", "✓" if data['followers'] > 1000 else "⚠"],
            ["Engagement Rate", f"{data['engagement_rate']}%", "✓" if data['engagement_rate'] > 3 else "⚠"],
            ["Total Likes", f"{data['likes']:,}", "✓"],
            ["Video Count", data['videos'], "✓" if data['videos'] > 20 else "⚠"],
            ["Following", data['following'], "⚠" if data['following'] > 5000 else "✓"]
        ]
        
        table = Table(metrics, colWidths=[2*inch, 2*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#FF0050')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 12),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.beige),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        story.append(table)
        story.append(Spacer(1, 30))
        
        # Recommendations
        story.append(Paragraph("<b>🚀 Actionable Recommendations:</b>", self.styles["Heading2"]))
        recommendations = [
            f"1. Post at {data['best_times'][0]} for maximum reach",
            "2. Use 3-5 relevant hashtags per video",
            "3. Engage with comments within 1 hour of posting",
            "4. Create duets with trending sounds",
            "5. Maintain consistent posting schedule"
        ]
        
        for rec in recommendations:
            story.append(Paragraph(rec, self.styles["Normal"]))
            story.append(Spacer(1, 5))
        
        doc.build(story)
        return filename
