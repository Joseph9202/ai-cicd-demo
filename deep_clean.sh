#!/bin/bash
# Script para limpieza profunda y reinicio

PROJECT_ID="travel-recomender"
ZONE="us-east1-b"
INSTANCE="evolution-api-server"

echo "🧹 LIMPIEZA PROFUNDA DE SESIONES"
echo "=============================="

gcloud compute ssh $INSTANCE --zone=$ZONE --project=$PROJECT_ID --command='
cd /opt/evolution-api

echo "🛑 Deteniendo servicios..."
sudo docker-compose down

echo "🗑️ Eliminando volúmenes de datos (sesiones corruptas)..."
sudo docker volume rm evolution-api_evolution_store evolution-api_evolution_instances
sudo docker volume prune -f

echo "🚀 Iniciando servicios limpios..."
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

# Instance name
instance = "garch_bot_instance"

# Create instance
print(f"📱 Creando instancia {instance}...")
try:
    url = f"{client.base_url}/instance/create"
    payload = {
        "instanceName": instance,
        "integration": "WHATSAPP-BAILEYS",
        "qrcode": True
    }
    response = requests.post(url, json=payload, headers=client._get_headers(), timeout=10)
    print(f"   Respuesta: {response.json()}")
except Exception as e:
    print(f"   Error creando: {e}")

time.sleep(5)

print("\n📱 Buscando QR code...")
qr = client.get_qr_code(max_attempts=25, wait_seconds=3)

if qr:
    print(f"✅ ¡QR CODE GENERADO! Longitud: {len(qr)}")
    with open('/tmp/whatsapp_qr_final.txt', 'w') as f:
        f.write(qr)
else:
    print("❌ No se pudo obtener el QR")
EOF
