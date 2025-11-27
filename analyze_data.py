#!/usr/bin/env python3
"""
Script de Metaanálisis para GARCH Trading Bot
==============================================
Extrae y analiza los datos de BigQuery para insights profundos.
"""

import pandas as pd
import json
from google.cloud import bigquery
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

# Configuración
PROJECT_ID = "travel-recomender"
DATASET_ID = "trading_bot"
TABLE_ID = "garch_predictions"

def fetch_data():
    """Extrae todos los datos de BigQuery"""
    client = bigquery.Client(project=PROJECT_ID)
    
    query = f"""
    SELECT 
        timestamp,
        asset,
        current_price,
        predicted_volatility,
        signal,
        model_params
    FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
    ORDER BY timestamp ASC
    """
    
    df = client.query(query).to_dataframe()
    
    # Parsear model_params JSON
    df['model_params_parsed'] = df['model_params'].apply(json.loads)
    
    # Extraer parámetros individuales
    df['p'] = df['model_params_parsed'].apply(lambda x: x.get('p', 1))
    df['q'] = df['model_params_parsed'].apply(lambda x: x.get('q', 1))
    df['omega'] = df['model_params_parsed'].apply(lambda x: x.get('omega', 0))
    df['alpha'] = df['model_params_parsed'].apply(lambda x: x.get('alpha', 0))
    df['beta'] = df['model_params_parsed'].apply(lambda x: x.get('beta', 0))
    df['aic'] = df['model_params_parsed'].apply(lambda x: x.get('aic', 0))
    df['bic'] = df['model_params_parsed'].apply(lambda x: x.get('bic', 0))
    
    return df

def analyze_signals(df):
    """Análisis de señales de trading"""
    print("\n" + "="*60)
    print("📊 ANÁLISIS DE SEÑALES")
    print("="*60)
    
    signal_counts = df['signal'].value_counts()
    print(f"\nDistribución de Señales:")
    for signal, count in signal_counts.items():
        pct = (count / len(df)) * 100
        print(f"  {signal}: {count} ({pct:.1f}%)")
    
    # Señales por rango de volatilidad
    print(f"\n📈 Señales por Rango de Volatilidad:")
    df['vol_range'] = pd.cut(df['predicted_volatility'], 
                              bins=[0, 1.5, 3.0, 100], 
                              labels=['Baja (<1.5%)', 'Media (1.5-3%)', 'Alta (>3%)'])
    
    signal_by_vol = pd.crosstab(df['vol_range'], df['signal'], normalize='index') * 100
    print(signal_by_vol.round(1))

def analyze_volatility(df):
    """Análisis de volatilidad predicha"""
    print("\n" + "="*60)
    print("📉 ANÁLISIS DE VOLATILIDAD")
    print("="*60)
    
    print(f"\nEstadísticas de Volatilidad Predicha:")
    print(f"  Media: {df['predicted_volatility'].mean():.4f}%")
    print(f"  Mediana: {df['predicted_volatility'].median():.4f}%")
    print(f"  Desv. Estándar: {df['predicted_volatility'].std():.4f}%")
    print(f"  Mínimo: {df['predicted_volatility'].min():.4f}%")
    print(f"  Máximo: {df['predicted_volatility'].max():.4f}%")
    
    # Volatilidad en el tiempo
    df['hour'] = df['timestamp'].dt.hour
    vol_by_hour = df.groupby('hour')['predicted_volatility'].agg(['mean', 'std'])
    print(f"\n⏰ Volatilidad Promedio por Hora del Día:")
    print(vol_by_hour.round(4))

def analyze_price_movements(df):
    """Análisis de movimientos de precio"""
    print("\n" + "="*60)
    print("💰 ANÁLISIS DE PRECIO BTC")
    print("="*60)
    
    print(f"\nEstadísticas de Precio:")
    print(f"  Precio Inicial: ${df['current_price'].iloc[0]:,.2f}")
    print(f"  Precio Final: ${df['current_price'].iloc[-1]:,.2f}")
    print(f"  Cambio Total: ${df['current_price'].iloc[-1] - df['current_price'].iloc[0]:,.2f}")
    print(f"  Cambio %: {((df['current_price'].iloc[-1] / df['current_price'].iloc[0]) - 1) * 100:.2f}%")
    
    # Calcular retornos
    df['return'] = df['current_price'].pct_change() * 100
    
    print(f"\n📊 Estadísticas de Retornos (%):")
    print(f"  Media: {df['return'].mean():.4f}%")
    print(f"  Mediana: {df['return'].median():.4f}%")
    print(f"  Volatilidad Realizada: {df['return'].std():.4f}%")

def analyze_model_performance(df):
    """Análisis de rendimiento del modelo GARCH"""
    print("\n" + "="*60)
    print("🤖 ANÁLISIS DE MODELO GARCH")
    print("="*60)
    
    print(f"\nParámetros GARCH Promedio:")
    print(f"  p (lags GARCH): {df['p'].mean():.2f}")
    print(f"  q (lags ARCH): {df['q'].mean():.2f}")
    print(f"  ω (omega): {df['omega'].mean():.6f}")
    print(f"  α (alpha): {df['alpha'].mean():.6f}")
    print(f"  β (beta): {df['beta'].mean():.6f}")
    
    # Persistencia de volatilidad
    persistence = df['alpha'] + df['beta']
    print(f"\n📌 Persistencia de Volatilidad (α + β):")
    print(f"  Media: {persistence.mean():.4f}")
    print(f"  Interpretación: {'Alta persistencia (shocks duraderos)' if persistence.mean() > 0.9 else 'Baja persistencia (shocks temporales)'}")
    
    # Calidad del ajuste
    print(f"\n🎯 Calidad de Ajuste:")
    print(f"  AIC Promedio: {df['aic'].mean():.2f}")
    print(f"  BIC Promedio: {df['bic'].mean():.2f}")

def export_to_csv(df):
    """Exporta datos a CSV para análisis externo"""
    filename = f"garch_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(filename, index=False)
    print(f"\n✅ Datos exportados a: {filename}")
    return filename

def main():
    print("🚀 Iniciando Metaanálisis del GARCH Trading Bot...")
    print(f"⏰ Fecha/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Extraer datos
    print("\n📥 Extrayendo datos de BigQuery...")
    df = fetch_data()
    print(f"✅ {len(df)} registros extraídos")
    
    # Análisis
    analyze_signals(df)
    analyze_volatility(df)
    analyze_price_movements(df)
    analyze_model_performance(df)
    
    # Exportar
    csv_file = export_to_csv(df)
    
    print("\n" + "="*60)
    print("✅ METAANÁLISIS COMPLETADO")
    print("="*60)
    print(f"\n💡 Próximos pasos:")
    print(f"  1. Revisar el archivo CSV: {csv_file}")
    print(f"  2. Crear visualizaciones con pandas/matplotlib")
    print(f"  3. Comparar volatilidad predicha vs realizada")
    print(f"  4. Evaluar performance del portfolio backtest")

if __name__ == "__main__":
    main()
