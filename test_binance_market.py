#!/usr/bin/env python3
"""
Test de Datos de Mercado en Binance Testnet
Obtiene información de precios, orderbook, y datos históricos
"""

import os
from dotenv import load_dotenv
from binance.client import Client
from binance.exceptions import BinanceAPIException
import sys
from datetime import datetime, timedelta

# Cargar variables de entorno
load_dotenv()

# Colores para terminal
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
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{message}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def test_market_data():
    """Test de obtención de datos de mercado"""

    print_header("📊 TEST DE DATOS DE MERCADO - BINANCE TESTNET")

    api_key = os.getenv('BINANCE_API_KEY')
    secret_key = os.getenv('BINANCE_SECRET_KEY')
    use_testnet = os.getenv('BINANCE_USE_TESTNET', 'true').lower() == 'true'
    trading_pair = os.getenv('DEFAULT_TRADING_PAIR', 'BTCUSDT')

    if not api_key or not secret_key:
        print_error("Configura tu archivo .env primero")
        sys.exit(1)

    try:
        client = Client(
            api_key=api_key,
            api_secret=secret_key,
            testnet=use_testnet
        )

        # Test 1: Precio actual
        print_info(f"Test 1: Obteniendo precio actual de {trading_pair}...")
        ticker = client.get_symbol_ticker(symbol=trading_pair)
        current_price = float(ticker['price'])
        print_success(f"Precio actual: ${current_price:,.2f}")
        print()

        # Test 2: Estadísticas 24h
        print_info(f"Test 2: Estadísticas de las últimas 24 horas...")
        stats = client.get_ticker(symbol=trading_pair)

        print_success("Estadísticas 24h:")
        print_data(f"  📈 Precio más alto: ${float(stats['highPrice']):,.2f}")
        print_data(f"  📉 Precio más bajo: ${float(stats['lowPrice']):,.2f}")
        print_data(f"  💹 Cambio de precio: {float(stats['priceChange']):,.2f}")
        print_data(f"  📊 Cambio %: {float(stats['priceChangePercent']):.2f}%")
        print_data(f"  💰 Volumen: {float(stats['volume']):,.2f} {trading_pair[:3]}")
        print_data(f"  💵 Volumen en quote: ${float(stats['quoteVolume']):,.2f}")
        print_data(f"  🔢 Número de trades: {stats['count']}")
        print()

        # Test 3: Order Book (libro de órdenes)
        print_info(f"Test 3: Obteniendo order book...")
        depth = client.get_order_book(symbol=trading_pair, limit=5)

        print_success("Top 5 órdenes de compra (bids):")
        for i, bid in enumerate(depth['bids'][:5], 1):
            price, qty = float(bid[0]), float(bid[1])
            total = price * qty
            print_data(f"  {i}. Precio: ${price:,.2f} | Cantidad: {qty:.8f} | Total: ${total:,.2f}")

        print()
        print_success("Top 5 órdenes de venta (asks):")
        for i, ask in enumerate(depth['asks'][:5], 1):
            price, qty = float(ask[0]), float(ask[1])
            total = price * qty
            print_data(f"  {i}. Precio: ${price:,.2f} | Cantidad: {qty:.8f} | Total: ${total:,.2f}")

        # Calcular spread
        best_bid = float(depth['bids'][0][0])
        best_ask = float(depth['asks'][0][0])
        spread = best_ask - best_bid
        spread_percent = (spread / best_bid) * 100

        print()
        print_data(f"  📊 Spread: ${spread:.2f} ({spread_percent:.4f}%)")
        print()

        # Test 4: Trades recientes
        print_info(f"Test 4: Obteniendo últimos trades...")
        trades = client.get_recent_trades(symbol=trading_pair, limit=5)

        print_success("Últimos 5 trades:")
        for i, trade in enumerate(trades[:5], 1):
            price = float(trade['price'])
            qty = float(trade['qty'])
            time = datetime.fromtimestamp(trade['time'] / 1000)
            is_buyer_maker = trade['isBuyerMaker']
            side = "🔴 VENTA" if is_buyer_maker else "🟢 COMPRA"

            print_data(f"  {i}. {side} | Precio: ${price:,.2f} | Cantidad: {qty:.8f} | {time.strftime('%H:%M:%S')}")
        print()

        # Test 5: Velas (Klines/Candlesticks)
        print_info(f"Test 5: Obteniendo velas (últimas 5 horas)...")
        klines = client.get_klines(
            symbol=trading_pair,
            interval=Client.KLINE_INTERVAL_1HOUR,
            limit=5
        )

        print_success("Últimas 5 velas (1 hora):")
        print_data(f"  {'Hora':<20} {'Apertura':<12} {'Cierre':<12} {'Máximo':<12} {'Mínimo':<12} {'Volumen':<12}")
        print_data(f"  {'-'*80}")

        for kline in klines:
            time = datetime.fromtimestamp(kline[0] / 1000)
            open_price = float(kline[1])
            high_price = float(kline[2])
            low_price = float(kline[3])
            close_price = float(kline[4])
            volume = float(kline[5])

            print_data(
                f"  {time.strftime('%Y-%m-%d %H:%M'):<20} "
                f"${open_price:<11,.2f} "
                f"${close_price:<11,.2f} "
                f"${high_price:<11,.2f} "
                f"${low_price:<11,.2f} "
                f"{volume:<11,.2f}"
            )
        print()

        # Test 6: Información del símbolo
        print_info(f"Test 6: Información del símbolo {trading_pair}...")
        exchange_info = client.get_exchange_info()

        symbol_info = None
        for s in exchange_info['symbols']:
            if s['symbol'] == trading_pair:
                symbol_info = s
                break

        if symbol_info:
            print_success(f"Configuración de {trading_pair}:")
            print_data(f"  Estado: {symbol_info['status']}")
            print_data(f"  Base Asset: {symbol_info['baseAsset']}")
            print_data(f"  Quote Asset: {symbol_info['quoteAsset']}")
            print_data(f"  Órdenes permitidas: {', '.join(symbol_info['orderTypes'])}")

            # Filtros
            print_data(f"\n  Filtros de trading:")
            for filter_item in symbol_info['filters']:
                if filter_item['filterType'] == 'PRICE_FILTER':
                    print_data(f"    - Precio mínimo: {filter_item['minPrice']}")
                    print_data(f"    - Precio máximo: {filter_item['maxPrice']}")
                elif filter_item['filterType'] == 'LOT_SIZE':
                    print_data(f"    - Cantidad mínima: {filter_item['minQty']}")
                    print_data(f"    - Cantidad máxima: {filter_item['maxQty']}")
                elif filter_item['filterType'] == 'MIN_NOTIONAL':
                    print_data(f"    - Valor mínimo de orden: {filter_item.get('minNotional', 'N/A')}")

        print()

        # Test 7: Top cryptos
        print_info("Test 7: Top 10 pares por volumen (24h)...")
        all_tickers = client.get_ticker()

        # Filtrar solo pares USDT y ordenar por volumen
        usdt_pairs = [
            t for t in all_tickers
            if t['symbol'].endswith('USDT') and float(t['quoteVolume']) > 0
        ]
        usdt_pairs.sort(key=lambda x: float(x['quoteVolume']), reverse=True)

        print_success("Top 10 pares USDT por volumen:")
        for i, pair in enumerate(usdt_pairs[:10], 1):
            symbol = pair['symbol']
            price = float(pair['lastPrice'])
            change = float(pair['priceChangePercent'])
            volume = float(pair['quoteVolume'])

            change_indicator = "🟢" if change >= 0 else "🔴"
            print_data(
                f"  {i:2d}. {symbol:<12} | "
                f"${price:>12,.2f} | "
                f"{change_indicator} {change:>6.2f}% | "
                f"Vol: ${volume:>15,.0f}"
            )

        print()
        print_header("🎉 TODOS LOS TESTS DE MERCADO COMPLETADOS")
        print_success("Los datos de mercado están disponibles y funcionando")
        print_info("Próximo paso: python test_binance_trading.py")
        print()

        return True

    except BinanceAPIException as e:
        print_error(f"Error de API: {e.message}")
        return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_market_data()
    sys.exit(0 if success else 1)
