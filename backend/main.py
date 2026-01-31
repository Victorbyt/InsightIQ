from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import stripe
import json
import os
from datetime import datetime
import sqlite3
import asyncio
from scraper import TikTokScraper
from pdf_generator import PDFGenerator
from email_sender import EmailSender

app = FastAPI(title="TikTok Audit System")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize services
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_...")
scraper = TikTokScraper()
pdf_gen = PDFGenerator()
email_sender = EmailSender()

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
    with open("frontend/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.get("/admin", response_class=HTMLResponse)
async def admin():
    with open("frontend/admin.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.post("/api/create-checkout")
async def create_checkout(username: str = Form(...), email: str = Form(...)):
    try:
        # Create Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'TikTok Audit for @{username}',
                    },
                    'unit_amount': 999,  # $9.99
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f'http://localhost:8000/success?session_id={{CHECKOUT_SESSION_ID}}&username={username}&email={email}',
            cancel_url='http://localhost:8000/',
            metadata={'username': username, 'email': email}
        )
        
        return JSONResponse({"session_id": session.id, "url": session.url})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/audit/{username}")
async def run_audit(username: str, email: str):
    try:
        # Scrape TikTok data
        data = await scraper.scrape_profile(username)
        
        # Generate PDF
        pdf_path = pdf_gen.generate_report(username, data)
        
        # Send email
        email_sender.send_report(email, username, pdf_path)
        
        # Save to database
        conn = sqlite3.connect('audits.db')
        c = conn.cursor()
        c.execute('''INSERT INTO audits (username, email, amount, status, pdf_path, created_at)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (username, email, 999, 'completed', pdf_path, datetime.now()))
        conn.commit()
        conn.close()
        
        return {"status": "success", "pdf_url": f"/download/{pdf_path}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/audits")
async def get_audits():
    conn = sqlite3.connect('audits.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM audits ORDER BY created_at DESC")
    audits = [dict(row) for row in c.fetchall()]
    conn.close()
    return {"audits": audits}

@app.get("/download/{filename}")
async def download_pdf(filename: str):
    return FileResponse(f"static/pdfs/{filename}", media_type='application/pdf')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
