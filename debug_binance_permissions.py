#!/usr/bin/env python3
"""
Debug detallado de permisos de Binance
"""

import os
import time
import hmac
import hashlib
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

API_KEY = os.getenv('BINANCE_API_KEY')
SECRET_KEY = os.getenv('BINANCE_SECRET_KEY')
BASE_URL = 'https://testnet.binance.vision'

print(f"\n{'='*70}")
print("🔍 DEBUG DETALLADO DE BINANCE API")
print(f"{'='*70}\n")

print(f"API Key: {API_KEY[:15]}...{API_KEY[-10:]}")
print(f"Base URL: {BASE_URL}\n")

# Test 1: Endpoint público (sin firma)
print(f"[1/4] Test endpoint público (sin autenticación)...")
try:
    response = requests.get(f"{BASE_URL}/api/v3/time")
    if response.status_code == 200:
        print(f"✅ Público OK: {response.json()}")
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
except Exception as e:
    print(f"❌ Excepción: {e}")

print()

# Test 2: Account info con firma HMAC
print(f"[2/4] Test endpoint con autenticación (account info)...")

timestamp = int(time.time() * 1000)
params = f"timestamp={timestamp}"

# Crear firma HMAC
signature = hmac.new(
    SECRET_KEY.encode('utf-8'),
    params.encode('utf-8'),
    hashlib.sha256
).hexdigest()

headers = {
    'X-MBX-APIKEY': API_KEY
}

url = f"{BASE_URL}/api/v3/account?{params}&signature={signature}"

try:
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Cuenta accesible!")
        print(f"   Account Type: {data.get('accountType', 'N/A')}")
        print(f"   Can Trade: {data.get('canTrade', False)}")
        print(f"   Can Deposit: {data.get('canDeposit', False)}")
        print(f"   Can Withdraw: {data.get('canWithdraw', False)}")

        balances = [b for b in data.get('balances', []) if float(b['free']) > 0]
        if balances:
            print(f"\n   Balances:")
            for b in balances[:5]:
                print(f"     💰 {b['asset']}: {float(b['free']):.8f}")
    else:
        error_data = response.json()
        print(f"❌ Error {response.status_code}: {error_data}")
        print(f"   Código: {error_data.get('code', 'N/A')}")
        print(f"   Mensaje: {error_data.get('msg', 'N/A')}")

except Exception as e:
    print(f"❌ Excepción: {type(e).__name__}: {e}")

print()

# Test 3: API Key permissions (nuevo endpoint)
print(f"[3/4] Test de permisos de API Key...")

timestamp = int(time.time() * 1000)
params = f"timestamp={timestamp}"

signature = hmac.new(
    SECRET_KEY.encode('utf-8'),
    params.encode('utf-8'),
    hashlib.sha256
).hexdigest()

headers = {
    'X-MBX-APIKEY': API_KEY
}

url = f"{BASE_URL}/sapi/v1/account/apiRestrictions?{params}&signature={signature}"

try:
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Permisos de API:")
        print(f"   {data}")
    else:
        error_data = response.json()
        print(f"⚠️  Endpoint no disponible o error:")
        print(f"   {error_data}")

except Exception as e:
    print(f"⚠️  Excepción: {type(e).__name__}: {e}")

print()

# Test 4: System status
print(f"[4/4] Test de estado del sistema...")

try:
    response = requests.get(f"{BASE_URL}/sapi/v1/system/status")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Sistema: {data}")
    else:
        print(f"⚠️  Status: {response.status_code}")
except Exception as e:
    print(f"⚠️  Excepción: {type(e).__name__}: {e}")

print()
print(f"{'='*70}")
print("📋 ANÁLISIS")
print(f"{'='*70}\n")

print("Si el Test 1 pasa pero el Test 2 falla con código -2015:")
print("  → Los permisos NO están realmente habilitados en Binance")
print("  → O hay una restricción de IP activa")
print()
print("Verifica en Binance Testnet:")
print("  1. Que los checkboxes estén REALMENTE marcados")
print("  2. Que hayas hecho click en 'Save' o 'Update'")
print("  3. Que la API Key sea la correcta")
print()
