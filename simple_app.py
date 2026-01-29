"""
Fast Medical Scan Report Chatbot - Simple and Stable Version
Upload → QR Code + PDFs in seconds
"""
import gradio as gr
import time
from pathlib import Path
from PIL import Image
from generate_scan_report_pdf import generate_report
from generate_prescription_pdf import generate_prescription
import qrcode
import uuid
import random


def generate_qr_image(token: str):
    """Generate QR code as PIL Image."""
    try:
        url = f"http://localhost:8002/verify?token={token}"
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        if hasattr(img, 'convert'):
            return img.convert('RGB')
        else:
            pil_img = Image.new('RGB', img.size, 'white')
            pil_img.paste(img)
            return pil_img
    except Exception as e:
        print(f"QR Error: {e}")
        return Image.new('RGB', (200, 200), 'red')


def get_mock_analysis():
    """Return random mock analysis."""
    analyses = [
        {"has_tumor": True, "tumor_type": "Glioma", "size": "1.2 cm", "location": "Right occipital lobe", "confidence": 0.92, "analysis_details": {"anomalous_regions": 2, "edge_complexity": 151, "tumor_score": 0.85, "region_intensities": [220.39, 158.87, 210.12, 176.93, 134.04, 160.1, 176.74, 124.37]}},
        {"has_tumor": True, "tumor_type": "Meningioma", "size": "0.8 cm", "location": "Left temporal lobe", "confidence": 0.88, "analysis_details": {"anomalous_regions": 1, "edge_complexity": 98, "tumor_score": 0.72, "region_intensities": [210.2, 145.5, 198.1, 165.3, 125.8, 152.9, 168.5, 118.2]}},
        {"has_tumor": False, "tumor_type": None, "size": None, "location": None, "confidence": 0.95, "analysis_details": {"anomalous_regions": 0, "edge_complexity": 45, "tumor_score": 0.12, "region_intensities": [180.5, 175.2, 178.9, 172.1, 176.3, 174.8, 179.2, 173.5]}}
    ]
    return random.choice(analyses)


def process_scan(file):
    """Main processing function."""
    if not file:
        return None, None, None, "❌ No file"
    
    try:
        # Get file path
        fpath = file.name if hasattr(file, 'name') else str(file)
        
        # Generate token and QR
        token = str(uuid.uuid4())[:16]
        qr_img = generate_qr_image(token)
        
        # Get analysis
        analysis = get_mock_analysis()
        
        # Generate PDFs
        out = str(Path(__file__).parent)
        report = generate_report(analysis, out_dir=out)
        prescrip = generate_prescription(analysis, patient_id=token[:8].upper(), out_dir=out)
        
        conf = analysis.get('confidence', 0)
        conf_str = f"{round(conf*100, 1)}%" if isinstance(conf, (int,float)) else "N/A"
        
        msg = (
            f"✅ **Reports Generated**\n\n"
            f"📄 Scan: {Path(report).name}\n"
            f"💊 Prescription: {Path(prescrip).name}\n"
            f"🔐 Token: {token}\n\n"
            f"**Results:**\n"
            f"• Tumor: {'Yes' if analysis.get('has_tumor') else 'No'}\n"
            f"• Type: {analysis.get('tumor_type', 'N/A')}\n"
            f"• Size: {analysis.get('size', 'N/A')}\n"
            f"• Location: {analysis.get('location', 'N/A')}\n"
            f"• Confidence: {conf_str}"
        )
        
        return report, prescrip, qr_img, msg
    except Exception as e:
        return None, None, None, f"❌ Error: {str(e)}"


# Create interface
demo = gr.Interface(
    fn=process_scan,
    inputs=gr.File(label="📤 Upload Brain Scan", file_types=["image"]),
    outputs=[
        gr.File(label="📄 Scan Report"),
        gr.File(label="💊 Prescription"),
        gr.Image(label="🔐 QR Code"),
        gr.Textbox(label="📋 Status", lines=6),
    ],
    title="🔐 Secure Brain Scan Report with QR",
    description="Upload scan → Get instant reports & QR code",
    theme=gr.themes.Soft(),
)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("GRADIO_PORT", "7865"))
    print(f"\n🚀 Chatbot: http://127.0.0.1:{port}")
    print(f"✅ Scan → Reports in seconds\n")
    demo.launch(share=False, server_name="127.0.0.1", server_port=port, show_error=True)
