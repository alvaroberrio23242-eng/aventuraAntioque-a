import pygame
import sys
import asyncio
from config import ventana, ANCHO, ALTO, FONDO, VERDE, ROJO_CORAL, RELOJ, FPS, FONT_TITULO
from utils.texto import dibujar_texto


async def mostrar_feedback(correcto):
    """Muestra brevemente un mensaje de correcto o incorrecto."""
    color = VERDE if correcto else ROJO_CORAL
    mensaje = "¡Correcto!" if correcto else "Incorrecto"
    duracion_ms = 800
    inicio = pygame.time.get_ticks()

    while pygame.time.get_ticks() - inicio < duracion_ms:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                return

        overlay = pygame.Surface((ANCHO, ALTO))
        overlay.fill(FONDO)
        ventana.blit(overlay, (0, 0))
        dibujar_texto(ventana, mensaje, FONT_TITULO, color, ANCHO // 2, ALTO // 2)
        pygame.display.flip()
        RELOJ.tick(FPS)
        await asyncio.sleep(0)