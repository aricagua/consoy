import requests
import json
import time
import random
import uuid
import sys

# ==============================================================================
# --- CONFIGURACIÓN DEL SIMULADOR ---
# --- ¡SOLO NECESITAS EDITAR ESTAS 3 LÍNEAS! ---
# ==============================================================================

# 1. Pega la URL de tu proyecto Supabase aquí
SUPABASE_URL = "https://ezvcuhzlegiphfaybhti.supabase.co"

# 2. Pega tu clave 'anon' (public) de Supabase aquí
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV6dmN1aHpsZWdpcGhmYXliaHRpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMxOTY1MTMsImV4cCI6MjA3ODc3MjUxM30.MZHkXMveud8KjPKkM5h3DjsEWkaBS30tf4CipuxFyNc"

# 3. Intervalo de envío de datos en segundos
SEND_INTERVAL_SECONDS = 10 # Lo ponemos en 10s para pruebas rápidas

# ==============================================================================

# --- LÓGICA DEL SIMULADOR (NO TOCAR) ---

def get_device_mac():
    """Obtiene la dirección MAC de la máquina actual para usarla como un deviceID único y persistente."""
    # uuid.getnode() devuelve un número de 48 bits, lo formateamos como una MAC address
    mac_num = uuid.getnode()
    mac = ':'.join(('%012X' % mac_num)[i:i+2] for i in range(0, 12, 2))
    return mac

def generate_realistic_data():
    """
    Simula la lógica del estabilizador para generar datos coherentes.
    El tap seleccionado dependerá del voltaje de entrada simulado.
    """
    # Simula un voltaje de entrada fluctuante en un rango realista
    voltaje_in = round(random.uniform(160.0, 245.0), 1)
    
    # Simula la lógica de selección de derivación del código original
    derivacion_actual = 0
    if 165.0 <= voltaje_in < 180.0:
        derivacion_actual = 180
    elif 180.0 <= voltaje_in < 190.0:
        derivacion_actual = 190
    elif 190.0 <= voltaje_in < 200.0:
        derivacion_actual = 200
    elif 200.0 <= voltaje_in <= 240.0:
        derivacion_actual = 220
    else: # Por debajo de 165 o por encima de 240
        derivacion_actual = 0 # Ningún tap activo
        
    # Simula un voltaje de salida estable, con una pequeña fluctuación
    voltaje_out = round(random.uniform(219.5, 221.0), 1) if derivacion_actual != 0 else 0.0
    
    return voltaje_in, voltaje_out, derivacion_actual

def main():
    """Función principal que ejecuta el ciclo de envío de datos."""
    device_mac = get_device_mac()
    api_url = f"{SUPABASE_URL}/rest/v1/readings"
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }

    print("==============================================")
    print("===   SIMULADOR DE ESTABILIZADOR CONSOY    ===")
    print("==============================================")
    print(f"[*] Iniciando simulación para el dispositivo: {device_mac}")
    print(f"[*] Enviando datos cada {SEND_INTERVAL_SECONDS} segundos a Supabase.")
    print("[*] Presiona CTRL+C para detener.")

    try:
        while True:
            volt_in, volt_out, derivacion = generate_realistic_data()

            payload = {
                "device_mac": device_mac,
                "voltaje_in": volt_in,
                "voltaje_out": volt_out,
                "derivacion_actual": derivacion
            }

            print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Enviando datos: {payload}")

            try:
                response = requests.post(api_url, headers=headers, data=json.dumps(payload), timeout=10)
                
                # Chequea la respuesta del servidor
                if response.status_code == 201:
                    print(f"[*] Éxito: Datos recibidos por Supabase (Código: {response.status_code})")
                else:
                    print(f"[!] Error: El servidor respondió con el código {response.status_code}")
                    print(f"    Respuesta: {response.text}")

            except requests.exceptions.RequestException as e:
                print(f"[!] Error de Conexión: No se pudo conectar al servidor.")
                print(f"    Detalle: {e}")

            time.sleep(SEND_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\n[*] Simulación detenida por el usuario. ¡Adiós!")
        sys.exit(0)

if __name__ == "__main__":
    main()
