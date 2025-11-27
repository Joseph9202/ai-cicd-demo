# 🤖 Guía del Bot de Telegram - GARCH Trading Bot

## ✅ Funcionalidad Implementada

¡SÍ! El bot **ya tiene la funcionalidad completa** para recibir comandos y generar reportes bajo demanda.

## 🎯 ¿Qué puede hacer el bot?

### 1. Comando `/reporte` o `/report`
Genera un análisis económico completo usando Gemini AI que incluye:
- 📊 Resumen ejecutivo del comportamiento de BTC
- 📈 Interpretación económica de la volatilidad
- ⚠️ Evaluación de riesgos basada en GARCH
- 🔮 Predicción para las próximas horas

**Ejemplo de respuesta:**
```
📊 *REPORTE HORARIO - GARCH Trading Bot*
⏰ 2025-11-25 21:54 UTC

[Análisis generado por Gemini AI basado en datos de las últimas 24h]

---
_Análisis generado por Gemini AI • Datos: últimas 24h_
```

### 2. Comando `/stats`
Muestra estadísticas rápidas de las últimas 24 horas:
- 📈 Número de predicciones realizadas
- 📉 Volatilidad promedio
- 💰 Precio máximo y mínimo de BTC

### 3. Comando `/ayuda` o `/help`
Muestra la lista completa de comandos disponibles

## 🚀 Cómo Activar el Bot

### Paso 1: Configurar Credenciales
```bash
# Configura las variables de entorno
export TELEGRAM_BOT_TOKEN='tu-bot-token'
export TELEGRAM_CHAT_ID='tu-chat-id'
export GEMINI_API_KEY='tu-gemini-key'
```

### Paso 2: Probar Conexión
```bash
./setup_telegram.sh test
```

### Paso 3: Desplegar a Cloud Functions
```bash
./deploy_with_ai.sh
```

### Paso 4: Configurar Webhook
```bash
./setup_webhook.sh
```

## 💬 Flujo de Interacción

```
Usuario en Telegram:
  /reporte
      ↓
Bot responde:
  "🔄 Generando reporte AI... (puede tomar unos segundos)"
      ↓
Cloud Function:
  1. Consulta datos de BigQuery (últimas 24h)
  2. Analiza estadísticas GARCH
  3. Envía datos a Gemini AI
  4. Gemini genera análisis económico
      ↓
Bot responde:
  [Reporte completo con análisis AI]
```

## 🔧 Arquitectura Técnica

```
Telegram Bot (@TuBot)
       ↓
   Webhook URL
       ↓
Google Cloud Functions
  ├── Endpoint: /telegram-webhook
  ├── Valida chat_id autorizado
  ├── Procesa comando
  └── Llama a funciones:
      ├── generate_ai_report() → Gemini AI
      ├── BigQuery para stats
      └── send_telegram_message()
```

## 📝 Código Relevante

El manejo de comandos está en [main.py](file:///home/jose-luis-orozco/Escritorio/PacificLabs/ai-cicd-demo/main.py):
- **Líneas 505-533**: Webhook de Telegram
- **Líneas 535-599**: Procesamiento de comandos
- **Líneas 540-546**: Comando `/reporte`
- **Líneas 566-592**: Comando `/stats`
- **Líneas 548-564**: Comando `/ayuda`

## 🔐 Seguridad

El bot incluye validación de autorización:
- Solo responde al `TELEGRAM_CHAT_ID` configurado
- Rechaza mensajes de otros usuarios
- Código HTTP 403 para no autorizados

## ✨ Características Adicionales

### Notificaciones Automáticas
Además de los comandos bajo demanda, el bot envía alertas automáticas cuando:
- El portafolio simulado tiene ganancia > 0.5%
- Incluye métricas del portafolio
- Señal actual (BUY/SELL/HOLD)
- Precio de BTC

### Integración con Gemini AI
Todos los reportes son generados por Gemini 1.5 Flash con:
- Análisis contextual de datos económicos
- Interpretación de modelos GARCH
- Recomendaciones basadas en volatilidad
- Formato optimizado para Telegram (Markdown)

## 🎯 Próximos Pasos

1. ✅ Configura las credenciales (si no lo has hecho)
2. ✅ Prueba con `./setup_telegram.sh test`
3. ✅ Despliega con `./deploy_with_ai.sh`
4. ✅ Configura webhook con `./setup_webhook.sh`
5. 🚀 ¡Envía `/reporte` a tu bot y disfruta!

## ❓ Resolución de Problemas

### El bot no responde
- Verifica que el webhook esté configurado: `./setup_webhook.sh`
- Revisa los logs de Cloud Functions

### Error "unauthorized"
- Verifica que `TELEGRAM_CHAT_ID` sea correcto
- Debe coincidir con el ID de tu chat

### El reporte está vacío
- Verifica que haya datos en BigQuery (últimas 24h)
- Ejecuta `/run` para generar nuevas predicciones

### Error de Gemini AI
- Verifica que `GEMINI_API_KEY` esté configurada
- Revisa los límites de tu API key en Google AI Studio
