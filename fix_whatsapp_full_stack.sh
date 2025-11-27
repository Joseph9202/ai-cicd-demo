#!/bin/bash
# Script para configurar Evolution API con PostgreSQL Y Redis (Stack Completo)

PROJECT_ID="travel-recomender"
ZONE="us-east1-b"
INSTANCE="evolution-api-server"

echo "🔧 SOLUCIONANDO PROBLEMA DE CONEXIÓN - STACK COMPLETO"
echo "======================================================"
echo ""
echo "Los logs indican que Evolution API necesita Redis para colas/caché"
echo "incluso cuando usa PostgreSQL como base de datos principal."
echo ""

echo "1️⃣ Conectando a la VM y actualizando configuración..."

gcloud compute ssh $INSTANCE --zone=$ZONE --project=$PROJECT_ID --command='
echo "📝 Creando docker-compose.yml con PostgreSQL + Redis..."

cd /opt/evolution-api

# Detener contenedores actuales
sudo docker-compose down

# Crear nuevo docker-compose.yml con AMBOS servicios
sudo tee docker-compose.yml > /dev/null <<EOF
version: "3.3"
services:
  evolution-api:
    image: atendai/evolution-api:v2.1.1
    restart: always
    ports:
      - "8080:8080"
    environment:
      - SERVER_URL=http://localhost:8080
      - AUTHENTICATION_API_KEY=\${AUTHENTICATION_API_KEY}
      # Base de datos principal (PostgreSQL)
      - DATABASE_ENABLED=true
      - DATABASE_PROVIDER=postgresql
      - DATABASE_CONNECTION_URI=postgresql://evolution:evolution@postgres:5432/evolution
      - DATABASE_CONNECTION_CLIENT_NAME=evolution_exchange
      # Caché y Colas (Redis)
      - CACHE_REDIS_ENABLED=true
      - CACHE_REDIS_URI=redis://redis:6379
      - REDIS_ENABLED=true
      - REDIS_URI=redis://redis:6379
      # Configuración adicional
      - LOG_LEVEL=ERROR
      - DEL_INSTANCE=false
      - CONFIG_SESSION_PHONE_VERSION=2.3000.1014080434
      - QRCODE_LIMIT=30
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

echo "✅ docker-compose.yml actualizado con stack completo"
echo ""

echo "🚀 Iniciando servicios..."
sudo docker-compose up -d

echo "⏳ Esperando que los servicios inicien (30 segundos)..."
sleep 30

echo "📊 Estado de contenedores:"
sudo docker ps
'

if [ $? -ne 0 ]; then
    echo "❌ Error configurando Evolution API"
    exit 1
fi

echo ""
echo "2️⃣ Esperando estabilización (15 segundos)..."
sleep 15

echo ""
echo "3️⃣ Probando generación de QR..."

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

# Delete old instance if exists
print("🗑️ Limpiando instancia anterior...")
try:
    requests.delete(f"{client.base_url}/instance/delete/{client.instance_name}", 
                   headers=client._get_headers(), timeout=5)
    time.sleep(3)
except:
    pass

print("\n📱 Generando QR code con Stack Completo (Postgres + Redis)...")
qr = client.get_qr_code(max_attempts=25, wait_seconds=3)

if qr:
    if qr == "ALREADY_CONNECTED":
        print("\n✅ WhatsApp ya está conectado!")
    elif qr.startswith('PAIRING_CODE:'):
        print(f"\n✅ Código de emparejamiento: {qr}")
    else:
        print(f"\n✅ ¡QR CODE GENERADO EXITOSAMENTE!")
        print(f"   Longitud: {len(qr)} caracteres")
        
        # Save to file
        with open('/tmp/whatsapp_qr_full.txt', 'w') as f:
            f.write(qr)
        print("   💾 Guardado en: /tmp/whatsapp_qr_full.txt")
        
        # Try to save as image
        try:
            import base64
            if ',' in qr:
                base64_data = qr.split(',')[1]
            else:
                base64_data = qr.replace('data:image/png;base64,', '')
                
            img_data = base64.b64decode(base64_data)
            with open('/tmp/whatsapp_qr.png', 'wb') as f:
                f.write(img_data)
            print("   🖼️ Imagen guardada en: /tmp/whatsapp_qr.png")
            print("\n   📱 Escanea este QR con WhatsApp:")
            print("      WhatsApp > Dispositivos vinculados > Vincular dispositivo")
        except Exception as e:
            print(f"   ⚠️ No se pudo guardar como imagen: {e}")
else:
    print("\n❌ No se pudo obtener el QR")
    print("   Revisa los logs: sudo docker logs evolution-api_evolution-api_1")
EOF

echo ""
echo "========================================================"
echo "✅ Proceso completado"
