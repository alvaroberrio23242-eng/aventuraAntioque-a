import os
import sys
import asyncio
import pygame

DIR_ACTUAL = os.path.dirname(os.path.abspath(__file__))
DIR_SRC = os.path.dirname(DIR_ACTUAL)
DIR_RAIZ = os.path.dirname(DIR_SRC)

for ruta in [DIR_RAIZ, DIR_SRC]:
    if ruta not in sys.path:
        sys.path.insert(0, ruta)

from config import (
    ventana, ANCHO, ALTO, NEGRO, AMARILLO, BLANCO, VERDE, AZUL, ROJO_CORAL,
    FONDO_TARJETA, FONT_TITULO, FONT_OPCION, FONT_INFORMACION, RELOJ, FPS
)
from utils.texto import dibujar_texto, dibujar_texto_neon
from utils.video_background import obtener_video
from utils import musica

TEXTOS = {
    "es": {
        "titulo": "AVENTURA ANTIOQUEÑA",
        "nombre": "Nombre:",
        "edad": "Edad:",
        "ciudad": "Ciudad:",
        "mujer": "Mujer",
        "hombre": "Hombre",
        "jugar": "¡JUGAR!",
        "aviso_genero": "Elige un personaje para continuar",
        "boton_idioma": "EN",
    },
    "en": {
        "titulo": "ANTIOQUIA ADVENTURE",
        "nombre": "Name:",
        "edad": "Age:",
        "ciudad": "City:",
        "mujer": "Woman",
        "hombre": "Man",
        "jugar": "PLAY!",
        "aviso_genero": "Choose a character to continue",
        "boton_idioma": "ES",
    },
}


async def pantalla_bienvenida():
    # Rutas absolutas del video (no dependen de la carpeta desde donde ejecutes)
    ruta_frames = os.path.join(
        DIR_RAIZ,
        "assets",
        "videos",
        "menu_guatape_frames"
    )

    if not os.path.exists(ruta_frames):
        ruta_frames = os.path.join(
            DIR_RAIZ,
            "assets",
            "videos",
            "menu_medellin_frames"
        )

    # --- PANTALLA DE CARGA ---
    # obtener_video() lee y escala TODOS los frames PNG antes de devolver
    # el objeto (puede tardar varios segundos la primera vez). Sin esto,
    # esos segundos se ven como pantalla negra; con esto, al menos se ve
    # un mensaje mientras carga.
    ventana.fill((20, 30, 50))
    dibujar_texto(ventana, "Cargando...", FONT_TITULO, AMARILLO, ANCHO // 2, ALTO // 2)
    pygame.display.flip()

    video_bg = None

    if os.path.exists(ruta_frames):
        video_bg = obtener_video(ruta_frames, (ANCHO, ALTO))

    ruta_musica = os.path.join(DIR_RAIZ, "assets", "music", "menu.ogg")
    musica.reproducir(ruta_musica, volumen=0.4)

    campos = {"nombre": "", "edad": "", "ciudad": ""}
    campo_activo = "nombre"
    genero = None  # obligatorio: no hay valor por defecto, el jugador debe elegirlo
    idioma = "es"
    mostrar_aviso = False

    rect_nombre = pygame.Rect(ANCHO // 2 - 160, 210, 320, 45)
    rect_edad   = pygame.Rect(ANCHO // 2 - 160, 270, 320, 45)
    rect_ciudad = pygame.Rect(ANCHO // 2 - 160, 330, 320, 45)

    btn_mujer  = pygame.Rect(ANCHO // 2 - 220, 400, 200, 55)
    btn_hombre = pygame.Rect(ANCHO // 2 + 20,  400, 200, 55)
    btn_jugar  = pygame.Rect(ANCHO // 2 - 100, 475, 200, 60)
    btn_idioma = pygame.Rect(ANCHO - 130, 20, 100, 40)

    esperando = True
    while esperando:
        dt = RELOJ.tick(FPS) / 1000.0

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                pos = evento.pos
                if rect_nombre.collidepoint(pos):
                    campo_activo = "nombre"
                elif rect_edad.collidepoint(pos):
                    campo_activo = "edad"
                elif rect_ciudad.collidepoint(pos):
                    campo_activo = "ciudad"
                elif btn_mujer.collidepoint(pos):
                    genero = "mujer"
                    mostrar_aviso = False
                elif btn_hombre.collidepoint(pos):
                    genero = "hombre"
                    mostrar_aviso = False
                elif btn_idioma.collidepoint(pos):
                    idioma = "en" if idioma == "es" else "es"
                elif btn_jugar.collidepoint(pos):
                    if genero is None:
                        mostrar_aviso = True
                    else:
                        esperando = False

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_TAB:
                    orden = ["nombre", "edad", "ciudad"]
                    campo_activo = orden[(orden.index(campo_activo) + 1) % 3]
                elif evento.key == pygame.K_RETURN:
                    if genero is None:
                        mostrar_aviso = True
                    else:
                        esperando = False
                elif evento.key == pygame.K_BACKSPACE:
                    campos[campo_activo] = campos[campo_activo][:-1]
                else:
                    if campo_activo == "edad":
                        if evento.unicode.isdigit():
                            posible_edad = campos["edad"] + evento.unicode
                            # Limite razonable: 1 a 120. No dejamos que el
                            # numero escrito supere eso mientras se teclea.
                            if len(posible_edad) <= 3 and int(posible_edad) <= 120:
                                campos["edad"] = posible_edad
                    else:
                        if len(campos[campo_activo]) < 20 and evento.unicode.isprintable():
                            campos[campo_activo] += evento.unicode

        # --- FONDO ---
        if video_bg:
            video_bg.dibujar(ventana, dt)
        else:
            ventana.fill((20, 30, 50))

        overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        ventana.blit(overlay, (0, 0))

        textos = TEXTOS[idioma]

        # --- TÍTULO (efecto neon parpadeante) ---
        dibujar_texto_neon(ventana, textos["titulo"], FONT_TITULO, AMARILLO, ANCHO // 2, 150)

        # --- BOTÓN DE IDIOMA ---
        pygame.draw.rect(ventana, FONDO_TARJETA, btn_idioma, border_radius=10)
        pygame.draw.rect(ventana, AZUL, btn_idioma, 2, border_radius=10)
        dibujar_texto(ventana, textos["boton_idioma"], FONT_INFORMACION, BLANCO, btn_idioma.centerx, btn_idioma.centery)

        # --- CAMPOS DE TEXTO (opcionales) ---
        for etiqueta, rect, clave in [
            (textos["nombre"], rect_nombre, "nombre"),
            (textos["edad"], rect_edad, "edad"),
            (textos["ciudad"], rect_ciudad, "ciudad"),
        ]:
            dibujar_texto(ventana, etiqueta, FONT_INFORMACION, BLANCO, rect.x - 70, rect.centery)
            pygame.draw.rect(ventana, FONDO_TARJETA, rect, border_radius=10)
            color_borde = VERDE if campo_activo == clave else BLANCO
            pygame.draw.rect(ventana, color_borde, rect, 3, border_radius=10)
            dibujar_texto(ventana, campos[clave], FONT_INFORMACION, BLANCO, rect.x + 12, rect.centery)

        # --- SELECCIÓN DE PERSONAJE (obligatoria) ---
        col_m = VERDE if genero == "mujer" else FONDO_TARJETA
        borde_m = BLANCO if genero == "mujer" else (ROJO_CORAL if mostrar_aviso else AZUL)
        pygame.draw.rect(ventana, col_m, btn_mujer, border_radius=12)
        pygame.draw.rect(ventana, borde_m, btn_mujer, 3, border_radius=12)
        dibujar_texto(ventana, textos["mujer"], FONT_INFORMACION, BLANCO, btn_mujer.centerx, btn_mujer.centery)

        col_h = VERDE if genero == "hombre" else FONDO_TARJETA
        borde_h = BLANCO if genero == "hombre" else (ROJO_CORAL if mostrar_aviso else AZUL)
        pygame.draw.rect(ventana, col_h, btn_hombre, border_radius=12)
        pygame.draw.rect(ventana, borde_h, btn_hombre, 3, border_radius=12)
        dibujar_texto(ventana, textos["hombre"], FONT_INFORMACION, BLANCO, btn_hombre.centerx, btn_hombre.centery)

        # --- BOTÓN JUGAR ---
        pygame.draw.rect(ventana, AMARILLO, btn_jugar, border_radius=15)
        dibujar_texto(ventana, textos["jugar"], FONT_OPCION, NEGRO, btn_jugar.centerx, btn_jugar.centery)

        # --- AVISO SI FALTA ELEGIR PERSONAJE ---
        if mostrar_aviso:
            dibujar_texto(ventana, textos["aviso_genero"], FONT_INFORMACION, ROJO_CORAL, ANCHO // 2, 545)

        pygame.display.flip()
        await asyncio.sleep(0)

    # No llamamos a video_bg.cerrar() aqui: el objeto viene de la cache
    # compartida de obtener_video(), y otras pantallas (instrucciones,
    # niveles) pueden seguir usando esos mismos frames. Vaciarlos ahora
    # dejaria a esas pantallas con un video en negro.

    return {
        "nombre": campos["nombre"] or "Aventurero",
        "edad": campos["edad"] or "N/A",
        "ciudad": campos["ciudad"] or "Antioquia",
        "genero": genero,
        "idioma": idioma
    }