#!/usr/bin/env python3
"""
Test de nueva API Key de Binance
Prueba exhaustiva de permisos
"""

import os
from dotenv import load_dotenv
from binance.client import Client
from binance.exceptions import BinanceAPIException
import time

# Force reload .env
load_dotenv(override=True)

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

api_key = os.getenv('BINANCE_API_KEY')
secret_key = os.getenv('BINANCE_SECRET_KEY')

print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
print(f"{Colors.BOLD}{Colors.BLUE}🔑 TEST DE NUEVA API KEY{Colors.RESET}")
print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")

print(f"{Colors.CYAN}API Key detectada:{Colors.RESET} {api_key[:12]}...{api_key[-8:]}")
print()

# Crear cliente
client = Client(
    api_key=api_key,
    api_secret=secret_key,
    testnet=True
)

tests_passed = 0
tests_total = 5

# Test 1: Server time
print(f"{Colors.BLUE}[1/5] Test de conectividad básica...{Colors.RESET}")
try:
    server_time = client.get_server_time()
    print(f"{Colors.GREEN}✅ Servidor responde{Colors.RESET}")
    print(f"   Hora del servidor: {server_time['serverTime']}")
    tests_passed += 1
except Exception as e:
    print(f"{Colors.RED}❌ Error: {e}{Colors.RESET}")

print()

# Test 2: API Key Status (get_account_api_key_permissions)
print(f"{Colors.BLUE}[2/5] Verificando permisos de API Key...{Colors.RESET}")
try:
    # Try to get API permissions (v3 endpoint)
    permissions = client.get_account_api_trading_status()
    print(f"{Colors.GREEN}✅ Permisos obtenidos{Colors.RESET}")
    print(f"   Data: {permissions}")
    tests_passed += 1
except BinanceAPIException as e:
    print(f"{Colors.YELLOW}⚠️  Error API: {e.message} (código: {e.code}){Colors.RESET}")
    if e.code == -2015:
        print(f"{Colors.RED}   → API Key sin permisos o IP bloqueada{Colors.RESET}")
except Exception as e:
    print(f"{Colors.YELLOW}⚠️  Error: {type(e).__name__}: {e}{Colors.RESET}")

print()

# Test 3: Intentar obtener cuenta (requiere lectura)
print(f"{Colors.BLUE}[3/5] Intentando leer información de cuenta...{Colors.RESET}")
try:
    account = client.get_account()
    print(f"{Colors.GREEN}✅ Cuenta accesible{Colors.RESET}")
    print(f"   Tipo: {account.get('accountType', 'N/A')}")
    print(f"   Puede tradear: {account.get('canTrade', False)}")
    print(f"   Puede depositar: {account.get('canDeposit', False)}")
    print(f"   Puede retirar: {account.get('canWithdraw', False)}")

    # Balances
    balances = [b for b in account['balances'] if float(b['free']) > 0]
    if balances:
        print(f"\n{Colors.GREEN}   Balances:{Colors.RESET}")
        for b in balances[:5]:
            print(f"     💰 {b['asset']}: {float(b['free']):.8f}")

    tests_passed += 1
except BinanceAPIException as e:
    print(f"{Colors.YELLOW}⚠️  Error API: {e.message} (código: {e.code}){Colors.RESET}")
    if e.code == -2015:
        print(f"{Colors.RED}   → API Key NO tiene permiso de lectura habilitado{Colors.RESET}")
    elif e.code == -2014:
        print(f"{Colors.RED}   → API Key inválida o expirada{Colors.RESET}")
except Exception as e:
    print(f"{Colors.YELLOW}⚠️  Error: {type(e).__name__}: {e}{Colors.RESET}")

print()

# Test 4: Intentar obtener órdenes (requiere lectura)
print(f"{Colors.BLUE}[4/5] Intentando leer órdenes...{Colors.RESET}")
try:
    orders = client.get_all_orders(symbol='BTCUSDT', limit=1)
    print(f"{Colors.GREEN}✅ Órdenes accesibles (total: {len(orders)}){Colors.RESET}")
    tests_passed += 1
except BinanceAPIException as e:
    print(f"{Colors.YELLOW}⚠️  Error API: {e.message} (código: {e.code}){Colors.RESET}")
except Exception as e:
    print(f"{Colors.YELLOW}⚠️  Error: {type(e).__name__}: {e}{Colors.RESET}")

print()

# Test 5: Intentar crear orden TEST (no se ejecuta, solo validación)
print(f"{Colors.BLUE}[5/5] Intentando crear orden TEST (no se ejecuta)...{Colors.RESET}")
try:
    # Test order (no se ejecuta realmente)
    test_order = client.create_test_order(
        symbol='BTCUSDT',
        side='BUY',
        type='MARKET',
        quantity=0.001
    )
    print(f"{Colors.GREEN}✅ Orden TEST validada (permisos de trading OK){Colors.RESET}")
    tests_passed += 1
except BinanceAPIException as e:
    print(f"{Colors.YELLOW}⚠️  Error API: {e.message} (código: {e.code}){Colors.RESET}")
    if e.code == -2015:
        print(f"{Colors.RED}   → API Key NO tiene permiso de trading habilitado{Colors.RESET}")
except Exception as e:
    print(f"{Colors.YELLOW}⚠️  Error: {type(e).__name__}: {e}{Colors.RESET}")

print()

# RESUMEN
print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
print(f"{Colors.BOLD}📊 RESUMEN{Colors.RESET}")
print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")

score = (tests_passed / tests_total) * 100

print(f"Tests pasados: {tests_passed}/{tests_total} ({score:.0f}%)\n")

if tests_passed == tests_total:
    print(f"{Colors.BOLD}{Colors.GREEN}🎉 ¡PERFECTO! API Key completamente funcional{Colors.RESET}")
    print(f"{Colors.GREEN}   Todos los permisos están habilitados correctamente{Colors.RESET}\n")
elif tests_passed >= 3:
    print(f"{Colors.YELLOW}⚠️  API Key parcialmente funcional{Colors.RESET}")
    print(f"{Colors.YELLOW}   Algunos permisos necesitan ser habilitados{Colors.RESET}\n")
    print(f"{Colors.CYAN}🔧 SOLUCIÓN:{Colors.RESET}")
    print(f"   1. Ve a https://testnet.binance.vision/")
    print(f"   2. Login → Click tu email → API Keys")
    print(f"   3. Edita la API Key: {api_key[:12]}...{api_key[-8:]}")
    print(f"   4. Habilita TODOS los permisos:")
    print(f"      ✓ Enable Reading")
    print(f"      ✓ Enable Spot & Margin Trading")
    print(f"   5. Guarda cambios\n")
elif tests_passed >= 1:
    print(f"{Colors.RED}❌ API Key tiene problemas serios{Colors.RESET}")
    print(f"{Colors.RED}   La mayoría de funciones no están disponibles{Colors.RESET}\n")
    print(f"{Colors.CYAN}🔧 SOLUCIONES POSIBLES:{Colors.RESET}")
    print(f"   1. Verifica que la API Key sea correcta")
    print(f"   2. Habilita TODOS los permisos en Binance")
    print(f"   3. Elimina restricciones de IP (si las hay)")
    print(f"   4. Espera 2-3 minutos después de cambiar permisos\n")
else:
    print(f"{Colors.RED}❌ API Key NO funcional{Colors.RESET}")
    print(f"{Colors.RED}   Ningún test pasó - API Key inválida o sin acceso{Colors.RESET}\n")
    print(f"{Colors.CYAN}🔧 GENERA UNA NUEVA API KEY:{Colors.RESET}")
    print(f"   1. Ve a https://testnet.binance.vision/")
    print(f"   2. Login → API Keys → Generate New Key")
    print(f"   3. Habilita ambos permisos desde el inicio")
    print(f"   4. Actualiza el .env con las nuevas credenciales\n")
