#!/bin/bash
# Script interactivo para configurar credenciales de WhatsApp (Evolution API)

echo "🔧 CONFIGURACIÓN INTERACTIVA - WHATSAPP (EVOLUTION API)"
echo "======================================================="
echo ""
echo "Este script te guiará para configurar las notificaciones por WhatsApp."
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

# 1. Configurar EVOLUTION_API_URL
if [ -z "$EVOLUTION_API_URL" ]; then
    echo "📝 PASO 1: Configurar URL de Evolution API"
    echo "   Ejemplo: https://api.tudominio.com"
    read_input "Ingresa la URL de tu API" "EVOLUTION_API_URL"
else
    echo "✅ EVOLUTION_API_URL ya está configurada"
    echo ""
fi

# 2. Configurar EVOLUTION_API_KEY
if [ -z "$EVOLUTION_API_KEY" ]; then
    echo "📝 PASO 2: Configurar API Key"
    echo "   Esta es la Global API Key de tu instancia de Evolution"
    read_input "Ingresa tu API Key" "EVOLUTION_API_KEY"
else
    echo "✅ EVOLUTION_API_KEY ya está configurada"
    echo ""
fi

# 3. Configurar WHATSAPP_TARGET_NUMBER
if [ -z "$WHATSAPP_TARGET_NUMBER" ]; then
    echo "📝 PASO 3: Configurar Número de Destino"
    echo "   El número al que llegarán los reportes (con código de país)"
    echo "   Ejemplo: 573001234567"
    read_input "Ingresa el número de destino" "WHATSAPP_TARGET_NUMBER"
else
    echo "✅ WHATSAPP_TARGET_NUMBER ya está configurado"
    echo ""
fi

# Resumen
echo ""
echo "═══════════════════════════════════════"
echo "📋 RESUMEN DE CONFIGURACIÓN"
echo "═══════════════════════════════════════"
echo "URL: $EVOLUTION_API_URL"
echo "API Key: ${EVOLUTION_API_KEY:0:10}..."
echo "Número: $WHATSAPP_TARGET_NUMBER"
echo ""

# Guardar en .env
echo "💾 ¿Guardar en archivo .env? (s/n)"
read -n 1 save_env
echo ""

if [ "$save_env" = "s" ] || [ "$save_env" = "S" ]; then
    # Append to .env if exists, or create new
    if [ -f .env ]; then
        # Remove old entries if they exist to avoid duplicates
        grep -v "EVOLUTION_API_URL" .env > .env.tmp && mv .env.tmp .env
        grep -v "EVOLUTION_API_KEY" .env > .env.tmp && mv .env.tmp .env
        grep -v "WHATSAPP_TARGET_NUMBER" .env > .env.tmp && mv .env.tmp .env
    fi
    
    cat >> .env << EOF

# WhatsApp / Evolution API
export EVOLUTION_API_URL='$EVOLUTION_API_URL'
export EVOLUTION_API_KEY='$EVOLUTION_API_KEY'
export WHATSAPP_TARGET_NUMBER='$WHATSAPP_TARGET_NUMBER'
EOF
    echo "✅ Credenciales guardadas en .env"
    echo "   Para usarlas: source .env"
    echo ""
fi

# Probar conexión
echo "🧪 ¿Probar conexión (enviar mensaje de prueba)? (s/n)"
read -n 1 test_conn
echo ""

if [ "$test_conn" = "s" ] || [ "$test_conn" = "S" ]; then
    echo "Enviando mensaje de prueba..."
    
    # Instance name hardcoded in python client, using same here for consistency
    INSTANCE="garch_bot_instance"
    
    # Check if instance exists/create it
    echo "Verificando instancia '$INSTANCE'..."
    CREATE_URL="$EVOLUTION_API_URL/instance/create"
    CREATE_PAYLOAD="{\"instanceName\": \"$INSTANCE\", \"integration\": \"WHATSAPP-BAILEYS\", \"qrcode\": true}"
    
    curl -s -X POST "$CREATE_URL" \
        -H "apikey: $EVOLUTION_API_KEY" \
        -H "Content-Type: application/json" \
        -d "$CREATE_PAYLOAD" > /dev/null
        
    # Send message
    SEND_URL="$EVOLUTION_API_URL/message/sendText/$INSTANCE"
    MSG="✅ *Prueba de Conexión GARCH Bot*\n\nSi lees esto, la integración de WhatsApp está funcionando correctamente. 🚀"
    
    PAYLOAD="{\"number\": \"$WHATSAPP_TARGET_NUMBER\", \"options\": {\"delay\": 1200, \"presence\": \"composing\"}, \"textMessage\": {\"text\": \"$MSG\"}}"
    
    RESPONSE=$(curl -s -X POST "$SEND_URL" \
        -H "apikey: $EVOLUTION_API_KEY" \
        -H "Content-Type: application/json" \
        -d "$PAYLOAD")
        
    echo "Respuesta del servidor:"
    echo "$RESPONSE"
    echo ""
fi

echo "🚀 Listo! Ahora ejecuta ./deploy_with_ai.sh para aplicar los cambios."
