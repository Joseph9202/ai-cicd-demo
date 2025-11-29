# 🚀 Alternativa: Binance Futures Testnet (MÁS FÁCIL)

Si no encuentras las opciones en Binance Spot Testnet, usa Futures Testnet que tiene mejor interfaz.

## Paso 1: Crear cuenta en Futures Testnet

1. Ve a: **https://testnet.binancefuture.com/**
2. Click en **"Log In"**
3. Puedes usar:
   - **GitHub** (login rápido - recomendado)
   - **Email** (registro tradicional)

## Paso 2: Obtener API Keys

1. Una vez logueado, mira la esquina **superior derecha**
2. Click en el **ícono de tu perfil** o **email**
3. Selecciona **"API Management"**

O ve directamente a:
```
https://testnet.binancefuture.com/en/futures/BTCUSDT
```

Luego click en tu perfil → API Management

## Paso 3: Generar API Key

1. Click **"Create API"**
2. Los permisos se habilitan automáticamente ✅
3. Copia tu **API Key** y **Secret Key**

## Paso 4: Actualizar .env

```bash
nano .env
```

Actualiza con las nuevas credenciales:
```env
BINANCE_API_KEY=tu_nueva_key_de_futures
BINANCE_SECRET_KEY=tu_nueva_secret_de_futures
BINANCE_USE_TESTNET=true
DEFAULT_TRADING_PAIR=BTCUSDT
```

## Paso 5: Ejecutar test

```bash
python diagnose_binance.py
```

## Ventajas de Futures Testnet

✅ Interfaz más moderna
✅ Login con GitHub (sin email)
✅ Permisos se habilitan automáticamente
✅ Misma funcionalidad que Spot Testnet
✅ Más fondos iniciales para testing

## Diferencias

- Futures Testnet usa contratos de futuros (pero puedes usar spot trading también)
- El código Python funciona igual
- Los tests funcionan exactamente igual

---

**¿Prefieres probar esta alternativa?** Es más rápida y fácil.
