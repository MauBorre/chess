from screen_drawer__ import MatchDrawer
import board
from board import NORTE, NOR_ESTE, NOR_OESTE, SUR, SUR_OESTE, SUR_ESTE, ESTE, OESTE # piece directions
from board import row_of_
import pieces

class PlayerColor__TeamUnit:
    name = ...

    initial_positions = ...

    actual_positions = ...

    visualFeedback_rects = ...

    pieces = ...

class Black(PlayerColor__TeamUnit):
    name = 'black'
    

class White(PlayerColor__TeamUnit):
    name = 'white'

class Turn:
    attacker = Black()
    defender = White()

    def swap():
        Turn.defender, Turn.attacker = Turn.attacker, Turn.defender

class Match(MatchDrawer):
    def __init__(self, instructions):
        self._instructions = instructions
        self._control_input = dict()
        Turn()
            
        #screen
        #controles
    
def start_match(instructions):
    '''Instanciar objeto Match como corresponde
    y devolverlo'''

    game_match = Match(instructions)
    return game_match

game_match = start_match(dict())

def render(controller_input, screen):

    # Peripherals
    game_match._control_input = controller_input

    # UI/HUD
    game_match.draw_HUD_title()
    game_match.draw_match_mode()

    # Game Board


print(Turn.attacker.name)
Turn.swap()
print(Turn.attacker.name)