# X-RAY Network Scan™

**Internal Name**: `xray_network_scan`

## Objetivo
El objetivo de este job es descubrir y catalogar todos los dispositivos conectados a la red local donde reside el agente. Proporciona una "radiografía" completa de la infraestructura del cliente, permitiendo identificar activos no gestionados, dispositivos IoT, y posibles riesgos de seguridad.

## Lógica de Ejecución (Agente)
1.  **Identificación de Red**: El agente identifica su interfaz de red principal, IP local y máscara de subred para determinar el rango a escanear.
2.  **Descubrimiento (Discovery)**:
    -   **Ping Sweep / ARP Scan**: Envía sondas ARP y ICMP a todas las direcciones del rango identificado para encontrar hosts activos.
    -   **Resolución de Nombres**: Intenta resolver el nombre de host mediante DNS reverso, NetBIOS y mDNS.
    -   **Identificación de MAC**: Obtiene la dirección MAC para cada host.
    -   **MAC Vendor**: Consulta una base de datos local o API (si disponible) para identificar el fabricante (Vendor) basado en la MAC.
3.  **Fingerprinting Ligero**:
    -   Realiza un escaneo rápido de puertos comunes (22, 80, 443, 3389, 445, 9100) para inferir el tipo de dispositivo y servicios básicos.
    -   Intenta adivinar el Sistema Operativo (OS Guess) y el tipo de dispositivo (`device_type`).

## Salida (Result Payload)
El agente retornará un JSON con la siguiente estructura en el campo `parsed_summary` o `data`:

```json
{
  "network": {
    "cidr": "192.168.1.0/24",
    "gateway": "192.168.1.1",
    "interface": "eth0"
  },
  "devices": [
    {
      "ip": "192.168.1.10",
      "mac": "AA:BB:CC:DD:EE:FF",
      "mac_vendor": "Dell Inc.",
      "hostname": "DESKTOP-OFFICE-01",
      "os_guess": "Windows 10/11",
      "device_type": "pc",
      "open_ports": [135, 139, 445, 3389],
      "first_seen": "2023-10-27T10:00:00Z",
      "last_seen": "2023-10-27T10:00:00Z"
    },
    {
      "ip": "192.168.1.50",
      "mac": "11:22:33:44:55:66",
      "mac_vendor": "Apple, Inc.",
      "hostname": "iPhone-de-Juan",
      "os_guess": "iOS",
      "device_type": "mobile",
      "open_ports": [],
      "first_seen": "2023-10-27T10:00:00Z",
      "last_seen": "2023-10-27T10:00:00Z"
    }
  ]
}
```

## Integración
-   **Orchestrator**: Recibe el resultado y actualiza la tabla `network_assets`.
-   **Consolas**: Muestran la lista de dispositivos en una vista dedicada "Red Local".
