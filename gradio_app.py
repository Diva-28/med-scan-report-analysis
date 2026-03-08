from main import analyze_scan
import gradio as gr # pyright: ignore[reportMissingImports]
import io
import time
from pathlib import Path
from PIL import Image
from generate_scan_report_pdf import generate_report
from generate_prescription_pdf import generate_prescription
import requests
import json


def _save_upload_to_path(uploaded) -> str:
    """Read various Gradio upload types and save to a file path, returning the path."""
    # If Gradio already gives a file path with a proper extension, use it directly
    filename = getattr(uploaded, "name", None)
    if filename and Path(filename).suffix:
        return filename

    # Otherwise read bytes and try to detect format with PIL
    try:
        # uploaded may be a SpooledTemporaryFile or file-like
        data = None
        try:
            # try reading attribute
            data = uploaded.read()
        except Exception:
            # try opening by name
            if filename:
                with open(filename, "rb") as f:
                    data = f.read()
        if data is None:
            raise ValueError("Unable to read uploaded file bytes")

        # Detect image format and downscale large images to speed processing
        try:
            img = Image.open(io.BytesIO(data))
            fmt = (img.format or "PNG").lower()

            # Downscale very large images to a max dimension to reduce processing time/memory
            max_dim = 1024
            if max(img.size) > max_dim:
                img.thumbnail((max_dim, max_dim), Image.LANCZOS)

            dest_dir = Path("uploads")
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest_path = dest_dir / f"upload_{int(time.time()*1000)}.{fmt}"

            # Save the (possibly resized) image to disk using an appropriate format
            try:
                save_kwargs = {}
                if fmt in ("jpeg", "jpg"):
                    save_kwargs = {"format": "JPEG", "quality": 85, "optimize": True}
                else:
                    save_kwargs = {"format": img.format or "PNG", "optimize": True}

                img.save(dest_path, **save_kwargs)
            except Exception:
                # Fallback: write original bytes
                with open(dest_path, "wb") as out:
                    out.write(data)

            return str(dest_path)
        except Exception:
            # If PIL detection failed, fall back to writing raw bytes as PNG
            fmt = "png"
            dest_dir = Path("uploads")
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest_path = dest_dir / f"upload_{int(time.time()*1000)}.{fmt}"
            with open(dest_path, "wb") as out:
                out.write(data)
            return str(dest_path)
    except Exception as e:
        raise


def analyze(file):
    """Accepts a file (path or file-like) and returns the analysis dict produced by analyze_scan.
    This re-uses your existing analyze_scan function in `main.py` so the model logic stays in one place.
    It robustly saves uploaded file-like objects to disk first so `analyze_scan` can validate extensions.
    """
    if not file:
        return {"error": "No file provided"}

    try:
        # If Gradio passed a path string, use it; otherwise save upload to uploads/ and pass path
        path = None
        if isinstance(file, str):
            path = file
        else:
            path = _save_upload_to_path(file)

        result = analyze_scan(path)
        return result
    except Exception as e:
        return {"error": f"Failed to analyze uploaded file: {str(e)}"}


def generate_verification_qr():
    """Request a new verification token from the backend and return QR code + token."""
    try:
        response = requests.post("http://localhost:8000/generate-token", timeout=5)
        response.raise_for_status()
        data = response.json()
        return data
    except Exception as e:
        return {"error": f"Failed to generate QR code: {str(e)}"}


def wait_for_verification(token: str, timeout_seconds: int = 300) -> bool:
    """Poll the verification endpoint until token is verified or timeout."""
    start_time = time.time()
    poll_interval = 1  # Check every 1 second
    
    while time.time() - start_time < timeout_seconds:
        try:
            response = requests.get(
                f"http://localhost:8000/token-status/{token}",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("verified"):
                    return True
            time.sleep(poll_interval)
        except Exception:
            time.sleep(poll_interval)
    
    return False


def analyze_and_report_with_verification(file):
    """
    Secure flow:
    1. Generate QR code for verification
    2. Wait for user to scan with mobile device
    3. Upon verification, analyze scan and generate both report + prescription PDFs
    """
    if not file:
        return None, None, None, "❌ No file provided"
    
    # Step 1: Generate QR code
    qr_data = generate_verification_qr()
    if "error" in qr_data:
        return None, None, None, f"❌ {qr_data['error']}"
    
    token = qr_data.get("token")
    qr_code_base64 = qr_data.get("qr_code_base64")
    
    # Convert base64 to PIL Image
    import base64
    qr_img_bytes = base64.b64decode(qr_code_base64)
    from PIL import Image as PILImage
    qr_img = PILImage.open(io.BytesIO(qr_img_bytes))
    
    # Display message with QR
    qr_message = f"🔐 **QR Code Generated**\n\nToken: {token}\n\n**Please scan this QR code with your mobile device (Expo Go or any QR scanner) within 5 minutes:**\n\nVerification URL: {qr_data.get('verification_url')}"
    
    # Step 2: Wait for verification (up to 5 minutes)
    verified = wait_for_verification(token, timeout_seconds=300)
    
    if not verified:
        return None, None, qr_img, "❌ QR verification failed or timed out. No files generated."
    
    # Step 3: Analyze scan
    analysis = analyze(file)
    if not isinstance(analysis, dict) or "error" in analysis:
        return None, None, qr_img, f"❌ Scan analysis failed: {analysis.get('error', 'Unknown error')}"
    
    try:
        # Step 4: Generate both PDFs
        out_dir = str(Path(__file__).parent)
        
        report_path = generate_report(analysis, out_dir=out_dir)
        prescription_path = generate_prescription(analysis, patient_id=token[:8].upper(), out_dir=out_dir)
        
        success_msg = f"✅ **QR verified. Secure PDFs generated successfully.**\n\n📄 Scan Report: {Path(report_path).name}\n💊 Prescription: {Path(prescription_path).name}"
        
        return report_path, prescription_path, qr_img, success_msg
    except Exception as e:
        return None, None, qr_img, f"❌ Failed to generate PDFs: {str(e)}"


def analyze_and_report(file):
    """Runs analysis and produces a PDF report; returns a tuple (analysis_dict, pdf_path).
    Gradio will present the JSON followed by a downloadable file.
    """
    analysis = analyze(file)
    if not isinstance(analysis, dict) or "error" in analysis:
        # return analysis and no file
        return analysis, None

    try:
        # generate_report expects a dict like the example in generate_scan_report_pdf
        pdf_path = generate_report(analysis, out_dir=str(Path(__file__).parent))
        return analysis, pdf_path
    except Exception as e:
        return {"error": f"Failed to generate PDF report: {str(e)}"}, None


# Simple Interface (No QR Verification)
demo = gr.Interface(
    fn=analyze_and_report,
    inputs=gr.File(label="Upload scan image"),
    outputs=[gr.JSON(label="Analysis"), gr.File(label="Download Report")],
    title="AI Brain Tumor Analysis System",
    description="Upload a brain MRI scan to get an AI-powered analysis of tumor type, size, and location, along with an auto-generated PDF report.",
    flagging_mode="never"
)





if __name__ == "__main__":
    # share=True will create a publicly accessible temporary link hosted by Gradio's servers.
    import os
    port = int(os.environ.get("GRADIO_PORT", "7861"))
    # Launch the tabbed interface (without share to avoid network checks during startup)
    demo.launch(share=False, server_name="127.0.0.1", server_port=port)

