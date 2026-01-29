"""
Verification Server - Handles QR scanning from Expo Go
Listens on http://localhost:7866 for /verify?token=TOKEN endpoint
"""
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
import threading
import sys

# Reference to gradio app's verification dict
# This will be imported/shared with secure_app.py
verification_status = {}

app = FastAPI(title="QR Verification Server")


@app.get("/verify")
async def verify_token(token: str):
    """
    Called when user scans QR code and opens link.
    Marks token as verified in secure_app.py - INSTANTLY returns response
    """
    global verification_status
    
    print(f"\n✅ QR Scanned! Token verified: {token}")
    
    # Mark as verified in background (non-blocking)
    def mark_verified_background():
        try:
            import secure_app
            secure_app.mark_verified(token)
        except Exception as e:
            print(f"Note: {e}")
    
    # Fire-and-forget background task
    import threading
    threading.Thread(target=mark_verified_background, daemon=True).start()
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>QR Verified ✓</title>
        <style>
            body {{ font-family: Arial, sans-serif; text-align: center; margin-top: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; height: 100vh; display: flex; flex-direction: column; justify-content: center; }}
            .success {{ color: #4ade80; font-size: 28px; margin: 20px; font-weight: bold; }}
            .token {{ font-family: monospace; background: rgba(255,255,255,0.2); padding: 12px; border-radius: 6px; word-break: break-all; }}
            h1 {{ margin: 0; font-size: 32px; }}
            .container {{ background: rgba(0,0,0,0.2); padding: 40px; border-radius: 12px; max-width: 500px; margin: 0 auto; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>✅ QR Code Verified!</h1>
            <p class="success">Your scan has been verified successfully</p>
            <p>Token: <span class="token">{token}</span></p>
            <p style="color: #e0e0e0; margin-top: 30px; font-size: 16px;">
                ✓ Verification confirmed<br>
                ✓ Reports are being generated<br>
                ✓ You can close this page now
            </p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "QR Verification Server"}


@app.get("/")
async def root():
    """Root endpoint info."""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>QR Verification Server</title>
        <style>
            body { font-family: Arial; padding: 20px; max-width: 600px; margin: 0 auto; }
            .endpoint { background: #f0f0f0; padding: 10px; margin: 10px 0; font-family: monospace; }
        </style>
    </head>
    <body>
        <h1>🔐 QR Verification Server</h1>
        <p>Endpoint: <span class="endpoint">/verify?token=TOKEN</span></p>
        <p>Health: <span class="endpoint">/health</span></p>
        <p style="color: #666; margin-top: 30px;">
            This server handles QR code verification scans from Expo Go.
        </p>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🔐 Starting QR Verification Server")
    print("="*60)
    print("📍 Listening on http://localhost:8000")
    print("📱 This handles scans from Expo Go")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
