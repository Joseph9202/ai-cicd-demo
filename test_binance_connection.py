#!/usr/bin/env python3
"""
Test de Conexión a Binance Testnet
Verifica que las credenciales y configuración sean correctas
"""

import os
from dotenv import load_dotenv
from binance.client import Client
from binance.exceptions import BinanceAPIException
import sys

# Cargar variables de entorno
load_dotenv()

# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
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

def print_header(message):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{message}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def test_connection():
    """Test básico de conexión a Binance Testnet"""

    print_header("🚀 TEST DE CONEXIÓN BINANCE TESTNET")

    # Verificar variables de entorno
    print_info("Verificando configuración...")

    api_key = os.getenv('BINANCE_API_KEY')
    secret_key = os.getenv('BINANCE_SECRET_KEY')
    use_testnet = os.getenv('BINANCE_USE_TESTNET', 'true').lower() == 'true'

    if not api_key or not secret_key:
        print_error("API_KEY o SECRET_KEY no encontradas en .env")
        print_info("Por favor, configura tu archivo .env según BINANCE_TESTNET_SETUP.md")
        sys.exit(1)

    # Mostrar configuración (parcial por seguridad)
    print_success("Variables de entorno cargadas")
    print(f"  API Key: {api_key[:8]}...{api_key[-8:]}")
    print(f"  Secret Key: {secret_key[:8]}...{secret_key[-8:]}")
    print(f"  Testnet: {'ACTIVADO' if use_testnet else 'DESACTIVADO'}")
    print()

    try:
        # Crear cliente de Binance
        print_info("Conectando a Binance Testnet...")

        client = Client(
            api_key=api_key,
            api_secret=secret_key,
            testnet=use_testnet
        )

        # Test 1: Verificar conectividad
        print_info("Test 1: Verificando conectividad...")
        server_time = client.get_server_time()
        print_success(f"Servidor respondiendo - Timestamp: {server_time['serverTime']}")

        # Test 2: Verificar cuenta
        print_info("Test 2: Verificando información de cuenta...")
        account_info = client.get_account()
        print_success(f"Cuenta configurada correctamente")
        print(f"  Tipo de cuenta: {account_info.get('accountType', 'N/A')}")
        print(f"  Puede tradear: {account_info.get('canTrade', False)}")
        print(f"  Puede depositar: {account_info.get('canDeposit', False)}")
        print(f"  Puede retirar: {account_info.get('canWithdraw', False)}")
        print()

        # Test 3: Obtener balances
        print_info("Test 3: Obteniendo balances...")
        balances = account_info['balances']

        # Filtrar balances con fondos
        non_zero_balances = [
            b for b in balances
            if float(b['free']) > 0 or float(b['locked']) > 0
        ]

        if non_zero_balances:
            print_success(f"Balances encontrados ({len(non_zero_balances)} assets):")
            for balance in non_zero_balances[:10]:  # Mostrar primeros 10
                asset = balance['asset']
                free = float(balance['free'])
                locked = float(balance['locked'])
                total = free + locked

                if total > 0:
                    print(f"  💰 {asset}: {total:.8f} (Libre: {free:.8f}, Bloqueado: {locked:.8f})")
        else:
            print_warning("No se encontraron balances")
            print_info("Solicita fondos ficticios en: https://testnet.binance.vision/")

        print()

        # Test 4: Obtener precio actual de BTC/USDT
        print_info("Test 4: Obteniendo precio actual de BTCUSDT...")
        ticker = client.get_symbol_ticker(symbol="BTCUSDT")
        print_success(f"Precio BTC/USDT: ${float(ticker['price']):,.2f}")

        # Test 5: Verificar límites de la API
        print_info("Test 5: Verificando límites de rate...")
        exchange_info = client.get_exchange_info()
        rate_limits = exchange_info['rateLimits']
        print_success("Límites de rate configurados:")
        for limit in rate_limits:
            interval = limit.get('interval', 'N/A')
            limit_type = limit.get('rateLimitType', 'N/A')
            max_limit = limit.get('limit', 'N/A')
            print(f"  - {limit_type}: {max_limit} por {interval}")

        print()
        print_header("🎉 TODOS LOS TESTS PASARON EXITOSAMENTE")
        print_success("Tu conexión a Binance Testnet está funcionando correctamente")
        print_info("Próximos pasos:")
        print("  1. Ejecuta: python test_binance_market.py")
        print("  2. Ejecuta: python test_binance_trading.py")
        print()

        return True

    except BinanceAPIException as e:
        print_error(f"Error de API de Binance: {e.message}")
        print_error(f"Código de error: {e.code}")
        print()
        print_info("Posibles soluciones:")
        print("  1. Verifica que tu API Key y Secret sean correctos")
        print("  2. Revisa los permisos de tu API Key")
        print("  3. Verifica que BINANCE_USE_TESTNET=true en .env")
        print("  4. Consulta BINANCE_TESTNET_SETUP.md sección Troubleshooting")
        return False

    except Exception as e:
        print_error(f"Error inesperado: {str(e)}")
        print_error(f"Tipo de error: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
