import pygame

# Pieces directions across the board
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
rects: list[pygame.Rect]

def place(mid_screen_vector):
    # board placement on current screen display
    board_begin = pygame.Vector2(
    (mid_screen_vector.x - width/2,
    mid_screen_vector.y - height/2))
    global rects
    rects = make_rects(board_begin)

def make_rects(board_origin_coordinates: pygame.Vector2) -> list[pygame.Rect]:
    board_rects = []
    startx = board_origin_coordinates.x
    starty = board_origin_coordinates.y
    y = starty
    for r in range(rows):
        x = startx
        for c in range(columns):
            rect = pygame.Rect(x,y,square_width,square_height)
            board_rects.append(rect)
            x+=square_width
        y+=square_height
    return board_rects

def make_nested_rows(row_count: int) -> list[list[int]]:
    rows = []
    for i in range(row_count):
        start = i*row_count
        end = start+row_count
        rows.append(list(range(start,end)))
    return rows

nested_rows = make_nested_rows(rows) # Fijar rows ayuda a validar movimientos.

def row_of_(position: int) -> list[int]:
    '''Devuelve el row al que corresponda la posición ingresada.'''
    for row in nested_rows:
        for num in row:
            if num == position:
                return row
    else: return []
