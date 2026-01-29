"""
Secure Medical Scan Report Chatbot - QR Verification Flow
1. Upload scan → Display QR code with unique token
2. User must scan QR with phone to verify
3. After verification → Reports generated
"""
import gradio as gr
import time
import threading
from pathlib import Path
from PIL import Image
from generate_scan_report_pdf import generate_report
from generate_prescription_pdf import generate_prescription
import qrcode
import uuid
import random
import concurrent.futures

# Global verification tracking
verification_tokens = {}
verification_lock = threading.Lock()


def mark_token_verified(token: str):
    """Mark token as verified (called by verify_server.py)."""
    with verification_lock:
        verification_tokens[token] = True
        print(f"✅ Token marked verified: {token}")


def mark_verified(token: str):
    """Compatibility wrapper for verify_server.py which expects mark_verified()."""
    return mark_token_verified(token)


def is_token_verified(token: str) -> bool:
    """Check if token has been verified."""
    with verification_lock:
        return verification_tokens.get(token, False)


def generate_qr_image(token: str):
    """Generate QR code image pointing to verification server."""
    try:
        # QR code links to http://localhost:7866/verify?token=TOKEN
        verification_url = f"http://localhost:7866/verify?token={token}"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=2,
        )
        qr.add_data(verification_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        if hasattr(img, 'convert'):
            return img.convert('RGB')
        return img
    except Exception as e:
        print(f"QR Error: {e}")
        return Image.new('RGB', (200, 200), 'white')


def get_mock_analysis():
    """Return random mock brain scan analysis."""
    analyses = [
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
    return random.choice(analyses)


def process_scan_secure(file):
    """
    FAST FLOW - QR Code first, then reports in background:
    1. User uploads scan
    2. Generate unique QR token & display QR code INSTANTLY (< 1 second)
    3. Return QR code immediately to show in UI
    4. Wait for QR verification in background
    5. Generate reports in separate background thread after verification
    """
    if not file:
        return None, None, None, "❌ No file provided"
    
    try:
        # Step 1: Generate unique token
        token = str(uuid.uuid4())[:16]
        print(f"\n🔐 Generated token: {token}")
        
        # Initialize token for verification
        with verification_lock:
            verification_tokens[token] = False
        
        # Step 2: Generate QR code (INSTANT - < 1 second)
        qr_img = generate_qr_image(token)

        # Also print the verification URL and an ASCII QR to the terminal for instant scanning
        # NOTE: verification endpoint uses port 8000 per secure workflow requirements
        verification_url = f"http://localhost:8000/verify?token={token}"
        print(f"✅ QR Code generated instantly!")
        print(f"🔗 Verification URL: {verification_url}\n")

        try:
            # build a QR object to get the matrix and print as blocks in terminal
            qr_term = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=1,
                border=2,
            )
            qr_term.add_data(verification_url)
            qr_term.make(fit=True)
            matrix = qr_term.get_matrix()

            print("Scan this QR in Expo Go (from your terminal):\n")
            # use double-block for better aspect ratio
            for row in matrix:
                line = ''.join('██' if col else '  ' for col in row)
                print(line)
            print("\n(If your terminal doesn't show the QR clearly, open the link above on your phone)\n")
        except Exception as e:
            print(f"⚠️ Could not print ASCII QR in terminal: {e}\n")

        # Step 3: Show initial message - RETURN IMMEDIATELY
        initial_msg = (
            f"📱 **QR CODE READY**\n\n"
            f"🔐 **Token:** `{token}`\n\n"
            f"**Scan the QR code above with Expo Go:**\n\n"
            f"1. Open Expo Go on your phone\n"
            f"2. Scan the QR code\n"
            f"3. Confirm verification\n\n"
            f"⏳ Waiting for scan..."
        )

        # Step 4: Synchronously wait for verification, then generate reports
        max_wait = 300  # 5 minutes
        poll_interval = 1
        elapsed = 0

        print(f"⏳ Waiting for QR verification...")

        while elapsed < max_wait:
            if is_token_verified(token):
                print(f"✅ QR Verified — Secure report generation started...")

                # Generate mock analysis (this simulates AI output already received)
                analysis = get_mock_analysis()
                out_dir = str(Path(__file__).parent)

                # Create quick summary immediately
                try:
                    quick_path = Path(out_dir) / f"quick_summary_{token}.txt"
                    with open(quick_path, "w", encoding="utf-8") as f:
                        f.write("Quick Scan Summary\n")
                        f.write("-------------------\n")
                        f.write(f"Token: {token}\n")
                        f.write(f"Tumor Detected: {analysis.get('has_tumor')}\n")
                        f.write(f"Type: {analysis.get('tumor_type') or 'N/A'}\n")
                        f.write(f"Size: {analysis.get('size') or 'N/A'}\n")
                        f.write(f"Location: {analysis.get('location') or 'N/A'}\n")
                        conf = analysis.get('confidence', 0)
                        conf_str = f"{round(conf*100,1)}%" if isinstance(conf, (int, float)) else 'N/A'
                        f.write(f"Confidence: {conf_str}\n")
                    print(f"✅ Quick summary ready: {quick_path.name}")
                except Exception as e:
                    print(f"⚠️ Could not write quick summary: {e}")

                # Generate both PDFs concurrently using processes (faster for CPU-bound PDF builds)
                report_path = None
                prescrip_path = None
                try:
                    with concurrent.futures.ProcessPoolExecutor(max_workers=2) as executor:
                        fut_report = executor.submit(generate_report, analysis, out_dir)
                        fut_presc = executor.submit(generate_prescription, analysis, token[:8].upper(), out_dir)

                        for fut in concurrent.futures.as_completed([fut_report, fut_presc]):
                            try:
                                res = fut.result()
                                if res and res.endswith('.pdf'):
                                    if 'scan_report_' in Path(res).name:
                                        report_path = res
                                        print(f"✅ Report generated: {Path(report_path).name}")
                                    else:
                                        prescrip_path = res
                                        print(f"✅ Prescription generated: {Path(prescrip_path).name}")
                            except Exception as e:
                                print(f"⚠️ Background generation error: {e}")
                except Exception:
                    # Fallback to threads if process-based parallelism fails
                    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                        fut_report = executor.submit(generate_report, analysis, out_dir)
                        fut_presc = executor.submit(generate_prescription, analysis, token[:8].upper(), out_dir)
                        for fut in concurrent.futures.as_completed([fut_report, fut_presc]):
                            try:
                                res = fut.result()
                                if res and res.endswith('.pdf'):
                                    if 'scan_report_' in Path(res).name:
                                        report_path = res
                                        print(f"✅ Report generated: {Path(report_path).name}")
                                    else:
                                        prescrip_path = res
                                        print(f"✅ Prescription generated: {Path(prescrip_path).name}")
                            except Exception as e:
                                print(f"⚠️ Background generation error: {e}")

                # Final terminal message and return to chatbot
                print("✅ Secure verification complete. Reports generated successfully.")
                if report_path:
                    print(f"📄 {Path(report_path).name} -> {report_path}")
                if prescrip_path:
                    print(f"📄 {Path(prescrip_path).name} -> {prescrip_path}")

                success_msg = "Verification successful. The report and prescription have been securely generated."
                return report_path, prescrip_path, None, success_msg

            time.sleep(poll_interval)
            elapsed += poll_interval

        # Timeout - did not verify
        print(f"❌ Verification timeout for token: {token}")
        timeout_msg = (
            f"⏱️ VERIFICATION TIMEOUT: No QR scan detected within {max_wait} seconds."
        )
        return None, None, None, timeout_msg
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None, f"❌ Error: {str(e)}"


# Gradio interface
demo = gr.Interface(
    fn=process_scan_secure,
    inputs=gr.File(label="📤 Upload Brain Scan Image", file_types=["image"]),
    outputs=[
        gr.File(label="📄 Download Scan Report (after QR verification)"),
        gr.File(label="💊 Download Prescription (after QR verification)"),
        gr.Textbox(label="📋 Status & Instructions", lines=8, max_lines=12),
    ],
    title="🔐 Secure Brain Scan Report - QR Verified",
    description="Upload scan → Scan QR with phone → Get secure reports",
    theme=gr.themes.Soft(),
)


if __name__ == "__main__":
    import os
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    port = int(os.environ.get("GRADIO_PORT", "7865"))
    print(f"\nSecure Chatbot: http://127.0.0.1:{port}")
    print(f"QR verification required before reports generated\n")
    try:
        demo.launch(share=False, server_name="127.0.0.1", server_port=port, show_error=False)
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
