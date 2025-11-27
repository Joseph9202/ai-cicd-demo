#!/bin/bash
# Check WhatsApp instance connection status and logs

export EVOLUTION_API_URL="http://35.196.220.94:8080"
export EVOLUTION_API_KEY="059b14c4be49ef31cc95ac3da78edfdf"
INSTANCE="garch_bot_instance"

echo "🔍 DIAGNÓSTICO DE CONEXIÓN WHATSAPP"
echo "===================================="

# 1. Check connection state
echo "1️⃣ Estado de conexión..."
STATUS=$(curl -s -X GET "$EVOLUTION_API_URL/instance/connectionState/$INSTANCE" \
    -H "apikey: $EVOLUTION_API_KEY")
echo "   Respuesta: $STATUS"
echo ""

# 2. Check instance info
echo "2️⃣ Información de instancia..."
INFO=$(curl -s -X GET "$EVOLUTION_API_URL/instance/fetchInstances?instanceName=$INSTANCE" \
    -H "apikey: $EVOLUTION_API_KEY")
echo "   Respuesta: $INFO"
echo ""

# 3. Get recent logs from VM
echo "3️⃣ Logs recientes de Evolution API..."
gcloud compute ssh evolution-api-server --zone=us-east1-b --project=travel-recomender --command="sudo docker logs evolution-api_evolution-api_1 --tail 50" 2>&1

echo ""
echo "===================================="
