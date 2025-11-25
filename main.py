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
from flask import Flask, render_template, jsonify
import functions_framework

# Create Flask app
app = Flask(__name__)

# Configuration
PROJECT_ID = "travel-recomender"
DATASET_ID = "trading_bot"
TABLE_ID = "garch_predictions"

def optimize_garch_params(returns, max_p=3, max_q=3):
    """
    Grid search to find optimal GARCH(p,q) parameters using AIC criterion
    
    Args:
        returns: Time series of returns
        max_p: Maximum p value to test
        max_q: Maximum q value to test
    
    Returns:
        tuple: (best_p, best_q)
    """
    best_aic = np.inf
    best_params = (1, 1)
    
    # Try different combinations of p and q
    for p in range(1, max_p + 1):
        for q in range(1, max_q + 1):
            try:
                model = arch_model(returns, vol='Garch', p=p, q=q)
                fitted = model.fit(disp='off', show_warning=False)
                
                if fitted.aic < best_aic:
                    best_aic = fitted.aic
                    best_params = (p, q)
                    print(f"  GARCH({p},{q}): AIC={fitted.aic:.2f} ✓")
            except:
                # Some combinations might not converge
                continue
    
    return best_params

@app.route('/')
def dashboard():
    """Serve the dashboard HTML"""
    return render_template('dashboard.html')

@app.route('/api/predictions')
def get_predictions():
    """API endpoint to fetch predictions from BigQuery"""
    try:
        client = bigquery.Client(project=PROJECT_ID)
        query = f"""
        SELECT 
            timestamp,
            asset,
            current_price,
            predicted_volatility,
            signal,
            model_params
        FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
        ORDER BY timestamp DESC
        LIMIT 100
        """
        
        results = client.query(query).result()
        predictions = []
        
        for row in results:
            predictions.append({
                'timestamp': row.timestamp.isoformat(),
                'asset': row.asset,
                'price': float(row.current_price),
                'volatility': float(row.predicted_volatility),
                'signal': row.signal,
                'params': row.model_params if row.model_params else {}
            })
        
        return jsonify({
            'status': 'success',
            'count': len(predictions),
            'predictions': predictions
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/run', methods=['POST', 'GET'])
def run_garch():
    """Run GARCH prediction - called by Cloud Scheduler"""
    
    ASSET = "BTC-USD"
    
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
        
        # 3. Fit GARCH model with automatic p,q selection
        print("Optimizing GARCH(p,q) parameters...")
        best_p, best_q = optimize_garch_params(data['returns'])
        print(f"Optimal parameters: GARCH({best_p},{best_q})")
        
        model = arch_model(data['returns'], vol='Garch', p=best_p, q=best_q)
        model_fitted = model.fit(disp='off')
        
        # 4. Forecast volatility for next period
        forecast = model_fitted.forecast(horizon=1)
        predicted_volatility = float(np.sqrt(forecast.variance.values[-1, 0]))
        
        # 5. Generate trading signal based on volatility
        volatility_threshold_high = 3.0
        volatility_threshold_low = 1.5
        
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
                "p": best_p,
                "q": best_q,
                "omega": float(model_fitted.params['omega']),
                "alpha": float(model_fitted.params[f'alpha[{best_q}]']) if f'alpha[{best_q}]' in model_fitted.params else float(model_fitted.params['alpha[1]']),
                "beta": float(model_fitted.params[f'beta[{best_p}]']) if f'beta[{best_p}]' in model_fitted.params else float(model_fitted.params['beta[1]']),
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
        return jsonify(response)
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(error_msg)
        return jsonify({"status": "error", "message": error_msg}), 500


@functions_framework.http
def garch_trading_bot(request):
    """Main Cloud Function entry point - routes to Flask app"""
    with app.request_context(request.environ):
        return app.full_dispatch_request()
