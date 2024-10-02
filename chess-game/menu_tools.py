'''Reactividad de los elementos

Los menúes deben ser reaccionar a ciertos
aspectos:

> Sus elementos tienen estado focus (bool)
    Cambia con el hover del mouse,
    pero tambien es movible con las flechas y wasd

> Sus elementos tienen acciones
    al ser confirmado su focus, se produce *algo*

> Son afectados por los controles del juego
    Enter confirma 'lo que tenga focus'
    Flechitas para mover el focus around
    Escape cierra sub-menues (como el menu de pausa y menu de opciones)
    Etc...

Los menúes tienen *elementos* que van *posicionados* en *pantalla*.
Podemos tomar varios enfoques:
    > grilla de rows y columnas (tkinter)
    > secciones con padding (html)
'''

import text_storage

class Menu:
    rows = ...#saltos de coordenada
    columns = ... #saltos de coordenada
    table_size = ... #auto center?
    sprites = ... #backgrounds, imagenes posicionadas en grilla
    fuente = ... # importar del escritorio
    size = ...
    textos = ...
    
    def resolver_posicion():
        #para colocer correctamente lo que tenga
        #que colocar
        ...

    def place_in_grid():
        ...
    
    def select_cell():
        ...

class MenuElement: #hereda de sprite?
    focus = bool
    label = ...
    position = ... #rows&columns system?
    clickable = bool

if __name__ == '__main__':
    '''Ejemplo de creación de menú
    Primero crearemos un objeto menú y luego
    lo introduciremos a un pygame loop'''

    my_menu = Menu() #cuánto debemos pre-definir de él?
    #my_menu = Menu(size=(200,200) )
    # agregando cosas al menú
    #my_menu.add_element('holis',row=0,col=0)
    ...