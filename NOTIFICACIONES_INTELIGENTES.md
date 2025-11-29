# 🔔 Sistema de Notificaciones Inteligentes

## 📋 Resumen de Cambios

Se modificó el sistema de notificaciones para enviar alertas a Telegram **SOLO cuando la señal cambie a BUY**, mientras que los reportes se siguen guardando en la base de datos vectorial cada hora.

---

## ⚡ Comportamiento Anterior

**Antes:**
- ❌ Enviaba reporte a Telegram cada hora (muy molesto)
- ❌ Mucho ruido, pocas señales accionables
- ✅ Guardaba en base de datos vectorial

```
Cada hora:
  ├── Genera reporte IA
  ├── Guarda en vector DB
  └── 📱 ENVÍA A TELEGRAM (SIEMPRE)
```

---

## ✨ Comportamiento Nuevo

**Ahora:**
- ✅ Guarda reporte en vector DB cada hora (sin cambios)
- ✅ Solo notifica a Telegram cuando la señal **cambia a BUY**
- ✅ Menos ruido, más señales accionables

```
Cada hora:
  ├── Genera reporte IA
  ├── Guarda en vector DB (SIEMPRE)
  ├── Compara señal actual vs anterior
  └── ¿Cambió a BUY?
      ├── SÍ → 📱 ENVÍA A TELEGRAM + WhatsApp
      └── NO → ℹ️  Solo guarda (sin notificar)
```

---

## 🔧 Implementación Técnica

### Lógica de Detección de Cambio

La función `/report` ahora:

1. **Genera reporte** con Gemini AI
2. **Guarda SIEMPRE** en vector DB + PDF
3. **Consulta BigQuery** para obtener las últimas 2 señales
4. **Compara señales:**
   ```python
   previous_signal = results[1].signal  # Señal anterior
   current_signal = metadata['signal']  # Señal actual

   should_notify = (current_signal == 'BUY' and previous_signal != 'BUY')
   ```
5. **Notifica SOLO si** `should_notify == True`

### Código Modificado

**Archivo:** [main.py:613](main.py:613)

```python
@app.route('/report', methods=['POST', 'GET'])
def send_ai_report():
    """
    IMPORTANT: Only sends to Telegram when signal changes to BUY
    Always saves to vector database regardless of signal
    """

    # 1. Generate report
    report_text, metadata = generate_ai_report()

    # 2. ALWAYS save to vector DB (no conditions)
    result = save_report_with_pdf(report_text, metadata)

    # 3. Get previous signal from BigQuery
    query = f"""
    SELECT signal
    FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
    ORDER BY timestamp DESC
    LIMIT 2
    """
    results = list(client.query(query).result())
    previous_signal = results[1].signal if len(results) > 1 else None

    # 4. Compare signals
    current_signal = metadata.get('signal', '')
    should_notify = (current_signal == 'BUY' and previous_signal != 'BUY')

    # 5. ONLY notify if signal changed to BUY
    if should_notify:
        send_telegram_alert(report_text)
        # Send PDF with special caption
        send_pdf_with_caption('🟢 SEÑAL DE COMPRA DETECTADA')
    else:
        print(f"ℹ️  Signal is {current_signal}. Report saved but not sent.")
```

---

## 📊 Escenarios de Notificación

### Escenario 1: Cambio a BUY ✅
```
Hora 1: HOLD → Guarda en DB, no notifica
Hora 2: HOLD → Guarda en DB, no notifica
Hora 3: BUY  → 🚨 GUARDA EN DB + NOTIFICA A TELEGRAM
```

### Escenario 2: Mantiene BUY ❌
```
Hora 1: BUY  → 🚨 GUARDA EN DB + NOTIFICA
Hora 2: BUY  → Guarda en DB, no notifica (ya era BUY)
Hora 3: BUY  → Guarda en DB, no notifica
```

### Escenario 3: Cambio a SELL ❌
```
Hora 1: BUY  → Guarda en DB, no notifica
Hora 2: SELL → Guarda en DB, no notifica (no es cambio a BUY)
Hora 3: HOLD → Guarda en DB, no notifica
```

### Escenario 4: De SELL a BUY ✅
```
Hora 1: SELL → Guarda en DB, no notifica
Hora 2: HOLD → Guarda en DB, no notifica
Hora 3: BUY  → 🚨 GUARDA EN DB + NOTIFICA A TELEGRAM
```

---

## 🎯 Beneficios

### Para el Usuario:
- ✅ **Menos spam:** Solo recibes notificaciones cuando hay una oportunidad de compra
- ✅ **Señales accionables:** Cada notificación es importante
- ✅ **Histórico completo:** Todos los reportes siguen guardándose en la base de datos

### Para el Sistema:
- ✅ **Eficiencia:** Menos llamadas a API de Telegram
- ✅ **Integridad de datos:** Vector DB sigue teniendo todos los reportes
- ✅ **Logs claros:** Indica explícitamente por qué no se notificó

---

## 📱 Formato de Notificación

### Cuando SE notifica (señal cambió a BUY):

**Mensaje de Telegram:**
```
🟢 SEÑAL DE COMPRA DETECTADA

📊 REPORTE HORARIO - GARCH Trading Bot
⏰ 2025-11-29 01:00 UTC

[Análisis completo de Gemini AI...]

---
Análisis generado por Gemini AI • Datos: últimas 24h
```

**PDF adjunto:**
- Nombre: `reporte_BUY_2025-11-29_01-00-00.pdf`
- Caption: `🟢 SEÑAL DE COMPRA DETECTADA - Reporte completo`

### Cuando NO se notifica:

**Logs del sistema:**
```
✅ Report saved to vector DB and PDF
📊 Signal comparison: Previous=HOLD, Current=HOLD
ℹ️  Signal is HOLD (no change to BUY). Report saved but not sent to Telegram.
```

---

## 🔍 Testing

### Test 1: Simular cambio a BUY
```bash
# Ejecutar reporte manualmente
curl -X POST "https://garch-trading-bot-l4qey4f4sq-ue.a.run.app/report"

# Response esperado (si cambió a BUY):
{
  "status": "success",
  "message": "Report saved to DB. Notification sent (BUY signal)",
  "signal": "BUY",
  "previous_signal": "HOLD",
  "notified": true
}
```

### Test 2: Sin cambio a BUY
```bash
# Ejecutar reporte cuando señal NO es BUY
curl -X POST "https://garch-trading-bot-l4qey4f4sq-ue.a.run.app/report"

# Response esperado:
{
  "status": "success",
  "message": "Report saved to DB. No notification (not a BUY signal)",
  "signal": "HOLD",
  "previous_signal": "HOLD",
  "notified": false
}
```

---

## 📊 Monitoreo

### Verificar en BigQuery:
```sql
-- Ver últimas 10 señales
SELECT
  timestamp,
  asset,
  signal,
  current_price,
  predicted_volatility
FROM `travel-recomender.trading_bot.garch_predictions`
ORDER BY timestamp DESC
LIMIT 10;
```

### Logs en Cloud Functions:
```
✅ Report saved to vector DB and PDF
📊 Signal comparison: Previous=HOLD, Current=BUY
🚨 SIGNAL CHANGED TO BUY! Sending notification to Telegram...
✅ PDF sent to Telegram
```

---

## 🚀 Deployment

**Desplegado exitosamente:**
- URL: https://garch-trading-bot-l4qey4f4sq-ue.a.run.app
- Revision: `garch-trading-bot-00024-nop`
- Deploy time: 2025-11-29 01:03 UTC

---

## 🔮 Mejoras Futuras Sugeridas

1. **Notificar también en cambio a SELL**
   - Útil para alertas de venta
   - Configuración: `NOTIFY_ON_SELL=true`

2. **Cooldown period**
   - Evitar múltiples notificaciones en poco tiempo
   - Ejemplo: No notificar si ya notificó en última hora

3. **Resumen diario**
   - Una vez al día, enviar resumen de todas las señales
   - Aunque no haya cambiado a BUY

4. **Configuración por usuario**
   - Telegram command: `/config notify_on buy,sell`
   - Cada usuario elige qué señales quiere recibir

---

## ✅ Checklist de Cambios

- [x] Modificar función `/report` para comparar señales
- [x] Consultar BigQuery para obtener señal anterior
- [x] Lógica condicional de notificación
- [x] Mantener guardado en vector DB (sin cambios)
- [x] Logs informativos de decisión
- [x] Desplegar a Cloud Functions
- [x] Documentar comportamiento

---

## 📞 Comandos Telegram

Los comandos de Telegram **siguen funcionando igual:**

- `/reporte` - Genera y envía reporte AI inmediatamente (sin importar señal)
- `/pdf` - Envía último reporte como PDF
- `/analisis [query]` - Busca en reportes históricos
- `/stats` - Estadísticas del bot
- `/ayuda` - Lista de comandos

---

## 🎉 Resultado Final

El sistema ahora es mucho más inteligente:
- **Guardas todo** en la base de datos (histórico completo)
- **Notificas solo lo importante** (cambios a BUY)
- **Reduces ruido** (no más notificaciones cada hora)
- **Mantienes opciones** (comandos manuales siguen disponibles)

¡Notificaciones inteligentes activadas! 🚀
