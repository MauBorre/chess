#https://stackoverflow.com/questions/63521847/finding-every-point-of-intersection-of-multiple-lines-using-pygame-in-python-for
import pygame
import math

pygame.init() 
WINDOW_SIZE = [800, 600]
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("Array Backed Grid")
done = False
clock = pygame.time.Clock()

def lineLineIntersect(P0, P1, Q0, Q1):  
    '''
    Esto funciona bien, pero necesito hacer el calculo en base
    a una recta y un punto
    '''
    d = (P1[0]-P0[0]) * (Q1[1]-Q0[1]) + (P1[1]-P0[1]) * (Q0[0]-Q1[0]) 
    if d == 0:
        return None
    t = ((Q0[0]-P0[0]) * (Q1[1]-Q0[1]) + (Q0[1]-P0[1]) * (Q0[0]-Q1[0])) / d
    u = ((Q0[0]-P0[0]) * (P1[1]-P0[1]) + (Q0[1]-P0[1]) * (P0[0]-P1[0])) / d
    if 0 <= t <= 1 and 0 <= u <= 1:
        return round(P1[0] * t + P0[0] * (1-t)), round(P1[1] * t + P0[1] * (1-t))
    return None

def mouse_pos_intersect(p0, p1, mouse):
    #return coordenada exacta de intersección
    #o
    #return None
    ...

board_lines = [
    ( 13,15,462,15 ), ( 13,469,462,469 ), #lin1 and line2,outer rect
    ( 62,86,409,86 ), ( 62,389,409,389 ), #line3 and l4,mid reect
    ( 114,186,360,186 ), ( 114,318,360,318 ), #line5,l6,internl rect
    ( 13,15,13,469 ), ( 462,12,462,469 ), #line9,l10,left and right sides
    ( 62,86,62,389 ), ( 409,85,409,389 ), #l7,l8left and right sides
    ( 114,186,114,316), ( 360,187,360,318 ), #l11,lin12left and right sides
    ( 237,15,237,186 ), ( 237,469,237,320 ), #upper V.line,lowerV
    ( 13,242,113,242 ), ( 360,242,462,242 ) #rIGHT LEFT hoRIZONTAL LINE
] 

intersectionPoints = []
for i, line1 in enumerate(board_lines):
    for line2 in board_lines[i:]:
        isectP = lineLineIntersect(line1[:2], line1[2:], line2[:2], line2[2:])
        if isectP:
            intersectionPoints.append(isectP)
 
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                done = True
    screen.fill('black')

    for line in board_lines:
        pygame.draw.line(screen, 'red', line[:2], line[2:], 3)

    for isectP in intersectionPoints:
        pygame.draw.circle(screen, 'green', isectP, 5)

    mouse_pos = pygame.mouse.get_pos()
    #consumir puntos de interes y mouse_pos
    #puntos de recta?...
    '''
    intersecting = mouse_pos_intersect(p0, p1, mouse_pos)
    if intersecting:
        pygame.draw.circle(screen,'green',intersecting,5)
    '''

    clock.tick(60)
    pygame.display.flip()
 
pygame.quit()