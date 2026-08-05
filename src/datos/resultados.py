import json
import os

RUTA_RESULTADOS = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "resultados.json")
)


def cargar_resultados():
    """Lee los resultados guardados de partidas anteriores."""
    if not os.path.exists(RUTA_RESULTADOS):
        return []
    try:
        with open(RUTA_RESULTADOS, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    except (json.JSONDecodeError, OSError):
        return []


def guardar_resultado(nombre, correctas, incorrectas, tiempo_segundos, puntos):
    """Agrega el resultado de la partida actual y lo guarda en disco."""
    resultados = cargar_resultados()
    resultados.append({
        "nombre": nombre,
        "correctas": correctas,
        "incorrectas": incorrectas,
        "tiempo_segundos": round(tiempo_segundos, 1),
        "puntos": puntos,
    })
    with open(RUTA_RESULTADOS, "w", encoding="utf-8") as archivo:
        json.dump(resultados, archivo, ensure_ascii=False, indent=2)
    return resultados