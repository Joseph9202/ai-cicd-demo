#!/bin/bash
# Script para actualizar SOLO las variables de entorno sin re-desplegar todo

echo "🔄 Actualizando variables de entorno en Cloud Functions"
echo "========================================================"
echo ""

# Verificar que las variables estén configuradas
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ ERROR: TELEGRAM_BOT_TOKEN no está configurada"
    echo ""
    echo "Configúrala con:"
    echo "  export TELEGRAM_BOT_TOKEN='tu-token-aqui'"
    echo ""
    exit 1
fi

if [ -z "$TELEGRAM_CHAT_ID" ]; then
    echo "❌ ERROR: TELEGRAM_CHAT_ID no está configurada"
    echo ""
    echo "Configúrala con:"
    echo "  export TELEGRAM_CHAT_ID='tu-chat-id-aqui'"
    echo ""
    exit 1
fi

if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  GEMINI_API_KEY no configurada, usando la existente en Cloud Functions"
    # Obtener la actual
    GEMINI_API_KEY=$(gcloud functions describe garch-trading-bot --region=us-east1 --format="value(serviceConfig.environmentVariables.GEMINI_API_KEY)" 2>/dev/null)
fi

echo "✅ Variables detectadas:"
echo "   GEMINI_API_KEY: ${GEMINI_API_KEY:0:20}..."
echo "   TELEGRAM_BOT_TOKEN: ${TELEGRAM_BOT_TOKEN:0:20}..."
echo "   TELEGRAM_CHAT_ID: $TELEGRAM_CHAT_ID"
echo ""
echo "🚀 Actualizando Cloud Function..."
echo ""

gcloud functions deploy garch-trading-bot \
  --region us-east1 \
  --update-env-vars GEMINI_API_KEY=$GEMINI_API_KEY,TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN,TELEGRAM_CHAT_ID=$TELEGRAM_CHAT_ID

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Variables actualizadas exitosamente"
    echo ""
    echo "🔗 Ahora configura el webhook:"
    echo "   ./setup_webhook.sh"
    echo ""
else
    echo ""
    echo "❌ Error al actualizar variables"
    exit 1
fi
