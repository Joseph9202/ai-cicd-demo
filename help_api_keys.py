#!/usr/bin/env python3
"""
Asistente interactivo para configurar Binance API Keys
"""

import webbrowser
import os
import time

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")

def print_step(number, text):
    print(f"{Colors.BOLD}{Colors.CYAN}[PASO {number}]{Colors.RESET} {text}")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")

def print_option(number, text):
    print(f"{Colors.MAGENTA}{number}.{Colors.RESET} {text}")

def main():
    print_header("🚀 ASISTENTE DE CONFIGURACIÓN BINANCE API")

    print_info("Este asistente te ayudará a obtener tus API Keys de Binance Testnet")
    print_info("con los permisos correctos.\n")

    print_warning("IMPORTANTE: Necesitas tener una cuenta en Binance Testnet")
    print()

    # Paso 1: Elegir testnet
    print_step(1, "¿Qué testnet quieres usar?")
    print()
    print_option(1, "Binance Spot Testnet (tradicional)")
    print_option(2, "Binance Futures Testnet (más fácil, recomendado)")
    print()

    choice = input(f"{Colors.CYAN}Tu elección (1 o 2): {Colors.RESET}").strip()

    if choice == "1":
        # Spot Testnet
        print_success("Has elegido: Binance Spot Testnet\n")

        print_step(2, "Voy a abrir la página de Binance Spot Testnet en tu navegador")
        print()
        input(f"{Colors.YELLOW}Presiona ENTER cuando estés listo...{Colors.RESET}")

        urls = [
            "https://testnet.binance.vision/",
            "https://testnet.binance.vision/userCenter/myApiKeys.html",
            "https://testnet.binance.vision/apiManagement.html"
        ]

        print_info("Abriendo Binance Spot Testnet...\n")
        try:
            webbrowser.open(urls[0])
            time.sleep(2)
        except:
            print_warning("No pude abrir el navegador automáticamente")
            print_info(f"Abre manualmente: {urls[0]}")

        print()
        print_step(3, "Sigue estos pasos en la página web:")
        print()
        print(f"{Colors.CYAN}   1. Login con tu cuenta (email y contraseña){Colors.RESET}")
        print(f"{Colors.CYAN}   2. Click en tu EMAIL (esquina superior derecha){Colors.RESET}")
        print(f"{Colors.CYAN}   3. Selecciona 'API Management' o 'API Keys'{Colors.RESET}")
        print()
        print_info("Si no encuentras 'API Management', intenta estos links directos:\n")
        for url in urls[1:]:
            print(f"   🔗 {url}")
        print()

    elif choice == "2":
        # Futures Testnet
        print_success("Has elegido: Binance Futures Testnet (buena elección!)\n")

        print_step(2, "Voy a abrir la página de Binance Futures Testnet")
        print()
        input(f"{Colors.YELLOW}Presiona ENTER cuando estés listo...{Colors.RESET}")

        url = "https://testnet.binancefuture.com/"

        print_info("Abriendo Binance Futures Testnet...\n")
        try:
            webbrowser.open(url)
            time.sleep(2)
        except:
            print_warning("No pude abrir el navegador automáticamente")
            print_info(f"Abre manualmente: {url}")

        print()
        print_step(3, "Sigue estos pasos en la página web:")
        print()
        print(f"{Colors.CYAN}   1. Click en 'Log In'{Colors.RESET}")
        print(f"{Colors.CYAN}   2. Elige login con GitHub (MÁS RÁPIDO){Colors.RESET}")
        print(f"{Colors.CYAN}      O registra con email{Colors.RESET}")
        print(f"{Colors.CYAN}   3. Una vez dentro, click en tu PERFIL (arriba derecha){Colors.RESET}")
        print(f"{Colors.CYAN}   4. Selecciona 'API Management'{Colors.RESET}")
        print()

    else:
        print_warning("Opción inválida. Ejecuta el script nuevamente.")
        return

    # Paso 4: Crear API Key
    print()
    print_step(4, "Crear API Key con PERMISOS")
    print()
    print(f"{Colors.CYAN}   1. Click en 'Create API' o 'Generate API Key'{Colors.RESET}")
    print(f"{Colors.CYAN}   2. Dale un nombre (label): 'testing-bot'{Colors.RESET}")
    print()
    print(f"{Colors.YELLOW}   3. IMPORTANTE - Marca estos permisos:{Colors.RESET}")
    print(f"{Colors.GREEN}      ✅ Enable Reading{Colors.RESET}")
    print(f"{Colors.GREEN}      ✅ Enable Spot & Margin Trading{Colors.RESET}")
    print(f"{Colors.RED}      ❌ Enable Withdrawals (NO marcar){Colors.RESET}")
    print()
    print(f"{Colors.CYAN}   4. IP Restriction: déjalo VACÍO{Colors.RESET}")
    print(f"{Colors.CYAN}   5. Click 'Generate' o 'Create'{Colors.RESET}")
    print()

    # Paso 5: Copiar credenciales
    print_step(5, "Copiar tus credenciales")
    print()
    print_warning("Las credenciales se muestran SOLO UNA VEZ!")
    print()
    print(f"{Colors.CYAN}   1. Copia la 'API Key' (Click en botón Copy){Colors.RESET}")
    print(f"{Colors.CYAN}   2. Copia la 'Secret Key' (Click en botón Copy){Colors.RESET}")
    print()

    input(f"{Colors.YELLOW}Presiona ENTER cuando hayas copiado AMBAS credenciales...{Colors.RESET}")

    # Paso 6: Configurar .env
    print()
    print_step(6, "Actualizar archivo .env")
    print()

    print_info("Ahora vamos a guardar tus credenciales en el archivo .env\n")

    api_key = input(f"{Colors.CYAN}Pega tu API Key aquí: {Colors.RESET}").strip()
    secret_key = input(f"{Colors.CYAN}Pega tu Secret Key aquí: {Colors.RESET}").strip()

    if not api_key or not secret_key:
        print_warning("No ingresaste las credenciales. Abortando.")
        print_info("Ejecuta el script nuevamente cuando tengas tus credenciales.")
        return

    # Guardar en .env
    env_path = os.path.join(os.getcwd(), '.env')

    env_content = f"""# ================================
# BINANCE TESTNET CONFIGURATION
# ================================

# API Keys - Binance Testnet
BINANCE_API_KEY={api_key}
BINANCE_SECRET_KEY={secret_key}

# Testnet URLs
BINANCE_TESTNET_URL=https://testnet.binance.vision
BINANCE_TESTNET_API=https://testnet.binance.vision/api

# Enable Testnet (IMPORTANT: set to true for testing)
BINANCE_USE_TESTNET=true

# Trading Configuration
DEFAULT_TRADING_PAIR=BTCUSDT
"""

    try:
        with open(env_path, 'w') as f:
            f.write(env_content)
        print_success(f"Archivo .env actualizado correctamente!")
        print_info(f"Ubicación: {env_path}\n")
    except Exception as e:
        print_warning(f"No pude escribir el archivo .env: {e}")
        print_info("Crea manualmente el archivo .env con este contenido:\n")
        print(env_content)
        return

    # Paso 7: Ejecutar test
    print()
    print_step(7, "Verificar configuración")
    print()

    run_test = input(f"{Colors.CYAN}¿Ejecutar test de diagnóstico ahora? (s/n): {Colors.RESET}").strip().lower()

    if run_test == 's' or run_test == 'si' or run_test == 'y' or run_test == 'yes':
        print()
        print_info("Ejecutando diagnóstico...\n")
        os.system("python diagnose_binance.py")
    else:
        print()
        print_info("Puedes ejecutar el diagnóstico manualmente con:")
        print(f"{Colors.CYAN}   python diagnose_binance.py{Colors.RESET}\n")

    print()
    print_header("🎉 CONFIGURACIÓN COMPLETADA")
    print()
    print_success("Si el diagnóstico fue exitoso, ya puedes usar:")
    print()
    print(f"{Colors.CYAN}   python test_binance_connection.py{Colors.RESET}")
    print(f"{Colors.CYAN}   python test_binance_market.py{Colors.RESET}")
    print(f"{Colors.CYAN}   python test_binance_trading.py{Colors.RESET}")
    print()
    print_info("Para más ayuda, consulta:")
    print(f"{Colors.CYAN}   cat GUIA_VISUAL_BINANCE.md{Colors.RESET}")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Operación cancelada por el usuario{Colors.RESET}\n")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error: {e}{Colors.RESET}\n")
