import pygame
import font, board, pieces
from board import NORTE, NOR_ESTE, NOR_OESTE, SUR, SUR_OESTE, SUR_ESTE, ESTE, OESTE # piece directions
from board import row_of_
from dataclasses import dataclass, field

'''Anotaciones lógica núcleo

>> ThreatOn attacker/defender
    kill-movement's *del enemigo* que caen en casillero rey TARGET o adyacencias legales.
    Puede ser DIRECTO (jaque) o INDIRECTO (restringe king_legal_moves).

    ANTES DE MOVER:
        El atacante debe revisar, dentro de sus movimientos posible, si su movimiento -expone al rey-
        al defensor.

    DESPUES DE MOVER:
        El defensor debe revisar si sus posibles movimiento exponen al rey al atacante, evaluando así
        "con qué posibilidades de movimiento quedó".
    
    El threat puede MATARSE o BLOQUEARSE
        A menos que haya más de un orígen de amenaza DIRECTA -> solo el rey moviendose puede escapar.

    Threat de bishop, queen y tower pueden bloquearse
    Threat de pawn y knight no pueden bloquearse

>> Color-King-legalMovements
    Posición actual + posibles movimientos (bloqueos aliados / casilleros threat).

>> defender.legalMoves (kingSupport):
    Actualizadas luego de que movió el atacante.
    Exhibe "si alguien puede hacer algo", mas no "dónde".
    Inexistentes si hay amenaza de orígen múltiple.

    Para fabricarlas correctamente, debemos comprobar y desestimar
        - Movimientos inv. por bloqueo.
        - Movimientos inv.  por exposición al rey.

Cuando existe origen de amenaza directa 'single':
    Únicos movimientos posibles: bloquear o matar la amenaza.
    > Bloquear una amenaza es movement coincidente en defender.direct_threat_trace
    > Matar la amenaza es kill-movement coincidente en defender.single_threat_standpoint
    NO verificar exposing-movements.
'''

@dataclass
class PlayerTeamUnit:
    name: str
    direct_threat_origin: str
    direct_threat_trace: list[int] = field(default_factory=list)
    positions: dict[int, str] = field(default_factory=dict)
    pawns_in_origin: list[int] = field(default_factory=list)
    threat_on_enemy: dict[str, int] = field(default_factory=dict)
    king_legal_moves: list[int] = field(default_factory=list)
    castling_enablers: dict[int, str] = field(default_factory=dict)
    single_threat_standpoint: int | None
    king_banned_direction: int | None
    legal_moves: set[str] 

    def clear(self):
        self.threat_on_enemy.clear()
        self.king_legal_moves.clear()
        self.direct_threat_trace.clear()
        self.direct_threat_origin = 'none'
        self.single_threat_standpoint = None
        self.king_banned_direction = None
        self.legal_moves.clear()        
    
    def __str__(cls):
        return cls.name

# Configurations -----------------------------------------------
screen: pygame.Surface
control_input: dict
def set_variables(screen_, control_input_):
    global screen, control_input
    screen = screen_
    control_input = control_input_
mid_screen_coordinates = (screen.get_width()/2, screen.get_height()/2)
mid_screen = pygame.Vector2(mid_screen_coordinates)
board.place(mid_screen)
# ---------------------------------------------------------------

# Initial content -----------------------------------------------
black = PlayerTeamUnit(
    name = 'black',
    direct_threat_origin = 'none', # or 'multiple' or 'single'
    direct_threat_trace = [],
    positions = pieces.black_positions.copy(),
    pawns_in_origin = [bpawn for bpawn in pieces.origins['black']['pawn']],
    threat_on_enemy = {piece:[] for piece in pieces.origins['black']},
    king_legal_moves = [],
    castling_enablers = {0: 'west-rook', 4: 'king', 7: 'east-rook'},
    single_threat_standpoint = None,
    king_banned_direction = None,
    legal_moves = set()
)
white = PlayerTeamUnit(
    name = 'white',
    direct_threat_origin = 'none', # or 'multiple' or 'single'
    direct_threat_trace = [],
    positions = pieces.white_positions.copy(),
    pawns_in_origin = [wpawn for wpawn in pieces.origins['white']['pawn']],
    threat_on_enemy = {piece:[] for piece in pieces.origins['white']},
    king_legal_moves = [],
    castling_enablers = {56: 'west-rook', 60: 'king', 63: 'east-rook'},
    single_threat_standpoint = None,
    king_banned_direction = None,
    legal_moves = set(),
)

# core game variables
gameClock_minutesLimit: int = 10
pause = False
move_here: int | None = None
winner: bool = False
stalemate: bool = False # Ahogado | draw
match_state: str = '' # HUD info
player_deciding_match: bool = False
killing: bool = False
finish_turn: bool = False # turn halt utility
# pawn promotion
player_deciding_promotion: bool = False
pawnPromotion_selection: str = ''
promoting_pawn: int | None = None
# king castling
castling: bool = False
castling_direction: str = ''
turn_attacker: PlayerTeamUnit = white
turn_defender: PlayerTeamUnit = black

# turn_defender.legal_moves: set[str] = set() # NO se considera en SWAP

# board feedback utilities
pieceValidMovement_posDisplay: dict[int, pygame.Rect] = {}
pieceValidKill_posDisplay: dict[int, pygame.Rect] = {}
kingValidCastling_posDisplay: dict[int, pygame.Rect] = {}

# turn times
globaltime_SNAP: int = pygame.time.get_ticks()
whitetime_SNAP: int = pygame.time.get_ticks()
blacktime_SNAP: int = pygame.time.get_ticks()
pausetime_SNAP: int = 0
current_turn_time: int = 0
'''El tiempo nos llega en forma de "minutos totales", pero debemos transformarlo
a segundos y minutos por separado para finalmente  y correctamente visualizarlo.
'''
black_turn_time: int = gameClock_minutesLimit * 60
black_turn_minutes: str = str(int(black_turn_time/60))
black_turn_seconds: str = '00'

white_turn_time: int = gameClock_minutesLimit * 60
white_turn_minutes: str = str(int(white_turn_time/60))
white_turn_seconds: str = '00'
# clock + or - remnants
white_time_leftover: int = 0
black_time_leftover: int = 0
pause_time_leftover: int = 0
# ---------------------------------------------------------------

def draw_text(text, color, x, y, center=True, font_size='large'):
    _font = font.large_font if font_size=='large' else font.medium_font
    surface = screen
    textobj = _font.render(text,1,color)
    text_width = textobj.get_width()
    text_height = textobj.get_height()
    textrect = textobj.get_rect()
    if center: textrect.topleft = (x - text_width/2, y - text_height/2) # anchors placement at center
    else: textrect.topleft = (x,y)
    surface.blit(textobj,textrect)

def init_content(): ...

def check_pawn_promotion():
    global pause, player_deciding_promotion, finish_turn
    # Obtener standpoints PAWN de attacker
    pawn_standpoints: list[int] = get_piece_standpoint(color=turn_attacker,piece="pawn")
    
    # Revisar si algun pawn llegó a la fila objetivo 
    if turn_attacker == 'white':
        for _pawn in pawn_standpoints:
            if _pawn in row_of_(0): # NORTHMOST ROW
                promoting_pawn = _pawn
                pause = True
                player_deciding_promotion = True
                finish_turn = False
    
    # Revisar si algun pawn llegó a la fila objetivo
    if turn_attacker == 'black':
        for _pawn in pawn_standpoints:
            if _pawn in row_of_(63): # SOUTHMOST ROW
                promoting_pawn = _pawn
                pause = True
                player_deciding_promotion = True
                finish_turn = False
    
    # allows turn to finish
    if promoting_pawn == None: finish_turn = True

def make_promotion():
    if pawnPromotion_selection != '':
        turn_attacker.positions.update({promoting_pawn: pawnPromotion_selection})
        pawnPromotion_selection == ''
        promoting_pawn = None
        finish_turn = True

def trace_direction_walk(
    defKing_standpoint: int,
    mixedDirections_threats: list[int],
    attThreat_standpoint: int,
    ) -> list[int]:
    '''Caminamos desde el rey hasta la amenaza devolviendo una traza.
    INCLUYE STANDPOINT DEL REY PERO NO DE LA AMENAZA.
    Prohibe al rey -actual defensor- dirigirse en la dirección de la amenaza.'''

    # direcciones
    cardinal_directions = [NORTE,SUR,ESTE,OESTE,NOR_OESTE,NOR_ESTE,SUR_OESTE,SUR_ESTE]
    walk_trace: set[int] = set()

    for direction in cardinal_directions:
        walk_trace.clear()
        walk_trace.add(defKing_standpoint)
        for mult in range(1,8):
            walk = defKing_standpoint+direction*mult
            if direction == ESTE or direction == OESTE:
                if walk not in row_of_(defKing_standpoint):     
                    break
            if direction == NOR_ESTE or direction == NOR_OESTE:
                if walk not in row_of_(defKing_standpoint+NORTE*mult):
                    break
            if direction == SUR_ESTE or direction == SUR_OESTE:
                if walk not in row_of_(defKing_standpoint+SUR*mult):
                    break
            if 0 <= walk <= 63: # VALID SQUARE

                if walk == attThreat_standpoint:
                    turn_defender.king_banned_direction = -direction # dirección inversa
                    return walk_trace

                elif walk in mixedDirections_threats:
                    walk_trace.add(walk)
    return walk_trace # vacía si llega a este punto.

def update_turn_objectives():
    '''Llama a todas las funciones _objectives() con sus correctas perspectivas-de-turno.
    En este punto de la ejecución, el atacante ya hizo su acción.

    Internamente se revisará:

        >> attacker.threat_on_enemy
        >> attacker.king_legal_moves
        >> attacker.direct_threat_origin
        >> attacker.single_threat_standpoint
        >> attacker.direct_threat_trace
        >> defender.direct_threat_trace
        >> defender.threat_on_enemy
        >> defender.king_legal_moves
        >> defender.direct_threat_origin
        >> defender.single_threat_standpoint
        >> defender.legalMoves
    
    Antes de ser utilizadas, estas variables (excepto defender.threat_on_enemy que puede contener
    información del *jaque actual* y es resultado de transferencia/SWAP ) deben limpiarse para evitar
    un solapamiento infinito de posiciones.
    
    Primero debemos actualizar la ofensiva -siendo restringido por la defensiva-, y luego la defensiva,
    revisando especialmente si puede salvar a su rey ante la última jugada ofensiva.

    direct_threat_origin será siempre y únicamente calculado luego de evaluar la ofensiva,
    Si es NONE no hay ninguna amenaza directa, pero si es FALSE significa que HAY MULTIPLES AMENAZAS
    DIRECTAS, por lo tanto el rey depende de su propio movimiento (o será jaque-mate).

    DEBO revisar defender.threat_on_enemy y defender.direct_threat_origin en perspectivas
    ofensivas de turno. Si direct_threat_origin es TRUE, DEBO revisar defender.DIRECT_THREATS .
    
    Al terminar estos cálculos, la funcion decide_check() establecerá si la partida debe continuar o
    terminarse con algún veredicto.
    
    Desde perspectiva = 'attacker' es importante:

        >> Atender que si existe defender.direct_threat_origin (jaque), solo puedo moverme/atacar si
            eso salva a mi rey. 
            -> if defender.direct_threat_origin == 'single'
                
        >> Si no existe jaque, debo revisar si "salirme del casillero" -moviendome o matando-
            expone a mi rey a un jaque.
            -> exposing_movement(standpoint, direction, request_from)

        >> Actualizaremos attacker.threat_on_enemy
            -> kill-movements aún no hechos pero que "amenazan" CASILLEROS VACÍOS/CASILLEROS CON ALIADOS EN EL.
    
    Desde perspectiva = 'defender' es importante:

        >> Verificar y validar LEGAL-MOVES, si resultan ser 0 para el actual defensor, el actual atacante ganó o empató.
        
        >> Los movimientos descartados (ilegales) son aquellos que no puedan realizarse si,
            NO ESTANDO EN JAQUE:
                - Por bloqueo aliado
                - Por ser expositivos-al-rey
            ESTANDO EN JAQUE:
                - Por bloqueo aliado
                - Por no *salvar al rey* (matando o bloqueando la amenaza)
    '''

    turn_attacker.clear()
    turn_defender.clear()

    # Attacker ----------------------------------------------------------------------------------------
    king_standpoints: list[int] = get_piece_standpoint(color=turn_attacker, piece="king")
    if len(king_standpoints) != 0:
        _king = king_standpoints.pop()
        king_objectives(_king, perspective='attacker')

    pawn_standpoints: list[int] = get_piece_standpoint(color=turn_attacker,piece="pawn")
    for _pawn in pawn_standpoints:
        pawn_objectives(_pawn, perspective='attacker')

    rook_standpoints: list[int] = get_piece_standpoint(color=turn_attacker,piece="rook")
    for _rook in rook_standpoints:
        rook_objectives(_rook, perspective='attacker')

    bishop_standpoints: list[int] = get_piece_standpoint(color=turn_attacker,piece="bishop")
    for _bishop in bishop_standpoints:
        bishop_objectives(_bishop, perspective='attacker')

    knight_standpoints: list[int] = get_piece_standpoint(color=turn_attacker, piece="knight")
    for _knight in knight_standpoints:
        knight_objectives(_knight, perspective='attacker')

    queen_standpoint: list[int] = get_piece_standpoint(color=turn_attacker, piece="queen")
    if len(queen_standpoint) != 0:
        _queen = queen_standpoint.pop()
        queen_objectives(_queen, perspective='attacker')
    # --------------------------------------------------------------------------------------------------

    # TURN DEBUG ++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # print(f'El jugador {attacker} dejó estas amenazas:')
    # for at, d in attacker.threat_on_enemy.items(): print(at, d)
    # print('------------')
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    # Defender -----------------------------------------------------------------------------------------
    king_standpoints: list[int] = get_piece_standpoint(color=turn_defender, piece="king")
    if len(king_standpoints) != 0:
        _king = king_standpoints.pop()

    # Revisión del estado de la amenaza del atacante sobre el rey defensor (jaque)
    for _threats_list in turn_attacker.threat_on_enemy.values():
        if _king in _threats_list:
            if turn_attacker.direct_threat_origin == 'single': # caso amenaza múltiple
                turn_attacker.direct_threat_origin = False
                turn_attacker.single_threat_standpoint = None
                turn_attacker.direct_threat_trace.clear()
                break

            # amenaza directa simple
            turn_attacker.direct_threat_origin = True
            # La posición de orígen de la amenaza estará SIEMPRE en _threats_list[-1].
            # attacker.direct_threat_trace NO INCLUYE STANDPOINT DE LA AMENAZA.
            # Si la pieza amenazante es el caballo NO llamar a trace_direction_walk.
            turn_attacker.single_threat_standpoint = _threats_list[-1]
            knight_walk_exception: str = turn_attacker.positions[_threats_list[-1]]
            if knight_walk_exception != 'knight':
                turn_attacker.direct_threat_trace = trace_direction_walk(_king, _threats_list, _threats_list[-1])
            else: turn_attacker.direct_threat_trace = []

    remove_all_attacker_standpoints() # Necesario para que el rey pueda identificar piezas como -quizás matable-.
    king_objectives(_king, perspective='defender') # genero/reviso defender.king_legal_moves.

    if turn_attacker.direct_threat_origin != False:
        # Defender kingSupport (Revision de movimientos legales del defensor para ver si perdió, empató, o nada de eso)
        pawn_standpoints = get_piece_standpoint(color=turn_defender, piece='pawn')
        for _pawn in pawn_standpoints:
            pawn_objectives(_pawn, perspective='defender')

        rook_standpoints = get_piece_standpoint(color=turn_defender, piece="rook")
        for _rook in rook_standpoints:
            rook_objectives(_rook, perspective='defender')
        
        bishop_standpoints = get_piece_standpoint(color=turn_defender, piece='bishop')
        for _bishop in bishop_standpoints:
            bishop_objectives(_bishop, perspective='defender')
        
        knight_standpoints = get_piece_standpoint(color=turn_defender, piece="knight")
        for _knight in knight_standpoints:
            knight_objectives(_knight, perspective='defender')
        
        queen_standpoint = get_piece_standpoint(color=turn_defender, piece="queen")
        if len(queen_standpoint) != 0:
            _queen = queen_standpoint.pop()
            queen_objectives(_queen, perspective='defender')
    # -------------------------------------------------------------------------------------------------

def reset_match():
    '''Puede que haya casos en los que el contenido del match varíe en su reinicio
    por eso debo tener cuidado *dónde* lo hago.'''
    init_content()

def turn_swap():
    global whitetime_SNAP, blacktime_SNAP
    '''
    Intercalaremos:
    >> positions
    >> threat_on_enemy
    >> king_legal_moves
    >> direct_threat_origin
    >> direct_threat_trace
    >> single_threat_standpoint
    >> king_banned_direction
    >> castling_enablers
    >> relojes
    
    Match aplicará cambios siempre sobre conjuntos generalizados bajo attacker/defender,
    entonces luego de realizados:

    PRIMERO los volveremos a adjudicar a su variable de color-origen. "COMO ERAN"
    LUEGO los intercambiamos por el color-equipo que corresponde. "COMO RESULTAN AHORA"
    '''

    if attacker == 'white':

        attacker = 'black'
        defender = 'white'
        if black_time_leftover < 1000:
            blacktime_SNAP = pygame.time.get_ticks() - black_time_leftover
        else:
            blacktime_SNAP = pygame.time.get_ticks() + black_time_leftover

        # Target Transfer (white <- attacker | black <- defender) ---------------------
        # > positions
        white.positions = attacker.positions
        black.positions = defender.positions

        # > threatOn
        white.threat_on_enemy = attacker.threat_on_enemy
        black.threat_on_enemy = defender.threat_on_enemy

        # > king_legal_moves
        white.king_legal_moves = attacker.king_legal_moves
        black.king_legal_moves = defender.king_legal_moves

        # > direct_threat_origin
        white.direct_threat_origin = attacker.direct_threat_origin
        black.direct_threat_origin = defender.direct_threat_origin

        # > direct_threat_trace
        white.direct_threat_trace = attacker.direct_threat_trace
        black.direct_threat_trace = defender.direct_threat_trace

        # > singleOriginThreat standpoint
        white.single_threat_standpoint = attacker.single_threat_standpoint
        black.single_threat_standpoint = defender.single_threat_standpoint

        # > king_banned_direction
        white.king_banned_direction = attacker.king_banned_direction
        black.king_banned_direction = defender.king_banned_direction

        # > castling_enablers
        white.castling_enablers = attacker.castling_enablers
        black.castling_enablers = defender.castling_enablers

        # Target Swap (attacker = black | defender = white ) ---------------------------
        # > positions
        attacker.positions = black.positions
        defender.positions = white.positions

        # > threatOn
        attacker.threat_on_enemy = black.threat_on_enemy
        defender.threat_on_enemy = white.threat_on_enemy

        # > king_legal_moves
        attacker.king_legal_moves = black.king_legal_moves
        defender.king_legal_moves = white.king_legal_moves

        # > direct_threat_origin
        attacker.direct_threat_origin = black.direct_threat_origin
        defender.direct_threat_origin = white.direct_threat_origin

        # > direct_threat_trace
        attacker.direct_threat_trace = black.direct_threat_trace
        defender.direct_threat_trace = white.direct_threat_trace

        # > SingleOriginThreat standpoint
        attacker.single_threat_standpoint = black.single_threat_standpoint
        defender.single_threat_standpoint = white.single_threat_standpoint

        # > king_banned_direction
        attacker.king_banned_direction = black.king_banned_direction
        defender.king_banned_direction = white.king_banned_direction

        # > castling_enablers
        attacker.castling_enablers = black.castling_enablers
        defender.castling_enablers = white.castling_enablers

        return
    
    if attacker == 'black':

        attacker = 'white'
        defender = 'black'
        if white_time_leftover < 1000:
            whitetime_SNAP = pygame.time.get_ticks() - white_time_leftover
        else:
            whitetime_SNAP = pygame.time.get_ticks() + white_time_leftover

        # Target Transfer (white <- defender | black <- attacker) ----------------------
        # > positions
        white.positions = defender.positions
        black.positions = attacker.positions

        # > threatOn
        white.threat_on_enemy = defender.threat_on_enemy
        black.threat_on_enemy = attacker.threat_on_enemy

        # > king_legal_moves
        white.king_legal_moves = defender.king_legal_moves
        black.king_legal_moves = attacker.king_legal_moves

        # > direct_threat_origin
        white.direct_threat_origin = defender.direct_threat_origin
        black.direct_threat_origin = attacker.direct_threat_origin

        # > direct_threat_trace
        white.direct_threat_trace = defender.direct_threat_trace
        black.direct_threat_trace = attacker.direct_threat_trace

        # > singleOriginThreat standpoint
        white.single_threat_standpoint = defender.single_threat_standpoint
        black.single_threat_standpoint = attacker.single_threat_standpoint

        # > king_banned_direction
        white.king_banned_direction = defender.king_banned_direction
        black.king_banned_direction = attacker.king_banned_direction

        # > castling_enablers
        white.castling_enablers = defender.castling_enablers
        black.castling_enablers = attacker.castling_enablers

        # Target Swap (attacker = white | defender = black) ----------------------------
        # > positions
        attacker.positions = white.positions
        defender.positions = black.positions

        # > threatOn
        attacker.threat_on_enemy = white.threat_on_enemy
        defender.threat_on_enemy = black.threat_on_enemy

        # > king_legal_moves
        attacker.king_legal_moves = white.king_legal_moves
        defender.king_legal_moves = black.king_legal_moves

        # > direct_threat_origin
        attacker.direct_threat_origin = white.direct_threat_origin
        defender.direct_threat_origin = black.direct_threat_origin

        # > direct_threat_trace
        attacker.direct_threat_trace = white.direct_threat_trace
        defender.direct_threat_trace = black.direct_threat_trace

        # > singleOriginThreat standpoint
        attacker.single_threat_standpoint = white.single_threat_standpoint
        defender.single_threat_standpoint = black.single_threat_standpoint

        # > king_banned_direction
        attacker.king_banned_direction = white.king_banned_direction
        defender.king_banned_direction = black.king_banned_direction

        # > castling_enablers
        attacker.castling_enablers = white.castling_enablers
        defender.castling_enablers = black.castling_enablers

        return

def remove_all_attacker_standpoints():
    '''
    Quita TODOS los standpoints de attacker.threat_on_enemy
    (y por consecuente su vuelta como def_threatOnAtt).
    Los standpoints coinciden SIEMPRE en el último item de la lista de amenazas.
    De esta forma aclaramos la visión al rey correspondiente en cuanto a amenazas
    matables y no-matables.
    '''
    for _threats in turn_attacker.threat_on_enemy.values():
        _threats.pop()

def exposing_direction(standpoint: int, direction: int, request_from: str) -> bool:
    '''Para verificar si un movimiento expone al rey aliado "falsificaremos" 
    un movimiento contra el conjunto de piezas que corresponda.
    >> falsificar defenderMov contra attacker
    >> falsificar attackerMov contra defender

    Llamaremos a las piezas correspondientes en la :perspectiva: correspondiente:
    "fake-attackerMov-toDef"
    "fake-defenderMov-toAtt"
    E inyectandoles posiciones falsas de "quien consulta".

    Cada piece_objective(perspective="fake...") devolverá:
        TRUE si encontró al rey en amenaza directa.
        FALSE si NO lo hizo.
    
    Crearemos un conjunto de posiciones falsas mediante:
        Buscar en el conjunto "consultante" el standpoint y lo reemplazaremos por
        fake_move (standpoint + direction)
        Esto deja un "hueco" por donde ahora el rey podría ser amenazado.

    **IMPORTANTE** Los peones y caballos NUNCA influyen en exposing-movements
    **IMPORTANTE** En perspectivas "fake..." NO se toman en cuenta *nuevos* exposing-movements.
    '''
    fake_move: int = standpoint+direction
    fake_positions: dict[int, str] = {}

    if request_from == 'attacker':
        for ap in turn_attacker.positions.keys():
            if standpoint != ap:
                fake_positions.update({ap: turn_attacker.positions[ap]})
            else:
                fake_positions.update({fake_move: turn_attacker.positions[ap]})

        '''En esta perspectiva debemos verificar si el ATACANTE está en jaque.
        Si está en jaque, debemos filtrar y descartar la pieza DEFENSORA amenazante
        (Torre, Alfil o Reina) o nunca obtendremos el resultado esperado.'''

        if turn_defender.direct_threat_origin:
            # nombre de la pieza que NO debemos considerar
            rejected_piece: str = turn_defender.positions[turn_defender.single_threat_standpoint]

            if rejected_piece != 'rook':
                rook_standpoints: list[int] = get_piece_standpoint(color=turn_defender,piece="rook")
                if len(rook_standpoints) != 0:
                    for _rook in rook_standpoints:
                        if rook_objectives(_rook, perspective='fake-attackerMov-toDef', fake_positions=fake_positions):
                            return True
            
            if rejected_piece != 'bishop':
                bishop_standpoints: list[int] = get_piece_standpoint(color=turn_defender,piece="bishop")
                if len(bishop_standpoints) != 0:
                    for _bishop in bishop_standpoints:
                        if bishop_objectives(_bishop, perspective='fake-attackerMov-toDef', fake_positions=fake_positions):
                            return True

            if rejected_piece != 'queen':
                queen_standpoint: list[int] = get_piece_standpoint(color=turn_defender, piece="queen")
                if len(queen_standpoint) != 0:
                    _queen = queen_standpoint.pop()
                    if queen_objectives(_queen, perspective='fake-attackerMov-toDef', fake_positions=fake_positions):
                        return True

        elif turn_defender.direct_threat_origin == 'none':
            rook_standpoints: list[int] = get_piece_standpoint(color=turn_defender,piece="rook")
            if len(rook_standpoints) != 0:
                for _rook in rook_standpoints:
                    if rook_objectives(_rook, perspective='fake-attackerMov-toDef', fake_positions=fake_positions):
                        return True

            bishop_standpoints: list[int] = get_piece_standpoint(color=turn_defender,piece="bishop")
            if len(bishop_standpoints) != 0:
                for _bishop in bishop_standpoints:
                    if bishop_objectives(_bishop, perspective='fake-attackerMov-toDef', fake_positions=fake_positions):
                        return True

            queen_standpoint: list[int] = get_piece_standpoint(color=turn_defender, piece="queen")
            if len(queen_standpoint) != 0:
                _queen = queen_standpoint.pop()
                if queen_objectives(_queen, perspective='fake-attackerMov-toDef', fake_positions=fake_positions):
                    return True
            return False

    if request_from == 'defender':
        for dp in turn_defender.positions.keys():
            if standpoint != dp:
                fake_positions.update({dp: turn_defender.positions[dp]})
            else:
                fake_positions.update({fake_move: turn_defender.positions[dp]})

        rook_standpoints: list[int] = get_piece_standpoint(color=turn_attacker,piece="rook")
        for _rook in rook_standpoints:
            if rook_objectives(_rook, perspective='fake-defenderMov-toAtt', fake_positions=fake_positions):
                return True

        bishop_standpoints: list[int] = get_piece_standpoint(color=turn_attacker,piece="bishop")
        for _bishop in bishop_standpoints:
            if bishop_objectives(_bishop, perspective='fake-defenderMov-toAtt', fake_positions=fake_positions):
                return True

        queen_standpoint: list[int] = get_piece_standpoint(color=turn_attacker, piece="queen")
        if len(queen_standpoint) != 0:
            _queen = queen_standpoint.pop()
            if queen_objectives(_queen, perspective='fake-defenderMov-toAtt', fake_positions=fake_positions):
                return True
        return False

def pawn_objectives(piece_standpoint: int, perspective: str) -> dict[int, pygame.Rect] | None:
    '''Movimiento Peón:
    NORTE (white)
    SUR (black)
    1 casillero por vez, excepto que sea su primer movimiento,
    lo que hará que pueda moverse 2 casilleros a la vez.
    Kill mov. Peón:
    Peon NEGRO: SUR_OESTE, SUR_ESTE
    Peon BLANCO: NOR_OESTE, NOR_ESTE
    '''

    # Visual feedback utils
    mov_target_positions: dict[int, pygame.Rect] = {piece_standpoint: board.rects[piece_standpoint]} # standpoint is always first pos 
    on_target_kill_positions: dict[int, pygame.Rect] = {}
    
    # Objectives
    kill_positions: list[int] = []
    movement: int

    if perspective == 'defender' :
        if turn_defender == 'black': # defiende hacia el SUR
        
            # 1st Movement
            movement = piece_standpoint+SUR
            if movement <= 63: # board limit

                if turn_attacker.direct_threat_origin == 'single':
                    if movement not in turn_defender.positions or movement not in turn_attacker.positions:
                        if not exposing_direction(piece_standpoint, direction=SUR, request_from="defender"):
                            
                            # 1st Movement -BLOCK saving position-
                            if movement in turn_attacker.direct_threat_trace:
                                turn_defender.legal_moves.add(f'pawn{piece_standpoint}')

                            # 2nd Movement
                            if piece_standpoint in black.pawns_in_origin:
                                if movement+SUR not in turn_defender.positions:

                                    # 2nd Movement -BLOCK saving position-
                                    if movement+SUR in turn_attacker.direct_threat_trace:
                                        turn_defender.legal_moves.add(f'pawn{piece_standpoint}')    
                        else: pass
                    
                    # kill saving positions
                    # board limits check
                    if piece_standpoint+OESTE not in row_of_(piece_standpoint):
                        kill_positions.append(piece_standpoint+SUR_ESTE)

                    if piece_standpoint+ESTE not in row_of_(piece_standpoint):
                        kill_positions.append(piece_standpoint+SUR_OESTE)

                    elif len(kill_positions) == 0:
                        kill_positions.extend([piece_standpoint+SUR_OESTE, piece_standpoint+SUR_ESTE])

                    for kp in kill_positions:
                        if kp in turn_attacker.positions:
                            if not exposing_direction(piece_standpoint, direction=kp, request_from="defender"):
                                if kp == turn_attacker.single_threat_standpoint:
                                    turn_defender.legal_moves.add(f'pawn{piece_standpoint}')
                    return
                        
                elif turn_attacker.direct_threat_origin == 'none': 
                    if movement not in turn_defender.positions or movement not in turn_attacker.positions:
                        if not exposing_direction(piece_standpoint, direction=SUR, request_from="defender"):
                            turn_defender.legal_moves.add(f'pawn{piece_standpoint}')
                        else: pass
                    
                    # kill positions
                    # board limits check
                    if piece_standpoint+OESTE not in row_of_(piece_standpoint):
                        kill_positions.append(piece_standpoint+SUR_ESTE)

                    if piece_standpoint+ESTE not in row_of_(piece_standpoint):
                        kill_positions.append(piece_standpoint+SUR_OESTE)

                    elif len(kill_positions) == 0:
                        kill_positions.extend([piece_standpoint+SUR_OESTE, piece_standpoint+SUR_ESTE])

                    for kp in kill_positions:
                        if kp in turn_attacker.positions:
                            if not exposing_direction(piece_standpoint, direction=kp, request_from="defender"):
                                turn_defender.legal_moves.add(f'pawn{piece_standpoint}')
                    return
            return

        if turn_defender == 'white': # defiende hacia el NORTE

            # 1st Movement
            movement = piece_standpoint+NORTE
            if movement <= 63: # board limit

                if turn_attacker.direct_threat_origin == 'single':
                    if movement not in turn_defender.positions:
                        if not exposing_direction(piece_standpoint, direction=NORTE, request_from="defender"):

                            # 1st Movement -BLOCK saving position-
                            if movement in turn_attacker.direct_threat_trace:
                                turn_defender.legal_moves.add(f'pawn{piece_standpoint}')
                            
                            # 2nd Movement
                            if piece_standpoint in white.pawns_in_origin:
                                if movement+NORTE not in turn_defender.positions:
                                    
                                    # 2nd Movement -BLOCK saving position-
                                    if movement+NORTE in turn_attacker.direct_threat_trace:
                                        turn_defender.legal_moves.add(f'pawn{piece_standpoint}')
                        else: pass
                
                    # kill saving positions
                    # board limits check
                    if piece_standpoint+OESTE not in row_of_(piece_standpoint):
                        kill_positions.append(piece_standpoint+NOR_ESTE)

                    if piece_standpoint+ESTE not in row_of_(piece_standpoint):
                        kill_positions.append(piece_standpoint+NOR_OESTE)

                    elif len(kill_positions) == 0:
                        kill_positions.extend([piece_standpoint+NOR_OESTE, piece_standpoint+NOR_ESTE])

                    for kp in kill_positions:
                        if kp in turn_attacker.positions:
                            if not exposing_direction(piece_standpoint, direction=kp, request_from="defender"):
                                if kp == turn_attacker.single_threat_standpoint:
                                    turn_defender.legal_moves.add(f'pawn{piece_standpoint}')
                    return
                                    
                elif turn_attacker.direct_threat_origin == 'none':
                    if movement not in turn_defender.positions or movement not in turn_attacker.positions:
                        if not exposing_direction(piece_standpoint, direction=NORTE, request_from="defender"):
                            turn_defender.legal_moves.add(f'pawn{piece_standpoint}')
                        else: pass
                    
                    # kill saving positions
                    # board limits check
                    if piece_standpoint+OESTE not in row_of_(piece_standpoint):
                        kill_positions.append(piece_standpoint+NOR_ESTE)

                    if piece_standpoint+ESTE not in row_of_(piece_standpoint):
                        kill_positions.append(piece_standpoint+NOR_OESTE)

                    elif len(kill_positions) == 0:
                        kill_positions.extend([piece_standpoint+NOR_OESTE, piece_standpoint+NOR_ESTE])

                    for kp in kill_positions:
                        if kp in turn_attacker.positions:
                            if not exposing_direction(piece_standpoint, direction=kp, request_from="defender"):
                                turn_defender.legal_moves.add(f'pawn{piece_standpoint}')
                    return
            return
        return

    if perspective == 'attacker':
        if turn_attacker == 'black': # Ataca hacia el SUR

            # 1st Movement
            movement = piece_standpoint+SUR
            if movement <= 63: # board limit

                if turn_defender.direct_threat_origin == 'single':
                    if movement not in turn_attacker.positions and movement not in turn_defender.positions: # piece block
                        if not exposing_direction(piece_standpoint, direction=SUR, request_from="attacker"):
                            if movement in turn_defender.direct_threat_trace:
                                # BLOCK saving position
                                mov_target_positions.update({movement: board.rects[movement]})

                            #probamos con el 2do mov
                            if piece_standpoint in black.pawns_in_origin:
                                if movement+SUR not in turn_attacker.positions and movement+SUR not in turn_defender.positions: # piece block
                                    if movement+SUR in turn_defender.direct_threat_trace:
                                        # BLOCK saving position
                                        mov_target_positions.update({movement+SUR: board.rects[movement+SUR]})

                    # kill-movements
                    # board limits check
                    if piece_standpoint+OESTE not in row_of_(piece_standpoint):
                        kill_positions.append(piece_standpoint+SUR_ESTE)
                    if piece_standpoint+ESTE not in row_of_(piece_standpoint):
                        kill_positions.append(piece_standpoint+SUR_OESTE)
                    elif len(kill_positions) == 0:
                        kill_positions.extend([piece_standpoint+SUR_OESTE, piece_standpoint+SUR_ESTE])
                    
                    for kp in kill_positions:
                        if kp not in turn_attacker.positions and kp == turn_defender.single_threat_standpoint: 
                            if not exposing_direction(piece_standpoint, direction=kp, request_from="attacker"):
                                # KILL saving position
                                on_target_kill_positions.update({kp: board.rects[kp]})

                    return mov_target_positions, on_target_kill_positions

                elif turn_defender.direct_threat_origin == 'none': 

                    if movement not in turn_attacker.positions and movement not in turn_defender.positions: # piece block
                        if not exposing_direction(piece_standpoint, direction=SUR, request_from="attacker"):
                            mov_target_positions.update({movement: board.rects[movement]}) # 1st Movement

                            if piece_standpoint in black.pawns_in_origin:
                                if movement+SUR <= 63: # board limit check
                                    if movement+SUR not in turn_attacker.positions and movement+SUR not in turn_defender.positions: # piece block
                                        mov_target_positions.update({movement+SUR: board.rects[movement+SUR]}) # 2nd Movement 
                        else: pass

                    # kill-movements
                    # board limits check
                    if piece_standpoint+OESTE not in row_of_(piece_standpoint):
                        kill_positions.append(piece_standpoint+SUR_ESTE)
                        
                    if piece_standpoint+ESTE not in row_of_(piece_standpoint):
                        kill_positions.append(piece_standpoint+SUR_OESTE)

                    elif len(kill_positions) == 0:
                        kill_positions.extend([piece_standpoint+SUR_OESTE, piece_standpoint+SUR_ESTE])
        
                    for kp in kill_positions:
                        if kp not in turn_attacker.positions:
                            if kp in turn_defender.positions:
                                if not exposing_direction(piece_standpoint, direction=kp, request_from="attacker"):
                                    on_target_kill_positions.update({kp: board.rects[kp]})
                            
                    # Threat on defender ------------------------
                    kill_positions.append(piece_standpoint)
                    turn_attacker.threat_on_enemy.update({f'pawn{piece_standpoint}': kill_positions})

                    return mov_target_positions, on_target_kill_positions

        if turn_attacker == 'white': # Ataca hacia el NORTE

            # 1st Movement
            movement = piece_standpoint+NORTE
            if movement >= 0: # board limit
                
                if turn_defender.direct_threat_origin == 'single':
                    if movement not in turn_attacker.positions and movement not in turn_defender.positions: # piece block
                        if not exposing_direction(piece_standpoint, direction=NORTE, request_from="attacker"):
                            if movement in turn_defender.direct_threat_trace:
                                # BLOCK saving position
                                mov_target_positions.update({movement: board.rects[movement]})

                            #probamos con el 2do mov
                            if piece_standpoint in white.pawns_in_origin:
                                if movement+NORTE not in turn_attacker.positions and movement+NORTE not in turn_defender.positions:# piece block
                                    if movement+NORTE in turn_defender.direct_threat_trace:
                                        # BLOCK saving position
                                        mov_target_positions.update({movement+NORTE: board.rects[movement+NORTE]})

                    # kill-movements
                    # board limits check
                    if piece_standpoint+OESTE not in row_of_(piece_standpoint):
                        kill_positions.append(piece_standpoint+NOR_ESTE)
                    if piece_standpoint+ESTE not in row_of_(piece_standpoint):
                        kill_positions.append(piece_standpoint+NOR_OESTE)
                    elif len(kill_positions) == 0:
                        kill_positions.extend([piece_standpoint+NOR_OESTE, piece_standpoint+NOR_ESTE])
                                
                    for kp in kill_positions:
                        if kp not in turn_attacker.positions and kp == turn_defender.single_threat_standpoint:
                            if not exposing_direction(piece_standpoint, direction=kp, request_from="attacker"):
                                # KILL saving position
                                on_target_kill_positions.update({kp: board.rects[kp]})
                    
                    return mov_target_positions, on_target_kill_positions
                                
                elif turn_defender.direct_threat_origin == 'none': # no jaque

                    if movement not in turn_attacker.positions and movement not in turn_defender.positions: # piece block
                        if not exposing_direction(piece_standpoint, direction=NORTE, request_from="attacker"):  
                            mov_target_positions.update({movement:board.rects[movement]}) # 1st Movement

                            if piece_standpoint in white.pawns_in_origin:
                                if movement+NORTE >= 0: # board limit check
                                    if movement+NORTE not in black.positions and movement+NORTE not in white.positions: # piece block
                                        mov_target_positions.update({movement+NORTE:board.rects[movement+NORTE]}) # 2nd Movement
                        else: pass
                
                    # kill-movements
                    # board limits check
                    if piece_standpoint+OESTE not in row_of_(piece_standpoint):
                        kill_positions.append(piece_standpoint+NOR_ESTE)

                    if piece_standpoint+ESTE not in row_of_(piece_standpoint):
                        kill_positions.append(piece_standpoint+NOR_OESTE)

                    elif len(kill_positions) == 0:
                        kill_positions.extend([piece_standpoint+NOR_OESTE, piece_standpoint+NOR_ESTE])

                    for kp in kill_positions:
                        if kp not in turn_attacker.positions:
                            if kp in turn_defender.positions:
                                if not exposing_direction(piece_standpoint, direction=kp, request_from="attacker"):
                                    on_target_kill_positions.update({kp:board.rects[kp]})

                    # Threat on defender ------------------------
                    kill_positions.append(piece_standpoint)
                    turn_attacker.threat_on_enemy.update({f'pawn{piece_standpoint}': kill_positions})

                    return mov_target_positions, on_target_kill_positions
            
        return mov_target_positions, on_target_kill_positions 

def rook_objectives(
    piece_standpoint: int,
    perspective: str,
    fake_positions: dict[int, str] | None = None
    ) -> dict[int, pygame.Rect] | None:
    '''Movimiento Torre:
    +NORTE
    +SUR
    +ESTE
    +OESTE 
    La torre mata como se mueve.
    '''

    # Visual feedback utils
    mov_target_positions: dict[int, pygame.Rect] = {piece_standpoint: board.rects[piece_standpoint]} # standpoint is always first pos
    on_target_kill_positions: dict[int, pygame.Rect] = {}
    
    # Objectives
    _threat_emission: list[int] = []
    rook_directions = [NORTE,SUR,ESTE,OESTE]

    if perspective == 'fake-attackerMov-toDef':
        for direction in rook_directions:
            for mult in range(1,8): # 1 to board_size
                movement = piece_standpoint+direction*mult
                if direction == ESTE or direction == OESTE:
                    if movement not in row_of_(piece_standpoint):
                        break
                if 0 <= movement <= 63: # VALID SQUARE

                    # bloqueos aliados
                    if movement in turn_defender.positions:
                        break 

                    elif movement in fake_positions:
                        if fake_positions[movement] == 'king':
                            return True
                        else: break # descartar kill-movements que NO sean al rey
        return False

    if perspective == 'fake-defenderMov-toAtt':
        for direction in rook_directions:
            for mult in range(1,8): # 1 to board_size
                movement = piece_standpoint+direction*mult
                if direction == ESTE or direction == OESTE:
                    if movement not in row_of_(piece_standpoint):
                        break
                if 0 <= movement <= 63: # VALID SQUARE
                    
                    # bloqueos aliados
                    if movement in turn_attacker.positions:
                        break 

                    elif movement in fake_positions:
                        if fake_positions[movement] == 'king':
                            return True
                        else: break # descartar kill-movements que NO sean al rey
        return False
    
    if perspective == 'defender':
        if turn_attacker.direct_threat_origin == 'single':
            for direction in rook_directions:
                for mult in range(1,8): # 1 to board_size
                    movement = piece_standpoint+direction*mult
                    if direction == ESTE or direction == OESTE:
                        if movement not in row_of_(piece_standpoint):
                            break
                    if 0 <= movement <= 63: # VALID SQUARE

                        if movement in turn_defender.positions:
                            break
                        if not exposing_direction(piece_standpoint, direction=direction, request_from="defender"):
                            if movement in turn_attacker.direct_threat_trace:
                                # block saving position
                                turn_defender.legal_moves.add(f'rook{piece_standpoint}') 
                            if movement == turn_attacker.single_threat_standpoint:
                                # kill saving position
                                turn_defender.legal_moves.add(f'rook{piece_standpoint}')
                        else: continue
            return
        elif turn_attacker.direct_threat_origin == 'none':
            for direction in rook_directions:
                for mult in range(1,8): # 1 to board_size
                    movement = piece_standpoint+direction*mult
                    if direction == ESTE or direction == OESTE:
                        if movement not in row_of_(piece_standpoint):
                            break
                    if 0 <= movement <= 63: # VALID SQUARE
                        
                        if movement not in turn_defender.positions:
                            if not exposing_direction(piece_standpoint, direction=direction, request_from="defender"):
                                # Puede que esté matando o bloqueando pero ambas opciones nos bastan.
                                turn_defender.legal_moves.add(f'rook{piece_standpoint}')
                    # else: break
            return
        return

    if perspective == 'attacker': 
        if turn_defender.direct_threat_origin == 'single':
            for direction in rook_directions:
                for mult in range(1,8): # 1 to board_size
                    movement = piece_standpoint+direction*mult
                    if direction == ESTE or direction == OESTE:
                        if movement not in row_of_(piece_standpoint):
                            break
                    if 0 <= movement <= 63: # VALID SQUARE

                        if movement not in turn_attacker.positions and movement not in turn_defender.positions:
                            if not exposing_direction(piece_standpoint, direction=direction, request_from='attacker'):
                                if movement in turn_defender.direct_threat_trace:
                                    # BLOCK saving position.
                                    mov_target_positions.update({movement: board.rects[movement]})
                                    break
                            else: break
                                
                        elif movement == turn_defender.single_threat_standpoint:
                            if not exposing_direction(piece_standpoint, direction=direction, request_from='attacker'):
                                # KILL saving position.
                                on_target_kill_positions.update({movement: board.rects[movement]})
                                break
                            else: break
                        else: break # chocamos contra un bloqueo - romper el mult
            return mov_target_positions, on_target_kill_positions
            
        elif turn_defender.direct_threat_origin == 'none':
            for direction in rook_directions:
                for mult in range(1,8): # 1 to board_size
                    movement = piece_standpoint+direction*mult
                    if direction == ESTE or direction == OESTE:
                        if movement not in row_of_(piece_standpoint):
                            break
                    if 0 <= movement <= 63: # VALID SQUARE

                        if movement not in turn_attacker.positions and movement not in turn_defender.positions:
                            if not exposing_direction(piece_standpoint, direction=direction, request_from='attacker'):
                                _threat_emission.append(movement)
                                mov_target_positions.update({movement: board.rects[movement]})
                            else: break # rompe hasta la siguiente dirección.  
                            
                        # Kill-movement
                        elif movement in turn_defender.positions:
                            if not exposing_direction(piece_standpoint, direction=direction, request_from='attacker'):
                                _threat_emission.append(movement)
                                on_target_kill_positions.update({movement: board.rects[movement]})
                                turn_attacker.threat_on_enemy.update({f'rook{piece_standpoint}': _threat_emission})
                                break
                            else: break
                        else: 
                            _threat_emission.append(movement)
                            break # chocamos contra un bloqueo - romper el mult
            _threat_emission.append(piece_standpoint)
            turn_attacker.threat_on_enemy.update({f'rook{piece_standpoint}': _threat_emission})
            return mov_target_positions, on_target_kill_positions
        return mov_target_positions, on_target_kill_positions
    return

def knight_objectives(piece_standpoint: int, perspective: str) -> dict[int,pygame.Rect] | None:
    '''Movimiento Caballo:
    doble-norte + este
    doble-norte + oeste
    doble-sur + este
    doble-sur + oeste
    doble-este + norte
    doble-este + sur
    doble-oeste + norte
    doble-oeste + sur
    El caballo mata como se mueve.
    '''
    
    # Visual feedback utils
    mov_target_positions: dict[int,pygame.Rect] = {piece_standpoint:board.rects[piece_standpoint]} # standpoint is always first pos
    on_target_kill_positions: dict[int,pygame.Rect] = {}

    # Objectives
    _threat_emission: list[int] = []
    knight_movements = []

    # ESTE / OESTE LIMITS
    if piece_standpoint+ESTE in row_of_(piece_standpoint):
        knight_movements.extend([piece_standpoint+NORTE+NOR_ESTE,
                                piece_standpoint+SUR+SUR_ESTE])
        if piece_standpoint+ESTE*2 in row_of_(piece_standpoint):
            knight_movements.extend([piece_standpoint+ESTE+NOR_ESTE,
                                    piece_standpoint+ESTE+SUR_ESTE])
    if piece_standpoint+OESTE in row_of_(piece_standpoint):
        knight_movements.extend([piece_standpoint+NORTE+NOR_OESTE,
                                piece_standpoint+SUR+SUR_OESTE])
        if piece_standpoint+OESTE*2 in row_of_(piece_standpoint):
            knight_movements.extend([piece_standpoint+OESTE+NOR_OESTE,
                                    piece_standpoint+OESTE+SUR_OESTE])
    
    if perspective == 'defender':
        if turn_attacker.direct_threat_origin:
            for movement in knight_movements:
                if 0 <= movement <= 63: # NORTE/SUR LIMIT
                    
                    if movement not in turn_defender.positions:
                        if not exposing_direction(piece_standpoint, direction=movement, request_from="defender"):
                            if movement in turn_attacker.direct_threat_trace:
                                turn_defender.legal_moves.add(f'knight{piece_standpoint}')
                            if movement == turn_attacker.single_threat_standpoint:
                                turn_defender.legal_moves.add(f'knight{piece_standpoint}')
                    else: continue 
            return

        elif turn_attacker.direct_threat_origin == 'none':
            for movement in knight_movements:
                if 0 <= movement <= 63: # NORTE/SUR LIMIT
                    if movement not in turn_defender.positions:
                        if not exposing_direction(piece_standpoint, direction=movement, request_from="defender"):
                            turn_defender.legal_moves.add(f'knight{piece_standpoint}')
            return
        return

    if perspective == 'attacker':
        if turn_defender.direct_threat_origin == 'single':
            for movement in knight_movements:
                if 0 <= movement <= 63: # NORTE/SUR LIMIT 

                    if movement not in turn_attacker.positions and movement not in turn_defender.positions:
                        if not exposing_direction(piece_standpoint, direction=movement, request_from='attacker'):
                            if movement in turn_defender.direct_threat_trace:
                                # BLOCK saving position.
                                mov_target_positions.update({movement: board.rects[movement]})
                    elif movement == turn_defender.single_threat_standpoint:
                        if not exposing_direction(piece_standpoint, direction=movement, request_from='attacker'):
                            # KILL saving position.
                            on_target_kill_positions.update({movement: board.rects[movement]}) 
                    else: continue
            return mov_target_positions, on_target_kill_positions
        
        elif turn_defender.direct_threat_origin == 'none':
            '''Unica pieza la cual podemos descartar todos sus movimientos si uno solo expone.'''
            for movement in knight_movements:
                if 0 <= movement <= 63: # NORTE/SUR LIMIT 

                    if movement not in turn_attacker.positions:
                        if not exposing_direction(piece_standpoint, direction=movement, request_from="attacker"):

                            # Movement
                            if movement not in turn_defender.positions:
                                _threat_emission.append(movement)
                                mov_target_positions.update({movement: board.rects[movement]})
                            
                            # Kill-movement
                            elif movement in turn_defender.positions:
                                _threat_emission.append(movement)
                                on_target_kill_positions.update({movement:board.rects[movement]})
                        else: return {}, {}
                    else:  _threat_emission.append(movement)
            _threat_emission.append(piece_standpoint)
            turn_attacker.threat_on_enemy.update({f'knight{piece_standpoint}': _threat_emission})
            return mov_target_positions, on_target_kill_positions
        return mov_target_positions, on_target_kill_positions
    return

def bishop_objectives(
    piece_standpoint: int,
    perspective: str,
    fake_positions: dict[int, str] | None = None
    ) -> dict[int,pygame.Rect] | None:
    '''Movimiento Alfil:
    +NOR_OESTE
    +NOR_ESTE
    +SUR_OESTE
    +SUR_ESTE
    '''
    
    # Visual feedback utils <- deberíamos desacoplar esto de aquí
    mov_target_positions: dict[int,pygame.Rect] = {piece_standpoint:board.rects[piece_standpoint]} # standpoint is always first pos
    on_target_kill_positions: dict[int,pygame.Rect] = {}
    
    # Objectives
    _threat_emission: list[int] = []
    bishop_directions = [NOR_OESTE,NOR_ESTE,SUR_OESTE,SUR_ESTE]

    if perspective == 'fake-attackerMov-toDef':
        for direction in bishop_directions:
            for mult in range(1,8):
                movement = piece_standpoint+direction*mult
                if direction == NOR_ESTE or direction == NOR_OESTE:
                    if movement not in row_of_(piece_standpoint+NORTE*mult):
                        break
                if direction == SUR_ESTE or direction == SUR_OESTE:
                    if movement not in row_of_(piece_standpoint+SUR*mult):
                        break
                if 0 <= movement <= 63: # VALID SQUARE

                    # bloqueos aliados
                    if movement in turn_defender.positions:
                        break

                    elif movement in fake_positions:
                        if fake_positions[movement] == 'king':
                            return True
                        else: break # descartar kill-movements que NO sean el rey
        return False

    if perspective == 'fake-defenderMov-toAtt':
        for direction in bishop_directions:
            for mult in range(1,8):
                movement = piece_standpoint+direction*mult
                if direction == NOR_ESTE or direction == NOR_OESTE:
                    if movement not in row_of_(piece_standpoint+NORTE*mult):
                        break
                if direction == SUR_ESTE or direction == SUR_OESTE:
                    if movement not in row_of_(piece_standpoint+SUR*mult):
                        break
                if 0 <= movement <= 63: # VALID SQUARE

                    # bloqueos aliados
                    if movement in turn_attacker.positions:
                        break
                    
                    elif movement in fake_positions:
                        if fake_positions[movement] == 'king':
                            return True
                        else: break # descartar kill-movements que NO sean al rey
        return False

    if perspective == 'defender':
        if turn_attacker.direct_threat_origin == 'single':
            for direction in bishop_directions:
                for mult in range(1,8):
                    movement = piece_standpoint+direction*mult
                    if direction == NOR_ESTE or direction == NOR_OESTE:
                        if movement not in row_of_(piece_standpoint+NORTE*mult):
                            break
                    if direction == SUR_ESTE or direction == SUR_OESTE:
                        if movement not in row_of_(piece_standpoint+SUR*mult):
                            break
                    if 0 <= movement <= 63: # VALID SQUARE

                        if movement in turn_defender.positions:
                            break
                        if not exposing_direction(piece_standpoint, direction=movement, request_from="defender"):
                            if movement in turn_attacker.direct_threat_trace:
                                # block saving position
                                turn_defender.legal_moves.add(f'bishop{piece_standpoint}')
                            if movement == turn_attacker.single_threat_standpoint:
                                # kill saving position
                                turn_defender.legal_moves.add(f'bishop{piece_standpoint}')
                        else: continue
            return
        elif turn_attacker.direct_threat_origin == 'none':
            for direction in bishop_directions:
                for mult in range(1,8):
                    movement = piece_standpoint+direction*mult
                    if direction == NOR_ESTE or direction == NOR_OESTE:
                        if movement not in row_of_(piece_standpoint+NORTE*mult):
                            break
                    if direction == SUR_ESTE or direction == SUR_OESTE:
                        if movement not in row_of_(piece_standpoint+SUR*mult):
                            break
                    if 0 <= movement <= 63: # VALID SQUARE

                        if movement not in turn_defender.positions:
                            if not exposing_direction(piece_standpoint, direction=direction, request_from="defender"):
                                turn_defender.legal_moves.add(f'bishop{piece_standpoint}')
                        else: break
            return
        return

    if perspective == 'attacker':
        if turn_defender.direct_threat_origin == 'single':
            for direction in bishop_directions:
                for mult in range(1,8):
                    movement = piece_standpoint+direction*mult
                    if direction == NOR_ESTE or direction == NOR_OESTE:
                        if movement not in row_of_(piece_standpoint+NORTE*mult):
                            break
                    if direction == SUR_ESTE or direction == SUR_OESTE:
                        if movement not in row_of_(piece_standpoint+SUR*mult):
                            break
                    if 0 <= movement <= 63: # VALID SQUARE

                        if movement not in turn_attacker.positions:
                            if not exposing_direction(piece_standpoint, direction=direction, request_from='attacker'):
                                if movement in turn_defender.direct_threat_trace:
                                    # BLOCK saving position.
                                        mov_target_positions.update({movement: board.rects[movement]})
                                elif movement == turn_defender.single_threat_standpoint:
                                    # KILL saving position.
                                    on_target_kill_positions.update({movement: board.rects[movement]})
                                else: continue
                            else: break
                        else: break
            return mov_target_positions, on_target_kill_positions
        
        elif turn_defender.direct_threat_origin == 'none':
            
            for direction in bishop_directions:
                for mult in range(1,8):
                    movement = piece_standpoint+direction*mult
                    if direction == NOR_ESTE or direction == NOR_OESTE:
                        if movement not in row_of_(piece_standpoint+NORTE*mult):
                            break
                    if direction == SUR_ESTE or direction == SUR_OESTE:
                        if movement not in row_of_(piece_standpoint+SUR*mult):
                            break
                    if 0 <= movement <= 63: # VALID SQUARE

                        if movement not in turn_attacker.positions and movement not in turn_defender.positions:
                            if not exposing_direction(piece_standpoint, direction=direction, request_from="attacker"):
                                _threat_emission.append(movement)
                                mov_target_positions.update({movement: board.rects[movement]})
                            else: break # rompe hasta la siguiente dirección.

                        # Kill-movement
                        elif movement in turn_defender.positions:
                            if not exposing_direction(piece_standpoint, direction=direction, request_from="attacker"):
                                _threat_emission.append(movement)
                                on_target_kill_positions.update({movement:board.rects[movement]})
                                break
                            else: break
                        else:
                            _threat_emission.append(movement)
                            break # chocamos contra un bloqueo - romper el mult
            _threat_emission.append(piece_standpoint)
            turn_attacker.threat_on_enemy.update({f'bishop{piece_standpoint}': _threat_emission})
            return mov_target_positions, on_target_kill_positions
        return mov_target_positions, on_target_kill_positions

def queen_objectives(
    piece_standpoint: int,
    perspective: str,
    fake_positions: dict[int, str] | None = None
    ) -> dict[int,pygame.Rect] | None:
    '''Movimiento Reina:
    +NORTE
    +SUR
    +ESTE
    +OESTE
    +NOR_OESTE
    +NOR_ESTE
    +SUR_OESTE
    +SUR_ESTE
    '''

    # Visual feedback utils
    mov_target_positions: dict[int, pygame.Rect] = {piece_standpoint: board.rects[piece_standpoint]} # standpoint is always first pos
    on_target_kill_positions: dict[int, pygame.Rect] = {}

    # Objectives
    _threat_emission: list[int] = []
    queen_directions = [NORTE,SUR,ESTE,OESTE,NOR_OESTE,NOR_ESTE,SUR_OESTE,SUR_ESTE]

    if perspective == 'fake-attackerMov-toDef': 
        for direction in queen_directions:
            for mult in range(1,8):
                movement = piece_standpoint+direction*mult
                if direction == ESTE or direction == OESTE:
                    if movement not in row_of_(piece_standpoint):     
                        break
                if direction == NOR_ESTE or direction == NOR_OESTE:
                    if movement not in row_of_(piece_standpoint+NORTE*mult):
                        break
                if direction == SUR_ESTE or direction == SUR_OESTE:
                    if movement not in row_of_(piece_standpoint+SUR*mult):
                        break
                if 0 <= movement <= 63: # VALID SQUARE

                    # bloqueos aliados
                    if movement in turn_defender.positions:
                        break

                    if movement in fake_positions:
                        if fake_positions[movement] == 'king':
                            return True
                        else: break # descartar kill-movements que NO sean el rey
        return False

    if perspective == 'fake-defenderMov-toAtt':
        for direction in queen_directions:
            for mult in range(1,8):
                movement = piece_standpoint+direction*mult
                if direction == ESTE or direction == OESTE:
                    if movement not in row_of_(piece_standpoint):     
                        break
                if direction == NOR_ESTE or direction == NOR_OESTE:
                    if movement not in row_of_(piece_standpoint+NORTE*mult):
                        break
                if direction == SUR_ESTE or direction == SUR_OESTE:
                    if movement not in row_of_(piece_standpoint+SUR*mult):
                        break
                if 0 <= movement <= 63: # VALID SQUARE

                    # bloqueos aliados
                    if movement in turn_attacker.positions:
                        break

                    elif movement in fake_positions:
                        if fake_positions[movement] == 'king':
                            return True
                        else: break # descartar kill-movements que NO sean al rey
        return False

    if perspective == 'defender':
        if turn_attacker.direct_threat_origin == 'single':
            for direction in queen_directions:
                for mult in range(1,8):
                    movement = piece_standpoint+direction*mult
                    if direction == ESTE or direction == OESTE:
                        if movement not in row_of_(piece_standpoint):     
                            break
                    if direction == NOR_ESTE or direction == NOR_OESTE:
                        if movement not in row_of_(piece_standpoint+NORTE*mult):
                            break
                    if direction == SUR_ESTE or direction == SUR_OESTE:
                        if movement not in row_of_(piece_standpoint+SUR*mult):
                            break
                    if 0 <= movement <= 63: # VALID SQUARE

                        if movement in turn_defender.positions:
                            break
                        if not exposing_direction(piece_standpoint, direction=direction, request_from="defender"):
                            if movement in turn_attacker.direct_threat_trace:
                                # block saving position
                                turn_defender.legal_moves.add(f'queen{piece_standpoint}')
                            if movement == turn_attacker.single_threat_standpoint:
                                # kill saving position
                                turn_defender.legal_moves.add(f'queen{piece_standpoint}')
                        else: continue
            return
        elif turn_attacker.direct_threat_origin == 'none':
            for direction in queen_directions:
                for mult in range(1,8):
                    movement = piece_standpoint+direction*mult
                    if direction == ESTE or direction == OESTE:
                        if movement not in row_of_(piece_standpoint):     
                            break
                    if direction == NOR_ESTE or direction == NOR_OESTE:
                        if movement not in row_of_(piece_standpoint+NORTE*mult):
                            break
                    if direction == SUR_ESTE or direction == SUR_OESTE:
                        if movement not in row_of_(piece_standpoint+SUR*mult):
                            break
                    if 0 <= movement <= 63: # VALID SQUARE

                        if movement not in turn_defender.positions:
                            if not exposing_direction(piece_standpoint, direction=direction, request_from="defender"):
                                turn_defender.legal_moves.add(f'queen{piece_standpoint}')
            return
        return                      
    
    if perspective == 'attacker':
        if turn_defender.direct_threat_origin == 'single':
            for direction in queen_directions:
                for mult in range(1,8):
                    movement = piece_standpoint+direction*mult
                    if direction == ESTE or direction == OESTE:
                        if movement not in row_of_(piece_standpoint):     
                            break
                    if direction == NOR_ESTE or direction == NOR_OESTE:
                        if movement not in row_of_(piece_standpoint+NORTE*mult):
                            break
                    if direction == SUR_ESTE or direction == SUR_OESTE:
                        if movement not in row_of_(piece_standpoint+SUR*mult):
                            break
                    if 0 <= movement <= 63: # VALID SQUARE

                        if movement not in turn_attacker.positions and movement not in turn_defender.positions:
                            if not exposing_direction(piece_standpoint, direction=direction, request_from='attacker'):
                                if movement in turn_defender.direct_threat_trace:
                                    # BLOCK saving position.
                                    mov_target_positions.update({movement: board.rects[movement]})
                                    break
                            else: break
                                    
                        elif movement == turn_defender.single_threat_standpoint:
                            if not exposing_direction(piece_standpoint, direction=direction, request_from='attacker'):
                                # KILL saving position.
                                on_target_kill_positions.update({movement: board.rects[movement]})
                                break      
                            else: break
                        else: break # chocamos contra un bloqueo - romper el mult
            return mov_target_positions, on_target_kill_positions
            
        elif turn_defender.direct_threat_origin == 'none':
            
            for direction in queen_directions:
                for mult in range(1,8):
                    movement = piece_standpoint+direction*mult
                    if direction == ESTE or direction == OESTE:
                        if movement not in row_of_(piece_standpoint):     
                            break
                    if direction == NOR_ESTE or direction == NOR_OESTE:
                        if movement not in row_of_(piece_standpoint+NORTE*mult):
                            break
                    if direction == SUR_ESTE or direction == SUR_OESTE:
                        if movement not in row_of_(piece_standpoint+SUR*mult):
                            break
                    if 0 <= movement <= 63: # VALID SQUARE

                        if movement not in turn_attacker.positions and movement not in turn_defender.positions:
                            if not exposing_direction(piece_standpoint, direction=direction, request_from="attacker"):
                                _threat_emission.append(movement)
                                mov_target_positions.update({movement: board.rects[movement]}) 
                            else: break

                        # Kill-movement
                        elif movement in turn_defender.positions:
                            if not exposing_direction(piece_standpoint, direction=direction, request_from="attacker"):
                                _threat_emission.append(movement) 
                                on_target_kill_positions.update({movement: board.rects[movement]})
                                break
                            else: break
                        else: 
                            _threat_emission.append(movement)
                            break # chocamos contra un bloqueo - romper el mult
            _threat_emission.append(piece_standpoint)
            turn_attacker.threat_on_enemy.update({'queen': _threat_emission})
            return mov_target_positions, on_target_kill_positions
        return mov_target_positions, on_target_kill_positions

def king_objectives(piece_standpoint: int, perspective: str) -> dict[int, pygame.Rect]:
    '''Movimiento Rey:
    +NORTE
    +SUR
    +ESTE
    +OESTE
    +NOR_OESTE
    +NOR_ESTE
    +SUR_OESTE
    +SUR_ESTE
    '''
    
    # Visual feedback utils
    mov_target_positions: dict[int, pygame.Rect] = {piece_standpoint: board.rects[piece_standpoint]} # standpoint is always first pos
    on_target_kill_positions: dict[int, pygame.Rect] = {}
    castling_positions: dict[int, pygame.Rect] = {}
    
    # Objectives
    _threat_emission: list[int] = []
    _castling: int | None = None
    king_directions = [NORTE,SUR,ESTE,OESTE,NOR_OESTE,NOR_ESTE,SUR_OESTE,SUR_ESTE]

    if perspective == 'defender':
        for direction in king_directions:
            if direction == turn_defender.king_banned_direction:
                continue
            movement = piece_standpoint+direction
            if direction == ESTE or direction == OESTE:
                if movement not in row_of_(piece_standpoint):     
                    continue
            if direction == NOR_ESTE or direction == NOR_OESTE:
                if movement-NORTE not in row_of_(piece_standpoint):
                    continue
            if direction == SUR_ESTE or direction == SUR_OESTE:
                if movement-SUR not in row_of_(piece_standpoint):
                    continue
            if 0 <= movement <= 63: # VALID SQUARE

                for threat in turn_attacker.threat_on_enemy.values():
                    if movement in threat: movement = None

                if movement != None:
                    if movement not in turn_defender.positions: # ally block
                        turn_defender.king_legal_moves.append(movement)
        return
    
    if perspective == 'attacker':
        for direction in king_directions:
            if direction == turn_attacker.king_banned_direction:
                continue
            movement: int | None = piece_standpoint+direction
            if direction == ESTE or direction == OESTE:
                if movement not in row_of_(piece_standpoint):
                    continue
                _castling = movement+direction
            if direction == NOR_ESTE or direction == NOR_OESTE:
                if movement-NORTE not in row_of_(piece_standpoint):
                    continue
            if direction == SUR_ESTE or direction == SUR_OESTE:
                if movement-SUR not in row_of_(piece_standpoint):
                    continue
            if 0 <= movement <= 63: # VALID SQUARE

                for threat in turn_defender.threat_on_enemy.values():
                    if movement in threat: movement = None
                    if _castling in threat: _castling = None

                if movement != None:

                    if movement not in turn_attacker.positions and not movement in turn_defender.positions:
                        _threat_emission.append(movement)
                        turn_attacker.king_legal_moves.append(movement)
                        mov_target_positions.update({movement: board.rects[movement]})

                        # castling -WEST-
                        if direction == OESTE:
                            if 'king' and 'west-rook' in turn_attacker.castling_enablers.values():
                                if turn_defender.direct_threat_origin == 'none':       
                                    if _castling != None:
                                        if _castling not in turn_attacker.positions and not _castling in turn_defender.positions:
                                            turn_attacker.king_legal_moves.append(_castling)
                                            castling_positions.update({_castling: board.rects[_castling]})
                                            castling_direction = 'west'

                        # castling -EAST-
                        if direction == ESTE:
                            if 'king' and 'east-rook' in turn_attacker.castling_enablers.values():
                                if turn_defender.direct_threat_origin == 'none':
                                    if _castling != None:
                                        if _castling not in turn_attacker.positions and not _castling in turn_defender.positions:
                                            turn_attacker.king_legal_moves.append(_castling)
                                            castling_positions.update({_castling: board.rects[_castling]})
                                            castling_direction = 'east'

                    elif movement in turn_defender.positions:
                        _threat_emission.append(movement)
                        turn_attacker.king_legal_moves.append(movement)
                        on_target_kill_positions.update({movement: board.rects[movement]})
                    else:
                        _threat_emission.append(movement)

        _threat_emission.append(piece_standpoint)
        turn_attacker.threat_on_enemy.update({'king': _threat_emission})

        return mov_target_positions, on_target_kill_positions, castling_positions
    return

def draw_board():
    global killing, castling, move_here
    # main board frame
    pygame.draw.rect(
        screen,
        (200,200,200),
        pygame.Rect(
            board.x,
            board.y,
            board.width,board.height
        ),
        width=3
    )

    for board_index, SQUARE_RECT in enumerate(board.rects): #celdas que sirven por posición, índice y medida.

        # individual grid frame
        pygame.draw.rect(screen, (200,200,200), SQUARE_RECT, width=1)
        draw_text(f'{board_index}',(150,150,150),
                        SQUARE_RECT.left +3,
                        SQUARE_RECT.top + board.square_height -17,
                        center=False, font_size='medium')
        
        # Square types/subtypes -----------------------------------------------------------------------------
        if board_index in black.positions.keys():
            SQUARE_SUBTYPE = "kill-movement" if board_index in pieceValidKill_posDisplay.keys() else ""
            SQUARE_TYPE =  black.positions[board_index]
            interacted_PColor = "black"

        elif board_index in white.positions.keys():
            SQUARE_SUBTYPE = "kill-movement" if board_index in pieceValidKill_posDisplay.keys() else ""
            SQUARE_TYPE = white.positions[board_index]
            interacted_PColor = "white"

        elif board_index in pieceValidMovement_posDisplay.keys():
            SQUARE_SUBTYPE = "valid-movement"
            SQUARE_TYPE = ""
            interacted_PColor = ""
        
        elif board_index in kingValidCastling_posDisplay.keys():
            SQUARE_SUBTYPE = "castling-movement"
            SQUARE_TYPE = ""
            interacted_PColor = ""

        else: SQUARE_TYPE = "EMPTY"; interacted_PColor = ""; SQUARE_SUBTYPE = ""
        # ----------------------------------------------------------------------------------------------------

        # draw piece
        if SQUARE_TYPE != "EMPTY":
            if interacted_PColor == 'black':
                draw_text(SQUARE_TYPE,'black', SQUARE_RECT.left + board.square_width/2,
                                                    SQUARE_RECT.top + board.square_height/2)
            if interacted_PColor == 'white':
                draw_text(SQUARE_TYPE,(120,120,120),
                                                    SQUARE_RECT.left + board.square_width/2,
                                                    SQUARE_RECT.top + board.square_height/2)

        # hidden/visible elements upon pause/finished game state
        if not pause and not winner and not stalemate and not player_deciding_promotion:
            if SQUARE_RECT.collidepoint((control_input['mouse-x'], control_input['mouse-y'])):

                # Hover -----------------------
                if interacted_PColor == turn_attacker:
                    pygame.draw.rect(screen, 'GREEN', SQUARE_RECT, width=2) # PIECE hover
                else:
                    pygame.draw.rect(screen, (150,150,150), SQUARE_RECT, width=2) # EMPTY hover
                # Hover -----------------------
            
                if control_input['click']:

                    pieceValidKill_posDisplay.clear()
                    kingValidCastling_posDisplay.clear()

                    if SQUARE_SUBTYPE == "kill-movement":
                        killing = True
                        move_here = board_index

                    elif SQUARE_SUBTYPE == "valid-movement":
                        move_here = board_index
                    
                    elif SQUARE_SUBTYPE == "castling-movement":
                        castling = True
                        move_here = board_index

                    else: 
                        if SQUARE_TYPE == 'pawn':
                            pieceValidMovement_posDisplay.clear()
                            if interacted_PColor == turn_attacker:
                                pieceValidMovement_posDisplay, pieceValidKill_posDisplay = pawn_objectives(board_index, perspective='attacker')

                        if SQUARE_TYPE == 'rook':
                            pieceValidMovement_posDisplay.clear()
                            if interacted_PColor == turn_attacker:
                                pieceValidMovement_posDisplay, pieceValidKill_posDisplay = rook_objectives(board_index, perspective='attacker')
                        
                        if SQUARE_TYPE == 'knight':
                            pieceValidMovement_posDisplay.clear()
                            if interacted_PColor == turn_attacker:
                                pieceValidMovement_posDisplay, pieceValidKill_posDisplay = knight_objectives(board_index, perspective='attacker')
                    
                        if SQUARE_TYPE == 'bishop':
                            pieceValidMovement_posDisplay.clear()
                            if interacted_PColor == turn_attacker:
                                pieceValidMovement_posDisplay, pieceValidKill_posDisplay = bishop_objectives(board_index, perspective='attacker')
                        
                        if SQUARE_TYPE == 'queen':
                            pieceValidMovement_posDisplay.clear()
                            if interacted_PColor == turn_attacker:
                                pieceValidMovement_posDisplay, pieceValidKill_posDisplay = queen_objectives(board_index, perspective='attacker')

                        if SQUARE_TYPE == 'king':
                            pieceValidMovement_posDisplay.clear()
                            if interacted_PColor == turn_attacker:
                                pieceValidMovement_posDisplay, pieceValidKill_posDisplay, kingValidCastling_posDisplay = king_objectives(board_index, perspective='attacker')
                            
                        if SQUARE_TYPE == "EMPTY":
                            pieceValidMovement_posDisplay.clear()
                            # kingValidCastling_posDisplay.clear()
                            
    # Pre-movements visual feedback
    if len(pieceValidMovement_posDisplay) > 1 or len(pieceValidKill_posDisplay) > 0: # avoids highlighting pieces with no movement
        for valid_mov_RECT in pieceValidMovement_posDisplay.values():
            pygame.draw.rect(screen, 'GREEN', valid_mov_RECT, width=2)
    for valid_kill_RECT in pieceValidKill_posDisplay.values():
        pygame.draw.rect(screen, 'RED', valid_kill_RECT, width=2)
    for valid_castling_RECT in kingValidCastling_posDisplay.values():
        pygame.draw.rect(screen, 'BLUE', valid_castling_RECT, width=2)

def get_piece_standpoint(color:str, piece:str) -> list[int]:
    '''
    > Argumentar pieza exactamente igual que en pieces.origins
    '''
    _actual_standpoints: list[int] = []
    if color == 'black':
        for k,v in black.positions.items():
            if v == piece:
                _actual_standpoints.append(k)
    if color == 'white':
        for k,v in white.positions.items():
            if v == piece:
                _actual_standpoints.append(k)

    return _actual_standpoints

def decide_check():
    global match_state, stalemate, pause, winner
    '''
    Evalua "cómo quedaron las piezas en el tablero despues del último movimiento".
    Revisando si el ATACANTE ganó.

    JAQUE > El rey es apuntado directamente, PUEDE escapar moviendose o siendo
        salvado por pieza aliada (matando O bloqueando amenaza) - defensa tiene movimientos legales 

    JAQUE-MATE > El rey es apuntado directamente, NO PUEDE escapar moviendose ni
        siendo salvado por pieza aliada. - defensa NO tiene movimientos legales

    STALE-MATE > El rey no es apuntado directamente, pero no puede moverse ni
        ser salvado por pieza aliada. Estado de empate. - defensa NO tiene movimientos legales
    
    DRAW > Solo quedan dos reyes en juego.
    '''
    control_input['click'] = False # evita conflictos de click con el posible menu entrante
    if turn_attacker.direct_threat_origin == 'none':
        if len(turn_attacker.positions) == 1 and len(turn_defender.positions) == 1:
            # Solo pueden ser los reyes, asi que es DRAW
            match_state = 'Draw'
            stalemate = True
            pause = True

        if len(turn_defender.king_legal_moves) == 0 and len(turn_defender.legal_moves) == 0:

            #STALE-MATE
            '''Termina el juego en empate.'''
            if turn_attacker == 'black':
                stalemate = True # repercute en render() - termina la partida
                match_state = 'Rey White ahogado.  -  Empate.'
                pause = True

            if turn_attacker == 'white':
                stalemate = True # repercute en render() - termina la partida
                match_state = 'Rey Black ahogado.  -  Empate.'
                pause = True

        else:
            match_state = ''
            return # La partida continúa con normalidad.

    if turn_attacker.direct_threat_origin:
        if len(turn_defender.king_legal_moves) > 0 or len(turn_defender.legal_moves) > 0:
            # JAQUE
            '''Esto requiere solo una notificación al jugador correspondiente.
            defender.color -> notificate CHECK (highlight possible solutions)'''

            # TURN DEBUG ++++++++++++++++++++++++++++++++++++++++++++++++++++++
                # print('**JAQUE**')
                # print('El rey defensor puede moverse en: ', defender.king_legal_moves);
                # print('Las piezas aliadas del rey defensor pueden moverse: ', defender.legalMoves)
                # print('**JAQUE**')
            # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            
            if turn_attacker == 'black':
                match_state = 'White en jaque.'

            if turn_attacker == 'white':
                match_state = 'Black en jaque.'

        elif len(turn_defender.king_legal_moves) == 0 and len(turn_defender.legal_moves) == 0:
            #JAQUE-MATE
            '''Termina el juego con el actual atacante victorioso. -> Spawn OptionsMenu'''
            if turn_attacker == 'black':
                winner = True # automaticamente repercutirá draw() 
                match_state = 'Black gana.  -  White en jaque-mate.'
                pause = True
            if turn_attacker == 'white':
                winner = True # automaticamente repercutirá draw()
                match_state = 'White gana  -  Black en jaque-mate.'
                pause = True

    if turn_attacker.direct_threat_origin == 'multiple': # múltiple origen de amenaza.
        if len(turn_defender.king_legal_moves) == 0:
            #JAQUE-MATE
            '''Termina el juego con el actual atacante victorioso. -> Spawn OptionsMenu'''
            if turn_attacker == 'black':
                winner = True # repercute en render() - termina la partida
                match_state = 'Black gana.  -  White en jaque-mate.'
                pause = True

            if turn_attacker == 'white':
                winner = True # repercute en render() - termina la partida
                match_state = 'White gana  -  Black en jaque-mate.'
                pause = True
        else:
            # JAQUE
            '''Notificar al jugador correspondiente.'''
            if turn_attacker == 'black':
                match_state = 'White en jaque.'
                
            if turn_attacker == 'white':
                match_state = 'Black en jaque.'

def make_moves():
    # moving piece standpoint
    ex_value: int = list(pieceValidMovement_posDisplay.items())[0][0]

    moving_piece = turn_attacker.positions.pop(ex_value)
    if killing:
        turn_defender.positions.pop(move_here)

    # castling enablers
    if not castling:
        if ex_value in turn_attacker.castling_enablers.keys():
            if turn_attacker.castling_enablers[ex_value] == 'king': # es ex_value posición de rey?
                turn_attacker.castling_enablers = {} # no more castling
            else:  # es ex_value posición de alguna torre?
                del turn_attacker.castling_enablers[ex_value]
        
        # NORMAL MOVEMENT
        turn_attacker.positions.update({move_here: moving_piece})

    elif castling:
        turn_attacker.positions.update({move_here: moving_piece}) # mueve al rey
        ex_rook: int = {k for k,_ in turn_attacker.castling_enablers.items() if turn_attacker.castling_enablers[k] == f'{castling_direction}-rook'}.pop()
        turn_attacker.positions.pop(ex_rook)
        _direction: int = ESTE if castling_direction == 'east' else OESTE
        castling_rook_movement = ex_value+_direction # king_standpoint + dirección
        turn_attacker.positions.update({castling_rook_movement: 'rook'}) # mueve a la torre
        turn_attacker.castling_enablers = {} # no more castling
    
    pieceValidMovement_posDisplay.clear()
    kingValidCastling_posDisplay.clear()
    move_here = None
    killing = False
    castling = False
    castling_direction = ''

def match_clock():
    global winner, match_state, current_turn_time
    global globaltime_SNAP, whitetime_SNAP, blacktime_SNAP

    if not pause:
        print(pause)
        pausetime_SNAP = 0
        # global (unused but useful for tests)
        globaltime_SNAP += pause_time_leftover
        if pygame.time.get_ticks() - globaltime_SNAP > 1000: 
            time_leftover = pygame.time.get_ticks() - globaltime_SNAP - 1000
            globaltime_SNAP += 1000 - time_leftover
            current_turn_time+=1
        
        if turn_attacker == 'white':
            whitetime_SNAP += pause_time_leftover
            if pygame.time.get_ticks() - whitetime_SNAP > 1000:
                white_time_leftover = pygame.time.get_ticks() - whitetime_SNAP - 1000
                whitetime_SNAP += 1000 - white_time_leftover
                substract_time(color='white')
            else:
                white_time_leftover = pygame.time.get_ticks() - whitetime_SNAP
            
            # out of time - white lose
            if white_turn_time == 0:
                winner = True
                match_state = 'Black gana.  -  White se ha quedado sin tiempo.'
                pause = True
        
        if turn_attacker == 'black':
            blacktime_SNAP += pause_time_leftover
            if pygame.time.get_ticks() - blacktime_SNAP > 1000: 
                black_time_leftover = pygame.time.get_ticks() - blacktime_SNAP - 1000
                blacktime_SNAP += 1000 - black_time_leftover
                substract_time(color='black')
            else:
                black_time_leftover = pygame.time.get_ticks() - blacktime_SNAP
            
            # out of time - black lose
            if black_turn_time == 0:
                winner = True
                match_state = 'White gana.  -  Black se ha quedado sin tiempo.'
                pause = True

        pause_time_leftover = 0
    else:
        #pause_time++
        if pausetime_SNAP == 0:
            pausetime_SNAP = pygame.time.get_ticks()
        else:
            pause_time_leftover = pygame.time.get_ticks() - pausetime_SNAP
    
def substract_time(color):
    global black_turn_minutes, white_turn_minutes
    global black_turn_time, white_turn_time
    '''Restamos un segundo en el reloj correspondiente.
    Al ser llamada esta función ya detectamos el paso de un segundo,
    debemos entonces disminuir en 1 tanto turn_time como turn_seconds.

    Si turn_seconds nos da -1 reemplazamos por '59'
    Si turn_seconds/minutes tienen longitud de 1 dígito, añadir un 0
    al principio de la cadena.
    Tanto seconds como minutes SON STRINGS FINALMENTE.
    '''
    if color == 'black':
        black_turn_time-=1
        minutes = int(black_turn_time/60)
        black_turn_minutes = str(minutes) if len(str(minutes)) > 1 else ' '+str(minutes)
        seconds = int(black_turn_seconds) - 1
        if seconds == -1:
            black_turn_seconds = '59'
        else: black_turn_seconds = str(seconds) if len(str(seconds)) > 1 else '0'+str(seconds)

    if color == 'white':
        white_turn_time-=1
        minutes = int(white_turn_time/60)
        white_turn_minutes = str(minutes) if len(str(minutes)) > 1 else ' '+str(minutes)
        seconds = int(white_turn_seconds) - 1
        if seconds == -1:
            white_turn_seconds = '59'
        else: white_turn_seconds = str(seconds) if len(str(seconds)) > 1 else '0'+str(seconds)

def match_state():
    draw_text(match_state, 'black', 400, 20, center=False)
    draw_text(turn_attacker, 'black', mid_screen.x - 25, board.height+60, center=False)

def clock_hud():
     # global
    # draw_text(str(current_turn_time), 'black', midScreen_pos.x , 20, center=True)
    # black team clock
    draw_text(f'{black_turn_minutes}:{black_turn_seconds}', 'black', mid_screen.x + board.width/2-20, 20, center=False)
    # white team clock
    draw_text(f'{white_turn_minutes}:{white_turn_seconds}', 'black', mid_screen.x-100, 20, center=False)

def control_handler():
    if control_input['escape']: pause = not pause

def render():

    control_handler()

    # hud
    match_state()
    clock_hud()

    # core logic
    draw_board()
    match_clock()
    if move_here != None:
        make_moves()
        check_pawn_promotion()
    if finish_turn:
        update_turn_objectives()
        decide_check()
        turn_swap()
        finish_turn = False
    
    # menus
    if pause or winner or stalemate: # debería ser si el jugador apreto la tecla ESC.
        if not player_deciding_match and not winner and not stalemate:
            draw_pause_menu()
        if winner or stalemate:
            draw_post_game_menu()
        elif player_deciding_match:
            draw_confirm_restart_menu()
    if player_deciding_promotion:
        draw_pawnPromotion_selection_menu()
        
# Confirm restart (pause menu children) ----------------------------------------------------------------
def draw_confirm_restart_menu(width=300,height=300):
    # frame
    pygame.draw.rect(screen,(100,100,100),
                    pygame.Rect(screen.get_width()-400,150,width,height))
    #leyenda
    draw_text('¿Está seguro que quiere reiniciar la partida?',
        'black',screen.get_width()-400,150,center=False)
    draw_confirm_match_restart_btn()
    draw_cancel_restart_btn()
    
def draw_confirm_match_restart_btn():
    global player_deciding_match, pause

    draw_text('Si','black',screen.get_width()-400,190,center=False)
    confirm_match_rect = pygame.Rect(screen.get_width()-400,190,200,50)
    if confirm_match_rect.collidepoint((control_input['mouse-x'], control_input['mouse-y'])):
        #hover
        pygame.draw.rect(screen,(255,0,0),confirm_match_rect,width=1)
        if control_input['click']:
            reset_match()
            player_deciding_match = False
            pause = False

def draw_cancel_restart_btn():
    global player_deciding_match

    draw_text('No','black',screen.get_width()-400,250,center=False)
    cancel_match_rect = pygame.Rect(screen.get_width()-400,250,200,50)
    if cancel_match_rect.collidepoint((control_input['mouse-x'],control_input['mouse-y'])):
        #hover
        pygame.draw.rect(screen,(255,0,0),cancel_match_rect,width=1)
        if control_input['click']:
            player_deciding_match = False
# ------------------------------------------------------------------------------------------------------

# Pause menu ---------------------------------------------------------------------------------------------
def draw_pause_menu(width=300,height=400):
    # frame
    pygame.draw.rect(screen,(100,100,100),
                    pygame.Rect(screen.get_width()-400,150,width,height))
    # tooltip
    draw_text('Paused','black',screen.get_width()-400,150,center=False)
    # buttons
    draw_continue_btn()
    draw_play_again_btn()
    draw_exit_game_btn()

def draw_continue_btn():
    global pause

    draw_text('Continuar','white',screen.get_width()-400,190,center=False)
    continue_match_rect = pygame.Rect(screen.get_width()-400,190,200,50)
    if continue_match_rect.collidepoint((control_input['mouse-x'],control_input['mouse-y'])):
        #hover
        pygame.draw.rect(screen,(255,0,0),continue_match_rect,width=1)
        if control_input['click']:
            pause = False

def draw_play_again_btn():
    global player_deciding_match

    draw_text('Jugar de nuevo', 'white', screen.get_width()-400, 400, center=False)
    play_again_rect = pygame.Rect(screen.get_width()-400, 400, 200, 50)
    if play_again_rect.collidepoint((control_input['mouse-x'], control_input['mouse-y'])):
        #hover
        pygame.draw.rect(screen, (255,0,0), play_again_rect, width=1)
        if control_input['click']:
            player_deciding_match = True

def draw_exit_game_btn():
    draw_text('Salir del juego','white',screen.get_width()-400,320,center=False)
    exit_game_rect = pygame.Rect(screen.get_width()-400,320,200,50)
    if exit_game_rect.collidepoint((control_input['mouse-x'],control_input['mouse-y'])):
        #hover
        pygame.draw.rect(screen,(255,0,0),exit_game_rect,width=1)
        if control_input['click']:
            pygame.event.Event(pygame.QUIT)
# --------------------------------------------------------------------------------------------------------

# Post game menu -----------------------------------------------------------------------------------------
def draw_post_game_menu(width=300,height=300):
    # frame
    pygame.draw.rect(screen,(100,100,100),
                    pygame.Rect(screen.get_width()-400,150,width,height))
    # tooltip
    draw_text('La partida ha finalizado.', 'black', screen.get_width()-400, 150, center=False)
    draw_postgame_again_btn()
    #opciones de cambiar reglas...

def draw_postgame_again_btn():
    global pause, player_deciding_match

    draw_text('Jugar de nuevo', 'white', screen.get_width()-400,400,center=False)
    play_again_rect = pygame.Rect(screen.get_width()-400,400,200,50)
    if play_again_rect.collidepoint((control_input['mouse-x'], control_input['mouse-y'])):
        #hover
        pygame.draw.rect(screen,(255,0,0),play_again_rect,width=1)
        if control_input['click']:
            pause = False
            player_deciding_match = False
            reset_match()
# --------------------------------------------------------------------------------------------------------

# Pawn promotion menu ------------------------------------------------------------------------------------
def draw_pawnPromotion_selection_menu(width=300, height=400):
    # frame
    pygame.draw.rect(screen, (100,100,100),
                    pygame.Rect(screen.get_width()-400, 150, width, height))
    # tooltip
    draw_text('Elija su promoción', 'white', screen.get_width()-100, 400, center=True)
    draw_rookOPT_btn()
    draw_knightOPT_btn()
    draw_queenOPT_btn()
    draw_bishopOPT_btn()

def draw_rookOPT_btn():
    global pawnPromotion_selection, player_deciding_promotion
    global pause

    draw_text('Rook', 'white', screen.get_width()-400, 200, center=False)
    selection_rect = pygame.Rect(screen.get_width()-400, 200, 200, 50)
    if selection_rect.collidepoint((control_input['mouse-x'], control_input['mouse-y'])):
        #hover
        pygame.draw.rect(screen, (255,0,0), selection_rect, width=1)
        if control_input['click']:
            pawnPromotion_selection = 'rook'
            player_deciding_promotion = False
            pause = False
            make_promotion()

def draw_knightOPT_btn():
    global pawnPromotion_selection, player_deciding_promotion
    global pause

    draw_text('Knight', 'white', screen.get_width()-400, 300, center=False)
    selection_rect = pygame.Rect(screen.get_width()-400, 300, 300, 50)
    if selection_rect.collidepoint((control_input['mouse-x'], control_input['mouse-y'])):
        #hover
        pygame.draw.rect(screen, (255,0,0), selection_rect, width=1)
        if control_input['click']:
            pawnPromotion_selection = 'knight'
            player_deciding_promotion = False
            pause = False
            make_promotion()

def draw_bishopOPT_btn():
    global pawnPromotion_selection, player_deciding_promotion
    global pause

    draw_text('Bishop', 'white', screen.get_width()-400, 400, center=False)
    selection_rect = pygame.Rect(screen.get_width()-400, 400, 300, 50)
    if selection_rect.collidepoint((control_input['mouse-x'], control_input['mouse-y'])):
        #hover
        pygame.draw.rect(screen, (255,0,0), selection_rect, width=1)
        if control_input['click']:
            pawnPromotion_selection = 'bishop'
            player_deciding_promotion = False
            pause = False
            make_promotion()

def draw_queenOPT_btn(): 
    global pawnPromotion_selection, player_deciding_promotion
    global pause
    
    draw_text('Queen', 'white', screen.get_width()-400, 500, center=False)
    selection_rect = pygame.Rect(screen.get_width()-400, 500, 300, 50)
    if selection_rect.collidepoint((control_input['mouse-x'], control_input['mouse-y'])):
        #hover
        pygame.draw.rect(screen, (255,0,0), selection_rect, width=1)
        if control_input['click']:
            pawnPromotion_selection = 'queen'
            player_deciding_promotion = False
            pause = False
            make_promotion()
# --------------------------------------------------------------------------------------------------------
