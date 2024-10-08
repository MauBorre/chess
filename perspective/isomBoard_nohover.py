'''Pruebas de tablero isométrico con movimiento
y testeos de intersecciones en bruto
Si presionamos click se dibuja un triángulo'''

import pygame
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
mid_screen = (screen.get_width()/2,screen.get_height()/2)
mid_screen_Vec = pygame.Vector2(mid_screen)

length=300
grid_size=10
offset_step = length/grid_size
movement = offset_step
player_pos = pygame.Vector2(mid_screen)
player_pos.y+=offset_step/2 #fix placement

def draw_triangle(p1,p2,p3):
    pygame.draw.line(screen,('white'),p1,p2)
    pygame.draw.line(screen,('white'),p2,p3)
    pygame.draw.line(screen,('green'),p3,p1) #hipotenusa / angulo objetivo

def board(grid_points=[(0,0),(10,0),(20,0),
                        (0,10),(10,10),(20,10)],
            rows=10,columns=10):

    #board drawing
    offset = 0 
    #vertical lines
    for c in range(columns):
        pygame.draw.line(screen,'white',
                        (mid_screen_Vec.x+length+offset,mid_screen_Vec.y-length),
                        (mid_screen_Vec.x-length+offset,mid_screen_Vec.y+length),1)
        offset+=offset_step

    #intersection points TEST
    offset = 0
    displacement = 0
    for r in range(rows):
        for c in range(columns):
            pygame.draw.circle(screen,'green',((mid_screen_Vec.x+offset-displacement,
                                                    mid_screen_Vec.y+displacement)),4)
            offset+=offset_step
        displacement+=30
        offset = 0

    #horizontal lines
    offset = 0
    for r in range(rows):
        pygame.draw.line(screen,'white',
                        (mid_screen_Vec.x-length,mid_screen_Vec.y+offset),
                        (mid_screen_Vec.x+length,mid_screen_Vec.y+offset),1)
        offset+=offset_step

    #center/player
    pygame.draw.circle(screen,'red',player_pos,4)

while running:
    screen.fill("black")
    # Pygame Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_w: #up
                player_pos.y-=movement
                player_pos.x+=movement
            if event.key == pygame.K_s: #down
                player_pos.y+=movement
                player_pos.x-=movement
            if event.key == pygame.K_a: #left
                player_pos.x-=movement
            if event.key == pygame.K_d: #right
                player_pos.x+=movement
    
    mouse_pos = pygame.mouse.get_pos()
    mousebtns = pygame.mouse.get_pressed()
    if mousebtns[0] == True:
        p1 = mouse_pos
        p2 = (mouse_pos[0],mouse_pos[1]+200)
        p3 = (mouse_pos[0]-200,mouse_pos[1]+200)
        draw_triangle(p1,p2,p3)
    # Render
    board()

    pygame.display.flip()
    clock.tick(60)
pygame.quit()



