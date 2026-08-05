import pygame
import sys
import asyncio
from config import (
    ventana, ANCHO, ALTO, FONDO, BLANCO, AMARILLO,
    VERDE, FONT_TITULO, FONT_PREGUNTAS, FONT_OPCION,
    FONT_INFORMACION, RELOJ, FPS
)
from utils.texto import dibujar_texto, dibujar_texto_neon


async def mostrar_victoria(nombre, puntos, correctas, incorrectas, tiempo_total):
    precision = 0
    total = correctas + incorrectas
    if total > 0:
        precision = int((correctas / total) * 100)

    ventana.fill(FONDO)

    dibujar_texto(
        ventana,
        '¡FELICITACIONES!',
        FONT_TITULO,
        AMARILLO,
        ANCHO // 2,
        90
    )

    dibujar_texto(
        ventana,
        f'{nombre}, completaste la Aventura Antioqueña',
        FONT_PREGUNTAS,
        BLANCO,
        ANCHO // 2,
        160
    )

    tarjeta = pygame.Rect(ANCHO // 2 - 300, 230, 600, 260)
    pygame.draw.rect(ventana, (35, 50, 75), tarjeta, border_radius=20)
    pygame.draw.rect(ventana, VERDE, tarjeta, 3, border_radius=20)

    dibujar_texto(
        ventana,
        f'Puntaje: {puntos}',
        FONT_OPCION,
        BLANCO,
        ANCHO // 2,
        285
    )

    dibujar_texto(
        ventana,
        f'Correctas: {correctas}',
        FONT_OPCION,
        BLANCO,
        ANCHO // 2,
        335
    )

    dibujar_texto(
        ventana,
        f'Incorrectas: {incorrectas}',
        FONT_OPCION,
        BLANCO,
        ANCHO // 2,
        385
    )

    dibujar_texto(
        ventana,
        f'Precisión: {precision}%',
        FONT_OPCION,
        BLANCO,
        ANCHO // 2,
        435
    )

    dibujar_texto(
        ventana,
        f'Tiempo total: {int(tiempo_total)} s',
        FONT_OPCION,
        BLANCO,
        ANCHO // 2,
        485
    )

    titulo = '🏆 EXPLORADOR DE ANTIOQUIA 🏆'
    if precision >= 90:
        titulo = '👑 MAESTRO DE ANTIOQUIA 👑'
    elif precision >= 75:
        titulo = '🏆 EXPLORADOR DE ANTIOQUIA 🏆'
    else:
        titulo = '🧭 VIAJERO ANTIOQUEÑO 🧭'

    dibujar_texto(
        ventana,
        titulo,
        FONT_PREGUNTAS,
        AMARILLO,
        ANCHO // 2,
        560
    )

    # --- AGRADECIMIENTO A MEDELLÍN ---
    # Hay espacio libre entre el badge de arriba (y=560) y el mensaje
    # final de "presiona una tecla" (y=ALTO-40), asi que el agradecimiento
    # va justo en ese hueco, sin desplazar nada mas de la pantalla.
    dibujar_texto_neon(
        ventana,
        '¡GRACIAS, MEDELLÍN!',
        FONT_OPCION,
        VERDE,
        ANCHO // 2,
        620
    )

    dibujar_texto(
        ventana,
        'Este juego nació inspirado en tu gente, tu comida, tu',
        FONT_INFORMACION,
        BLANCO,
        ANCHO // 2,
        660
    )

    dibujar_texto(
        ventana,
        'arquitectura y tus montañas. Gracias por la oportunidad.',
        FONT_INFORMACION,
        BLANCO,
        ANCHO // 2,
        690
    )

    dibujar_texto(
        ventana,
        'Presiona cualquier tecla para continuar al ranking',
        FONT_INFORMACION,
        BLANCO,
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