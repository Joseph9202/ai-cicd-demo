# 🔧 Solución: Notificaciones de Telegram

## Problema Identificado

Las notificaciones de Telegram no funcionaban porque las credenciales (`TELEGRAM_BOT_TOKEN` y `TELEGRAM_CHAT_ID`) no estaban configuradas en Cloud Functions.

## Solución Implementada

### 1. Script de Despliegue Actualizado

Actualicé `deploy_with_ai.sh` para:
- ✅ Validar que `TELEGRAM_BOT_TOKEN` esté configurado
- ✅ Validar que `TELEGRAM_CHAT_ID` esté configurado
- ✅ Incluir ambas variables en el despliegue de Cloud Functions

### 2. Script de Configuración Nuevo

Creé `setup_telegram.sh` que:
- 📋 Muestra el estado actual de las variables
- 📚 Proporciona guía paso a paso
- 🧪 Permite probar la conexión antes del despliegue

## 🚀 Pasos para Arreglar las Notificaciones

### Paso 1: Configurar el Bot de Telegram

1. Abre Telegram y busca **@BotFather**
2. Envía el comando: `/newbot`
3. Sigue las instrucciones (nombre y username del bot)
4. **Copia el token** que te da (ejemplo: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

### Paso 2: Obtener el Chat ID

1. Inicia conversación con tu nuevo bot en Telegram
2. Envía cualquier mensaje (por ejemplo: "Hola")
3. Abre en tu navegador:
   ```
   https://api.telegram.org/bot<TU_TOKEN>/getUpdates
   ```
   (Reemplaza `<TU_TOKEN>` con el token del Paso 1)
4. **Busca** en la respuesta JSON: `"chat":{"id": NUMERO}`
5. **Copia ese número** (puede ser positivo o negativo)

### Paso 3: Configurar Variables de Entorno

En tu terminal, ejecuta:

```bash
export TELEGRAM_BOT_TOKEN='tu-token-aqui'
export TELEGRAM_CHAT_ID='tu-chat-id-aqui'
export GEMINI_API_KEY='tu-gemini-key-aqui'  # Si no la tienes ya
```

**💡 Tip:** Para que las variables persistan entre sesiones, agrégalas a tu `~/.bashrc` o `~/.zshrc`:

```bash
echo "export TELEGRAM_BOT_TOKEN='tu-token-aqui'" >> ~/.bashrc
echo "export TELEGRAM_CHAT_ID='tu-chat-id-aqui'" >> ~/.bashrc
source ~/.bashrc
```

### Paso 4: Probar la Conexión

```bash
./setup_telegram.sh test
```

Deberías recibir un mensaje en Telegram confirmando que funciona.

### Paso 5: Desplegar a Cloud Functions

```bash
./deploy_with_ai.sh
```

Este script ahora:
- ✅ Verificará que todas las credenciales estén configuradas
- ✅ Desplegará la función con las variables de Telegram
- ✅ Las notificaciones funcionarán correctamente

### Paso 6: Configurar el Webhook de Telegram

Para que el bot pueda recibir comandos, configura el webhook:

```bash
./setup_webhook.sh
```

Esto conectará tu bot con Cloud Functions para que puedas enviar comandos directamente en Telegram.

## 🤖 Comandos Disponibles en el Bot

Una vez configurado el webhook, puedes usar estos comandos en tu bot de Telegram:

| Comando | Descripción |
|---------|-------------|
| `/reporte` | 🤖 Genera un análisis económico AI inmediato usando Gemini |
| `/stats` | 📊 Muestra estadísticas rápidas de las últimas 24 horas |
| `/ayuda` | ℹ️ Lista de comandos disponibles |

**Ejemplo de uso:**
1. Abre tu bot en Telegram
2. Envía `/reporte`
3. El bot responderá "🔄 Generando reporte AI..."
4. En unos segundos recibirás un análisis completo generado por Gemini AI

## 🧪 Probar las Notificaciones

Una vez desplegado, puedes probar:

```bash
# Endpoint de reporte AI (envía a Telegram)
curl -X POST https://us-east1-travel-recomender.cloudfunctions.net/garch-trading-bot/report
```

También puedes enviar comandos directamente a tu bot de Telegram:
- `/reporte` - Genera un reporte AI inmediato
- `/stats` - Muestra estadísticas rápidas
- `/ayuda` - Lista de comandos disponibles

## 📝 Archivos Modificados

1. **`deploy_with_ai.sh`** - Validación y despliegue de credenciales de Telegram
2. **`setup_telegram.sh`** (nuevo) - Script de configuración y prueba

## ⚠️ Importante

- Nunca compartas tu `TELEGRAM_BOT_TOKEN` públicamente
- No subas las credenciales a Git
- El archivo `.gitignore` ya está configurado para evitar subir archivos `.env`

## 🎯 Próximos Pasos

1. Configura las variables de entorno (Pasos 1-3)
2. Prueba con `./setup_telegram.sh test`
3. Despliega con `./deploy_with_ai.sh`
4. ¡Disfruta de las notificaciones automáticas! 🚀
