from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import json
import os
from datetime import datetime
import sqlite3
import hashlib
import random

app = FastAPI(title="TikTok Audit System - Test Mode")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Database setup
def init_db():
    conn = sqlite3.connect('audits.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS audits
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT,
                  email TEXT,
                  amount INTEGER,
                  status TEXT,
                  pdf_path TEXT,
                  created_at TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>TikTok Audit - Test Mode</title>
        <style>
            body { font-family: Arial; max-width: 600px; margin: 50px auto; padding: 20px; }
            input, button { width: 100%; padding: 12px; margin: 10px 0; font-size: 16px; }
            button { background: linear-gradient(135deg, #FF0050, #FFAA00); color: white; border: none; cursor: pointer; }
            .report { background: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 10px; }
        </style>
    </head>
    <body>
        <h1>🔍 TikTok Audit (Test Mode)</h1>
        <p>Enter any TikTok username to generate a sample audit report.</p>
        
        <input type="text" id="username" placeholder="@username">
        <input type="email" id="email" placeholder="your@email.com (optional)">
        <button onclick="generateAudit()">Generate Free Audit</button>
        
        <div id="result"></div>
        
        <script>
        async function generateAudit() {
            const username = document.getElementById('username').value;
            const email = document.getElementById('email').value;
            
            if (!username) {
                alert('Please enter a username');
                return;
            }
            
            const response = await fetch('/api/audit', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username, email})
            });
            
            const data = await response.json();
            
            document.getElementById('result').innerHTML = `
                <div class="report">
                    <h2>📊 Audit Report for @${username}</h2>
                    <p><strong>Fake Follower Score:</strong> ${data.shadowban_score}%</p>
                    <p><strong>Engagement Rate:</strong> ${data.engagement_rate}%</p>
                    <p><strong>Optimal Posting Times:</strong> ${data.best_times.join(', ')}</p>
                    <p><strong>Recommendations:</strong></p>
                    <ol>
                        <li>Post at ${data.best_times[0]} for maximum reach</li>
                        <li>Use 3-5 relevant hashtags per video</li>
                        <li>Engage with comments within 1 hour</li>
                        <li>Create duets with trending sounds</li>
                    </ol>
                    <a href="${data.pdf_url}" target="_blank">📥 Download Full PDF Report</a>
                </div>
            `;
        }
        </script>
    </body>
    </html>
    """

@app.post("/api/audit")
async def run_audit(data: dict):
    username = data.get('username', '@testuser')
    email = data.get('email', 'test@example.com')
    
    try:
        # Generate fake TikTok data (for testing)
        tiktok_data = {
            "username": username,
            "followers": random.randint(1000, 100000),
            "following": random.randint(100, 5000),
            "likes": random.randint(5000, 500000),
            "videos": random.randint(10, 500),
            "engagement_rate": round(random.uniform(1.0, 10.0), 2),
            "shadowban_score": random.randint(0, 50),
            "best_times": ["7-9 PM", "12-2 PM", "4-6 PM"],
            "timestamp": datetime.now().isoformat()
        }
        
        # Generate PDF
        pdf_filename = await generate_pdf(username, tiktok_data)
        
        # Save to database
        conn = sqlite3.connect('audits.db')
        c = conn.cursor()
        c.execute('''INSERT INTO audits (username, email, amount, status, pdf_path, created_at)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (username, email, 0, 'completed', pdf_filename, datetime.now()))
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "username": username,
            "shadowban_score": tiktok_data["shadowban_score"],
            "engagement_rate": tiktok_data["engagement_rate"],
            "best_times": tiktok_data["best_times"],
            "pdf_url": f"/download/{pdf_filename}"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/audits")
async def get_audits():
    conn = sqlite3.connect('audits.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM audits ORDER BY created_at DESC LIMIT 100")
    audits = [dict(row) for row in c.fetchall()]
    conn.close()
    return {"audits": audits}

@app.get("/download/{filename}")
async def download_pdf(filename: str):
    # Check if file exists
    if os.path.exists(f"static/pdfs/{filename}"):
        return FileResponse(f"static/pdfs/{filename}", media_type='application/pdf')
    else:
        # Generate a simple PDF on the fly
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib.utils import simpleSplit
        
        os.makedirs("static/pdfs", exist_ok=True)
        filepath = f"static/pdfs/{filename}"
        
        c = canvas.Canvas(filepath, pagesize=letter)
        c.setFont("Helvetica", 12)
        c.drawString(100, 750, f"TikTok Audit Report for {filename.replace('_audit.pdf', '')}")
        c.drawString(100, 730, "Generated in test mode")
        c.drawString(100, 710, "This is a sample report.")
        c.drawString(100, 690, "In production mode, this would include:")
        c.drawString(100, 670, "- Real TikTok data analysis")
        c.drawString(100, 650, "- Shadowban detection")
        c.drawString(100, 630, "- Engagement metrics")
        c.drawString(100, 610, "- Competitor benchmarking")
        c.save()
        
        return FileResponse(filepath, media_type='application/pdf')

async def generate_pdf(username, data):
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    import os
    
    os.makedirs("static/pdfs", exist_ok=True)
    
    # Create unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{username}_{timestamp}_audit.pdf"
    filepath = f"static/pdfs/{filename}"
    
    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 20)
    c.drawString(100, height - 100, f"TikTok Audit Report")
    c.setFont("Helvetica", 16)
    c.drawString(100, height - 130, f"For: @{username}")
    
    # Metrics
    y = height - 180
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, y, "Account Metrics:")
    c.setFont("Helvetica", 12)
    
    metrics = [
        f"Followers: {data['followers']:,}",
        f"Following: {data['following']:,}",
        f"Total Likes: {data['likes']:,}",
        f"Videos Posted: {data['videos']}",
        f"Engagement Rate: {data['engagement_rate']}%",
        f"Shadowban Risk: {data['shadowban_score']}%"
    ]
    
    for i, metric in enumerate(metrics):
        c.drawString(120, y - 30 - (i * 20), metric)
    
    # Recommendations
    y_start = y - 200
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, y_start, "Growth Recommendations:")
    c.setFont("Helvetica", 12)
    
    recommendations = [
        "1. Post during peak hours (7-9 PM, 12-2 PM)",
        "2. Use trending sounds with 5-10k videos",
        "3. Engage with comments within first hour",
        "4. Collaborate with similar-sized creators",
        "5. Analyze competitor content strategy",
        "6. Maintain consistent posting schedule"
    ]
    
    for i, rec in enumerate(recommendations):
        c.drawString(120, y_start - 30 - (i * 20), rec)
    
    c.save()
    return filename

@app.get("/health")
async def health_check():
    return {"status": "healthy", "mode": "test", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    
    # Create necessary directories
    os.makedirs("static/pdfs", exist_ok=True)
    
    port = int(os.environ.get("PORT", 8080))
    host = "0.0.0.0"
    
    print(f"🚀 TikTok Audit System Starting in TEST MODE")
    print(f"📡 Server: http://{host}:{port}")
    print(f"🔗 Health check: http://{host}:{port}/health")
    print(f"📊 Admin data: http://{host}:{port}/api/audits")
    print(f"💡 No API keys needed - Running in demo mode")
    
    uvicorn.run(app, host=host, port=port)
