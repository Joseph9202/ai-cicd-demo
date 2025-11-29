# 🚀 Binance API Testing Suite

Sistema completo de testing para la API de Binance usando Testnet (cuenta de prueba sin riesgo).

## 📁 Archivos Incluidos

```
.
├── BINANCE_TESTNET_SETUP.md      # Guía completa paso a paso
├── .env.example                   # Plantilla de configuración
├── test_binance_connection.py    # Test de conexión básica
├── test_binance_market.py         # Test de datos de mercado
├── test_binance_trading.py        # Test de trading (compra/venta)
└── requirements.txt               # Dependencias actualizadas
```

## ⚡ Quick Start (5 minutos)

### 1. Crear cuenta Testnet

```bash
# Abre en tu navegador:
https://testnet.binance.vision/

# Regístrate y obtén tus API Keys
```

### 2. Instalar dependencias

```bash
# Activar entorno virtual
source venv/bin/activate

# Instalar nuevas dependencias
pip install -r requirements.txt
```

### 3. Configurar credenciales

```bash
# Copiar plantilla
cp .env.example .env

# Editar .env y agregar tus credenciales
nano .env
```

Configuración mínima en `.env`:
```env
BINANCE_API_KEY=tu_api_key_aqui
BINANCE_SECRET_KEY=tu_secret_key_aqui
BINANCE_USE_TESTNET=true
```

### 4. Ejecutar tests

```bash
# Test 1: Conexión básica
python test_binance_connection.py

# Test 2: Datos de mercado
python test_binance_market.py

# Test 3: Trading simulado
python test_binance_trading.py
```

## 📊 Qué hace cada test

### `test_binance_connection.py`
✅ Verifica conexión a Binance Testnet
✅ Valida API Keys
✅ Muestra balances de cuenta
✅ Obtiene precio actual de BTC/USDT
✅ Verifica límites de rate

**Tiempo estimado:** 5-10 segundos

### `test_binance_market.py`
✅ Precio actual y estadísticas 24h
✅ Order book (libro de órdenes)
✅ Trades recientes
✅ Velas/Candlesticks (últimas 5 horas)
✅ Información del símbolo
✅ Top 10 criptos por volumen

**Tiempo estimado:** 10-15 segundos

### `test_binance_trading.py`
✅ Verificación de balances
✅ Límites de trading
✅ Orden TEST (validación sin ejecutar)
✅ Orden MARKET de compra REAL
✅ Orden MARKET de venta REAL
✅ Cálculo de ganancias/pérdidas

**Tiempo estimado:** Variable (requiere confirmación del usuario)

## 🔒 Seguridad

⚠️ **IMPORTANTE:**

- ✅ Archivo `.env` está en `.gitignore` (no se sube a Git)
- ✅ Usa solo TESTNET para pruebas
- ✅ Nunca compartas tus API keys
- ✅ Los scripts verifican `BINANCE_USE_TESTNET=true`
- ❌ NO ejecutar en producción sin modificaciones

## 🛠️ Troubleshooting

### Error: "Invalid API-key"
→ Verifica que copiaste correctamente las credenciales en `.env`

### Error: "Timestamp outside recvWindow"
→ Sincroniza el reloj de tu sistema:
```bash
sudo ntpdate -s time.nist.gov
```

### Error: "Insufficient balance"
→ Solicita más fondos ficticios en https://testnet.binance.vision/

### Más ayuda
→ Consulta [BINANCE_TESTNET_SETUP.md](BINANCE_TESTNET_SETUP.md) sección Troubleshooting

## 📚 Documentación Completa

Para configuración detallada paso a paso, consulta:

📖 **[BINANCE_TESTNET_SETUP.md](BINANCE_TESTNET_SETUP.md)**

Incluye:
- Tutorial completo de registro
- Obtención de API Keys
- Configuración avanzada
- Solución de problemas comunes
- Recursos adicionales

## 🔗 Enlaces Útiles

- **Binance Testnet:** https://testnet.binance.vision/
- **API Docs:** https://binance-docs.github.io/apidocs/spot/en/
- **Python-Binance:** https://python-binance.readthedocs.io/

## 💡 Próximos Pasos

Después de completar los tests:

1. ✅ Experimenta con diferentes pares de trading
2. ✅ Implementa estrategias de trading automatizadas
3. ✅ Integra con tu sistema de análisis económico
4. ✅ Conecta con bots de Telegram/WhatsApp
5. ✅ Genera reportes automáticos con datos de Binance

## 🤝 Integración con el Proyecto Actual

Este módulo se integra perfectamente con:

- **Telegram Bot** → Comandos para obtener precios cripto
- **WhatsApp Bot** → Alertas de precio en tiempo real
- **Gemini AI** → Análisis de mercado cripto con IA
- **PDF Reports** → Informes automáticos de portafolio
- **CI/CD** → Tests automáticos en cada push

Ejemplo de integración:
```python
# En tu bot de Telegram
from binance.client import Client
import os

client = Client(
    os.getenv('BINANCE_API_KEY'),
    os.getenv('BINANCE_SECRET_KEY'),
    testnet=True
)

# Obtener precio para comando /precio
def get_btc_price():
    ticker = client.get_symbol_ticker(symbol="BTCUSDT")
    return float(ticker['price'])
```

## 📄 Licencia

Este código es parte del proyecto ai-cicd-demo.
Úsalo libremente para aprendizaje y desarrollo.

---

**Happy Testing! 🚀📊**

¿Preguntas? Revisa la documentación completa en `BINANCE_TESTNET_SETUP.md`
