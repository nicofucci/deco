# Plan de Hardening: Systemd Drop-ins

## 1. Objetivo

El objetivo de este documento es definir la configuración de "Drop-ins" para systemd.
**¿Por qué Drop-ins?**
En lugar de editar los archivos de unidad originales (que pueden ser sobrescritos por actualizaciones del paquete o del sistema), utilizamos directorios `override.conf` (drop-ins). Esto permite:
*   Inyectar configuración específica sin tocar el vendor ni el upstream.
*   Mantener la persistencia tras actualizaciones.
*   Centralizar el hardening en archivos controlados.

## 2. Servicios Objetivo

Se aplicará hardening a los siguientes servicios identificados como críticos o expuestos:

*   **deco-autostart**: Servicio de arranque principal.
*   **deco-tower**: Orquestador principal.
*   **Servicios Deco-Security**:
    *   API Backend.
    *   Workers asíncronos.
*   **Ollama**: Servicio de inferencia AI (consumo alto de recursos).
*   **FastAPI**: Servidores de aplicación.
*   **Servicios generales**: Cualquier otro servicio de usuario o sistema que requiera estabilidad garantizada.

## 3. Drop-in Estándar Propuesto (Template)

Este template se aplicará a la mayoría de los servicios genéricos para asegurar reinicios automáticos y limpiar privilegios básicos.

**Archivo:** `/etc/systemd/system/<servicio>.service.d/hardening.conf`

```ini
[Service]
# Reinicio automático ante fallos
Restart=on-failure
RestartSec=5

# Evitar bucles de reinicio infinito (Start Burst)
StartLimitIntervalSec=300
StartLimitBurst=5

# Hardening Básico de Seguridad
NoNewPrivileges=true
PrivateTmp=true
```

## 4. Drop-in Especial: deco-autostart / deco-tower

Estos servicios son críticos y dependen explícitamente de Docker. Requieren una configuración más robusta para evitar condiciones de carrera al inicio.

**Archivo:** `/etc/systemd/system/deco-autostart.service.d/override.conf`

```ini
[Service]
# Dependencia fuerte con Docker
BindsTo=docker.service
After=docker.service

# Verificación de existencia antes de arrancar
ConditionPathExists=/opt/deco/docker-compose.yml

# Timeout extendido para levantar contenedores pesados
TimeoutStartSec=120

# Reinicio controlado
Restart=on-failure
RestartSec=10
StartLimitIntervalSec=300
StartLimitBurst=3

# NOTA: Evita loops infinitos si Docker falla repetidamente.
```

## 5. Notas de Seguridad y Ejecución

*   **Hardening Gradual**: No estamos aplicando todavía directivas agresivas como `ProtectKernelTunables` o `ProtectHome` para evitar romper la compatibilidad con contenedores que necesiten acceso al host.
*   **Validación**: Cada drop-in debe ser verificado con `systemd-analyze verify <servicio>` antes de reiniciar.
*   **Recarga**: Es obligatorio ejecutar `systemctl daemon-reload` después de crear los archivos drop-in.

---
**ESTE DOCUMENTO ES SOLO UNA GUÍA DE PLANIFICACIÓN. NO APLICAR SIN SUDO Y SIN RESPALDO.**
