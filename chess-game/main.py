'''Como debe iniciar mi juego?

Pre-cargar cosas?
Pre-crear mundos?
Anticiparse a ciertas cosas?
Deberíamos hacer checkeos del sistema e iniciar
el juego conciertos parámetros?
Spawnear threads?

'''
'''
Deberían haber diferencias entre un juego para subir 
a itch.io y steam u cualquier otra plataforma?

Itch.io (o mi página web)
En este aspecto creo que tenemos que usar WebAssembly para
pasar mostrar el juego en un navegador
'''

'''with game as g:
    g.start()
    #esto nos permite por ejemplo salvar el juego de forma segura?
    #mantener o intentar mantener un estado frente a un error
    #(posible recoleccion de errores, reanudar partida, etc.)
Exceptions...
'''

'''Verificaciones previas
Verificación de paths...
    Imágenes - Fuentes - Audio - Scripts
'''

import game
#if todo está bien...
g = game.GameMaster() #todo está bien params?
g.start_loop()