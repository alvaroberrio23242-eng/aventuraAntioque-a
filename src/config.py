import pygame

pygame.init()

try:
    pygame.mixer.init()
except pygame.error as e:
    # En el navegador (pygbag), el contexto de audio puede estar
    # bloqueado hasta que el usuario interactúa (clic, tecla). Si esto
    # falla, seguimos sin sonido en vez de tumbar el juego entero.
    print(f"[AUDIO NO DISPONIBLE] {e}")

# Ventana
ANCHO, ALTO = 1400, 800
ventana = pygame.display.set_mode(
    (ANCHO, ALTO),
    pygame.RESIZABLE | pygame.SCALED
)
pygame.display.set_caption("Aventura Antioqueña")

FPS = 60
RELOJ = pygame.time.Clock()

# Colores base
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)

# Paleta vibrante inspirada en Antioquia (tema oscuro + acentos de color)
FONDO = (22, 24, 43)           # azul noche
FONDO_TARJETA = (33, 36, 62)   # un poco más claro, para tarjetas

AMARILLO = (255, 209, 102)     # oro / café
VERDE = (6, 214, 160)          # verde menta / biodiversidad
ROJO_CORAL = (239, 71, 111)    # rojo coral / energía paisa
AZUL = (17, 138, 178)          # azul montaña

ACENTOS = [AMARILLO, VERDE, ROJO_CORAL, AZUL]  # colores que ciclan en las opciones

# Fuentes
FONT_TITULO = pygame.font.Font(None, 90)
FONT_PREGUNTAS = pygame.font.Font(None, 52)
FONT_OPCION = pygame.font.Font(None, 40)
FONT_INFORMACION = pygame.font.Font(None, 36)

# Importamos las preguntas
from datos.preguntas import PREGUNTAS_DATA