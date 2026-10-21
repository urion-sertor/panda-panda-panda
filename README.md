# Matching alumnos y notas con Pandas

Proyecto de procesamiento y cruce de datos académicos utilizando **Pandas** y visualización estadística con **Matplotlib** (Módulo MP0486 · RA1).

## Requisitos e Instalación

1. Crear y activar el entorno virtual (opcional pero recomendado):
   ```bash
   python -m venv .venv
   # En Windows:
   .venv\Scripts\activate
   # En Linux / Mac:
   source .venv/bin/activate
   ```
2. Instalar las dependencias del proyecto:
   ```bash
   pip install -r requirements.txt
   ```

## Ejecución

Para iniciar el menú interactivo, ejecuta:
```bash
python main.py
```

Opciones disponibles en el menú:
- **Opción 1:** Prepara los datos, muestra el informe detallado en consola y exporta los archivos `informe_notas.csv` e `informe_notas.json` a la carpeta `datos/salida/`.
- **Opción 2:** Calcula las medias por actividad de los alumnos con calificaciones completas, guarda la imagen `medias_actividades.png` y muestra la figura.
- **Opción 0:** Sale de la aplicación.

## Sobre el Gráfico de Medias

El gráfico de barras refleja el rendimiento medio por actividad únicamente para aquellos estudiantes que cuentan con las tres calificaciones completas y válidas. Permite comparar visualmente la dificultad relativa de cada actividad, observándose una tendencia ascendente en las puntuaciones medias de la Actividad 1 a la Actividad 3.
