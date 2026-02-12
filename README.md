# Deco-Security – Operativo de Consolas y API

## Puertos y servicios principales
- 3005 → Consola Cliente (`dashboard_client`)
- 3006 → Consola Master (`dashboard`)
- 3007 → Consola Partner (`deco-sec-dashboard-partner`)
- 18001 → API Orquestador FastAPI (`orchestrator_api`, interno 8000)

## Consola Partner – URLs de API
- Externa (navegador): `NEXT_PUBLIC_ORCHESTRATOR_URL=http://127.0.0.1:18001` (ajustar a dominio/túnel cuando aplique).
- Interna (SSR): `ORCHESTRATOR_INTERNAL_URL=http://orchestrator_api:8000`.
- Ubicación: `docker/docker-compose.yml` y `.env.local` de `dashboard_partners` para desarrollo.

## Verificaciones rápidas tras un deploy
1) `cd /opt/deco/docker && docker compose ps` (ver contenedores arriba).
2) `bash /opt/deco/scripts/check_deco_ports.sh` (HTTP 200/307 esperados en 3005/3006/3007; 200 en 18001/health).
3) `curl -sS http://127.0.0.1:18001/health` (API OK) y abrir las consolas en navegador para validar login y dashboard.

## Si se requiere reconstruir
- `cd /opt/deco/docker && docker compose up -d --build dashboard dashboard_partner deco-sec-dashboard-client orchestrator_api`
  (ajusta la lista de servicios según lo cambiado). 

## Observabilidad opcional
- Script de chequeo: `/opt/deco/scripts/check_deco_ports.sh` (añadir a cron si se desea monitorizar).

## Seguridad de claves
- Ejecuta rotación de claves expuestas (p.ej. API Keys de partners) y guarda en vault interno antes de compartir entornos externos.
