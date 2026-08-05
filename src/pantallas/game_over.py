import pygame
import sys
import asyncio
from config import (
    ventana, ANCHO, ALTO, FONDO, BLANCO, AMARILLO,
    ROJO_CORAL, FONT_TITULO, FONT_PREGUNTAS, FONT_OPCION,
    FONT_INFORMACION, RELOJ, FPS
)
from utils.texto import dibujar_texto


async def pantalla_game_over(nombre, puntos, correctas, incorrectas, tiempo_total):
    """Se muestra cuando el jugador agota sus vidas antes de terminar
    los tres niveles."""
    ventana.fill(FONDO)

    dibujar_texto(
        ventana,
        'GAME OVER',
        FONT_TITULO,
        ROJO_CORAL,
        ANCHO // 2,
        110
    )

    dibujar_texto(
        ventana,
        f'{nombre}, se te acabaron las vidas',
        FONT_PREGUNTAS,
        BLANCO,
        ANCHO // 2,
        180
    )

    tarjeta = pygame.Rect(ANCHO // 2 - 300, 250, 600, 210)
    pygame.draw.rect(ventana, (35, 50, 75), tarjeta, border_radius=20)
    pygame.draw.rect(ventana, ROJO_CORAL, tarjeta, 3, border_radius=20)

    dibujar_texto(ventana, f'Puntaje: {puntos}', FONT_OPCION, BLANCO, ANCHO // 2, 305)
    dibujar_texto(ventana, f'Correctas: {correctas}', FONT_OPCION, BLANCO, ANCHO // 2, 355)
    dibujar_texto(ventana, f'Incorrectas: {incorrectas}', FONT_OPCION, BLANCO, ANCHO // 2, 405)
    dibujar_texto(ventana, f'Tiempo jugado: {int(tiempo_total)} s', FONT_OPCION, BLANCO, ANCHO // 2, 455)

    dibujar_texto(
        ventana,
        'Presiona cualquier tecla para continuar al ranking',
        FONT_INFORMACION,
        AMARILLO,
        ANCHO // 2,
        ALTO - 40
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