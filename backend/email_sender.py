import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

class EmailSender:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.sender_email = os.getenv("SENDER_EMAIL", "")
        self.sender_password = os.getenv("SENDER_PASSWORD", "")
    
    def send_report(self, recipient_email, username, pdf_path):
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            msg['Subject'] = f"Your TikTok Audit for @{username} is Ready!"
            
            body = f"""
            <html>
            <body>
                <h2>🎯 Your TikTok Audit Report</h2>
                <p>Hello!</p>
                <p>Your TikTok audit for <b>@{username}</b> is complete.</p>
                <p>Download your comprehensive report attached to this email.</p>
                <p><b>Key insights include:</b></p>
                <ul>
                    <li>Shadowban risk assessment</li>
                    <li>Engagement rate analysis</li>
                    <li>Optimal posting times</li>
                    <li>Competitor benchmarking</li>
                    <li>Actionable growth strategies</li>
                </ul>
                <p>Need help implementing the recommendations? Reply to this email!</p>
                <p>Best regards,<br>InsightIQ Team</p>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(body, 'html'))
            
            # Attach PDF
            with open(f"static/pdfs/{pdf_path}", "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename="{pdf_path}"')
            msg.attach(part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            print(f"Email sent to {recipient_email}")
            return True
        except Exception as e:
            print(f"Email error: {e}")
            return False
