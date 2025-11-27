#!/bin/bash
# Test WhatsApp QR generation with proper credentials

echo "🧪 PROBANDO GENERACIÓN DE QR DE WHATSAPP"
echo "========================================"
echo ""

# Set credentials
export EVOLUTION_API_URL="http://35.196.220.94:8080"
export EVOLUTION_API_KEY="059b14c4be49ef31cc95ac3da78edfdf"
export WHATSAPP_TARGET_NUMBER="573001234567"  # Placeholder

# Run the diagnostic script again
echo "1️⃣ Ejecutando diagnóstico con credenciales..."
./test_whatsapp_qr.sh
echo ""

# Test with Python
echo "2️⃣ Probando con Python..."
python3 << 'EOF'
import os
os.environ['EVOLUTION_API_URL'] = 'http://35.196.220.94:8080'
os.environ['EVOLUTION_API_KEY'] = '059b14c4be49ef31cc95ac3da78edfdf'

from whatsapp_client import get_whatsapp_qr

print("📱 Llamando a get_whatsapp_qr()...")
qr = get_whatsapp_qr()

if qr:
    if qr.startswith('PAIRING_CODE:'):
        print(f"✅ Código de emparejamiento recibido: {qr}")
    else:
        print(f"✅ QR code recibido (longitud: {len(qr)} caracteres)")
        print(f"   Primeros 50 chars: {qr[:50]}...")
        
        # Save to file
        with open('/tmp/whatsapp_qr.txt', 'w') as f:
            f.write(qr)
        print("   💾 Guardado en: /tmp/whatsapp_qr.txt")
else:
    print("❌ No se recibió QR code")
EOF

echo ""
echo "✅ Prueba completada"
