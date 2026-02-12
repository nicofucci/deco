# INFORME DE RESTAURACIÓN: API Y CONSOLA DECO-GRAVITY

## 1. Resumen de la Intervención
Se ha restaurado la conectividad entre el Dashboard (Next.js) y la API (Orchestrator/Jarvis). El problema principal era una configuración incorrecta que apuntaba a puertos legacy y un conflicto en la resolución de DNS en Cloudflare.

**Estado Actual:**
- **Dashboard**: Operativo en `http://127.0.0.1:3000`.
- **API**: Operativa en `http://127.0.0.1:18001`.
- **Servicio Legacy**: `deco-app.service` (antiguo uvicorn en user space) ha sido **DESHABILITADO** para evitar conflictos.
- **Configuración**: El Dashboard ahora sabe distinguir entre llamadas internas (Docker/Localhost) y externas (Cloudflare).

## 2. Cambios Técnicos Realizados (Lado Servidor)

### Servicios y Puertos
- Se confirmó que `orchestrator_api` corre en el puerto **18001** (mapeado desde el 8000 interno del contenedor).
- Se confirmó que `dashboard` corre en el puerto **3000** (host mode).
- Se deshabilitó `deco-app.service` que intentaba levantar otra instancia de la API y fallaba.

### Configuración de Entorno (`/opt/deco/docker/docker-compose.yml`)
Se actualizaron las variables de entorno del servicio `dashboard`:
```yaml
environment:
  - NEXT_PUBLIC_API_URL=https://api.deco-security.com  # Para el navegador del usuario
  - INTERNAL_API_URL=http://127.0.0.1:18001            # Para el servidor Next.js (SSR)
```

### Código del Dashboard (`/opt/deco/agent_runtime/dashboard/lib/api.ts`)
Se modificó la lógica de conexión para usar `INTERNAL_API_URL` cuando el código se ejecuta en el servidor, evitando errores de conexión SSL/DNS internos.

## 3. INSTRUCCIONES PARA NICO – CLOUDFLARE

> [!IMPORTANT]
> Sigue estos pasos EXACTAMENTE para resolver el error "A, AAAA, or CNAME record with that host already exists" y habilitar el acceso externo.

### Explicación del Error
El mensaje indica que existe un registro DNS manual (tipo A, AAAA o CNAME) para `api.deco-security.com` en la zona DNS clásica de Cloudflare. Esto entra en conflicto cuando intentas crear una "Public Hostname" en el Túnel con el mismo nombre, ya que el Túnel intenta crear su propio registro CNAME virtual.

### Pasos a Seguir

1.  **Limpiar DNS Clásico**:
    *   Ve al panel de Cloudflare > **Sitios web** > `deco-security.com` > **DNS**.
    *   Busca en la lista cualquier registro con el nombre `api` (o `api.deco-security.com`).
    *   **Bórralo** (Delete). *Nota: Si ves un CNAME que apunta a `[tu-tunnel-id].cfargotunnel.com`, ese es el del túnel. Si Cloudflare no te deja crear la ruta en el paso 2, bórralo también y deja que el túnel lo recree.*

2.  **Configurar el Túnel (Zero Trust)**:
    *   Ve a **Zero Trust** > **Networks** > **Tunnels**.
    *   Selecciona tu túnel (`deco-global-tunnel`) y dale a **Configure**.
    *   Ve a la pestaña **Public Hostname**.
    *   Añade una nueva ruta (o edita la de `api` si quedó a medias):
        *   **Subdomain**: `api`
        *   **Domain**: `deco-security.com`
        *   **Path**: Dejar vacío o poner `*` (según te pida, normalmente vacío cubre todo).
        *   **Service**: `HTTP` :// `127.0.0.1:18001`
    *   Guarda los cambios (`Save hostname`).

3.  **Verificación Final**:
    *   Abre en tu navegador: `https://api.deco-security.com/health` (debería responder `{"status":"ok",...}`).
    *   Abre en tu navegador: `https://consola.deco-security.com`.
    *   **Resultado esperado**: El Dashboard carga y YA NO aparece el mensaje "Error connecting to system".

## 4. Checklist de Mantenimiento

### Comandos de Verificación Rápida
*   **Ver estado de contenedores**:
    ```bash
    docker ps --format "table {{.Names}}\t{{.Ports}}\t{{.Status}}"
    ```
*   **Ver logs del Dashboard**:
    ```bash
    cd /opt/deco/docker && docker compose logs -f dashboard
    ```
*   **Ver logs de la API**:
    ```bash
    cd /opt/deco/docker && docker compose logs -f orchestrator_api
    ```

### Solución de Problemas
Si vuelve a aparecer "Error connecting to system":
1.  Comprueba que el contenedor `orchestrator_api` esté corriendo (`docker ps`).
2.  Comprueba que `https://api.deco-security.com/health` responde desde tu navegador (si no, es problema de Cloudflare o del Túnel).
3.  Comprueba que `curl http://127.0.0.1:18001/health` responde desde la torre (si no, es problema del contenedor API).

---
**FASE RESTAURACIÓN API + DASHBOARD COMPLETADA**
