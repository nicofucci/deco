# MASTER EXECUTION PLAN: Hardening Deco-Security

> **⚠️ CRITICAL WARNING**
> Este documento contiene **COMANDOS DE SISTEMA** que requieren privilegios de `root` o `sudo`.
> NO ejecutar paso a paso sin entender lo que hace cada comando.
> NO ejecutar fuera de una ventana de mantenimiento.

## 0. Verificación Previa
- [ ] Acceso `sudo` verificado.
- [ ] No hay alertas críticas activas en este momento.
- [ ] Cargas del sistema (load average) normales.

## 1. Backup de Seguridad (Rapid Rollback)
Antes de tocar nada, respaldar las configuraciones actuales.

```bash
sudo mkdir -p /root/deco_backup_$(date +%F)
# Backup systemd configurations
sudo cp -r /etc/systemd/system /root/deco_backup_$(date +%F)/
# Backup journald config
sudo cp /etc/systemd/journald.conf /root/deco_backup_$(date +%F)/
```

## 2. Aplicar Systemd Drop-ins (Hardening)

### A. Crear Directorios
```bash
sudo mkdir -p /etc/systemd/system/deco-autostart.service.d
sudo mkdir -p /etc/systemd/system/deco-tower.service.d
# Repetir para otros servicios si es necesario
```

### B. Inyectar Configuraciones (Override)
*Copiar y pegar los bloques siguientes en la terminal:*

**Para `deco-autostart` (Crítico con Docker):**
```bash
sudo bash -c 'cat > /etc/systemd/system/deco-autostart.service.d/override.conf <<EOF
[Service]
BindsTo=docker.service
After=docker.service
ConditionPathExists=/opt/deco/docker-compose.yml
TimeoutStartSec=120
Restart=on-failure
RestartSec=10
StartLimitIntervalSec=300
StartLimitBurst=3
EOF'
```

**Para servicios genéricos (ej. `deco-tower`):**
```bash
sudo bash -c 'cat > /etc/systemd/system/deco-tower.service.d/hardening.conf <<EOF
[Service]
Restart=on-failure
RestartSec=5
StartLimitIntervalSec=300
StartLimitBurst=5
NoNewPrivileges=true
PrivateTmp=true
EOF'
```

### C. Recargar Systemd
```bash
sudo systemctl daemon-reload
```

## 3. Limpieza y Configuración de Journald

### A. Aplicar Límites (Drop-in)
```bash
sudo mkdir -p /etc/systemd/journald.conf.d
sudo bash -c 'cat > /etc/systemd/journald.conf.d/hardening.conf <<EOF
[Journal]
SystemMaxUse=1G
RuntimeMaxUse=500M
MaxRetentionSec=7day
SystemKeepFree=2G
EOF'
```

### B. Limpieza Inmediata (Vacuum)
```bash
sudo journalctl --vacuum-size=1G
sudo journalctl --vacuum-time=7d
```

### C. Reiniciar Journald
```bash
sudo systemctl restart systemd-journald
```

## 4. Reinicio Controlado de Servicios
Aplicar el hardening reiniciando los servicios (uno por uno).

```bash
sudo systemctl restart deco-tower
sudo systemctl restart deco-autostart
# Verificar estado
sudo systemctl status deco-tower --no-pager
sudo systemctl status deco-autostart --no-pager
```

## 5. Implementación Monitorización (Manual)
*Solo si se aprobó el script de healthcheck.*

```bash
# Crear script (si no existe)
# Asignar permisos +x
# Verificar ejecución manual: ./deco-healthcheck.sh
```

## 6. Verificación Final

1.  **Disco**: `journalctl --disk-usage` debe mostrar < 1G.
2.  **Servicios**: `systemctl --failed` debe estar vacío.
3.  **Logs**: `journalctl -f` debe mostrar logs fluyendo normalmente.

## 7. Plan de Rollback
En caso de fallo crítico (boot loop o servicio no arranca):

1.  **Eliminar Drop-ins**:
    ```bash
    sudo rm /etc/systemd/system/deco-autostart.service.d/override.conf
    sudo rm /etc/systemd/system/deco-tower.service.d/hardening.conf
    sudo rm /etc/systemd/journald.conf.d/hardening.conf
    ```
2.  **Recargar y Reiniciar**:
    ```bash
    sudo systemctl daemon-reload
    sudo systemctl restart deco-autostart
    sudo systemctl restart systemd-journald
    ```

---
**FIN DEL PROCEDIMIENTO**
