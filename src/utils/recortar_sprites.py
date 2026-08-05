import pygame

def obtener_frame(spritesheet, columna, fila, ancho_frame, alto_frame):
    rect = pygame.Rect(
        columna * ancho_frame, 
        fila * alto_frame, 
        ancho_frame, 
        alto_frame
    )
    frame = pygame.Surface((ancho_frame, alto_frame), pygame.SRCALPHA)
    frame.blit(spritesheet, (0, 0), rect)
    return frame