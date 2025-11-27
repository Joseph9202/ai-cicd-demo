#!/bin/bash
# Script para reiniciar instancia de WhatsApp y obtener QR fresco

export EVOLUTION_API_URL="http://35.196.220.94:8080"
export EVOLUTION_API_KEY="059b14c4be49ef31cc95ac3da78edfdf"
INSTANCE="garch_bot_instance"

echo "🔄 REINICIANDO INSTANCIA DE WHATSAPP"
echo "===================================="
echo ""

# 1. Eliminar instancia existente
echo "1️⃣ Eliminando instancia existente..."
DELETE_RESPONSE=$(curl -s -X DELETE "$EVOLUTION_API_URL/instance/delete/$INSTANCE" \
    -H "apikey: $EVOLUTION_API_KEY")
echo "   Respuesta: $DELETE_RESPONSE"
echo ""

# 2. Esperar un momento
sleep 2

# 3. Crear nueva instancia
echo "2️⃣ Creando nueva instancia..."
CREATE_RESPONSE=$(curl -s -X POST "$EVOLUTION_API_URL/instance/create" \
    -H "apikey: $EVOLUTION_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"instanceName\": \"$INSTANCE\", \"integration\": \"WHATSAPP-BAILEYS\", \"qrcode\": true}")
echo "   Respuesta: $CREATE_RESPONSE"
echo ""

# 4. Esperar a que se genere el QR
echo "3️⃣ Esperando generación de QR (5 segundos)..."
sleep 5

# 5. Intentar obtener QR de varios endpoints
echo "4️⃣ Intentando obtener QR..."

# Endpoint 1: /instance/connect
echo "   📍 Probando /instance/connect/$INSTANCE..."
QR1=$(curl -s -X GET "$EVOLUTION_API_URL/instance/connect/$INSTANCE" \
    -H "apikey: $EVOLUTION_API_KEY")
echo "   Respuesta: $QR1"
echo ""

# Endpoint 2: /instance/qrcode
echo "   📍 Probando /instance/qrcode/$INSTANCE..."
QR2=$(curl -s -X GET "$EVOLUTION_API_URL/instance/qrcode/$INSTANCE" \
    -H "apikey: $EVOLUTION_API_KEY")
echo "   Respuesta: $QR2"
echo ""

# Endpoint 3: Fetch instances (para ver estado)
echo "   📍 Verificando estado de instancia..."
STATUS=$(curl -s -X GET "$EVOLUTION_API_URL/instance/fetchInstances?instanceName=$INSTANCE" \
    -H "apikey: $EVOLUTION_API_KEY")
echo "   Estado: $STATUS"
echo ""

echo "===================================="
echo "✅ Proceso completado"
echo ""
echo "💡 Si no aparece el QR, puede que Evolution API v2 use webhooks o eventos."
echo "   Revisa la documentación en: https://doc.evolution-api.com"
