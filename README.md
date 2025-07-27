# Proyecto de Procesamiento de Imágenes Satelitales VNP46A1

Este proyecto proporciona herramientas para el procesamiento y análisis de imágenes satelitales VNP46A1 de la NASA, específicamente diseñado para extraer mediciones de radianza por municipio en la Ciudad de México.

## 📋 Descripción

El proyecto incluye dos implementaciones principales:

- **`satellite_sync/`**: Implementación síncrona para procesamiento de imágenes satelitales
- **`satellite_async/`**: Implementación asíncrona para procesamiento más eficiente

### Características principales

- 📥 Descarga automática de imágenes satelitales VNP46A1 desde la NASA
- 🗺️ Recorte de imágenes por coordenadas de municipio
- 📊 Extracción de mediciones de radianza
- 📈 Visualización de resultados con gráficos
- 🔄 Procesamiento de múltiples fechas
- ⚡ Versión asíncrona para mejor rendimiento

## 🚀 Instalación

### Prerrequisitos

- Python 3.8+
- pip o conda

### Instalación de dependencias

```bash
pip install -r requirements.txt
```

### Dependencias principales

- **numpy**: Procesamiento numérico
- **pandas**: Manipulación de datos
- **matplotlib**: Visualización de gráficos
- **h5py**: Lectura de archivos HDF5
- **PyQt6**: Interfaz gráfica (opcional)
- **aiohttp**: Cliente HTTP asíncrono
- **pydantic**: Validación de datos

## 📁 Estructura del proyecto

```
├── satellite_sync/          # Implementación síncrona
│   ├── main.py             # Punto de entrada principal
│   ├── processor.py        # Clase principal SatelliteProcessor
│   ├── downloader.py       # Descarga de archivos
│   ├── image_processor.py  # Procesamiento de imágenes
│   ├── models.py           # Modelos de datos (Pydantic)
│   ├── utils.py            # Funciones auxiliares
│   └── config.py           # Configuración
├── satellite_async/        # Implementación asíncrona
│   ├── main.py             # Punto de entrada asíncrono
│   ├── satellite_async.py  # Clase principal asíncrona
│   ├── downloader.py       # Descarga asíncrona
│   ├── processing.py       # Procesamiento asíncrono
│   ├── models.py           # Modelos de datos
│   ├── utils.py            # Utilidades
│   └── config.py           # Configuración
├── Data/                   # Datos de municipios
│   ├── municipios_coordenadas_pixeles.json
│   └── limite-de-las-alcaldas.json
├── temp/                   # Archivos temporales
├── requirements.txt        # Dependencias de Python
└── README.md              # Este archivo
```

## 🎯 Uso

### Implementación Síncrona

```python
from satellite_sync import SatelliteProcessor

# Crear instancia del procesador
processor = SatelliteProcessor("Iztapalapa")

# Lista de fechas a procesar
fechas = ["01-01-24", "02-01-24", "03-01-24"]

# Procesar múltiples fechas
df = processor.run(fechas, "h08v07", show_plots=True)

if not df.empty:
    print("Resultados obtenidos:")
    print(df)
```

### Implementación Asíncrona

```python
from satellite_async import SatelliteImagesAsync
import asyncio

# Crear instancia asíncrona
municipio = "Iztapalapa"
fechas = ["01-01-24", "02-01-24"]
sat = SatelliteImagesAsync(municipio)

# Ejecutar procesamiento asíncrono
df = asyncio.run(sat.run(fechas))
print(df)
```

### Ejecutar desde línea de comandos

```bash
# Versión síncrona
cd satellite_sync
python main.py

# Versión asíncrona
cd satellite_async
python main.py
```

## 📊 Funcionalidades

### Procesamiento de Imágenes

- **Recorte automático**: Las imágenes se recortan automáticamente según las coordenadas del municipio
- **Normalización**: Procesamiento de bordes y completado de datos faltantes
- **Extracción de píxeles**: Obtención de valores de radianza por coordenada

### Análisis de Datos

- **Mediciones de radianza**: Extracción de valores de luminosidad nocturna
- **Estadísticas**: Cálculo de estadísticas descriptivas por fecha
- **Visualización**: Generación automática de gráficos y mapas

### Gestión de Datos

- **Descarga automática**: Obtención de archivos desde servidores de la NASA
- **Cache local**: Almacenamiento temporal de archivos descargados
- **Validación**: Verificación de integridad de datos con Pydantic

## 🔧 Configuración

### Parámetros principales

- **Municipio**: Nombre del municipio a procesar (ej: "Iztapalapa")
- **Fechas**: Lista de fechas en formato "DD-MM-YY"
- **Tile**: Identificador de tile satelital (ej: "h08v07")
- **Mostrar gráficos**: Opción para visualizar resultados

### Archivos de configuración

- `satellite_sync/config.py`: Configuración para versión síncrona
- `satellite_async/config.py`: Configuración para versión asíncrona

## 📈 Resultados

El sistema genera:

1. **DataFrame con mediciones**: Contiene valores de radianza por fecha
2. **Gráficos de visualización**: Mapas de calor y gráficos temporales
3. **Estadísticas**: Resúmenes estadísticos de los datos procesados

## 🛠️ Desarrollo

### Agregar nuevos municipios

1. Actualizar `Data/municipios_coordenadas_pixeles.json` con las coordenadas del nuevo municipio
2. Verificar que las coordenadas estén en el formato correcto

### Extender funcionalidades

- Los módulos están diseñados de forma modular para facilitar extensiones
- Usar los modelos Pydantic para validación de datos
- Seguir el patrón establecido en los procesadores existentes

## 📝 Notas

- Las imágenes VNP46A1 contienen datos de luminosidad nocturna
- El procesamiento puede tomar tiempo dependiendo del número de fechas
- Se recomienda usar la versión asíncrona para grandes volúmenes de datos
- Los archivos temporales se almacenan en el directorio `temp/`

## 🤝 Contribuciones

Para contribuir al proyecto:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👥 Autores

- Desarrollado para el trabajo terminal de ESCOM
- Basado en datos de la NASA VNP46A1

## 📞 Contacto

Para preguntas o soporte, por favor abrir un issue en el repositorio. 