#!/bin/bash
# Script para configurar el webhook de Telegram

echo "🔗 Configuración del Webhook de Telegram"
echo "========================================"
echo ""

# Check if credentials are set
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ ERROR: TELEGRAM_BOT_TOKEN no está configurada"
    echo "Ejecuta: export TELEGRAM_BOT_TOKEN='tu-token'"
    exit 1
fi

# Cloud Function URL
FUNCTION_URL="https://us-east1-travel-recomender.cloudfunctions.net/garch-trading-bot"
WEBHOOK_URL="${FUNCTION_URL}/telegram-webhook"

echo "📍 URL del webhook: $WEBHOOK_URL"
echo ""
echo "🔄 Configurando webhook..."
echo ""

# Set webhook
RESPONSE=$(curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook" \
    -H "Content-Type: application/json" \
    -d "{\"url\":\"${WEBHOOK_URL}\"}")

if echo "$RESPONSE" | grep -q '"ok":true'; then
    echo "✅ ¡Webhook configurado exitosamente!"
    echo ""
    echo "Respuesta:"
    echo "$RESPONSE" | python3 -m json.tool
    echo ""
    echo "🎉 ¡Listo! Ahora puedes usar estos comandos en tu bot de Telegram:"
    echo ""
    echo "📝 Comandos disponibles:"
    echo "  /reporte  - Genera un análisis económico AI inmediato"
    echo "  /stats    - Muestra estadísticas de las últimas 24h"
    echo "  /ayuda    - Lista de comandos disponibles"
    echo ""
else
    echo "❌ Error al configurar webhook:"
    echo "$RESPONSE" | python3 -m json.tool
    exit 1
fi

echo ""
echo "🔍 Para verificar el webhook:"
echo "  curl https://api.telegram.org/bot\$TELEGRAM_BOT_TOKEN/getWebhookInfo | python3 -m json.tool"
echo ""
