# Plan de Refactorización

## 1. Separar responsabilidades (arquitectura por módulos)

Actualmente, todo está en un solo archivo. Lo ideal sería estructurarlo así:

```
app/
 ├── main.py               # Punto de entrada FastAPI
 ├── config.py             # Configuración (paths, logging, variables de entorno)
 ├── models/
 │    └── prediction.py    # Modelos Pydantic
 ├── services/
 │    ├── data_fetcher.py  # Lógica para obtener datos de Coinbase
 │    ├── predictor.py     # Lógica de inferencia ONNX
 │    └── loader.py        # Carga y gestión de modelos
 ├── utils/
 │    └── logger.py        # Configuración centralizada de logging
 └── requirements.txt
```

### Beneficios:
- Separación clara de la lógica de negocio (fetch/predicción) del código de presentación (endpoints).
- Mantenimiento más simple a largo plazo.

## 2. Uso de variables de entorno

Mover rutas de modelos, parámetros de conexión, etc., a variables de entorno usando `pydantic-settings` o `python-decouple`.

En Cloud Run, estas variables se configuran en el despliegue (`gcloud run deploy --set-env-vars VAR=VALUE`).

### Ejemplo (config.py):

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    eth_model_path: str = "trained_models/model_eth.onnx"
    allowed_origins: list[str] = ["*"]

settings = Settings()
```

## 3. Mejorar logging y trazabilidad

- Usar un logger con formato JSON para integrarse con Cloud Logging.
- Incluir IDs de petición para seguimiento (FastAPI middleware con uuid).

### Ejemplo (utils/logger.py):

```python
import logging
import sys

def get_logger(name: str):
    logger = logging.getLogger(name)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
```

## 4. Manejo de errores más explícito

- Crear excepciones personalizadas (`ModelNotLoadedError`, `DataFetchError`) y manejadores globales con `app.exception_handler`.
- Evitar que errores genéricos se devuelvan sin contexto.

### Ejemplo:

```python
from fastapi.responses import JSONResponse
from fastapi import Request

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(status_code=500, content={"error": "Internal Server Error"})
```

## 5. Carga de modelos optimizada

- Usar `InferenceSession` con `providers=["CPUExecutionProvider"]` explícito para evitar fallback lento.
- Soporte para múltiples modelos (si en el futuro hay BTC, BNB, etc.) usando un cargador genérico.

## 6. Testing y validación

- Crear tests unitarios y de integración con `pytest`.
- Mockear llamadas a `ccxt` para no depender de la red en tests.

## 7. Optimización para Cloud Run

Configurar tiempos de espera y threads para uso eficiente:

```bash
gunicorn -k uvicorn.workers.UvicornWorker --bind :$PORT --workers 1 --threads 8 --timeout 0
```

## 8. Documentación y contratos

- Documentar el endpoint `/prediction` con ejemplos de request/response en el docstring.
- Usar tags en FastAPI para agrupar endpoints en `/docs`.