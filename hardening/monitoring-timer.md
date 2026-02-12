# Plan de Hardening: Monitoring & Early Detection

## 1. Objetivo

Implementar un mecanismo ligero de "autodiagnóstico" que permita la detección temprana de degradación en el servidor antes de que ocurra un fallo catastrófico (kernel panic o bloqueo total).
Puntos clave a vigilar:
*   Servicios en estado `failed`.
*   Crecimiento descontrolado de `journald`.
*   Ocupación de puertos críticos por procesos zombis o inesperados.

## 2. Script Propuesto: `deco-healthcheck.sh`

**Ubicación sugerida:** `/opt/deco/scripts/deco-healthcheck.sh`
**Permisos:** Ejecutable (+x)

Este script **NO** se debe crear ahora. Este es el diseño conceptual de lo que ejecutará:

```bash
#!/bin/bash
# Concepto de Healthcheck - NO EJECUTAR
echo "=== System Health Start: $(date) ==="

# 1. Verificar servicios caídos
echo "[Checking Failed Services]"
systemctl --failed --no-pager

# 2. Verificar ocupación de puerto 3000 (Next.js) y 8000 (API)
echo "[Checking Critical Ports]"
ss -lntp | grep -E ':3000|:8000'

# 3. Verificar uso de disco de Journald
echo "[Checking Journal Usage]"
journalctl --disk-usage

# 4. Verificar carga general
uptime

echo "=== System Health End ==="
```

## 3. Systemd Timer (Concepto)

Para automatizar esta revisión sin depender de cron, usaremos un **Systemd Timer**.

**Beneficios:**
*   Logging integrado en journald.
*   Gestión de dependencias (se ejecuta solo si el sistema arrancó bien).
*   `OnCalendar`: Flexibilidad en horarios.

**Unidad de Servicio (`deco-healthcheck.service`):**
Define la ejecución del script ("Type=oneshot").

**Unidad de Timer (`deco-healthcheck.timer`):**
Define la periodicidad.

```ini
[Timer]
# Ejecutar cada día a las 04:00 AM
OnCalendar=*-*-* 04:00:00
# O ejecutar cada 6 horas
# OnCalendar=00/6:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

## 4. Métricas Críticas y Umbrales

Si se implementan alertas futuras, estos son los valores de referencia ("Warning Thresholds"):

| Métrica | Umbral Crítico | Acción Recomendada |
| :--- | :--- | :--- |
| **Journald Size** | `> 80%` del límite (800MB) | `journalctl --vacuum-size=500M` |
| **Services Failed** | `> 0` | Revisar logs del servicio específico |
| **Puerto 3000** | Sin LISTEN o PID duplicado | Reiniciar `deco-tower` / `docker` |
| **Load Average** | `> N_CPUs * 2` (15 min) | Investigar procesos (posible minería o bucle) |

---
**ESTE DOCUMENTO ES SOLO UNA GUÍA DE DISEÑO. NO IMPLEMENTAR EL TIMER SIN VALIDAR EL SCRIPT MANUALMENTE PRIMERO.**
