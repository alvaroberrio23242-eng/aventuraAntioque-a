import os
import pygame

# Cache compartida por ruta de carpeta: si bienvenida e instrucciones
# (u otras pantallas) piden el mismo video, se cargan los frames del
# disco una sola vez en vez de dos.
_CACHE_VIDEOS = {}


def obtener_video(ruta_carpeta_frames, tamano_destino, fps=8, fade_segundos=1.0):
    """Devuelve un VideoBackground cacheado por ruta absoluta. Usa esto
    en vez de instanciar VideoBackground(...) directamente, salvo que
    tengas una razon especifica para no compartir la cache."""
    clave = (os.path.abspath(ruta_carpeta_frames), tamano_destino)
    if clave not in _CACHE_VIDEOS:
        _CACHE_VIDEOS[clave] = VideoBackground(
            ruta_carpeta_frames, tamano_destino, fps=fps, fade_segundos=fade_segundos
        )
    return _CACHE_VIDEOS[clave]


class VideoBackground:
    """
    Reproduce un video de fondo como secuencia de imagenes PNG (no usa
    cv2 en tiempo real: eso permite que funcione tanto en escritorio
    como en el navegador via pygbag).

    Espera una carpeta con frames nombrados en orden, generada de
    antemano con generar_frames_video.py, ej:
        assets/videos/nivel1_gastronomia_frames/frame_0001.png
        assets/videos/nivel1_gastronomia_frames/frame_0002.png
        ...
    """

    def __init__(self, ruta_carpeta_frames, tamano_destino, fps=8, fade_segundos=1.0):
        """
        tamano_destino: (ancho, alto) al que se reescala cada frame
        UNA SOLA VEZ al cargar (normalmente ANCHO, ALTO de config.py).
        Como ese tamaño no cambia durante la partida, esto evita
        reescalar en cada dibujado (60 veces por segundo), que era el
        cuello de botella de rendimiento de la version anterior.
        """
        self.ruta_carpeta_frames = ruta_carpeta_frames
        self.fps = fps
        self.frames = []
        self.frame_actual = 0
        self.tiempo_acumulado = 0.0
        self.duracion_frame = 1.0 / fps if fps > 0 else 1.0 / 12

        if os.path.isdir(ruta_carpeta_frames):
            nombres = sorted(
                f for f in os.listdir(ruta_carpeta_frames)
                if f.lower().endswith((".png", ".jpg", ".jpeg"))
            )
            for nombre in nombres:
                ruta = os.path.join(ruta_carpeta_frames, nombre)
                try:
                    img = pygame.image.load(ruta).convert()
                    if img.get_size() != tamano_destino:
                        img = pygame.transform.scale(img, tamano_destino)
                    self.frames.append(img)
                except Exception as e:
                    print(f"[ERROR AL CARGAR FRAME] {ruta}: {e}")
        else:
            print(f"[CARPETA DE FRAMES NO ENCONTRADA] {ruta_carpeta_frames}")
            print("Corre 'python generar_frames_video.py' desde la raiz del proyecto.")

        self.total_frames = len(self.frames)

        # Fundido simple entre el ultimo y el primer frame, para que el
        # loop no se note como un corte brusco.
        self.frames_fade = 0
        if fade_segundos > 0 and self.total_frames > 0:
            self.frames_fade = max(
                1, min(int(fps * fade_segundos), self.total_frames // 4 or 1)
            )

    def actualizar(self, dt):
        if not self.frames:
            return None

        self.tiempo_acumulado += dt
        while self.tiempo_acumulado >= self.duracion_frame:
            self.tiempo_acumulado -= self.duracion_frame
            self.frame_actual = (self.frame_actual + 1) % self.total_frames

        base = self.frames[self.frame_actual]

        # Fundido hacia el primer frame cerca del final del loop
        if self.frames_fade > 0 and self.frame_actual >= self.total_frames - self.frames_fade:
            progreso = self.frame_actual - (self.total_frames - self.frames_fade)
            alpha = min(255, max(0, int(255 * (progreso / self.frames_fade))))
            primer_frame = self.frames[0]  # ya viene del mismo tamano_destino
            resultado = base.copy()
            overlay = primer_frame.copy()
            overlay.set_alpha(alpha)
            resultado.blit(overlay, (0, 0))
            return resultado

        return base

    def dibujar(self, ventana, dt=None):
        # dt en segundos desde el ultimo frame. Si no se pasa, asumimos
        # 1/60 (llamado cada frame a 60 FPS aprox).
        if dt is None:
            dt = 1.0 / 60.0

        surf = self.actualizar(dt)
        if surf:
            ventana.blit(surf, (0, 0))

    def update_and_draw(self, ventana, dt=None):
        # Compatibilidad por si otro archivo llama a este nombre de método
        self.dibujar(ventana, dt)

    def cerrar(self):
        # No hay archivo de video abierto que liberar (son PNGs ya
        # cargados en memoria), pero se deja el metodo para no romper
        # el codigo que lo llama.
        self.frames = []
