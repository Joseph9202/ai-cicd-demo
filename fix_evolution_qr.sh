#!/bin/bash
# Fix Evolution API to generate QR codes properly

export EVOLUTION_API_URL="http://35.196.220.94:8080"
export EVOLUTION_API_KEY="059b14c4be49ef31cc95ac3da78edfdf"

echo "🔧 CONFIGURANDO EVOLUTION API PARA QR"
echo "====================================="
echo ""

echo "1️⃣ Conectando a la VM..."
gcloud compute ssh evolution-api-server --zone=us-east1-b --project=travel-recomender --command='
echo "📝 Actualizando configuración de Evolution API..."

# Navigate to Evolution API directory
cd /opt/evolution-api

# Stop current container
echo "⏸️ Deteniendo contenedor..."
docker-compose down

# Update .env with CONFIG_SESSION_PHONE_VERSION
echo "✏️ Agregando CONFIG_SESSION_PHONE_VERSION..."
if ! grep -q "CONFIG_SESSION_PHONE_VERSION" .env; then
    echo "CONFIG_SESSION_PHONE_VERSION=4.0.0" >> .env
fi

# Also add other helpful configs
if ! grep -q "QRCODE_LIMIT" .env; then
    echo "QRCODE_LIMIT=30" >> .env
fi

echo "📄 Configuración actualizada:"
cat .env

# Restart container
echo "🚀 Reiniciando contenedor..."
docker-compose up -d

echo "⏳ Esperando que el servicio inicie..."
sleep 10

echo "✅ Evolution API actualizada"
'

echo ""
echo "2️⃣ Esperando estabilización del servicio (15s)..."
sleep 15

echo ""
echo "3️⃣ Probando generación de QR..."
python3 << 'EOF'
import os
os.environ['EVOLUTION_API_URL'] = 'http://35.196.220.94:8080'
os.environ['EVOLUTION_API_KEY'] = '059b14c4be49ef31cc95ac3da78edfdf'

from whatsapp_client import WhatsAppClient
import time

# Delete old instance first
client = WhatsAppClient()
print("🗑️ Eliminando instancia anterior...")
import requests
delete_url = f"{client.base_url}/instance/delete/{client.instance_name}"
requests.delete(delete_url, headers=client._get_headers())
time.sleep(2)

print("\\n📱 Obteniendo QR code...")
qr = client.get_qr_code(max_attempts=15, wait_seconds=2)

if qr:
    if qr == "ALREADY_CONNECTED":
        print("✅ WhatsApp ya está conectado!")
    elif qr.startswith('PAIRING_CODE:'):
        print(f"✅ Código de emparejamiento: {qr}")
    else:
        print(f"✅ QR code recibido!")
        print(f"   Longitud: {len(qr)} caracteres")
        
        # Save to file
        with open('/tmp/whatsapp_qr_final.txt', 'w') as f:
            f.write(qr)
        print("   💾 Guardado en: /tmp/whatsapp_qr_final.txt")
else:
    print("❌ No se pudo obtener el QR")
EOF

echo ""
echo "====================================="
echo "✅ Proceso completado"
