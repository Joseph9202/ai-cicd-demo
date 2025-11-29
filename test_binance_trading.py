#!/usr/bin/env python3
"""
Test de Trading en Binance Testnet
Realiza operaciones de compra/venta simuladas (sin riesgo)
⚠️ SOLO PARA TESTNET - No usar en producción sin modificaciones
"""

import os
from dotenv import load_dotenv
from binance.client import Client
from binance.exceptions import BinanceAPIException
import sys
from datetime import datetime
import time

# Cargar variables de entorno
load_dotenv()

# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.RESET}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.RESET}")

def print_trade(message):
    print(f"{Colors.MAGENTA}💹 {message}{Colors.RESET}")

def print_header(message):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{message}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def get_balance(client, asset):
    """Obtener balance de un asset específico"""
    account = client.get_account()
    for balance in account['balances']:
        if balance['asset'] == asset:
            return float(balance['free'])
    return 0.0

def test_trading():
    """Test de operaciones de trading"""

    print_header("💹 TEST DE TRADING - BINANCE TESTNET")
    print_warning("IMPORTANTE: Este script solo funciona en TESTNET")
    print_warning("NO ejecutar en cuenta real sin modificaciones")
    print()

    api_key = os.getenv('BINANCE_API_KEY')
    secret_key = os.getenv('BINANCE_SECRET_KEY')
    use_testnet = os.getenv('BINANCE_USE_TESTNET', 'true').lower() == 'true'
    trading_pair = os.getenv('DEFAULT_TRADING_PAIR', 'BTCUSDT')

    if not use_testnet:
        print_error("Este script requiere BINANCE_USE_TESTNET=true")
        print_error("No se ejecutará en cuenta real por seguridad")
        sys.exit(1)

    if not api_key or not secret_key:
        print_error("Configura tu archivo .env primero")
        sys.exit(1)

    try:
        client = Client(
            api_key=api_key,
            api_secret=secret_key,
            testnet=use_testnet
        )

        # Extraer base y quote asset
        base_asset = trading_pair.replace('USDT', '').replace('BUSD', '')
        quote_asset = 'USDT' if 'USDT' in trading_pair else 'BUSD'

        print_info(f"Par de trading: {trading_pair}")
        print_info(f"Base asset: {base_asset}")
        print_info(f"Quote asset: {quote_asset}")
        print()

        # Test 1: Verificar balances iniciales
        print_info("Test 1: Verificando balances iniciales...")
        initial_base = get_balance(client, base_asset)
        initial_quote = get_balance(client, quote_asset)

        print_success(f"Balance inicial {base_asset}: {initial_base:.8f}")
        print_success(f"Balance inicial {quote_asset}: {initial_quote:.2f}")
        print()

        # Obtener precio actual
        ticker = client.get_symbol_ticker(symbol=trading_pair)
        current_price = float(ticker['price'])
        print_info(f"Precio actual de {trading_pair}: ${current_price:,.2f}")
        print()

        # Test 2: Información del símbolo (límites)
        print_info("Test 2: Obteniendo límites de trading...")
        symbol_info = client.get_symbol_info(trading_pair)

        min_qty = 0.0
        max_qty = 0.0
        step_size = 0.0
        min_notional = 0.0

        for f in symbol_info['filters']:
            if f['filterType'] == 'LOT_SIZE':
                min_qty = float(f['minQty'])
                max_qty = float(f['maxQty'])
                step_size = float(f['stepSize'])
            elif f['filterType'] == 'MIN_NOTIONAL':
                min_notional = float(f.get('minNotional', 0))

        print_success(f"Cantidad mínima: {min_qty}")
        print_success(f"Cantidad máxima: {max_qty}")
        print_success(f"Step size: {step_size}")
        print_success(f"Valor mínimo de orden: ${min_notional}")
        print()

        # Test 3: Crear orden LIMIT de COMPRA (test)
        print_info("Test 3: Creando orden TEST de compra (no se ejecutará)...")

        # Calcular cantidad pequeña para test
        test_amount_usdt = 50.0  # Comprar por $50 USDT
        test_quantity = test_amount_usdt / current_price

        # Ajustar a step size
        test_quantity = round(test_quantity / step_size) * step_size

        # Precio límite 1% por debajo del actual (más probable de ejecutarse)
        limit_price = current_price * 0.99
        limit_price = round(limit_price, 2)

        print_trade(f"Intentando comprar {test_quantity:.8f} {base_asset}")
        print_trade(f"Precio límite: ${limit_price:,.2f}")
        print_trade(f"Valor total: ${test_quantity * limit_price:.2f}")
        print()

        try:
            # Orden TEST (no se ejecuta realmente)
            test_order = client.create_test_order(
                symbol=trading_pair,
                side=Client.SIDE_BUY,
                type=Client.ORDER_TYPE_LIMIT,
                timeInForce=Client.TIME_IN_FORCE_GTC,
                quantity=test_quantity,
                price=f"{limit_price:.2f}"
            )
            print_success("✅ Orden TEST de compra: VÁLIDA")
            print_info("(No se ejecutó realmente - solo validación)")
        except BinanceAPIException as e:
            print_error(f"Orden TEST falló: {e.message}")
            print_info("Ajusta los parámetros según los límites del símbolo")

        print()

        # Test 4: Crear orden MARKET de COMPRA REAL (pequeña cantidad)
        print_info("Test 4: ¿Deseas crear una orden REAL de compra?")
        print_warning("Esto ejecutará una compra REAL en el testnet")
        print_info(f"Comprarás aproximadamente {test_quantity:.8f} {base_asset}")
        print_info(f"Costo aproximado: ${test_amount_usdt:.2f} USDT")
        print()

        response = input("¿Continuar? (escribe 'SI' para confirmar): ")

        if response.strip().upper() == 'SI':
            print_info("Ejecutando orden de compra MARKET...")

            try:
                # Orden MARKET real
                order = client.order_market_buy(
                    symbol=trading_pair,
                    quantity=test_quantity
                )

                print_success("🎉 ORDEN DE COMPRA EJECUTADA!")
                print_trade(f"Order ID: {order['orderId']}")
                print_trade(f"Status: {order['status']}")
                print_trade(f"Símbolo: {order['symbol']}")
                print_trade(f"Lado: {order['side']}")
                print_trade(f"Tipo: {order['type']}")
                print_trade(f"Cantidad: {order['origQty']}")
                print_trade(f"Precio promedio: {order.get('fills', [{}])[0].get('price', 'N/A')}")

                # Calcular comisión
                total_commission = 0.0
                commission_asset = ''
                if 'fills' in order:
                    for fill in order['fills']:
                        total_commission += float(fill['commission'])
                        commission_asset = fill['commissionAsset']

                if total_commission > 0:
                    print_trade(f"Comisión: {total_commission} {commission_asset}")

                print()

                # Esperar un momento para que se actualice la cuenta
                time.sleep(2)

                # Verificar nuevo balance
                new_base = get_balance(client, base_asset)
                new_quote = get_balance(client, quote_asset)

                print_success(f"Nuevo balance {base_asset}: {new_base:.8f} (antes: {initial_base:.8f})")
                print_success(f"Nuevo balance {quote_asset}: {new_quote:.2f} (antes: {initial_quote:.2f})")

                # Test 5: Obtener órdenes recientes
                print()
                print_info("Test 5: Obteniendo órdenes recientes...")
                recent_orders = client.get_all_orders(symbol=trading_pair, limit=5)

                print_success(f"Últimas {len(recent_orders)} órdenes:")
                for i, o in enumerate(recent_orders[-5:], 1):
                    order_time = datetime.fromtimestamp(o['time'] / 1000)
                    print_trade(
                        f"{i}. ID: {o['orderId']} | "
                        f"{o['side']} | "
                        f"{o['type']} | "
                        f"{o['status']} | "
                        f"Qty: {o['origQty']} | "
                        f"{order_time.strftime('%Y-%m-%d %H:%M:%S')}"
                    )

                print()

                # Test 6: Vender lo que compramos (opcional)
                print_info("Test 6: ¿Deseas vender lo que acabas de comprar?")
                print_warning("Esto cerrará la posición")
                print()

                sell_response = input("¿Vender ahora? (escribe 'SI' para confirmar): ")

                if sell_response.strip().upper() == 'SI':
                    # Calcular cantidad a vender (lo que compramos)
                    sell_quantity = new_base - initial_base
                    sell_quantity = round(sell_quantity / step_size) * step_size

                    if sell_quantity > min_qty:
                        print_info(f"Vendiendo {sell_quantity:.8f} {base_asset}...")

                        sell_order = client.order_market_sell(
                            symbol=trading_pair,
                            quantity=sell_quantity
                        )

                        print_success("🎉 ORDEN DE VENTA EJECUTADA!")
                        print_trade(f"Order ID: {sell_order['orderId']}")
                        print_trade(f"Status: {sell_order['status']}")
                        print_trade(f"Cantidad vendida: {sell_order['origQty']}")

                        time.sleep(2)

                        final_quote = get_balance(client, quote_asset)
                        profit_loss = final_quote - initial_quote

                        print()
                        print_success(f"Balance final {quote_asset}: {final_quote:.2f}")
                        if profit_loss > 0:
                            print_success(f"✅ Ganancia: ${profit_loss:.2f}")
                        elif profit_loss < 0:
                            print_error(f"❌ Pérdida: ${abs(profit_loss):.2f}")
                        else:
                            print_info("Neutro: $0.00")

                    else:
                        print_warning("Cantidad a vender es menor que el mínimo permitido")
                else:
                    print_info("Venta cancelada - manteniendo posición")

            except BinanceAPIException as e:
                print_error(f"Error en la orden: {e.message}")
                print_error(f"Código: {e.code}")
                print()
                print_info("Posibles causas:")
                print("  - Fondos insuficientes")
                print("  - Cantidad menor que el mínimo")
                print("  - Permisos de API insuficientes")
                return False

        else:
            print_info("Orden cancelada por el usuario")

        print()
        print_header("🎉 TESTS DE TRADING COMPLETADOS")
        print_success("Has probado exitosamente el sistema de trading")
        print()
        print_info("Recordatorios importantes:")
        print("  ✅ Siempre usa testnet para experimentos")
        print("  ✅ Implementa gestión de riesgos antes de producción")
        print("  ✅ Monitorea tus órdenes activas")
        print("  ✅ Verifica balances antes y después de tradear")
        print("  ✅ Mantén tus API keys seguras")
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
    success = test_trading()
    sys.exit(0 if success else 1)
