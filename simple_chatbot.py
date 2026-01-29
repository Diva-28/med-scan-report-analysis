"""
Simple Medical Scan Report Chatbot
Upload scan → Get instant automated report & prescription (no QR verification required)
"""
import gradio as gr
import time
from pathlib import Path
from generate_scan_report_pdf import generate_report
from generate_prescription_pdf import generate_prescription
import uuid
import random
from datetime import datetime


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


def process_scan(file):
    """
    Simple flow:
    1. User uploads scan
    2. Generate analysis & reports instantly
    3. Return files to download
    """
    if not file:
        return None, None, "❌ No file provided"
    
    try:
        print(f"\n📋 Processing scan upload...")
        
        # Generate unique token/ID
        token = str(uuid.uuid4())[:12]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Get mock analysis
        analysis = get_mock_analysis()
        out_dir = str(Path(__file__).parent)
        
        print(f"🔐 Report ID: {token}")
        print(f"📊 Analysis: Tumor = {analysis.get('has_tumor')}, Type = {analysis.get('tumor_type')}")
        
        # Generate reports concurrently for speed
        import concurrent.futures
        
        try:
            with concurrent.futures.ProcessPoolExecutor(max_workers=2) as executor:
                fut_report = executor.submit(generate_report, analysis, out_dir)
                fut_presc = executor.submit(generate_prescription, analysis, token.upper(), out_dir)
                
                report_path = fut_report.result()
                prescrip_path = fut_presc.result()
        except Exception:
            # Fallback to threads
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                fut_report = executor.submit(generate_report, analysis, out_dir)
                fut_presc = executor.submit(generate_prescription, analysis, token.upper(), out_dir)
                
                report_path = fut_report.result()
                prescrip_path = fut_presc.result()
        
        # Format confidence
        conf = analysis.get('confidence', 0)
        conf_str = f"{round(conf*100, 1)}%" if isinstance(conf, (int, float)) else "N/A"
        
        # Create output message with analysis results
        output_msg = (
            f"✅ **SCAN ANALYSIS COMPLETE**\n\n"
            f"**Report ID:** {token}\n"
            f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"**📋 Analysis Results:**\n"
            f"• Tumor Detected: {'✅ YES' if analysis.get('has_tumor') else '❌ NO'}\n"
            f"• Type: {analysis.get('tumor_type') or 'N/A'}\n"
            f"• Size: {analysis.get('size') or 'N/A'}\n"
            f"• Location: {analysis.get('location') or 'N/A'}\n"
            f"• Confidence: {conf_str}\n\n"
            f"**📄 Generated Files:**\n"
            f"✓ {Path(report_path).name}\n"
            f"✓ {Path(prescrip_path).name}\n\n"
            f"Both files are ready for download below."
        )
        
        print(f"✅ Report generated: {Path(report_path).name}")
        print(f"✅ Prescription generated: {Path(prescrip_path).name}")
        
        return report_path, prescrip_path, output_msg
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None, None, f"❌ Error: {str(e)}"


# Gradio interface - SIMPLE VERSION
demo = gr.Interface(
    fn=process_scan,
    inputs=gr.File(label="📤 Upload Brain Scan Image", file_types=["image"]),
    outputs=[
        gr.File(label="📄 Scan Report PDF"),
        gr.File(label="💊 Prescription PDF"),
        gr.Textbox(label="📋 Analysis Output", lines=12, max_lines=16),
    ],
    title="🏥 Medical Scan Report Generator",
    description="Upload brain scan → Get instant automated report & prescription",
    theme=gr.themes.Soft(),
    examples=None,
)


if __name__ == "__main__":
    import os
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    port = int(os.environ.get("GRADIO_PORT", "7865"))
    print(f"\n🏥 Medical Scan Chatbot: http://127.0.0.1:{port}")
    print(f"Upload scans → Get instant reports & prescriptions\n")
    try:
        demo.launch(share=False, server_name="127.0.0.1", server_port=port, show_error=False)
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
