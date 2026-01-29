"""
FastAPI server for QR code verification.
Generates one-time tokens, serves QR codes, and verifies scans.
"""
import uuid
import qrcode
import io
import time
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import uvicorn
from pathlib import Path

app = FastAPI(title="Secure Medical Report Verification")

# In-memory token store: {token: {"verified": bool, "expires_at": float, "created_at": float}}
verification_tokens = {}
TOKEN_EXPIRY_SECONDS = 300  # 5 minutes


def generate_verification_token():
    """Create a unique token and store it."""
    token = str(uuid.uuid4())[:16]
    verification_tokens[token] = {
        "verified": False,
        "expires_at": time.time() + TOKEN_EXPIRY_SECONDS,
        "created_at": time.time(),
    }
    return token


def verify_token(token: str) -> bool:
    """Mark token as verified and check if valid."""
    if token not in verification_tokens:
        return False
    
    data = verification_tokens[token]
    
    # Check expiry
    if time.time() > data["expires_at"]:
        del verification_tokens[token]
        return False
    
    # Check if already verified (one-time use)
    if data["verified"]:
        return False
    
    # Mark as verified
    data["verified"] = True
    return True


def generate_qr_code(token: str) -> bytes:
    """Generate QR code image PNG bytes linking to verification endpoint."""
    # Adjust URL if you want to deploy to a public server
    verification_url = f"http://localhost:8000/verify?token={token}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data(verification_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to PNG bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    
    return img_bytes.getvalue()


@app.post("/generate-token")
def endpoint_generate_token():
    """Generate a new verification token and return QR code."""
    token = generate_verification_token()
    qr_bytes = generate_qr_code(token)
    
    return {
        "token": token,
        "verification_url": f"http://localhost:8000/verify?token={token}",
        "qr_code_base64": __import__("base64").b64encode(qr_bytes).decode("utf-8"),
        "expires_in_seconds": TOKEN_EXPIRY_SECONDS,
    }


@app.get("/verify")
def endpoint_verify(token: str):
    """Verification endpoint hit by QR scanner (e.g., Expo Go).
    Mark token as verified and return confirmation."""
    # Import from qr_verified_app to update its verification_status
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from qr_verified_app import verification_status, verification_lock
        
        # Mark token as verified
        with verification_lock:
            if token in verification_status:
                verification_status[token] = True
                return JSONResponse(
                    {
                        "status": "success",
                        "message": "✅ QR verified successfully. Reports being generated...",
                        "token": token,
                    }
                )
            else:
                raise HTTPException(status_code=400, detail="Token not found or expired.")
    except Exception as e:
        print(f"Verification error: {e}")
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")


@app.get("/token-status/{token}")
def endpoint_token_status(token: str):
    """Check if a token has been verified."""
    if token not in verification_tokens:
        raise HTTPException(status_code=404, detail="Token not found.")
    
    data = verification_tokens[token]
    
    # Check expiry
    if time.time() > data["expires_at"]:
        del verification_tokens[token]
        raise HTTPException(status_code=400, detail="Token expired.")
    
    return {
        "token": token,
        "verified": data["verified"],
        "expires_at": data["expires_at"],
        "time_remaining": max(0, data["expires_at"] - time.time()),
    }


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}


if __name__ == "__main__":
    print("Starting Verification Server on http://localhost:8000")
    print("  - Generate token: POST /generate-token")
    print("  - Verify scan: GET /verify?token=<token>")
    print("  - Check status: GET /token-status/<token>")
    print("  - Health check: GET /health")
    uvicorn.run(app, host="0.0.0.0", port=8000)
