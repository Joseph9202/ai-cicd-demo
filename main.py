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
from google.cloud import storage
from flask import Flask, render_template, jsonify, request, send_file
import functions_framework
import requests
import google.generativeai as genai
from pdf_generator import create_pdf_report
from vector_db import store_report, search_similar_reports, get_report_stats
from whatsapp_client import send_whatsapp_message, send_whatsapp_pdf, get_whatsapp_qr
from io import BytesIO

# Create Flask app
app = Flask(__name__)

# Configuration
PROJECT_ID = "travel-recomender"
DATASET_ID = "trading_bot"
TABLE_ID = "garch_predictions"
BUCKET_NAME = "travel-recomender-garch-reports"

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
        model = genai.GenerativeModel('gemini-pro-latest')
        
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
            # model_params is already a dict from BigQuery (JSON type)
            if row.model_params:
                params = row.model_params if isinstance(row.model_params, dict) else json.loads(row.model_params)
            else:
                params = {}
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
        
        # Create advanced prompt for Gemini
        prompt = f"""You are a senior quantitative analyst at a hedge fund, specializing in cryptocurrency volatility modeling and GARCH econometrics. Analyze the following BTC market data with depth and nuance.

**Market Data (Last 24h):**
- Current Price: ${prices[0]:,.2f} USD
- Price Movement: {price_change:+.2f}%
- Sample Size: {len(predictions)} observations
- Price Range: ${min(prices):,.2f} - ${max(prices):,.2f}

**GARCH Model Diagnostics:**
- Mean Predicted Volatility: {avg_vol:.4f}%
- Volatility Std Dev: {vol_std:.4f}%
- Persistence Coefficient (α+β): {persistence:.4f}
- Volatility Range: {min(vols):.4f}% - {max(vols):.4f}%
- Coefficient of Variation: {(vol_std/avg_vol)*100 if avg_vol > 0 else 0:.2f}%

**Trading Signal Distribution:**
- BUY signals: {buy_pct:.1f}%
- SELL signals: {signals.count('SELL')/len(signals)*100:.1f}%
- HOLD signals: {signals.count('HOLD')/len(signals)*100:.1f}%

**Your Analysis Must Include:**

1. **Market Regime Identification**: Is this a high/low volatility regime? Is volatility clustering present?

2. **Persistence Interpretation**: With α+β = {persistence:.4f}, what does this tell us about volatility shocks? Will volatility mean-revert quickly or slowly?

3. **Risk Assessment**: Given the current volatility distribution, quantify the risk exposure. Are we seeing heteroskedasticity? What's the tail risk?

4. **Actionable Intelligence**: Based on GARCH diagnostics, what specific trading strategy adjustments should be made? Be concrete and avoid generic advice.

5. **Market Context**: Connect these technical metrics to potential macro drivers or market microstructure effects.

**Style Requirements:**
- Be analytical, not descriptive
- Use precise econometric language
- Avoid repetitive phrases like "this suggests" or "we can see"
- Include specific numerical insights
- Maximum 250 words
- Use emojis sparingly and strategically
- Write in Spanish for Latin American audience

Generate a professional analysis that a PM would actually read and act on."""

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
        
        # Prepare metadata for PDF and vector DB
        metadata = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'price': prices[0],
            'volatility': avg_vol,
            'signal': signals[0],  # Latest signal
            'avg_volatility': avg_vol,
            'persistence': persistence,
            'num_predictions': len(predictions),
            'price_change_24h': price_change
        }
        
        return report, metadata
        
    except Exception as e:
        error_msg = f"❌ Error generando reporte AI: {str(e)}"
        print(error_msg)
        return error_msg, None

def get_top_volatile_cryptos(n=5):
    """
    Get top N most volatile cryptocurrencies in the last 7 days

    Returns:
        list: List of crypto symbols (e.g., ['BTC-USD', 'ETH-USD', ...])
    """
    # Popular cryptos to analyze
    cryptos = [
        'BTC-USD',   # Bitcoin
        'ETH-USD',   # Ethereum
        'BNB-USD',   # Binance Coin
        'SOL-USD',   # Solana
        'ADA-USD',   # Cardano
        'XRP-USD',   # Ripple
        'DOT-USD',   # Polkadot
        'MATIC-USD', # Polygon
        'LINK-USD',  # Chainlink
        'AVAX-USD',  # Avalanche
        'UNI-USD',   # Uniswap
        'ATOM-USD',  # Cosmos
    ]

    volatilities = []

    for symbol in cryptos:
        try:
            # Get last 7 days of data
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="7d", interval="1h")

            if len(data) < 24:
                continue

            # Calculate returns and volatility
            returns = data['Close'].pct_change().dropna()
            volatility = returns.std() * 100  # As percentage

            volatilities.append({
                'symbol': symbol,
                'volatility': volatility,
                'price': data['Close'].iloc[-1]
            })
        except:
            continue

    # Sort by volatility (descending)
    volatilities.sort(key=lambda x: x['volatility'], reverse=True)

    # Return top N symbols
    return [v['symbol'] for v in volatilities[:n]]

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

@app.route('/api/top-cryptos')
def get_top_cryptos_endpoint():
    """API endpoint to get top 5 most volatile cryptocurrencies"""
    try:
        top_cryptos = get_top_volatile_cryptos(n=5)
        return jsonify({
            'status': 'success',
            'cryptos': top_cryptos,
            'count': len(top_cryptos)
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

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
    """Run GARCH prediction - called by Cloud Scheduler or API request

    Query params or JSON body:
        asset: Cryptocurrency symbol (e.g., 'BTC-USD'). Default: BTC-USD
    """

    # Get asset from query params or JSON body
    if request.method == 'POST' and request.is_json:
        ASSET = request.json.get('asset', 'BTC-USD')
    else:
        ASSET = request.args.get('asset', 'BTC-USD')
    
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

        # 5. Generate trading signal based on DYNAMIC volatility thresholds
        # Calculate historical volatility distribution from recent data
        historical_volatilities = data['returns'].rolling(window=24).std().dropna()

        # Use percentiles for dynamic thresholds
        vol_75_percentile = np.percentile(historical_volatilities, 75)
        vol_25_percentile = np.percentile(historical_volatilities, 25)

        # Add buffer to avoid too many trades (10% buffer)
        buffer = (vol_75_percentile - vol_25_percentile) * 0.1
        threshold_high = vol_75_percentile + buffer
        threshold_low = vol_25_percentile - buffer

        print(f"Dynamic thresholds: LOW={threshold_low:.4f}%, HIGH={threshold_high:.4f}%")
        print(f"Predicted volatility: {predicted_volatility:.4f}%")

        # Generate signal based on dynamic thresholds
        if predicted_volatility > threshold_high:
            signal = "SELL"  # High volatility = risky, sell
        elif predicted_volatility < threshold_low:
            signal = "BUY"   # Low volatility = stable, buy
        else:
            signal = "HOLD"  # Medium volatility = wait
        
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
                "bic": float(model_fitted.bic),
                "threshold_high": float(threshold_high),
                "threshold_low": float(threshold_low),
                "vol_75_percentile": float(vol_75_percentile),
                "vol_25_percentile": float(vol_25_percentile)
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
    """Generate and send AI-powered economic analysis report via Telegram with PDF

    IMPORTANT: Only sends to Telegram when signal changes to BUY
    Always saves to vector database regardless of signal
    """
    try:
        print("Generating AI report...")

        # Generate report using Gemini AI
        report_text, metadata = generate_ai_report()

        if not metadata:
            # Error occurred, cannot proceed
            return jsonify({
                "status": "error",
                "message": "Failed to generate report",
                "report_length": len(report_text) if report_text else 0
            }), 500

        # ALWAYS save report to vector DB and PDF (regardless of signal)
        result = save_report_with_pdf(report_text, metadata)
        print(f"✅ Report saved to vector DB and PDF")

        # Get current and previous signal from BigQuery
        current_signal = metadata.get('signal', '')

        try:
            client = bigquery.Client(project=PROJECT_ID)
            # Get the last 2 predictions to compare signals
            query = f"""
            SELECT signal
            FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
            ORDER BY timestamp DESC
            LIMIT 2
            """
            results = list(client.query(query).result())

            previous_signal = results[1].signal if len(results) > 1 else None

            print(f"📊 Signal comparison: Previous={previous_signal}, Current={current_signal}")

        except Exception as e:
            print(f"⚠️ Could not get previous signal: {e}")
            previous_signal = None

        # ONLY send to Telegram if signal changed to BUY
        should_notify = (current_signal == 'BUY' and previous_signal != 'BUY')

        if should_notify:
            print(f"🚨 SIGNAL CHANGED TO BUY! Sending notification to Telegram...")

            # Send report text via Telegram
            send_telegram_alert(report_text)

            # Send PDF to Telegram if available
            if result and result.get('pdf_bytes'):
                try:
                    token = os.environ.get('TELEGRAM_BOT_TOKEN')
                    chat_id = os.environ.get('TELEGRAM_CHAT_ID')

                    if token and chat_id:
                        url = f"https://api.telegram.org/bot{token}/sendDocument"
                        files = {'document': (f"reporte_BUY_{metadata['timestamp']}.pdf".replace(' ', '_').replace(':', '-'), result['pdf_bytes'], 'application/pdf')}
                        data = {'chat_id': chat_id, 'caption': '🟢 SEÑAL DE COMPRA DETECTADA - Reporte completo'}
                        requests.post(url, files=files, data=data, timeout=30)
                        print("✅ PDF sent to Telegram")
                except Exception as e:
                    print(f"⚠️ Error sending PDF to Telegram: {e}")

            # Send to WhatsApp if configured
            try:
                print("Sending to WhatsApp...")
                send_whatsapp_message(f"🟢 SEÑAL DE COMPRA DETECTADA\n\n{report_text}")
                if result and result.get('pdf_url'):
                    send_whatsapp_pdf(result['pdf_url'], "📄 Reporte GARCH - SEÑAL BUY")
            except Exception as e:
                print(f"⚠️ Error sending to WhatsApp: {e}")
        else:
            print(f"ℹ️  Signal is {current_signal} (no change to BUY). Report saved but not sent to Telegram.")

        return jsonify({
            "status": "success",
            "message": f"Report saved to DB. {'Notification sent (BUY signal)' if should_notify else 'No notification (not a BUY signal)'}",
            "report_length": len(report_text),
            "pdf_url": result.get('pdf_url') if result else None,
            "doc_id": result.get('doc_id') if result else None,
            "signal": current_signal,
            "previous_signal": previous_signal,
            "notified": should_notify
        })

    except Exception as e:
        error_msg = f"Error generating/sending report: {str(e)}"
        print(error_msg)
        return jsonify({"status": "error", "message": error_msg}), 500

@app.route('/telegram-webhook', methods=['POST'])
def telegram_webhook():
    """Handle incoming Telegram bot updates"""
    try:
        update = request.get_json()
        
        # Extract message info
        if 'message' not in update:
            return jsonify({"status": "ok"}), 200
            
        message = update['message']
        chat_id = message['chat']['id']
        text = message.get('text', '')
        
        # Only respond to authorized chat
        authorized_chat_id = os.environ.get('TELEGRAM_CHAT_ID')
        if str(chat_id) != str(authorized_chat_id):
            print(f"Unauthorized chat ID: {chat_id}")
            return jsonify({"status": "unauthorized"}), 403
        
        # Handle commands
        if text.startswith('/'):
            handle_telegram_command(text, chat_id)
        
        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        print(f"Error in telegram webhook: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

def handle_telegram_command(command, chat_id):
    """Process Telegram bot commands"""
    command = command.lower().strip()
    
    try:
        if command == '/reporte' or command == '/report':
            # Generate and send AI report with PDF
            msg = "🔄 Generando reporte AI... (puede tomar unos segundos)"
            send_telegram_message(chat_id, msg)
            
            report, metadata = generate_ai_report()
            
            if metadata:
                # Save PDF and send
                result = save_report_with_pdf(report, metadata)
                send_telegram_message(chat_id, report)
                
                # Send PDF
                if result and result.get('pdf_bytes'):
                    try:
                        token = os.environ.get('TELEGRAM_BOT_TOKEN')
                        url = f"https://api.telegram.org/bot{token}/sendDocument"
                        files = {'document': (f"reporte.pdf", result['pdf_bytes'], 'application/pdf')}
                        data = {'chat_id': chat_id, 'caption': '📄 Reporte en PDF'}
                        requests.post(url, files=files, data=data, timeout=30)
                    except Exception as e:
                        print(f"Error sending PDF: {e}")
            else:
                send_telegram_message(chat_id, report)
            
        elif command == '/pdf':
            # Send last report as PDF
            msg = "📄 Generando PDF del último reporte..."
            send_telegram_message(chat_id, msg)
            
            report, metadata = generate_ai_report()
            if metadata:
                result = save_report_with_pdf(report, metadata)
                if result and result.get('pdf_bytes'):
                    try:
                        token = os.environ.get('TELEGRAM_BOT_TOKEN')
                        url = f"https://api.telegram.org/bot{token}/sendDocument"
                        files = {'document': (f"reporte.pdf", result['pdf_bytes'], 'application/pdf')}
                        data = {'chat_id': chat_id, 'caption': f"📄 Reporte PDF\n🔗 {result.get('pdf_url','')}"}
                        requests.post(url, files=files, data=data, timeout=30)
                        send_telegram_message(chat_id, "✅ PDF enviado")
                    except Exception as e:
                        send_telegram_message(chat_id, f"❌ Error: {str(e)}")
            else:
                send_telegram_message(chat_id, "❌ Error generando PDF")
        
        elif command.startswith('/analisis'):
            # Meta-analysis command
            msg = "🔍 Buscando reportes históricos..."
            send_telegram_message(chat_id, msg)
            
            # Extract query from command (e.g., "/analisis volatilidad")
            query = command.replace('/analisis', '').strip()
            if not query:
                query = "tendencias y volatilidad del mercado"
            
            results = search_similar_reports(query, n_results=5)
            
            if results['documents'] and results['documents'][0]:
                # Generate meta-analysis
                reports_context = []
                for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
                    reports_context.append({
                        'timestamp': meta.get('timestamp', ''),
                        'price': meta.get('price', 0),
                        'volatility': meta.get('volatility', 0),
                        'signal': meta.get('signal', '')
                    })
                
                # Generate analysis with Gemini
                api_key = os.environ.get('GEMINI_API_KEY')
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-pro-latest')
                
                prompt = f"""Analiza estos {len(reports_context)} reportes históricos de Bitcoin:

Query: "{query}"

Reportes:
"""
                for i, rpt in enumerate(reports_context[:3], 1):
                    prompt += f"{i}. {rpt['timestamp']}: ${rpt['price']:,.2f}, Vol: {rpt['volatility']:.4f}%, {rpt['signal']}\n"
                
                prompt += "\nGenera análisis conciso (max 150 palabras) con tendencias e insights."
                
                response = model.generate_content(prompt)
                analysis = f"""📊 *Metaanálisis*
🔍 Query: {query}
📈 Reportes encontrados: {len(reports_context)}

{response.text}"""
                
                send_telegram_message(chat_id, analysis)
            else:
                send_telegram_message(chat_id, "📊 No hay suficientes reportes históricos")
        
        elif command == '/link-whatsapp':
            # Link WhatsApp via QR Code
            msg = "🔄 Generando código QR para WhatsApp..."
            send_telegram_message(chat_id, msg)
            
            qr_base64 = get_whatsapp_qr()
            
            if qr_base64:
                try:
                    # Send QR image to Telegram
                    import base64
                    qr_bytes = base64.b64decode(qr_base64.replace('data:image/png;base64,', ''))
                    
                    token = os.environ.get('TELEGRAM_BOT_TOKEN')
                    url = f"https://api.telegram.org/bot{token}/sendPhoto"
                    files = {'photo': ('qrcode.png', qr_bytes, 'image/png')}
                    data = {'chat_id': chat_id, 'caption': '📱 Escanea este código con tu WhatsApp\n(Dispositivos vinculados > Vincular dispositivo)'}
                    requests.post(url, files=files, data=data, timeout=30)
                except Exception as e:
                    send_telegram_message(chat_id, f"❌ Error enviando QR: {str(e)}")
            else:
                send_telegram_message(chat_id, "❌ No se pudo generar el QR. Verifica que la VM de Evolution API esté corriendo.")

        elif command == '/ayuda' or command == '/help':
            help_text = """
📊 *GARCH Trading Bot - Comandos Disponibles*

🤖 *Reportes AI:*
/reporte - Genera análisis económico AI inmediato (incluye PDF)
/pdf - Envía último reporte en PDF

📈 *Análisis:*
/analisis [tema] - Metaanálisis de reportes históricos
/stats - Estadísticas rápidas de 24h

📱 *WhatsApp:*
/link-whatsapp - Vincular cuenta de WhatsApp

ℹ️ *Ayuda:*
/ayuda - Muestra este mensaje

---
_Bot con Gemini AI + Vector DB + WhatsApp_
"""
            send_telegram_message(chat_id, help_text)
            
        elif command == '/stats':
            # Quick stats from BigQuery
            try:
                client = bigquery.Client(project=PROJECT_ID)
                query = f"""
                SELECT 
                    COUNT(*) as total,
                    AVG(predicted_volatility) as avg_vol,
                    MAX(current_price) as max_price,
                    MIN(current_price) as min_price
                FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
                WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
                """
                
                result = list(client.query(query).result())[0]
                
                stats_msg = f"""📊 *Estadísticas 24h*

📈 Predicciones: {result.total}
📉 Volatilidad promedio: {result.avg_vol:.4f}%
💰 Precio máximo: ${result.max_price:,.2f}
💵 Precio mínimo: ${result.min_price:,.2f}
"""
                send_telegram_message(chat_id, stats_msg)
                
            except Exception as e:
                send_telegram_message(chat_id, f"❌ Error obteniendo stats: {str(e)}")
        
        else:
            send_telegram_message(chat_id, f"Comando no reconocido: {command}\n\nUsa /ayuda para ver comandos disponibles.")
            
    except Exception as e:
        print(f"Error handling command {command}: {str(e)}")
        send_telegram_message(chat_id, f"❌ Error procesando comando: {str(e)}")

def send_telegram_message(chat_id, text):
    """Send message to specific Telegram chat"""
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not token:
        print("TELEGRAM_BOT_TOKEN not configured")
        return
        
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Error sending Telegram message: {e}")


def upload_pdf_to_storage(pdf_bytes, filename):
    """Upload PDF to Cloud Storage and return public URL"""
    try:
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(f"reports/{filename}")
        
        blob.upload_from_string(pdf_bytes, content_type='application/pdf')
        
        # Make blob publicly accessible
        blob.make_public()
        
        public_url = blob.public_url
        print(f"✅ PDF uploaded: {public_url}")
        return public_url
    
    except Exception as e:
        print(f"❌ Error uploading PDF: {e}")
        return None


def save_report_with_pdf(report_text, metadata):
    """
    Generate PDF, upload to storage, and save in vector DB
    
    Args:
        report_text (str): Full AI-generated report text
        metadata (dict): Report metadata
    
    Returns:
        dict: {'pdf_url': str, 'doc_id': str}
    """
    try:
        # Prepare data for PDF
        pdf_data = {
            'title': 'GARCH Trading Bot - AI Report',
            'timestamp': metadata.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            'price': metadata.get('price', 0),
            'volatility': metadata.get('volatility', 0),
            'signal': metadata.get('signal', 'N/A'),
            'ai_analysis': report_text,
            'stats': {
                'avg_volatility': metadata.get('avg_volatility', 0),
                'persistence': metadata.get('persistence', 0),
                'num_predictions': metadata.get('num_predictions', 0)
            }
        }
        
        # Generate PDF
        pdf_bytes = create_pdf_report(pdf_data)
        
        # Upload to Cloud Storage
        timestamp_str = metadata.get('timestamp', datetime.now().strftime('%Y%m%d_%H%M%S'))
        filename = f"garch_report_{timestamp_str}.pdf".replace(' ', '_').replace(':', '-')
        pdf_url = upload_pdf_to_storage(pdf_bytes, filename)
        
        # Store in vector database
        doc_id = store_report(report_text, metadata, pdf_url)
        
        return {
            'pdf_url': pdf_url,
            'doc_id': doc_id,
            'pdf_bytes': pdf_bytes  # For sending via Telegram
        }
    
    except Exception as e:
        print(f"❌ Error in save_report_with_pdf: {e}")
        return None


@app.route('/meta-analysis', methods=['POST'])
def meta_analysis():
    """Generate meta-analysis using semantic search of historical reports"""
    try:
        data = request.get_json() or {}
        query = data.get('query', 'volatilidad y tendencias del mercado')
        n_results = data.get('n_results', 10)
        
        print(f"🔍 Meta-analysis query: {query}")
        
        # Search similar reports
        results = search_similar_reports(query, n_results=n_results)
        
        if not results['documents'] or not results['documents'][0]:
            return jsonify({
                'status': 'success',
                'message': 'No hay suficientes reportes históricos para metaanálisis',
                'reports_found': 0
            })
        
        # Prepare context from search results
        reports_context = []
        for i, (doc, meta) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
            reports_context.append({
                'timestamp': meta.get('timestamp', ''),
                'price': meta.get('price', 0),
                'volatility': meta.get('volatility', 0),
                'signal': meta.get('signal', ''),
                'excerpt': doc[:300]  # First 300 chars
            })
        
        # Generate meta-analysis using Gemini
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            return jsonify({'status': 'error', 'message': 'GEMINI_API_KEY not configured'}), 500
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro-latest')
        
        # Create prompt for meta-analysis
        prompt = f"""Eres un analista cuantitativo experto. Analiza los siguientes {len(reports_context)} reportes históricos de trading de Bitcoin basados en GARCH.

Query del usuario: "{query}"

Reportes encontrados (ordenados por relevancia):
"""
        
        for i, rpt in enumerate(reports_context[:5], 1):  # Top 5
            prompt += f"\n{i}. Fecha: {rpt['timestamp']}\n"
            prompt += f"   Precio: ${rpt['price']:,.2f}\n"
            prompt += f"   Volatilidad: {rpt['volatility']:.4f}%\n"
            prompt += f"   Señal: {rpt['signal']}\n"
            prompt += f"   Extracto: {rpt['excerpt']}...\n"
        
        prompt += """\n
Genera un metaanálisis que incluya:
1. **Tendencias Identificadas**: Patrones en volatilidad, precios y señales
2. **Evolución Temporal**: Cómo han cambiado las métricas a lo largo del tiempo
3. **Insights Clave**: Hallazgos importantes para trading
4. **Recomendaciones**: Basadas en el análisis histórico

Máximo 300 palabras. Usa formato markdown para Telegram."""
        
        response = model.generate_content(prompt)
        meta_analysis_text = response.text
        
        return jsonify({
            'status': 'success',
            'query': query,
            'reports_found': len(reports_context),
            'meta_analysis': meta_analysis_text,
            'top_reports': reports_context[:5]
        })
    
    except Exception as e:
        error_msg = f"Error en meta-analysis: {str(e)}"
        print(error_msg)
        return jsonify({'status': 'error', 'message': error_msg}), 500



@functions_framework.http
def garch_trading_bot(request):
    """Main Cloud Function entry point - routes to Flask app"""
    with app.request_context(request.environ):
        return app.full_dispatch_request()
