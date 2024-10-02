'''Graficando una grilla de puntos
util para hacer hover bajo un area
en perspectiva
'''

'''Perspectiva

>>Debemos movernos 'en triangulos' para manipular las posiciones
en perspectiva<<

Debemos dibujar una grilla en perspectiva, la cual
sera el tablero

Este chess sera un juego para usar el mouse,
asi responderemos a su posicion marcando con 
contornos 'lo que se va a seleccionar'
ya sea una pieza, un espacio en la grilla, etc

Debemos dibujar poligonos en los cuadrados
que se forman de las lineas para poder 'colorearlos'
adecuadamente, posiblemente el calculo
de interseccion de lineas nos ayude para saber exactamente
que puntos marcan los poligonos buscados
**Agregamos una opcion para poner la perspectiva 'desde arriba'?**
'''

import pygame
pygame.init()
screen = pygame.display.set_mode((620, 520))
clock = pygame.time.Clock()
running = True

def check_mouse_hover(mouse,cell_positions):
    '''Consumir una array con celdas y verificar sus 4 coordenadas'''
    # >>> DEBO CREAR UN PERÍMETRO DE PUNTOS??? <<< 06/09/24
    '''BUG no me esta tomando correctamente la perspectiva aplicada a las coordenadas
    de celda,
    Lo estamos calculando como un cuadrado normal y eso es incorrecto.
    '''
    #https://stackoverflow.com/questions/64095396/detecting-collisions-between-polygons-and-rectangles-in-pygame
    #https://stackoverflow.com/questions/59553156/pygame-detecting-collision-of-a-rotating-rectangle/59553589#59553589
    #https://stackoverflow.com/questions/56100547/how-do-i-check-collision-between-a-line-and-a-rect-in-pygame

    for cell_quad in cell_positions:

        #Esto solo sirve para rectangulos, no paralelogramos
        min_x = min(coord_array[cell_quad[0]][0],coord_array[cell_quad[1]][0],coord_array[cell_quad[2]][0],coord_array[cell_quad[3]][0])
        max_x = max(coord_array[cell_quad[0]][0],coord_array[cell_quad[1]][0],coord_array[cell_quad[2]][0],coord_array[cell_quad[3]][0])
        min_y = min(coord_array[cell_quad[0]][1],coord_array[cell_quad[1]][1],coord_array[cell_quad[2]][1],coord_array[cell_quad[3]][1])
        max_y = max(coord_array[cell_quad[0]][1],coord_array[cell_quad[1]][1],coord_array[cell_quad[2]][1],coord_array[cell_quad[3]][1])

        if  min_x < mouse[0] < max_x and min_y < mouse[1] < max_y:
            '''Esto debe ser:
            If mouse intersects line:
                draw.polygon
            '''
            # no hay chances que no dibuje este polígono
            pygame.draw.polygon(screen,'yellow',[coord_array[cell_quad[0]],
                                                 coord_array[cell_quad[2]],
                                                 coord_array[cell_quad[3]],
                                                 coord_array[cell_quad[1]]],
                                                 0)

# generamos una lista de puntos expandidos -> +colPad +rowPad +perspPad
def make_coord_array(pad=50,
                    coord_array=[],
                    columns=2,
                    rows=2,
                    position_offset=200,
                    perspective=-40):
    cells = make_cells(columns,rows) 
    row_pad=0
    perspective_offset = 0
    for row in range(rows):
            col_pad=0+perspective_offset
            for col in range(columns): # falta + perspective offset (aplica solo al col_pad)
                coord_array.append((col+col_pad+position_offset,row+row_pad+position_offset))
                col_pad+=pad
            row_pad+=pad
            perspective_offset+=perspective
    return coord_array, cells

# almacenando POSICIONES del array de coordenadas
def make_cells(columns,rows):
    '''
    case: rows = 3
          col  = 3
    point_array =   [(0,0),(1,0),(2,0),
                    (0,1),(1,1),(2,1),
                    (0,2),(1,2),(2,2)]
    
    Cell A/0 = ((0,0), point_array[0]
                (1,0), point_array[1]
                (0,1), point_array[3]
                (1,1)) point_array[4]

    Cell B/1 = ((1,0), point_array[1]
                (2,0), point_array[2]
                (1,1), point_array[4]
                (2,1)) point_array[5]

    Cell C/2 = ((0,1), point_array[3]
                (1,1), point_array[4]
                (0,2), point_array[6]
                (1,2)) point_array[7]

    Cell D/3 = ((1,1), point_array[4]
                (2,1), point_array[5]
                (1,2), point_array[7]
                (2,2)) point_array[8]

    '''
    cells = []
    gap = columns
    max_cells = (columns-1)*(rows-1)
    col_stop = columns-1
    for p in range(columns*rows):
        if p == col_stop: 
            p+=1
            quad_pos = (p,p+1,p+gap,p+gap+1)
            col_stop+=columns
            continue
        else:
            quad_pos = (p,p+1,p+gap,p+gap+1)
        cells.append(quad_pos)
        if len(cells) == max_cells:
          break
    # print(f'Cell positions: {cells}')
    return cells

coord_array, cell_positions  = make_coord_array()
# print(f'Cell amount: {len(cell_positions)}')

def draw_point_grid(grid):
    for p in grid:
        pygame.draw.circle(screen,'white',p,5)

lgrid = [(100,100,200,100),
          (100,200,200,200),
          (100,200,100,100),
          (200,100,200,200)]

def draw_grid():
    draw_point_grid(coord_array)
    
    # for line in lgrid:
    #     pygame.draw.line(screen,'white',line[:2], line[2:], 1)

    '''ATENCION hacer rectas de punto en punto es solo para validar
    nuestra grilla de puntos, pero en realidad solo tenemos que
    dibujar una sola gran recta por cada eje objetivo,
    luego los intermedios puntos nos serviran para dibujar el polígono de hover
    y poder formar celdas para el movimiento de nuestras piezas
    '''
    
while running:
    screen.fill("black")
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    mouse_pos = pygame.mouse.get_pos()
    #debemos pasar mouse_pos a algun lugar para verificar
    #continuamente sobre *que* hace hover
    draw_grid()
    check_mouse_hover(mouse_pos, cell_positions)
    
    pygame.display.flip()
    clock.tick(60)
pygame.quit()