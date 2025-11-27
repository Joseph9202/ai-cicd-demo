#!/bin/bash
# Script para downgrade a Evolution API v2.0.0

PROJECT_ID="travel-recomender"
ZONE="us-east1-b"
INSTANCE="evolution-api-server"

echo "🔄 DOWNGRADE A EVOLUTION API v2.0.0"
echo "==================================="

gcloud compute ssh $INSTANCE --zone=$ZONE --project=$PROJECT_ID --command='
cd /opt/evolution-api

echo "📝 Modificando docker-compose.yml..."
# Cambiar imagen a v2.0.0
sudo sed -i "s|image: atendai/evolution-api:v2.1.1|image: atendai/evolution-api:v2.0.0|g" docker-compose.yml

echo "🧹 Limpiando todo (contenedores y volúmenes)..."
sudo docker-compose down
sudo docker volume prune -f

echo "🚀 Iniciando Evolution API v2.0.0..."
sudo docker-compose up -d

echo "⏳ Esperando 40 segundos..."
sleep 40

echo "📊 Estado:"
sudo docker ps
'

echo ""
echo "📱 Probando generación de QR..."

export EVOLUTION_API_URL="http://35.196.220.94:8080"
export EVOLUTION_API_KEY="059b14c4be49ef31cc95ac3da78edfdf"

python3 << 'EOF'
import os
import time
import requests
from whatsapp_client import WhatsAppClient

os.environ['EVOLUTION_API_URL'] = 'http://35.196.220.94:8080'
os.environ['EVOLUTION_API_KEY'] = '059b14c4be49ef31cc95ac3da78edfdf'

client = WhatsAppClient()

# Delete old instance
try:
    requests.delete(f"{client.base_url}/instance/delete/{client.instance_name}", 
                   headers=client._get_headers(), timeout=5)
    time.sleep(2)
except:
    pass

print("📱 Generando QR code (v2.0.0)...")
qr = client.get_qr_code(max_attempts=25, wait_seconds=3)

if qr:
    print(f"✅ ¡QR CODE GENERADO! Longitud: {len(qr)}")
    with open('/tmp/whatsapp_qr_final.txt', 'w') as f:
        f.write(qr)
else:
    print("❌ No se pudo obtener el QR")
EOF
