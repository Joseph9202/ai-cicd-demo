#!/usr/bin/env python3
"""
Sistema de Trading Automatizado
Compra y vende basándose en predicciones y señales
"""

import os
from dotenv import load_dotenv
from binance.client import Client
from binance.exceptions import BinanceAPIException
import json
from datetime import datetime
import time

load_dotenv()

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class AutoTrader:
    def __init__(self, api_key=None, secret_key=None, testnet=True):
        """
        Inicializar trading automatizado

        Args:
            api_key: Binance API Key (opcional, usa .env si no se proporciona)
            secret_key: Binance Secret Key (opcional, usa .env si no se proporciona)
            testnet: Si True, usa testnet; si False, usa producción (PELIGRO!)
        """

        # Validación de seguridad
        if not testnet:
            confirm = input(f"{Colors.RED}⚠️  PELIGRO: ¿Estás seguro de usar API REAL? (escribe 'SI CONFIRMO'): {Colors.RESET}")
            if confirm != "SI CONFIRMO":
                print(f"{Colors.YELLOW}Abortado por seguridad. Usando testnet.{Colors.RESET}")
                testnet = True

        self.testnet = testnet
        self.api_key = api_key or os.getenv('BINANCE_API_KEY')
        self.secret_key = secret_key or os.getenv('BINANCE_SECRET_KEY')

        if not self.api_key or not self.secret_key:
            raise ValueError("API keys no encontradas. Configura tu archivo .env")

        self.client = Client(
            self.api_key,
            self.secret_key,
            testnet=self.testnet
        )

        self.trades_log = "trades_history.json"

    def get_balance(self, asset):
        """Obtener balance disponible de un asset"""
        try:
            account = self.client.get_account()
            for balance in account['balances']:
                if balance['asset'] == asset:
                    return float(balance['free'])
            return 0.0
        except BinanceAPIException as e:
            print(f"{Colors.RED}❌ Error obteniendo balance: {e.message}{Colors.RESET}")
            return None

    def get_current_price(self, symbol):
        """Obtener precio actual de un símbolo"""
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except Exception as e:
            print(f"{Colors.RED}❌ Error obteniendo precio: {e}{Colors.RESET}")
            return None

    def buy_market(self, symbol, amount_usdt=None, quantity=None):
        """
        Comprar a precio de mercado

        Args:
            symbol: Par de trading (ej: BTCUSDT)
            amount_usdt: Cantidad en USDT a gastar (exclusivo con quantity)
            quantity: Cantidad exacta a comprar (exclusivo con amount_usdt)

        Returns:
            Order object si exitoso, None si falla
        """

        print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.GREEN}🛒 ORDEN DE COMPRA{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*60}{Colors.RESET}\n")

        try:
            # Obtener precio actual
            current_price = self.get_current_price(symbol)
            if not current_price:
                return None

            # Calcular cantidad
            if amount_usdt and not quantity:
                quantity = amount_usdt / current_price
            elif not amount_usdt and not quantity:
                print(f"{Colors.RED}❌ Debes especificar amount_usdt o quantity{Colors.RESET}")
                return None

            # Obtener info del símbolo para validar
            symbol_info = self.client.get_symbol_info(symbol)

            # Ajustar cantidad a step size
            lot_filter = next(f for f in symbol_info['filters'] if f['filterType'] == 'LOT_SIZE')
            step_size = float(lot_filter['stepSize'])
            quantity = round(quantity / step_size) * step_size

            # Validar cantidad mínima
            min_qty = float(lot_filter['minQty'])
            if quantity < min_qty:
                print(f"{Colors.RED}❌ Cantidad {quantity} menor que mínimo {min_qty}{Colors.RESET}")
                return None

            print(f"{Colors.BLUE}📊 Detalles de la orden:{Colors.RESET}")
            print(f"   Símbolo: {symbol}")
            print(f"   Precio actual: ${current_price:,.2f}")
            print(f"   Cantidad: {quantity:.8f}")
            print(f"   Valor total: ${quantity * current_price:.2f}")
            print()

            # Confirmar
            confirm = input(f"{Colors.YELLOW}¿Ejecutar compra? (s/n): {Colors.RESET}").lower()
            if confirm not in ['s', 'si', 'y', 'yes']:
                print(f"{Colors.YELLOW}⚠️  Compra cancelada{Colors.RESET}")
                return None

            # Ejecutar orden
            print(f"{Colors.BLUE}🔄 Ejecutando orden...{Colors.RESET}")

            order = self.client.order_market_buy(
                symbol=symbol,
                quantity=quantity
            )

            # Log de la operación
            self._log_trade(order, 'BUY')

            # Mostrar resultado
            print(f"\n{Colors.GREEN}✅ COMPRA EXITOSA{Colors.RESET}")
            print(f"   Order ID: {order['orderId']}")
            print(f"   Status: {order['status']}")
            print(f"   Cantidad ejecutada: {order['executedQty']}")

            if 'fills' in order and order['fills']:
                avg_price = sum(float(f['price']) * float(f['qty']) for f in order['fills']) / float(order['executedQty'])
                print(f"   Precio promedio: ${avg_price:,.2f}")

                total_commission = sum(float(f['commission']) for f in order['fills'])
                commission_asset = order['fills'][0]['commissionAsset']
                print(f"   Comisión: {total_commission} {commission_asset}")

            print()
            return order

        except BinanceAPIException as e:
            print(f"{Colors.RED}❌ Error en compra: {e.message}{Colors.RESET}")
            print(f"   Código: {e.code}")
            return None
        except Exception as e:
            print(f"{Colors.RED}❌ Error inesperado: {e}{Colors.RESET}")
            return None

    def sell_market(self, symbol, quantity=None, sell_all=False):
        """
        Vender a precio de mercado

        Args:
            symbol: Par de trading (ej: BTCUSDT)
            quantity: Cantidad a vender
            sell_all: Si True, vende todo el balance disponible

        Returns:
            Order object si exitoso, None si falla
        """

        print(f"\n{Colors.CYAN}{'='*60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.RED}💰 ORDEN DE VENTA{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*60}{Colors.RESET}\n")

        try:
            # Obtener precio actual
            current_price = self.get_current_price(symbol)
            if not current_price:
                return None

            # Si sell_all, obtener balance
            if sell_all:
                base_asset = symbol.replace('USDT', '').replace('BUSD', '')
                quantity = self.get_balance(base_asset)
                if not quantity or quantity == 0:
                    print(f"{Colors.RED}❌ No tienes {base_asset} para vender{Colors.RESET}")
                    return None

            if not quantity:
                print(f"{Colors.RED}❌ Debes especificar quantity o sell_all=True{Colors.RESET}")
                return None

            # Obtener info del símbolo
            symbol_info = self.client.get_symbol_info(symbol)

            # Ajustar cantidad a step size
            lot_filter = next(f for f in symbol_info['filters'] if f['filterType'] == 'LOT_SIZE')
            step_size = float(lot_filter['stepSize'])
            quantity = round(quantity / step_size) * step_size

            # Validar cantidad mínima
            min_qty = float(lot_filter['minQty'])
            if quantity < min_qty:
                print(f"{Colors.RED}❌ Cantidad {quantity} menor que mínimo {min_qty}{Colors.RESET}")
                return None

            print(f"{Colors.BLUE}📊 Detalles de la orden:{Colors.RESET}")
            print(f"   Símbolo: {symbol}")
            print(f"   Precio actual: ${current_price:,.2f}")
            print(f"   Cantidad: {quantity:.8f}")
            print(f"   Valor total: ${quantity * current_price:.2f}")
            print()

            # Confirmar
            confirm = input(f"{Colors.YELLOW}¿Ejecutar venta? (s/n): {Colors.RESET}").lower()
            if confirm not in ['s', 'si', 'y', 'yes']:
                print(f"{Colors.YELLOW}⚠️  Venta cancelada{Colors.RESET}")
                return None

            # Ejecutar orden
            print(f"{Colors.BLUE}🔄 Ejecutando orden...{Colors.RESET}")

            order = self.client.order_market_sell(
                symbol=symbol,
                quantity=quantity
            )

            # Log de la operación
            self._log_trade(order, 'SELL')

            # Mostrar resultado
            print(f"\n{Colors.GREEN}✅ VENTA EXITOSA{Colors.RESET}")
            print(f"   Order ID: {order['orderId']}")
            print(f"   Status: {order['status']}")
            print(f"   Cantidad ejecutada: {order['executedQty']}")

            if 'fills' in order and order['fills']:
                avg_price = sum(float(f['price']) * float(f['qty']) for f in order['fills']) / float(order['executedQty'])
                print(f"   Precio promedio: ${avg_price:,.2f}")

                total_commission = sum(float(f['commission']) for f in order['fills'])
                commission_asset = order['fills'][0]['commissionAsset']
                print(f"   Comisión: {total_commission} {commission_asset}")

            print()
            return order

        except BinanceAPIException as e:
            print(f"{Colors.RED}❌ Error en venta: {e.message}{Colors.RESET}")
            print(f"   Código: {e.code}")
            return None
        except Exception as e:
            print(f"{Colors.RED}❌ Error inesperado: {e}{Colors.RESET}")
            return None

    def buy_limit(self, symbol, price, quantity):
        """Crear orden de compra límite"""
        try:
            order = self.client.order_limit_buy(
                symbol=symbol,
                quantity=quantity,
                price=f"{price:.2f}"
            )
            self._log_trade(order, 'BUY_LIMIT')
            return order
        except BinanceAPIException as e:
            print(f"{Colors.RED}❌ Error: {e.message}{Colors.RESET}")
            return None

    def sell_limit(self, symbol, price, quantity):
        """Crear orden de venta límite"""
        try:
            order = self.client.order_limit_sell(
                symbol=symbol,
                quantity=quantity,
                price=f"{price:.2f}"
            )
            self._log_trade(order, 'SELL_LIMIT')
            return order
        except BinanceAPIException as e:
            print(f"{Colors.RED}❌ Error: {e.message}{Colors.RESET}")
            return None

    def get_open_orders(self, symbol=None):
        """Obtener órdenes abiertas"""
        try:
            if symbol:
                orders = self.client.get_open_orders(symbol=symbol)
            else:
                orders = self.client.get_open_orders()
            return orders
        except Exception as e:
            print(f"{Colors.RED}❌ Error: {e}{Colors.RESET}")
            return []

    def cancel_order(self, symbol, order_id):
        """Cancelar una orden"""
        try:
            result = self.client.cancel_order(symbol=symbol, orderId=order_id)
            print(f"{Colors.GREEN}✅ Orden {order_id} cancelada{Colors.RESET}")
            return result
        except Exception as e:
            print(f"{Colors.RED}❌ Error: {e}{Colors.RESET}")
            return None

    def _log_trade(self, order, side):
        """Registrar trade en historial"""
        trade = {
            'timestamp': datetime.now().isoformat(),
            'order_id': order['orderId'],
            'symbol': order['symbol'],
            'side': side,
            'type': order['type'],
            'status': order['status'],
            'quantity': order['executedQty'],
            'order': order
        }

        # Cargar historial
        history = []
        if os.path.exists(self.trades_log):
            with open(self.trades_log, 'r') as f:
                history = json.load(f)

        history.append(trade)

        # Guardar
        with open(self.trades_log, 'w') as f:
            json.dump(history, f, indent=2)


def interactive_trading():
    """Modo interactivo de trading"""

    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}🤖 TRADING AUTOMATIZADO - BINANCE TESTNET{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")

    try:
        trader = AutoTrader(testnet=True)
        print(f"{Colors.GREEN}✅ Conexión exitosa{Colors.RESET}\n")
    except Exception as e:
        print(f"{Colors.RED}❌ Error de conexión: {e}{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Verifica:{Colors.RESET}")
        print(f"  1. API Keys configuradas en .env")
        print(f"  2. Permisos habilitados en Binance Testnet")
        print(f"  3. Ejecuta: python diagnose_binance.py\n")
        return

    while True:
        print(f"{Colors.CYAN}┌─────────────────────────────────────────┐{Colors.RESET}")
        print(f"{Colors.CYAN}│            MENÚ DE TRADING              │{Colors.RESET}")
        print(f"{Colors.CYAN}└─────────────────────────────────────────┘{Colors.RESET}\n")

        print(f"  {Colors.MAGENTA}1.{Colors.RESET} Ver balances")
        print(f"  {Colors.MAGENTA}2.{Colors.RESET} Ver precio actual")
        print(f"  {Colors.GREEN}3.{Colors.RESET} Comprar (market)")
        print(f"  {Colors.RED}4.{Colors.RESET} Vender (market)")
        print(f"  {Colors.YELLOW}5.{Colors.RESET} Ver órdenes abiertas")
        print(f"  {Colors.BLUE}6.{Colors.RESET} Ver historial de trades")
        print(f"  {Colors.MAGENTA}0.{Colors.RESET} Salir\n")

        choice = input(f"{Colors.CYAN}Tu opción: {Colors.RESET}").strip()

        if choice == '1':
            # Ver balances
            print(f"\n{Colors.BLUE}💰 Balances:{Colors.RESET}")
            for asset in ['BTC', 'ETH', 'BNB', 'USDT']:
                balance = trader.get_balance(asset)
                if balance and balance > 0:
                    print(f"   {asset}: {balance:.8f}")
            print()

        elif choice == '2':
            # Ver precio
            symbol = input(f"{Colors.CYAN}Símbolo (ej: BTCUSDT): {Colors.RESET}").upper()
            price = trader.get_current_price(symbol)
            if price:
                print(f"{Colors.GREEN}   Precio de {symbol}: ${price:,.2f}{Colors.RESET}\n")

        elif choice == '3':
            # Comprar
            symbol = input(f"{Colors.CYAN}Símbolo (ej: BTCUSDT): {Colors.RESET}").upper()
            amount = input(f"{Colors.CYAN}Monto en USDT (ej: 50): {Colors.RESET}")
            try:
                trader.buy_market(symbol, amount_usdt=float(amount))
            except ValueError:
                print(f"{Colors.RED}❌ Monto inválido{Colors.RESET}\n")

        elif choice == '4':
            # Vender
            symbol = input(f"{Colors.CYAN}Símbolo (ej: BTCUSDT): {Colors.RESET}").upper()
            sell_all = input(f"{Colors.CYAN}¿Vender todo? (s/n): {Colors.RESET}").lower()

            if sell_all in ['s', 'si', 'y']:
                trader.sell_market(symbol, sell_all=True)
            else:
                qty = input(f"{Colors.CYAN}Cantidad a vender: {Colors.RESET}")
                try:
                    trader.sell_market(symbol, quantity=float(qty))
                except ValueError:
                    print(f"{Colors.RED}❌ Cantidad inválida{Colors.RESET}\n")

        elif choice == '5':
            # Órdenes abiertas
            orders = trader.get_open_orders()
            if orders:
                print(f"\n{Colors.YELLOW}📋 Órdenes abiertas:{Colors.RESET}")
                for o in orders:
                    print(f"   ID: {o['orderId']} | {o['symbol']} | {o['side']} | {o['price']}")
                print()
            else:
                print(f"{Colors.YELLOW}⚠️  No hay órdenes abiertas{Colors.RESET}\n")

        elif choice == '6':
            # Historial
            if os.path.exists(trader.trades_log):
                with open(trader.trades_log, 'r') as f:
                    history = json.load(f)
                print(f"\n{Colors.BLUE}📜 Historial de trades:{Colors.RESET}")
                for t in history[-10:]:  # Últimos 10
                    print(f"   {t['timestamp']} | {t['side']} | {t['symbol']} | Qty: {t['quantity']}")
                print()
            else:
                print(f"{Colors.YELLOW}⚠️  No hay historial{Colors.RESET}\n")

        elif choice == '0':
            print(f"\n{Colors.GREEN}👋 ¡Hasta luego!{Colors.RESET}\n")
            break

        else:
            print(f"{Colors.RED}❌ Opción inválida{Colors.RESET}\n")


if __name__ == "__main__":
    interactive_trading()
