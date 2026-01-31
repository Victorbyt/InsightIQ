const stripe = Stripe('pk_test_51...'); // Add your Stripe public key

async function startAudit() {
    const username = document.getElementById('username').value.trim();
    const email = document.getElementById('email').value.trim();
    
    if (!username || !email) {
        alert('Please enter both username and email');
        return;
    }
    
    const btn = document.getElementById('audit-btn');
    const btnText = btn.querySelector('.btn-text');
    const btnLoading = btn.querySelector('.btn-loading');
    
    btnText.style.display = 'none';
    btnLoading.style.display = 'inline';
    btn.disabled = true;
    
    try {
        // Create checkout session
        const response = await fetch('/api/create-checkout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, email })
        });
        
        const data = await response.json();
        
        if (data.url) {
            // Redirect to Stripe checkout
            window.location.href = data.url;
        } else {
            throw new Error('No checkout URL received');
        }
    } catch (error) {
        alert('Error starting audit: ' + error.message);
        console.error('Audit error:', error);
    } finally {
        btnText.style.display = 'inline';
        btnLoading.style.display = 'none';
        btn.disabled = false;
    }
}

// Handle success page
async function handleSuccess() {
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('session_id');
    const username = urlParams.get('username');
    const email = urlParams.get('email');
    
    if (sessionId && username && email) {
        try {
            // Show loading state
            document.body.innerHTML = `
                <div style="display: flex; justify-content: center; align-items: center; height: 100vh;">
                    <div style="text-align: center;">
                        <div style="font-size: 48px; margin-bottom: 20px;">🎉</div>
                        <h1 style="color: #333; margin-bottom: 10px;">Payment Successful!</h1>
                        <p style="color: #666; margin-bottom: 30px;">Processing your TikTok audit for @${username}...</p>
                        <div class="spinner"></div>
                        <p style="color: #666; margin-top: 20px;">Your report will be emailed to ${email}</p>
                    </div>
                </div>
            `;
            
            // Start audit
            const response = await fetch(`/api/audit/${username}?email=${encodeURIComponent(email)}`);
            const result = await response.json();
            
            if (result.status === 'success') {
                // Show success message
                document.body.innerHTML = `
                    <div style="display: flex; justify-content: center; align-items: center; height: 100vh;">
                        <div style="text-align: center; max-width: 500px;">
                            <div style="font-size: 64px; margin-bottom: 20px;">✅</div>
                            <h1 style="color: #333; margin-bottom: 10px;">Audit Complete!</h1>
                            <p style="color: #666; margin-bottom: 30px;">
                                Your TikTok audit for @${username} has been completed and sent to ${email}
                            </p>
                            <a href="${result.pdf_url}" target="_blank" 
                               style="background: linear-gradient(135deg, #FF0050, #FFAA00); 
                                      color: white; padding: 15px 30px; 
                                      border-radius: 10px; text-decoration: none; 
                                      display: inline-block; margin-bottom: 20px;">
                                Download PDF Report
                            </a>
                            <p style="color: #666; margin-top: 20px;">
                                Check your email for the complete report with actionable insights.
                            </p>
                        </div>
                    </div>
                `;
            }
        } catch (error) {
            document.body.innerHTML = `
                <div style="text-align: center; padding: 50px;">
                    <h1 style="color: #ff3333;">Something went wrong</h1>
                    <p>${error.message}</p>
                    <a href="/">Go back</a>
                </div>
            `;
        }
    }
}

// Check if we're on success page
if (window.location.pathname.includes('success')) {
    handleSuccess();
}
