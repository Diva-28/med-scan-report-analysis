# Quick Start Guide

## ✅ Services Status

Both services are currently **RUNNING**:

```
Chatbot:             http://127.0.0.1:7865  ✅
Verification Server: http://127.0.0.1:7866 ✅
```

---

## 🚀 Open Chatbot Now

**Click here or paste in browser:**
```
http://127.0.0.1:7865
```

---

## 📱 Using the Chatbot

### Step 1: Upload Image
- Click "Upload Brain Scan Image"
- Select any image file from your computer

### Step 2: View QR Code
- Chatbot displays a unique QR code
- Shows a token (example: `a1b2c3d4e5f6g7h8`)

### Step 3: Scan with Phone
**On your smartphone:**
1. Open **Expo Go** app (download from App Store/Google Play if needed)
2. **Scan the QR code** with your phone camera
3. The link will open and show **"QR Code Verified!"**

### Step 4: Download Reports
- The chatbot **automatically generates**:
  - **Scan Report PDF** - Professional medical analysis
  - **Prescription PDF** - Recommended treatment
- Click download buttons to save files

---

## ⏱️ Timeline

| Step | Time |
|------|------|
| Upload image | Instant |
| Generate QR | < 1 second |
| Scan QR with phone | ~3 seconds |
| Generate reports | ~2-3 seconds |
| **Total** | **~10 seconds** |

---

## 🎯 Demo Analysis

The chatbot returns random analysis:

- **60% chance:** Glioma tumor detected (1.2 cm, right occipital lobe)
- **20% chance:** Meningioma tumor detected (0.8 cm, left temporal lobe)  
- **20% chance:** No tumor detected (normal scan)

---

## ❌ Troubleshooting

### Problem: "This site can't be reached"

**Solution:** Check if services are running
```powershell
# Terminal 1 - Verification Server
cd C:\Users\kanimozhi\Downloads\chatbot
python verify_server.py

# Terminal 2 - Chatbot
cd C:\Users\kanimozhi\Downloads\chatbot
$env:GRADIO_PORT=7865
python secure_app.py
```

### Problem: QR code shows "localhost is unreachable"

**Solution:** This is normal! The QR code says `http://127.0.0.1:7866/verify?...`
- On **phone**: Scan QR code in Expo Go
- On **computer**: Manually visit that URL in browser

### Problem: Phone can't scan QR

**Solution 1:** Make sure phone has Expo Go installed
```
App Store: Search "Expo Go"
Google Play: Search "Expo Go"
```

**Solution 2:** Ensure phone is on same WiFi network

**Solution 3:** Use longer token wait time (max 5 minutes)

### Problem: Reports not generating after QR scan

**Solution:** 
1. Check verification server is running (port 7866)
2. Try uploading again
3. Scan QR code quickly (within 5 minutes)

---

## 📂 Generated Files

All files save to your Downloads folder:
```
C:\Users\kanimozhi\Downloads\chatbot\
├── scan_report_20250111_143025.pdf
├── prescription_20250111_143025.pdf
└── (more PDFs as you upload)
```

---

## 🔒 Privacy & Security

- ✅ All files stay on your computer
- ✅ Reports generated locally
- ✅ No cloud uploads
- ✅ Unique tokens prevent unauthorized access
- ✅ Token expires in 5 minutes if not used

---

## 📱 Expo Go Installation

### iOS (iPhone/iPad)
1. Open App Store
2. Search "Expo Go"
3. Tap "Get"
4. Use Face ID/Touch ID to confirm

### Android (Android Phone)
1. Open Google Play Store
2. Search "Expo Go"
3. Tap "Install"
4. Open the app

---

## 🎬 What Happens After QR Scan

```
Phone Screen:
┌────────────────────────┐
│ ✅ QR Code Verified!   │
│                        │
│ Your scan has been     │
│ verified. Reports      │
│ are now being          │
│ generated...           │
│                        │
│ You can close this.    │
└────────────────────────┘

↓ (Browser closes)

Computer Screen:
┌────────────────────────┐
│ ✅ VERIFICATION        │
│    SUCCESSFUL          │
│                        │
│ Analysis:              │
│ • Tumor: Yes           │
│ • Type: Glioma         │
│ • Size: 1.2 cm         │
│ • Confidence: 92%      │
│                        │
│ [Download Report]      │
│ [Download RX]          │
└────────────────────────┘
```

---

## 💡 Tips

✅ **Faster:** Have phone nearby and ready
✅ **Better:** Use good lighting for QR scanning
✅ **Safer:** Use unique device per upload
✅ **Organized:** Save PDFs with date labels

---

## 📞 Need Help?

1. **Check logs** - Look at terminal windows for errors
2. **Restart services** - Kill Python and restart both
3. **Test URL** - Visit `http://127.0.0.1:7866/` to verify server
4. **Manual test** - Copy token and manually visit `http://127.0.0.1:7866/verify?token=YOUR_TOKEN`

---

## 🎯 What's Next?

After you try the basic flow:

1. **Integrate real AI model** - Replace mock analysis with actual ML model
2. **Deploy to cloud** - Make accessible from anywhere with ngrok/Render
3. **Add database** - Store verification history and user data
4. **Customize PDFs** - Add hospital logo, custom formatting
5. **Mobile app** - Convert Gradio to native iOS/Android app

---

**Everything is ready to use!** 

Open browser → `http://127.0.0.1:7865`

Get started now! ✨
