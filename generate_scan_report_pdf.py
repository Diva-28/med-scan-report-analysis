import json
from datetime import datetime
import uuid
import os
import statistics

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
except Exception as e:
    raise ImportError(
        "reportlab is required to run this script. Install with: pip install reportlab"
    )


def safe_get(d, key, default="Not Available"):
    return d.get(key, default) if isinstance(d, dict) else default


def compute_average_intensity(arr):
    try:
        if not arr:
            return "Not Available"
        return round(statistics.mean(arr), 2)
    except Exception:
        return "Not Available"


def generate_report(data: dict, out_dir: str = ".") -> str:
    # Fill missing top-level fields
    has_tumor = safe_get(data, "has_tumor", "Not Available")
    tumor_type = safe_get(data, "tumor_type", "Not Available")
    size = safe_get(data, "size", "Not Available")
    location = safe_get(data, "location", "Not Available")
    confidence = safe_get(data, "confidence", "Not Available")

    details = safe_get(data, "analysis_details", {})
    anomalous_regions = safe_get(details, "anomalous_regions", "Not Available")
    edge_complexity = safe_get(details, "edge_complexity", "Not Available")
    tumor_score = safe_get(details, "tumor_score", "Not Available")
    region_intensities = safe_get(details, "region_intensities", [])

    average_intensity = compute_average_intensity(region_intensities)

    now = datetime.now()
    timestamp_str = now.strftime("%Y%m%d_%H%M%S")
    human_dt = now.strftime("%Y-%m-%d %H:%M:%S")
    report_id = str(uuid.uuid4())[:8]
    patient_id = str(uuid.uuid4())[:8]

    filename = f"scan_report_{timestamp_str}.pdf"
    filepath = os.path.join(out_dir, filename)

    doc = SimpleDocTemplate(filepath, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()
    normal = styles["Normal"]
    heading = styles["Heading1"]

    elems = []

    # Header
    elems.append(Paragraph("AI-Powered Scan Analysis Report", ParagraphStyle(
        name="Title", fontSize=18, leading=22, alignment=1)))
    elems.append(Spacer(1, 12))

    meta_table_data = [
        ["Date & Time:", human_dt],
        ["Report ID:", report_id],
        ["Patient ID:", patient_id]
    ]
    meta_table = Table(meta_table_data, colWidths=[1.6 * inch, 4.4 * inch])
    meta_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.darkblue),
    ]))
    elems.append(meta_table)
    elems.append(Spacer(1, 18))

    # Summary
    elems.append(Paragraph("Summary", styles["Heading2"]))
    elems.append(Spacer(1, 6))

    tumor_detected_str = "Yes" if has_tumor is True else ("No" if has_tumor is False else "Not Available")
    confidence_pct = (f"{round(confidence * 100, 1)}%" if isinstance(confidence, (int, float)) else "Not Available")

    summary_table_data = [
        ["Tumor Detected:", tumor_detected_str],
        ["Tumor Type:", tumor_type],
        ["Tumor Size:", size],
        ["Tumor Location:", location],
        ["Confidence Level:", confidence_pct]
    ]
    summary_table = Table(summary_table_data, colWidths=[2.0 * inch, 4.0 * inch])
    summary_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elems.append(summary_table)
    elems.append(Spacer(1, 12))

    # Detailed Analysis
    elems.append(Paragraph("Detailed Analysis", styles["Heading2"]))
    elems.append(Spacer(1, 6))

    details_table_data = [
        ["Number of Anomalous Regions:", str(anomalous_regions)],
        ["Edge Complexity:", str(edge_complexity)],
        ["Tumor Score:", str(tumor_score)],
        ["Average Intensity:", str(average_intensity)]
    ]
    details_table = Table(details_table_data, colWidths=[2.5 * inch, 3.5 * inch])
    details_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    elems.append(details_table)
    elems.append(Spacer(1, 12))

    # AI Observation
    elems.append(Paragraph("AI Observation", styles["Heading2"]))
    elems.append(Spacer(1, 6))

    # craft observation sentence
    # Format confidence for sentence
    conf_for_sentence = (f"{round(confidence * 100)}%" if isinstance(confidence, (int, float)) else "an unknown confidence level")

    if isinstance(has_tumor, bool) and has_tumor and tumor_type != "Not Available" and location != "Not Available":
        obs = (f"The AI model detected a high-probability {tumor_type.lower()} in the {location} with {conf_for_sentence} confidence. "
               "Further clinical evaluation is recommended.")
    elif isinstance(has_tumor, bool) and not has_tumor:
        obs = "No tumor was detected by the AI model; however, clinical correlation is recommended."
    else:
        obs = "The scan was analyzed by the AI system. Some required fields were not available; clinical verification is recommended."

    elems.append(Paragraph(obs, normal))
    elems.append(Spacer(1, 24))

    # Footer note (exact required wording)
    footer = Paragraph(
        "<i>This report was auto-generated by an AI model for diagnostic assistance only.</i>",
        ParagraphStyle(name="Footer", fontSize=8, alignment=1, textColor=colors.grey)
    )
    elems.append(footer)

    # Build PDF
    doc.build(elems)

    return os.path.abspath(filepath)


if __name__ == "__main__":
    # Example usage with the JSON provided in the prompt
    example_json = {
        "has_tumor": True,
        "tumor_type": "Glioma",
        "size": "1.2 cm",
        "location": "Right occipital lobe",
        "confidence": 0.9,
        "analysis_details": {
            "anomalous_regions": 2,
            "edge_complexity": 151,
            "tumor_score": 1,
            "region_intensities": [220.39, 158.87, 210.12, 176.93, 134.04, 160.1, 176.74, 124.37]
        }
    }

    out_path = generate_report(example_json, out_dir=os.path.dirname(__file__))
    print(out_path)
