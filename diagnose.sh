#!/bin/bash
# Script rápido de diagnóstico y reparación

echo "🔍 DIAGNÓSTICO RÁPIDO - TELEGRAM BOT"
echo "====================================="
echo ""

# 1. Verificar variables locales
echo "1️⃣ Variables de entorno locales:"
if [ -n "$GEMINI_API_KEY" ]; then
    echo "   ✅ GEMINI_API_KEY: Configurada"
else
    echo "   ❌ GEMINI_API_KEY: NO configurada"
fi

if [ -n "$TELEGRAM_BOT_TOKEN" ]; then
    echo "   ✅ TELEGRAM_BOT_TOKEN: Configurada"
else
    echo "   ❌ TELEGRAM_BOT_TOKEN: NO configurada"
fi

if [ -n "$TELEGRAM_CHAT_ID" ]; then
    echo "   ✅ TELEGRAM_CHAT_ID: Configurada"
else
    echo "   ❌ TELEGRAM_CHAT_ID: NO configurada"
fi

echo ""

# 2. Verificar Cloud Function
echo "2️⃣ Variables en Cloud Functions:"
ENV_VARS=$(gcloud functions describe garch-trading-bot --region=us-east1 --format="value(serviceConfig.environmentVariables)" 2>/dev/null)

if echo "$ENV_VARS" | grep -q "GEMINI_API_KEY"; then
    echo "   ✅ GEMINI_API_KEY: Desplegada"
else
    echo "   ❌ GEMINI_API_KEY: NO desplegada"
fi

if echo "$ENV_VARS" | grep -q "TELEGRAM_BOT_TOKEN"; then
    echo "   ✅ TELEGRAM_BOT_TOKEN: Desplegada"
else
    echo "   ❌ TELEGRAM_BOT_TOKEN: NO desplegada"
fi

if echo "$ENV_VARS" | grep -q "TELEGRAM_CHAT_ID"; then
    echo "   ✅ TELEGRAM_CHAT_ID: Desplegada"
else
    echo "   ❌ TELEGRAM_CHAT_ID: NO desplegada"
fi

echo ""

# 3. Verificar webhook
echo "3️⃣ Webhook de Telegram:"
if [ -n "$TELEGRAM_BOT_TOKEN" ]; then
    WEBHOOK_INFO=$(curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getWebhookInfo")
    WEBHOOK_URL=$(echo "$WEBHOOK_INFO" | python3 -c "import sys, json; print(json.load(sys.stdin).get('result', {}).get('url', 'NO CONFIGURADO'))" 2>/dev/null)
    
    if [ "$WEBHOOK_URL" != "NO CONFIGURADO" ] && [ -n "$WEBHOOK_URL" ]; then
        echo "   ✅ Webhook: $WEBHOOK_URL"
    else
        echo "   ❌ Webhook: NO configurado"
    fi
else
    echo "   ⚠️  No se puede verificar (TELEGRAM_BOT_TOKEN no configurado)"
fi

echo ""
echo "═══════════════════════════════════════"
echo "🔧 SOLUCIONES SUGERIDAS"
echo "═══════════════════════════════════════"
echo ""

# Determinar qué hacer
NEEDS_LOCAL_CONFIG=false
NEEDS_DEPLOY=false
NEEDS_WEBHOOK=false

if [ -z "$GEMINI_API_KEY" ] || [ -z "$TELEGRAM_BOT_TOKEN" ] || [ -z "$TELEGRAM_CHAT_ID" ]; then
    NEEDS_LOCAL_CONFIG=true
fi

if ! echo "$ENV_VARS" | grep -q "TELEGRAM_BOT_TOKEN"; then
    NEEDS_DEPLOY=true
fi

if [ "$WEBHOOK_URL" = "NO CONFIGURADO" ] || [ -z "$WEBHOOK_URL" ]; then
    NEEDS_WEBHOOK=true
fi

# Mostrar pasos necesarios
STEP=1

if $NEEDS_LOCAL_CONFIG; then
    echo "${STEP}. Configurar credenciales locales:"
    echo "   ./setup_telegram.sh"
    echo ""
    STEP=$((STEP+1))
fi

if $NEEDS_DEPLOY; then
    echo "${STEP}. Re-desplegar Cloud Function con credenciales:"
    echo "   ./deploy_with_ai.sh"
    echo ""
    STEP=$((STEP+1))
fi

if $NEEDS_WEBHOOK; then
    echo "${STEP}. Configurar webhook de Telegram:"
    echo "   ./setup_webhook.sh"
    echo ""
    STEP=$((STEP+1))
fi

if ! $NEEDS_LOCAL_CONFIG && ! $NEEDS_DEPLOY && ! $NEEDS_WEBHOOK; then
    echo "✅ ¡Todo está configurado correctamente!"
    echo ""
    echo "Prueba enviando a tu bot en Telegram:"
    echo "   /reporte"
    echo "   /stats"
    echo "   /ayuda"
fi

echo ""
echo "💡 TIP: Si tienes un archivo .env, cárgalo con:"
echo "   source .env"
echo ""
