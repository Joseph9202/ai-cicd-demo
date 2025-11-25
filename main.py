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
import requests
import google.generativeai as genai

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

def send_telegram_alert(message):
    """Send alert via Telegram Bot API"""
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    if not token or not chat_id:
        print("Telegram credentials not configured")
        return
        
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        requests.post(url, json=payload, timeout=10)
        print("Telegram alert sent")
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}")

def send_whatsapp_alert(message):
    """Send alert via Evolution API (WhatsApp)"""
    api_url = os.environ.get('EVOLUTION_API_URL')
    api_key = os.environ.get('EVOLUTION_API_KEY')
    instance = os.environ.get('EVOLUTION_INSTANCE')
    number = os.environ.get('WHATSAPP_NUMBER')
    
    if not api_url or not api_key or not instance or not number:
        print("Evolution API credentials not configured")
        return
        
    try:
        # Evolution API endpoint for sending text
        url = f"{api_url}/message/sendText/{instance}"
        
        payload = {
            "number": number,
            "options": {
                "delay": 1200,
                "presence": "composing",
                "linkPreview": False
            },
            "textMessage": {
                "text": message
            }
        }
        
        headers = {
            "apikey": api_key,
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"WhatsApp alert sent: {response.status_code}")
    except Exception as e:
        print(f"Failed to send WhatsApp alert: {e}")

def check_and_alert(portfolio_stats, signal, current_price):
    """Check conditions and send alerts if profitable"""
    # Alert if return is positive OR if there's a new signal
    # For demo purposes, we'll alert on every run if there's a profit > 0.5%
    # In production you'd want to limit frequency
    
    if portfolio_stats['return_pct'] > 0.5:
        emoji = "🚀" if portfolio_stats['return_pct'] > 5 else "📈"
        
        msg = f"{emoji} *GARCH Bot - REPORTE DE GANANCIAS*\n\n"
        msg += f"💰 *Portafolio:* ${portfolio_stats['current']}\n"
        msg += f"📊 *Retorno:* +{portfolio_stats['return_pct']}%\n"
        msg += f"🆚 *vs HODL:* {portfolio_stats['vs_hodl']}%\n\n"
        msg += f"🏷️ *Señal Actual:* {signal}\n"
        msg += f"💲 *Precio BTC:* ${current_price:,.2f}"
        
        print(f"Sending alerts for profit: {portfolio_stats['return_pct']}%")
        send_telegram_alert(msg)
        send_whatsapp_alert(msg)

def generate_ai_report():
    """
    Generate AI-powered economic analysis report using Gemini
    Returns formatted report text
    """
    try:
        # Configure Gemini API
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            return "⚠️ GEMINI_API_KEY not configured"
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Fetch last 24 hours of data
        client = bigquery.Client(project=PROJECT_ID)
        query = f"""
        SELECT 
            timestamp,
            current_price,
            predicted_volatility,
            signal,
            model_params
        FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
        WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
        ORDER BY timestamp DESC
        """
        
        results = client.query(query).result()
        predictions = []
        
        for row in results:
            params = json.loads(row.model_params) if row.model_params else {}
            predictions.append({
                'timestamp': row.timestamp.isoformat(),
                'price': float(row.current_price),
                'volatility': float(row.predicted_volatility),
                'signal': row.signal,
                'alpha': params.get('alpha', 0),
                'beta': params.get('beta', 0)
            })
        
        if not predictions:
            return "📊 No hay datos suficientes para generar reporte (últimas 24h)"
        
        # Calculate statistics
        prices = [p['price'] for p in predictions]
        vols = [p['volatility'] for p in predictions]
        signals = [p['signal'] for p in predictions]
        
        price_change = ((prices[0] - prices[-1]) / prices[-1]) * 100
        avg_vol = np.mean(vols)
        vol_std = np.std(vols)
        persistence = np.mean([p['alpha'] + p['beta'] for p in predictions if p['alpha'] > 0])
        
        buy_pct = (signals.count('BUY') / len(signals)) * 100
        
        # Create prompt for Gemini
        prompt = f"""Eres un analista económico experto en modelos GARCH y volatilidad financiera.

Analiza los siguientes datos de BTC de las últimas 24 horas:

**Datos del Mercado:**
- Precio actual: ${prices[0]:,.2f}
- Cambio 24h: {price_change:+.2f}%
- Número de observaciones: {len(predictions)}

**Análisis de Volatilidad GARCH:**
- Volatilidad promedio predicha: {avg_vol:.4f}%
- Desviación estándar: {vol_std:.4f}%
- Persistencia (α+β): {persistence:.4f}
- Rango: {min(vols):.4f}% - {max(vols):.4f}%

**Señales de Trading:**
- BUY: {buy_pct:.1f}%
- SELL: {100-buy_pct:.1f}%

Genera un reporte conciso (máximo 200 palabras) que incluya:
1. **Resumen ejecutivo** del comportamiento del activo
2. **Interpretación económica** de la persistencia de volatilidad
3. **Evaluación de riesgos** basada en las métricas GARCH
4. **Outlook** para las próximas horas

Usa emojis apropiados y formato claro para Telegram."""

        # Generate AI response
        response = model.generate_content(prompt)
        ai_analysis = response.text
        
        # Format final report
        report = f"""📊 *REPORTE HORARIO - GARCH Trading Bot*
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC

{ai_analysis}

---
_Análisis generado por Gemini AI • Datos: últimas 24h_
"""
        
        return report
        
    except Exception as e:
        error_msg = f"❌ Error generando reporte AI: {str(e)}"
        print(error_msg)
        return error_msg

def calculate_portfolio_performance(predictions):
    """
    Simulate a $1000 portfolio following GARCH signals
    
    DISCLAIMER: PURELY EDUCATIONAL SIMULATION - NOT FINANCIAL ADVICE
    
    Args:
        predictions: List of prediction dicts with price, signal, timestamp
    
    Returns:
        dict: Portfolio statistics
    """
    if not predictions or len(predictions) < 2:
        return {
            "initial": 1000,
            "current": 1000,
            "return_pct": 0,
            "vs_hodl": 0,
            "trades": 0
        }
    
    # Sort by timestamp
    predictions = sorted(predictions, key=lambda x: x['timestamp'])
    
    # Initialize
    initial_capital = 1000
    cash = 0
    btc_holdings = 0
    last_signal = None
    trades = 0
    
    # Start with first prediction - assume BUY to compare fairly
    first_price = predictions[0]['price']
    btc_holdings = initial_capital / first_price
    cash = 0
    
    # Simulate trades based on signals
    for pred in predictions[1:]:
        current_price = pred['price']
        signal = pred['signal']
        
        # Execute trade if signal changed
        if signal != last_signal:
            if signal == 'SELL' and btc_holdings > 0:
                # Sell BTC to USD
                cash = btc_holdings * current_price
                btc_holdings = 0
                trades += 1
            elif signal == 'BUY' and cash > 0:
                # Buy BTC with USD
                btc_holdings = cash / current_price
                cash = 0
                trades += 1
        
        last_signal = signal
    
    # Calculate current portfolio value
    last_price = predictions[-1]['price']
    current_value = cash + (btc_holdings * last_price)
    
    # Calculate buy & hold for comparison
    hodl_btc = initial_capital / first_price
    hodl_value = hodl_btc * last_price
    
    return {
        "initial": initial_capital,
        "current": round(current_value, 2),
        "return_pct": round(((current_value - initial_capital) / initial_capital) * 100, 2),
        "vs_hodl": round(((current_value - hodl_value) / hodl_value) * 100, 2),
        "hodl_value": round(hodl_value, 2),
        "trades": trades
    }

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
        
        # Calculate portfolio performance
        portfolio_stats = calculate_portfolio_performance(predictions)
        
        # Check for alerts
        if predictions:
            latest = predictions[0]
            signal = latest['signal']
            current_price = latest['price']
            check_and_alert(portfolio_stats, signal, current_price)
        
        return jsonify({
            'status': 'success',
            'count': len(predictions),
            'predictions': predictions,
            'portfolio': portfolio_stats
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

@app.route('/report', methods=['POST', 'GET'])
def send_ai_report():
    """Generate and send AI-powered economic analysis report via Telegram"""
    try:
        print("Generating AI report...")
        
        # Generate report using Gemini AI
        report_text = generate_ai_report()
        
        # Send via Telegram
        send_telegram_alert(report_text)
        
        return jsonify({
            "status": "success",
            "message": "AI report sent to Telegram",
            "report_length": len(report_text)
        })
        
    except Exception as e:
        error_msg = f"Error generating/sending report: {str(e)}"
        print(error_msg)
        return jsonify({"status": "error", "message": error_msg}), 500


@functions_framework.http
def garch_trading_bot(request):
    """Main Cloud Function entry point - routes to Flask app"""
    with app.request_context(request.environ):
        return app.full_dispatch_request()
