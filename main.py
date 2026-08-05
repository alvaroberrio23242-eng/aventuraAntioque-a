"""
Punto de entrada para pygbag (build web).

pygbag exige que exista un archivo main.py justo en la raíz de la
carpeta que se empaqueta (esta carpeta), y que la carga de assets no
"salga" de esa carpeta. Como el juego real vive en src/main.py (con
su propia lógica de rutas para importar pantallas/, utils/, datos/),
este archivo solo agrega src/ al sys.path y delega ahí.

Para jugar en escritorio seguís usando: python src/main.py
Para compilar la version web: pygbag .   (ejecutado desde esta carpeta)
"""
import asyncio
import os
import sys

DIR_RAIZ = os.path.dirname(os.path.abspath(__file__))
DIR_SRC = os.path.join(DIR_RAIZ, "src")

if DIR_SRC not in sys.path:
    sys.path.insert(0, DIR_SRC)

from main import main  # src/main.py

if __name__ == "__main__":
    asyncio.run(main())
