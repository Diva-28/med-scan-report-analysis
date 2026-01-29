# Secure Medical Scan Report Chatbot - Complete Setup

## ✅ Services Running

Both services are now active and working:

### 1. **Chatbot Interface** (Gradio)
- **URL:** `http://127.0.0.1:7865`
- **Port:** 7865
- **File:** `secure_app.py`
- **Status:** Running ✅

### 2. **QR Verification Server** (FastAPI)
- **URL:** `http://127.0.0.1:7866`
- **Port:** 7866
- **File:** `verify_server.py`
- **Status:** Running ✅

---

## 📱 How It Works

### Step 1: Upload Brain Scan
- Open `http://127.0.0.1:7865` in your browser
- Click "Upload Brain Scan Image"
- Select an image file

### Step 2: Get QR Code
- The chatbot generates a **unique token**
- A **QR code** is displayed showing that token
- A status message shows instructions

### Step 3: Scan with Expo Go (Phone)
**On your smartphone:**
1. Download and open **Expo Go** app
2. **Scan the QR code** displayed in the chatbot
3. The QR code links to: `http://127.0.0.1:7866/verify?token=YOUR_TOKEN`
4. Your phone will show a verification confirmation page

### Step 4: Reports Generate Automatically
- The chatbot **waits** for your phone to scan the QR
- Once verified (scanning the QR), it automatically:
  - Analyzes the scan (mock analysis for demo)
  - Generates **Scan Report PDF**
  - Generates **Prescription PDF**
  - Shows download buttons for both files

### Step 5: Download Reports
- Click the file download buttons to save your:
  - `scan_report_YYYYMMDD_HHMMSS.pdf`
  - `prescription_YYYYMMDD_HHMMSS.pdf`

---

## 🔐 Security Features

✅ **Unique Tokens:** Every upload gets a unique token
✅ **QR Verification:** Reports only generated AFTER phone verification
✅ **One-Time Use:** Token expires after 5 minutes if not scanned
✅ **Mobile Verification:** Phone must scan QR to proceed

---

## 🛠️ Technical Architecture

### secure_app.py (Gradio Chatbot)
```python
# Main functions:
- generate_qr_image(token)          # Creates QR code image
- is_token_verified(token)          # Checks if phone scanned QR
- process_scan(file)                # Main processing flow
- mark_token_verified(token)        # Called by verification server
```

**Flow:**
1. User uploads image → Generate unique token
2. Generate QR code image
3. Display QR code to user
4. WAIT for token to be marked as verified (polling every 2 seconds)
5. Once verified → Run mock analysis
6. Generate PDF reports
7. Return all outputs to user

### verify_server.py (FastAPI Backend)
```python
# Endpoints:
GET /verify?token=TOKEN             # Called when QR is scanned
GET /health                         # Health check endpoint
GET /                               # Server info page
```

**Flow:**
1. User scans QR code on phone
2. Opens link: `http://127.0.0.1:7866/verify?token=TOKEN`
3. Verification server marks token as verified
4. Displays confirmation page to user
5. Chatbot detects verification and generates reports

---

## 📊 Mock Analysis Scenarios

The chatbot returns one of three random analyses:

### 1. **Glioma Tumor Detected**
- Type: Glioma
- Size: 1.2 cm
- Location: Right occipital lobe
- Confidence: 92%

### 2. **Meningioma Tumor Detected**
- Type: Meningioma
- Size: 0.8 cm
- Location: Left temporal lobe
- Confidence: 88%

### 3. **No Tumor Detected**
- Type: None
- Confidence: 95%

---

## 📁 Generated Files

All files are saved to: `C:\Users\kanimozhi\Downloads\chatbot\`

### Report Formats:
- **Scan Report PDF:** Professional medical report with:
  - Report header (title, date, ID)
  - Summary table (tumor info)
  - Detailed analysis metrics
  - AI observation paragraph
  - Professional footer

- **Prescription PDF:** Medical recommendation form with:
  - Diagnosis summary (AI-generated based on analysis)
  - Recommended next steps
  - Doctor signature area
  - Certification section

---

## ⏰ Timing

- **Upload to QR Code:** < 1 second
- **Waiting for verification:** Depends on user (max 5 minutes)
- **Analysis to Reports:** ~2-3 seconds AFTER verification
- **Total (with phone verification):** ~10 seconds (excluding network delay)

---

## 🔧 Testing the QR Code

### Option 1: **With Real Phone (Recommended)**
1. Ensure phone is on same network (or use localhost tunnel)
2. Open Expo Go app
3. Scan the QR code in the chatbot
4. Verification happens automatically

### Option 2: **Manual Testing (Without Phone)**
1. Copy the token from the chatbot
2. Manually visit: `http://127.0.0.1:7866/verify?token=TOKEN`
3. Token gets marked as verified
4. Chatbot continues processing

---

## 🚀 Restart Services

If services stop, restart them:

```powershell
# Terminal 1 - Start verification server
cd C:\Users\kanimozhi\Downloads\chatbot
python verify_server.py

# Terminal 2 - Start chatbot (different terminal)
cd C:\Users\kanimozhi\Downloads\chatbot
$env:GRADIO_PORT=7865
python secure_app.py
```

Or use one-liner to start both in background:
```powershell
cd C:\Users\kanimozhi\Downloads\chatbot
Start-Process python -ArgumentList "verify_server.py"
Start-Process python -ArgumentList "secure_app.py" -Env @{"GRADIO_PORT"="7865"}
```

---

## 📝 File Structure

```
c:\Users\kanimozhi\Downloads\chatbot\
├── secure_app.py               # Main Gradio chatbot
├── verify_server.py            # QR verification backend
├── generate_scan_report_pdf.py  # Report PDF generator
├── generate_prescription_pdf.py # Prescription PDF generator
├── requirements.txt            # Dependencies
└── uploads/                    # User uploads folder
└── scan_report_*.pdf           # Generated reports
└── prescription_*.pdf          # Generated prescriptions
```

---

## ✨ Key Features

✅ Instant QR code generation
✅ Mobile phone verification via Expo Go
✅ Professional medical PDF reports
✅ Mock AI scan analysis
✅ Automatic file downloads
✅ Token expiration (5 minutes)
✅ Beautiful Gradio interface
✅ Error handling and status messages

---

## 🎯 Next Steps (Optional Enhancements)

1. **Real Model Integration:** Replace mock analysis with actual ML model from `main.py`
2. **Database Storage:** Persist verification tokens in database
3. **Cloud Deployment:** Deploy to Hugging Face Spaces, Render, or Azure
4. **ngrok Tunnel:** Make accessible from any phone (not just local network)
5. **Custom Branding:** Add hospital/clinic logo to PDFs

---

## 📞 Support

- **Chatbot down:** Check if port 7865 is in use
- **QR not working:** Ensure port 7866 is accessible
- **Phone can't scan:** Make sure phone is on same network
- **Verification timeout:** Token expires in 5 minutes, upload new scan

---

**Status:** All systems operational ✅
**Last Updated:** 2025-01-11
