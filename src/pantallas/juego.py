import os
import sys
import random
import math
import asyncio
import pygame

# --- CONFIGURACIÓN DE RUTAS ---
DIR_PANTALLAS = os.path.dirname(os.path.abspath(__file__))
DIR_SRC = os.path.dirname(DIR_PANTALLAS)

if DIR_SRC not in sys.path:
    sys.path.insert(0, DIR_SRC)

from config import (
    ventana, ANCHO, ALTO, FONDO, FONDO_TARJETA, BLANCO, NEGRO,
    ACENTOS, AMARILLO, VERDE, ROJO_CORAL, AZUL,
    FONT_TITULO, FONT_PREGUNTAS, FONT_OPCION, FONT_INFORMACION,
    RELOJ, FPS
)
from utils.texto import dibujar_texto, dibujar_texto_neon
from utils.video_background import obtener_video
from utils import musica
from pantallas.pausa import pantalla_pausa

# Fuente mas grande solo para el titulo de la cabecera del juego (antes
# usaba FONT_PREGUNTAS=52, se veia chico). FONT_TITULO=90 (config.py) es
# el otro extremo y no cabe sin recortarse en el espacio de la cabecera,
# asi que este tamaño intermedio (70) es el punto justo: grande y legible,
# sin cortarse arriba ni chocar con las insignias de abajo.
FONT_TITULO_JUEGO = pygame.font.Font(None, 70)

# --- CONSTANTES DE FÍSICAS Y MAPA ---
SUELO_Y = ALTO - 100
ANCHO_JUGADOR = 70
ALTO_JUGADOR = 90
VELOCIDAD_X = 480    # px/segundo (antes: 8 px/frame, dependia del FPS real)
GRAVEDAD = 2200       # px/segundo^2
FUERZA_SALTO = -820   # px/segundo
SALTOS_MAXIMOS = 2  # 1 = salto normal, 2 = doble salto

ANCHO_META = 210
ALTO_META = 95
AMPLITUD_META = 18       # cuanto sube y baja cada plataforma (px)
VELOCIDAD_META = 2.2     # que tan rapido oscila

# --- MAPEO DE ESTADOS DEL JUEGO -> EXPRESION DEL PERSONAJE ---
# Cambia estos valores si quieres usar otras expresiones para cada
# situacion. Los nombres deben coincidir con los archivos generados
# por recortar.py dentro de assets/characters/<genero>_sprites/
EXPRESION_POR_ESTADO = {
    "idle": "sonriendo",
    "saltando": "emocionada",
    "correcto": "feliz",
    "incorrecto": "triste",
    "tiempo_agotado": "panico",
}

# --- COLOR DE NEON DE LA CABECERA, DISTINTO POR NIVEL ---
# 1 = gastronomia (dorado), 2 = arquitectura (azul), 3 = biodiversidad
# (verde). Si algun dia agregas un cuarto nivel sin color asignado,
# usa AMARILLO como respaldo (ver .get(...) mas abajo).
COLOR_NEON_POR_NIVEL = {
    1: AMARILLO,
    2: AZUL,
    3: VERDE,
}


def _cargar_sonido(nombre_archivo):
    """Carga un efecto de sonido desde assets/sounds/. Si no existe o
    falla al cargar, devuelve None (el juego sigue funcionando sin
    sonido, solo lo avisa por consola)."""
    DIR_RAIZ = os.path.dirname(DIR_SRC)
    ruta = os.path.join(DIR_RAIZ, "assets", "sounds", nombre_archivo)
    if os.path.exists(ruta):
        try:
            return pygame.mixer.Sound(ruta)
        except Exception as e:
            print(f"[ERROR AL CARGAR SONIDO] {ruta}: {e}")
    else:
        print(f"[SONIDO NO ENCONTRADO] {ruta}")
    return None


SONIDO_CORRECTO = _cargar_sonido("correcto.ogg")
SONIDO_INCORRECTO = _cargar_sonido("incorrecto.ogg")
SONIDO_SALTO = _cargar_sonido("salto.ogg")

# --- VIDEO DE FONDO POR NIVEL ---
# El orden coincide con "tema" en preguntas.py: nivel 1 = gastronomia,
# nivel 2 = arquitectura, nivel 3 = biodiversidad. Estas son carpetas
# de frames PNG (generadas con generar_frames_video.py) dentro de
# assets/videos/. Si una carpeta no existe, ese nivel usa el color
# solido de FONDO como respaldo.
VIDEOS_POR_NIVEL = {
    1: "nivel1_gastronomia_frames",
    2: "nivel2_arquitectura_frames",
    3: "nivel3_biodiversidad_frames",
}

# Misma idea para la musica de fondo de cada nivel. Coloca estos
# archivos en assets/music/. Si un nivel no tiene pista asignada o el
# archivo no existe, simplemente sigue sonando lo que ya estaba (o
# nada, si tampoco habia musica antes).
MUSICA_POR_NIVEL = {
    1: "nivel1_gastronomia.ogg",
    2: "nivel2_arquitectura.ogg",
    3: "nivel3_biodiversidad.ogg",
}

# Recordamos solo que nivel de musica ya esta sonando, para no volver a
# llamar musica.reproducir() en cada pregunta del mismo nivel (aunque
# musica.py ya evita reiniciar la misma pista, esto ahorra el chequeo).
_ULTIMO_NIVEL_MUSICA = {"nivel": None}


def _obtener_video_nivel(nivel_actual):
    """Devuelve el VideoBackground (basado en frames) del nivel actual.
    Usa la cache compartida de obtener_video(), asi que no hay que
    abrir ni cerrar nada manualmente al cambiar de nivel: si el jugador
    rejuega el mismo nivel, los frames ya estan en memoria."""
    DIR_RAIZ = os.path.dirname(DIR_SRC)
    nombre_carpeta = VIDEOS_POR_NIVEL.get(nivel_actual)
    fondo = None
    if nombre_carpeta:
        ruta = os.path.join(DIR_RAIZ, "assets", "videos", nombre_carpeta)
        if os.path.exists(ruta):
            fondo = obtener_video(ruta, (ANCHO, ALTO))
        else:
            print(f"[CARPETA DE FRAMES NO ENCONTRADA] {ruta}")

    if _ULTIMO_NIVEL_MUSICA["nivel"] != nivel_actual:
        nombre_musica = MUSICA_POR_NIVEL.get(nivel_actual)
        if nombre_musica:
            ruta_musica = os.path.join(DIR_RAIZ, "assets", "music", nombre_musica)
            musica.reproducir(ruta_musica, volumen=0.35)
        _ULTIMO_NIVEL_MUSICA["nivel"] = nivel_actual

    return fondo


def precargar_video_nivel(nivel):
    """Carga (o deja ya en cache) los frames de video de un nivel, SIN
    tocar la musica ni ningun otro estado de la partida.

    Pensada para llamarse desde un hilo aparte (threading.Thread) justo
    cuando se muestra la pantalla de "nivel completado": el jugador se
    queda leyendo esa pantalla varios segundos de todas formas, y ese
    tiempo es gratis para adelantar la carga pesada de los frames PNG
    del SIGUIENTE nivel. Asi, cuando jugar_pregunta() pide ese video con
    _obtener_video_nivel(), ya esta en la cache de obtener_video() y no
    hay demora perceptible al entrar al nivel nuevo.

    Si el nivel no existe (por ejemplo, se llama con nivel=4 despues del
    ultimo nivel) simplemente no hace nada.
    """
    DIR_RAIZ = os.path.dirname(DIR_SRC)
    nombre_carpeta = VIDEOS_POR_NIVEL.get(nivel)
    if not nombre_carpeta:
        return
    ruta = os.path.join(DIR_RAIZ, "assets", "videos", nombre_carpeta)
    if os.path.exists(ruta):
        obtener_video(ruta, (ANCHO, ALTO))
    else:
        print(f"[PRECARGA] Carpeta de frames no encontrada: {ruta}")


# Cache de sprites por genero: se llenan la primera vez que se piden y
# se reutilizan el resto de la partida, en vez de releer 15 archivos
# PNG del disco en cada pregunta.
_CACHE_SPRITES = {}


def cargar_sprites_jugador(genero="mujer"):
    """
    Carga las 15 expresiones del personaje YA RECORTADAS desde:
    assets/characters/<genero>_sprites/<expresion>.png

    Devuelve un diccionario {"emocionada": Surface, "sonriendo": Surface, ...}
    con una entrada por cada expresion encontrada. Cada sprite se escala
    manteniendo su proporcion original (sin deformarlo) para que quepa
    dentro de un rectangulo de ANCHO_JUGADOR x ALTO_JUGADOR.

    Los resultados se cachean por genero: la primera llamada lee del
    disco, las siguientes devuelven el mismo diccionario ya cargado.
    """
    if genero in _CACHE_SPRITES:
        return _CACHE_SPRITES[genero]

    DIR_RAIZ = os.path.dirname(DIR_SRC)
    carpeta_sprites = os.path.join(DIR_RAIZ, "assets", "characters", f"{genero}_sprites")

    expresiones = [
        "emocionada", "sonriendo", "triste", "llorando", "rabia",
        "panico", "confundida", "feliz", "asustada", "dormida",
        "sorprendida", "agotada", "brindis", "baile", "guino",
    ]

    sprites = {}

    for expresion in expresiones:
        ruta = os.path.join(carpeta_sprites, f"{expresion}.png")
        if os.path.exists(ruta):
            try:
                img = pygame.image.load(ruta).convert_alpha()
                sprites[expresion] = _escalar_manteniendo_proporcion(
                    img, ANCHO_JUGADOR, ALTO_JUGADOR
                )
            except Exception as e:
                print(f"[ERROR AL CARGAR SPRITE] {ruta}: {e}")
        else:
            print(f"[NO ENCONTRADO] {ruta}")

    _CACHE_SPRITES[genero] = sprites
    return sprites


def _escalar_manteniendo_proporcion(img, ancho_max, alto_max):
    """Escala una imagen para que quepa dentro de ancho_max x alto_max
    sin deformarla (mantiene su proporcion original)."""
    ancho_orig, alto_orig = img.get_size()
    factor = min(ancho_max / ancho_orig, alto_max / alto_orig)
    nuevo_ancho = max(1, round(ancho_orig * factor))
    nuevo_alto = max(1, round(alto_orig * factor))
    return pygame.transform.smoothscale(img, (nuevo_ancho, nuevo_alto))


def _obtener_sprite(sprites_jugador, estado):
    """Devuelve el Surface correspondiente al estado del juego, con
    respaldo a 'sonriendo' o al primer sprite disponible si falta algo."""
    expresion = EXPRESION_POR_ESTADO.get(estado, "sonriendo")
    return (
        sprites_jugador.get(expresion)
        or sprites_jugador.get("sonriendo")
        or (next(iter(sprites_jugador.values())) if sprites_jugador else None)
    )


# Cache de fuentes Arial por tamaño: crear un Font es relativamente
# caro y _preparar_texto_opcion se llama varias veces por frame (una
# por tarjeta de respuesta), asi que reusamos la misma instancia en
# vez de crear objetos nuevos 60 veces por segundo.
_CACHE_FUENTES_OPCION = {}


def _fuente_opcion(tam):
    if tam not in _CACHE_FUENTES_OPCION:
        _CACHE_FUENTES_OPCION[tam] = pygame.font.SysFont("Arial", tam, bold=True)
    return _CACHE_FUENTES_OPCION[tam]


def _preparar_texto_opcion(texto, ancho_max):
    """Devuelve (lineas, fuente) que garantizan que el texto quepa dentro
    de una tarjeta de ancho ancho_max. Primero prueba a reducir el tamaño
    de fuente; si aun asi no cabe en una linea, lo parte en dos."""
    padding = 20
    ancho_disponible = ancho_max - padding

    for tam in (22, 20, 18, 16, 14):
        fuente = _fuente_opcion(tam)
        if fuente.size(texto)[0] <= ancho_disponible:
            return [texto], fuente

    fuente = _fuente_opcion(14)
    palabras = texto.split(" ")
    mitad = max(1, len(palabras) // 2)
    linea1 = " ".join(palabras[:mitad])
    linea2 = " ".join(palabras[mitad:])
    return [linea1, linea2], fuente


def calcular_rects_metas(cantidad_opciones):
    espacio = ANCHO // (cantidad_opciones + 1)
    rects = []
    for i in range(cantidad_opciones):
        x = espacio * (i + 1) - ANCHO_META // 2
        y = SUELO_Y - ALTO_META
        rects.append(pygame.Rect(x, y, ANCHO_META, ALTO_META))
    return rects


def _dibujar_fondo_texto(ventana, texto, font, x, y, padding_x=18, padding_y=8, alpha=150):
    """Dibuja una tarjetita semitransparente (mismo color que
    FONDO_TARJETA) detras de donde va a ir un texto, centrada en (x, y).
    Sin esto, los mensajes de resultado se dibujaban directo sobre el
    video de fondo: si en ese instante el frame del video era claro
    justo ahi, el texto perdia contraste. Con esta tarjeta de respaldo
    el texto se lee igual sin importar que este pasando en el video."""
    ancho_texto, alto_texto = font.size(texto)
    ancho = ancho_texto + padding_x * 2
    alto = alto_texto + padding_y * 2
    superficie = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    pygame.draw.rect(superficie, (*FONDO_TARJETA, alpha), superficie.get_rect(), border_radius=12)
    rect = superficie.get_rect(center=(x, y))
    ventana.blit(superficie, rect.topleft)


def _dibujar_cabecera(nivel_actual, puntos, tiempo_restante, vidas):
    # --- FILA 1: titulo del juego, centrado de verdad y con efecto neon
    # (color distinto segun el nivel: dorado/gastronomia, azul/
    # arquitectura, verde/biodiversidad). Antes usaba FONT_TITULO (90pt)
    # centrado en y=30, lo que hacia que la mitad superior del texto
    # quedara literalmente fuera de la pantalla (por eso se veia "muy
    # cerca del borde" / cortado), y ademas estaba corrido a la derecha
    # (ANCHO // 2 + 240) en vez de centrado. Ahora usa una fuente mas
    # moderada, va realmente centrado, y tiene aire de sobra arriba.
    color_titulo = COLOR_NEON_POR_NIVEL.get(nivel_actual, AMARILLO)
    dibujar_texto_neon(ventana, "AVENTURA ANTIOQUEÑA", FONT_TITULO_JUEGO, color_titulo, ANCHO // 2, 48)

    # --- FILA 2: insignias (nivel, puntos, vidas, tiempo), debajo del
    # titulo en vez de compartir la misma fila (asi nunca se superponen).
    # Bajadas de y=78 a y=100 porque el titulo ahora es mas grande (70pt
    # en vez de 52pt) y necesita mas aire debajo.
    badges = [
        (f"Nivel {nivel_actual}", AZUL),
        (f"{puntos} pts", VERDE),
        (f"Vidas: {vidas}", ROJO_CORAL),
        (f"{int(tiempo_restante)}s", ROJO_CORAL if tiempo_restante <= 10 else AMARILLO),
    ]

    x = 15
    y_badges = 100
    for texto, color in badges:
        rect = pygame.Rect(x, y_badges, 110, 32)
        pygame.draw.rect(ventana, color, rect, border_radius=16)
        dibujar_texto(ventana, texto, FONT_INFORMACION, NEGRO, rect.centerx, rect.centery)
        x += 120


async def jugar_pregunta(preguntas_data, nivel_actual, actual_pregunta, puntos, tiempo, genero="mujer", vidas=3):
    """
    Ejecuta una pregunta como minijuego de plataformas.
    Devuelve una tupla (es_correcta: bool, tiempo_usado: float en segundos).
    """
    pregunta_data = preguntas_data["tema"][nivel_actual - 1]["pregunta"][actual_pregunta]

    # Mezclamos el orden de las opciones (sin tocar los datos originales
    # en preguntas.py) para que la respuesta correcta no siempre este en
    # la misma posicion.
    orden_opciones = list(range(len(pregunta_data["opciones"])))
    random.shuffle(orden_opciones)
    opciones = [pregunta_data["opciones"][i] for i in orden_opciones]
    respuesta_correcta = orden_opciones.index(pregunta_data["respuesta"])

    metas = calcular_rects_metas(len(opciones))
    metas_y_base = [meta.y for meta in metas]

    video_fondo = _obtener_video_nivel(nivel_actual)

    sprites_jugador = cargar_sprites_jugador(genero)
    jugador = pygame.Rect(50, SUELO_Y - ALTO_JUGADOR, ANCHO_JUGADOR, ALTO_JUGADOR)

    vel_y = 0
    en_suelo = True
    saltos_restantes = SALTOS_MAXIMOS
    mostrando_resultado = False
    inicio_pausa = 0
    es_correcta = False
    opcion_seleccionada = -1
    tiempo_restante = float(tiempo)
    tiempo_agotado = False
    direccion = "derecha"
    meta_hover = -1

    while True:
        dt = RELOJ.tick(FPS) / 1000.0

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_SPACE, pygame.K_UP) and saltos_restantes > 0 and not mostrando_resultado:
                    vel_y = FUERZA_SALTO
                    en_suelo = False
                    saltos_restantes -= 1
                    if SONIDO_SALTO:
                        SONIDO_SALTO.play()
                elif evento.key == pygame.K_ESCAPE:
                    accion = await pantalla_pausa()
                    if accion == "salir":
                        pygame.quit()
                        sys.exit()

        if not mostrando_resultado:
            # --- Cuenta regresiva real ---
            tiempo_restante -= dt
            if tiempo_restante <= 0:
                tiempo_restante = 0
                tiempo_agotado = True
                mostrando_resultado = True
                inicio_pausa = pygame.time.get_ticks()
                es_correcta = False
                opcion_seleccionada = -1
                if SONIDO_INCORRECTO:
                    SONIDO_INCORRECTO.play()

            if not mostrando_resultado:
                # --- Plataformas móviles: cada una oscila con una fase
                # distinta para que no se muevan todas igual ---
                tiempo_animacion = pygame.time.get_ticks() / 1000.0
                for i, meta in enumerate(metas):
                    desfase = i * 0.9
                    meta.y = metas_y_base[i] + int(
                        math.sin(tiempo_animacion * VELOCIDAD_META + desfase) * AMPLITUD_META
                    )

                # Si el jugador ya estaba en el aire (saltando) al empezar
                # este frame. Caminando en el piso esto es siempre False,
                # sin importar la gravedad, asi que caminar nunca elige.
                estaba_en_aire = not en_suelo

                teclas = pygame.key.get_pressed()
                if teclas[pygame.K_LEFT]:
                    jugador.x -= VELOCIDAD_X * dt
                    direccion = "izquierda"
                if teclas[pygame.K_RIGHT]:
                    jugador.x += VELOCIDAD_X * dt
                    direccion = "derecha"

                jugador.x = max(0, min(ANCHO - jugador.width, jugador.x))

                # Físicas de movimiento y salto (escaladas por dt para que
                # no dependan del framerate real; si el video de fondo
                # provoca caidas de FPS, el jugador ya no se ve mas lento)
                vel_y += GRAVEDAD * dt
                jugador.y += vel_y * dt

                if jugador.y >= SUELO_Y - jugador.height:
                    jugador.y = SUELO_Y - jugador.height
                    vel_y = 0
                    en_suelo = True
                    saltos_restantes = SALTOS_MAXIMOS

                # Sobre que tarjeta esta el jugador ahora mismo
                meta_hover = -1
                for i, meta in enumerate(metas):
                    if jugador.colliderect(meta):
                        meta_hover = i
                        break

                # Se elige la respuesta solo si el jugador la toca ESTANDO
                # EN UN SALTO (estaba en el aire). Caminar sobre la tarjeta
                # sin saltar solo la resalta, no la selecciona.
                if meta_hover != -1 and estaba_en_aire:
                    mostrando_resultado = True
                    inicio_pausa = pygame.time.get_ticks()
                    opcion_seleccionada = meta_hover
                    es_correcta = (opcion_seleccionada == respuesta_correcta)
                    if es_correcta and SONIDO_CORRECTO:
                        SONIDO_CORRECTO.play()
                    elif not es_correcta and SONIDO_INCORRECTO:
                        SONIDO_INCORRECTO.play()
        else:
            if pygame.time.get_ticks() - inicio_pausa > 1200:
                tiempo_usado = float(tiempo) - tiempo_restante
                return es_correcta, tiempo_usado

        # --- DIBUJADO DE LA PANTALLA ---
        if video_fondo:
            video_fondo.dibujar(ventana, dt)
            overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
            overlay.fill((*FONDO, 140))
            ventana.blit(overlay, (0, 0))
        else:
            ventana.fill(FONDO)
        _dibujar_cabecera(nivel_actual, puntos, tiempo_restante, vidas)

        # Pregunta (bajada de y=80 a y=145 para dejar espacio a la
        # cabecera de 2 filas: titulo mas grande (70pt) + insignias)
        tarjeta_p = pygame.Rect(ANCHO // 2 - 550, 145, 1100, 90)
        pygame.draw.rect(ventana, FONDO_TARJETA, tarjeta_p, border_radius=20)
        dibujar_texto(ventana, pregunta_data["pregunta"], FONT_PREGUNTAS, BLANCO, ANCHO // 2, tarjeta_p.centery)

        # Suelo
        pygame.draw.rect(ventana, FONDO_TARJETA, (0, SUELO_Y, ANCHO, ALTO - SUELO_Y))

        # Tarjetas de respuestas
        for i, (opcion, meta) in enumerate(zip(opciones, metas)):
            if mostrando_resultado:
                color = VERDE if i == respuesta_correcta else (ROJO_CORAL if i == opcion_seleccionada else ACENTOS[i % len(ACENTOS)])
            else:
                color = ACENTOS[i % len(ACENTOS)]

            pygame.draw.rect(ventana, color, meta, border_radius=16)

            if not mostrando_resultado and i == meta_hover:
                pygame.draw.rect(ventana, BLANCO, meta, 4, border_radius=16)

            texto_full = f"{chr(65 + i)}. {opcion}"
            lineas, fuente_opcion = _preparar_texto_opcion(texto_full, meta.width)
            if len(lineas) == 1:
                dibujar_texto(ventana, lineas[0], fuente_opcion, NEGRO, meta.centerx, meta.centery)
            else:
                dibujar_texto(ventana, lineas[0], fuente_opcion, NEGRO, meta.centerx, meta.centery - 12)
                dibujar_texto(ventana, lineas[1], fuente_opcion, NEGRO, meta.centerx, meta.centery + 12)

        # --- Personaje: elige la expresion segun el estado del juego ---
        if mostrando_resultado:
            if tiempo_agotado:
                estado_actual = "tiempo_agotado"
            elif es_correcta:
                estado_actual = "correcto"
            else:
                estado_actual = "incorrecto"
        elif not en_suelo:
            estado_actual = "saltando"
        else:
            estado_actual = "idle"

        sprite_img = _obtener_sprite(sprites_jugador, estado_actual)
        if sprite_img:
            if direccion == "izquierda":
                sprite_img = pygame.transform.flip(sprite_img, True, False)
            # Centrar el sprite dentro del rect del jugador (por si quedo
            # mas angosto/alto que ANCHO_JUGADOR x ALTO_JUGADOR al
            # mantener su proporcion original)
            offset_x = (jugador.width - sprite_img.get_width()) // 2
            offset_y = jugador.height - sprite_img.get_height()  # alineado al piso
            ventana.blit(sprite_img, (jugador.x + offset_x, jugador.y + offset_y))
        else:
            pygame.draw.rect(ventana, AMARILLO, jugador, border_radius=8)

        # Mensajes
        if mostrando_resultado:
            texto_correcta = opciones[respuesta_correcta]
            if tiempo_agotado:
                _dibujar_fondo_texto(ventana, "¡SE ACABÓ EL TIEMPO!", FONT_OPCION, ANCHO // 2, SUELO_Y - ALTO_META - 55)
                dibujar_texto(ventana, "¡SE ACABÓ EL TIEMPO!", FONT_OPCION, ROJO_CORAL, ANCHO // 2, SUELO_Y - ALTO_META - 55)
                _dibujar_fondo_texto(ventana, f"Era: {texto_correcta}", FONT_INFORMACION, ANCHO // 2, SUELO_Y - ALTO_META - 20)
                dibujar_texto(ventana, f"Era: {texto_correcta}", FONT_INFORMACION, AMARILLO, ANCHO // 2, SUELO_Y - ALTO_META - 20)
            elif es_correcta:
                _dibujar_fondo_texto(ventana, "¡CORRECTO! +10 Puntos", FONT_OPCION, ANCHO // 2, SUELO_Y - ALTO_META - 30)
                dibujar_texto(ventana, "¡CORRECTO! +10 Puntos", FONT_OPCION, VERDE, ANCHO // 2, SUELO_Y - ALTO_META - 30)
            else:
                _dibujar_fondo_texto(ventana, "¡INCORRECTO!", FONT_OPCION, ANCHO // 2, SUELO_Y - ALTO_META - 55)
                dibujar_texto(ventana, "¡INCORRECTO!", FONT_OPCION, ROJO_CORAL, ANCHO // 2, SUELO_Y - ALTO_META - 55)
                _dibujar_fondo_texto(ventana, f"Era: {texto_correcta}", FONT_INFORMACION, ANCHO // 2, SUELO_Y - ALTO_META - 20)
                dibujar_texto(ventana, f"Era: {texto_correcta}", FONT_INFORMACION, AMARILLO, ANCHO // 2, SUELO_Y - ALTO_META - 20)
        else:
            if meta_hover != -1:
                mensaje_ayuda = "¡Salta para caer sobre esta respuesta y elegirla!"
                _dibujar_fondo_texto(ventana, mensaje_ayuda, FONT_INFORMACION, ANCHO // 2, ALTO - 20)
                dibujar_texto(ventana, mensaje_ayuda, FONT_INFORMACION, AMARILLO, ANCHO // 2, ALTO - 20)
            else:
                mensaje_ayuda = "Camina hasta una respuesta y salta sobre ella para elegirla"
                _dibujar_fondo_texto(ventana, mensaje_ayuda, FONT_INFORMACION, ANCHO // 2, ALTO - 20)
                dibujar_texto(ventana, mensaje_ayuda, FONT_INFORMACION, BLANCO, ANCHO // 2, ALTO - 20)

        pygame.display.flip()
        await asyncio.sleep(0)