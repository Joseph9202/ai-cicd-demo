#!/bin/bash
# Script simple para consultar datos de BigQuery

echo "📊 Consultas Rápidas para GARCH Trading Bot"
echo "==========================================="
echo ""

# Contar total de registros
echo "1️⃣ Total de predicciones:"
bq query --use_legacy_sql=false --format=pretty \
  'SELECT COUNT(*) as total FROM `travel-recomender.trading_bot.garch_predictions`'

echo ""
echo "2️⃣ Últimas 5 predicciones:"
bq query --use_legacy_sql=false --format=pretty \
  'SELECT timestamp, current_price, predicted_volatility, signal 
   FROM `travel-recomender.trading_bot.garch_predictions` 
   ORDER BY timestamp DESC LIMIT 5'

echo ""
echo "3️⃣ Distribución de señales:"
bq query --use_legacy_sql=false --format=pretty \
  'SELECT signal, COUNT(*) as count 
   FROM `travel-recomender.trading_bot.garch_predictions` 
   GROUP BY signal ORDER BY count DESC'

echo ""
echo "4️⃣ Estadísticas de volatilidad:"
bq query --use_legacy_sql=false --format=pretty \
  'SELECT 
     MIN(predicted_volatility) as min_vol,
     AVG(predicted_volatility) as avg_vol,
     MAX(predicted_volatility) as max_vol
   FROM `travel-recomender.trading_bot.garch_predictions`'

echo ""
echo "✅ Para exportar a CSV, ejecuta:"
echo "   bq extract --destination_format CSV travel-recomender:trading_bot.garch_predictions gs://tu-bucket/data.csv"
