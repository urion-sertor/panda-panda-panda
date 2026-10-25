"""Módulo main.py
Menú interactivo y punto de entrada de la aplicación.
MP0486 · RA1 · Práctica Pandas
"""

import sys
from datos import preparar_datos, guardar_informes, mostrar_grafico

# Asegurar codificación UTF-8 para visualización limpia en consolas de Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main() -> None:
    """Bucle principal de la aplicación con menú interactivo."""
    while True:
        print("\n" + "=" * 40)
        print(" Matching alumnos y notas con Pandas")
        print("=" * 40)
        print("1. Generar informes CSV y JSON")
        print("2. Mostrar gráfico de medias")
        print("0. Salir")
        print("=" * 40)

        opcion = input("Elige una opción: ").strip()

        if opcion == "1":
            # Opción 1: Prepara los datos, guarda ambos formatos y muestra el informe
            informe = preparar_datos()
            if informe is not None:
                guardar_informes(informe)
        elif opcion == "2":
            # Opción 2: Prepara los datos, guarda el PNG y muestra la figura
            informe = preparar_datos()
            if informe is not None:
                mostrar_grafico(informe)
        elif opcion == "0":
            print("\nSaliendo del programa. ¡Hasta pronto!")
            sys.exit(0)
        else:
            print("\nOpción no válida. Por favor, introduce 1, 2 o 0.")


if __name__ == "__main__":
    main()
