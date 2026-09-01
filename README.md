# Reporte de ítems

Servicio programado que consulta los ítems de una compañía en una API externa y genera el archivo `items.xlsx`. En cada ejecución se autentica, consulta los ítems y actualiza el reporte; si el token expira, lo renueva y reintenta una vez.

## Configuración

Crea `.env` desde la plantilla y completa las credenciales de la API:

```powershell
Copy-Item .env.example .env
```

| Variable | Descripción | Predeterminado |
| --- | --- | --- |
| `API_BASE_URL` | URL base de la API externa. | — |
| `API_KEY` | Clave de acceso de la API. | — |
| `API_EMAIL` | Correo de autenticación. | — |
| `API_PASSWORD` | Contraseña de autenticación. | — |
| `COMPANY_ID` | Compañía cuyos ítems se consultarán. | — |
| `SCHEDULE_CRON` | Cron de cinco campos para generar el reporte. | — |
| `API_CHANNEL` | Valor enviado en el encabezado `x-canal`. | `API` |
| `API_TIMEOUT` | Tiempo máximo de espera HTTP, en segundos. | `30` |
| `SCHEDULE_TIMEZONE` | Zona horaria del cron. | `America/Bogota` |
| `REPORT_OUTPUT_DIR` | Nombre de la carpeta hermana donde se guardará el reporte. | `Items` |

## Producción: Docker

Requiere Docker con Docker Compose. Con `.env` configurado, inicia el servicio con un solo comando:

```powershell
docker compose up -d --build
```

El contenedor se reinicia automáticamente salvo que se detenga manualmente. El reporte se conserva como `../<REPORT_OUTPUT_DIR>/items.xlsx` en el equipo anfitrión, incluso si se recrea el contenedor. La ruta es relativa a la carpeta del proyecto: con `REPORT_OUTPUT_DIR=Items`, `/home/report-items` genera `/home/Items/items.xlsx` en Linux.

Consulta los registros o detén el servicio con:

```powershell
docker compose logs -f
docker compose down
```

## Desarrollo: uv

Requiere Python 3.14+ y [uv](https://docs.astral.sh/uv/).

```powershell
uv sync
uv run report-items
```

El proceso queda activo y ejecuta el reporte en los horarios definidos por `SCHEDULE_CRON`. Para detenerlo, usa `Ctrl+C`.

Al ejecutarlo desde la raíz de `report-items`, el reporte se guarda en la carpeta hermana indicada por `REPORT_OUTPUT_DIR`; con el valor `Items`, queda en `../Items/items.xlsx`.

Ejecuta las pruebas con:

```powershell
uv run pytest
```
