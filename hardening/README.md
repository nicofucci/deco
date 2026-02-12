# Deco-Security Hardening

Esta carpeta contiene la configuración y documentación necesaria para aplicar el hardening del sistema, systemd y journald.

## ⚠️ ADVERTENCIA CRÍTICA

**TODO lo que hay en esta carpeta requiere permisos de `sudo` para ser aplicado.**
No intente ejecutar ningún script ni aplicar configuraciones sin los privilegios adecuados y sin seguir el plan de ejecución estricto.

## Contexto

Esta preparación responde a la necesidad de estabilizar el sistema tras incidentes previos de saturación de recursos (kernel panic). El objetivo es establecer límites claros en los logs y asegurar el reinicio controlado de servicios críticos.

## Instrucciones

1.  **NO ejecutar cambios de sistema** fuera de la ventana de mantenimiento programada.
2.  **Solo crear archivos** y validar su contenido.
3.  Seguir la guía maestra `RUN_WITH_SUDO_ONCE.md` para la aplicación final.
