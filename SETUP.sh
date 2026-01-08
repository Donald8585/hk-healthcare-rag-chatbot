#!/bin/bash
# Quick Setup Script for HK Healthcare RAG Chatbot
# Run this after downloading all files

echo "🚀 Setting up HK Healthcare RAG Chatbot..."
echo ""

# 1. Move files to project
echo "📁 Step 1: Organizing files..."
mv frontend.py ~/OneDrive/文件/hk-health-rag/
mv Dockerfile ~/OneDrive/文件/hk-health-rag/
mv cloudbuild.yaml ~/OneDrive/文件/hk-health-rag/
mv .gcloudignore ~/OneDrive/文件/hk-health-rag/
mv DEPLOYMENT.md ~/OneDrive/文件/hk-health-rag/
mv README_FULL.md ~/OneDrive/文件/hk-health-rag/README.md

# Replace app.py with monitoring version
mv app_with_monitoring.py ~/OneDrive/文件/hk-health-rag/app.py

cd ~/OneDrive/文件/hk-health-rag/

# 2. Update requirements
echo "📦 Step 2: Updating requirements.txt..."
echo "streamlit==1.41.1" >> requirements.txt
pip install streamlit

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo ""
echo "1. Test Streamlit UI:"
echo "   streamlit run frontend.py"
echo ""
echo "2. Start backend (if not running):"
echo "   uvicorn app:app --port 8000"
echo ""
echo "3. Test Docker build:"
echo "   docker build -t hk-healthcare-rag ."
echo ""
echo "4. Deploy to GCP (optional):"
echo "   gcloud builds submit --config cloudbuild.yaml"
echo ""
echo "5. Commit to GitHub:"
echo "   git add ."
echo "   git commit -m 'Add Streamlit UI, Docker, monitoring, and GCP deployment'"
echo "   git push"
echo ""
echo "🎉 Your RAG chatbot is production-ready!"
