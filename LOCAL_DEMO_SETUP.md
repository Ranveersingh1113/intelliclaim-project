# IntelliClaim - Local Demo Setup Guide

This guide will help you run IntelliClaim locally for your demo tomorrow.

## ⏱️ Quick Setup (15 minutes)

### Step 1: Backend Setup

1. **Navigate to backend directory**:
```bash
cd backend
```

2. **Create virtual environment** (if not already done):
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**:

Create a `.env` file in the `backend` directory:
```env
# API Keys (Required)
AIMLAPI_KEY=your_aimlapi_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Environment
ENVIRONMENT=development

# Port (Optional - defaults to 8000)
PORT=8000
```

**To get API keys:**
- **AIMLAPI_KEY**: Get from https://aimlapi.com
- **GOOGLE_API_KEY**: Get from https://makersuite.google.com/app/apikey

5. **Start the backend server**:
```bash
python chatgpt_app.py
```

Backend will be available at: **http://localhost:8000**

✅ **Verify it's working**: Open http://localhost:8000/docs in your browser

---

### Step 2: Frontend Setup

1. **Navigate to frontend directory** (in a new terminal):
```bash
cd frontend
```

2. **Install dependencies**:
```bash
npm install
```

3. **Start the frontend**:
```bash
npm start
```

Frontend will automatically open at: **http://localhost:3000**

---

## 🎯 Running the Demo

Once both servers are running:

1. **Frontend** is at: http://localhost:3000
2. **Backend API** is at: http://localhost:8000
3. **API Docs** at: http://localhost:8000/docs

### Demo Flow:

1. **Open the frontend** in your browser
2. **Upload a sample document** (use one of the PDFs in `backend/uploads/`)
3. **Ask a query** like:
   - "What is the waiting period for cataract surgery?"
   - "Is maternity covered in this policy?"
   - "What are the sub-limits for room rent?"

---

## 🛠️ Troubleshooting

### Issue: "GOOGLE_API_KEY environment variable not set"
**Solution**: Make sure you created the `.env` file in the `backend` directory with your Google API key.

### Issue: "Module not found" errors
**Solution**: 
```bash
cd backend
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Issue: Frontend can't connect to backend
**Solution**: 
1. Verify backend is running on http://localhost:8000
2. Check that `frontend/src/config/api.js` points to `http://localhost:8000` (it should by default)
3. Check browser console for CORS errors

### Issue: PyTorch installation fails
**Solution**: Install CPU-only PyTorch separately:
```bash
pip install torch==2.1.0+cpu --index-url https://download.pytorch.org/whl/cpu
```

---

## 📦 Sample Documents Available

You have sample documents in `backend/uploads/`:
- `BAJHLIP23020V012223.pdf`
- `CHOTGDP23004V012223.pdf`
- `EDLHLGA23009V012223.pdf`
- `ICIHLIP22012V012223.pdf`
- `sample_policy.pdf`

**Tip**: Use these for your demo!

---

## 🚀 Alternative: Quick Start Script (Windows)

Create `start-demo.bat` in project root:

```batch
@echo off
echo Starting IntelliClaim Demo...

echo Starting Backend...
start cmd /k "cd backend && venv\Scripts\activate && python chatgpt_app.py"

timeout /t 5

echo Starting Frontend...
start cmd /k "cd frontend && npm start"

echo Both servers starting...
```

---

## ⚠️ Important Notes

1. **API Keys Required**: You need both AIMLAPI_KEY and GOOGLE_API_KEY to run the full system
2. **Local Only**: This runs locally and doesn't affect your AWS deployment
3. **Sample Data**: Use the PDF files in `backend/uploads/` for your demo
4. **No Internet**: The AI features won't work without internet connection

---

## 🎉 Ready for Demo!

Everything should be working now. Test it with:
- Visit: http://localhost:3000
- Upload a sample PDF
- Ask an insurance-related question

**Good luck with your demo tomorrow!** 🚀

