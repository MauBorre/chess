import pygame
from match import Match

class GameManager:
    pygame.init()
    resolution = (800,800)
    screen = pygame.display.set_mode(resolution)
    pygame.display.set_caption('Chess')
    frame_rate_clock = pygame.time.Clock()
    running = True

    control_input = {
        'escape': False,
        'click': False,
        'mouse-x': 0,
        'mouse-y': 0,
    }

    @classmethod
    def update_mouse(cls, coordinates):
        cls.control_input['mouse-x'] = coordinates[0]
        cls.control_input['mouse-y'] = coordinates[1]

    @classmethod
    def exit_game(cls):
        cls.running = False

    @classmethod
    def event_handler(cls):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cls.exit_game()

                # Keyboard
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        cls.control_input['escape'] = True
                        break

                # Mouse
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        cls.control_input['click'] = False
                        break
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        cls.control_input['click'] = True
                        break

    '''Escapar a dividir screen y control_input parece realmente
    inútil, siempre se nos adhiere junto a la lógica del juego de
    algúna manera.
    No debemos instanciar a un "Match" con estos valores, pero sí
    siento que en algún aspecto conviene inicializar ALGO-IMPORANTE
    por razones de reiniciar partida por ejemplo (que encima podría
    incluir cambios en las reglas de juego...).'''

    @classmethod
    def run_match(cls):
        Match(cls.screen, cls.control_input)
        while cls.running:
            cls.event_handler()
            cls.update_mouse(pygame.mouse.get_pos())
            cls.screen.fill("white")
            Match.render()
            pygame.display.flip()
            cls.frame_rate_clock.tick(60)
        pygame.quit()
        
GameManager.run_match()
