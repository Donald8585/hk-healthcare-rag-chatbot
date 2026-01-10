# 🇭🇰 Hong Kong Setup Guide - NO CREDIT CARD NEEDED!

## 🎉 100% FREE Solution for Hong Kong Users

This guide is specifically for developers in Hong Kong who:
- ❌ Cannot access Groq (blocked)
- ❌ Cannot use OpenAI (needs US credit card)
- ✅ Want a FREE, production-ready RAG chatbot!

## 🔑 Step 1: Get FREE API Keys (5 minutes)

### HuggingFace Token (100% FREE Forever!)
1. Go to: https://huggingface.co/settings/tokens
2. Click "New token"
3. Name: "hk-healthcare-rag"
4. Type: Read
5. Click "Generate"
6. Copy token (starts with `hf_`)

**Rate Limits (FREE):**
- ~1000 API calls per hour
- Perfect for portfolio projects!

### Cohere API Key (FREE Tier - No Card!)
1. Go to: https://dashboard.cohere.com/api-keys
2. Sign up with email (NO credit card required!)
3. Automatically get FREE trial key
4. Copy your API key

**Rate Limits (FREE):**
- 100 embeds per minute
- 1000 embeds per month
- More than enough for demos!

## 📦 Step 2: Local Setup

### Install Dependencies
```bash
cd ~/path/to/hk-healthcare-rag-chatbot

# Install requirements
pip install -r requirements.txt
```

### Create .env File
```bash
# Copy template
cp .env.example .env

# Edit with your keys
nano .env
```

Add your real keys:
```
HUGGINGFACE_API_KEY=hf_your_actual_token_here
COHERE_API_KEY=your_actual_cohere_key_here
```

## 📄 Step 3: Prepare Your Data

### Add Healthcare Documents
```bash
# Create data folder
mkdir -p data

# Add your Hong Kong healthcare PDFs/TXT files
# Examples:
# - Hospital directories
# - Clinic information
# - Medical service guides
# - Healthcare FAQs
```

### Run Ingestion
```bash
python ingest_data.py
```

This creates `chroma_db/` folder with your embeddings.

**⏱️ Expected time:**
- 100 pages = ~2-3 minutes
- 500 pages = ~10-15 minutes

## 🧪 Step 4: Test Locally

```bash
# Create Streamlit secrets
mkdir -p .streamlit
cp secrets.toml.example .streamlit/secrets.toml

# Edit with your keys
nano .streamlit/secrets.toml

# Run the app
streamlit run streamlit_app.py
```

Visit http://localhost:8501 and test your chatbot!

## 🚀 Step 5: Deploy to Streamlit Cloud

### Push to GitHub
```bash
# Add files
git add .
git commit -m "Add HK Healthcare RAG chatbot with FREE APIs"
git push origin main

# Make sure .env is in .gitignore!
echo ".env" >> .gitignore
echo ".streamlit/secrets.toml" >> .gitignore
```

### Deploy on Streamlit
1. Go to: https://share.streamlit.io
2. Click "New app"
3. Select your repo: `Donald8585/hk-healthcare-rag-chatbot`
4. Main file: `streamlit_app.py`
5. Click "Advanced settings" → "Secrets"
6. Paste:
```toml
HUGGINGFACE_API_KEY = "hf_your_actual_token"
COHERE_API_KEY = "your_actual_cohere_key"
```
7. Click "Deploy"!

**⏱️ Deployment time:** 5-7 minutes

## 💰 Cost Breakdown

| Component | Cost | Notes |
|-----------|------|-------|
| HuggingFace LLM | $0/month | FREE forever! |
| Cohere Embeddings | $0/month | FREE tier = 1000/month |
| Streamlit Cloud | $0/month | Community tier |
| **TOTAL** | **$0/month** | 🎉 Completely FREE! |

## 🎯 Available Models (All FREE!)

**Recommended for RAG:**
- `mistralai/Mistral-7B-Instruct-v0.2` ⭐ BEST balance
- `HuggingFaceH4/zephyr-7b-beta` ⭐ Fast responses
- `meta-llama/Llama-2-7b-chat-hf` Good quality
- `google/flan-t5-xxl` Fastest but basic

## ⚡ Performance Expectations

**Response Times:**
- HuggingFace Inference: 2-5 seconds
- Cohere Embeddings: <1 second
- Total: ~3-6 seconds per query

**Not as fast as Groq, but:**
- ✅ 100% FREE
- ✅ No credit card
- ✅ Works in Hong Kong
- ✅ Perfect for portfolio!

## 🐛 Troubleshooting

### "Rate limit exceeded"
- Wait 1 minute and try again
- Switch to a different model
- Upgrade to HF PRO ($9/month) for unlimited

### "Model loading error"
- Some models take 20-30 seconds to "wake up"
- Be patient on first request
- Subsequent requests are faster

### "Cohere API error"
- Check your API key is correct
- Verify you haven't exceeded 1000 embeds/month
- Create a new account if needed (FREE!)

## 📊 Upgrade Options (Optional)

If you need more capacity later:

**HuggingFace PRO:** $9/month
- Unlimited API calls
- Faster inference
- Access to all models

**Cohere Production:** $0.0001 per embed
- Pay-as-you-go
- No monthly fees
- Still very cheap!

## 🎓 Interview Talking Points

"I deployed a production RAG chatbot using HuggingFace's serverless inference and Cohere embeddings, optimized for cost-effectiveness with zero monthly costs while maintaining sub-6-second response times. This demonstrates my ability to architect ML systems within budget constraints and navigate API limitations in different regions."

## 🇭🇰 Hong Kong Specific Notes

- ✅ Both APIs work perfectly in HK
- ✅ No VPN needed
- ✅ No payment method required
- ✅ Fully legal and compliant
- ✅ Fast enough for APAC region

## 📞 Support

If you hit issues:
1. Check HuggingFace status: https://status.huggingface.co
2. Cohere docs: https://docs.cohere.com
3. Streamlit community: https://discuss.streamlit.io

## ✨ You're Ready!

This setup gives you a production-grade RAG chatbot that:
- Costs $0/month
- Works in Hong Kong
- Needs no credit card
- Looks great on your portfolio!

Good luck! 🚀
