# GARCH Trading Bot - EDUCATIONAL DEMO

> **⚠️ DISCLAIMER: This is an EDUCATIONAL project for demonstrating CI/CD pipelines and ML model deployment.**  
> **This is NOT for actual cryptocurrency trading or mining.**  
> **This is a proof-of-concept to showcase automated ML workflows on GCP.**

## Purpose
This project demonstrates:
- Automated GARCH volatility prediction models
- Cloud Functions deployment
- BigQuery data storage
- Cloud Scheduler for periodic execution
- **CI/CD best practices for ML pipelines**

## What It Does
Every 5 minutes (configurable), this Cloud Function:
1. Fetches Bitcoin price data from **public Yahoo Finance API** (free, no auth required)
2. Fits a GARCH(1,1) econometric model to predict price volatility
3. Generates hypothetical trading signals (educational only)
4. Stores predictions in BigQuery for analysis
5. **NEW**: Sends automated alerts via Telegram when profitable
6. **NEW**: Generates AI-powered economic analysis reports using Gemini

## 🤖 Interactive Telegram Bot

The bot responds to commands in real-time:
- `/reporte` - Generate AI-powered economic analysis report instantly
- `/stats` - View quick statistics from the last 24 hours
- `/ayuda` - Show available commands

**See [BOT_GUIDE.md](BOT_GUIDE.md) for complete bot documentation.**

## Architecture
```
Cloud Scheduler (every 5 min)
    ↓
Cloud Function (Python)
    ↓
Yahoo Finance API (public, free)
    ↓
GARCH Model Training
    ↓
BigQuery (predictions storage)
```

## Files
- `main.py` - Cloud Function entry point with GARCH logic
- `requirements.txt` - Python dependencies
- `.gcloudignore` - Files to exclude from deployment

## Setup

### 1. Create BigQuery Resources
```bash
# Dataset
bq mk --dataset --location=us-east1 travel-recomender:trading_bot

# Table
bq mk --table travel-recomender:trading_bot.garch_predictions \
  timestamp:TIMESTAMP,asset:STRING,current_price:FLOAT64,predicted_volatility:FLOAT64,signal:STRING,model_params:JSON
```

### 2. Configure Telegram Bot & AI Reports

```bash
# Set up environment variables
export GEMINI_API_KEY='your-gemini-api-key'
export TELEGRAM_BOT_TOKEN='your-bot-token'
export TELEGRAM_CHAT_ID='your-chat-id'

# Test Telegram connection
./setup_telegram.sh test

# Deploy with all credentials
./deploy_with_ai.sh

# Configure webhook for bot commands
./setup_webhook.sh
```

**📚 Detailed setup instructions:** [TELEGRAM_FIX.md](TELEGRAM_FIX.md)

### 3. Deploy Cloud Function

**Option A: With Telegram & AI (Recommended)**
```bash
./deploy_with_ai.sh
```

**Option B: Manual deployment**
```bash
gcloud functions deploy garch-trading-bot \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point garch_trading_bot \
  --region us-east1 \
  --memory 512MB \
  --timeout 540s
```

### 4. Setup Scheduler (Every 5 Minutes)
```bash
gcloud scheduler jobs create http garch-bot-scheduler \
  --schedule "*/5 * * * *" \
  --uri "https://us-east1-travel-recomender.cloudfunctions.net/garch-trading-bot" \
  --http-method POST \
  --location us-east1
```

## Testing
```bash
# Manual trigger
curl -X POST https://us-east1-travel-recomender.cloudfunctions.net/garch-trading-bot

# Check BigQuery
bq query --use_legacy_sql=false \
  'SELECT * FROM `travel-recomender.trading_bot.garch_predictions` ORDER BY timestamp DESC LIMIT 10'
```

## Technologies
- **GARCH Models**: `arch` library for volatility forecasting
- **Data Source**: `yfinance` (Yahoo Finance public API)
- **Storage**: Google BigQuery
- **Compute**: Google Cloud Functions (serverless)
- **Scheduling**: Google Cloud Scheduler

## Educational Note
This project is designed to teach:
- Time series econometric modeling
- Serverless ML deployment
- Automated data pipelines
- GCP cloud services integration

**Not intended for:** Real trading, financial advice, or cryptocurrency mining.
