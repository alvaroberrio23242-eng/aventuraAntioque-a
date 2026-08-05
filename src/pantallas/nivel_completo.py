import pygame
import sys
import asyncio
from config import ventana, ANCHO, ALTO, BLANCO, FONT_TITULO, FONT_PREGUNTAS, RELOJ, FPS
from utils.texto import dibujar_texto
from pantallas.juego import precargar_video_nivel

MENSAJES_NIVEL = [
    "",
    "Has ganado el nivel gastronómico",
    "Has ganado el nivel de arquitectura",
    "Has ganado el nivel de biodiversidad",
]


async def nivel_completo(nivel_completado):
    """Muestra la pantalla de finalización de nivel.

    Antes esto precargaba el video del siguiente nivel en un hilo
    aparte (threading.Thread). Los navegadores (via pygbag) no
    soportan hilos reales de Python, asi que ahora se precarga de
    forma directa: como esta pantalla ya requiere que el jugador
    presione una tecla para continuar, ese tiempo de lectura sigue
    siendo "gratis" aunque la carga ya no ocurra en paralelo.
    """
    siguiente_nivel = nivel_completado + 1
    precargar_video_nivel(siguiente_nivel)

    ventana.fill((0, 0, 0))
    dibujar_texto(ventana, "¡Felicitaciones!", FONT_TITULO, BLANCO, ANCHO // 2, ALTO // 2 - 50)
    dibujar_texto(ventana, MENSAJES_NIVEL[nivel_completado], FONT_PREGUNTAS, BLANCO, ANCHO // 2, ALTO // 2 + 50)
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