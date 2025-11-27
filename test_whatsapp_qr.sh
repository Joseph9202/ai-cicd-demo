#!/bin/bash
# Script para diagnosticar y probar la generación del QR de WhatsApp

echo "🔍 DIAGNÓSTICO DE WHATSAPP QR CODE"
echo "=================================="
echo ""

# 1. Verificar VM
echo "1️⃣ Verificando VM de Evolution API..."
VM_STATUS=$(gcloud compute instances list --filter="name:evolution-api-server" --format="value(status)" --project=travel-recomender 2>/dev/null)
VM_IP=$(gcloud compute instances list --filter="name:evolution-api-server" --format="value(networkInterfaces[0].accessConfigs[0].natIP)" --project=travel-recomender 2>/dev/null)

if [ "$VM_STATUS" = "RUNNING" ]; then
    echo "   ✅ VM está corriendo"
    echo "   📍 IP: $VM_IP"
else
    echo "   ❌ VM no está corriendo. Estado: $VM_STATUS"
    echo "   💡 Ejecuta: ./setup_evolution_vm.sh"
    exit 1
fi
echo ""

# 2. Verificar variables de entorno
echo "2️⃣ Verificando variables de entorno..."
if [ -z "$EVOLUTION_API_URL" ]; then
    echo "   ⚠️ EVOLUTION_API_URL no configurada"
    echo "   💡 Sugerencia: export EVOLUTION_API_URL='http://$VM_IP:8080'"
else
    echo "   ✅ EVOLUTION_API_URL: $EVOLUTION_API_URL"
fi

if [ -z "$EVOLUTION_API_KEY" ]; then
    echo "   ⚠️ EVOLUTION_API_KEY no configurada"
    echo "   💡 Recupera la key con:"
    echo "      gcloud compute instances get-serial-port-output evolution-api-server --zone=us-east1-b --project=travel-recomender | grep AUTHENTICATION_API_KEY"
else
    echo "   ✅ EVOLUTION_API_KEY: ${EVOLUTION_API_KEY:0:10}..."
fi
echo ""

# 3. Probar conectividad
echo "3️⃣ Probando conectividad con Evolution API..."
if [ -n "$EVOLUTION_API_URL" ]; then
    HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" "$EVOLUTION_API_URL" 2>/dev/null)
    if [ "$HEALTH_CHECK" = "200" ] || [ "$HEALTH_CHECK" = "404" ]; then
        echo "   ✅ API responde (HTTP $HEALTH_CHECK)"
    else
        echo "   ❌ API no responde (HTTP $HEALTH_CHECK)"
        echo "   💡 Verifica que Docker esté corriendo en la VM"
    fi
else
    echo "   ⏭️ Saltando (EVOLUTION_API_URL no configurada)"
fi
echo ""

# 4. Intentar crear instancia y obtener QR
echo "4️⃣ Intentando generar QR code..."
if [ -n "$EVOLUTION_API_URL" ] && [ -n "$EVOLUTION_API_KEY" ]; then
    INSTANCE="garch_bot_instance"
    
    # Crear instancia
    echo "   📱 Creando instancia '$INSTANCE'..."
    CREATE_RESPONSE=$(curl -s -X POST "$EVOLUTION_API_URL/instance/create" \
        -H "apikey: $EVOLUTION_API_KEY" \
        -H "Content-Type: application/json" \
        -d "{\"instanceName\": \"$INSTANCE\", \"integration\": \"WHATSAPP-BAILEYS\", \"qrcode\": true}")
    
    echo "   Respuesta: $CREATE_RESPONSE"
    echo ""
    
    # Esperar un momento
    sleep 2
    
    # Intentar obtener QR
    echo "   🔍 Obteniendo QR code..."
    QR_RESPONSE=$(curl -s -X GET "$EVOLUTION_API_URL/instance/connect/$INSTANCE" \
        -H "apikey: $EVOLUTION_API_KEY")
    
    echo "   Respuesta: $QR_RESPONSE"
    echo ""
    
    # Verificar si hay base64 en la respuesta
    if echo "$QR_RESPONSE" | grep -q "base64"; then
        echo "   ✅ QR code generado exitosamente!"
        
        # Guardar QR en archivo para inspección
        echo "$QR_RESPONSE" | grep -o '"base64":"[^"]*"' | cut -d'"' -f4 > /tmp/whatsapp_qr_base64.txt
        echo "   💾 QR guardado en: /tmp/whatsapp_qr_base64.txt"
    else
        echo "   ⚠️ No se encontró QR en la respuesta"
        echo "   💡 Posibles causas:"
        echo "      - La instancia ya está conectada"
        echo "      - El endpoint cambió en la versión de Evolution API"
        echo "      - Necesita reiniciar la instancia"
    fi
else
    echo "   ⏭️ Saltando (credenciales no configuradas)"
fi
echo ""

# 5. Verificar estado de la instancia
echo "5️⃣ Verificando estado de la instancia..."
if [ -n "$EVOLUTION_API_URL" ] && [ -n "$EVOLUTION_API_KEY" ]; then
    INSTANCE_STATUS=$(curl -s -X GET "$EVOLUTION_API_URL/instance/fetchInstances" \
        -H "apikey: $EVOLUTION_API_KEY")
    
    echo "   Instancias: $INSTANCE_STATUS"
else
    echo "   ⏭️ Saltando (credenciales no configuradas)"
fi
echo ""

echo "=================================="
echo "✅ Diagnóstico completado"
echo ""
echo "📝 PRÓXIMOS PASOS:"
echo "   1. Si faltan variables, configúralas con: source .env"
echo "   2. Si la API no responde, verifica Docker en la VM"
echo "   3. Si el QR no aparece, prueba el endpoint /instance/qrcode/$INSTANCE"
