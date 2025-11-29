#!/usr/bin/env python3
"""
Diagnóstico de conexión a Binance Testnet
Ayuda a identificar problemas de configuración
"""

import os
from dotenv import load_dotenv
from binance.client import Client
from binance.exceptions import BinanceAPIException
import sys

load_dotenv()

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_section(title):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")

print_section("🔍 DIAGNÓSTICO DE BINANCE TESTNET")

api_key = os.getenv('BINANCE_API_KEY')
secret_key = os.getenv('BINANCE_SECRET_KEY')
use_testnet = os.getenv('BINANCE_USE_TESTNET', 'true').lower() == 'true'

# Test 1: Variables de entorno
print(f"{Colors.BLUE}[1/5] Verificando variables de entorno...{Colors.RESET}")
if api_key and secret_key:
    print(f"{Colors.GREEN}✅ API Key encontrada: {api_key[:12]}...{api_key[-8:]}{Colors.RESET}")
    print(f"{Colors.GREEN}✅ Secret Key encontrada: {secret_key[:12]}...{secret_key[-8:]}{Colors.RESET}")
    print(f"{Colors.GREEN}✅ Testnet: {'ACTIVADO' if use_testnet else 'DESACTIVADO'}{Colors.RESET}")
else:
    print(f"{Colors.RED}❌ Faltan credenciales en .env{Colors.RESET}")
    sys.exit(1)

# Test 2: Conectividad básica (sin autenticación)
print(f"\n{Colors.BLUE}[2/5] Probando conectividad básica (sin autenticación)...{Colors.RESET}")
try:
    client_public = Client("", "", testnet=use_testnet)
    server_time = client_public.get_server_time()
    print(f"{Colors.GREEN}✅ Servidor Binance Testnet responde{Colors.RESET}")
    print(f"   Server time: {server_time['serverTime']}")
except Exception as e:
    print(f"{Colors.RED}❌ No se puede conectar al servidor: {e}{Colors.RESET}")
    sys.exit(1)

# Test 3: Precio público (no requiere API key)
print(f"\n{Colors.BLUE}[3/5] Obteniendo precio público (sin autenticación)...{Colors.RESET}")
try:
    ticker = client_public.get_symbol_ticker(symbol="BTCUSDT")
    print(f"{Colors.GREEN}✅ Precio BTC/USDT: ${float(ticker['price']):,.2f}{Colors.RESET}")
except Exception as e:
    print(f"{Colors.RED}❌ Error obteniendo precio: {e}{Colors.RESET}")

# Test 4: Crear cliente autenticado
print(f"\n{Colors.BLUE}[4/5] Creando cliente autenticado...{Colors.RESET}")
try:
    client = Client(
        api_key=api_key,
        api_secret=secret_key,
        testnet=use_testnet
    )
    print(f"{Colors.GREEN}✅ Cliente creado exitosamente{Colors.RESET}")
except Exception as e:
    print(f"{Colors.RED}❌ Error creando cliente: {e}{Colors.RESET}")
    sys.exit(1)

# Test 5: Verificar permisos (esto requiere API key válida)
print(f"\n{Colors.BLUE}[5/5] Verificando permisos de API Key...{Colors.RESET}")
try:
    # Intentar obtener info de cuenta
    account = client.get_account()
    print(f"{Colors.GREEN}✅ API Key válida y con permisos correctos{Colors.RESET}")
    print(f"   Tipo de cuenta: {account.get('accountType', 'N/A')}")
    print(f"   Puede tradear: {account.get('canTrade', False)}")
    print(f"   Puede depositar: {account.get('canDeposit', False)}")
    print(f"   Puede retirar: {account.get('canWithdraw', False)}")

    # Mostrar balances
    balances = [b for b in account['balances'] if float(b['free']) > 0]
    if balances:
        print(f"\n{Colors.GREEN}✅ Balances encontrados:{Colors.RESET}")
        for b in balances[:5]:
            print(f"   💰 {b['asset']}: {float(b['free']):.8f}")

    print(f"\n{Colors.BOLD}{Colors.GREEN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.GREEN}🎉 DIAGNÓSTICO EXITOSO - TODO FUNCIONA CORRECTAMENTE{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.GREEN}{'='*70}{Colors.RESET}\n")

except BinanceAPIException as e:
    print(f"{Colors.RED}❌ Error de API: {e.message}{Colors.RESET}")
    print(f"{Colors.RED}   Código: {e.code}{Colors.RESET}\n")

    if e.code == -2015:
        print(f"{Colors.YELLOW}📋 POSIBLES CAUSAS Y SOLUCIONES:{Colors.RESET}\n")
        print(f"{Colors.YELLOW}1. API Key sin permisos habilitados:{Colors.RESET}")
        print(f"   → Ve a: https://testnet.binance.vision/")
        print(f"   → Login con tu cuenta")
        print(f"   → Click en tu email (esquina superior derecha)")
        print(f"   → Selecciona 'API Keys'")
        print(f"   → Edita tu API Key existente")
        print(f"   → Habilita estos permisos:")
        print(f"     ✓ Enable Reading")
        print(f"     ✓ Enable Spot & Margin Trading")
        print(f"   → Guarda los cambios\n")

        print(f"{Colors.YELLOW}2. API Key inválida o expirada:{Colors.RESET}")
        print(f"   → Genera una nueva API Key")
        print(f"   → Actualiza el archivo .env con las nuevas credenciales\n")

        print(f"{Colors.YELLOW}3. Restricción de IP:{Colors.RESET}")
        print(f"   → Verifica si configuraste restricción de IP")
        print(f"   → Si es así, elimínala o agrega tu IP actual\n")

        print(f"{Colors.BLUE}🔗 Link directo a API Management:{Colors.RESET}")
        print(f"   https://testnet.binance.vision/\n")

    elif e.code == -1021:
        print(f"{Colors.YELLOW}📋 Problema de sincronización de tiempo:{Colors.RESET}")
        print(f"   → Ejecuta: sudo ntpdate -s time.nist.gov")
        print(f"   → O reinicia tu sistema\n")

    sys.exit(1)

except Exception as e:
    print(f"{Colors.RED}❌ Error inesperado: {str(e)}{Colors.RESET}")
    print(f"{Colors.RED}   Tipo: {type(e).__name__}{Colors.RESET}")
    sys.exit(1)
