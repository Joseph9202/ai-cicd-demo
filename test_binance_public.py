#!/usr/bin/env python3
"""
Test de Binance usando SOLO datos públicos
NO requiere API Keys ni permisos especiales
"""

from binance.client import Client
from binance.exceptions import BinanceAPIException
import sys
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.RESET}")

def print_data(message):
    print(f"{Colors.CYAN}{message}{Colors.RESET}")

def print_header(message):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{message}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")

def main():
    print_header("📊 TEST BINANCE - DATOS PÚBLICOS (SIN API KEYS)")

    print_info("Este test NO requiere API Keys ni permisos")
    print_info("Obtiene datos públicos del mercado en tiempo real\n")

    try:
        # Crear cliente público (sin credenciales)
        client = Client("", "", testnet=True)

        # Test 1: Conectividad
        print_info("Test 1: Verificando conectividad con Binance Testnet...")
        server_time = client.get_server_time()
        timestamp = server_time['serverTime']
        server_datetime = datetime.fromtimestamp(timestamp / 1000)
        print_success(f"Servidor respondiendo: {server_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Test 2: Precio BTC/USDT
        print_info("Test 2: Obteniendo precio de BTC/USDT...")
        ticker = client.get_symbol_ticker(symbol="BTCUSDT")
        btc_price = float(ticker['price'])
        print_success(f"Precio BTC/USDT: ${btc_price:,.2f}")
        print()

        # Test 3: Top 10 cryptos por volumen
        print_info("Test 3: Top 10 criptomonedas por volumen (24h)...")
        all_tickers = client.get_ticker()

        # Filtrar pares USDT
        usdt_pairs = [t for t in all_tickers if t['symbol'].endswith('USDT')]
        usdt_pairs.sort(key=lambda x: float(x['quoteVolume']), reverse=True)

        print_success("Top 10 por volumen:")
        print_data(f"\n  {'#':<4} {'Par':<12} {'Precio':<15} {'Cambio 24h':<12} {'Volumen (USDT)':<20}")
        print_data(f"  {'-'*70}")

        for i, pair in enumerate(usdt_pairs[:10], 1):
            symbol = pair['symbol']
            price = float(pair['lastPrice'])
            change = float(pair['priceChangePercent'])
            volume = float(pair['quoteVolume'])

            change_icon = "🟢" if change >= 0 else "🔴"

            print_data(
                f"  {i:<4} {symbol:<12} ${price:>13,.2f} "
                f"{change_icon} {change:>6.2f}%   ${volume:>18,.0f}"
            )
        print()

        # Test 4: Order Book (libro de órdenes) de BTC
        print_info("Test 4: Order Book de BTC/USDT (top 5)...")
        depth = client.get_order_book(symbol="BTCUSDT", limit=5)

        print_success("Órdenes de COMPRA (bids):")
        for i, bid in enumerate(depth['bids'][:5], 1):
            price, qty = float(bid[0]), float(bid[1])
            print_data(f"  {i}. ${price:,.2f} - {qty:.6f} BTC")

        print()
        print_success("Órdenes de VENTA (asks):")
        for i, ask in enumerate(depth['asks'][:5], 1):
            price, qty = float(ask[0]), float(ask[1])
            print_data(f"  {i}. ${price:,.2f} - {qty:.6f} BTC")

        # Spread
        best_bid = float(depth['bids'][0][0])
        best_ask = float(depth['asks'][0][0])
        spread = best_ask - best_bid
        spread_pct = (spread / best_bid) * 100

        print()
        print_data(f"  📊 Spread: ${spread:.2f} ({spread_pct:.4f}%)")
        print()

        # Test 5: Últimos trades
        print_info("Test 5: Últimos 10 trades de BTC/USDT...")
        trades = client.get_recent_trades(symbol="BTCUSDT", limit=10)

        print_success("Trades recientes:")
        print_data(f"\n  {'Hora':<12} {'Tipo':<8} {'Precio':<15} {'Cantidad':<12}")
        print_data(f"  {'-'*50}")

        for trade in trades[:10]:
            price = float(trade['price'])
            qty = float(trade['qty'])
            trade_time = datetime.fromtimestamp(trade['time'] / 1000)
            side = "VENTA" if trade['isBuyerMaker'] else "COMPRA"
            side_icon = "🔴" if trade['isBuyerMaker'] else "🟢"

            print_data(
                f"  {trade_time.strftime('%H:%M:%S'):<12} "
                f"{side_icon} {side:<6} ${price:>13,.2f} {qty:>10.6f}"
            )
        print()

        # Test 6: Estadísticas 24h de múltiples pares
        print_info("Test 6: Mayores ganadores y perdedores (24h)...")

        # Ordenar por cambio de precio
        usdt_pairs_sorted = sorted(usdt_pairs, key=lambda x: float(x['priceChangePercent']), reverse=True)

        print_success("🚀 Top 5 GANADORES:")
        for i, pair in enumerate(usdt_pairs_sorted[:5], 1):
            symbol = pair['symbol']
            change = float(pair['priceChangePercent'])
            price = float(pair['lastPrice'])
            print_data(f"  {i}. {symbol:<12} 🟢 +{change:.2f}%  (${price:,.4f})")

        print()
        print_success("📉 Top 5 PERDEDORES:")
        for i, pair in enumerate(usdt_pairs_sorted[-5:], 1):
            symbol = pair['symbol']
            change = float(pair['priceChangePercent'])
            price = float(pair['lastPrice'])
            print_data(f"  {i}. {symbol:<12} 🔴 {change:.2f}%  (${price:,.4f})")
        print()

        # Test 7: Klines (velas) de BTC
        print_info("Test 7: Velas de BTC/USDT (últimas 5 horas)...")
        klines = client.get_klines(
            symbol="BTCUSDT",
            interval=Client.KLINE_INTERVAL_1HOUR,
            limit=5
        )

        print_success("Candlesticks (1h):")
        print_data(f"\n  {'Hora':<20} {'Apertura':<12} {'Cierre':<12} {'Alto':<12} {'Bajo':<12} {'Vol':<10}")
        print_data(f"  {'-'*85}")

        for kline in klines:
            kline_time = datetime.fromtimestamp(kline[0] / 1000)
            open_p = float(kline[1])
            high_p = float(kline[2])
            low_p = float(kline[3])
            close_p = float(kline[4])
            volume = float(kline[5])

            # Indicador de vela verde/roja
            candle = "🟢" if close_p >= open_p else "🔴"

            print_data(
                f"  {kline_time.strftime('%Y-%m-%d %H:%M'):<20} "
                f"${open_p:<11,.2f} ${close_p:<11,.2f} "
                f"${high_p:<11,.2f} ${low_p:<11,.2f} {volume:<9.2f} {candle}"
            )
        print()

        # Test 8: Info de símbolos disponibles
        print_info("Test 8: Símbolos de trading disponibles...")
        exchange_info = client.get_exchange_info()
        symbols = exchange_info['symbols']

        # Contar por quote asset
        usdt_count = len([s for s in symbols if s['quoteAsset'] == 'USDT'])
        btc_count = len([s for s in symbols if s['quoteAsset'] == 'BTC'])

        print_success(f"Total de pares disponibles: {len(symbols)}")
        print_data(f"  Pares USDT: {usdt_count}")
        print_data(f"  Pares BTC: {btc_count}")
        print_data(f"  Otros: {len(symbols) - usdt_count - btc_count}")
        print()

        # Resumen final
        print_header("🎉 TODOS LOS TESTS COMPLETADOS EXITOSAMENTE")

        print_success("Funcionalidades disponibles SIN API Keys:")
        print()
        print_data("  ✅ Precios en tiempo real")
        print_data("  ✅ Order book (libro de órdenes)")
        print_data("  ✅ Trades recientes")
        print_data("  ✅ Velas/Candlesticks históricos")
        print_data("  ✅ Estadísticas 24h")
        print_data("  ✅ Rankings de volumen")
        print_data("  ✅ Información de símbolos")
        print()

        print_info("Funcionalidades que REQUIEREN API Keys con permisos:")
        print()
        print_data("  ❌ Ver balances de cuenta")
        print_data("  ❌ Crear órdenes de compra/venta")
        print_data("  ❌ Ver historial de órdenes")
        print_data("  ❌ Obtener información de cuenta")
        print()

        print_success("💡 PUEDES usar estos datos públicos para:")
        print()
        print_data("  • Análisis de precios en tiempo real")
        print_data("  • Bot de alertas de precio")
        print_data("  • Reportes de mercado automáticos")
        print_data("  • Integración con Telegram/WhatsApp para consultas")
        print_data("  • Dashboard de monitoreo de cryptos")
        print_data("  • Análisis técnico con IA (Gemini)")
        print()

        return True

    except BinanceAPIException as e:
        print_error(f"Error de API: {e.message}")
        return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
