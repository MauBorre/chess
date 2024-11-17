import pygame
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
    threat_origin = 'single' or 'multiple' or 'none'
    # singleOrigin_directThreat: bool | None = None
    direct_threat_trace: list[int] = []
    
class White:
    name = 'white'
    positions: dict[int, str] = pieces.white_positions.copy()
    in_base_panws: list[int] = [wpawn for wpawn in pieces.origins['white']['pawn']]
    threat_on_enemy: dict[str, int] = {piece:[] for piece in pieces.origins['white']}
    king_legal_moves: list[int] = []
    threat_origin = 'single' or 'multiple' or 'none'
    # singleOrigin_directThreat: bool | None = None
    direct_threat_trace: list[int] = []

class Attacker: ...
class Defender: ...

class Turn:
    attacker = Black()
    defender = White()

    def swap():
        Turn.defender, Turn.attacker = Turn.attacker, Turn.defender

class Board: ...

class Match(MatchDrawer):
    def __init__(self, instructions, ctrl_emitter, screen):
        super().__init__(screen)
        self._instructions = instructions
        self._control_input = ctrl_emitter
        Turn()
        Board()
            
        #screen
        #controles
    
    def board():
        ...
    
def start_match(instructions):
    '''Instanciar objeto Match como corresponde
    y devolverlo'''

    match_ = Match(instructions)
    return match_

game_match = start_match(dict())

def render(
    game_matchObj: Match,
    controller_input: dict[str, bool],
    screen: pygame.Surface
    ):

    # Peripherals
    game_matchObj._control_input = controller_input
    game_matchObj.screen = screen

    # UI/HUD
    game_matchObj.draw_HUD_title()
    game_matchObj.draw_match_mode()

    # Game Board
    game_matchObj.board()


print(Turn.attacker.name)
Turn.swap()
print(Turn.attacker.name)
