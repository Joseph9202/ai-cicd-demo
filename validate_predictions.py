#!/usr/bin/env python3
"""
Sistema de Validación de Predicciones
Compara las predicciones de tu bot contra datos reales de Binance
"""

import json
import os
from datetime import datetime, timedelta
from binance.client import Client
from binance.exceptions import BinanceAPIException
import pandas as pd
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class PredictionValidator:
    def __init__(self, testnet=True):
        """Inicializar validador de predicciones"""
        self.client = Client("", "", testnet=testnet)
        self.predictions_file = "predictions_log.json"
        self.results_file = "validation_results.json"

    def log_prediction(self, symbol, prediction_type, predicted_value,
                      timeframe_hours=24, context=None):
        """
        Registrar una predicción para validar después

        Args:
            symbol: Par de trading (ej: BTCUSDT)
            prediction_type: Tipo de predicción (price_up, price_down, price_target, etc)
            predicted_value: Valor predicho (precio, porcentaje, etc)
            timeframe_hours: Horas para validar la predicción
            context: Información adicional (estrategia, confianza, etc)
        """

        # Obtener precio actual
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            current_price = float(ticker['price'])
        except Exception as e:
            print(f"{Colors.RED}❌ Error obteniendo precio: {e}{Colors.RESET}")
            return None

        prediction = {
            'id': datetime.now().strftime('%Y%m%d_%H%M%S_%f'),
            'symbol': symbol,
            'prediction_type': prediction_type,
            'predicted_value': predicted_value,
            'current_price': current_price,
            'prediction_time': datetime.now().isoformat(),
            'validation_time': (datetime.now() + timedelta(hours=timeframe_hours)).isoformat(),
            'timeframe_hours': timeframe_hours,
            'context': context or {},
            'validated': False,
            'result': None
        }

        # Cargar predicciones existentes
        predictions = self._load_predictions()
        predictions.append(prediction)

        # Guardar
        with open(self.predictions_file, 'w') as f:
            json.dump(predictions, f, indent=2)

        print(f"{Colors.GREEN}✅ Predicción registrada:{Colors.RESET}")
        print(f"   ID: {prediction['id']}")
        print(f"   {symbol}: {prediction_type}")
        print(f"   Predicción: {predicted_value}")
        print(f"   Precio actual: ${current_price:,.2f}")
        print(f"   Validar en: {timeframe_hours}h")

        return prediction['id']

    def validate_predictions(self):
        """Validar predicciones que ya cumplieron su timeframe"""

        predictions = self._load_predictions()
        now = datetime.now()
        validated_count = 0

        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}🔍 VALIDANDO PREDICCIONES{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")

        for pred in predictions:
            if pred['validated']:
                continue

            validation_time = datetime.fromisoformat(pred['validation_time'])

            if now >= validation_time:
                # Es hora de validar
                result = self._validate_single_prediction(pred)
                pred['validated'] = True
                pred['result'] = result
                validated_count += 1

        # Guardar resultados actualizados
        with open(self.predictions_file, 'w') as f:
            json.dump(predictions, f, indent=2)

        # Guardar resumen de resultados
        self._save_validation_summary(predictions)

        print(f"\n{Colors.CYAN}📊 Predicciones validadas: {validated_count}{Colors.RESET}\n")

        return validated_count

    def _validate_single_prediction(self, pred):
        """Validar una predicción individual"""

        symbol = pred['symbol']
        pred_type = pred['prediction_type']
        predicted_value = pred['predicted_value']
        initial_price = pred['current_price']

        print(f"{Colors.BLUE}🔍 Validando: {pred['id']}{Colors.RESET}")
        print(f"   Símbolo: {symbol}")
        print(f"   Tipo: {pred_type}")
        print(f"   Predicción: {predicted_value}")
        print(f"   Precio inicial: ${initial_price:,.2f}")

        try:
            # Obtener precio actual
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            current_price = float(ticker['price'])

            # Calcular cambio real
            price_change_pct = ((current_price - initial_price) / initial_price) * 100

            print(f"   Precio actual: ${current_price:,.2f}")
            print(f"   Cambio real: {price_change_pct:+.2f}%")

            # Validar según el tipo de predicción
            result = {
                'actual_price': current_price,
                'price_change_pct': price_change_pct,
                'validation_time': datetime.now().isoformat(),
                'success': False,
                'accuracy': 0.0,
                'error': 0.0
            }

            if pred_type == 'price_up':
                # Predicción: precio subirá
                result['success'] = price_change_pct > 0
                result['accuracy'] = max(0, min(100, price_change_pct * 10))  # Escala 0-100

            elif pred_type == 'price_down':
                # Predicción: precio bajará
                result['success'] = price_change_pct < 0
                result['accuracy'] = max(0, min(100, abs(price_change_pct) * 10))

            elif pred_type == 'price_target':
                # Predicción: precio alcanzará valor específico
                target = float(predicted_value)
                error_pct = abs((current_price - target) / target) * 100
                result['error'] = error_pct
                result['success'] = error_pct < 5  # Éxito si error < 5%
                result['accuracy'] = max(0, 100 - error_pct)

            elif pred_type == 'price_range':
                # Predicción: precio estará en rango
                min_price, max_price = predicted_value
                result['success'] = min_price <= current_price <= max_price
                result['accuracy'] = 100 if result['success'] else 0

            elif pred_type == 'change_percentage':
                # Predicción: cambio de porcentaje específico
                predicted_pct = float(predicted_value)
                error_pct = abs(price_change_pct - predicted_pct)
                result['error'] = error_pct
                result['success'] = error_pct < 2  # Éxito si error < 2%
                result['accuracy'] = max(0, 100 - (error_pct * 10))

            # Mostrar resultado
            if result['success']:
                print(f"   {Colors.GREEN}✅ PREDICCIÓN CORRECTA{Colors.RESET}")
                print(f"   Accuracy: {result['accuracy']:.1f}%")
            else:
                print(f"   {Colors.RED}❌ PREDICCIÓN INCORRECTA{Colors.RESET}")
                if result['error'] > 0:
                    print(f"   Error: {result['error']:.2f}%")

            print()
            return result

        except Exception as e:
            print(f"   {Colors.RED}❌ Error validando: {e}{Colors.RESET}\n")
            return {
                'error': str(e),
                'success': False,
                'accuracy': 0.0
            }

    def get_statistics(self):
        """Obtener estadísticas de accuracy del bot"""

        predictions = self._load_predictions()
        validated = [p for p in predictions if p['validated']]

        if not validated:
            print(f"{Colors.YELLOW}⚠️  No hay predicciones validadas aún{Colors.RESET}")
            return None

        # Calcular estadísticas
        total = len(validated)
        successful = len([p for p in validated if p['result']['success']])
        failed = total - successful

        success_rate = (successful / total) * 100
        avg_accuracy = sum(p['result']['accuracy'] for p in validated) / total

        # Estadísticas por tipo
        by_type = {}
        for pred in validated:
            pred_type = pred['prediction_type']
            if pred_type not in by_type:
                by_type[pred_type] = {'total': 0, 'successful': 0}
            by_type[pred_type]['total'] += 1
            if pred['result']['success']:
                by_type[pred_type]['successful'] += 1

        # Estadísticas por símbolo
        by_symbol = {}
        for pred in validated:
            symbol = pred['symbol']
            if symbol not in by_symbol:
                by_symbol[symbol] = {'total': 0, 'successful': 0}
            by_symbol[symbol]['total'] += 1
            if pred['result']['success']:
                by_symbol[symbol]['successful'] += 1

        stats = {
            'total_predictions': total,
            'successful': successful,
            'failed': failed,
            'success_rate': success_rate,
            'average_accuracy': avg_accuracy,
            'by_type': by_type,
            'by_symbol': by_symbol,
            'last_updated': datetime.now().isoformat()
        }

        return stats

    def print_statistics(self):
        """Imprimir estadísticas de forma visual"""

        stats = self.get_statistics()

        if not stats:
            return

        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}📊 ESTADÍSTICAS DE PREDICCIONES{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")

        # Resumen general
        print(f"{Colors.CYAN}📈 RESUMEN GENERAL:{Colors.RESET}\n")
        print(f"   Total de predicciones validadas: {stats['total_predictions']}")
        print(f"   {Colors.GREEN}✅ Exitosas: {stats['successful']}{Colors.RESET}")
        print(f"   {Colors.RED}❌ Fallidas: {stats['failed']}{Colors.RESET}")
        print(f"   {Colors.BOLD}Tasa de éxito: {stats['success_rate']:.1f}%{Colors.RESET}")
        print(f"   Accuracy promedio: {stats['average_accuracy']:.1f}%\n")

        # Barra de progreso
        bar_length = 50
        filled = int(bar_length * stats['success_rate'] / 100)
        bar = '█' * filled + '░' * (bar_length - filled)

        color = Colors.GREEN if stats['success_rate'] >= 70 else Colors.YELLOW if stats['success_rate'] >= 50 else Colors.RED
        print(f"   {color}{bar}{Colors.RESET} {stats['success_rate']:.1f}%\n")

        # Por tipo de predicción
        if stats['by_type']:
            print(f"{Colors.CYAN}📋 POR TIPO DE PREDICCIÓN:{Colors.RESET}\n")
            for pred_type, data in stats['by_type'].items():
                success_rate = (data['successful'] / data['total']) * 100
                print(f"   {pred_type}:")
                print(f"      {data['successful']}/{data['total']} exitosas ({success_rate:.1f}%)")
            print()

        # Por símbolo
        if stats['by_symbol']:
            print(f"{Colors.CYAN}💱 POR SÍMBOLO:{Colors.RESET}\n")
            for symbol, data in stats['by_symbol'].items():
                success_rate = (data['successful'] / data['total']) * 100
                print(f"   {symbol}:")
                print(f"      {data['successful']}/{data['total']} exitosas ({success_rate:.1f}%)")
            print()

        # Evaluación
        print(f"{Colors.CYAN}🎯 EVALUACIÓN:{Colors.RESET}\n")
        if stats['success_rate'] >= 70:
            print(f"   {Colors.GREEN}🌟 EXCELENTE - Tu bot tiene muy buenas predicciones{Colors.RESET}")
        elif stats['success_rate'] >= 50:
            print(f"   {Colors.YELLOW}⚠️  ACEPTABLE - Hay margen de mejora{Colors.RESET}")
        else:
            print(f"   {Colors.RED}❌ POBRE - Considera revisar tu estrategia{Colors.RESET}")
        print()

    def _load_predictions(self):
        """Cargar predicciones del archivo"""
        if not os.path.exists(self.predictions_file):
            return []
        try:
            with open(self.predictions_file, 'r') as f:
                return json.load(f)
        except:
            return []

    def _save_validation_summary(self, predictions):
        """Guardar resumen de validaciones"""
        stats = self.get_statistics()
        if stats:
            with open(self.results_file, 'w') as f:
                json.dump(stats, f, indent=2)


def example_usage():
    """Ejemplo de uso del validador"""

    validator = PredictionValidator(testnet=True)

    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}🤖 SISTEMA DE VALIDACIÓN DE PREDICCIONES{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")

    print(f"{Colors.CYAN}Este sistema te permite:{Colors.RESET}\n")
    print(f"  1. Registrar predicciones de tu bot")
    print(f"  2. Validarlas automáticamente contra datos reales")
    print(f"  3. Obtener estadísticas de accuracy")
    print(f"  4. Mejorar tu bot basándote en resultados\n")

    print(f"{Colors.YELLOW}Ejemplo de uso:{Colors.RESET}\n")

    # Ejemplo: Registrar predicción
    print(f"{Colors.CYAN}# Registrar una predicción:{Colors.RESET}")
    print(f"validator.log_prediction(")
    print(f"    symbol='BTCUSDT',")
    print(f"    prediction_type='price_up',  # precio subirá")
    print(f"    predicted_value='alcista',")
    print(f"    timeframe_hours=24,  # validar en 24 horas")
    print(f"    context={{'strategy': 'IA Gemini', 'confidence': 0.85}}")
    print(f")\n")

    # Registrar ejemplo real
    prediction_id = validator.log_prediction(
        symbol='BTCUSDT',
        prediction_type='price_up',
        predicted_value='alcista',
        timeframe_hours=1,  # 1 hora para demo rápida
        context={'strategy': 'Análisis técnico', 'confidence': 0.75}
    )

    print(f"\n{Colors.CYAN}# Validar predicciones después del timeframe:{Colors.RESET}")
    print(f"validator.validate_predictions()\n")

    print(f"\n{Colors.CYAN}# Ver estadísticas:{Colors.RESET}")
    print(f"validator.print_statistics()\n")


if __name__ == "__main__":
    example_usage()
