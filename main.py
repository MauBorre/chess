import pygame
from scenes import Match

class GameMaster:
    def __init__(self):
        pygame.init()

        # default values - config
        self.resolution = (800,800)
        self.screen = pygame.display.set_mode(self.resolution) # una screen por escena o una screen para todo el juego?
        pygame.display.set_caption('Chess')
        self.frame_rate_clock = pygame.time.Clock()
        self.scene_manager_running = True
        self.pause = False
        self.scene_manager = Match
        self.game_variables: dict = {'clock-minutes-limit': 10} # default
        self.mx = 0
        self.my = 0
        self.click = False

        self.control_input: dict[str, bool] = {
            'escape': False,
            'click': False,
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

                        # if not self.pause:
                        #     self.pause = True
                        #     break
                        # if self.pause:
                        #     self.pause = False
                        #     break

                        self.control_input['excape'] = True

                # Mouse
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        # self.click = True
                        self.control_input['click'] = True

    def match_loop(self):
        current_scene = Match(master=self)
        while self.scene_manager == Match:
            self.click = False
            self.match_event_handler()
            self.update_mouse(pygame.mouse.get_pos())
            self.screen.fill("white")
            current_scene.render() # (variables+updates+display)
            pygame.display.flip()
            self.frame_rate_clock.tick(60)
        pygame.quit()
        
if __name__ == '__main__':
    gm = GameMaster()
    gm.match_loop()
