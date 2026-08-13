import os

X_HANDLE = os.environ.get("X_HANDLE", "davidfgonzalezc")

# Dominio publico del sitio, para construir URLs absolutas (og:url, og:image).
# Override por entorno; default al dominio de Railway. Sin barra final.
SITE_URL = os.environ.get(
    "SITE_URL", "https://manos-a-la-obra-production.up.railway.app"
).rstrip("/")
