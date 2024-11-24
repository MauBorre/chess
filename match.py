import pygame
from dataclasses import dataclass, field
import font, board, pieces
from board import row_of_
from board import (
    NORTE, NOR_ESTE, NOR_OESTE,
    SUR, SUR_OESTE, SUR_ESTE,
    ESTE, OESTE) # piece movement directions

# Game colors -------------------------
LEGAL_MOV_HIGHLIGHT = (100,230,100)
LEGAL_KILL_HIGHLIGHT = (230,100,100)
CASTLING_HIGHLIGHT = (100,100,230)
EMPTY_SQUARE_HIGHLIGHT = (230,230,230)
GRAY_BTN_HOVER = (230,230,230)
# -------------------------------------

@dataclass
class PlayerTeamUnit:
    name: str
    direct_threatOrigin_type: str # 'single' or 'multiple' or 'none'
    single_threat_standpoint: int | None
    king_banned_direction: int | None
    legal_moves: set[str] # DEFENDER ONLY perspective util
    
    all_effectiveThreat_standpoints: list[int] = field(default_factory=list)
    single_directThreatOnEnemy_trace: list[int] = field(default_factory=list)
    positions: dict[int, str] = field(default_factory=dict)
    pawns_in_origin: list[int] = field(default_factory=list)
    all_threat_emissions: dict[str, int] = field(default_factory=dict)
    king_legal_moves: list[int] = field(default_factory=list)
    castling_enablers: dict[int, str] = field(default_factory=dict)
    enPassant_enablers: dict[str, int] = field(default_factory=dict)
    
    def clear(self):
        self.all_threat_emissions.clear()
        self.king_legal_moves.clear()
        self.single_directThreatOnEnemy_trace.clear()
        self.direct_threatOrigin_type = 'none'
        self.single_threat_standpoint = None
        self.king_banned_direction = None
        self.legal_moves.clear()
        self.all_effectiveThreat_standpoints.clear()

class Match:
    def __init__(self, screen, control_input):
        self.running = True
        self.screen = screen
        self.curtain = pygame.Surface(self.screen.get_size(), flags=pygame.SRCALPHA)
        self.control_input = control_input
        self.mid_screen_coordinates = (self.screen.get_width()/2, self.screen.get_height()/2)
        self.mid_screen = pygame.Vector2(self.mid_screen_coordinates)
        board.place(self.mid_screen)
        self.set_content()
    
    def set_content(self):
        
        # Match initial content -----------------------------------------------
        self.black = PlayerTeamUnit(
            name = 'black',
            direct_threatOrigin_type = 'none',
            single_directThreatOnEnemy_trace = [],
            positions = pieces.black_positions.copy(),
            pawns_in_origin = [bpawn for bpawn in pieces.origins['black']['pawn']],
            all_threat_emissions = {piece:[] for piece in pieces.origins['black']},
            king_legal_moves = [],
            castling_enablers = {0: 'west-rook', 4: 'king', 7: 'east-rook'},
            single_threat_standpoint = None,
            king_banned_direction = None,
            legal_moves = set(),
            all_effectiveThreat_standpoints = [],
            enPassant_enablers = dict()
        )
        self.white = PlayerTeamUnit(
            name = 'white',
            direct_threatOrigin_type = 'none',
            single_directThreatOnEnemy_trace = [],
            positions = pieces.white_positions.copy(),
            pawns_in_origin = [wpawn for wpawn in pieces.origins['white']['pawn']],
            all_threat_emissions = {piece:[] for piece in pieces.origins['white']},
            king_legal_moves = [],
            castling_enablers = {56: 'west-rook', 60: 'king', 63: 'east-rook'},
            single_threat_standpoint = None,
            king_banned_direction = None,
            legal_moves = set(),
            all_effectiveThreat_standpoints = [],
            enPassant_enablers = dict()
        )
        
        # menu spawn variables / game halt reasons
        self.pause = False 
        self.player_selecting_gameClockLimit = True # match opening
        self.player_deciding_match: bool = False 
        self.player_deciding_promotion: bool = False
        self.winner: bool = False 
        self.game_halt: bool = False
        self.stalemate: bool = False # Ahogado | draw
        self.show_switchable_menu = True
        # ---------------------------------------
        self.curtain_transparency = 255
        self.curtain.fill((255,255,255,self.curtain_transparency))
        self.showing_openingCurtain = True
        self.showing_closingCurtain = False
        self.match_restarting = False

        # core game variables -------------------
        self.move_here: int | None = None
        self.match_state: str = '' # HUD info
        self.killing: bool = False
        self.finish_turn: bool = False # turn halt utility
        self.pawn_being_promoted: int | None = None
        self.castling: bool = False
        self.castling_direction: str = ''
        self.pawn_doubleMove: bool = False
        # ---------------------------------------

        # turn look-ups
        self.turn_attacker: PlayerTeamUnit = self.white
        self.turn_defender: PlayerTeamUnit = self.black

        # board feedback utilities
        self.selectedPiece_legalMoves: list[int] = []
        self.selectedPiece_killMoves: list[int] = []
        self.selectedPiece_castlingMoves: list[int] = []
        self.selectedPiece_pawnDoubleMove: list[int] = []

        # turn clocks (defaults)
        self.gameClockLimit_minutes: int = 10
        self.whitetime_SNAP: int = pygame.time.get_ticks()
        self.blacktime_SNAP: int = pygame.time.get_ticks()
        self.pausetime_SNAP: int = 0

        self.black_turn_time: int = self.gameClockLimit_minutes * 60
        self.black_turn_minutes: str = '00'
        self.black_turn_seconds: str = '00'

        self.white_turn_time: int = self.gameClockLimit_minutes * 60
        self.white_turn_minutes: str = '00'
        self.white_turn_seconds: str = '00'
        # clock + or - remnants
        self.white_time_leftover: int = 0
        self.black_time_leftover: int = 0
        self.pause_time_leftover: int = 0
        # ---------------------------------------------------------------
    
    def set_turn_clocks(self, minutes: int):
        self.gameClockLimit_minutes = minutes
        self.whitetime_SNAP: int = pygame.time.get_ticks()
        self.blacktime_SNAP: int = pygame.time.get_ticks()
        self.pausetime_SNAP: int = 0

        self.black_turn_time: int = self.gameClockLimit_minutes * 60
        self.black_turn_minutes: str = str(int(self.black_turn_time/60))
        self.black_turn_seconds: str = '00'

        self.white_turn_time: int = self.gameClockLimit_minutes * 60
        self.white_turn_minutes: str = str(int(self.white_turn_time/60))
        self.white_turn_seconds: str = '00'
        # clock + or - remnants
        self.white_time_leftover: int = 0
        self.black_time_leftover: int = 0
        self.pause_time_leftover: int = 1200 # default match count-down

    def draw_text(
        self,text,
        color, x, y,
        center=False, font_size='large',
        x_center=False):
        _font = font.large_font if font_size=='large' else font.medium_font
        textobj = _font.render(text,1,color)
        text_width = textobj.get_width()
        text_height = textobj.get_height()
        textrect = textobj.get_rect()
        if center: textrect.topleft = (x - text_width/2, y - text_height/2) # x&y center
        elif x_center: textrect.topleft = (x - text_width/2, y)
        else: textrect.topleft = (x,y)
        self.screen.blit(textobj,textrect)

    def check_pawn_promotion(self):
        # Obtener standpoints PAWN de attacker
        pawn_standpoints: list[int] = self.get_piece_standpoint(color=self.turn_attacker.name,piece="pawn")

        # Revisar si algun pawn llegó a la fila objetivo 
        if self.turn_attacker.name == 'white':
            for _pawn in pawn_standpoints:
                if _pawn in row_of_(0): # NORTHMOST ROW
                    self.pawn_being_promoted = _pawn
                    self.player_deciding_promotion = True
                    self.finish_turn = False
        
        # Revisar si algun pawn llegó a la fila objetivo
        if self.turn_attacker.name == 'black':
            for _pawn in pawn_standpoints:
                if _pawn in row_of_(63): # SOUTHMOST ROW
                    self.pawn_being_promoted = _pawn
                    self.player_deciding_promotion = True
                    self.finish_turn = False
        
        # allows turn to finish
        if self.pawn_being_promoted == None: self.finish_turn = True

    def make_promotion(self, selected_piece: str):
        self.turn_attacker.positions.update({self.pawn_being_promoted: selected_piece})
        self.pawn_being_promoted = None
        self.finish_turn = True

    def trace_direction_walk(
        self,
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
                        self.turn_defender.king_banned_direction = -direction # requiere dirección inversa
                        return walk_trace

                    elif walk in mixedDirections_threats:
                        walk_trace.add(walk)
        return walk_trace # vacía si llega a este punto.

    def update_turn_objectives(self):
        '''Llama a todas las funciones _objectives() con sus correctas perspectivas-de-turno.
        En este punto de la ejecución, el atacante ya hizo su acción.
        
        Antes de ser utilizadas, estas variables (excepto defender.threat_on_enemy que puede contener
        información del *jaque actual* y es resultado de transferencia/SWAP ) deben limpiarse para evitar
        un solapamiento infinito de posiciones.
        
        Primero debemos actualizar la ofensiva -siendo restringido por la defensiva-, y luego la defensiva,
        revisando especialmente si puede salvar a su rey ante la última jugada ofensiva.

        direct_threatOrigin_type será siempre y únicamente calculado luego de evaluar la ofensiva,
        Si es multiple el rey depende SOLO de su propio movimiento (o será jaque-mate).
        
        Desde perspectiva = 'attacker' es importante:

            >> Si defender.direct_threatOrigin_type = 'single' (jaque), solo puedo moverme/atacar si
                eso salva a mi rey.
                    
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
                    - Por ser REexpositivos-al-rey
                    - Por no *salvar al rey* (matando o bloqueando la amenaza)
        '''

        self.turn_attacker.clear()
        self.turn_defender.clear()

        # Attacker ----------------------------------------------------------------------------------------
        king_standpoints: list[int] = self.get_piece_standpoint(color=self.turn_attacker.name, piece="king")
        if len(king_standpoints) != 0:
            _king = king_standpoints.pop()
            self.king_objectives(_king, perspective='attacker')

        pawn_standpoints: list[int] = self.get_piece_standpoint(color=self.turn_attacker.name,piece="pawn")
        for _pawn in pawn_standpoints:
            self.pawn_objectives(_pawn, perspective='attacker')

        rook_standpoints: list[int] = self.get_piece_standpoint(color=self.turn_attacker.name,piece="rook")
        for _rook in rook_standpoints:
            self.rook_objectives(_rook, perspective='attacker')

        bishop_standpoints: list[int] = self.get_piece_standpoint(color=self.turn_attacker.name,piece="bishop")
        for _bishop in bishop_standpoints:
            self.bishop_objectives(_bishop, perspective='attacker')

        knight_standpoints: list[int] = self.get_piece_standpoint(color=self.turn_attacker.name, piece="knight")
        for _knight in knight_standpoints:
            self.knight_objectives(_knight, perspective='attacker')

        queen_standpoint: list[int] = self.get_piece_standpoint(color=self.turn_attacker.name, piece="queen")
        for _queen in queen_standpoint:
            self.queen_objectives(_queen, perspective='attacker')
        # --------------------------------------------------------------------------------------------------

        # Defender -----------------------------------------------------------------------------------------
        king_standpoints: list[int] = self.get_piece_standpoint(color=self.turn_defender.name, piece="king")
        if len(king_standpoints) != 0:
            _king = king_standpoints.pop()

        # Revisión del estado de la amenaza del atacante sobre el rey defensor (jaque)
        # La posición de orígen de la amenaza estará SIEMPRE en _threats_list[-1].
        # attacker.single_directThreatOnEnemy_trace NO INCLUIRÁ STANDPOINT DE LA AMENAZA.
        # Si la pieza amenazante es el caballo NO llamar a trace_direction_walk.
        for _threats_list in self.turn_attacker.all_threat_emissions.values():
            if _king in _threats_list:

                self.turn_attacker.all_effectiveThreat_standpoints.append(_threats_list[-1])

                if self.turn_attacker.direct_threatOrigin_type == 'single': # caso amenaza múltiple
                    self.turn_attacker.direct_threatOrigin_type = 'multiple'
                    self.turn_attacker.single_threat_standpoint = None
                    self.turn_attacker.single_directThreatOnEnemy_trace.clear()

                if self.turn_attacker.direct_threatOrigin_type == 'none':
                    self.turn_attacker.direct_threatOrigin_type = 'single'
                    self.turn_attacker.single_threat_standpoint = _threats_list[-1]
                    knight_walk_exception: str = self.turn_attacker.positions[_threats_list[-1]]
                    if knight_walk_exception != 'knight':
                        self.turn_attacker.single_directThreatOnEnemy_trace = self.trace_direction_walk(_king, _threats_list, _threats_list[-1])
                    else: self.turn_attacker.single_directThreatOnEnemy_trace = []

        self.remove_all_attacker_standpoints() # Necesario para que el rey pueda identificar piezas como -quizás matable-.
        self.king_objectives(_king, perspective='defender') # genero/reviso defender.king_legal_moves.

        if self.turn_attacker.direct_threatOrigin_type != 'multiple':
            # defender legal moves update
            pawn_standpoints = self.get_piece_standpoint(color=self.turn_defender.name, piece='pawn')
            for _pawn in pawn_standpoints:
                self.pawn_objectives(_pawn, perspective='defender')

            rook_standpoints = self.get_piece_standpoint(color=self.turn_defender.name, piece="rook")
            for _rook in rook_standpoints:
                self.rook_objectives(_rook, perspective='defender')
            
            bishop_standpoints = self.get_piece_standpoint(color=self.turn_defender.name, piece='bishop')
            for _bishop in bishop_standpoints:
                self.bishop_objectives(_bishop, perspective='defender')
            
            knight_standpoints = self.get_piece_standpoint(color=self.turn_defender.name, piece="knight")
            for _knight in knight_standpoints:
                self.knight_objectives(_knight, perspective='defender')
            
            queen_standpoint = self.get_piece_standpoint(color=self.turn_defender.name, piece="queen")
            for _queen in queen_standpoint:
                self.queen_objectives(_queen, perspective='defender')
        # -------------------------------------------------------------------------------------------------

    def turn_swap(self):

        if self.turn_attacker == self.white:

            if self.black_time_leftover < 1000:
                self.blacktime_SNAP = pygame.time.get_ticks() - self.black_time_leftover
            else:
                self.blacktime_SNAP = pygame.time.get_ticks() + self.black_time_leftover

            self.turn_attacker = self.black
            self.turn_defender = self.white

            return
        
        if self.turn_attacker == self.black:

            if self.white_time_leftover < 1000:
                self.whitetime_SNAP = pygame.time.get_ticks() - self.white_time_leftover
            else:
                self.whitetime_SNAP = pygame.time.get_ticks() + self.white_time_leftover

            self.turn_attacker = self.white
            self.turn_defender = self.black

            return

    def remove_all_attacker_standpoints(self):
        '''
        Quita TODOS los standpoints de attacker.all_threat_emissions
        (y por consecuente su vuelta como def_threatOnAtt).
        Los standpoints coinciden SIEMPRE en el último item de la lista de amenazas.
        De esta forma aclaramos la visión al rey correspondiente en cuanto a amenazas
        matables y no-matables.
        '''
        for _threats in self.turn_attacker.all_threat_emissions.values():
            _threats.pop()

    def exposing_direction(self, standpoint: int, intended_move: int, request_from: str) -> bool:
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
        **IMPORTANTE** Para evitar superposiciones de piezas que nos den errores, no haremos
        las comprobaciones de fake_positions que caigan justo en posición del otro equipo.
        la superposición de posiciones nos dictará incorrectamente que estamos exponiendo al rey 
        cuando en realidad *quizás* mataríamos a la pieza.
        '''
        fake_move: int = standpoint+intended_move
        fake_positions: dict[int, str] = {}

        if request_from == 'attacker':
            for ap in self.turn_attacker.positions.keys():
                if standpoint != ap:
                    fake_positions.update({ap: self.turn_attacker.positions[ap]})
                else:
                    fake_positions.update({fake_move: self.turn_attacker.positions[ap]})

            if self.turn_defender.direct_threatOrigin_type == 'single':
                '''Si el ATACANTE está en jaque, debemos filtrar y descartar la pieza
                DEFENSORA amenazante (Torre, Alfil o Reina) o nunca obtendremos el resultado
                esperado, nos dirá SIEMPRE que estamos exponiendo al rey porque ya está en jaque.'''
                # nombre de la pieza que NO debemos considerar
                rejected_piece: str = self.turn_defender.positions[self.turn_defender.single_threat_standpoint]

                if rejected_piece != 'rook':
                    rook_standpoints: list[int] = self.get_piece_standpoint(color=self.turn_defender.name,piece="rook")
                    for _rook in rook_standpoints:
                        if _rook != fake_move:
                            if self.rook_objectives(_rook, perspective='fake-attackerMov-toDef', fake_positions=fake_positions):
                                return True
                
                if rejected_piece != 'bishop':
                    bishop_standpoints: list[int] = self.get_piece_standpoint(color=self.turn_defender.name,piece="bishop")
                    for _bishop in bishop_standpoints:
                        if _bishop != fake_move:
                            if self.bishop_objectives(_bishop, perspective='fake-attackerMov-toDef', fake_positions=fake_positions):
                                return True

                if rejected_piece != 'queen':
                    queen_standpoint: list[int] = self.get_piece_standpoint(color=self.turn_defender.name, piece="queen")
                    for _queen in queen_standpoint:
                        if _queen != fake_move:
                            if self.queen_objectives(_queen, perspective='fake-attackerMov-toDef', fake_positions=fake_positions):
                                return True
                return False

            elif self.turn_defender.direct_threatOrigin_type == 'none':

                rook_standpoints: list[int] = self.get_piece_standpoint(color=self.turn_defender.name,piece="rook")
                for _rook in rook_standpoints:
                    if _rook != fake_move:
                        if self.rook_objectives(_rook, perspective='fake-attackerMov-toDef', fake_positions=fake_positions):
                            return True

                bishop_standpoints: list[int] = self.get_piece_standpoint(color=self.turn_defender.name,piece="bishop")
                for _bishop in bishop_standpoints:
                    if _bishop != fake_move:
                        if self.bishop_objectives(_bishop, perspective='fake-attackerMov-toDef', fake_positions=fake_positions):
                            return True

                queen_standpoint: list[int] = self.get_piece_standpoint(color=self.turn_defender.name, piece="queen")
                for _queen in queen_standpoint:
                    if _queen != fake_move:
                        if self.queen_objectives(_queen, perspective='fake-attackerMov-toDef', fake_positions=fake_positions):
                            return True
                return False

        if request_from == 'defender':

            for dp in self.turn_defender.positions.keys():
                if standpoint != dp:
                    fake_positions.update({dp: self.turn_defender.positions[dp]})
                else:
                    fake_positions.update({fake_move: self.turn_defender.positions[dp]})

            rook_standpoints: list[int] = self.get_piece_standpoint(color=self.turn_attacker.name,piece="rook")
            for _rook in rook_standpoints:
                if _rook != fake_move:
                    if self.rook_objectives(_rook, perspective='fake-defenderMov-toAtt', fake_positions=fake_positions):
                        return True

            bishop_standpoints: list[int] = self.get_piece_standpoint(color=self.turn_attacker.name,piece="bishop")
            for _bishop in bishop_standpoints:
                if _bishop != fake_move:
                    if self.bishop_objectives(_bishop, perspective='fake-defenderMov-toAtt', fake_positions=fake_positions):
                        return True

            queen_standpoint: list[int] = self.get_piece_standpoint(color=self.turn_attacker.name, piece="queen")
            for _queen in queen_standpoint:
                if _queen != fake_move:
                    if self.queen_objectives(_queen, perspective='fake-defenderMov-toAtt', fake_positions=fake_positions):
                        return True
            return False

    def pawn_objectives(self, piece_standpoint: int, perspective: str) -> dict[int, pygame.Rect] | None:
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
        _legal_movements: list[int] = [piece_standpoint] # standpoint is always first pos 
        on_target_kill_positions: list[int] = []
        double_movement: list[int] = []
        
        # Objectives
        kill_positions: list[int] = []
        movement: int

        if perspective == 'defender' :
            if self.turn_defender.name == 'black': # defiende hacia el SUR
            
                # 1st Movement
                movement = piece_standpoint+SUR
                if movement <= 63: # board limit

                    if self.turn_attacker.direct_threatOrigin_type == 'single':
                        if movement not in self.turn_defender.positions or movement not in self.turn_attacker.positions:
                            if not self.exposing_direction(piece_standpoint, intended_move=SUR, request_from="defender"):
                                
                                # 1st Movement -BLOCK saving position-
                                if movement in self.turn_attacker.single_directThreatOnEnemy_trace:
                                    self.turn_defender.legal_moves.add(f'pawn{piece_standpoint}')

                                # 2nd Movement
                                if piece_standpoint in self.black.pawns_in_origin:
                                    if movement+SUR not in self.turn_defender.positions:

                                        # 2nd Movement -BLOCK saving position-
                                        if movement+SUR in self.turn_attacker.single_directThreatOnEnemy_trace:
                                            self.turn_defender.legal_moves.add(f'pawn{piece_standpoint}')    
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
                            if kp in self.turn_attacker.positions:
                                if not self.exposing_direction(piece_standpoint, intended_move=kp-piece_standpoint, request_from="defender"):
                                    if kp == self.turn_attacker.single_threat_standpoint:
                                        self.turn_defender.legal_moves.add(f'pawn{piece_standpoint}')
                        return
                            
                    elif self.turn_attacker.direct_threatOrigin_type == 'none': 
                        if movement not in self.turn_defender.positions or movement not in self.turn_attacker.positions:
                            if not self.exposing_direction(piece_standpoint, intended_move=SUR, request_from="defender"):
                                self.turn_defender.legal_moves.add(f'pawn{piece_standpoint}')
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
                            if kp in self.turn_attacker.positions:
                                if not self.exposing_direction(piece_standpoint, intended_move=kp-piece_standpoint, request_from="defender"):
                                    self.turn_defender.legal_moves.add(f'pawn{piece_standpoint}')
                        return
                return

            if self.turn_defender.name == 'white': # defiende hacia el NORTE

                # 1st Movement
                movement = piece_standpoint+NORTE
                if movement <= 63: # board limit

                    if self.turn_attacker.direct_threatOrigin_type == 'single':
                        if movement not in self.turn_defender.positions:
                            if not self.exposing_direction(piece_standpoint, intended_move=NORTE, request_from="defender"):

                                # 1st Movement -BLOCK saving position-
                                if movement in self.turn_attacker.single_directThreatOnEnemy_trace:
                                    self.turn_defender.legal_moves.add(f'pawn{piece_standpoint}')
                                
                                # 2nd Movement
                                if piece_standpoint in self.white.pawns_in_origin:
                                    if movement+NORTE not in self.turn_defender.positions:
                                        
                                        # 2nd Movement -BLOCK saving position-
                                        if movement+NORTE in self.turn_attacker.single_directThreatOnEnemy_trace:
                                            self.turn_defender.legal_moves.add(f'pawn{piece_standpoint}')
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
                            if kp in self.turn_attacker.positions:
                                if not self.exposing_direction(piece_standpoint, intended_move=kp-piece_standpoint, request_from="defender"):
                                    if kp == self.turn_attacker.single_threat_standpoint:
                                        self.turn_defender.legal_moves.add(f'pawn{piece_standpoint}')
                        return
                                        
                    elif self.turn_attacker.direct_threatOrigin_type == 'none':
                        if movement not in self.turn_defender.positions or movement not in self.turn_attacker.positions:
                            if not self.exposing_direction(piece_standpoint, intended_move=NORTE, request_from="defender"):
                                self.turn_defender.legal_moves.add(f'pawn{piece_standpoint}')
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
                            if kp in self.turn_attacker.positions:
                                if not self.exposing_direction(piece_standpoint, intended_move=kp-piece_standpoint, request_from="defender"):
                                    self.turn_defender.legal_moves.add(f'pawn{piece_standpoint}')
                        return
                return
            return

        if perspective == 'attacker':
            if self.turn_attacker.name == 'black': # Ataca hacia el SUR

                # 1st Movement
                movement = piece_standpoint+SUR
                if movement <= 63: # board limit

                    if self.turn_defender.direct_threatOrigin_type == 'single':
                        if movement not in self.turn_attacker.positions and movement not in self.turn_defender.positions: # piece block
                            if not self.exposing_direction(piece_standpoint, intended_move=SUR, request_from="attacker"):
                                if movement in self.turn_defender.single_directThreatOnEnemy_trace:
                                    # BLOCK saving position
                                    _legal_movements.append(movement)

                                #probamos con el 2do mov
                                if piece_standpoint in self.black.pawns_in_origin:
                                    if movement+SUR not in self.turn_attacker.positions and movement+SUR not in self.turn_defender.positions: # piece block
                                        if movement+SUR in self.turn_defender.single_directThreatOnEnemy_trace:
                                            # BLOCK saving position
                                            _legal_movements.update({movement+SUR: board.rects[movement+SUR]})

                        # kill-movements
                        # board limits check
                        if piece_standpoint+OESTE not in row_of_(piece_standpoint):
                            kill_positions.append(piece_standpoint+SUR_ESTE)
                        if piece_standpoint+ESTE not in row_of_(piece_standpoint):
                            kill_positions.append(piece_standpoint+SUR_OESTE)
                        elif len(kill_positions) == 0:
                            kill_positions.extend([piece_standpoint+SUR_OESTE, piece_standpoint+SUR_ESTE])
                        
                        for kp in kill_positions:
                            if kp not in self.turn_attacker.positions and kp == self.turn_defender.single_threat_standpoint: 
                                if not self.exposing_direction(piece_standpoint, intended_move=kp-piece_standpoint, request_from="attacker"):
                                    # KILL saving position
                                    on_target_kill_positions.append(kp)
                            #necesitamos desarrollar aquí el caso especial en-passant que puede salvar al rey

                        return _legal_movements, on_target_kill_positions, double_movement

                    elif self.turn_defender.direct_threatOrigin_type == 'none': 

                        if movement not in self.turn_attacker.positions and movement not in self.turn_defender.positions: # piece block
                            if not self.exposing_direction(piece_standpoint, intended_move=SUR, request_from="attacker"):
                                _legal_movements.append(movement) # 1st Movement

                                if piece_standpoint in self.black.pawns_in_origin:
                                    if movement+SUR <= 63: # board limit check
                                        if movement+SUR not in self.turn_attacker.positions and movement+SUR not in self.turn_defender.positions: # piece block
                                            _legal_movements.append(movement+SUR) # 2nd Movement 
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
                            if kp not in self.turn_attacker.positions:
                                if kp in self.turn_defender.positions:
                                    if not self.exposing_direction(piece_standpoint, intended_move=kp-piece_standpoint, request_from="attacker"):
                                        on_target_kill_positions.append(kp)
                            #necesitamos desarrollar en-passant aquí
                                
                        # Threat on defender ------------------------
                        kill_positions.append(piece_standpoint)
                        self.turn_attacker.all_threat_emissions.update({f'pawn{piece_standpoint}': kill_positions})

                        return _legal_movements, on_target_kill_positions, double_movement

            if self.turn_attacker.name == 'white': # Ataca hacia el NORTE

                # 1st Movement
                movement = piece_standpoint+NORTE
                if movement >= 0: # board limit
                    
                    if self.turn_defender.direct_threatOrigin_type == 'single':
                        if movement not in self.turn_attacker.positions and movement not in self.turn_defender.positions: # piece block
                            if not self.exposing_direction(piece_standpoint, intended_move=NORTE, request_from="attacker"):
                                if movement in self.turn_defender.single_directThreatOnEnemy_trace:
                                    # BLOCK saving position
                                    _legal_movements.append(movement)

                                #probamos con el 2do mov
                                if piece_standpoint in self.white.pawns_in_origin:
                                    if movement+NORTE not in self.turn_attacker.positions and movement+NORTE not in self.turn_defender.positions:# piece block
                                        if movement+NORTE in self.turn_defender.single_directThreatOnEnemy_trace:
                                            # BLOCK saving position
                                            _legal_movements.append(movement+NORTE)

                        # kill-movements
                        # board limits check
                        if piece_standpoint+OESTE not in row_of_(piece_standpoint):
                            kill_positions.append(piece_standpoint+NOR_ESTE)
                        if piece_standpoint+ESTE not in row_of_(piece_standpoint):
                            kill_positions.append(piece_standpoint+NOR_OESTE)
                        elif len(kill_positions) == 0:
                            kill_positions.extend([piece_standpoint+NOR_OESTE, piece_standpoint+NOR_ESTE])
                                    
                        for kp in kill_positions:
                            if kp not in self.turn_attacker.positions and kp == self.turn_defender.single_threat_standpoint:
                                if not self.exposing_direction(piece_standpoint, intended_move=kp-piece_standpoint, request_from="attacker"):
                                    # KILL saving position
                                    on_target_kill_positions.append(kp)
                            #necesitamos desarrollar aquí el caso especial en-passant que puede salvar al rey
                        
                        return _legal_movements, on_target_kill_positions, double_movement
                                    
                    elif self.turn_defender.direct_threatOrigin_type == 'none': # no jaque

                        if movement not in self.turn_attacker.positions and movement not in self.turn_defender.positions: # piece block
                            if not self.exposing_direction(piece_standpoint, intended_move=NORTE, request_from="attacker"):  
                                _legal_movements.append(movement) # 1st Movement

                                if piece_standpoint in self.white.pawns_in_origin:
                                    if movement+NORTE >= 0: # board limit check
                                        if movement+NORTE not in self.black.positions and movement+NORTE not in self.white.positions: # piece block
                                            _legal_movements.append(movement+NORTE) # 2nd Movement
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
                            if kp not in self.turn_attacker.positions:
                                if kp in self.turn_defender.positions:
                                    if not self.exposing_direction(piece_standpoint, intended_move=kp-piece_standpoint, request_from="attacker"):
                                        on_target_kill_positions.append(kp)
                            #necesitamos desarrollar en-passant aquí
                            #if kp in enPassant_enabler and piece_standpoint in enPassant_enabler: ...

                        # Threat on defender ------------------------
                        kill_positions.append(piece_standpoint)
                        self.turn_attacker.all_threat_emissions.update({f'pawn{piece_standpoint}': kill_positions})

                        return _legal_movements, on_target_kill_positions, double_movement
            return _legal_movements, on_target_kill_positions, double_movement

    def rook_objectives(
        self,
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
        _legal_movements: list[int] = [piece_standpoint] # standpoint is always first pos
        on_target_kill_positions: list[int] = []
        
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
                        if movement in self.turn_defender.positions:
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
                        if movement in self.turn_attacker.positions:
                            break 

                        elif movement in fake_positions:
                            if fake_positions[movement] == 'king':
                                return True
                            else: break # descartar kill-movements que NO sean al rey
            return False
        
        if perspective == 'defender':
            for direction in rook_directions:
                for mult in range(1,8): # 1 to board_size
                    movement = piece_standpoint+direction*mult
                    if direction == ESTE or direction == OESTE:
                        if movement not in row_of_(piece_standpoint):
                            break
                    if 0 <= movement <= 63: # VALID SQUARE

                        if self.exposing_direction(piece_standpoint, intended_move=direction, request_from="defender"):
                            continue
                        if movement in self.turn_defender.positions:
                            break

                        if self.turn_attacker.direct_threatOrigin_type == 'single':
                            if movement in self.turn_attacker.single_directThreatOnEnemy_trace:
                                # block saving position
                                self.turn_defender.legal_moves.add(f'rook{piece_standpoint}') 
                            elif movement == self.turn_attacker.single_threat_standpoint:
                                # kill saving position
                                self.turn_defender.legal_moves.add(f'rook{piece_standpoint}')
                        
                        elif self.turn_attacker.direct_threatOrigin_type == 'none':
                            self.turn_defender.legal_moves.add(f'rook{piece_standpoint}')
            return

        if perspective == 'attacker': 
            if self.turn_defender.direct_threatOrigin_type == 'single':
                for direction in rook_directions:
                    for mult in range(1,8): # 1 to board_size
                        movement = piece_standpoint+direction*mult
                        if direction == ESTE or direction == OESTE:
                            if movement not in row_of_(piece_standpoint):
                                break
                        if 0 <= movement <= 63: # VALID SQUARE

                            if self.exposing_direction(piece_standpoint, intended_move=direction, request_from='attacker'):
                                break
                            if movement not in self.turn_attacker.positions and movement not in self.turn_defender.positions:
                                if movement in self.turn_defender.single_directThreatOnEnemy_trace:
                                    # BLOCK saving position.
                                    _legal_movements.append(movement)
                                    break
                            elif movement == self.turn_defender.single_threat_standpoint:
                                # KILL saving position.
                                on_target_kill_positions.append(movement)
                                break
                            else: break # ally block
                return _legal_movements, on_target_kill_positions
                
            elif self.turn_defender.direct_threatOrigin_type == 'none':
                for direction in rook_directions:
                    for mult in range(1,8): # 1 to board_size
                        movement = piece_standpoint+direction*mult
                        if direction == ESTE or direction == OESTE:
                            if movement not in row_of_(piece_standpoint):
                                break
                        if 0 <= movement <= 63: # VALID SQUARE

                            if self.exposing_direction(piece_standpoint, intended_move=direction, request_from='attacker'):
                                break
                            if movement not in self.turn_attacker.positions and movement not in self.turn_defender.positions:
                                _threat_emission.append(movement)
                                _legal_movements.append(movement) 
                            # Kill-movement
                            elif movement in self.turn_defender.positions:
                                _threat_emission.append(movement)
                                on_target_kill_positions.append(movement)
                                break
                            else: # ally block
                                _threat_emission.append(movement)
                                break

                _threat_emission.append(piece_standpoint)
                self.turn_attacker.all_threat_emissions.update({f'rook{piece_standpoint}': _threat_emission})

                return _legal_movements, on_target_kill_positions
            return _legal_movements, on_target_kill_positions

    def knight_objectives(self, piece_standpoint: int, perspective: str) -> dict[int,pygame.Rect] | None:
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
        Unica pieza la cual podemos descartar todos sus movimientos si uno solo -expone-.
        '''
        
        # Visual feedback utils
        _legal_movements: list[int] = [piece_standpoint] # standpoint is always first pos
        on_target_kill_positions: list[int] = []

        # Objectives
        _threat_emission: list[int] = []
        knight_pre_movements = []

        # ESTE / OESTE LIMITS
        if piece_standpoint+ESTE in row_of_(piece_standpoint):
            knight_pre_movements.extend([piece_standpoint+NORTE+NOR_ESTE,
                                        piece_standpoint+SUR+SUR_ESTE])
            if piece_standpoint+ESTE*2 in row_of_(piece_standpoint):
                knight_pre_movements.extend([piece_standpoint+ESTE+NOR_ESTE,
                                            piece_standpoint+ESTE+SUR_ESTE])
        if piece_standpoint+OESTE in row_of_(piece_standpoint):
            knight_pre_movements.extend([piece_standpoint+NORTE+NOR_OESTE,
                                        piece_standpoint+SUR+SUR_OESTE])
            if piece_standpoint+OESTE*2 in row_of_(piece_standpoint):
                knight_pre_movements.extend([piece_standpoint+OESTE+NOR_OESTE,
                                            piece_standpoint+OESTE+SUR_OESTE])
        
        if perspective == 'defender':
            for movement in knight_pre_movements:
                if 0 <= movement <= 63: # NORTE/SUR LIMIT

                    if self.exposing_direction(piece_standpoint, intended_move=movement-piece_standpoint, request_from="defender"):
                        return
                    
                    if self.turn_attacker.direct_threatOrigin_type == 'single':
                        if movement not in self.turn_defender.positions:

                            if movement in self.turn_attacker.single_directThreatOnEnemy_trace:
                                self.turn_defender.legal_moves.add(f'knight{piece_standpoint}')

                            if movement == self.turn_attacker.single_threat_standpoint:
                                self.turn_defender.legal_moves.add(f'knight{piece_standpoint}')

                    elif self.turn_attacker.direct_threatOrigin_type == 'none':
                        if movement not in self.turn_defender.positions:
                            self.turn_defender.legal_moves.add(f'knight{piece_standpoint}')
            return

        if perspective == 'attacker':
            if self.turn_defender.direct_threatOrigin_type == 'single':
                for movement in knight_pre_movements:
                    if 0 <= movement <= 63: # NORTE/SUR LIMIT 

                        if self.exposing_direction(piece_standpoint, intended_move=movement-piece_standpoint, request_from="attacker"):
                            return {}, {}

                        if movement not in self.turn_attacker.positions and movement not in self.turn_defender.positions:
                            if movement in self.turn_defender.single_directThreatOnEnemy_trace:
                                # BLOCK saving position.
                                _legal_movements.append(movement)
                        elif movement == self.turn_defender.single_threat_standpoint:
                            # KILL saving position.
                            on_target_kill_positions.append(movement)

                return _legal_movements, on_target_kill_positions
            
            elif self.turn_defender.direct_threatOrigin_type == 'none':
                for movement in knight_pre_movements:
                    if 0 <= movement <= 63: # NORTE/SUR LIMIT 

                        if self.exposing_direction(piece_standpoint, intended_move=movement-piece_standpoint, request_from="attacker"):
                            return {}, {}
                        
                        if movement not in self.turn_attacker.positions and movement not in self.turn_defender.positions:
                            # Movement
                            _threat_emission.append(movement)
                            _legal_movements.append(movement) 
                        # Kill-movement
                        elif movement in self.turn_defender.positions:
                            _threat_emission.append(movement)
                            on_target_kill_positions.append(movement)
                        else:  _threat_emission.append(movement)

                _threat_emission.append(piece_standpoint)
                self.turn_attacker.all_threat_emissions.update({f'knight{piece_standpoint}': _threat_emission})

                return _legal_movements, on_target_kill_positions
            return _legal_movements, on_target_kill_positions 

    def bishop_objectives(
        self,
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
        
        # Visual feedback utils
        _legal_movements: list[int] = [piece_standpoint] # standpoint is always first pos
        on_target_kill_positions: list[int] = []
        
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
                        if movement in self.turn_defender.positions:
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
                        if movement in self.turn_attacker.positions:
                            break
                        
                        elif movement in fake_positions:
                            if fake_positions[movement] == 'king':
                                return True
                            else: break # descartar kill-movements que NO sean al rey
            return False

        if perspective == 'defender':
            # if self.turn_attacker.direct_threatOrigin_type == 'single':
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

                        if self.exposing_direction(piece_standpoint, intended_move=direction, request_from="defender"):
                            continue
                        if movement in self.turn_defender.positions:
                            break

                        if self.turn_attacker.direct_threatOrigin_type == 'single':
                            if movement in self.turn_attacker.single_directThreatOnEnemy_trace:
                                # block saving position
                                self.turn_defender.legal_moves.add(f'bishop{piece_standpoint}')
                            if movement == self.turn_attacker.single_threat_standpoint:
                                # kill saving position
                                self.turn_defender.legal_moves.add(f'bishop{piece_standpoint}')
                        
                        elif self.turn_attacker.direct_threatOrigin_type == 'none':
                            self.turn_defender.legal_moves.add(f'bishop{piece_standpoint}')
            return

        if perspective == 'attacker':
            if self.turn_defender.direct_threatOrigin_type == 'single':
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

                            if self.exposing_direction(piece_standpoint, intended_move=direction, request_from='attacker'):
                                break
                            if movement not in self.turn_attacker.positions and movement not in self.turn_defender.positions:
                                if movement in self.turn_defender.single_directThreatOnEnemy_trace:
                                    # BLOCK saving position.
                                    _legal_movements.append(movement)
                                    break
                            elif movement == self.turn_defender.single_threat_standpoint:
                                # KILL saving position.
                                on_target_kill_positions.append(movement)
                                break
                            else: break # ally block
                return _legal_movements, on_target_kill_positions
            
            elif self.turn_defender.direct_threatOrigin_type == 'none':
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

                            if self.exposing_direction(piece_standpoint, intended_move=direction, request_from="attacker"):
                                break
                            if movement not in self.turn_attacker.positions and movement not in self.turn_defender.positions:
                                _threat_emission.append(movement)
                                _legal_movements.append(movement)
                            # Kill-movement
                            elif movement in self.turn_defender.positions: 
                                _threat_emission.append(movement)
                                on_target_kill_positions.append(movement)
                                break
                            else: # ally block
                                _threat_emission.append(movement)
                                break

                _threat_emission.append(piece_standpoint)
                self.turn_attacker.all_threat_emissions.update({f'bishop{piece_standpoint}': _threat_emission})

                return _legal_movements, on_target_kill_positions
            return _legal_movements, on_target_kill_positions 

    def queen_objectives(
        self,
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
        _legal_movements: list[int] = [piece_standpoint] # standpoint is always first pos
        on_target_kill_positions: list[int] = []

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
                        if movement in self.turn_defender.positions:
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
                        if movement in self.turn_attacker.positions:
                            break

                        elif movement in fake_positions:
                            if fake_positions[movement] == 'king':
                                return True
                            else: break # descartar kill-movements que NO sean al rey
            return False

        if perspective == 'defender':
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

                        if self.exposing_direction(piece_standpoint, intended_move=direction, request_from="defender"):
                            continue
                        if movement in self.turn_defender.positions:
                            break

                        if self.turn_attacker.direct_threatOrigin_type == 'single':
                            if movement in self.turn_attacker.single_directThreatOnEnemy_trace:
                                # block saving position
                                self.turn_defender.legal_moves.add(f'queen{piece_standpoint}')
                            if movement == self.turn_attacker.single_threat_standpoint:
                                # kill saving position
                                self.turn_defender.legal_moves.add(f'queen{piece_standpoint}')

                        elif self.turn_attacker.direct_threatOrigin_type == 'none':
                            self.turn_defender.legal_moves.add(f'queen{piece_standpoint}')       
            return                   
        
        if perspective == 'attacker':
            if self.turn_defender.direct_threatOrigin_type == 'single':
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

                            if self.exposing_direction(piece_standpoint, intended_move=direction, request_from='attacker'):
                                break
                            if movement not in self.turn_attacker.positions and movement not in self.turn_defender.positions:
                                if movement in self.turn_defender.single_directThreatOnEnemy_trace:
                                    # BLOCK saving position.
                                    _legal_movements.append(movement)
                                    break
                            elif movement == self.turn_defender.single_threat_standpoint:
                                # KILL saving position.
                                on_target_kill_positions.append(movement)
                                break      
                            else: break # ally block
                return _legal_movements, on_target_kill_positions
                
            elif self.turn_defender.direct_threatOrigin_type == 'none':
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

                            if self.exposing_direction(piece_standpoint, intended_move=direction, request_from='attacker'):
                                break
                            if movement not in self.turn_attacker.positions and movement not in self.turn_defender.positions:
                                _threat_emission.append(movement)
                                _legal_movements.append(movement) 
                            # Kill-movement
                            elif movement in self.turn_defender.positions:
                                _threat_emission.append(movement) 
                                on_target_kill_positions.append(movement)
                                break
                            else:  # ally block
                                _threat_emission.append(movement)
                                break

                _threat_emission.append(piece_standpoint)
                self.turn_attacker.all_threat_emissions.update({f'queen{piece_standpoint}': _threat_emission})

                return _legal_movements, on_target_kill_positions
            return _legal_movements, on_target_kill_positions

    def king_objectives(self, piece_standpoint: int, perspective: str) -> dict[int, pygame.Rect]:
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
        _legal_movements: list[int] = [piece_standpoint] # standpoint is always first pos
        on_target_kill_positions: list[int] = []
        castling_positions: list[int] = []
        
        # Objectives
        _threat_emission: list[int] = []
        _castling: int | None = None # pre-evaluated position
        king_directions = [NORTE,SUR,ESTE,OESTE,NOR_OESTE,NOR_ESTE,SUR_OESTE,SUR_ESTE]

        if perspective == 'defender':
            for direction in king_directions:
                if direction == self.turn_defender.king_banned_direction:
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

                    for threat in self.turn_attacker.all_threat_emissions.values():
                        if movement in threat: movement = None

                    if movement != None:
                        if movement not in self.turn_defender.positions: # ally block
                            self.turn_defender.king_legal_moves.append(movement)
            return
        
        if perspective == 'attacker':
            for direction in king_directions:
                if direction == self.turn_attacker.king_banned_direction:
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

                    for threat in self.turn_defender.all_threat_emissions.values():
                        if movement in threat: movement = None
                        if _castling in threat: _castling = None

                    if movement != None:

                        if movement not in self.turn_attacker.positions and not movement in self.turn_defender.positions:
                            _threat_emission.append(movement)
                            self.turn_attacker.king_legal_moves.append(movement)
                            _legal_movements.append(movement)

                            # castling -WEST-
                            if direction == OESTE:
                                if 'king' and 'west-rook' in self.turn_attacker.castling_enablers.values():
                                    if self.turn_defender.direct_threatOrigin_type == 'none':       
                                        if _castling != None:
                                            if _castling not in self.turn_attacker.positions and not _castling in self.turn_defender.positions:
                                                if _castling+direction not in self.turn_attacker.positions and _castling+direction not in self.turn_defender.positions:
                                                    self.turn_attacker.king_legal_moves.append(_castling)
                                                    castling_positions.append(_castling)
                                                    self.castling_direction = 'west'

                            # castling -EAST-
                            if direction == ESTE:
                                if 'king' and 'east-rook' in self.turn_attacker.castling_enablers.values():
                                    if self.turn_defender.direct_threatOrigin_type == 'none':
                                        if _castling != None:
                                            if _castling not in self.turn_attacker.positions and not _castling in self.turn_defender.positions:
                                                self.turn_attacker.king_legal_moves.append(_castling)
                                                castling_positions.append(_castling)
                                                self.castling_direction = 'east'

                        elif movement in self.turn_defender.positions:
                            _threat_emission.append(movement)
                            self.turn_attacker.king_legal_moves.append(movement)
                            on_target_kill_positions.append(movement)
                        else:
                            _threat_emission.append(movement)

            _threat_emission.append(piece_standpoint)
            self.turn_attacker.all_threat_emissions.update({'king': _threat_emission})

            return _legal_movements, on_target_kill_positions, castling_positions

    def draw_board(self):

        styleAux_row = 1
        for board_index, SQUARE_RECT in enumerate(board.rects): #celdas que sirven por posición, índice y medida.
            
            # Square style
            if board_index == 8*styleAux_row: styleAux_row+=1
            # fill
            if board_index % 2 == 0:
                if styleAux_row % 2 == 1:
                    pygame.draw.rect(self.screen, board.light_square, SQUARE_RECT)
                if styleAux_row % 2 == 0:
                    pygame.draw.rect(self.screen, board.dark_square, SQUARE_RECT)
            if board_index % 2 == 1:
                if styleAux_row % 2 == 0:
                    pygame.draw.rect(self.screen, board.light_square, SQUARE_RECT)
                if styleAux_row % 2 == 1:
                    pygame.draw.rect(self.screen, board.dark_square, SQUARE_RECT)
            # grid
            pygame.draw.rect(self.screen, board.dark_square, SQUARE_RECT, width=1)

            # debug square tooltip
            # self.draw_text(f'{board_index}',(150,150,150),
            #                 SQUARE_RECT.left +3,
            #                 SQUARE_RECT.top + board.square_height -17,
            #                 center=False, font_size='medium')
            
            # Square types/subtypes -----------------------------------------------------------------------------
            if board_index in self.black.positions.keys():
                SQUARE_SUBTYPE = "kill-movement" if board_index in self.selectedPiece_killMoves else ""
                SQUARE_TYPE =  self.black.positions[board_index]
                interacted_PColor = "black"

            elif board_index in self.white.positions.keys():
                SQUARE_SUBTYPE = "kill-movement" if board_index in self.selectedPiece_killMoves else ""
                SQUARE_TYPE = self.white.positions[board_index]
                interacted_PColor = "white"

            elif board_index in self.selectedPiece_legalMoves:
                SQUARE_SUBTYPE = "valid-movement"
                SQUARE_TYPE = ""
                interacted_PColor = ""
            
            elif board_index in self.selectedPiece_castlingMoves:
                SQUARE_SUBTYPE = "castling-movement"
                SQUARE_TYPE = ""
                interacted_PColor = ""
            
            elif board_index in self.selectedPiece_pawnDoubleMove:
                SQUARE_SUBTYPE = "pawn-double-movement"
                SQUARE_TYPE = ""
                interacted_PColor = ""

            else: SQUARE_TYPE = "EMPTY"; interacted_PColor = ""; SQUARE_SUBTYPE = ""
            # ----------------------------------------------------------------------------------------------------

            # draw piece
            if SQUARE_TYPE != "EMPTY":
                if interacted_PColor == 'black':
                    self.draw_text(
                        SQUARE_TYPE,'black',
                        SQUARE_RECT.left + board.square_width/2,
                        SQUARE_RECT.top + board.square_height/2,
                        center=True)
                if interacted_PColor == 'white':
                    self.draw_text(
                        SQUARE_TYPE,(255,255,255),
                        SQUARE_RECT.left + board.square_width/2,
                        SQUARE_RECT.top + board.square_height/2,
                        center=True)

            # hidden/visible elements upon pause/finished game state
            if not self.game_halt:

                if SQUARE_RECT.collidepoint((self.control_input['mouse-x'], self.control_input['mouse-y'])):

                    # Hover -----------------------
                    if interacted_PColor == self.turn_attacker.name:
                        pygame.draw.rect(self.screen, LEGAL_MOV_HIGHLIGHT, SQUARE_RECT, width=2) # PIECE hover
                    else:
                        pygame.draw.rect(self.screen, EMPTY_SQUARE_HIGHLIGHT, SQUARE_RECT, width=2) # EMPTY hover
                    # Hover -----------------------
                
                    if self.control_input['click']:
                        self.selectedPiece_killMoves.clear()
                        self.selectedPiece_castlingMoves.clear()
                        self.selectedPiece_pawnDoubleMove.clear()

                        if SQUARE_SUBTYPE == "kill-movement":
                            self.killing = True
                            self.move_here = board_index

                        elif SQUARE_SUBTYPE == "valid-movement":
                            self.move_here = board_index
                        
                        elif SQUARE_SUBTYPE == "castling-movement":
                            self.castling = True
                            self.move_here = board_index
                        
                        elif SQUARE_SUBTYPE == "pawn-double-movement":
                            self.pawn_doubleMove = True
                            self.move_here = board_index

                        else: 
                            if SQUARE_TYPE == 'pawn':
                                self.selectedPiece_legalMoves.clear()
                                if interacted_PColor == self.turn_attacker.name:
                                    self.selectedPiece_legalMoves, self.selectedPiece_killMoves, self.selectedPiece_pawnDoubleMove = self.pawn_objectives(board_index, perspective='attacker')

                            if SQUARE_TYPE == 'rook':
                                self.selectedPiece_legalMoves.clear()
                                if interacted_PColor == self.turn_attacker.name:
                                    self.selectedPiece_legalMoves, self.selectedPiece_killMoves = self.rook_objectives(board_index, perspective='attacker')
                            
                            if SQUARE_TYPE == 'knight':
                                self.selectedPiece_legalMoves.clear()
                                if interacted_PColor == self.turn_attacker.name:
                                    self.selectedPiece_legalMoves, self.selectedPiece_killMoves = self.knight_objectives(board_index, perspective='attacker')
                        
                            if SQUARE_TYPE == 'bishop':
                                self.selectedPiece_legalMoves.clear()
                                if interacted_PColor == self.turn_attacker.name:
                                    self.selectedPiece_legalMoves, self.selectedPiece_killMoves = self.bishop_objectives(board_index, perspective='attacker')
                            
                            if SQUARE_TYPE == 'queen':
                                self.selectedPiece_legalMoves.clear()
                                if interacted_PColor == self.turn_attacker.name:
                                    self.selectedPiece_legalMoves, self.selectedPiece_killMoves = self.queen_objectives(board_index, perspective='attacker')

                            if SQUARE_TYPE == 'king':
                                self.selectedPiece_legalMoves.clear()
                                if interacted_PColor == self.turn_attacker.name:
                                    self.selectedPiece_legalMoves, self.selectedPiece_killMoves, self.selectedPiece_castlingMoves = self.king_objectives(board_index, perspective='attacker')
                                
                            if SQUARE_TYPE == "EMPTY":
                                self.selectedPiece_legalMoves.clear()

        # Pre-movements visual feedback
        if len(self.selectedPiece_legalMoves) > 1 or len(self.selectedPiece_killMoves) > 0: # avoids highlighting pieces with no actual movement
            for position_index in self.selectedPiece_legalMoves:
                pygame.draw.rect(self.screen, LEGAL_MOV_HIGHLIGHT, board.rects[position_index], width=2)

        for position_index in self.turn_defender.all_effectiveThreat_standpoints:
            pygame.draw.rect(self.screen, 'yellow', board.rects[position_index], width=2)

        for position_index in self.selectedPiece_killMoves:
            pygame.draw.rect(self.screen, LEGAL_KILL_HIGHLIGHT, board.rects[position_index], width=2)

        for position_index in self.selectedPiece_castlingMoves:
            pygame.draw.rect(self.screen, CASTLING_HIGHLIGHT, board.rects[position_index], width=2)
        
        for position_index in self.selectedPiece_pawnDoubleMove:
            pygame.draw.rect(self.screen, LEGAL_MOV_HIGHLIGHT, board.rects[position_index], width=2)
        
    def get_piece_standpoint(self, color:str, piece:str) -> list[int]:
        '''Argumentar pieza exactamente igual que en pieces.origins'''
        _actual_standpoints: list[int] = []
        if color == 'black':
            for k,v in self.black.positions.items():
                if v == piece:
                    _actual_standpoints.append(k)
        if color == 'white':
            for k,v in self.white.positions.items():
                if v == piece:
                    _actual_standpoints.append(k)
        return _actual_standpoints

    def decide_check(self):
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
        self.control_input['click'] = False # evita conflictos de click con el posible menu entrante
        if self.turn_attacker.direct_threatOrigin_type == 'none':
            if len(self.turn_attacker.positions) == 1 and len(self.turn_defender.positions) == 1:
                # Solo pueden ser los reyes, asi que es DRAW
                self.match_state = 'Draw.'
                self.stalemate = True

            if len(self.turn_defender.king_legal_moves) == 0 and len(self.turn_defender.legal_moves) == 0:

                #STALE-MATE
                if self.turn_attacker.name == 'black':
                    self.stalemate = True # repercute en render() - termina la partida
                    self.match_state = 'Stalemate.'

                if self.turn_attacker.name == 'white':
                    self.stalemate = True # repercute en render() - termina la partida
                    self.match_state = 'Stalemate.'

            else:
                self.match_state = ''
                return # La partida continúa con normalidad.

        if self.turn_attacker.direct_threatOrigin_type == 'single':
            if len(self.turn_defender.king_legal_moves) > 0 or len(self.turn_defender.legal_moves) > 0:
                # JAQUE

                # TURN DEBUG ++++++++++++++++++++++++++++++++++++++++++++++++++++++
                    # print('**JAQUE**')
                    # print('El rey defensor puede moverse en: ', defender.king_legal_moves);
                    # print('Las piezas aliadas del rey defensor pueden moverse: ', defender.legalMoves)
                    # print('**JAQUE**')
                # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                
                if self.turn_attacker.name == 'black':
                    self.match_state = 'White is in check.'

                if self.turn_attacker.name == 'white':
                    self.match_state = 'Black is in check.'

            elif len(self.turn_defender.king_legal_moves) == 0 and len(self.turn_defender.legal_moves) == 0:
                #JAQUE-MATE
                if self.turn_attacker.name == 'black':
                    self.winner = True # automaticamente repercutirá draw() 
                    self.match_state = 'Black wins.'
                if self.turn_attacker.name == 'white':
                    self.winner = True # automaticamente repercutirá draw()
                    self.match_state = 'White wins.'

        if self.turn_attacker.direct_threatOrigin_type == 'multiple': # múltiple origen de amenaza.
            if len(self.turn_defender.king_legal_moves) == 0:
                #JAQUE-MATE
                if self.turn_attacker.name == 'black':
                    self.winner = True # repercute en render() - termina la partida
                    self.match_state = 'Black wins.'

                if self.turn_attacker.name == 'white':
                    self.winner = True # repercute en render() - termina la partida
                    self.match_state = 'White wins.'
            else:
                # JAQUE
                '''Notificar al jugador correspondiente.'''
                if self.turn_attacker.name == 'black':
                    self.match_state = 'White is in check.'
                    
                if self.turn_attacker.name == 'white':
                    self.match_state = 'Black is in check.'

    def make_moves(self):
        # moving piece standpoint
        moving_piece_standpoint: int = self.selectedPiece_legalMoves[0]
        moving_piece: str = self.turn_attacker.positions.pop(moving_piece_standpoint)

        if self.killing:
            # NORMAL KILLING
            self.turn_defender.positions.pop(self.move_here)
            # castling disablers (killed rook)
            if self.move_here in self.turn_defender.castling_enablers.keys():
                del self.turn_defender.castling_enablers[self.move_here]
            # esto puede ser killing por en-passant, cuidado...

        # castling disablers (movement)
        if not self.castling:
            if moving_piece_standpoint in self.turn_attacker.castling_enablers.keys():
                if self.turn_attacker.castling_enablers[moving_piece_standpoint] == 'king': # es ex_value posición de rey?
                    self.turn_attacker.castling_enablers = {} # no more castling
                else:  # es ex_value posición de alguna torre?
                    del self.turn_attacker.castling_enablers[moving_piece_standpoint]
            
            # NORMAL MOVEMENT
            self.turn_attacker.positions.update({self.move_here: moving_piece})

        elif self.castling:
            self.turn_attacker.positions.update({self.move_here: moving_piece}) # mueve al rey
            ex_rook: int = {k for k,_ in self.turn_attacker.castling_enablers.items() if self.turn_attacker.castling_enablers[k] == f'{self.castling_direction}-rook'}.pop()
            self.turn_attacker.positions.pop(ex_rook)
            _direction: int = ESTE if self.castling_direction == 'east' else OESTE
            castling_rook_movement = moving_piece_standpoint+_direction # king_standpoint + dirección
            self.turn_attacker.positions.update({castling_rook_movement: 'rook'}) # mueve a la torre
            self.turn_attacker.castling_enablers = {} # no more castling
        
        # en-passant
        if self.pawn_doubleMove:

            # objective kill position
            offset_position: int = SUR if self.turn_attacker.name == 'white' else NORTE

            if self.move_here+ESTE in self.turn_defender.positions:
                if self.turn_defender.positions[self.move_here+ESTE] == 'pawn':
                    #ENABLE EN-PASSANT
                    self.turn_attacker.enPassant_enablers.update({'true-pos':self.move_here})
                    self.turn_attacker.enPassant_enablers.update({'offset-kill-pos':moving_piece_standpoint+offset_position})
            if self.move_here+OESTE in self.turn_defender.positions:
                if self.turn_defender.positions[self.move_here+OESTE] == 'pawn':
                    #ENABLE EN-PASSANT
                    self.turn_attacker.enPassant_enablers.update({'true-pos':self.move_here})
                    self.turn_attacker.enPassant_enablers.update({'offset-kill-pos':moving_piece_standpoint+offset_position})
        else: self.turn_attacker.enPassant_enablers.clear() # deshabilitado en sig. turno
        
        self.selectedPiece_legalMoves.clear()
        self.selectedPiece_castlingMoves.clear()
        self.selectedPiece_pawnDoubleMove.clear()
        self.move_here = None
        self.killing = False
        self.castling = False
        self.castling_direction = ''
        self.pawn_doubleMove = False 

    def match_clock(self):

        if not self.pause and not self.game_halt:
            self.pausetime_SNAP = 0
            
            if self.turn_attacker.name == 'white':
                self.whitetime_SNAP += self.pause_time_leftover
                if pygame.time.get_ticks() - self.whitetime_SNAP >= 1000:
                    self.white_time_leftover = pygame.time.get_ticks() - self.whitetime_SNAP - 1000
                    # self.whitetime_SNAP += 1000 - self.white_time_leftover
                    self.whitetime_SNAP = pygame.time.get_ticks() - self.white_time_leftover
                    self.substract_time(color='white')
                else:
                    self.white_time_leftover = pygame.time.get_ticks() - self.whitetime_SNAP
                
                # out of time - white lose
                if self.white_turn_time == 0:
                    self.winner = True
                    self.match_state = 'Black wins.'
            
            if self.turn_attacker.name == 'black':
                self.blacktime_SNAP += self.pause_time_leftover
                if pygame.time.get_ticks() - self.blacktime_SNAP > 1000: 
                    self.black_time_leftover = pygame.time.get_ticks() - self.blacktime_SNAP - 1000
                    # self.blacktime_SNAP += 1000 - self.black_time_leftover
                    self.blacktime_SNAP = pygame.time.get_ticks() - self.black_time_leftover
                    self.substract_time(color='black')
                else:
                    self.black_time_leftover = pygame.time.get_ticks() - self.blacktime_SNAP
                
                # out of time - black lose
                if self.black_turn_time == 0:
                    self.winner = True
                    self.match_state = 'White wins.'

            self.pause_time_leftover = 0
        elif self.pause or self.player_deciding_promotion:
            #pause_time++
            if self.pausetime_SNAP == 0:
                self.pausetime_SNAP = pygame.time.get_ticks()
            else:
                self.pause_time_leftover = pygame.time.get_ticks() - self.pausetime_SNAP
        
    def substract_time(self, color):
        '''Restamos un segundo en el reloj correspondiente.
        Al ser llamada esta función ya detectamos el paso de un segundo,
        debemos entonces disminuir en 1 tanto turn_time como turn_seconds.

        Si turn_seconds nos da -1 reemplazamos por '59'
        Si turn_seconds/minutes tienen longitud de 1 dígito, añadir un 0
        al principio de la cadena.
        Tanto seconds como minutes SON STRINGS FINALMENTE.
        '''
        if color == 'black':
            self.black_turn_time-=1
            minutes = int(self.black_turn_time/60)
            self.black_turn_minutes = str(minutes) if len(str(minutes)) > 1 else ' '+str(minutes)
            seconds = int(self.black_turn_seconds) - 1
            if seconds == -1:
                self.black_turn_seconds = '59'
            else: self.black_turn_seconds = str(seconds) if len(str(seconds)) > 1 else '0'+str(seconds)

        if color == 'white':
            self.white_turn_time-=1
            minutes = int(self.white_turn_time/60)
            self.white_turn_minutes = str(minutes) if len(str(minutes)) > 1 else ' '+str(minutes)
            seconds = int(self.white_turn_seconds) - 1
            if seconds == -1:
                self.white_turn_seconds = '59'
            else: self.white_turn_seconds = str(seconds) if len(str(seconds)) > 1 else '0'+str(seconds)

    def match_state_info(self):
        self.draw_text(self.match_state, 'black', board.x, 20, center=False)

    def clock_display(self):
        
        # black team clock
        if self.turn_attacker.name == 'black':
            self.draw_text(
                f'{self.black_turn_minutes}:{self.black_turn_seconds}',
                (0,200,0), self.mid_screen.x , board.y-20, center=True)
        else:
            self.draw_text(
                f'{self.black_turn_minutes}:{self.black_turn_seconds}',
                'black', self.mid_screen.x , board.y-20, center=True)

        # white team clock
        if self.turn_attacker.name == 'white':
            self.draw_text(
                f'{self.white_turn_minutes}:{self.white_turn_seconds}',
                (0,200,0), self.mid_screen.x, board.height+70, center=True)
        else:
            self.draw_text(
                f'{self.white_turn_minutes}:{self.white_turn_seconds}',
                'black', self.mid_screen.x, board.height+70, center=True)

    def render(self):

        if self.control_input['escape']:
            if not self.showing_closingCurtain:
                self.menu_handler()

        # HUD
        self.match_state_info()
        self.clock_display()
        self.menu_toggle_btn()

        # Core logic
        self.draw_board()
        self.match_clock()
        if self.move_here != None:
            self.make_moves()
            self.check_pawn_promotion()
        if self.finish_turn:
            self.update_turn_objectives()
            self.decide_check()
            self.turn_swap()
            self.finish_turn = False
        
        # Menus
        # match opening ------------------------------------------------------
        if self.player_selecting_gameClockLimit: # menú no removible con ESC
            self.game_halt = True
            self.screen.blit(self.curtain, (0,0))    
            self.draw_starting_time_selection_menu()
        
        if not self.player_selecting_gameClockLimit and self.showing_openingCurtain:
            self.curtain_transparency -= 3
            if self.curtain_transparency > 0:
                self.curtain.fill((255,255,255,self.curtain_transparency))
                self.screen.blit(self.curtain, (0,0))
            if self.curtain_transparency <= 0:
                self.showing_openingCurtain = False
        # --------------------------------------------------------------------

        if self.pause: # menú switcheable con ESC
            self.game_halt = True
            if not self.player_deciding_match:
                self.draw_pause_menu()
            else:
                self.draw_confirm_restart_menu()
        
        if self.winner or self.stalemate: # menú switcheable con ESC
            if self.show_switchable_menu:
                self.game_halt = True
                if not self.player_deciding_match:
                    self.draw_post_game_menu()
                else:
                    self.draw_confirm_restart_menu()

        if self.player_deciding_promotion: # menú switcheable con ESC
            if self.show_switchable_menu:
                self.game_halt = True
                self.draw_pawnPromotion_selection_menu()
        
        # match closing ------------------------------------------------------
        if self.match_restarting:
            self.show_switchable_menu = False
            self.pause = False
            self.showing_closingCurtain = True
            self.game_halt = True
            self.curtain_transparency += 3
            if self.curtain_transparency > 255:
                self.screen.blit(self.curtain, (0,0))
                self.set_content()
            else:
                self.curtain.fill((255,255,255,self.curtain_transparency))
                self.screen.blit(self.curtain, (0,0))
        # --------------------------------------------------------------------
        
        # clock/game_halt release
        if not self.pause and not self.winner:
            if not self.stalemate and not self.player_deciding_promotion:
                if not self.player_selecting_gameClockLimit and not self.showing_openingCurtain:
                    if not self.showing_closingCurtain:
                        self.game_halt = False

        # control release
        self.control_input['escape'] = False
        self.control_input['click'] = False
    
    def menu_handler(self):
        if not self.player_selecting_gameClockLimit and not self.player_deciding_promotion:
            if not self.player_deciding_match:
                if not self.winner or self.stalemate:
                    self.pause = not self.pause
        if self.player_deciding_promotion:
            # hide/show menu
            self.show_switchable_menu = not self.show_switchable_menu
        if self.winner or self.stalemate:
            # hide/show menu
            self.show_switchable_menu = not self.show_switchable_menu
        if self.player_deciding_match:
            self.player_deciding_match = False
            self.pause = False
    
    def menu_toggle_btn(self):
        x = self.mid_screen.x + board.width/2 - 73
        y = board.y-30
        btn_rect = pygame.Rect(x-16, y-15, 89, 45)
        if btn_rect.collidepoint((self.control_input['mouse-x'], self.control_input['mouse-y'])):
            # hover
            pygame.draw.rect(self.screen, GRAY_BTN_HOVER, btn_rect)
            # action
            if self.control_input['click']:
                if not self.showing_closingCurtain:
                    self.menu_handler()
        self.draw_text('Menu',
            'black',x, y, center=False)
            
    # Confirm restart (pause menu children) ----------------------------------------------------------------
    def draw_confirm_restart_menu(self, width=430, height=170):
        x = self.mid_screen.x - width/2
        y = self.mid_screen.y - height/2 
        # frame
        pygame.draw.rect(self.screen, (100,100,100),
                        pygame.Rect(x, y, width, height))
        # tooltip
        self.draw_text('¿Are you sure you want to restart the game?',
            'white',self.mid_screen.x, y+15, x_center=True)
        self.draw_confirm_match_restart_btn(y)
        self.draw_cancel_restart_btn(y)
        
    def draw_confirm_match_restart_btn(self, y):
        x = self.mid_screen.x
        y += 60
        text_color = 'white'
        confirm_match_rect = pygame.Rect(x-430/2, y-15, 430, 50)
        if confirm_match_rect.collidepoint((self.control_input['mouse-x'], self.control_input['mouse-y'])):
            # hover
            pygame.draw.rect(self.screen, GRAY_BTN_HOVER, confirm_match_rect)
            text_color = 'black'
            # action
            if self.control_input['click']:
                self.match_restarting = True
        self.draw_text('Yes', text_color, x, y, x_center=True)

    def draw_cancel_restart_btn(self, y):
        x = self.mid_screen.x
        y += 120
        text_color = 'white'
        cancel_match_rect = pygame.Rect(x-430/2, y-15, 430, 50)
        if cancel_match_rect.collidepoint((self.control_input['mouse-x'],self.control_input['mouse-y'])):
            #hover
            pygame.draw.rect(self.screen, GRAY_BTN_HOVER, cancel_match_rect)
            text_color = 'black'
            # action
            if self.control_input['click']:
                self.player_deciding_match = False
        self.draw_text('No', text_color, x, y, x_center=True)
    # ------------------------------------------------------------------------------------------------------

    # Pause menu ---------------------------------------------------------------------------------------------
    def draw_pause_menu(self, width=300, height=230):
        x = self.mid_screen.x - width/2
        y = self.mid_screen.y - height/2
        # frame
        pygame.draw.rect(self.screen,(100,100,100),
                        pygame.Rect(x, y, width, height))
        # tooltip
        self.draw_text('Paused','white', self.mid_screen.x, y+15, x_center=True)
        # buttons
        self.draw_continue_btn(y)
        self.draw_play_again_btn(y)
        self.draw_exit_game_btn(y)

    def draw_continue_btn(self, y):
        x = self.mid_screen.x
        y += 60
        text_color = 'white'
        continue_match_rect = pygame.Rect(x-300/2, y-15, 300, 50)
        if continue_match_rect.collidepoint((self.control_input['mouse-x'], self.control_input['mouse-y'])):
            # hover
            pygame.draw.rect(self.screen, GRAY_BTN_HOVER, continue_match_rect)
            text_color = 'black'
            # action
            if self.control_input['click']:
                self.pause = False
        self.draw_text('Continue', text_color, x, y, x_center=True)

    def draw_play_again_btn(self, y):
        x = self.mid_screen.x
        y += 120
        text_color = 'white'
        play_again_rect = pygame.Rect(x-300/2, y-15, 300, 50)
        if play_again_rect.collidepoint((self.control_input['mouse-x'], self.control_input['mouse-y'])):
            # hover
            pygame.draw.rect(self.screen, GRAY_BTN_HOVER, play_again_rect)
            text_color = 'black'
            # action
            if self.control_input['click']:
                self.player_deciding_match = True
        self.draw_text('Play again', text_color, x, y, x_center=True)

    def draw_exit_game_btn(self, y):
        x = self.mid_screen.x
        y += 180
        text_color = 'white'
        exit_game_rect = pygame.Rect(x-300/2, y-15, 300, 50)
        if exit_game_rect.collidepoint((self.control_input['mouse-x'], self.control_input['mouse-y'])):
            # hover
            pygame.draw.rect(self.screen, GRAY_BTN_HOVER, exit_game_rect)
            text_color = 'black'
            # action
            if self.control_input['click']:
                self.running = False
        self.draw_text('Exit game', text_color, x, y, x_center=True)
    # --------------------------------------------------------------------------------------------------------

    # Post game menu -----------------------------------------------------------------------------------------
    def draw_post_game_menu(self, width=300, height=170):
        x = self.mid_screen.x - width/2
        y = self.mid_screen.y - height/2 
        # frame
        pygame.draw.rect(self.screen,(100,100,100),
                        pygame.Rect(x, y, width, height))
        # tooltip
        self.draw_text('Game over', 'white', self.mid_screen.x, y+15, x_center=True)
        self.draw_show_board_btn(y)
        self.draw_postgame_again_btn(y)

    def draw_show_board_btn(self, y):
        x = self.mid_screen.x
        y += 60
        text_color = 'white'
        btn_rect = pygame.Rect(x-300/2, y-15, 300, 50)
        if btn_rect.collidepoint((self.control_input['mouse-x'], self.control_input['mouse-y'])):
            # hover
            pygame.draw.rect(self.screen, GRAY_BTN_HOVER, btn_rect)
            text_color = 'black'
            # action
            if self.control_input['click']:
                self.show_switchable_menu = False
        self.draw_text('Hide menu', text_color, x, y, x_center=True)

    def draw_postgame_again_btn(self, y):
        x = self.mid_screen.x
        y += 120
        text_color = 'white'
        play_again_rect = pygame.Rect(x-300/2, y-15, 300, 50)
        if play_again_rect.collidepoint((self.control_input['mouse-x'], self.control_input['mouse-y'])):
            # hover
            pygame.draw.rect(self.screen, GRAY_BTN_HOVER, play_again_rect)
            text_color = 'black'
            # action
            if self.control_input['click']:
                self.match_restarting = True
        self.draw_text('Play again', text_color, x, y, x_center=True)
    # --------------------------------------------------------------------------------------------------------

    # Pawn promotion menu ------------------------------------------------------------------------------------
    def draw_pawnPromotion_selection_menu(self, width=300, height=290):
        x = self.mid_screen.x - width/2
        y = self.mid_screen.y - height/2  
        # frame
        pygame.draw.rect(self.screen, (100,100,100),
                        pygame.Rect(x, y, width, height))
        # tooltip
        self.draw_text('Choose pawn promotion', 'white', self.mid_screen.x, y+15, x_center=True)
        self.draw_rookOPT_btn(y)
        self.draw_knightOPT_btn(y)
        self.draw_queenOPT_btn(y)
        self.draw_bishopOPT_btn(y)

    def draw_rookOPT_btn(self, y):
        x = self.mid_screen.x
        y += 60
        text_color = 'white'
        selection_rect = pygame.Rect(x-300/2, y-15, 300, 50)
        if selection_rect.collidepoint((self.control_input['mouse-x'], self.control_input['mouse-y'])):
            # hover
            pygame.draw.rect(self.screen, GRAY_BTN_HOVER, selection_rect)
            text_color = 'black'
            # action
            if self.control_input['click']:
                self.player_deciding_promotion = False
                self.make_promotion('rook')
        self.draw_text('Rook', text_color, x, y, x_center=True)

    def draw_knightOPT_btn(self, y):
        x = self.mid_screen.x
        y += 120
        text_color = 'white'
        selection_rect = pygame.Rect(x-300/2, y-15, 300, 50)
        if selection_rect.collidepoint((self.control_input['mouse-x'], self.control_input['mouse-y'])):
            # hover
            pygame.draw.rect(self.screen, GRAY_BTN_HOVER, selection_rect)
            text_color = 'black'
            # action
            if self.control_input['click']:
                self.player_deciding_promotion = False
                self.make_promotion('knight')
        self.draw_text('Knight', text_color, x, y, x_center=True)

    def draw_bishopOPT_btn(self, y):
        x = self.mid_screen.x
        y += 180
        text_color = 'white'
        selection_rect = pygame.Rect(x-300/2, y-15, 300, 50)
        if selection_rect.collidepoint((self.control_input['mouse-x'], self.control_input['mouse-y'])):
            # hover
            pygame.draw.rect(self.screen, GRAY_BTN_HOVER, selection_rect)
            text_color = 'black'
            # action
            if self.control_input['click']:
                self.player_deciding_promotion = False
                self.make_promotion('bishop')
        self.draw_text('Bishop', text_color, x, y, x_center=True)

    def draw_queenOPT_btn(self, y):
        x = self.mid_screen.x
        y += 240
        text_color = 'white'
        selection_rect = pygame.Rect(x-300/2, y-15, 300, 50)
        if selection_rect.collidepoint((self.control_input['mouse-x'], self.control_input['mouse-y'])):
            # hover
            pygame.draw.rect(self.screen, GRAY_BTN_HOVER, selection_rect)
            text_color = 'black'
            # action
            if self.control_input['click']:
                self.player_deciding_promotion = False
                self.make_promotion('queen')
        self.draw_text('Queen', text_color, x, y, x_center=True)
    # --------------------------------------------------------------------------------------------------------

    # Time selection Menu ------------------------------------------------------------------------------------
    def draw_starting_time_selection_menu(self, width=300, height=350):
        x = self.mid_screen.x - width/2
        y = self.mid_screen.y - height/2
        # frame
        pygame.draw.rect(self.screen, (100,100,100),
                        pygame.Rect(x, y, width, height))
        # tooltip
        self.draw_text('Select clock limit', 'white', self.mid_screen.x, y+15, x_center=True)
        # buttons
        self.draw_oneMinOPT_btn(y)
        self.draw_threeMinOPT_btn(y)
        self.draw_fiveMinOPT_btn(y)
        self.draw_tenMinOPT_btn(y)
        self.draw_fifteenMinOPN_btn(y)
    
    def draw_oneMinOPT_btn(self, y):
        x = self.mid_screen.x
        y += 60
        text_color = 'white'
        selection_rect = pygame.Rect(x-300/2, y-15, 300, 50)
        if selection_rect.collidepoint((self.control_input['mouse-x'], self.control_input['mouse-y'])):
            # hover
            pygame.draw.rect(self.screen, GRAY_BTN_HOVER, selection_rect)
            text_color = 'black'
            # action
            if self.control_input['click']:
                self.set_turn_clocks(1)
                self.player_selecting_gameClockLimit = False
        self.draw_text('1 min', text_color, x, y, x_center=True)

    def draw_threeMinOPT_btn(self, y):
        x = self.mid_screen.x
        y += 120
        text_color = 'white'
        selection_rect = pygame.Rect(x-300/2, y-15, 300, 50)
        if selection_rect.collidepoint((self.control_input['mouse-x'], self.control_input['mouse-y'])):
            # hover
            pygame.draw.rect(self.screen, GRAY_BTN_HOVER, selection_rect)
            text_color = 'black'
            # action
            if self.control_input['click']:
                self.set_turn_clocks(3)
                self.player_selecting_gameClockLimit = False
        self.draw_text('3 mins', text_color, x, y, x_center=True)

    def draw_fiveMinOPT_btn(self, y):
        x = self.mid_screen.x
        y += 180
        text_color = 'white'
        selection_rect = pygame.Rect(x-300/2, y-15, 300, 50)
        if selection_rect.collidepoint((self.control_input['mouse-x'], self.control_input['mouse-y'])):
            # hover
            pygame.draw.rect(self.screen, GRAY_BTN_HOVER, selection_rect)
            text_color = 'black'
            # action
            if self.control_input['click']:
                self.set_turn_clocks(5)
                self.player_selecting_gameClockLimit = False
        self.draw_text('5 mins', text_color, x, y, x_center=True)

    def draw_tenMinOPT_btn(self, y):
        x = self.mid_screen.x
        y += 240
        text_color = 'white'
        selection_rect = pygame.Rect(x-300/2, y-15, 300, 50)
        if selection_rect.collidepoint((self.control_input['mouse-x'], self.control_input['mouse-y'])):
            # hover
            pygame.draw.rect(self.screen, GRAY_BTN_HOVER, selection_rect)
            text_color = 'black'
            # action
            if self.control_input['click']:
                self.set_turn_clocks(10)
                self.player_selecting_gameClockLimit = False
        self.draw_text('10 mins', text_color, x, y, x_center=True)

    def draw_fifteenMinOPN_btn(self, y):
        x = self.mid_screen.x
        y += 300
        text_color = 'white'
        selection_rect = pygame.Rect(x-300/2, y-15, 300, 50)
        if selection_rect.collidepoint((self.control_input['mouse-x'], self.control_input['mouse-y'])):
            # hover
            pygame.draw.rect(self.screen, GRAY_BTN_HOVER, selection_rect)
            text_color = 'black'
            # action
            if self.control_input['click']:
                self.set_turn_clocks(15)
                self.player_selecting_gameClockLimit = False
        self.draw_text('15 mins', text_color, x, y, x_center=True)
    # --------------------------------------------------------------------------------------------------------
