from screen_drawer__ import MatchDrawer
import board
from board import NORTE, NOR_ESTE, NOR_OESTE, SUR, SUR_OESTE, SUR_ESTE, ESTE, OESTE # piece directions
from board import row_of_
import pieces

class Black:
    name = 'black'
    positions: dict[int, str] = pieces.black_positions.copy()
    in_base_pawns: list[int] = [bpawn for bpawn in pieces.origins['black']['pawn']]
    threat_on_enemy: dict[str, int] = {piece:[] for piece in pieces.origins['black']}
    king_legal_moves: list[int] = []
    threat_origin = 'single' or 'mult' or 'none'
    # singleOrigin_directThreat: bool | None = None
    direct_threat_trace: list[int] = []
    
class White:
    name = 'white'
    positions: dict[int, str] = pieces.white_positions.copy()
    in_base_panws: list[int] = [wpawn for wpawn in pieces.origins['white']['pawn']]
    threat_on_enemy: dict[str, int] = {piece:[] for piece in pieces.origins['white']}
    king_legal_moves: list[int] = []
    threat_origin = 'single' or 'mult' or 'none'
    # singleOrigin_directThreat: bool | None = None
    direct_threat_trace: list[int] = []

class Turn:
    attacker = Black()
    defender = White()

    def swap():
        Turn.defender, Turn.attacker = Turn.attacker, Turn.defender

class Match(MatchDrawer):
    def __init__(self, instructions, ctrl_emitter, screen):
        super().__init__(screen)
        self._instructions = instructions
        self._control_input = ctrl_emitter
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
