import asyncio
import pygame

async def main():
    pygame.display.init()
    ventana = pygame.display.set_mode((800, 600))
    reloj = pygame.time.Clock()

    color = (200, 50, 50)
    corriendo = True
    while corriendo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False

        ventana.fill(color)
        pygame.display.flip()
        reloj.tick(60)
        await asyncio.sleep(0)

    pygame.quit()

asyncio.run(main())