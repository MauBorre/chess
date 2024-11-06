from screen_drawer__ import MainMenuDrawer

class MainMenu(MainMenuDrawer) :
    def __init__(self, control_manager):
        self.control = control_manager

view = ...

def draw_text(): ...

def draw_match_btn(): ...

def draw_exit_btn(): ...

def draw_match_modes(): ...

def render(): 
    draw_text()
    if view == 'main':
        draw_match_btn()
        draw_exit_btn()
    if view == 'mode-selection':
        draw_match_modes()


    
    ...