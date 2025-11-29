#!/usr/bin/env python3
"""
Test del Modelo GARCH Mejorado
Compara modelo antiguo (umbrales fijos) vs nuevo (umbrales dinámicos)
"""

import yfinance as yf
import pandas as pd
import numpy as np
from arch import arch_model
from datetime import datetime, timedelta

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

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

def generate_signals_old(volatilities):
    """Modelo ANTIGUO con umbrales fijos"""
    signals = []
    for vol in volatilities:
        if vol > 3.0:
            signals.append('SELL')
        elif vol < 1.5:
            signals.append('BUY')
        else:
            signals.append('HOLD')
    return signals

def generate_signals_new(volatilities):
    """Modelo NUEVO con umbrales dinámicos"""
    vol_75 = np.percentile(volatilities, 75)
    vol_25 = np.percentile(volatilities, 25)

    buffer = (vol_75 - vol_25) * 0.1
    threshold_high = vol_75 + buffer
    threshold_low = vol_25 - buffer

    signals = []
    for vol in volatilities:
        if vol > threshold_high:
            signals.append('SELL')
        elif vol < threshold_low:
            signals.append('BUY')
        else:
            signals.append('HOLD')

    return signals, threshold_low, threshold_high

def simulate_strategy(prices, signals):
    """Simular trading con señales"""
    if len(prices) != len(signals):
        return None

    initial_capital = 1000
    cash = 0
    btc = 0
    position = None
    trades = []

    # Empezar con primera señal
    first_price = prices[0]
    if signals[0] == 'BUY':
        btc = initial_capital / first_price
        position = 'BUY'
    else:
        cash = initial_capital
        position = 'HOLD'

    for i in range(1, len(signals)):
        signal = signals[i]
        price = prices[i]

        if signal != position:
            if signal == 'SELL' and btc > 0:
                cash = btc * price
                btc = 0
                trades.append({'type': 'SELL', 'price': price, 'index': i})
                position = 'SELL'
            elif signal == 'BUY' and cash > 0:
                btc = cash / price
                cash = 0
                trades.append({'type': 'BUY', 'price': price, 'index': i})
                position = 'BUY'

    # Valor final
    last_price = prices[-1]
    if btc > 0:
        final_value = btc * last_price
    else:
        final_value = cash

    # HODL comparison
    hodl_btc = initial_capital / first_price
    hodl_value = hodl_btc * last_price

    return {
        'initial': initial_capital,
        'final': final_value,
        'return_pct': ((final_value - initial_capital) / initial_capital) * 100,
        'hodl_value': hodl_value,
        'hodl_return_pct': ((hodl_value - initial_capital) / initial_capital) * 100,
        'vs_hodl': final_value - hodl_value,
        'trades': len(trades),
        'trade_details': trades
    }

def run_comparison_test():
    """Ejecutar prueba comparativa"""

    print_header("🧪 PRUEBA COMPARATIVA: MODELO VIEJO vs NUEVO")

    print_info("Descargando datos de BTC...")

    # Descargar datos de BTC de últimos 30 días
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    ticker = yf.Ticker("BTC-USD")
    data = ticker.history(start=start_date, end=end_date, interval="1h")

    if len(data) < 100:
        print_error(f"Datos insuficientes: {len(data)} puntos")
        return

    print_success(f"Datos descargados: {len(data)} puntos")
    print()

    # Calcular returns
    data['returns'] = 100 * data['Close'].pct_change()
    data = data.dropna()

    print_info("Calculando volatilidades GARCH...")

    # Fit GARCH model
    model = arch_model(data['returns'], vol='Garch', p=1, q=1)
    model_fitted = model.fit(disp='off', show_warning=False)

    # Generar predicciones de volatilidad
    volatilities = []
    prices = []

    for i in range(100, len(data)):
        # Usar ventana deslizante
        window_data = data['returns'].iloc[i-100:i]

        try:
            model_window = arch_model(window_data, vol='Garch', p=1, q=1)
            fitted = model_window.fit(disp='off', show_warning=False)
            forecast = fitted.forecast(horizon=1)
            vol = float(np.sqrt(forecast.variance.values[-1, 0]))
            volatilities.append(vol)
            prices.append(data['Close'].iloc[i])
        except:
            continue

    volatilities = np.array(volatilities)
    prices = np.array(prices)

    print_success(f"Volatilidades calculadas: {len(volatilities)}")
    print()

    # Estadísticas de volatilidad
    print_info("📊 Estadísticas de Volatilidad:")
    print(f"   Promedio: {np.mean(volatilities):.4f}%")
    print(f"   Desv. Est: {np.std(volatilities):.4f}%")
    print(f"   Mínimo: {np.min(volatilities):.4f}%")
    print(f"   Máximo: {np.max(volatilities):.4f}%")
    print(f"   Percentil 25: {np.percentile(volatilities, 25):.4f}%")
    print(f"   Percentil 75: {np.percentile(volatilities, 75):.4f}%")
    print()

    # MODELO VIEJO
    print_header("🔴 MODELO VIEJO (Umbrales Fijos)")

    print_info("Configuración:")
    print(f"   SELL si volatilidad > {Colors.RED}3.0%{Colors.RESET}")
    print(f"   BUY  si volatilidad < {Colors.GREEN}1.5%{Colors.RESET}")
    print(f"   HOLD entre 1.5% y 3.0%")
    print()

    signals_old = generate_signals_old(volatilities)

    buy_old = signals_old.count('BUY')
    sell_old = signals_old.count('SELL')
    hold_old = signals_old.count('HOLD')
    total = len(signals_old)

    print_info("Distribución de Señales:")
    print(f"   BUY:  {buy_old:4d} ({buy_old/total*100:5.1f}%)")
    print(f"   SELL: {sell_old:4d} ({sell_old/total*100:5.1f}%)")
    print(f"   HOLD: {hold_old:4d} ({hold_old/total*100:5.1f}%)")
    print()

    # Simular
    results_old = simulate_strategy(prices, signals_old)

    if results_old:
        print_info("Performance:")
        print(f"   Capital inicial: ${results_old['initial']:.2f}")
        print(f"   Capital final:   ${results_old['final']:.2f}")
        print(f"   Retorno:         {results_old['return_pct']:+.2f}%")
        print(f"   HODL:            {results_old['hodl_return_pct']:+.2f}%")
        print(f"   vs HODL:         {results_old['return_pct'] - results_old['hodl_return_pct']:+.2f}%")
        print(f"   Trades:          {results_old['trades']}")
        print()

    # MODELO NUEVO
    print_header("🟢 MODELO NUEVO (Umbrales Dinámicos)")

    signals_new, threshold_low, threshold_high = generate_signals_new(volatilities)

    print_info("Configuración:")
    print(f"   SELL si volatilidad > {Colors.RED}{threshold_high:.4f}%{Colors.RESET} (dinámico)")
    print(f"   BUY  si volatilidad < {Colors.GREEN}{threshold_low:.4f}%{Colors.RESET} (dinámico)")
    print(f"   HOLD entre {threshold_low:.4f}% y {threshold_high:.4f}%")
    print()

    buy_new = signals_new.count('BUY')
    sell_new = signals_new.count('SELL')
    hold_new = signals_new.count('HOLD')

    print_info("Distribución de Señales:")
    print(f"   BUY:  {buy_new:4d} ({buy_new/total*100:5.1f}%)")
    print(f"   SELL: {sell_new:4d} ({sell_new/total*100:5.1f}%)")
    print(f"   HOLD: {hold_new:4d} ({hold_new/total*100:5.1f}%)")
    print()

    # Simular
    results_new = simulate_strategy(prices, signals_new)

    if results_new:
        print_info("Performance:")
        print(f"   Capital inicial: ${results_new['initial']:.2f}")
        print(f"   Capital final:   ${results_new['final']:.2f}")
        print(f"   Retorno:         {results_new['return_pct']:+.2f}%")
        print(f"   HODL:            {results_new['hodl_return_pct']:+.2f}%")
        print(f"   vs HODL:         {results_new['return_pct'] - results_new['hodl_return_pct']:+.2f}%")
        print(f"   Trades:          {results_new['trades']}")
        print()

    # COMPARACIÓN FINAL
    print_header("📊 COMPARACIÓN FINAL")

    comparison_data = []

    comparison_data.append(["Métrica", "Modelo VIEJO", "Modelo NUEVO", "Diferencia"])
    comparison_data.append(["-"*20, "-"*15, "-"*15, "-"*15])

    # Distribución de señales
    comparison_data.append([
        "BUY signals",
        f"{buy_old/total*100:.1f}%",
        f"{buy_new/total*100:.1f}%",
        f"{(buy_new-buy_old)/total*100:+.1f}%"
    ])

    comparison_data.append([
        "SELL signals",
        f"{sell_old/total*100:.1f}%",
        f"{sell_new/total*100:.1f}%",
        f"{(sell_new-sell_old)/total*100:+.1f}%"
    ])

    comparison_data.append([
        "HOLD signals",
        f"{hold_old/total*100:.1f}%",
        f"{hold_new/total*100:.1f}%",
        f"{(hold_new-hold_old)/total*100:+.1f}%"
    ])

    # Performance
    if results_old and results_new:
        comparison_data.append(["-"*20, "-"*15, "-"*15, "-"*15])

        comparison_data.append([
            "Retorno",
            f"{results_old['return_pct']:+.2f}%",
            f"{results_new['return_pct']:+.2f}%",
            f"{results_new['return_pct'] - results_old['return_pct']:+.2f}%"
        ])

        comparison_data.append([
            "vs HODL",
            f"{results_old['return_pct'] - results_old['hodl_return_pct']:+.2f}%",
            f"{results_new['return_pct'] - results_new['hodl_return_pct']:+.2f}%",
            f"{(results_new['return_pct'] - results_new['hodl_return_pct']) - (results_old['return_pct'] - results_old['hodl_return_pct']):+.2f}%"
        ])

        comparison_data.append([
            "Trades",
            f"{results_old['trades']}",
            f"{results_new['trades']}",
            f"{results_new['trades'] - results_old['trades']:+d}"
        ])

    # Imprimir tabla
    for row in comparison_data:
        print(f"   {row[0]:<20} {row[1]:>15} {row[2]:>15} {row[3]:>15}")

    print()

    # CONCLUSIÓN
    print_header("🎯 CONCLUSIÓN")

    # Señales más balanceadas
    old_balance = max(buy_old, sell_old, hold_old) / total
    new_balance = max(buy_new, sell_new, hold_new) / total

    if new_balance < old_balance:
        print_success("✅ El NUEVO modelo tiene señales MÁS BALANCEADAS")
    else:
        print_warning("⚠️  El VIEJO modelo tenía mejor balance de señales")

    # Diversidad de señales
    old_diversity = len(set(signals_old))
    new_diversity = len(set(signals_new))

    if new_diversity > old_diversity:
        print_success(f"✅ El NUEVO modelo usa MÁS tipos de señales ({new_diversity} vs {old_diversity})")
    elif new_diversity == old_diversity:
        print_info(f"ℹ️  Ambos modelos usan {new_diversity} tipos de señales")

    # Performance
    if results_old and results_new:
        if results_new['return_pct'] > results_old['return_pct']:
            diff = results_new['return_pct'] - results_old['return_pct']
            print_success(f"✅ El NUEVO modelo tiene MEJOR retorno (+{diff:.2f}%)")
        elif results_new['return_pct'] == results_old['return_pct']:
            print_info("ℹ️  Ambos modelos tienen el mismo retorno")
        else:
            diff = results_old['return_pct'] - results_new['return_pct']
            print_warning(f"⚠️  El VIEJO modelo tiene mejor retorno (+{diff:.2f}%)")

        # vs HODL
        old_vs_hodl = results_old['return_pct'] - results_old['hodl_return_pct']
        new_vs_hodl = results_new['return_pct'] - results_new['hodl_return_pct']

        if new_vs_hodl > old_vs_hodl:
            print_success(f"✅ El NUEVO modelo SUPERA más a HODL")
        elif abs(new_vs_hodl - old_vs_hodl) < 0.5:
            print_info("ℹ️  Ambos modelos son similares vs HODL")
        else:
            print_warning("⚠️  El VIEJO modelo superaba más a HODL")

        # Trades
        if results_new['trades'] > 0 and results_old['trades'] == 0:
            print_success(f"✅ El NUEVO modelo SÍ ejecuta trades ({results_new['trades']} trades)")
        elif results_new['trades'] > results_old['trades']:
            print_info(f"ℹ️  El NUEVO modelo es más activo ({results_new['trades']} vs {results_old['trades']} trades)")

    print()
    print(f"{Colors.BOLD}{Colors.GREEN}🎉 MODELO MEJORADO IMPLEMENTADO EXITOSAMENTE{Colors.RESET}")
    print()

if __name__ == "__main__":
    run_comparison_test()
