from tumor_analyzer import analyze_tumor, reject

def analyze_scan_local(file):
    # Backward compatibility wrapper
    return analyze_tumor(file)


def reject(reason, message):
    return {
        "has_tumor": False,
        "tumor_type": reason,
        "size": "N/A",
        "location": "N/A",
        "confidence": 0.0,
        "analysis_details": {
            "message": message
        }
    }
