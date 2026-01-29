"""
Medical Scan Report Chatbot with Real QR Verification via Expo Go.
Upload scan → Get QR code → Scan with Expo Go on phone → PDFs generated on approval.
"""
import gradio as gr
import io
import time
from pathlib import Path
from PIL import Image
from generate_scan_report_pdf import generate_report
from generate_prescription_pdf import generate_prescription
import qrcode
import uuid
import threading
import requests
from datetime import datetime


# In-memory verification status storage
verification_status = {}
verification_lock = threading.Lock()


def generate_qr_code_image(token: str) -> Image.Image:
    """
    Generate QR code that links to verification endpoint.
    Returns PIL Image that Gradio can display.
    """
    try:
        # Use port 8000 for verification server (match verification_server.py and other callers)
        verification_url = f"http://localhost:8000/verify?token={token}"

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=2,
        )
        qr.add_data(verification_url)
        qr.make(fit=True)

        # Get the PIL Image from qrcode
        qr_pil = qr.make_image(fill_color="black", back_color="white")

        # Ensure it's PIL Image format (not QRCode's PilImage wrapper)
        if hasattr(qr_pil, 'convert'):
            # It's already a PIL Image
            return qr_pil.convert('RGB')
        else:
            # Convert QRCode image to PIL
            img = Image.new('RGB', qr_pil.size, 'white')
            img.paste(qr_pil)
            return img

    except Exception as e:
        print(f"Error generating QR: {e}")
        # Return a placeholder image on error
        placeholder = Image.new('RGB', (200, 200), color='red')
        return placeholder


def wait_for_mobile_verification(token: str, timeout_seconds: int = 300) -> bool:
    """
    Wait for user to scan QR code with Expo Go.
    Returns True if verified, False if timeout.
    """
    print(f"\n🔐 Waiting for QR verification (token: {token})...")
    start_time = time.time()
    
    while time.time() - start_time < timeout_seconds:
        with verification_lock:
            if token in verification_status and verification_status[token]:
                print(f"✅ Token {token} verified!")
                return True
        
        time.sleep(1)  # Check every 1 second
    
    print(f"❌ Verification timeout for token {token}")
    return False


def generate_mock_analysis(file_path: str) -> dict:
    """
    Generate mock brain scan analysis.
    In production, replace with real ML model.
    """
    try:
        img = Image.open(file_path)
        
        # Mock analysis options
        analysis_options = [
            {
                "has_tumor": True,
                "tumor_type": "Glioma",
                "size": "1.2 cm",
                "location": "Right occipital lobe",
                "confidence": 0.92,
                "analysis_details": {
                    "anomalous_regions": 2,
                    "edge_complexity": 151,
                    "tumor_score": 0.85,
                    "region_intensities": [220.39, 158.87, 210.12, 176.93, 134.04, 160.1, 176.74, 124.37]
                }
            },
            {
                "has_tumor": True,
                "tumor_type": "Meningioma",
                "size": "0.8 cm",
                "location": "Left temporal lobe",
                "confidence": 0.88,
                "analysis_details": {
                    "anomalous_regions": 1,
                    "edge_complexity": 98,
                    "tumor_score": 0.72,
                    "region_intensities": [210.2, 145.5, 198.1, 165.3, 125.8, 152.9, 168.5, 118.2]
                }
            },
            {
                "has_tumor": False,
                "tumor_type": None,
                "size": None,
                "location": None,
                "confidence": 0.95,
                "analysis_details": {
                    "anomalous_regions": 0,
                    "edge_complexity": 45,
                    "tumor_score": 0.12,
                    "region_intensities": [180.5, 175.2, 178.9, 172.1, 176.3, 174.8, 179.2, 173.5]
                }
            }
        ]
        
        # Deterministic selection based on file
        import random
        file_hash = hash(Path(file_path).read_bytes())
        random.seed(file_hash)
        return random.choice(analysis_options)
        
    except Exception as e:
        return {"error": str(e)}


def qr_verified_report_flow(file):
    """
    Main flow:
    1. Upload scan image
    2. Generate unique QR token
    3. Show QR code to user
    4. Wait for Expo Go to scan
    5. Upon scan, analyze and generate PDFs
    6. Return all outputs
    """
    if not file:
        return None, None, None, "❌ No file provided"
    
    try:
        file_path = file.name if hasattr(file, 'name') else str(file)
        
        # Step 1: Generate unique token
        token = str(uuid.uuid4())[:16]
        print(f"\n📱 Generated token: {token}")
        
        # Initialize verification status for this token
        with verification_lock:
            verification_status[token] = False
        
        # Step 2: Generate QR code image
        qr_img = generate_qr_code_image(token)
        print(f"✅ QR code generated")
        
        # Step 3: Show QR and wait for scan
        status_waiting = (
            f"📱 **QR Code Generated - Scan with Expo Go Now**\n\n"
            f"🔐 Token: {token}\n"
            f"📲 Verification URL: http://localhost:8000/verify?token={token}\n\n"
            f"**Instructions:**\n"
            f"1. Open Expo Go on your phone\n"
            f"2. Scan the QR code shown above\n"
            f"3. Tap 'Allow' or 'Approve' when prompted\n"
            f"4. Wait for reports to generate\n\n"
            f"⏳ Waiting for your phone to scan QR code...\n"
            f"(Timeout in 5 minutes)"
        )
        
        # Step 4: Wait for mobile verification (up to 5 minutes)
        verified = wait_for_mobile_verification(token, timeout_seconds=300)
        
        if not verified:
            return None, qr_img, None, (
                f"❌ **Verification Timeout**\n\n"
                f"No scan detected within 5 minutes.\n"
                f"Please try again with a new upload."
            )
        
        # Step 5: Analyze and generate PDFs after verification
        status_processing = (
            f"✅ **QR Verified Successfully**\n\n"
            f"Processing your scan..."
        )
        
        analysis = generate_mock_analysis(file_path)
        
        if "error" in analysis:
            return None, qr_img, None, f"❌ Analysis failed: {analysis['error']}"
        
        # Step 6: Generate PDFs
        out_dir = str(Path(__file__).parent)
        report_path = generate_report(analysis, out_dir=out_dir)
        prescription_path = generate_prescription(analysis, patient_id=token[:8].upper(), out_dir=out_dir)
        
        # Format confidence
        confidence_val = analysis.get('confidence', 0)
        if isinstance(confidence_val, (int, float)):
            confidence_pct = f"{round(confidence_val * 100, 1)}%"
        else:
            confidence_pct = "N/A"
        
        final_status = (
            f"✅ **Reports Generated Successfully**\n\n"
            f"📄 Scan Report: {Path(report_path).name}\n"
            f"💊 Prescription: {Path(prescription_path).name}\n"
            f"🔐 Verified Token: {token}\n\n"
            f"**Analysis Results:**\n"
            f"• Tumor Detected: {'Yes' if analysis.get('has_tumor') else 'No'}\n"
            f"• Tumor Type: {analysis.get('tumor_type', 'N/A')}\n"
            f"• Size: {analysis.get('size', 'N/A')}\n"
            f"• Location: {analysis.get('location', 'N/A')}\n"
            f"• Confidence: {confidence_pct}"
        )
        
        return report_path, qr_img, prescription_path, final_status
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None, f"❌ Error: {str(e)}"


# Create Gradio interface
demo = gr.Interface(
    fn=qr_verified_report_flow,
    inputs=gr.File(label="📤 Upload Brain Scan Image", file_types=["image"]),
    outputs=[
        gr.File(label="📄 Download Scan Report (appears after QR scan)"),
        gr.Image(label="🔐 QR Code (Scan with Expo Go)", type="pil"),
        gr.File(label="💊 Download Prescription (appears after QR scan)"),
        gr.Textbox(label="📋 Status & Instructions", lines=8),
    ],
    title="🔐 Secure Brain Scan Report with QR Verification",
    description="Upload scan → Get QR → Scan with Expo Go on your phone → Get secure PDFs",
    theme=gr.themes.Soft(),
)


if __name__ == "__main__":
    import os
    port = int(os.environ.get("GRADIO_PORT", "7865"))
    print(f"\n🚀 QR Verification Chatbot on http://127.0.0.1:{port}")
    print(f"📱 Uses Expo Go for secure mobile verification\n")
    demo.launch(share=False, server_name="127.0.0.1", server_port=port)
