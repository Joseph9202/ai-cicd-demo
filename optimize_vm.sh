#!/bin/bash
# Script para restaurar v2.1.1 y optimizar memoria (Swap)

PROJECT_ID="travel-recomender"
ZONE="us-east1-b"
INSTANCE="evolution-api-server"

echo "🔧 OPTIMIZANDO VM Y RESTAURANDO V2.1.1"
echo "======================================="

gcloud compute ssh $INSTANCE --zone=$ZONE --project=$PROJECT_ID --command='
echo "💾 Configurando Swap de 2GB..."
# Verificar si ya existe swap
if [ ! -f /swapfile ]; then
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo "/swapfile none swap sw 0 0" | sudo tee -a /etc/fstab
    echo "✅ Swap creado"
else
    echo "✅ Swap ya existe"
fi

cd /opt/evolution-api

echo "📝 Restaurando docker-compose.yml a v2.1.1..."
# Asegurar que usamos la imagen v2.1.1
sudo sed -i "s|image: atendai/evolution-api:v2.0.0|image: atendai/evolution-api:v2.1.1|g" docker-compose.yml

echo "🚀 Reiniciando servicios..."
sudo docker-compose down
sudo docker-compose up -d

echo "⏳ Esperando 30 segundos..."
sleep 30

echo "📊 Memoria:"
free -h
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

print("📱 Generando QR code (v2.1.1 + Swap)...")
qr = client.get_qr_code(max_attempts=25, wait_seconds=3)

if qr:
    print(f"✅ ¡QR CODE GENERADO! Longitud: {len(qr)}")
    with open('/tmp/whatsapp_qr_final.txt', 'w') as f:
        f.write(qr)
else:
    print("❌ No se pudo obtener el QR")
EOF
