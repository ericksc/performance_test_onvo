#!/usr/bin/env pwsh
# Script de demostración del nuevo flujo de trabajo

Write-Host @"
╔═══════════════════════════════════════════════════════════════╗
║  Demo: Gestión Centralizada de Secretos de ONVO Pay          ║
╚═══════════════════════════════════════════════════════════════╝

Este script muestra cómo usar el nuevo sistema de configuración.

PASO 1: Configuración inicial (una sola vez)
"@

Write-Host @"
─────────────────────────────────────────────────────────────
Para configurar tu llave secreta:

    python configurar_clave.py

Esto te pedirá:
  1. Tu llave del Dashboard de ONVO (onvo_test_secret_key_...)
  2. Confirmar pegando la llave nuevamente
  3. Crea un archivo .env protegido

PASO 2: Usar medir_onvo.py
─────────────────────────────────────────────────────────────
Ahora es mucho más simple, sin parámetros:

    # Medir 1 solicitud
    python medir_onvo.py 1

    # Medir 20 solicitudes
    python medir_onvo.py 20

    # Diagnóstico sin credenciales
    python medir_onvo.py 10 --sin-clave

PASO 3: Usar Locust
─────────────────────────────────────────────────────────────
Test de verificación:
    python locust/ejecutar.py verificar

Test de latencia (1 usuario, 1 minuto):
    python locust/ejecutar.py latencia

Test de concurrencia (3 usuarios, 2 minutos):
    python locust/ejecutar.py concurrencia

Los reportes se guardan en: locust/reportes/<timestamp>_<perfil>/


MÉTODOS ANTIGUOS SIGUEN FUNCIONANDO
─────────────────────────────────────────────────────────────
Si prefieres no crear .env:

    # Variable de entorno temporal
    `$env:ONVO_TEST_SECRET_KEY = "tu_llave_aqui"
    python medir_onvo.py 10

    # Pedir la llave cada vez
    python medir_onvo.py 10 --pedir-clave


ARCHIVOS IMPORTANTES
─────────────────────────────────────────────────────────────
  .env              - Tu llave secreta (creada por configurar_clave.py)
  .env.example      - Plantilla de referencia
  .gitignore        - Protege .env del versionado
  configurar_clave.py - Script de configuración
  SETUP.md          - Guía de inicio rápido
  GUIA_SECRETOS.md  - Detalles técnicos

"@
