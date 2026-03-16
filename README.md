## Procesamiento de Imágenes Satelitales VNP46A1

Proyecto para procesar imágenes satelitales VNP46A1 (luminosidad nocturna) y obtener métricas de radianza por municipio.  
Incluye una **API asíncrona con FastAPI** para lanzar jobs de procesamiento en segundo plano y guardar resultados en Parquet.

### Componentes principales

- `satellite_sync/`: implementación **síncrona** del pipeline de procesamiento.
- `satellite_async/`: implementación **asíncrona**, utilizada por la API.
- `api/`: aplicación FastAPI que expone el procesamiento como servicio HTTP.
- `Data/`: datos auxiliares (coordenadas de municipios, límites geográficos).

Se utilizan **Pydantic v2** y modelos como `MedicionResultado` para validar y serializar los resultados.

---

## Requisitos e instalación

- Python 3.11+ (recomendado 3.12)
- `pip` y `virtualenv` (o equivalente)

```bash
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

pip install -r requirements.txt
# Para desarrollo y tests:
pip install -r requirements-dev.txt
```

Con esta instalación el paquete queda en el path de Python; **no hace falta usar `PYTHONPATH`** para ejecutar los ejemplos ni la API desde la raíz del proyecto.

Los datos de municipios (`limite-de-las-alcaldias.json`, `municipios_coordenadas_pixeles.json`) vienen incluidos en el paquete; no hace falta configurar rutas. Solo necesitas definir `NASA_API_TOKEN` en tu `.env` (o en el entorno) para la descarga de imágenes.

---

## Uso de la API FastAPI (versión async)

Desde la raíz del proyecto:

```bash
uvicorn api.main:app --reload
```

La documentación interactiva estará disponible en:

- `http://localhost:8000/docs`

### Endpoints principales

- **`GET /municipios`**
  - Devuelve la lista de municipios disponibles para procesamiento.
  - Respuesta: `{ "municipios": ["iztapalapa", "coyoacan", ...] }`

- **`POST /jobs`**
  - Crea un job de procesamiento asíncrono.
  - Cuerpo (`JobRequest`):

    ```json
    {
      "municipios": ["iztapalapa"],
      "fecha_inicio": "2024-01-01",
      "fecha_fin": "2024-01-03",
      "chunks": 2
    }
    ```

  - Respuesta (`JobStatus`, HTTP 202):

    ```json
    {
      "job_id": "uuid-generado",
      "status": "pending",
      "progress": null,
      "created_at": "2024-01-01T00:00:00",
      "finished_at": null,
      "error": null,
      "total_results": 0
    }
    ```

- **`GET /jobs/{job_id}`**
  - Consulta el estado actual del job (`pending`, `running`, `completed`, `failed`).
  - Respuesta: `JobStatus`.

- **`GET /jobs/{job_id}/results`**
  - Devuelve los resultados del job una vez completado.
  - Respuesta (`JobResult`): contiene `results`, una lista de `MedicionResultado` serializados a JSON, por ejemplo:

    ```json
    {
      "job_id": "uuid-generado",
      "results": [
        {
          "Fecha": "2024-01-01",
          "Municipio": "iztapalapa",
          "Cantidad_de_pixeles": 100,
          "Suma_de_radianza": 1000.0,
          "Media_de_radianza": 10.0,
          "Desviacion_estandar_de_radianza": 1.0,
          "Maximo_de_radianza": 12.0,
          "Minimo_de_radianza": 8.0,
          "Percentil_25_de_radianza": 9.0,
          "Percentil_50_de_radianza": 10.0,
          "Percentil_75_de_radianza": 11.0
        }
      ]
    }
    ```

- **`DELETE /jobs/{job_id}`**
  - Cancela un job pendiente/en ejecución y lo elimina del store.

---

## Flujo de procesamiento (vista rápida)

1. Para cada fecha y municipio:
   - Se descarga el archivo HDF5 VNP46A1 correspondiente (NASA).
   - Se recorta la imagen usando las coordenadas de píxeles del municipio.
2. Se calculan métricas de radianza (media, suma, percentiles, máximo, mínimo, etc.) y se modelan con `MedicionResultado`.
3. Los resultados se consolidan en un `DataFrame` de `pandas` y se **guardan como Parquet** para análisis posterior.

La API usa la implementación **asíncrona** (`satellite_async`) para mejorar el rendimiento cuando se procesan muchas fechas o municipios.

---

## Ejemplos de uso desde código

En la carpeta `examples/` hay tres scripts listos para ejecutar desde la raíz del proyecto:

- `examples/sync_example.py`: uso básico de la versión síncrona (`SatelliteProcessor`).
- `examples/async_example.py`: uso básico de la versión asíncrona (`SatelliteImagesAsync`).
- `examples/api_example.py`: consumo de la API FastAPI (requiere tener levantado `uvicorn api.main:app --reload`).

Ejemplos de ejecución:

```bash
python examples/sync_example.py
python examples/async_example.py
python examples/api_example.py
```

---

## Ejecución de tests

El proyecto usa `pytest` y tests para:
- Lógica síncrona y asíncrona.
- Descarga de archivos.
- API FastAPI (endpoints y manejo de jobs).

Desde la raíz del proyecto, con el entorno virtual activado:

```bash
python -m pytest          # Ejecuta toda la batería de tests
python -m pytest tests/api  # Solo tests de la API
```

---

## Notas

- Se usa **Pydantic v2** (`model_dump`, `model_validate`) para validación y serialización de datos.
- Los resultados de mediciones se devuelven tipados como `MedicionResultado` en la API.
- Los archivos temporales y resultados intermedios se gestionan dentro del proyecto (por ejemplo, directorio `temp/`).

### Autores y coautores

- Proyecto desarrollado como trabajo terminal en ESCOM.
- Coautora: [Carolina Corral](https://github.com/carolinacorral).

Para dudas o contribuciones, abre un issue o un Pull Request en el repositorio.