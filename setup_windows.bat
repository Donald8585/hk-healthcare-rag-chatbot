@echo off
echo ================================================
echo HK Healthcare RAG Chatbot - Windows Setup
echo ================================================
echo.

echo Step 1: Installing Python packages...
echo (This takes 2-3 minutes)
echo.

pip install --upgrade pip
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Installation failed!
    echo Try running as Administrator or check your internet connection.
    pause
    exit /b 1
)

echo.
echo ================================================
echo SUCCESS! All packages installed!
echo ================================================
echo.
echo Next steps:
echo 1. Get FREE API keys:
echo    - HuggingFace: https://huggingface.co/settings/tokens
echo    - Cohere: https://dashboard.cohere.com/api-keys
echo.
echo 2. Create .env file:
echo    copy .env.example .env
echo    notepad .env
echo.
echo 3. Add your documents to data/ folder
echo.
echo 4. Run: python ingest_data.py
echo.
pause
