"""
GARCH Trading Bot - Cloud Function
===================================

EDUCATIONAL DEMO - NOT FOR ACTUAL TRADING

This Cloud Function demonstrates automated volatility prediction using GARCH models.
It is designed to showcase CI/CD pipelines and ML deployment on GCP.

Purpose:
- Educational demonstration of econometric models
- Proof-of-concept for automated ML workflows
- Example of serverless data pipelines on GCP

Data Source: Yahoo Finance public API (free, no authentication required)
Model: GARCH(1,1) for volatility forecasting
Storage: Google BigQuery

NOT intended for: Cryptocurrency trading, mining, or financial advice
"""

import os
import json
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import numpy as np
from arch import arch_model
from google.cloud import bigquery

def garch_trading_bot(request):
    """Cloud Function to run GARCH volatility prediction every 5 minutes"""
    
    # Configuration
    ASSET = "BTC-USD"
    PROJECT_ID = "travel-recomender"
    DATASET_ID = "trading_bot"
    TABLE_ID = "garch_predictions"
    
    try:
        # 1. Fetch recent price data (last 30 days for sufficient history)
        print(f"Fetching data for {ASSET}...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        ticker = yf.Ticker(ASSET)
        data = ticker.history(start=start_date, end=end_date, interval="1h")
        
        if len(data) < 100:
            raise ValueError(f"Insufficient data: only {len(data)} points")
        
        # 2. Calculate returns
        data['returns'] = 100 * data['Close'].pct_change()
        data = data.dropna()
        
        current_price = float(data['Close'].iloc[-1])
        
        # 3. Fit GARCH(1,1) model
        print("Fitting GARCH model...")
        model = arch_model(data['returns'], vol='Garch', p=1, q=1)
        model_fitted = model.fit(disp='off')
        
        # 4. Forecast volatility for next period
        forecast = model_fitted.forecast(horizon=1)
        predicted_volatility = float(np.sqrt(forecast.variance.values[-1, 0]))
        
        # 5. Generate trading signal based on volatility
        # High volatility = opportunity (but risky)
        # We'll use a simple threshold approach
        volatility_threshold_high = 3.0  # Above this = SELL (too risky)
        volatility_threshold_low = 1.5   # Below this = BUY (stable)
        
        if predicted_volatility > volatility_threshold_high:
            signal = "SELL"
        elif predicted_volatility < volatility_threshold_low:
            signal = "BUY"
        else:
            signal = "HOLD"
        
        # 6. Prepare data for BigQuery
        row = {
            "timestamp": datetime.utcnow().isoformat(),
            "asset": ASSET,
            "current_price": current_price,
            "predicted_volatility": predicted_volatility,
            "signal": signal,
            "model_params": json.dumps({
                "omega": float(model_fitted.params['omega']),
                "alpha": float(model_fitted.params['alpha[1]']),
                "beta": float(model_fitted.params['beta[1]']),
                "aic": float(model_fitted.aic),
                "bic": float(model_fitted.bic)
            })
        }
        
        # 7. Insert into BigQuery
        print(f"Inserting to BigQuery: {signal} signal, volatility={predicted_volatility:.2f}")
        client = bigquery.Client(project=PROJECT_ID)
        table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
        errors = client.insert_rows_json(table_ref, [row])
        
        if errors:
            raise Exception(f"BigQuery insert errors: {errors}")
        
        # 8. Return response
        response = {
            "status": "success",
            "timestamp": row["timestamp"],
            "asset": ASSET,
            "price": current_price,
            "volatility": predicted_volatility,
            "signal": signal
        }
        
        print(f"Success: {response}")
        return (response, 200)
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(error_msg)
        return ({"status": "error", "message": error_msg}, 500)
