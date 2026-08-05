import pygame
import sys
import os
import asyncio

DIR_ACTUAL = os.path.dirname(os.path.abspath(__file__))
DIR_SRC = os.path.dirname(DIR_ACTUAL)
DIR_RAIZ = os.path.dirname(DIR_SRC)

if DIR_SRC not in sys.path:
    sys.path.insert(0, DIR_SRC)

from config import (
    ventana, ANCHO, ALTO, FONDO, FONDO_TARJETA, BLANCO,
    AMARILLO, VERDE, FONT_TITULO, FONT_INFORMACION, RELOJ, FPS
)
from utils.texto import dibujar_texto
from utils.video_background import obtener_video
from utils import musica


async def mostrar_instrucciones():
    """Muestra las instrucciones del juego."""
    ruta_frames = os.path.join(DIR_RAIZ, "assets", "videos", "menu_guatape_frames")
    if not os.path.exists(ruta_frames):
        ruta_frames = os.path.join(DIR_RAIZ, "assets", "videos", "menu_medellin_frames")

    bg = obtener_video(ruta_frames, (ANCHO, ALTO)) if os.path.exists(ruta_frames) else None

    ruta_musica = os.path.join(DIR_RAIZ, "assets", "music", "menu.ogg")
    musica.reproducir(ruta_musica, volumen=0.4)

    instrucciones = [
        "1. Responde correctamente a las preguntas.",
        "2. Cada nivel tiene 10 preguntas.",
        "3. La dificultad aumenta con cada nivel.",
        "4. Ganas 10 puntos por cada respuesta correcta.",
        "5. Tienes 60 segundos por pregunta antes de que se acabe el tiempo.",
        "6. Salta sobre la tarjeta con la respuesta correcta para elegirla.",
    ]

    alto_tarjeta = len(instrucciones) * 34 + 40
    tarjeta = pygame.Rect(ANCHO // 2 - 500, (ALTO - alto_tarjeta) // 2, 1000, alto_tarjeta)

    esperando = True
    while esperando:
        dt = RELOJ.tick(FPS) / 1000.0

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                esperando = False

        # --- Fondo: video en loop, o color sólido de respaldo ---
        if bg:
            bg.dibujar(ventana, dt)
        else:
            ventana.fill(FONDO)

        # --- Overlay semitransparente para legibilidad ---
        overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        overlay.fill((*FONDO, 140))
        ventana.blit(overlay, (0, 0))

        dibujar_texto(ventana, "Instrucciones", FONT_TITULO, AMARILLO, ANCHO // 2, 60)

        pygame.draw.rect(ventana, FONDO_TARJETA, tarjeta, border_radius=20)
        for i, linea in enumerate(instrucciones):
            dibujar_texto(ventana, linea, FONT_INFORMACION, BLANCO, ANCHO // 2, tarjeta.top + 40 + i * 34)

        dibujar_texto(ventana, "Presiona cualquier tecla para continuar", FONT_INFORMACION, VERDE, ANCHO // 2, ALTO - 50)

        pygame.display.flip()
        await asyncio.sleep(0)

    # No hace falta bg.cerrar(): al usar obtener_video() el objeto queda
    # en la cache compartida (por si otra pantalla vuelve a pedir el
    # mismo video) y sus frames ya viven en memoria como Surfaces, sin
    # ningun archivo abierto que liberar.