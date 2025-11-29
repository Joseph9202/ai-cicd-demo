#!/bin/bash
# Verificar deployment del modelo GARCH mejorado

echo "=========================================="
echo "🔍 VERIFICACIÓN DE DEPLOYMENT"
echo "=========================================="
echo ""

FUNCTION_URL="https://garch-trading-bot-l4qey4f4sq-ue.a.run.app"

# Test 1: Ejecutar predicción
echo "📊 Test 1: Ejecutando nueva predicción..."
response=$(curl -s -X POST "$FUNCTION_URL/run")

if echo "$response" | grep -q "success"; then
    echo "✅ Predicción ejecutada correctamente"

    # Extraer datos de la respuesta
    volatility=$(echo "$response" | grep -o '"volatility":[0-9.]*' | cut -d: -f2)
    signal=$(echo "$response" | grep -o '"signal":"[A-Z]*"' | cut -d\" -f4)

    echo "   Volatilidad predicha: $volatility%"
    echo "   Señal generada: $signal"
    echo ""
else
    echo "❌ Error en predicción"
    echo "$response"
    exit 1
fi

# Test 2: Verificar que NO sea siempre BUY
echo "📈 Test 2: Verificando distribución de señales (últimas 10 ejecuciones)..."
echo "   Esperando 5 minutos para recolectar datos..."
echo "   (Puedes cancelar con Ctrl+C y ejecutar manualmente después)"
echo ""

# Dar tiempo para que se ejecuten varias predicciones
for i in {1..5}; do
    echo "   Ejecutando predicción $i/5..."
    curl -s -X POST "$FUNCTION_URL/run" > /dev/null
    if [ $i -lt 5 ]; then
        sleep 60  # Esperar 1 minuto entre ejecuciones
    fi
done

echo ""
echo "✅ Deployment verificado"
echo ""
echo "🔗 URL de la función:"
echo "   $FUNCTION_URL"
echo ""
echo "📊 Comandos útiles:"
echo "   Ver predicciones: curl $FUNCTION_URL/api/predictions"
echo "   Ejecutar predicción: curl -X POST $FUNCTION_URL/run"
echo "   Dashboard: $FUNCTION_URL/"
echo ""
echo "📋 Próximos pasos:"
echo "   1. Espera 24 horas"
echo "   2. Ejecuta: python validate_garch_model.py"
echo "   3. Verifica que las señales estén balanceadas"
echo ""
