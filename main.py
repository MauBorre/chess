import pygame
from scenes import MainMenu, Match

class GameMaster:
    '''

    GameMaster debería ser un -main loop master-


    Es GameMaster un scene manger ,un control manager
    y un "default maker"?

    Es una clase de las cuales actualmente todas las "escenas" consumen
    controles y SCREEN (y variables -de juego-).

    Es una clase que instancia y maneja escenas.

    Si es maestro debería notificar cosas, no "ser consumido"
    '''
    def __init__(self):
        pygame.init()

        # default values (config)
        self.resolution = (800,800)
        self.screen = pygame.display.set_mode(self.resolution) # una screen por escena o una screen para todo el juego?
        pygame.display.set_caption('Chess')
        self.frame_rate_clock = pygame.time.Clock()

        # scene manager
        '''Por ahora las escenas consumen screen, controles y "variable de pausa"
        de GameMaster.
        GameMaster controla vistas de las escenas.
        '''
        self.scene_manager_running = True
        self.pause = False
        self.scene_manager = MainMenu

        # Tenemos que pasar las variables de juego seleccionadas en la interfaz aquí
        # ya que será este manager quien instancie la escena Match
        self.game_variables: dict = {'mode': 'j1-vs-j2', 'clock-minutes-limit': 10} #default
        
        # control manager -> Consumidos por escenas
        self.mx = 0
        self.my = 0
        self.click = False

        self.control_input: dict[str, bool] = {
            'up': False,
            'down': False,
            'left': False,
            'right': False,
            'enter': False,
            'escape': False,
            'click': False,
            'mouse0': False,
            'mouse2': False
        }

    def update_mouse(self,coordinates):
        self.mx = coordinates[0]
        self.my = coordinates[1]
    
    def match_event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.scene_manager = 'exit'

                # Keyboard Controls
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # if self.pre_move_focus:
                            # not self.pre_move_focus
                        # if not self.pause: #and not self.pre_move_focus
                        #     self.pause = True
                        #     break
                        # if self.pause:
                        #     self.pause = False
                        #     break
                        self.control_input['excape'] = True

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
                        # self.click = True
                        self.control_input['click'] = True


    def match_loop(self):
        current_scene = Match(master=self)
        while self.scene_manager == Match:
            self.click = False

            # Pygame Events
            self.match_event_handler()
                
            # Mouse
            self.update_mouse(pygame.mouse.get_pos())
            # Esto va a servir, no borrar: 
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
            current_scene.render() # (variables+updates+display)
            
            # Pygame Loop Closer
            pygame.display.flip()
            self.frame_rate_clock.tick(60)
    
    def mainMenu_event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.scene_manager = 'exit'

            # Keyboard Controls
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.control_input['escape'] = True
                    #if active sub_group (e.g. options) = go to previous menu
                    # if current_scene.view == 'mode-selection':
                    #     current_scene.view = 'main'
                    #     break
                    # #if no sub_group (e.g. options) = salir del juego
                    # if current_scene.view == 'main':
                    #     self.scene_manager = 'exit'
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
                    self.control_input['click'] = True
                    # self.click = True

    def main_menu_loop(self):
        current_scene = MainMenu(master=self)
        while self.scene_manager == MainMenu:
            self.click = False

            # Pygame Events
            self.mainMenu_event_handler()
            self.update_mouse(pygame.mouse.get_pos())

            # Scene Render 
            self.screen.fill("black")
            current_scene.render() # (variables+updates+display)

            # Pygame Loop Closer
            pygame.display.flip()
            self.frame_rate_clock.tick(60)
    
    '''Puede ser bueno para manejar multiples escenas pero creo que simplemente
    para esta versión pública no lo usaremos.'''
    def start_manager(self,scene=None): # Es responsabilidad del manager 100%
        if scene!=None:
            self.scene_manager = scene # defaults MainMenu (init)
        # Registro de escenas --------------------------
        while self.scene_manager_running:
            if self.scene_manager == MainMenu:
                self.main_menu_loop()
                #main_menu.render()
            if self.scene_manager == Match:     
                self.match_loop()
                #match.render()
            if self.scene_manager == 'exit':
                self.scene_manager_running = False
        # ----------------------------------------------
        pygame.quit()

if __name__ == '__main__':
    gm = GameMaster()
    gm.start_manager(scene=Match)
