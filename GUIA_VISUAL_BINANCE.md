# 🎯 Guía Visual: Cómo Habilitar Permisos en Binance Testnet

## Problema Actual
Tu API Key existe pero **NO tiene permisos habilitados** para leer información de cuenta o hacer trading.

---

## ✅ SOLUCIÓN RÁPIDA: Crear Nueva API Key CON Permisos

Es más fácil crear una nueva API Key con los permisos correctos desde el inicio.

### 📍 PASO 1: Ir a Binance Testnet

1. Abre tu navegador
2. Ve a: **https://testnet.binance.vision/**
3. **Login** con tu cuenta (email y contraseña)

---

### 📍 PASO 2: Acceder a API Management

Una vez logueado, verás la interfaz principal. Ahora:

**Opción A - Desde el menú superior:**
```
┌─────────────────────────────────────────────────────────┐
│  Binance Testnet                    [tu-email@gmail.com] ▼ │
└─────────────────────────────────────────────────────────┘
```
1. Click en **tu email** (esquina superior derecha)
2. Se desplegará un menú con opciones
3. Busca y click en **"API Management"** o **"API Keys"**

**Opción B - URL directa:**

Simplemente ve directo a:
```
https://testnet.binance.vision/apiManagement.html
```

---

### 📍 PASO 3: Eliminar API Key Antigua (Opcional pero recomendado)

Verás una tabla con tus API Keys existentes:

```
┌──────────────────────────────────────────────────────────────┐
│ API Key Management                                            │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│ Label          API Key                        Actions         │
│ ───────────────────────────────────────────────────────────  │
│ [tu-label]     TkggDlWNZlx6...mtTWODEF       [Edit] [Delete] │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

1. Busca tu API Key que termina en `...ODEF`
2. Click en **[Delete]** o **[Eliminar]**
3. Confirma la eliminación

**¿Por qué eliminar?** Porque crearemos una nueva CON los permisos correctos desde el inicio.

---

### 📍 PASO 4: Crear Nueva API Key (CON PERMISOS)

1. Click en botón **"Create API"** o **"Generate HMAC_SHA256 Key"**

Verás un formulario como este:

```
┌─────────────────────────────────────────────────────────┐
│  Create API Key                                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  API Key Label: [_____________________________]         │
│                 (Ejemplo: "mi-trading-bot")              │
│                                                          │
│  ☐ Enable Reading                                       │
│  ☐ Enable Spot & Margin Trading                         │
│  ☐ Enable Withdrawals                                   │
│  ☐ Enable Futures                                       │
│                                                          │
│  IP Restriction (optional):                             │
│  [_____________________________]                         │
│                                                          │
│  [ Generate ]  [ Cancel ]                               │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**CONFIGURACIÓN CORRECTA:**

1. **API Key Label:** Escribe algo como `testing-bot` o `mi-api`

2. **PERMISOS - MARCA ESTAS OPCIONES:**
   - ✅ **Enable Reading** ← IMPORTANTE
   - ✅ **Enable Spot & Margin Trading** ← IMPORTANTE
   - ❌ **Enable Withdrawals** ← NO marcar
   - ❌ **Enable Futures** ← NO marcar (a menos que lo necesites)

3. **IP Restriction:**
   - **DÉJALO VACÍO** (sin restricción)
   - O puedes poner tu IP actual si lo prefieres

4. Click en **[Generate]** o **[Crear]**

---

### 📍 PASO 5: COPIAR Nuevas Credenciales

⚠️ **MUY IMPORTANTE:** Las credenciales se muestran **SOLO UNA VEZ**

Verás una pantalla como esta:

```
┌─────────────────────────────────────────────────────────┐
│  ✅ API Key Created Successfully                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  API Key:                                                │
│  ┌────────────────────────────────────────────────────┐ │
│  │ vmPUZE6mv9SD5VNHk4HlWFsOr6aKE2zvsw0MuIgwCIPy...   │ │
│  │                                        [📋 Copy]    │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  Secret Key:                                             │
│  ┌────────────────────────────────────────────────────┐ │
│  │ NhqPtmdSJYdKjVHjA7PZj4Mge3R5YNiP1e3UZjInClVN...   │ │
│  │                                        [📋 Copy]    │ │
│  └────────────────────────────────────────────────────┘ │
│                                                          │
│  ⚠️  Save these keys now. They won't be shown again.    │
│                                                          │
│  [ Done ]                                                │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**ACCIÓN:**

1. Click en **[📋 Copy]** junto a **API Key**
2. Pégala en un lugar seguro (temporal)
3. Click en **[📋 Copy]** junto a **Secret Key**
4. Pégala en un lugar seguro (temporal)

**NO CIERRES LA VENTANA** hasta que hayas copiado ambas claves.

---

### 📍 PASO 6: Actualizar el archivo .env

Ahora actualiza tu archivo `.env` con las nuevas credenciales:

1. Abre la terminal en tu proyecto:
   ```bash
   cd /home/jose-luis-orozco/Escritorio/PacificLabs/ai-cicd-demo
   ```

2. Edita el archivo `.env`:
   ```bash
   nano .env
   ```

3. Reemplaza las credenciales antiguas con las nuevas:
   ```env
   BINANCE_API_KEY=TU_NUEVA_API_KEY_AQUI
   BINANCE_SECRET_KEY=TU_NUEVA_SECRET_KEY_AQUI
   BINANCE_USE_TESTNET=true
   DEFAULT_TRADING_PAIR=BTCUSDT
   ```

4. Guarda el archivo:
   - Presiona `Ctrl + O` (guardar)
   - Presiona `Enter`
   - Presiona `Ctrl + X` (salir)

---

### 📍 PASO 7: Ejecutar Test

```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar diagnóstico
python diagnose_binance.py
```

**Resultado esperado:**
```
✅ API Key válida y con permisos correctos
   Tipo de cuenta: SPOT
   Puede tradear: True
   Puede depositar: True
   Puede retirar: False

✅ Balances encontrados:
   💰 BTC: 10.00000000
   💰 USDT: 1000.00000000
   💰 BNB: 100.00000000

🎉 DIAGNÓSTICO EXITOSO - TODO FUNCIONA CORRECTAMENTE
```

---

## 🚨 ¿TODAVÍA NO ENCUENTRAS LA OPCIÓN?

### Alternativa 1: Usar la API de creación directa

Si la interfaz web tiene problemas, podemos crear la API Key usando Python:

```bash
# Ejecuta este script
python create_api_key_helper.py
```

(Te crearé este script si es necesario)

### Alternativa 2: Probar Binance Futures Testnet

Otra opción es usar el testnet de Futures que tiene una interfaz diferente:

1. Ve a: **https://testnet.binancefuture.com/**
2. Login con GitHub o email
3. La interfaz es más moderna y fácil de encontrar las opciones

---

## 📸 Capturas de Pantalla de Referencia

### Cómo se ve el menú de usuario:

```
Testnet Binance                                 [tu-email@mail.com] ▼

Cuando haces click en tu email, aparece:
┌────────────────────────┐
│ Dashboard              │
│ API Management    ← AQUÍ
│ Settings               │
│ Security               │
│ ──────────────────     │
│ Logout                 │
└────────────────────────┘
```

### Cómo se ve la página de API Management:

```
┌─────────────────────────────────────────────────────────────┐
│  API Management                          [+ Create API Key]  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Your API Keys:                                              │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Label          Created         Actions                 │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │ test-key       2025-01-27      [Edit] [Delete]        │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Checklist Final

Antes de ejecutar los tests, verifica:

- [ ] Creaste nueva API Key en https://testnet.binance.vision/
- [ ] Marcaste "Enable Reading" al crear la key
- [ ] Marcaste "Enable Spot & Margin Trading" al crear la key
- [ ] Copiaste AMBAS credenciales (API Key y Secret Key)
- [ ] Actualizaste el archivo `.env` con las nuevas credenciales
- [ ] `BINANCE_USE_TESTNET=true` está en el .env
- [ ] Ejecutaste `python diagnose_binance.py`

---

## 💬 ¿Necesitas Más Ayuda?

Si aún no encuentras las opciones, dime:

1. ¿Qué ves cuando haces login en https://testnet.binance.vision/?
2. ¿Hay algún menú o botón visible en la esquina superior derecha?
3. ¿La página se ve diferente a lo descrito?

Puedo crear un script automatizado que te ayude a crear las API Keys si la interfaz web no funciona.

---

**📌 CONSEJO PRO:** Si todo esto es muy complicado, puedo configurar el proyecto para usar datos públicos de Binance que NO requieren API Keys (solo precios, sin trading). ¿Te interesa esa opción?
