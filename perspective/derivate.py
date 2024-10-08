'''
Un juego derivado del desarrollo del chess
'''

'''
Tenemos un 'movimiento en perspectiva' base

y si le agregamos un divertidisimo auto-lock?
'''

import pygame
from math import sin, cos, pi, radians, degrees
import random

pygame.init()
screen = pygame.display.set_mode((500, 500))
clock = pygame.time.Clock()
running = True
midScreen = (screen.get_width()/2,screen.get_height()/2)
midScreen_pos = pygame.Vector2(midScreen)
start_screen = (0,0)
start_screen_vec = pygame.Vector2(start_screen)
player_pos = pygame.Vector2((midScreen[0]-20,midScreen[1]+30))
platform_pos = pygame.Vector2((midScreen[0]+10,midScreen[1]-90))
enemy_pos = pygame.Vector2((midScreen[0]+34,midScreen[1]-73))

grid_size = 5
length = 300

def platform():
    pygame.draw.line(screen,'white',(platform_pos.x+20,platform_pos.y-20),(platform_pos.x-20,platform_pos.y+20))
    pygame.draw.line(screen,'white',(platform_pos.x+20,platform_pos.y-20),(platform_pos.x-40,platform_pos.y-40))
    pygame.draw.line(screen,'white',(platform_pos.x-80,platform_pos.y),(platform_pos.x-40,platform_pos.y-40))
    pygame.draw.line(screen,'white',(platform_pos.x-80,platform_pos.y),(platform_pos.x-20,platform_pos.y+20))
    pygame.draw.line(screen,'white',(platform_pos.x-20,platform_pos.y+80),(platform_pos.x-20,platform_pos.y+20))
    pygame.draw.line(screen,'white',(platform_pos.x-80,platform_pos.y+60),(platform_pos.x-20,platform_pos.y+80))
    pygame.draw.line(screen,'white',(platform_pos.x-80,platform_pos.y+60),(platform_pos.x-80,platform_pos.y))
    pygame.draw.line(screen,'white',(platform_pos.x+20,platform_pos.y+40),(platform_pos.x+20,platform_pos.y-20))
    pygame.draw.line(screen,'white',(platform_pos.x+20,platform_pos.y+40),(platform_pos.x-20,platform_pos.y+80))
def grid():
    '''
    'coordenadas triangulares' representadas parcialmente con lineas.
    Pareciera que solo debemos controlar un 'ofset' por ahora,
    aplicandolo en el lugar correcto.
    se utiliza una pequeña formula de offset para el movimiento en
    grilla
    '''
    offset = 0
    #enemy
    pygame.draw.circle(screen,'red',enemy_pos,4)

    platform()
    
    for i in range(grid_size):
        if i != 0:
            pygame.draw.line(screen,'white',
                            (midScreen_pos.x+length+offset,midScreen_pos.y-length),
                            (midScreen_pos.x-length+offset,midScreen_pos.y+length),1) #vertical
            pygame.draw.line(screen,'red',
                            (midScreen_pos.x-length,midScreen_pos.y+offset),
                            (midScreen_pos.x+length,midScreen_pos.y+offset),1) #horizontal
        offset+=120
    
    #center/player
    pygame.draw.circle(screen,'green',player_pos,4)

    #auto-lock
    '''
    Necesitamos algun mecanismo de verificacion de interseccion
    de lineas

    Como se maneja esta mecanica frente a varios enemigos?
    '''

    pygame.draw.line(screen,'green',player_pos,enemy_pos)

def draw_triangle(p1,p2,p3):  
    # pygame.draw.line(screen,('white'),p1,p2)
    # pygame.draw.line(screen,('white'),p2,p3)
    pygame.draw.line(screen,('green'),p3,p1) #hipotenusa / angulo objetivo

player_movement = length/grid_size
while running:
    screen.fill("black")
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            # if event.key == pygame.K_w: #up
            #     player_pos.y-=player_movement
            #     player_pos.x+=player_movement
                
            # if event.key == pygame.K_s: #down
            #     player_pos.y+=player_movement
            #     player_pos.x-=player_movement
            #     # platform_pos.y+=player_movement
            #     # platform_pos.x-=player_movement
            # if event.key == pygame.K_a: #left
            #     player_pos.x-=player_movement
            #     # platform_pos.x-=player_movement
            # if event.key == pygame.K_d: #right
            #     player_pos.x+=player_movement
            #     # platform_pos.x+=player_movement
            
            # if event.key == pygame.K_i:
            #     platform_pos.y-=1
            # if event.key == pygame.K_k:
            #     platform_pos.y+=1
            # if event.key == pygame.K_j:
            #     platform_pos.x-=1
            # if event.key == pygame.K_l:
            #     platform_pos.x+=1

    keys = pygame.key.get_pressed()

    #platform
    if keys[pygame.K_i]: #up
        platform_pos.y-=1
    if keys[pygame.K_k]: #down
        platform_pos.y+=1
    if keys[pygame.K_j]: #left
        platform_pos.x-=1
    if keys[pygame.K_l]: #right
        platform_pos.x+=1

    #player
    if keys[pygame.K_w]: #up
        player_pos.y-=4
        player_pos.x+=4
    if keys[pygame.K_s]: #down
        player_pos.y+=4
        player_pos.x-=4
    if keys[pygame.K_a]: #left
        player_pos.x-=4
        player_pos.y-=4/3
    if keys[pygame.K_d]: #right
        player_pos.x+=4
        player_pos.y+=4/3
    


    mousebtns = pygame.mouse.get_pressed()
    if mousebtns[0] == True:
        mouse_pos = pygame.mouse.get_pos()
        p1 = mouse_pos
        p2 = (mouse_pos[0],mouse_pos[1]+200)
        p3 = (mouse_pos[0]-200,mouse_pos[1]+200)
        draw_triangle(p1,p2,p3)
    if mousebtns[2] == True:
        mouse_pos = pygame.mouse.get_pos()
        p1 = mouse_pos
        p2 = (mouse_pos[0],mouse_pos[1]-200)
        p3 = (mouse_pos[0]-200,mouse_pos[1]-200)
        draw_triangle(p1,p2,p3)
       
    grid()
    pygame.display.flip()
    clock.tick(60)
    
pygame.quit()