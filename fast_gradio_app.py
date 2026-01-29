"""
Fast Medical Scan Report Chatbot - Instant PDF generation (no wait).
Upload scan → Get QR code + PDFs in < 10 seconds.
"""
from main import analyze_scan
import gradio as gr
import io
import time
from pathlib import Path
from PIL import Image
from generate_scan_report_pdf import generate_report
from generate_prescription_pdf import generate_prescription
import base64
import qrcode
from datetime import datetime
import uuid


def _save_upload_to_path(uploaded) -> str:
    """Read various Gradio upload types and save to a file path, returning the path."""
    filename = getattr(uploaded, "name", None)
    if filename and Path(filename).suffix:
        return filename

    # Read uploaded bytes (supports SpooledTemporaryFile or file-like objects)
    data = None
    try:
        try:
            data = uploaded.read()
        except Exception:
            if filename:
                with open(filename, "rb") as f:
                    data = f.read()
    except Exception:
        data = None

    if data is None:
        raise ValueError("Unable to read uploaded file bytes")

    # Try to open with PIL and downscale very large images to speed processing
    try:
        img = Image.open(io.BytesIO(data))
        fmt = (img.format or "PNG").lower()

        max_dim = 1024
        if max(img.size) > max_dim:
            img.thumbnail((max_dim, max_dim), Image.LANCZOS)

        dest_dir = Path("uploads")
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / f"upload_{int(time.time()*1000)}.{fmt}"

        try:
            if fmt in ("jpeg", "jpg"):
                img.save(dest_path, format="JPEG", quality=85, optimize=True)
            else:
                img.save(dest_path, format=img.format or "PNG", optimize=True)
        except Exception:
            with open(dest_path, "wb") as out:
                out.write(data)

        return str(dest_path)
    except Exception:
        # Fallback: write raw bytes
        fmt = "png"
        dest_dir = Path("uploads")
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / f"upload_{int(time.time()*1000)}.{fmt}"
        with open(dest_path, "wb") as out:
            out.write(data)
        return str(dest_path)


def analyze(file):
    """Analyze scan and return JSON result."""
    if not file:
        return {"error": "No file provided"}

    try:
        path = None
        if isinstance(file, str):
            path = file
        else:
            path = _save_upload_to_path(file)

        result = analyze_scan(path)
        return result
    except Exception as e:
        return {"error": f"Failed to analyze uploaded file: {str(e)}"}


def generate_qr_instant(token: str):
    """Generate QR code instantly (no server call)."""
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
    # Convert to PIL Image (Gradio compatible format)
    pil_img = Image.new('RGB', img.size, 'white')
    pil_img.paste(img)
    return pil_img


def fast_analyze_and_report(file):
    """
    FAST FLOW (< 10 seconds):
    1. Upload scan
    2. Analyze immediately
    3. Generate QR instantly
    4. Generate PDFs instantly
    5. Return all outputs
    NO WAITING for verification!
    """
    start_time = time.time()
    
    if not file:
        return None, None, None, "❌ No file provided"
    
    try:
        # Step 1: Analyze scan (fast)
        analysis = analyze(file)
        if not isinstance(analysis, dict):
            return None, None, None, f"❌ Analysis failed: Invalid response type"
        if "error" in analysis:
            return None, None, None, f"❌ Analysis failed: {analysis.get('error', 'Unknown error')}"
        
        # Step 2: Generate unique token for QR
        token = str(uuid.uuid4())[:16]
        
        # Step 3: Generate QR code instantly (no network call)
        try:
            qr_img = generate_qr_instant(token)
        except Exception as e:
            qr_img = None
            print(f"Warning: QR generation failed: {e}")
        
        # Step 4: Generate PDFs instantly
        try:
            out_dir = str(Path(__file__).parent)
            report_path = generate_report(analysis, out_dir=out_dir)
            prescription_path = generate_prescription(analysis, patient_id=token[:8].upper(), out_dir=out_dir)
        except Exception as e:
            return None, None, qr_img, f"❌ PDF generation failed: {str(e)}"
        
        elapsed = time.time() - start_time
        
        success_msg = (
            f"✅ **Report Generated Successfully in {elapsed:.1f}s**\n\n"
            f"📄 Scan Report: {Path(report_path).name}\n"
            f"💊 Prescription: {Path(prescription_path).name}\n"
            f"🔐 QR Token: {token}\n\n"
            f"**Analysis Results:**\n"
            f"• Tumor Detected: {analysis.get('has_tumor', 'N/A')}\n"
            f"• Tumor Type: {analysis.get('tumor_type', 'N/A')}\n"
            f"• Size: {analysis.get('size', 'N/A')}\n"
            f"• Location: {analysis.get('location', 'N/A')}\n"
            f"• Confidence: {round(float(analysis.get('confidence', 0)) * 100, 1) if isinstance(analysis.get('confidence'), (int, float)) else 'N/A'}%"
        )
        
        return report_path, prescription_path, qr_img, success_msg
        
    except Exception as e:
        print(f"Error in fast_analyze_and_report: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None, f"❌ Unexpected error: {str(e)}"


# Create the fast Gradio interface
demo = gr.Interface(
    fn=fast_analyze_and_report,
    inputs=gr.File(label="📤 Upload Brain Scan Image", file_types=["image"]),
    outputs=[
        gr.File(label="📄 Download Scan Report", show_label=True),
        gr.File(label="💊 Download Prescription", show_label=True),
        gr.Image(label="🔐 QR Code for Verification", show_label=True),
        gr.Textbox(label="📋 Status & Results", lines=5, max_lines=10),
    ],
    title="⚡ Fast AI Brain Scan Report Generator",
    description="Upload a brain scan image → Get report, prescription, and QR code instantly (< 10 seconds)",
    theme=gr.themes.Soft(),
)


if __name__ == "__main__":
    import os
    port = int(os.environ.get("GRADIO_PORT", "7862"))
    print(f"\nFast Chatbot launching on http://127.0.0.1:{port}")
    print("Expected response time: < 10 seconds\n")
    demo.launch(share=False, server_name="127.0.0.1", server_port=port)
