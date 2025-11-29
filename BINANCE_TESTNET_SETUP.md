# 🚀 Configuración de Binance Testnet - Guía Paso a Paso

Esta guía te ayudará a configurar una cuenta de prueba (demo) de Binance para testing sin riesgo financiero.

---

## 📋 Tabla de Contenidos
1. [Crear cuenta en Binance Testnet](#1-crear-cuenta-en-binance-testnet)
2. [Obtener API Keys](#2-obtener-api-keys)
3. [Configurar el proyecto](#3-configurar-el-proyecto)
4. [Ejecutar tests](#4-ejecutar-tests)
5. [Troubleshooting](#5-troubleshooting)

---

## 1. Crear Cuenta en Binance Testnet

### Opción A: Binance Spot Testnet (Recomendado para empezar)

**Paso 1.1:** Ir a Binance Testnet
- 🌐 **URL:** https://testnet.binance.vision/
- No requiere registro de Binance real
- Dinero ficticio para pruebas

**Paso 1.2:** Crear cuenta
1. Click en **"Register"** (esquina superior derecha)
2. Ingresa un email válido (recibirás confirmación)
3. Crea una contraseña segura
4. Confirma tu email

**Paso 1.3:** Login
- Usa tus credenciales para acceder
-Recibirás **1000 USDT** y **10 BTC** ficticios automáticamente

---

### Opción B: Binance Futures Testnet (Para trading de futuros)

**Paso 1.1:** Ir a Futures Testnet
- 🌐 **URL:** https://testnet.binancefuture.com/
- Similar al Spot Testnet

**Paso 1.2:** Autenticación
- Puedes usar GitHub para login rápido
- O crear cuenta con email

---

## 2. Obtener API Keys

### Paso 2.1: Navegar a API Management

**Para Spot Testnet:**
1. Login en https://testnet.binance.vision/
2. Click en tu email (esquina superior derecha)
3. Selecciona **"API Keys"**

**Para Futures Testnet:**
1. Login en https://testnet.binancefuture.com/
2. Click en tu perfil
3. Selecciona **"API Keys"**

### Paso 2.2: Generar nuevas API Keys

1. Click en **"Generate HMAC_SHA256 Key"** o **"Create API"**
2. **Importante:** Escribe un label/nombre descriptivo
   - Ejemplo: `"testing-local-dev"`
3. Click **"Generate"**

### Paso 2.3: Guardar credenciales de forma SEGURA

⚠️ **MUY IMPORTANTE:**
- Te mostrarán **API Key** y **Secret Key** solo UNA VEZ
- Cópialas inmediatamente
- Guárdalas en un lugar seguro (usaremos archivo `.env`)

**Ejemplo de credenciales (NO REALES):**
```
API Key: vmPUZE6mv9SD5VNHk4HlWFsOr6aKE2zvsw0MuIgwCIPy6utIco14y7Ju91duEh8A
Secret Key: NhqPtmdSJYdKjVHjA7PZj4Mge3R5YNiP1e3UZjInClVN65XAbvqqM6A7H5fATj0j
```

### Paso 2.4: Configurar permisos (Opcional pero recomendado)

En la configuración de API Keys, habilita:
- ✅ **Enable Reading** (lectura)
- ✅ **Enable Spot & Margin Trading** (solo si necesitas trading)
- ❌ **Enable Withdrawals** (NO habilitar - no es necesario para testing)
- ✅ **Enable Futures** (solo si usas Futures Testnet)

**Restricción de IP (Opcional):**
- Puedes restringir el acceso a tu IP actual para mayor seguridad
- O dejar sin restricción para testing local

---

## 3. Configurar el Proyecto

### Paso 3.1: Instalar dependencias

```bash
# Asegúrate de estar en el directorio del proyecto
cd /home/jose-luis-orozco/Escritorio/PacificLabs/ai-cicd-demo

# Activar entorno virtual (si existe)
source venv/bin/activate

# Instalar dependencias de Binance
pip install python-binance python-dotenv
```

### Paso 3.2: Crear archivo `.env`

Crea un archivo `.env` en la raíz del proyecto:

```bash
touch .env
```

### Paso 3.3: Configurar variables de entorno

Edita `.env` y agrega tus credenciales:

```env
# ================================
# BINANCE TESTNET CONFIGURATION
# ================================

# API Keys (obtenidas en paso 2.3)
BINANCE_API_KEY=tu_api_key_aqui
BINANCE_SECRET_KEY=tu_secret_key_aqui

# Testnet URLs
BINANCE_TESTNET_URL=https://testnet.binance.vision
BINANCE_TESTNET_API=https://testnet.binance.vision/api

# Configuración de trading
BINANCE_USE_TESTNET=true

# Símbolos para testing
DEFAULT_TRADING_PAIR=BTCUSDT
```

**⚠️ IMPORTANTE:**
- Reemplaza `tu_api_key_aqui` y `tu_secret_key_aqui` con tus credenciales reales
- NO subas este archivo a Git (debe estar en `.gitignore`)

### Paso 3.4: Verificar `.gitignore`

Asegúrate de que `.env` esté en `.gitignore`:

```bash
# Verificar si .gitignore existe
cat .gitignore | grep .env

# Si no existe, agrégalo
echo ".env" >> .gitignore
```

### Paso 3.5: Crear `.env.example` (plantilla)

```bash
cp .env .env.example
```

Edita `.env.example` y reemplaza valores reales con placeholders:

```env
BINANCE_API_KEY=your_api_key_here
BINANCE_SECRET_KEY=your_secret_key_here
BINANCE_TESTNET_URL=https://testnet.binance.vision
BINANCE_TESTNET_API=https://testnet.binance.vision/api
BINANCE_USE_TESTNET=true
DEFAULT_TRADING_PAIR=BTCUSDT
```

---

## 4. Ejecutar Tests

### Paso 4.1: Verificar instalación

```bash
python -c "import binance; print(binance.__version__)"
```

Deberías ver la versión instalada (ej: `1.0.19`)

### Paso 4.2: Ejecutar test básico de conexión

```bash
python test_binance_connection.py
```

**Output esperado:**
```
✅ Conexión exitosa a Binance Testnet
📊 Cuenta configurada correctamente
💰 Balance USDT: 1000.00
🪙 Balance BTC: 10.00
```

### Paso 4.3: Ejecutar test de mercado

```bash
python test_binance_market.py
```

### Paso 4.4: Ejecutar test de trading (opcional)

```bash
python test_binance_trading.py
```

---

## 5. Troubleshooting

### ❌ Error: "Invalid API-key, IP, or permissions"

**Causa:** API Key incorrecta o permisos insuficientes

**Solución:**
1. Verifica que copiaste correctamente API Key y Secret Key
2. Revisa que no haya espacios extra en el archivo `.env`
3. Verifica permisos en la configuración de API (paso 2.4)
4. Si restringiste IP, asegúrate que tu IP actual esté permitida

### ❌ Error: "Timestamp for this request is outside of the recvWindow"

**Causa:** Reloj del sistema no sincronizado

**Solución:**
```bash
# Linux/Mac - Sincronizar hora
sudo ntpdate -s time.nist.gov

# O en el código, agregar offset
# (Ver ejemplo en test_binance_connection.py)
```

### ❌ Error: "ModuleNotFoundError: No module named 'binance'"

**Causa:** Librería no instalada

**Solución:**
```bash
pip install python-binance
```

### ❌ Error: "Connection refused" o "Timeout"

**Causa:** Problemas de red o URL incorrecta

**Solución:**
1. Verifica tu conexión a Internet
2. Confirma la URL del testnet en `.env`
3. Intenta acceder manualmente: https://testnet.binance.vision/
4. Verifica firewall/proxy

### ❌ Fondos insuficientes en Testnet

**Causa:** Gastaste los fondos ficticios

**Solución:**
1. Ve a https://testnet.binance.vision/
2. Click en tu perfil → "Test Network Faucet"
3. Solicita más fondos ficticios
4. O crea una nueva cuenta de testnet

---

## 📚 Recursos Adicionales

### Documentación Oficial:
- **Binance API Docs:** https://binance-docs.github.io/apidocs/spot/en/
- **Python-Binance Library:** https://python-binance.readthedocs.io/
- **Testnet FAQ:** https://dev.binance.vision/t/faq/16

### Endpoints Útiles:

**Spot Testnet:**
- Web UI: https://testnet.binance.vision/
- API Base: https://testnet.binance.vision/api
- WebSocket: wss://testnet.binance.vision/ws

**Futures Testnet:**
- Web UI: https://testnet.binancefuture.com/
- API Base: https://testnet.binancefuture.com/fapi
- WebSocket: wss://stream.binancefuture.com

### Limitaciones del Testnet:

⚠️ **Ten en cuenta:**
- Los datos NO son en tiempo real (pueden tener delay)
- Algunas funcionalidades pueden no estar disponibles
- El testnet puede reiniciarse ocasionalmente
- No se puede transferir dinero real
- Las órdenes no afectan el mercado real

---

## 🎯 Próximos Pasos

Una vez configurado el testnet:

1. ✅ Ejecuta todos los tests de conexión
2. ✅ Prueba obtener precios en tiempo real
3. ✅ Experimenta con órdenes de compra/venta (sin riesgo)
4. ✅ Implementa estrategias de trading
5. ✅ Integra con tu sistema de análisis existente
6. ✅ Cuando estés listo, considera migrar a la API real (con precaución)

---

## ⚠️ Advertencia Final

**Antes de usar la API real de Binance:**

1. Prueba EXHAUSTIVAMENTE en testnet
2. Implementa gestión de riesgos adecuada
3. Nunca compartas tus API keys reales
4. Habilita 2FA en tu cuenta real
5. Usa restricciones de IP en producción
6. Comienza con cantidades pequeñas
7. Monitorea constantemente tus operaciones

---

**¿Problemas? ¿Preguntas?**

Revisa la sección de Troubleshooting o consulta la documentación oficial de Binance.

**Happy Testing! 🚀📊**
