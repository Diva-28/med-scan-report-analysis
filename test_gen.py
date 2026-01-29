import time
from generate_scan_report_pdf import generate_report
from generate_prescription_pdf import generate_prescription
analysis = {
    "has_tumor": True,
    "tumor_type": "Glioma",
    "size": "1.2 cm",
    "location": "Right occipital lobe",
    "confidence": 0.92,
    "analysis_details": {"anomalous_regions":2, "edge_complexity":151, "tumor_score":0.85, "region_intensities":[220,158,210]}
}
start = time.time()
report = generate_report(analysis, out_dir='.')
mid = time.time()
presc = generate_prescription(analysis, patient_id='TESTID', out_dir='.')
end = time.time()
print('report time:', round(mid-start,3))
print('presc time: ', round(end-mid,3))
print('total: ', round(end-start,3))
print('report file:', report)
print('presc file:', presc)
