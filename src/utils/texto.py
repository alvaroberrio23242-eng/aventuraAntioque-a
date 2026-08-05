import math
import random

import pygame


def dibujar_texto(ventana, texto, font, color, x, y):
    """Dibuja texto centrado en (x, y) sobre la ventana dada."""
    superficie = font.render(texto, True, color)
    rect = superficie.get_rect(center=(x, y))
    ventana.blit(superficie, rect)


# Estado del parpadeo de neon, guardado por texto (por si en el futuro
# hay mas de un titulo neon en pantalla a la vez, cada uno parpadea de
# forma independiente en vez de todos al mismo tiempo).
_ESTADO_NEON = {}


def dibujar_texto_neon(ventana, texto, font, color, x, y, color_resplandor=None):
    """Dibuja un texto con efecto de letrero de neon: resplandor pulsante
    alrededor de las letras y parpadeos ocasionales (como un neon real
    que de vez en cuando "titila"). Pensado para titulos, no para texto
    que cambia seguido (cachea la superficie renderizada por texto)."""
    if color_resplandor is None:
        color_resplandor = color

    ahora = pygame.time.get_ticks()
    estado = _ESTADO_NEON.setdefault(texto, {"prox_flicker": 0, "flicker_hasta": 0})

    # Parpadeo aleatorio ocasional, como una falla electrica del neon
    if ahora >= estado["prox_flicker"]:
        estado["flicker_hasta"] = ahora + random.randint(50, 130)
        estado["prox_flicker"] = ahora + random.randint(2200, 4800)

    en_flicker = ahora < estado["flicker_hasta"]

    # Pulso suave de brillo ("respiracion" del neon) entre 0.75 y 1.0,
    # que cae a un valor bajo durante el parpadeo
    pulso = 0.75 + 0.25 * math.sin(ahora / 350.0)
    intensidad = 0.2 if en_flicker else pulso

    # --- Resplandor: varias copias translucidas del texto, desplazadas
    # alrededor del texto principal, para simular un halo de luz ---
    resplandor = font.render(texto, True, color_resplandor)
    resplandor.set_alpha(max(0, min(255, int(70 * intensidad))))
    for dx, dy in ((-4, 0), (4, 0), (0, -4), (0, 4), (-3, -3), (3, 3), (-3, 3), (3, -3)):
        rect = resplandor.get_rect(center=(x + dx, y + dy))
        ventana.blit(resplandor, rect)

    # --- Texto nitido encima, tambien modulado por el pulso ---
    principal = font.render(texto, True, color)
    principal.set_alpha(max(0, min(255, int(255 * intensidad))))
    rect = principal.get_rect(center=(x, y))
    ventana.blit(principal, rect)