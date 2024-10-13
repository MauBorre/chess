'''Notas de desarrollo - primero version 2d

Haremos una version 2d plana de arriba
para testear el comportamiento de piezas, controles, tablero
y demas.

Una vez tengamos esto pensaremos el modo en perspectiva porque
será algo mas tedioso.
'''

'''Notas de desarrollo - un solo loop es dañino?

Quizas nuestro concepto de 'escena' signifique en realidad
que cada escena es un loop independiente del resto.

De esta forma en cada loop tenemos un gran gobierno sobre
los controles presionados.

Sin embargo sí necesitamos un *decididor* de qué y cuándo
mostrar determinada escena'''

import pygame
from scenes import MainMenuSCENE, MatchSCENE

class GameMaster:
    '''Es GameMaster un scene manger ,un control manager
    y un "default maker"?
    Es una clase de las cuales todas las "escenas" comparten *cosas*?
    Es maestro o es esclavo entonces?
    El concepto de "escena" no es tan fuerte aún,
    pero siento que van a ser necesarias para hace transiciones.
    '''
    starting_volume : float #volume in db
    def __init__(self):
        pygame.init()
        #default values
        self.resolution = (800,800)
        self.screen = pygame.display.set_mode(self.resolution)
        pygame.display.set_caption('Chess')
        self.clock = pygame.time.Clock()

        # Small font
        # ...

        # Medium font
        self.m_font_size = 22
        self.medium_font = pygame.font.Font(None,self.m_font_size)

        # Large font
        self.l_font_size = 28
        self.large_font = pygame.font.Font(None,self.l_font_size)

        self.assets = ...#{'piezas': load_images('assets/piezas')} # colección de paths?

        # scene manager
        self.scene_manager_running = True
        self.paused = False
        self.scene_manager = MainMenuSCENE
        self.match_mode = '' # Scenes set this variable 
        
        # control manager
        self.mx = 0
        self.my = 0
        self.click = False

    def update_mouse(self,coordinates):
        self.mx = coordinates[0]
        self.my = coordinates[1]

    def render_scene(scene):
        #scene.init()
        #scene.loop()
            #internamente la escena hace .update() y luego .draw()
        ...

    def make_mode(self):
        '''PARTIDA es una colección de ordenes
        - modo: 1 jugador
        - j1_color: blancas
        - je_color: negras
        - tiempo: desactivado
        '''
        '''Las cosas cambian segun el modo q se elija
        Los modos son J1 vs J2 | J1 vs IA

        El jugador es quien selecciona estos modos

        Deberían los modos ser 'importados' a este programa
        para trabajarlos mas facilmente?

        >>Son los modos de juego un 'estado complejo' del juego?
            Modo elegido: j1 vs j2
            **el ajedrez tiene distintos modos por tiempo**
                -> entonces
                    elegir color
                    darle el control a x jugador
                        comienza danza de controles
                        hasta encontrar un ganador
                            ->al encontrar ganador mostrar
                            post_game_menu
        '''
        set_colors = ...#player choice over menu focus
        return {}

    def match_SCENE(self):
        current_scene = MatchSCENE(self)
        while self.scene_manager == MatchSCENE:
            self.click = False
            # Pygame Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.scene_manager = 'exit'

                # Keyboard Controls
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # if self.pre_move_focus:
                            # not self.pre_move_focus
                        if not self.paused: #and not self.pre_move_focus
                            self.paused = True
                            break
                        if self.paused:
                            self.paused = False
                            break

                    if event.key == pygame.K_w: #up
                        #move menu_pausa focus UP
                        #move board focus UP
                        ...
                    if event.key == pygame.K_s: #down
                        #move menu_pausa focus DOWN
                        #move board focus DOWN
                        ...
                    if event.key == pygame.K_a: #left
                        #move menu_pausa focus LEFT
                        #move board focus LEFT
                        ...
                    if event.key == pygame.K_d: #right
                        #move menu_pausa focus RIGHT
                        #move board focus RIGHT
                        ...

                # Mouse
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.click = True
            # Mouse
            self.update_mouse(pygame.mouse.get_pos())
            '''mousebtns = pygame.mouse.get_pressed()
            if mousebtns[0] == True:
                # Movemos la pieza a la grilla hovereada legal
                # Clickeamos el menu element
                ...
            if mousebtns[2] == True:
                # Des-seleccionamos
                ...'''

            # Scene Render
            self.screen.fill("white")
            current_scene.draw()

            # Pygame Loop Closer
            pygame.display.flip()
            self.clock.tick(60)
    
    def main_menu_SCENE(self):
        current_scene = MainMenuSCENE(self)
        while self.scene_manager == MainMenuSCENE:
            self.click = False
            # Pygame Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.scene_manager = 'exit'

                # Keyboard Controls
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        #if active sub_group (e.g. options) = go to previous menu
                        if current_scene.view == 'mode-selection':
                            current_scene.view = 'main'
                            break
                        #if no sub_group (e.g. options) = salir del juego
                        if current_scene.view == 'main':
                            self.scene_manager = 'exit'
                    if event.key == pygame.K_w: #up
                        #move current_menu focus UP
                        #move board focus UP
                        ...
                    if event.key == pygame.K_s: #down
                        #move current_menu focus DOWN
                        #move board focus DOWN
                        ...
                    if event.key == pygame.K_a: #left
                        #move current_menu focus LEFT
                        #move board focus LEFT
                        ...
                    if event.key == pygame.K_d: #right
                        #move current_menu focus RIGHT
                        #move board focus RIGHT
                        ...

                # Mouse
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.click = True

            self.update_mouse(pygame.mouse.get_pos())

            # Scene Render 
            self.screen.fill("black")
            current_scene.draw() # no estamos updateando cosas acá tambien?

            # Pygame Loop Closer
            pygame.display.flip()
            self.clock.tick(60)
    
    def start_loop(self,scene=None):
        if scene!=None:
            self.scene_manager = scene
        # Registro de escenas --------------------------
        while self.scene_manager_running:
            if self.scene_manager == MainMenuSCENE:
                self.main_menu_SCENE()
            if self.scene_manager == MatchSCENE:     
                self.match_SCENE()
            if self.scene_manager == 'exit':
                self.scene_manager_running = False
        # ----------------------------------------------
        pygame.quit()
    
class ControlManager: # clase usada por quién? Es necesaria una clase para los controles?
    '''CONTROLES

    Jugador 1 o 2 seran las únicas entidades que tendran controles.
    Pero el enemigo puede realizar las mismas acciones.

    El juego podrá ser controlado con el mouse y con el teclado

    >> Mouse:
        Click izq
            seleccion general
        Click der
            des-seleccion general

    >> Teclado:
        Wasd - flechitas
            movimiento en menues
            movimiento de seleccion
        Enter
            confirmacion de seleccion  
        Escape
            desconfirmacion de seleccion

    >> Joystick:
        Flechitas - analógicos:
            movimiento en menues
            movimiento de seleccion
        Equis
            confirmacion de seleccion
        Circulo / Triángulo
            desconfirmacion de seleccion
    '''
    '''A ControlManager hay que preguntarle:
    ¿qué debería hacer *este input* *ahora*?'''
    #es esto solo un dict?
    #una colección de dicts?
    ...

if __name__ == '__main__':
    gm = GameMaster()
    gm.start_loop(scene=MatchSCENE)
