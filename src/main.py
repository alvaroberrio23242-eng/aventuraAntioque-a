import sys
import os
import json
import random
import asyncio

DIR_SRC = os.path.dirname(os.path.abspath(__file__))
if DIR_SRC not in sys.path:
    sys.path.insert(0, DIR_SRC)

import pygame
from config import PREGUNTAS_DATA
from pantallas.bienvenida import pantalla_bienvenida
from pantallas.instrucciones import mostrar_instrucciones
from pantallas.juego import jugar_pregunta
from pantallas.nivel_completo import nivel_completo
from pantallas.victoria import mostrar_victoria
from pantallas.fin_juego import fin_juego
from pantallas.game_over import pantalla_game_over
from utils import musica

DIR_RAIZ = os.path.dirname(DIR_SRC)
RUTA_RANKING = os.path.join(DIR_RAIZ, "ranking.json")
TIEMPO_POR_PREGUNTA = 60
PUNTOS_POR_ACIERTO = 10
PENALIZACION_INCORRECTA = 5
VIDAS_INICIALES = 3


def cargar_ranking():
    if os.path.exists(RUTA_RANKING):
        try:
            with open(RUTA_RANKING, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def guardar_ranking(ranking):
    try:
        with open(RUTA_RANKING, "w", encoding="utf-8") as f:
            json.dump(ranking, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"No se pudo guardar el ranking: {e}")


async def main():
    datos_jugador = await pantalla_bienvenida()
    genero_elegido = datos_jugador.get("genero", "mujer")
    nombre_jugador = datos_jugador.get("nombre", "Aventurero")

    await mostrar_instrucciones()

    nivel_actual = 1
    total_niveles = len(PREGUNTAS_DATA["tema"])
    puntos = 0
    correctas = 0
    incorrectas = 0
    tiempo_total = 0.0
    vidas = VIDAS_INICIALES
    sin_vidas = False

    while nivel_actual <= total_niveles:
        preguntas_nivel = PREGUNTAS_DATA["tema"][nivel_actual - 1]["pregunta"]

        # Orden aleatorio de las preguntas de este nivel, para que
        # rejugar no sea siempre la misma secuencia memorizable.
        orden_preguntas = list(range(len(preguntas_nivel)))
        random.shuffle(orden_preguntas)

        for pregunta_idx in orden_preguntas:
            es_correcta, tiempo_usado = await jugar_pregunta(
                PREGUNTAS_DATA,
                nivel_actual=nivel_actual,
                actual_pregunta=pregunta_idx,
                puntos=puntos,
                tiempo=TIEMPO_POR_PREGUNTA,
                genero=genero_elegido,
                vidas=vidas
            )

            tiempo_total += tiempo_usado

            if es_correcta:
                puntos += PUNTOS_POR_ACIERTO
                correctas += 1
            else:
                incorrectas += 1
                puntos = max(0, puntos - PENALIZACION_INCORRECTA)
                vidas -= 1
                if vidas <= 0:
                    sin_vidas = True
                    break

        if sin_vidas:
            break

        if nivel_actual < total_niveles:
            await nivel_completo(nivel_actual)

        nivel_actual += 1

    # Pantalla final: game over si se acabaron las vidas, victoria si
    # completó los tres niveles
    musica.detener()
    if sin_vidas:
        await pantalla_game_over(nombre_jugador, puntos, correctas, incorrectas, tiempo_total)
    else:
        await mostrar_victoria(nombre_jugador, puntos, correctas, incorrectas, tiempo_total)

    # Guardar y mostrar ranking persistente entre partidas
    ranking = cargar_ranking()
    ranking.append({
        "nombre": nombre_jugador,
        "correctas": correctas,
        "incorrectas": incorrectas,
        "tiempo_segundos": int(tiempo_total),
        "puntos": puntos
    })
    guardar_ranking(ranking)

    await fin_juego(nombre_jugador, puntos, correctas, incorrectas, tiempo_total, ranking)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    asyncio.run(main())