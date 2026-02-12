# Plan de Hardening: Journald Limits

## 1. Problema Actual

*   **Síntoma**: El directorio `/var/log/journal` ha llegado a ocupar ~3 GB o más.
*   **Riesgo**: Saturación del sistema de archivos raíz (`/`), lo que puede provocar un *Kernel Panic* o fallos en cascada de servicios críticos por falta de espacio ("No space left on device").
*   **Causa**: La configuración por defecto de systemd suele ser permisiva (hasta un 10-15% del disco), lo cual es excesivo para este entorno.

## 2. Configuración Propuesta (Drop-in)

Para evitar editar `/etc/systemd/journald.conf` directamente, se recomienda evaluar si la distribución soporta drop-ins en `/etc/systemd/journald.conf.d/`. Si no, se editará el archivo principal con respaldo previo.

**Valores Recomendados:**

```ini
[Journal]
# Límite duro de espacio en disco
SystemMaxUse=1G

# Límite de logs en memoria (si se usa Storage=volatile)
RuntimeMaxUse=500M

# Tiempo máximo de retención de logs antiguos
MaxRetentionSec=7day

# Espacio que SIEMPRE debe quedar libre en disco
SystemKeepFree=2G

# Opcional: Reducir verbosidad / rate limit si hay spam
# RateLimitIntervalSec=30s
# RateLimitBurst=1000
```

## 3. Limpieza Inicial (Documentada)

Estos comandos son **DESTRUCTIVOS** y requieren `sudo`. Solo deben ejecutarse UNA VEZ durante la ventana de mantenimiento para recuperar espacio inmediatamente.

```bash
# Reducir logs a un tamaño específico inmediatamente
sudo journalctl --vacuum-size=1G

# Eliminar logs más antiguos de 7 días
sudo journalctl --vacuum-time=7d

# Verificar integridad tras limpieza
sudo journalctl --verify
```

## 4. Decisión sobre Storage

*   **`Storage=persistent`** (Actual/Default): Logs se guardan en `/var/log/journal`. Sobreviven reinicios.
    *   *Uso*: Necesario para depurar fallos post-crash o kernel panics anteriores.
*   **`Storage=volatile`**: Logs se guardan en `/run/log/journal` (RAM). Se pierden al reiniciar.
    *   *Uso*: Solo si el disco es extremadamente lento o frágil.
    *   *Decisión*: **Mantener `persistent`** pero con los límites estrictos de `SystemMaxUse=1G` definidos arriba.

## 5. Checklist de Verificación Post-Ejecución

Tras aplicar cambios y reiniciar `systemd-journald`:

1.  [ ] Verificar uso de disco actual: `journalctl --disk-usage` (Debe decir "< 1.0G").
2.  [ ] Verificar que se están escribiendo logs nuevos: `logger "Test de hardening journald" && journalctl -n 5`.
3.  [ ] Reinicio de prueba (Reboot Test): Confirmar que no hay corrupción de journals al arrancar.

---
**ESTE DOCUMENTO ES SOLO UNA GUÍA DE PLANIFICACIÓN. NO EJECUTAR COMANDOS DE VACUUM SIN AUTORIZACIÓN.**
