'''
Comportamientos cruzados
Interacción
Afectados por los controles
'''

import assets

NORTE = -8
NOR_ESTE = -8+1
NOR_OESTE = -8-1
SUR = +8
SUR_OESTE = +8-1
SUR_ESTE = +8+1
ESTE = +1
OESTE = -1

class Player:
    '''**HAY JUGADOR 1 Y 2**
    Comparten controles, la diferencia
    es el TURNO de uno y otro

    TURNO significa que 
    se mueve x color de piezas
    se asocia un color de piezas a un *puntaje*
    se asocia un color de piezas a un *tiempo*
    >> Quién revisa de quién es el turno?

'''
    controles = set
    focus = bool
    color = {'black' or 'white'}
    number = 1 or 2
    participant = {'person' or 'ia'}
    turn = bool
    side = {'white' or 'black'}

class Enemy: #hereda de player?
    '''Enemy IA
    Como hacemos una IA de ajedrez?
    1- Movimientos aleatorios
    2- Movimientos reactivos al movimiento del jugador,
        el estado del tablero y el 'camino a ganar'
    3- Evaluación caminos
        Posibilidades de movimiento hacia la victoria

    Tiene las mismas acciones que el jugador en el tablero
        Mover piezas
    '''
    color = ...
    piezas = ...
    def eval_next_mov():
        ...
    def easy_mode():
        ...
    def hard_mode():
        ...

class Board:
    '''>> Responsabilidades
        board.actualizar_posiciones
        board.revisar_ganador
        board.alguien_gano?
    '''
    
    def __init__(self):
        self.piezas = {}

    def dibujar_piezas():
        #hacer piezas
        '''Las piezas serán absolutamente
        siempre la misma cantidad, spawneadas
        en exactamente el mismo lugar'''
        if Pieza.visible == False:
            #expulsar pieza de coleccion de piezas renderizando
            ...
        ...

    def posicion_valida(intencion):
        '''Nos llegaran preguntas por cada posicion,
        debemos contestarlas todas para saber que posicion
        colorear al jugador 
        '''
        return True or False
    
    def resolve_positions():
        ...
    
    def get_available_positions():
        ...

class Pieza:
    '''Lista de piezas
    >> Peón
        Movimiento
            3 posibles movimientos
            Al inicio puede moverse hasta dos casilleros hacia adelante
            El movimiento normal es 1 casillero hacia adelante
            Come en diagonal
    >> Alfil
        Movimiento
            en diagonal en el numero deseado de casilleros
            Come en diagonal
    >> Reina
        Movimiento
            El movimiento normal es en cualquier direccion en el numero
            deseado de casilleros
            Come en cualquier direccion
    >> Rey
        Movimiento
            El movimiento normal es 1 solo casillero en cualquier direccion
            Come en cualquier direccion
    >> Torre
        Movimiento
            El movimiento normal es en vertical u horizontal en el numero
            deseado de casilleros
            Come en vertical u horizontal
    >> Caballo
        Movimiento
            El movimiento normal es en L, en cualquiera de sus 4 rotaciones
            Come en el ultimo casillero 'donde cae'
    '''

    '''las piezas son "headless" cuando importa "en qué dirección avanzan",
    como el peón.
    Todas las otras piezas son "headless" y no les importa,
    Solo importa luego revisar si en X casilla hay una pieza
    del equipo enemigo.
    '''

    '''Movimientos

        posibles_movimientos = los que resolvamos del tablero

        El movimiento es cambiar la pieza de lugar

        El 'posible movimiento' debe ser marcado en el tablero

        Cuidado con los limites del tablero

        El movimiento puede involucrar 'comer' si se cae en
        un SQUARE_TYPE = "comible"

        Al 'comer', la pieza que vence se posiciona en el lugar donde 'comio'

        Necesitamos un mecanismo de 'inspección' de movimientos
        posibles para la pieza seleccionada
    '''
    def __repr__(self):
        return self.__class__.__name__

class Peon(Pieza): ...
class Alfil(Pieza): ...
class Caballo(Pieza): ...
class Torre(Pieza): ...
class Reina(Pieza): ...
class Rey(Pieza): ...

if __name__ == '__main__':
    # p = Peon()
    # print(repr(p))
    # a = Alfil()
    # print(repr(a))
    print(repr(Peon))