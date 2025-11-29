#!/usr/bin/env python3
"""
Validación del Modelo GARCH
Verifica si las predicciones son buenas o están sesgadas
"""

import os
from google.cloud import bigquery
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import yfinance as yf

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

PROJECT_ID = "travel-recomender"
DATASET_ID = "trading_bot"
TABLE_ID = "garch_predictions"

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(80)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.RESET}")

def analyze_garch_bias():
    """Analiza si el modelo GARCH tiene sesgos"""

    print_header("🔍 ANÁLISIS DE SESGOS DEL MODELO GARCH")

    try:
        client = bigquery.Client(project=PROJECT_ID)

        # Obtener todas las predicciones
        query = f"""
        SELECT
            timestamp,
            current_price,
            predicted_volatility,
            signal,
            model_params
        FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
        WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
        ORDER BY timestamp ASC
        """

        results = client.query(query).result()
        predictions = list(results)

        if len(predictions) < 10:
            print_warning(f"Muy pocas predicciones para analizar: {len(predictions)}")
            print_info("El modelo necesita al menos 10 predicciones para análisis confiable")
            return

        print_success(f"Predicciones encontradas: {len(predictions)}")
        print()

        # Convertir a DataFrame
        data = []
        for pred in predictions:
            data.append({
                'timestamp': pred.timestamp,
                'price': float(pred.current_price),
                'volatility': float(pred.predicted_volatility),
                'signal': pred.signal
            })

        df = pd.DataFrame(data)

        # ANÁLISIS 1: Distribución de señales
        print_info("📊 ANÁLISIS 1: Distribución de Señales")

        buy_count = (df['signal'] == 'BUY').sum()
        sell_count = (df['signal'] == 'SELL').sum()
        hold_count = (df['signal'] == 'HOLD').sum()
        total = len(df)

        buy_pct = (buy_count / total) * 100
        sell_pct = (sell_count / total) * 100
        hold_pct = (hold_count / total) * 100

        print(f"   BUY:  {buy_count:3d} ({buy_pct:5.1f}%)")
        print(f"   SELL: {sell_count:3d} ({sell_pct:5.1f}%)")
        print(f"   HOLD: {hold_count:3d} ({hold_pct:5.1f}%)")
        print()

        # SESGO DETECTADO si >70% es una señal
        if buy_pct > 70:
            print_error(f"🚨 SESGO DETECTADO: {buy_pct:.1f}% de señales son BUY")
            print_warning("   El modelo está sesgado hacia COMPRAR - NO ES CONFIABLE")
        elif sell_pct > 70:
            print_error(f"🚨 SESGO DETECTADO: {sell_pct:.1f}% de señales son SELL")
            print_warning("   El modelo está sesgado hacia VENDER - NO ES CONFIABLE")
        elif hold_pct > 80:
            print_warning(f"⚠️  MODELO CONSERVADOR: {hold_pct:.1f}% señales HOLD")
            print_info("   El modelo casi nunca toma decisiones")
        else:
            print_success("✅ Distribución de señales parece balanceada")

        print()

        # ANÁLISIS 2: ¿El modelo recalcula cada vez?
        print_info("🔄 ANÁLISIS 2: ¿Recalcula el Modelo Cada 5 Minutos?")

        df['time_diff'] = df['timestamp'].diff().dt.total_seconds() / 60

        # Filtrar outliers (primero valor es NaN)
        time_diffs = df['time_diff'].dropna()

        if len(time_diffs) > 0:
            avg_interval = time_diffs.mean()
            median_interval = time_diffs.median()

            print(f"   Intervalo promedio: {avg_interval:.1f} minutos")
            print(f"   Intervalo mediano:  {median_interval:.1f} minutos")

            if 4 <= avg_interval <= 6:
                print_success("✅ El modelo SÍ se ejecuta aproximadamente cada 5 minutos")
            elif avg_interval < 2:
                print_error(f"❌ Ejecución muy frecuente ({avg_interval:.1f}min) - desperdicio de recursos")
            elif avg_interval > 10:
                print_warning(f"⚠️  Ejecución muy espaciada ({avg_interval:.1f}min) - datos obsoletos")
            else:
                print_info(f"ℹ️  Intervalo de {avg_interval:.1f} minutos (esperado: 5)")

        print()

        # ANÁLISIS 3: ¿Las predicciones cambian?
        print_info("🎯 ANÁLISIS 3: ¿Las Predicciones Cambian o Son Siempre Iguales?")

        unique_signals = df['signal'].nunique()
        signal_changes = (df['signal'] != df['signal'].shift()).sum() - 1  # -1 por el primero

        print(f"   Señales únicas: {unique_signals}/3 posibles (BUY, SELL, HOLD)")
        print(f"   Cambios de señal: {signal_changes} veces")

        if unique_signals == 1:
            print_error(f"🚨 MODELO ESTÁTICO: Siempre da la misma señal ({df['signal'].iloc[0]})")
            print_warning("   El modelo NO está funcionando correctamente")
        elif signal_changes < 2 and len(df) > 50:
            print_warning(f"⚠️  Pocas variaciones ({signal_changes} cambios en {len(df)} predicciones)")
        else:
            print_success(f"✅ El modelo SÍ cambia sus predicciones ({signal_changes} cambios)")

        print()

        # ANÁLISIS 4: Volatilidad predicha vs real
        print_info("📈 ANÁLISIS 4: Precisión de Volatilidad Predicha")

        # Calcular volatilidad real (siguiente período)
        df['real_return'] = df['price'].pct_change() * 100
        df['real_volatility'] = df['real_return'].rolling(window=6).std()  # 6 períodos = ~30 min

        # Comparar predicha vs real (shift para comparar predicción con realidad siguiente)
        df['predicted_vol_prev'] = df['volatility'].shift(1)

        # Calcular error solo donde tenemos ambos valores
        valid_comparison = df.dropna(subset=['predicted_vol_prev', 'real_volatility'])

        if len(valid_comparison) > 5:
            error = np.abs(valid_comparison['predicted_vol_prev'] - valid_comparison['real_volatility'])
            mae = error.mean()
            rmse = np.sqrt((error ** 2).mean())

            # Calcular accuracy
            threshold = 0.5  # 0.5% de tolerancia
            accurate = (error < threshold).sum()
            accuracy_pct = (accurate / len(error)) * 100

            print(f"   Error Absoluto Medio (MAE): {mae:.4f}%")
            print(f"   RMSE: {rmse:.4f}%")
            print(f"   Accuracy (error < {threshold}%): {accuracy_pct:.1f}%")

            if accuracy_pct > 60:
                print_success(f"✅ Buena precisión: {accuracy_pct:.1f}% de predicciones cercanas")
            elif accuracy_pct > 40:
                print_warning(f"⚠️  Precisión moderada: {accuracy_pct:.1f}%")
            else:
                print_error(f"❌ Baja precisión: {accuracy_pct:.1f}% - modelo poco confiable")
        else:
            print_warning("⚠️  Pocos datos para evaluar precisión de volatilidad")

        print()

        # ANÁLISIS 5: Performance de la estrategia
        print_info("💰 ANÁLISIS 5: Performance Real vs HODL")

        # Simular estrategia
        initial_capital = 1000
        cash = 0
        btc = 0
        position = None
        trades = []

        # Empezar con BUY en primera señal
        first_price = df.iloc[0]['price']
        btc = initial_capital / first_price
        position = 'BUY'

        for idx, row in df.iterrows():
            signal = row['signal']
            price = row['price']

            if signal != position:
                if signal == 'SELL' and position == 'BUY':
                    # Vender
                    cash = btc * price
                    pnl = cash - initial_capital
                    trades.append({'action': 'SELL', 'price': price, 'pnl': pnl})
                    btc = 0
                    position = 'SELL'

                elif signal == 'BUY' and position == 'SELL':
                    # Comprar
                    btc = cash / price
                    cash = 0
                    position = 'BUY'
                    trades.append({'action': 'BUY', 'price': price})

        # Valor final
        last_price = df.iloc[-1]['price']
        if btc > 0:
            final_value = btc * last_price
        else:
            final_value = cash

        # HODL comparison
        hodl_btc = initial_capital / first_price
        hodl_value = hodl_btc * last_price

        strategy_return = ((final_value - initial_capital) / initial_capital) * 100
        hodl_return = ((hodl_value - initial_capital) / initial_capital) * 100

        print(f"   Capital inicial: ${initial_capital:.2f}")
        print(f"   Valor final (GARCH): ${final_value:.2f}")
        print(f"   Valor final (HODL):  ${hodl_value:.2f}")
        print()
        print(f"   Retorno GARCH: {strategy_return:+.2f}%")
        print(f"   Retorno HODL:  {hodl_return:+.2f}%")
        print(f"   Diferencia:    {strategy_return - hodl_return:+.2f}%")
        print(f"   Trades ejecutados: {len(trades)}")

        print()

        if strategy_return > hodl_return + 1:
            print_success(f"✅ Estrategia GARCH SUPERA a HODL por {strategy_return - hodl_return:.2f}%")
        elif strategy_return > hodl_return - 1:
            print_info(f"ℹ️  Estrategia similar a HODL (diferencia: {strategy_return - hodl_return:+.2f}%)")
        else:
            print_error(f"❌ HODL es MEJOR que GARCH por {hodl_return - strategy_return:.2f}%")
            print_warning("   La estrategia NO agrega valor")

        print()

        # ANÁLISIS 6: Problema de los umbrales
        print_info("⚙️  ANÁLISIS 6: Umbrales de Decisión")
        print()
        print("   Código actual usa umbrales FIJOS:")
        print(f"   - Volatilidad > 3.0%  → {Colors.RED}SELL{Colors.RESET}")
        print(f"   - Volatilidad < 1.5%  → {Colors.GREEN}BUY{Colors.RESET}")
        print(f"   - Entre 1.5% y 3.0%   → {Colors.YELLOW}HOLD{Colors.RESET}")
        print()

        vol_mean = df['volatility'].mean()
        vol_std = df['volatility'].std()

        print(f"   Volatilidad promedio observada: {vol_mean:.4f}%")
        print(f"   Desviación estándar: {vol_std:.4f}%")
        print()

        # Verificar si los umbrales tienen sentido
        if vol_mean > 3.0:
            print_error("🚨 PROBLEMA: Volatilidad promedio > umbral SELL (3.0%)")
            print_warning("   El modelo casi siempre dice SELL")
        elif vol_mean < 1.5:
            print_error("🚨 PROBLEMA: Volatilidad promedio < umbral BUY (1.5%)")
            print_warning("   El modelo casi siempre dice BUY")
        else:
            print_success("✅ Umbrales parecen razonables para volatilidad observada")

        print()

        # CONCLUSIÓN FINAL
        print_header("📋 RESUMEN Y CONCLUSIONES")

        print(f"{Colors.BOLD}Periodo analizado:{Colors.RESET} {len(df)} predicciones")
        print(f"{Colors.BOLD}Desde:{Colors.RESET} {df.iloc[0]['timestamp']}")
        print(f"{Colors.BOLD}Hasta:{Colors.RESET} {df.iloc[-1]['timestamp']}")
        print()

        # Calcular score
        score = 0
        total_tests = 6

        # Test 1: Distribución balanceada
        if not (buy_pct > 70 or sell_pct > 70 or hold_pct > 80):
            score += 1

        # Test 2: Intervalo correcto
        if 4 <= avg_interval <= 6:
            score += 1

        # Test 3: Predicciones varían
        if signal_changes >= 2:
            score += 1

        # Test 4: Accuracy razonable
        if len(valid_comparison) > 5 and accuracy_pct > 40:
            score += 1

        # Test 5: Supera o iguala HODL
        if strategy_return >= hodl_return - 1:
            score += 1

        # Test 6: Umbrales adecuados
        if 1.5 <= vol_mean <= 3.0:
            score += 1

        score_pct = (score / total_tests) * 100

        print(f"{Colors.BOLD}Score de Confiabilidad: {score}/{total_tests} ({score_pct:.0f}%){Colors.RESET}")
        print()

        if score_pct >= 80:
            print_success("🌟 MODELO CONFIABLE - Las decisiones son buenas")
            print_info("   Puedes confiar en las predicciones del modelo GARCH")
        elif score_pct >= 60:
            print_warning("⚠️  MODELO MODERADO - Úsalo con precaución")
            print_info("   Las predicciones tienen cierta validez pero necesitan mejoras")
        elif score_pct >= 40:
            print_warning("❌ MODELO DÉBIL - No confiar mucho")
            print_info("   Las predicciones no son muy confiables")
        else:
            print_error("🚨 MODELO NO CONFIABLE - NO USAR para trading real")
            print_warning("   Las predicciones están muy sesgadas o son incorrectas")

        print()
        print(f"{Colors.CYAN}{'─'*80}{Colors.RESET}")
        print()

        # Recomendaciones
        print(f"{Colors.BOLD}💡 RECOMENDACIONES:{Colors.RESET}")
        print()

        if buy_pct > 70 or sell_pct > 70:
            print(f"   1. {Colors.YELLOW}Ajustar umbrales de volatilidad{Colors.RESET}")
            print(f"      - Actual: SELL>{Colors.RED}3.0%{Colors.RESET}, BUY<{Colors.GREEN}1.5%{Colors.RESET}")
            print(f"      - Sugerencia: Usar percentiles dinámicos (25% y 75%)")
            print()

        if strategy_return < hodl_return - 1:
            print(f"   2. {Colors.YELLOW}La estrategia no supera HODL{Colors.RESET}")
            print(f"      - Considera usar más indicadores (no solo volatilidad)")
            print(f"      - Agrega filtros de tendencia (MA, RSI, etc)")
            print()

        if unique_signals == 1:
            print(f"   3. {Colors.RED}El modelo no está funcionando{Colors.RESET}")
            print(f"      - Verifica que Cloud Scheduler esté ejecutándose")
            print(f"      - Revisa los logs de la Cloud Function")
            print()

        print(f"   4. {Colors.CYAN}Validar con más datos{Colors.RESET}")
        print(f"      - Espera al menos 7 días de predicciones")
        print(f"      - Compara con diferentes períodos de mercado")
        print()

    except Exception as e:
        print_error(f"Error en análisis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_garch_bias()
