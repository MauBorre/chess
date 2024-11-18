import pygame
import match

pygame.init()
resolution = (800,800)
screen = pygame.display.set_mode(resolution)
pygame.display.set_caption('Chess')
frame_rate_clock = pygame.time.Clock()
running = True
# mx = 0
# my = 0
# click = False

control_input = {
    'escape': False,
    'click': False,
    'mouse-x': 0,
    'mouse-y': 0,
}

def update_mouse(coordinates):
    control_input['mouse-x'] = coordinates[0]
    control_input['mouse-y'] = coordinates[1]

def exit_game():
    global running
    running = False

def event_handler():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit_game()

            # Keyboard
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    control_input['escape'] = True
                    break

            # Mouse
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    control_input['click'] = False
                    break
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    control_input['click'] = True
                    break

def run_match():
    match.set_variables(screen, control_input)
    # match.init_content()
    while running:
        event_handler()
        update_mouse(pygame.mouse.get_pos())
        screen.fill("white")
        match.render()
        pygame.display.flip()
        frame_rate_clock.tick(60)
    pygame.quit()
        
run_match()
