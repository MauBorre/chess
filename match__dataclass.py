import pieces

class Black:
    name = 'black'
    positions: dict[int, str] = pieces.black_positions.copy()
    in_base_pawns: list[int] = [bpawn for bpawn in pieces.origins['black']['pawn']]
    threat_on_enemy: dict[str, int] = {piece:[] for piece in pieces.origins['black']}
    king_legal_moves: list[int] = []
    direct_threat_origin = 'single' or 'multiple' or 'none'
    direct_threat_trace: list[int] = []
    
class White:
    name = 'white'
    positions: dict[int, str] = pieces.white_positions.copy()
    in_base_panws: list[int] = [wpawn for wpawn in pieces.origins['white']['pawn']]
    threat_on_enemy: dict[str, int] = {piece:[] for piece in pieces.origins['white']}
    king_legal_moves: list[int] = []
    direct_threat_origin = 'single' or 'multiple' or 'none'
    direct_threat_trace: list[int] = []
