# Deployment Guide

## Deploy on HuggingFace Spaces

1. **Create a new Space** on HuggingFace
   - Go to https://huggingface.co/spaces
   - Click "Create new Space"
   - Choose Streamlit as SDK

2. **Push your code**
   ```bash
   git clone https://huggingface.co/spaces/your-username/querymind
   cd querymind
   git remote add origin https://huggingface.co/spaces/your-username/querymind.git
   git push -u origin main
   ```

3. **Set secrets**
   - Go to Space Settings → Secrets
   - Add `OPENAI_API_KEY` or `GROQ_API_KEY`

4. **Configure Streamlit**
   - Create `.streamlit/config.toml` in your repo:
   ```toml
   [server]
   headless = true
   port = 7860
   
   [theme]
   primaryColor = "#0066cc"
   backgroundColor = "#ffffff"
   secondaryBackgroundColor = "#f0f2f6"
   textColor = "#262730"
   ```

5. **Run locally first to test**
   ```bash
   streamlit run app.py
   ```

The space will automatically restart when you push changes.

## Local Deployment

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API key
streamlit run app.py
```

Visit `http://localhost:8501` to use QueryMind.
