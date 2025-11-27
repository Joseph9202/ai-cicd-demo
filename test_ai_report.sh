#!/bin/bash
# Test script para el sistema de reportes AI

echo "🧪 Testing AI Report System"
echo "============================"
echo ""

# Check if GEMINI_API_KEY is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ GEMINI_API_KEY no está configurada"
    echo ""
    echo "Para configurarla:"
    echo "  1. Obtén tu API key en: https://aistudio.google.com/app/apikey"
    echo "  2. Ejecuta: export GEMINI_API_KEY='tu-api-key-aqui'"
    echo ""
    exit 1
fi

echo "✅ GEMINI_API_KEY configurada"
echo ""

# Check Telegram config
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "⚠️  TELEGRAM_BOT_TOKEN no está configurada (opcional para pruebas)"
fi

if [ -z "$TELEGRAM_CHAT_ID" ]; then
    echo "⚠️  TELEGRAM_CHAT_ID no está configurada (opcional para pruebas)"
fi

echo ""
echo "📊 Para probar el endpoint de reporte:"
echo "  curl -X POST http://localhost:5000/report"
echo ""
echo "🚀 Para desplegar a producción con la API key:"
echo "  gcloud functions deploy garch-trading-bot \\"
echo "    --runtime python311 \\"
echo "    --trigger-http \\"
echo "    --allow-unauthenticated \\"
echo "    --entry-point garch_trading_bot \\"
echo "    --region us-east1 \\"
echo "    --memory 512MB \\"
echo "    --timeout 540s \\"
echo "    --set-env-vars GEMINI_API_KEY=\$GEMINI_API_KEY"
echo ""
