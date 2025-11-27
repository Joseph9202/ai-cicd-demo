#!/bin/bash
# Test QR generation with PostgreSQL setup

export EVOLUTION_API_URL="http://35.196.220.94:8080"
export EVOLUTION_API_KEY="059b14c4be49ef31cc95ac3da78edfdf"

echo "🧪 PROBANDO QR CON POSTGRESQL"
echo "============================"

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

print("\n📱 Generando QR code...")
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
        with open('/tmp/whatsapp_qr_final.txt', 'w') as f:
            f.write(qr)
        print("   💾 Guardado en: /tmp/whatsapp_qr_final.txt")
else:
    print("\n❌ No se pudo obtener el QR")
EOF
