import os
from config import TOKEN, HEADERS

print("🔍 Verificando configuración del token...")

print(f"📊 TOKEN: {TOKEN}")
print(f"📊 HEADERS: {HEADERS}")

# Verificar si el token existe
if TOKEN:
    print(f"✅ Token encontrado: {TOKEN[:10]}...{TOKEN[-10:] if len(TOKEN) > 20 else '***'}")
else:
    print(f"❌ Token no encontrado")

# Verificar variable de entorno
env_token = os.getenv("NASA_API_TOKEN")
if env_token:
    print(f"✅ Variable de entorno NASA_API_TOKEN encontrada: {env_token[:10]}...{env_token[-10:] if len(env_token) > 20 else '***'}")
else:
    print(f"❌ Variable de entorno NASA_API_TOKEN no encontrada")

# Verificar headers
if HEADERS and "Authorization" in HEADERS:
    auth_header = HEADERS["Authorization"]
    print(f"✅ Header de autorización configurado: {auth_header[:20]}...")
else:
    print(f"❌ Header de autorización no configurado")
    print(f"📊 HEADERS completo: {HEADERS}") 