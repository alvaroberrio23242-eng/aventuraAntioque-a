import pygame
import sys
import asyncio

from config import (
    ventana, ANCHO, ALTO, NEGRO, BLANCO,
    AMARILLO, VERDE, ROJO_CORAL, FONT_TITULO, FONT_OPCION, FONT_INFORMACION,
    RELOJ, FPS
)
from utils.texto import dibujar_texto


async def pantalla_pausa():
    """Muestra el menú de pausa sobre el juego actual (sin borrar lo que
    ya estaba dibujado en pantalla). Bloquea hasta que el jugador elige
    continuar o salir. Devuelve "continuar" o "salir"."""

    # Capturamos lo que ya había en pantalla para poder mantenerlo de
    # fondo (congelado) detrás del overlay de pausa.
    fondo_congelado = ventana.copy()

    btn_continuar = pygame.Rect(ANCHO // 2 - 150, ALTO // 2 - 20, 300, 60)
    btn_salir = pygame.Rect(ANCHO // 2 - 150, ALTO // 2 + 60, 300, 60)

    resultado = "continuar"
    esperando = True

    while esperando:
        RELOJ.tick(FPS)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                return "salir"

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    resultado = "continuar"
                    esperando = False

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if btn_continuar.collidepoint(evento.pos):
                    resultado = "continuar"
                    esperando = False
                elif btn_salir.collidepoint(evento.pos):
                    resultado = "salir"
                    esperando = False

        ventana.blit(fondo_congelado, (0, 0))

        overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        ventana.blit(overlay, (0, 0))

        dibujar_texto(ventana, "PAUSA", FONT_TITULO, AMARILLO, ANCHO // 2, ALTO // 2 - 100)

        pygame.draw.rect(ventana, VERDE, btn_continuar, border_radius=15)
        dibujar_texto(ventana, "Continuar", FONT_OPCION, NEGRO, btn_continuar.centerx, btn_continuar.centery)

        pygame.draw.rect(ventana, ROJO_CORAL, btn_salir, border_radius=15)
        dibujar_texto(ventana, "Salir del juego", FONT_OPCION, NEGRO, btn_salir.centerx, btn_salir.centery)

        dibujar_texto(ventana, "Presiona ESC para continuar", FONT_INFORMACION, BLANCO, ANCHO // 2, ALTO // 2 + 150)

        pygame.display.flip()
        await asyncio.sleep(0)

    return resultado