#!/bin/bash
# Simple test to get WhatsApp QR with fixed code

export EVOLUTION_API_URL="http://35.196.220.94:8080"
export EVOLUTION_API_KEY="059b14c4be49ef31cc95ac3da78edfdf"

echo "📱 PRUEBA FINAL DE QR DE WHATSAPP"
echo "================================="
echo ""

python3 << 'EOF'
import os
os.environ['EVOLUTION_API_URL'] = 'http://35.196.220.94:8080'
os.environ['EVOLUTION_API_KEY'] = '059b14c4be49ef31cc95ac3da78edfdf'

from whatsapp_client import WhatsAppClient
import requests
import time

client = WhatsAppClient()

# Delete old instance
print("🗑️ Eliminando instancia anterior...")
delete_url = f"{client.base_url}/instance/delete/{client.instance_name}"
try:
    requests.delete(delete_url, headers=client._get_headers(), timeout=5)
    time.sleep(2)
except:
    pass

print("\n📱 Generando QR code...\n")
qr = client.get_qr_code(max_attempts=20, wait_seconds=2)

if qr:
    if qr == "ALREADY_CONNECTED":
        print("\n✅ WhatsApp ya está conectado!")
    elif qr.startswith('PAIRING_CODE:'):
        print(f"\n✅ Código de emparejamiento: {qr}")
    elif qr.startswith('data:image'):
        print(f"\n✅ QR code recibido (formato data URI)")
        print(f"   Longitud: {len(qr)} caracteres")
        
        # Save to file
        with open('/tmp/whatsapp_qr_success.txt', 'w') as f:
            f.write(qr)
        print("   💾 Guardado en: /tmp/whatsapp_qr_success.txt")
        
        # Try to decode and save as image
        try:
            import base64
            from io import BytesIO
            
            # Extract base64 part
            if ',' in qr:
                base64_data = qr.split(',')[1]
            else:
                base64_data = qr
                
            img_data = base64.b64decode(base64_data)
            with open('/tmp/whatsapp_qr.png', 'wb') as f:
                f.write(img_data)
            print("   🖼️ Imagen guardada en: /tmp/whatsapp_qr.png")
        except Exception as e:
            print(f"   ⚠️ No se pudo guardar como imagen: {e}")
    else:
        print(f"\n✅ QR code recibido!")
        print(f"   Longitud: {len(qr)} caracteres")
        print(f"   Primeros 100 chars: {qr[:100]}...")
        
        # Save to file
        with open('/tmp/whatsapp_qr_success.txt', 'w') as f:
            f.write(qr)
        print("   💾 Guardado en: /tmp/whatsapp_qr_success.txt")
else:
    print("\n❌ No se pudo obtener el QR")
    print("\n💡 Verifica:")
    print("   1. Que Evolution API esté corriendo")
    print("   2. Los logs de Evolution API en la VM")
    print("   3. La versión de Evolution API")
EOF

echo ""
echo "================================="
echo "✅ Prueba completada"
