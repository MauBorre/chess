import pygame
from scenes import Match

pygame.init()
resolution = (800,800)
screen = pygame.display.set_mode(resolution) # una screen por escena o una screen para todo el juego?
pygame.display.set_caption('Chess')
frame_rate_clock = pygame.time.Clock()
scene_manager_running = True
pause = False
game_variables: dict = {'clock-minutes-limit': 10} # default
# mx = 0
# my = 0
# click = False

control_input: dict[str, bool] = {
    'escape': False,
    'click': False,
    'mouse-x': 0,
    'mouse-y': 0,
}

def update_mouse(coordinates):
    control_input['mouse-x'] = coordinates[0]
    control_input['mouse-y'] = coordinates[1]

def event_handler():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            scene = 'exit'

            # Keyboard
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:

                    # if not pause:
                    #     pause = True
                    #     break
                    # if pause:
                    #     pause = False
                    #     break

                    control_input['escape'] = True

            # Mouse
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    control_input['click'] = True

def match_loop():
    scene = Match(screen, control_input)
    while scene == Match:
        control_input['click'] = False
        event_handler()
        update_mouse(pygame.mouse.get_pos())
        screen.fill("white")
        scene.render() # (variables+updates+display)
        pygame.display.flip()
        frame_rate_clock.tick(60)
    pygame.quit()
        
match_loop()
