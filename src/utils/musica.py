"""
Control centralizado de la música del juego.
"""

import pygame

_musica_activada = True
_pista_actual = None


def activar():
    """Activa la música."""
    global _musica_activada
    _musica_activada = True
    try:
        pygame.mixer.music.unpause()
    except pygame.error:
        pass


def desactivar():
    """Desactiva la música."""
    global _musica_activada
    _musica_activada = False
    try:
        pygame.mixer.music.pause()
    except pygame.error:
        pass


def alternar():
    """
    Activa o desactiva la música.
    Devuelve True si quedó activada.
    """
    if _musica_activada:
        desactivar()
    else:
        activar()

    return _musica_activada


def esta_activada():
    return _musica_activada


def reproducir(ruta_musica, volumen=0.35, loop=True):
    """
    Reproduce música de fondo.
    No reinicia la canción si ya está sonando.
    """

    global _pista_actual

    if not _musica_activada:
        return

    if (
        _pista_actual == ruta_musica
        and pygame.mixer.music.get_busy()
    ):
        return

    try:
        pygame.mixer.music.load(ruta_musica)
        pygame.mixer.music.set_volume(volumen)
        pygame.mixer.music.play(-1 if loop else 0)
        _pista_actual = ruta_musica

    except pygame.error:
        _pista_actual = None


def detener(fade_ms=500):
    global _pista_actual

    try:
        pygame.mixer.music.fadeout(fade_ms)
    except pygame.error:
        pass

    _pista_actual = None


def pausar():
    try:
        pygame.mixer.music.pause()
    except pygame.error:
        pass


def reanudar():
    try:
        pygame.mixer.music.unpause()
    except pygame.error:
        pass