# 🔐 Secure Medical AI Scan Report Chatbot with QR Verification

## ⚡ Quick Start

Your secure medical chatbot is now **LIVE** with QR code verification for Expo Go mobile app scanning.

### 🌐 **Access the Chatbot:**
```
http://127.0.0.1:7865
```

---

## 📱 **How It Works:**

### **Step-by-Step Flow:**

1. **Open the Chatbot**
   - Visit: `http://127.0.0.1:7865` in your web browser

2. **Upload a Brain Scan Image**
   - Click "Upload Brain Scan Image"
   - Select any JPG/PNG image (brain scan recommended)

3. **Get QR Code**
   - A unique QR code will be generated
   - Shows verification URL and token


4. **Scan with Expo Go (Phone)**
   - Open **Expo Go** app on your phone
   - Tap the QR scanner icon (camera)
   - Point phone camera at the QR code on screen
   - Wait for link to load in Expo Go

5. **Grant Permission**
   - Expo Go will ask for permission
   - Tap "Allow" or "Approve"
   - This verifies your identity

6. **Get PDFs Automatically**
   - Once scanned and approved:
     - 📄 **Scan Report PDF** generated
     - 💊 **Prescription PDF** generated
   - Both files appear as downloadable buttons
   - Status shows "✅ Reports Generated Successfully"

---

## 🔧 **System Architecture:**

### **Running Services:**

1. **Gradio Chatbot** (Port 7865)
   - Web interface for image upload
   - QR code display
   - PDF download buttons

2. **FastAPI Verification Server** (Port 8001)
   - Handles QR scan verification
   - Generates verification tokens
   - Tracks approval status

3. **PDF Generation Engines**
   - Scan Report Generator
   - Prescription Form Generator

---

## 📂 **Generated Files:**

All PDFs save to: `c:\Users\kanimozhi\Downloads\chatbot\`

**Examples:**
- `scan_report_20251111_220340.pdf`
- `prescription_20251111_220340.pdf`

---

## 🎯 **Features:**

✅ **QR Code Verification** - Secure mobile-to-web verification  
✅ **Expo Go Integration** - Works with popular mobile app  
✅ **Professional PDFs** - Medical-grade formatting  
✅ **Two-Factor Approval** - Upload + Mobile scan required  
✅ **Fast Processing** - Reports within 30 seconds of scan  
✅ **Unique Tokens** - Each upload gets unique token/QR  
✅ **Timeout Protection** - 5-minute verification window  

---

## 🚀 **Restart Instructions:**

If you need to restart the services:

### Terminal 1 - Verification Server (Port 8001):
```powershell
cd c:\Users\kanimozhi\Downloads\chatbot
python -m uvicorn verification_server:app --host 0.0.0.0 --port 8001
```

### Terminal 2 - Chatbot (Port 7865):
```powershell
cd c:\Users\kanimozhi\Downloads\chatbot
$env:GRADIO_PORT=7865
python qr_verified_app.py
```

---

## 📋 **Files in This System:**

- `qr_verified_app.py` - Main Gradio chatbot with QR flow
- `verification_server.py` - FastAPI endpoint for QR verification
- `generate_scan_report_pdf.py` - Clinical scan report generator
- `generate_prescription_pdf.py` - Prescription form generator

---

## ❓ **Troubleshooting:**

**Q: QR code not displaying?**
- A: Refresh the browser page or re-upload image

**Q: Expo Go can't scan QR?**
- A: Ensure phone is connected to same WiFi as PC
- Make sure brightness is good

**Q: "Verification timeout" error?**
- A: Scan must happen within 5 minutes of upload
- Try uploading again for a new QR code

**Q: Port already in use?**
- A: Change port in command (e.g., `GRADIO_PORT=7866`)

---

## 🔐 **Security Notes:**

- Each QR code is unique (UUID token)
- Tokens expire after 5 minutes
- One-time use only per token
- Mobile verification required before PDF generation
- No PDFs generated without QR scan approval

---

## 📊 **System Status:**

| Service | Port | Status | URL |
|---------|------|--------|-----|
| Gradio Chatbot | 7865 | ✅ Running | http://127.0.0.1:7865 |
| Verification API | 8001 | ✅ Running | http://localhost:8001 |

---

## 🎉 **Ready to Use!**

**Open your browser and visit:**
```
http://127.0.0.1:7865
```

Upload a scan → Get QR → Scan with Expo Go on your phone → Download secure PDFs! 🚀
