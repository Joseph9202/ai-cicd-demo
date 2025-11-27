#!/bin/bash
# Script interactivo para configurar credenciales de Telegram paso a paso

echo "🔧 CONFIGURACIÓN INTERACTIVA - TELEGRAM BOT"
echo "==========================================="
echo ""
echo "Este script te guiará para configurar tu bot de Telegram."
echo ""

# Función para leer input de forma segura
read_input() {
    local prompt="$1"
    local var_name="$2"
    echo -n "$prompt: "
    read value
    export $var_name="$value"
    echo "✅ $var_name configurado"
    echo ""
}

# Verificar si ya existe GEMINI_API_KEY
if [ -z "$GEMINI_API_KEY" ]; then
    echo "📝 PASO 1: Configurar GEMINI_API_KEY"
    echo "   Si no tienes una, consíguela en: https://aistudio.google.com/app/apikey"
    read_input "Ingresa tu GEMINI_API_KEY" "GEMINI_API_KEY"
else
    echo "✅ GEMINI_API_KEY ya está configurada"
    echo ""
fi

# Configurar TELEGRAM_BOT_TOKEN
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "📝 PASO 2: Configurar TELEGRAM_BOT_TOKEN"
    echo ""
    echo "   Si no tienes un bot, créalo así:"
    echo "   1. Abre Telegram y busca: @BotFather"
    echo "   2. Envía: /newbot"
    echo "   3. Sigue las instrucciones"
    echo "   4. Copia el token (formato: 123456789:ABC-DEF1234...)"
    echo ""
    read_input "Ingresa tu TELEGRAM_BOT_TOKEN" "TELEGRAM_BOT_TOKEN"
else
    echo "✅ TELEGRAM_BOT_TOKEN ya está configurado"
    echo ""
fi

# Configurar TELEGRAM_CHAT_ID
if [ -z "$TELEGRAM_CHAT_ID" ]; then
    echo "📝 PASO 3: Configurar TELEGRAM_CHAT_ID"
    echo ""
    echo "   Para obtener tu Chat ID:"
    echo "   1. Envía cualquier mensaje a tu bot en Telegram"
    echo "   2. Visita en tu navegador:"
    echo "      https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getUpdates"
    echo "   3. Busca: \"chat\":{\"id\": NUMERO }"
    echo "   4. Copia ese número (puede ser negativo)"
    echo ""
    
    # Ofrecer ayuda para obtener el chat_id
    echo "¿Quieres que intente obtener tu Chat ID automáticamente? (s/n)"
    read -n 1 auto_get
    echo ""
    
    if [ "$auto_get" = "s" ] || [ "$auto_get" = "S" ]; then
        echo ""
        echo "📡 Obteniendo actualizaciones de Telegram..."
        UPDATES=$(curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getUpdates")
        
        # Intentar extraer el chat_id del último mensaje
        CHAT_ID=$(echo "$UPDATES" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['result'][-1]['message']['chat']['id']) if data.get('result') else ''" 2>/dev/null)
        
        if [ -n "$CHAT_ID" ]; then
            echo "✅ Chat ID encontrado: $CHAT_ID"
            export TELEGRAM_CHAT_ID="$CHAT_ID"
            echo ""
        else
            echo "⚠️  No se encontró ningún mensaje. Asegúrate de haber enviado un mensaje a tu bot primero."
            echo ""
            read_input "Ingresa tu TELEGRAM_CHAT_ID manualmente" "TELEGRAM_CHAT_ID"
        fi
    else
        read_input "Ingresa tu TELEGRAM_CHAT_ID" "TELEGRAM_CHAT_ID"
    fi
else
    echo "✅ TELEGRAM_CHAT_ID ya está configurado"
    echo ""
fi

# Resumen de configuración
echo ""
echo "═══════════════════════════════════════"
echo "📋 RESUMEN DE CONFIGURACIÓN"
echo "═══════════════════════════════════════"
echo "GEMINI_API_KEY: ${GEMINI_API_KEY:0:20}..."
echo "TELEGRAM_BOT_TOKEN: ${TELEGRAM_BOT_TOKEN:0:20}..."
echo "TELEGRAM_CHAT_ID: $TELEGRAM_CHAT_ID"
echo ""

# Guardar en archivo .env
echo "💾 ¿Guardar en archivo .env para uso futuro? (s/n)"
read -n 1 save_env
echo ""

if [ "$save_env" = "s" ] || [ "$save_env" = "S" ]; then
    cat > .env << EOF
# Credenciales del Bot - NO SUBIR A GIT
export GEMINI_API_KEY='$GEMINI_API_KEY'
export TELEGRAM_BOT_TOKEN='$TELEGRAM_BOT_TOKEN'
export TELEGRAM_CHAT_ID='$TELEGRAM_CHAT_ID'
EOF
    echo "✅ Credenciales guardadas en .env"
    echo "   Para usarlas en el futuro: source .env"
    echo ""
fi

# Probar conexión
echo "🧪 ¿Probar conexión con Telegram ahora? (s/n)"
read -n 1 test_conn
echo ""

if [ "$test_conn" = "s" ] || [ "$test_conn" = "S" ]; then
    echo ""
    echo "📤 Enviando mensaje de prueba..."
    
    MESSAGE="✅ ¡Configuración exitosa!

🤖 Tu bot está listo para usar
⏰ $(date '+%Y-%m-%d %H:%M:%S')

Comandos disponibles:
/reporte - Análisis AI
/stats - Estadísticas 24h
/ayuda - Ver ayuda"
    
    RESPONSE=$(curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
        -H "Content-Type: application/json" \
        -d "{\"chat_id\":\"${TELEGRAM_CHAT_ID}\",\"text\":\"${MESSAGE}\"}")
    
    if echo "$RESPONSE" | grep -q '"ok":true'; then
        echo "✅ ¡Mensaje enviado con éxito!"
        echo "   Revisa tu Telegram"
        echo ""
    else
        echo "❌ Error al enviar mensaje:"
        echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
        echo ""
    fi
fi

# Siguiente paso
echo ""
echo "═══════════════════════════════════════"
echo "🚀 PRÓXIMOS PASOS"
echo "═══════════════════════════════════════"
echo ""
echo "1. Desplegar a Cloud Functions:"
echo "   ./deploy_with_ai.sh"
echo ""
echo "2. Configurar webhook:"
echo "   ./setup_webhook.sh"
echo ""
echo "3. Probar el bot enviando en Telegram:"
echo "   /reporte"
echo ""
