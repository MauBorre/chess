import pygame
'''
Las piezas pueden a través del tablero en las siguientes direcciones:
    > ADELANTE
    > ATRAS
    > IZQUIERDA
    > DERECHA
    > DIAGONALES
Definidos como:
    > NORTE = -8
    > NORESTE = -8+1
    > NOROESTE = -8-1
    > SUR = +8
    > SUROESTE = +8-1
    > SURESTE = +8+1
    > ESTE = +1
    > OESTE = -1
'''
NORTE = -8
NOR_ESTE = -8+1
NOR_OESTE = -8-1
SUR = +8
SUR_OESTE = +8-1
SUR_ESTE = +8+1
ESTE = +1
OESTE = -1

square_width = 88
square_height = square_width
rows = 8
columns = rows
width = square_width * rows
height = width

def make_rects(board_origin_coordinates: pygame.Vector2) -> list[pygame.Rect]:
    _boardRects = []
    startx = board_origin_coordinates.x
    starty = board_origin_coordinates.y
    y = starty
    for r in range(rows):
        x = startx
        for c in range(columns):
            rect = pygame.Rect(x,y,square_width,square_height)
            _boardRects.append(rect)
            x+=square_width
        y+=square_height
    return _boardRects

def make_nested_rows(row_count: int) -> list[list[int]]:
    _rows = []
    for i in range(row_count):
        start = i*row_count
        end = start+row_count
        _rows.append(list(range(start,end)))
    return _rows

nested_rows = make_nested_rows(rows) # Fijar rows ayuda a validar movimientos.

def row_of_(position: int) -> list[int]:
    '''Devuelve el row al que corresponda la posición ingresada.'''
    for row in nested_rows:
        for num in row:
            if num == position:
                return row
    else: return []
