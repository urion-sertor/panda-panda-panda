"""Módulo datos.py
Lógica de procesamiento de datos con Pandas y visualización con Matplotlib.
MP0486 · RA1 · Práctica Pandas
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# Definición de rutas con pathlib respecto a la carpeta del script
BASE_DIR = Path(__file__).resolve().parent
RUTA_ENTRADA = BASE_DIR / "datos" / "entrada"
RUTA_SALIDA = BASE_DIR / "datos" / "salida"
RUTA_ALUMNOS = RUTA_ENTRADA / "alumnos.csv"
RUTA_NOTAS = RUTA_ENTRADA / "notas.csv"


def validar_archivo_csv(ruta: Path, columnas_esperadas: list[str]) -> pd.DataFrame | None:
    """Comprueba que el CSV exista, no esté vacío y contenga las columnas requeridas."""
    if not ruta.is_file():
        print(f"Error: No se encuentra el archivo '{ruta.name}'. Revisa {ruta.name}")
        return None

    try:
        # Se lee id_alumno como str para preservar ceros a la izquierda (ej. '001')
        df = pd.read_csv(ruta, sep=";", encoding="utf-8", dtype={"id_alumno": str})
    except Exception as e:
        print(f"Error al leer '{ruta.name}': {e}. Revisa {ruta.name}")
        return None

    if df.empty:
        print(f"Error: El archivo '{ruta.name}' está vacío. Revisa {ruta.name}")
        return None

    # Normalizar nombres de columnas eliminando posibles espacios accidentales
    df.columns = df.columns.str.strip()

    faltantes = [col for col in columnas_esperadas if col not in df.columns]
    if faltantes:
        print(f"Error: Columnas faltantes en '{ruta.name}': {faltantes}. Revisa {ruta.name}")
        return None

    # Limpiar cadenas de texto en id_alumno
    df["id_alumno"] = df["id_alumno"].astype(str).str.strip()
    return df


def preparar_datos() -> pd.DataFrame | None:
    """Lee, limpia, cruza y calcula el total y media de las notas de los alumnos.

    Devuelve un DataFrame con el informe consolidado o None si ocurre un error de validación.
    """
    # 1. Leer y validar archivos de entrada
    df_alumnos_raw = validar_archivo_csv(RUTA_ALUMNOS, ["id_alumno", "nombre"])
    if df_alumnos_raw is None:
        return None

    df_notas_raw = validar_archivo_csv(RUTA_NOTAS, ["id_alumno", "nota1", "nota2", "nota3"])
    if df_notas_raw is None:
        return None

    # 2. Limpiar
    # Eliminar duplicados en alumnos por id_alumno
    total_inicial_alumnos = len(df_alumnos_raw)
    df_alumnos = df_alumnos_raw.drop_duplicates(subset=["id_alumno"]).copy()
    duplicados_eliminados = total_inicial_alumnos - len(df_alumnos)

    # Validar que notas.csv tenga una única fila por identificador
    if df_notas_raw["id_alumno"].duplicated().any():
        print("Aviso: Existen filas duplicadas en notas.csv. Revisa notas.csv")
        # Conservamos la primera ocurrencia por consistencia
        df_notas = df_notas_raw.drop_duplicates(subset=["id_alumno"]).copy()
    else:
        df_notas = df_notas_raw.copy()

    # Convertir notas a numérico con errores forzados a NaN (coerce)
    cols_notas = ["nota1", "nota2", "nota3"]
    for col in cols_notas:
        df_notas[col] = pd.to_numeric(df_notas[col], errors="coerce")
        # Las notas fuera del rango [0.0, 10.0] quedan ausentes (NaN); no se sustituyen por cero
        df_notas.loc[(df_notas[col] < 0) | (df_notas[col] > 10), col] = float("nan")

    # 3. Identificar discrepancias antes o durante el cruce
    ids_alumnos = set(df_alumnos["id_alumno"])
    ids_notas = set(df_notas["id_alumno"])

    sin_notas = sorted(list(ids_alumnos - ids_notas))
    sin_alumno = sorted(list(ids_notas - ids_alumnos))

    # Cruzar: Conserva todos los alumnos (how="left"). Las notas sin alumno quedan fuera.
    informe = pd.merge(df_alumnos, df_notas, on="id_alumno", how="left")

    # Validación de coincidencias
    if informe.empty:
        print("Aviso: El cruce de datos no generó resultados.")
        return None

    # Comprobar que haya al menos alguna nota válida en el informe general
    if informe[cols_notas].notna().sum().sum() == 0:
        print("Aviso: No se encontraron notas válidas en el informe.")
        return None

    # 4. Calcular Total y Media
    # min_count=3 exige las 3 notas válidas; si falta alguna, la suma devuelve NaN
    informe["total"] = informe[cols_notas].sum(axis=1, min_count=3)
    informe["media"] = (informe["total"] / 3).round(2)

    # Ordenar por id_alumno
    informe = informe.sort_values("id_alumno").reset_index(drop=True)

    # 5. Salida por consola formateada
    print(f"\nDuplicados eliminados: {duplicados_eliminados}")
    print(f"Alumnos sin notas: {', '.join(sin_notas) if sin_notas else 'Ninguno'}")
    print(f"Notas sin alumno: {', '.join(sin_alumno) if sin_alumno else 'Ninguno'}\n")

    # Preparar vista formateada para la consola sustituyendo ausentes por 'N/D'
    vista = informe.copy()
    for col in cols_notas + ["total"]:
        vista[col] = vista[col].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "N/D")
    vista["media"] = vista["media"].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/D")

    print(vista.to_string(index=False))

    total_alumnos = len(informe)
    completos = informe["media"].notna().sum()
    pendientes = total_alumnos - completos
    print(f"\nAlumnos: {total_alumnos} | Completos: {completos} | Pendientes: {pendientes}\n")

    return informe


def guardar_informes(informe: pd.DataFrame) -> None:
    """Genera informe_notas.csv e informe_notas.json en datos/salida/ y comprueba su integridad."""
    if informe is None or informe.empty:
        print("Aviso: No hay datos para guardar.")
        return

    # Crear la carpeta de salida si no existe
    RUTA_SALIDA.mkdir(parents=True, exist_ok=True)

    ruta_csv = RUTA_SALIDA / "informe_notas.csv"
    ruta_json = RUTA_SALIDA / "informe_notas.json"

    # Exportar a CSV (UTF-8, separador ;) y JSON (records, legible sin escapar caracteres UTF-8)
    informe.to_csv(ruta_csv, index=False, sep=";", encoding="utf-8")
    informe.to_json(ruta_json, orient="records", force_ascii=False, indent=2)

    # Releer y comprobar integridad de ambos archivos
    try:
        df_csv = pd.read_csv(ruta_csv, sep=";", encoding="utf-8", dtype={"id_alumno": str})
        df_json = pd.read_json(ruta_json, dtype={"id_alumno": str})

        # Comprobación de filas
        coincide_filas = len(df_csv) == len(informe) and len(df_json) == len(informe)
        # Comprobación de columnas
        coincide_columnas = list(df_csv.columns) == list(informe.columns) and list(df_json.columns) == list(informe.columns)
        # Comprobación de identificadores
        coincide_ids = list(df_csv["id_alumno"]) == list(informe["id_alumno"]) and list(df_json["id_alumno"]) == list(informe["id_alumno"])

        if coincide_filas and coincide_columnas and coincide_ids:
            print("CSV y JSON guardados y comprobados en datos/salida.")
        else:
            print("Aviso: La verificación de integridad de los archivos guardados detectó discrepancias.")
    except Exception as e:
        print(f"Error al verificar los archivos guardados: {e}")


def mostrar_grafico(informe: pd.DataFrame) -> None:
    """Genera un gráfico de barras con la media de las actividades para alumnos con notas completas."""
    if informe is None or informe.empty:
        print("Aviso: No hay datos para generar el gráfico.")
        return

    cols_notas = ["nota1", "nota2", "nota3"]
    # Selecciona solo alumnos con las tres notas válidas
    completos = informe[informe[cols_notas].notna().all(axis=1)]

    if len(completos) == 0:
        print("No hay alumnos con las tres notas válidas para crear el gráfico.")
        return

    # Calcular la media de cada actividad
    medias = completos[cols_notas].mean()

    # Configuración de gráfico con Matplotlib
    plt.figure(figsize=(7, 5))
    etiquetas = ["Actividad 1", "Actividad 2", "Actividad 3"]
    barras = plt.bar(etiquetas, medias, width=0.55, color="#1f77b4", edgecolor="#0e4b75")
    plt.bar_label(barras, fmt="%.2f", padding=3)

    plt.ylim(0, 10)
    plt.title(f"Media por actividad ({len(completos)} alumnos)", fontsize=13, pad=15)
    plt.ylabel("Nota media", fontsize=11)
    plt.grid(axis="y", linestyle="--", alpha=0.5)

    # Asegurar carpeta de salida y guardar gráfico
    RUTA_SALIDA.mkdir(parents=True, exist_ok=True)
    ruta_png = RUTA_SALIDA / "medias_actividades.png"
    plt.savefig(ruta_png, dpi=300, bbox_inches="tight")
    print(f"Gráfico guardado en {ruta_png}")

    # Mostrar la figura interactiva (se bloquea hasta que el usuario cierra la ventana)
    plt.show()
    plt.close()
