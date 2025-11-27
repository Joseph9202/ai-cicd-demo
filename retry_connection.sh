#!/bin/bash
# Script para reintentar conexión limpia

PROJECT_ID="travel-recomender"
ZONE="us-east1-b"
INSTANCE="evolution-api-server"

echo "🔄 REINTENTO DE CONEXIÓN LIMPIA"
echo "=============================="

gcloud compute ssh $INSTANCE --zone=$ZONE --project=$PROJECT_ID --command='
echo "🕒 Verificando hora del sistema..."
date

echo "♻️ Reiniciando contenedor de Evolution API..."
sudo docker restart evolution-api_evolution-api_1
sleep 10
'

echo ""
echo "📱 Generando nuevo QR..."

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

# Create and get QR
print("📱 Obteniendo QR fresco...")
qr = client.get_qr_code(max_attempts=10, wait_seconds=3)

if qr:
    print(f"✅ ¡QR CODE GENERADO! Longitud: {len(qr)}")
    with open('/tmp/whatsapp_qr_final.txt', 'w') as f:
        f.write(qr)
    print("👉 ¡ESCANEA AHORA RÁPIDAMENTE!")
else:
    print("❌ No se pudo obtener el QR")
EOF
