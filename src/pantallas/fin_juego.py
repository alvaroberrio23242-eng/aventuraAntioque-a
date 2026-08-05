import pygame
import sys
import asyncio

from config import (
    ventana,
    ANCHO,
    ALTO,
    FONDO,
    FONDO_TARJETA,
    BLANCO,
    AMARILLO,
    VERDE,
    ROJO_CORAL,
    FONT_TITULO,
    FONT_INFORMACION,
    FONT_OPCION,
    RELOJ,
    FPS
)

from utils.texto import dibujar_texto


async def fin_juego(nombre, puntos, correctas, incorrectas, tiempo_total, resultados):

    ventana.fill(FONDO)

    dibujar_texto(
        ventana,
        "RANKING DE JUGADORES",
        FONT_TITULO,
        ROJO_CORAL,
        ANCHO // 2,
        60
    )

    resumen = (
        f"{nombre} | "
        f"{puntos} pts | "
        f"{correctas} correctas | "
        f"{incorrectas} incorrectas | "
        f"{int(tiempo_total)} s"
    )

    dibujar_texto(
        ventana,
        resumen,
        FONT_INFORMACION,
        BLANCO,
        ANCHO // 2,
        115
    )

    tarjeta = pygame.Rect(
        ANCHO // 2 - 550,
        150,
        1100,
        ALTO - 220
    )

    pygame.draw.rect(
        ventana,
        FONDO_TARJETA,
        tarjeta,
        border_radius=20
    )

    encabezados = [
        "Nombre",
        "Correctas",
        "Incorrectas",
        "Tiempo",
        "Puntos"
    ]

    columnas = [
        tarjeta.left + 170,
        tarjeta.left + 430,
        tarjeta.left + 620,
        tarjeta.left + 820,
        tarjeta.left + 980
    ]

    for texto, x in zip(encabezados, columnas):
        dibujar_texto(
            ventana,
            texto,
            FONT_INFORMACION,
            VERDE,
            x,
            tarjeta.top + 40
        )

    ranking = sorted(
        resultados,
        key=lambda r: r["puntos"],
        reverse=True
    )

    y = tarjeta.top + 90

    for jugador in ranking[:8]:

        valores = [
            jugador["nombre"],
            str(jugador["correctas"]),
            str(jugador["incorrectas"]),
            f'{jugador["tiempo_segundos"]} s',
            str(jugador["puntos"])
        ]

        for texto, x in zip(valores, columnas):
            dibujar_texto(
                ventana,
                texto,
                FONT_INFORMACION,
                BLANCO,
                x,
                y
            )

        y += 45

    if len(ranking) == 0:
        dibujar_texto(
            ventana,
            "No hay resultados.",
            FONT_INFORMACION,
            BLANCO,
            ANCHO // 2,
            tarjeta.centery
        )

    dibujar_texto(
        ventana,
        "Presiona cualquier tecla para salir",
        FONT_INFORMACION,
        AMARILLO,
        ANCHO // 2,
        ALTO - 35
    )

    pygame.display.flip()

    esperando = True

    while esperando:
        RELOJ.tick(FPS)

        for evento in pygame.event.get():

            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:
                esperando = False
        await asyncio.sleep(0)