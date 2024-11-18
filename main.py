import pygame
from match import Match

class GameManager:

    def __new__(cls):
        pygame.init()
        cls.resolution = (800,800)
        cls.screen = pygame.display.set_mode(cls.resolution)
        pygame.display.set_caption('Chess')
        cls.frame_rate_clock = pygame.time.Clock()
        cls.running = True
        cls.control_input = {
            'escape': False,
            'click': False,
            'mouse-x': 0,
            'mouse-y': 0,
        }
        cls.match = Match(cls.screen, cls.control_input)
        cls.run_game()

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
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    cls.control_input['escape'] = False
                    break

            # Mouse
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    cls.control_input['click'] = True
                    break
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    cls.control_input['click'] = False
                    break

    @classmethod
    def run_game(cls):
        while cls.match.running:
            cls.event_handler()
            cls.update_mouse(pygame.mouse.get_pos())
            cls.screen.fill("white")
            cls.match.render()
            pygame.display.flip()
            cls.frame_rate_clock.tick(60)
        pygame.quit()
        
GameManager()
