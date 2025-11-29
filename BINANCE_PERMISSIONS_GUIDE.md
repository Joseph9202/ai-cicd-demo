# 🔧 Guía Visual: Habilitar Permisos de API en Binance Testnet

## 🚨 Estado Actual

Tu API Key está **parcialmente configurada**:

```
API Key: Tdhxu8fmnWde...mlqeRMVx
Estado: VÁLIDA pero SIN PERMISOS
Tests: 2/5 pasados (40%)
```

### ❌ Permisos Faltantes:
- ❌ **Enable Reading** - NO habilitado
- ❌ **Enable Spot & Margin Trading** - NO habilitado

---

## 📋 Pasos para Habilitar Permisos

### 1️⃣ Accede a Binance Testnet
```
https://testnet.binance.vision/
```

### 2️⃣ Login
- Usa tus credenciales de Binance Testnet
- Si no las recuerdas, usa "Forgot Password"

### 3️⃣ Ve a API Keys
- Click en tu **email** (esquina superior derecha)
- Click en **"API Keys"**

### 4️⃣ Encuentra tu API Key
Busca la que empieza con: `Tdhxu8fmnWde...`

### 5️⃣ Editar Permisos (¡IMPORTANTE!)

Verás algo como esto:

```
┌─────────────────────────────────────────────────┐
│ API Key: Tdhxu8fmnWde...mlqeRMVx                │
│                                                 │
│ Permissions:                                    │
│                                                 │
│ □ Enable Reading                                │
│ □ Enable Spot & Margin Trading                  │
│ □ Enable Withdrawals                            │
│ □ Enable Futures                                │
│                                                 │
│ IP Restrictions:                                │
│ [ ] No restrictions                             │
│ [ ] Restrict access to trusted IPs only         │
│                                                 │
│          [Save Changes]                         │
└─────────────────────────────────────────────────┘
```

### 6️⃣ Habilita ESTOS permisos (marcar checkbox):

```
✅ Enable Reading                    ← ¡MARCA ESTE!
✅ Enable Spot & Margin Trading      ← ¡MARCA ESTE!
□  Enable Withdrawals                ← NO necesario
□  Enable Futures                    ← NO necesario
```

### 7️⃣ IP Restrictions

**IMPORTANTE:** Asegúrate de seleccionar:

```
● No restrictions                    ← ¡SELECCIONA ESTE!
○ Restrict access to trusted IPs only
```

Si ves IPs listadas debajo, **ELIMÍNALAS TODAS**.

### 8️⃣ Guarda Cambios

- Click en **"Save Changes"** o **"Update"**
- Confirma si te pide autenticación 2FA

---

## ✅ Verificar que Funcionó

Después de guardar, espera **1 minuto** y ejecuta:

```bash
source venv/bin/activate
python test_new_api_key.py
```

**Resultado esperado:**
```
Tests pasados: 5/5 (100%)
🎉 ¡PERFECTO! API Key completamente funcional
```

---

## 🔍 Troubleshooting

### Si sigue fallando después de habilitar permisos:

#### Opción 1: Genera una NUEVA API Key
1. Ve a Binance Testnet → API Keys
2. Click **"Generate New Key"**
3. **ANTES de generarla**, asegúrate de marcar:
   - ✅ Enable Reading
   - ✅ Enable Spot & Margin Trading
4. Copia la nueva API Key y Secret
5. Actualiza el archivo `.env`:

```bash
BINANCE_API_KEY=<tu_nueva_key>
BINANCE_SECRET_KEY=<tu_nuevo_secret>
```

#### Opción 2: Verifica restricciones de IP

1. En la página de API Keys, verifica si hay IPs listadas
2. Si ves algo como `192.168.1.100` o similar, **elimínalo**
3. Asegúrate que dice **"No restrictions"**

#### Opción 3: Espera 5 minutos

A veces los cambios de permisos tardan en propagarse:
- Guarda cambios en Binance
- Espera **5 minutos**
- Ejecuta el test de nuevo

---

## 📸 Capturas de Pantalla de Referencia

### ✅ CORRECTO - Permisos Habilitados
```
Permissions:
✓ Enable Reading                    ← CHECK ACTIVADO
✓ Enable Spot & Margin Trading      ← CHECK ACTIVADO

IP Restrictions:
● No restrictions                    ← SELECCIONADO
```

### ❌ INCORRECTO - Sin Permisos
```
Permissions:
□ Enable Reading                    ← SIN MARCAR
□ Enable Spot & Margin Trading      ← SIN MARCAR

IP Restrictions:
○ Restrict access to trusted IPs
  192.168.1.100                     ← IP BLOQUEANDO
```

---

## 🆘 Si Nada Funciona

Si después de todo esto sigue sin funcionar:

1. **Elimina completamente la API Key actual**
2. **Crea una NUEVA desde cero**
3. **Habilita permisos ANTES de generarla**
4. **No agregues restricciones de IP**
5. **Actualiza el .env con las nuevas credenciales**

Comando para probar:
```bash
unset BINANCE_API_KEY BINANCE_SECRET_KEY
source venv/bin/activate
python test_new_api_key.py
```

---

## 📞 Recursos

- **Binance Testnet:** https://testnet.binance.vision/
- **Documentación:** https://binance-docs.github.io/apidocs/testnet/en/
- **Script de test:** `test_new_api_key.py`
- **Script de diagnóstico:** `diagnose_binance.py`

---

## ✨ Estado Deseado Final

Cuando todo esté bien configurado, deberías ver:

```
🔑 TEST DE NUEVA API KEY
======================================================================

[1/5] Test de conectividad básica...
✅ Servidor responde

[2/5] Verificando permisos de API Key...
✅ Permisos obtenidos

[3/5] Intentando leer información de cuenta...
✅ Cuenta accesible
   Tipo: SPOT
   Puede tradear: True
   Puede depositar: True
   Puede retirar: True

   Balances:
     💰 BTC: 1.00000000
     💰 USDT: 10000.00000000

[4/5] Intentando leer órdenes...
✅ Órdenes accesibles (total: 0)

[5/5] Intentando crear orden TEST...
✅ Orden TEST validada (permisos de trading OK)

======================================================================
📊 RESUMEN
======================================================================

Tests pasados: 5/5 (100%)

🎉 ¡PERFECTO! API Key completamente funcional
   Todos los permisos están habilitados correctamente
```
