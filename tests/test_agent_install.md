# Validación de Instalación de Agente (General)

## Objetivo
Verificar que el Agente Universal se instala, configura y comunica correctamente con el Orchestrator.

## Prerrequisitos
- API Key de Cliente válida.
- Acceso a internet (o ruta al Orchestrator).

## Flujo de Prueba

1. **Instalación Limpia**:
   - Eliminar instalaciones previas (`/opt/deco-security-agent`, `%PROGRAMDATA%\DecoSecurityAgent`).
   - Ejecutar instalador.

2. **Configuración**:
   - Verificar que se crea `config.json`.
   - Verificar que contiene la API Key correcta.

3. **Primer Arranque**:
   - El servicio debe iniciar automáticamente.
   - Debe registrarse en el Orchestrator (POST `/api/agents/register`).
   - Debe guardar el `agent_id` en `config.json`.

4. **Heartbeat y Discovery**:
   - Esperar 10-20 segundos.
   - Verificar en logs: "Heartbeat sent".
   - Verificar en Consola:
     - Agente Online.
     - IP Local correcta.
     - CIDR correcto.

5. **Persistencia**:
   - Reiniciar la máquina (o contenedor).
   - Verificar que el servicio arranca solo.
