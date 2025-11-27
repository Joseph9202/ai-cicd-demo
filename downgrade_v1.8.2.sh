#!/bin/bash
# Script para downgrade a Evolution API v1.8.2 (Versión Estable)

PROJECT_ID="travel-recomender"
ZONE="us-east1-b"
INSTANCE="evolution-api-server"

echo "🔄 DOWNGRADE A EVOLUTION API v1.8.2 (ESTABLE)"
echo "============================================="

gcloud compute ssh $INSTANCE --zone=$ZONE --project=$PROJECT_ID --command='
cd /opt/evolution-api

echo "🛑 Deteniendo servicios..."
sudo docker-compose down
sudo docker volume prune -f

echo "📝 Creando docker-compose.yml para v1.8.2..."
sudo tee docker-compose.yml > /dev/null <<EOF
version: "3.3"
services:
  evolution-api:
    image: atendai/evolution-api:v1.8.2
    restart: always
    ports:
      - "8080:8080"
    environment:
      - SERVER_URL=http://localhost:8080
      - AUTHENTICATION_API_KEY=\${AUTHENTICATION_API_KEY}
      - DEL_INSTANCE=false
      # v1.8.2 usa configuración diferente
      - DB_TYPE=postgres
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_USER=evolution
      - DB_PASS=evolution
      - DB_NAME=evolution
      - REDIS_ENABLED=true
      - REDIS_URI=redis://redis:6379
      - REDIS_PREFIX=evolution
    volumes:
      - evolution_instances:/evolution/instances
      - evolution_store:/evolution/store
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15-alpine
    restart: always
    environment:
      - POSTGRES_USER=evolution
      - POSTGRES_PASSWORD=evolution
      - POSTGRES_DB=evolution
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    restart: always
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  evolution_instances:
  evolution_store:
  postgres_data:
  redis_data:
EOF

echo "🚀 Iniciando Evolution API v1.8.2..."
sudo docker-compose up -d

echo "⏳ Esperando 40 segundos..."
sleep 40

echo "📊 Estado:"
sudo docker ps
'

echo ""
echo "📱 Probando generación de QR (v1.8.2)..."

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

print("📱 Generando QR code...")
# v1.8.2 might respond faster
qr = client.get_qr_code(max_attempts=25, wait_seconds=3)

if qr:
    print(f"✅ ¡QR CODE GENERADO! Longitud: {len(qr)}")
    with open('/tmp/whatsapp_qr_final.txt', 'w') as f:
        f.write(qr)
else:
    print("❌ No se pudo obtener el QR")
EOF
