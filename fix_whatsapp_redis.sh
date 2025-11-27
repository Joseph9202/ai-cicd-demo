#!/bin/bash
# Script para agregar Redis a Evolution API y solucionar el problema del QR

PROJECT_ID="travel-recomender"
ZONE="us-east1-b"
INSTANCE="evolution-api-server"

echo "🔧 SOLUCIONANDO PROBLEMA DE QR - AGREGANDO REDIS"
echo "================================================"
echo ""

echo "📝 Este script va a:"
echo "   1. Agregar Redis al docker-compose.yml"
echo "   2. Reiniciar Evolution API con Redis"
echo "   3. Probar la generación del QR"
echo ""
read -p "¿Continuar? (s/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "❌ Cancelado"
    exit 1
fi

echo ""
echo "1️⃣ Conectando a la VM y actualizando configuración..."

gcloud compute ssh $INSTANCE --zone=$ZONE --project=$PROJECT_ID --command='
echo "📝 Creando nuevo docker-compose.yml con Redis..."

cd /opt/evolution-api

# Backup del archivo actual
sudo cp docker-compose.yml docker-compose.yml.backup

# Crear nuevo docker-compose.yml
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
      - DATABASE_ENABLED=true
      - DATABASE_PROVIDER=redis
      - REDIS_URI=redis://redis:6379
      - LOG_LEVEL=ERROR
      - DEL_INSTANCE=false
      - CONFIG_SESSION_PHONE_VERSION=4.0.0
      - QRCODE_LIMIT=30
    volumes:
      - evolution_instances:/evolution/instances
      - evolution_store:/evolution/store
    depends_on:
      - redis

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
  redis_data:
EOF

echo "✅ docker-compose.yml actualizado"
echo ""

echo "🔄 Deteniendo contenedores actuales..."
sudo docker-compose down

echo "🚀 Iniciando Evolution API con Redis..."
sudo docker-compose up -d

echo "⏳ Esperando que los servicios inicien (20 segundos)..."
sleep 20

echo "📊 Estado de contenedores:"
sudo docker ps

echo ""
echo "✅ Evolution API con Redis configurado"
'

if [ $? -ne 0 ]; then
    echo "❌ Error configurando Evolution API"
    exit 1
fi

echo ""
echo "2️⃣ Esperando estabilización (10 segundos)..."
sleep 10

echo ""
echo "3️⃣ Probando generación de QR..."

export EVOLUTION_API_URL="http://35.196.220.94:8080"
export EVOLUTION_API_KEY="059b14c4be49ef31cc95ac3da78edfdf"

python3 << 'EOF'
import os
import time
os.environ['EVOLUTION_API_URL'] = 'http://35.196.220.94:8080'
os.environ['EVOLUTION_API_KEY'] = '059b14c4be49ef31cc95ac3da78edfdf'

from whatsapp_client import WhatsAppClient
import requests

client = WhatsAppClient()

# Delete old instance
print("🗑️ Eliminando instancia anterior...")
delete_url = f"{client.base_url}/instance/delete/{client.instance_name}"
try:
    requests.delete(delete_url, headers=client._get_headers(), timeout=5)
    time.sleep(3)
except:
    pass

print("\n📱 Generando QR code con Redis configurado...\n")
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
        with open('/tmp/whatsapp_qr_redis.txt', 'w') as f:
            f.write(qr)
        print("   💾 Guardado en: /tmp/whatsapp_qr_redis.txt")
        
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
    print("\n💡 Revisa los logs de Evolution API:")
    print("   gcloud compute ssh evolution-api-server --zone=us-east1-b --command='sudo docker logs \$(sudo docker ps -q --filter name=evolution-api) --tail 50'")
EOF

echo ""
echo "================================================"
echo "✅ Proceso completado"
echo ""
echo "📝 Próximos pasos:"
echo "   1. Si el QR se generó, escanéalo con WhatsApp"
echo "   2. Si no, revisa los logs de Evolution API"
echo "   3. Verifica que Redis esté corriendo: sudo docker ps"
