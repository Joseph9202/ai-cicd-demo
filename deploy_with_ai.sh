#!/bin/bash
# Script para desplegar el bot con reportes AI a Cloud Functions

echo "🚀 Desplegando GARCH Trading Bot con Reportes AI"
echo "=================================================="
echo ""

# Check if GEMINI_API_KEY is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ ERROR: GEMINI_API_KEY no está configurada"
    echo ""
    echo "Pasos para configurar:"
    echo "  1. Ve a: https://aistudio.google.com/app/apikey"
    echo "  2. Crea una nueva API key (gratis)"
    echo "  3. Ejecuta: export GEMINI_API_KEY='tu-api-key-aqui'"
    echo "  4. Vuelve a ejecutar este script"
    echo ""
    exit 1
fi

echo "✅ GEMINI_API_KEY configurada"

# Check if TELEGRAM credentials are set
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ ERROR: TELEGRAM_BOT_TOKEN no está configurada"
    echo ""
    echo "Pasos para configurar:"
    echo "  1. Crea un bot con @BotFather en Telegram"
    echo "  2. Copia el token que te da"
    echo "  3. Ejecuta: export TELEGRAM_BOT_TOKEN='tu-bot-token-aqui'"
    echo "  4. Vuelve a ejecutar este script"
    echo ""
    exit 1
fi

echo "✅ TELEGRAM_BOT_TOKEN configurada"

if [ -z "$TELEGRAM_CHAT_ID" ]; then
    echo "❌ ERROR: TELEGRAM_CHAT_ID no está configurada"
    echo ""
    echo "Pasos para configurar:"
    echo "  1. Inicia conversación con tu bot en Telegram"
    echo "  2. Obtén el chat_id visitando:"
    echo "     https://api.telegram.org/bot<TU_BOT_TOKEN>/getUpdates"
    echo "  3. Ejecuta: export TELEGRAM_CHAT_ID='tu-chat-id-aqui'"
    echo "  4. Vuelve a ejecutar este script"
    echo ""
    exit 1
fi

echo "✅ TELEGRAM_CHAT_ID configurada"

# Check if WHATSAPP credentials are set
if [ -z "$EVOLUTION_API_URL" ] || [ -z "$EVOLUTION_API_KEY" ] || [ -z "$WHATSAPP_TARGET_NUMBER" ]; then
    echo "⚠️  ADVERTENCIA: Credenciales de WhatsApp no configuradas"
    echo "   El bot funcionará, pero no enviará mensajes a WhatsApp."
    echo ""
    echo "   Para configurar:"
    echo "   1. Ejecuta: ./setup_whatsapp.sh"
    echo "   2. Vuelve a ejecutar este script"
    echo ""
    echo "   Continuando despliegue sin WhatsApp en 5 segundos..."
    sleep 5
else
    echo "✅ Credenciales de WhatsApp configuradas"
fi

echo ""
echo "📤 Desplegando a Cloud Functions..."
echo ""

gcloud functions deploy garch-trading-bot \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point garch_trading_bot \
  --region us-east1 \
  --memory 512MB \
  --timeout 540s \
  --set-env-vars GEMINI_API_KEY=$GEMINI_API_KEY,TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN,TELEGRAM_CHAT_ID=$TELEGRAM_CHAT_ID,EVOLUTION_API_URL=$EVOLUTION_API_URL,EVOLUTION_API_KEY=$EVOLUTION_API_KEY,WHATSAPP_TARGET_NUMBER=$WHATSAPP_TARGET_NUMBER

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Despliegue exitoso!"
    echo ""
    echo "📋 Próximos pasos:"
    echo ""
    echo "1️⃣ Probar el endpoint de reportes:"
    echo "   curl -X POST https://us-east1-travel-recomender.cloudfunctions.net/garch-trading-bot/report"
    echo ""
    echo "2️⃣ Configurar Cloud Scheduler para reportes horarios:"
    echo "   gcloud scheduler jobs create http garch-report-scheduler \\"
    echo "     --schedule \"0 * * * *\" \\"
    echo "     --uri \"https://us-east1-travel-recomender.cloudfunctions.net/garch-trading-bot/report\" \\"
    echo "     --http-method POST \\"
    echo "     --location us-east1"
    echo ""
    echo "   O si ya existe, actualízalo:"
    echo "   gcloud scheduler jobs update http garch-report-scheduler \\"
    echo "     --schedule \"0 * * * *\" \\"
    echo "     --uri \"https://us-east1-travel-recomender.cloudfunctions.net/garch-trading-bot/report\" \\"
    echo "     --location us-east1"
    echo ""
else
    echo ""
    echo "❌ Error en el despliegue"
    exit 1
fi
