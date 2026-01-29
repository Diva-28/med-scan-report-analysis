# Chatbot wrapper for your scan analyzer

This folder contains a small Gradio app that wraps the `analyze_scan` function from `main.py` and exposes a web UI and a public shareable link.

Files created:

- `gradio_app.py` — Gradio UI; run this to get a public link (temporary) and a local link.
- `requirements.txt` — minimal dependencies for the demo.

How to run (Windows PowerShell):

```powershell
cd $env:USERPROFILE\Downloads
python -m pip install -r requirements.txt
python gradio_app.py
```

When you run `gradio_app.py` it will print two URLs in the terminal: a local URL (http://127.0.0.1:7860 by default) and a public "share" URL (if `share=True` is successful) that you can give to anyone.

Notes / next steps:

- The Gradio app imports `analyze_scan` from `main.py`, which is already in this folder. That function currently returns placeholder results — replace with your CNN inference code.
- If you prefer to keep the FastAPI server (`main.py`) running and have Gradio call the POST `/upload` endpoint instead, I can provide an alternate `gradio_app_api.py` that uploads the file to the FastAPI endpoint instead of importing `analyze_scan` directly.
- To create a persistent public deployment consider deploying to Hugging Face Spaces, Railway, or a small cloud VM and configuring a proper model backend.
