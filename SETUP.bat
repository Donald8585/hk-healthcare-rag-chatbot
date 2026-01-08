@echo off
REM Quick Setup Script for HK Healthcare RAG Chatbot (Windows)
echo 🚀 Setting up HK Healthcare RAG Chatbot...
echo.

REM 1. Move files
echo 📁 Step 1: Organizing files...
move frontend.py %USERPROFILE%\OneDrive\文件\hk-health-rag\
move Dockerfile %USERPROFILE%\OneDrive\文件\hk-health-rag\
move cloudbuild.yaml %USERPROFILE%\OneDrive\文件\hk-health-rag\
move .gcloudignore %USERPROFILE%\OneDrive\文件\hk-health-rag\
move DEPLOYMENT.md %USERPROFILE%\OneDrive\文件\hk-health-rag\
move README_FULL.md %USERPROFILE%\OneDrive\文件\hk-health-rag\README.md
move app_with_monitoring.py %USERPROFILE%\OneDrive\文件\hk-health-rag\app.py

cd %USERPROFILE%\OneDrive\文件\hk-health-rag

REM 2. Update requirements
echo 📦 Step 2: Updating packages...
pip install streamlit

echo.
echo ✅ Setup complete!
echo.
echo 📋 Next steps:
echo.
echo 1. Test Streamlit UI:
echo    streamlit run frontend.py
echo.
echo 2. Start backend (if not running):
echo    uvicorn app:app --port 8000
echo.
echo 3. Commit to GitHub:
echo    git add .
echo    git commit -m "Add Streamlit UI, Docker, monitoring, and GCP deployment"
echo    git push
echo.
echo 🎉 Your RAG chatbot is production-ready!
pause
