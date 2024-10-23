import pygame
import font
import board
import pieces
from board import NORTE, NOR_ESTE, NOR_OESTE, SUR, SUR_OESTE, SUR_ESTE, ESTE, OESTE # piece directions
from board import row_of_

class Scene:
    '''Deberíamos abstraer mas a los draws, quizás haciendo por ej. una clase 
    que herede de Scene llamada MainMenuDrawer, y MainMenu hereda de MainMenuDrawer?

    >>Draw está estrechamente relacionado con MASTER.
    Los draws nos indican uso de fuentes, de posiciones en la pantalla (ui related), 
    uso de rectángulos, escucha a clicks y modificaciones de variables.
    Tienen gran relación con el *screen actual* y los controles presionados.

    El objetivo es que el contenido de la "Escena final" sea la lógica mas neta posible del juego.
    Un mixer de todos los elementos necesarios para dicha escena, como board+pieces,
    sin que los mecanismos draw "choquen tanto" con estos. Un poco más prolijo nomá.
    '''
    def __init__(self,master): # paso master o paso LO QUE NECESITO de master?
        self.master = master # interfaz para comunicar variables y controles
        self.screen = self.master.screen

        # screen position utils
        self.midScreen = (self.screen.get_width()/2, self.screen.get_height()/2)
        self.midScreen_pos = pygame.Vector2(self.midScreen)

    def draw_text(self,text,color,x,y,center=True,font_size='large'):
        _font = font.large_font if font_size=='large' else font.medium_font
        surface = self.master.screen
        textobj = _font.render(text,1,color)
        text_width = textobj.get_width()
        text_height = textobj.get_height()
        textrect = textobj.get_rect()
        if center: textrect.topleft = (x - text_width/2, y - text_height/2) # anchors placement at center
        else: textrect.topleft = (x,y)
        surface.blit(textobj,textrect)

class MainMenu(Scene):
    '''> Escena MAIN_MENU

    Comienza con una pequeña animación
        imagen se mueve, frena repentinamente y se le pide 
        al jugador que presione una tecla cualquiera para 
        iniciar todo el resto.
            Esto tiene realmente una utilidad?
    >>Animaciones de transición de escenas<<

    +) contiene:
        botón nueva partida
                j1 vs j2 | j1 vs IA
                    modos de tiempo, modos de dificultad
                    >> al clickear el último boton llamaremos a self.make_mode()

        botón reglas
                reglas del juego...?

        botón opciones
                resolución
                    400x800
                    600x800
                    1280x920
                audio
                    Volumen
        botón salir

        Aguardará una señal de comenzar partida.
        Esta señal contiene un dict de instrucciones
        para la escena Match
    '''

    def __init__(self,master):
        super().__init__(master)
        self.view = 'main'
        self._match_modes: dict = {}
    
    def update_game_variables(self):
        '''Escena Match debe inicializarse consumiendo variables de juego,
        como modo, colores de jugador, activación de tiempo, reglas etc.

        Posibles modos = J1-VS-J2, J1-VS-IA
        J1_color posibles = blancas, negras
        J2_color posibles = blancas, negras
        IA_color posibles = blancas, negras
        tiempo posible: activado / desactivado
        otras reglas: ...
        ______________________________________
        ^
        ^ - - Decididos en la GUI

        Desde aquí (MainMenu) prepararemos toda la información en un dict que deberá
        pasarse a Match.

        Ejemplo final_dict:
        - modo: 1 jugador
        - j1_color: blancas
        - je_color: negras
        - tiempo: desactivado
        '''
        # match_modes: dict
        set_player_colors = ...#player choice over menu focus
        mode: str
        time_activated: bool
        #if time_activated:...
        #match_modes.update(selected_from_gui) ...
        self.master.game_variables.update(self._match_modes)

    def draw_newMatch_btn(self):
        self.draw_text('Nueva partida','white',50,100,center=False)
        new_match_rect = pygame.Rect(50,100,200,50)
        if new_match_rect.collidepoint((self.master.mx,self.master.my)):
            # hover
            pygame.draw.rect(self.master.screen,(255,0,0),new_match_rect,width=1)
            if self.master.click:
                #preguntar modo -> J1-vs-J2 | J1-vs-IA
                self.view = 'mode-selection'
                self.master.click = False
    
    def draw_exit_btn(self):
        self.draw_text('Salir','white',50,200,center=False)
        exit_btn = pygame.Rect(50,200,200,50)
        if exit_btn.collidepoint((self.master.mx,self.master.my)):
            # hover
            pygame.draw.rect(self.master.screen,(255,0,0),exit_btn,width=1)
            if self.master.click:
                self.master.scene_manager = 'exit'

    def draw_match_modes(self):
        self.draw_text('Elija un modo:','white',50,100,center=False)

        # J1 VS J2 MODE
        self.draw_text('J1 vs J2','white',50,150,center=False)
        j1_vs_j2_rect = pygame.Rect(50,130,200,50)
        if j1_vs_j2_rect.collidepoint((self.master.mx,self.master.my)):
            #hover
            pygame.draw.rect(self.master.screen,(255,0,0),j1_vs_j2_rect,width=1)
            if self.master.click: #function_call() master.make_mode?
                
                self._match_modes.update({'mode':'j1-vs-j2'})
                self.update_game_variables()
                self.master.scene_manager = Match

        # J1 VS IA MODE
        self.draw_text('J1 vs IA','white',50,200,center=False)
        j1_vs_ia_rect = pygame.Rect(50,200,200,50)
        if j1_vs_ia_rect.collidepoint((self.master.mx,self.master.my)):
            # hover
            pygame.draw.rect(self.master.screen,(255,0,0),j1_vs_ia_rect,width=1)
            if self.master.click:
                
                self._match_modes.update({'mode':'j1-vs-ia'})
                self.update_game_variables()
                self.master.scene_manager = Match

    def render(self):
        #hud
        self.draw_text('Main menu scene','white',20,20,center=False)
        if self.view == 'main':
            self.draw_newMatch_btn()
            self.draw_exit_btn()
        if self.view == 'mode-selection':
            self.draw_match_modes()
        #if view == 'options':
            #MainMenuSCENE.draw_options()

class Match(Scene):
    '''> Escena JUEGO
    Es inicializada bajo una 'comanda' por el modo j1-VS-j2 o j1-VS-ia seleccionado en el
    menú previo
    +) contiene:
        2 actores
            cada actor tiene un color y cada color
            corresponde a un color y un lado del tablero'''

    def __init__(self, master):
        super().__init__(master)

        # judge variables
        self.match_mode: dict = self.master.game_variables
        self.move_here: int | None = None
        self.winner: bool = False
        self.stalemate: bool = False # Ahogado | draw
        self.match_state: str = '' # HUD info
        self.player_deciding_match = False
        self.killing: bool = False

        # board config
        self.board_begin = pygame.Vector2(
            (self.midScreen_pos.x - board.width/2,
            self.midScreen_pos.y - board.height/2))
        self.boardRects: list[pygame.Rect] = board.make_rects(self.board_begin)
        
        # board feedback utilities
        self.pieceValidMovement_posDisplay: dict[int, pygame.Rect] = {}
        self.pieceValidKill_posDisplay: dict[int, pygame.Rect] = {} 

        # Board defaults ---------------------------------------------------
        # Black
        self.black_positions: dict[int, str] = pieces.black_positions
        self.in_base_Bpawns: list[int] = [bpawn for bpawn in pieces.origins['negras']['Peón']]
        self.black_threatOnWhite: dict[str, int] = {piece:[] for piece in pieces.origins['negras']} # {'peon': [1,2,3], 'alfil': [4,5,6]}
        self.black_kingLegalMoves: list[int] = []
        # White
        self.white_positions: dict[int, str] = pieces.white_positions
        self.in_base_Wpawns: list[int] = [wpawn for wpawn in pieces.origins['blancas']['Peón']]
        self.white_threatOnBlack: dict[str, int] = {piece:[] for piece in pieces.origins['blancas']} # {'peon': [1,2,3], 'alfil': [4,5,6]}
        self.white_kingLegalMoves: list[int] = []

        # Turn lookups ---------------------------------------------------
        self.turn_attacker: str = 'White'
        self.turn_defender: str = 'Black'

        '''Registro de AMENAZAS y MOVIMIENTOS LEGALES DEL REY: 

        >> Threat-on-black/white - PRE-movements
            kill-movement's *del enemigo* que caen en casillero rey TARGET o adyacencias legales.
            Restringen movements y kill-movements de *TARGET*.
            Puede ser DIRECTO o INDIRECTO.
            Deben ser revisados ANTES DE intentar un movimiento.
            Sirven para saber: Donde NO puede moverse el rey.
                               Si el rey está en jaque/jaque-mate.
            Si estos casilleros son iguales a los posibles movimientos del rey
            Y
            Ninguna pieza *aliada* puede MATAR o BLOQUEAR *TODAS* las amenazas = JAQUE MATE
            (Puede que haya un actual-threat y un future-threat)

            El threat puede MATARSE o BLOQUEARSE, depende de qué pieza esté haciendo
            threat.
            Threat de bishop, queen y tower pueden bloquearse
            Threat de pawn y horse no pueden bloquearse

        >> Color-King-legalMovements
            Posición actual + posibles movimientos.
            Que su standpoint esté en threat o no significa dos situaciones distintas.

        TODOS Los conjuntos THREAT y COLOR-KING-LEGALMOVES se actualizarán en la función 
        update_turn_objectives() luego de mover una pieza. 
        '''
        self.defender_positions: dict[int, str] = self.black_positions #22/10 NO ESTA HECHO EL SWAP
        self.defender_threatOnAttacker: dict[str, int] = self.black_threatOnWhite
        self.defender_kingLegalMoves: list[int] = self.black_kingLegalMoves
        self.attacker_positions: dict[int, str] = self.white_positions #22/10 NO ESTA HECHO EL SWAP
        self.attacker_threatOnDefender: dict[str, int] = self.white_threatOnBlack
        self.attacker_kingLegalMoves: list[int] = self.white_kingLegalMoves
        self.update_turn_objectives() 

    def update_turn_objectives(self):
        '''Actualizando conjuntos threatOn y kingLegalMoves para
        TODOS los equipos'''
        
        # Defender
        '''BUG estamos levantando internamente casillas del rey TURN ATTACKER, necesitamos que sea del TURN TARGET'''
        king_standpoint: int = self.get_piece_standpoint(color=self.turn_defender,piece="Rey").pop()
        self.king_objectives(king_standpoint)

        # Attacker
        pawn_standpoints: list[int] = self.get_piece_standpoint(color=self.turn_attacker,piece="Peón")
        for _pawn in pawn_standpoints:
            self.pawn_objectives(_pawn)

        tower_standpoints: list[int] = self.get_piece_standpoint(color=self.turn_attacker,piece="Torre")
        for _tower in tower_standpoints:
            self.tower_objectives(_tower)

        bishop_standpoints: list[int] = self.get_piece_standpoint(color=self.turn_attacker,piece="Alfil")
        for _bishop in bishop_standpoints:
            self.bishop_objectives(_bishop)

        horse_standpoints: list[int] = self.get_piece_standpoint(color=self.turn_attacker,piece="Caballo")
        for _horse in horse_standpoints:
            self.horse_objectives(_horse)

        queen_standpoint: int = self.get_piece_standpoint(color=self.turn_attacker,piece="Reina").pop()
        self.queen_objectives(queen_standpoint)

    def reset_board(self):
        self.in_base_Bpawns = [bpawn for bpawn in pieces.origins['negras']['Peón']]
        self.in_base_Wpawns = [wpawn for wpawn in pieces.origins['blancas']['Peón']]
        self.black_positions = pieces.black_positions
        self.white_positions = pieces.white_positions
        self.turn_attacker = 'White'
        self.winner = False

    def turn_swap(self):
        if self.turn_attacker == 'White':
            self.turn_attacker = 'Black'
            self.turn_defender = 'White'
            #1ro transfiero targets
            #...
            #luego intercambio targets lists
            #...
            return
        if self.turn_attacker == 'Black':
            self.turn_attacker = 'White'
            self.turn_defender = 'Black'
            #1ro transfiero targets
            #...
            #luego intercambio targets lists
            #...
            return
    
    def pawn_objectives(self,piece_standpoint: int) -> dict[int,pygame.Rect]:
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
        mov_target_positions: dict[int,pygame.Rect] = {piece_standpoint:self.boardRects[piece_standpoint]} # standpoint is always first pos 
        on_target_kill_positions: dict[int,pygame.Rect] = {}
        
        # Objectives
        _single_origin_threat: bool | None = None
        _threat_origin_pos: int | None = None
        _blocking_threat: bool = False
        kill_positions: list[int] = []

        if self.turn_defender == 'White':
            # SUR
            movement: int = piece_standpoint+SUR

            # piece block condition
            if movement <= 63: # SUR LIMIT

                # Attacker piece blocking Defender direct threat case lookup
                for threat_pos_list in self.defender_threatOnAttacker.values():
                    for _pos in threat_pos_list:
                        if piece_standpoint == _pos:
                            _blocking_threat = True
                        if self.attacker_positions[_pos] == 'Rey' and _blocking_threat:
                            # La pieza está bloqueando un threat directo al rey
                            _single_origin_threat = True
                            # Aún puedo matar la amenaza.
                            # El orígen de la amenaza es el mínimo o máximo de
                            # la lista de posiciones-amenaza.
                            if movement == max(threat_pos_list):
                                _threat_origin_pos = max(threat_pos_list)
                            elif movement == min(threat_pos_list): 
                                _threat_origin_pos = min(threat_pos_list)
                            continue #skip to next iteration
                        # PERO si hay MAS DE UN origen de amenaza DIRECTA,
                        # invalidar todos los objetivos.
                        # (ninguna pieza puede eliminar dos o más orígenes de amenaza).
                        if self.attacker_positions[_pos] == 'Rey' and _single_origin_threat:
                            _single_origin_threat == False
                            return {}, {}
                # sino, devolver la única opcion de movimiento posible (matar amenaza)
                if _single_origin_threat and _threat_origin_pos != None:
                    on_target_kill_positions.update({_threat_origin_pos:self.boardRects[_threat_origin_pos]})
                    return mov_target_positions, on_target_kill_positions
                # ------------------------------------------------

                # Movement
                if movement not in self.black_positions and movement not in self.white_positions:
                    if piece_standpoint in self.in_base_Bpawns:
                        mov_target_positions.update({movement:self.boardRects[movement]})

                        # 2nd piece block condition
                        if movement+SUR <= 63: #board limit check

                            # Movement
                            if movement+SUR not in self.black_positions and movement+SUR not in self.white_positions:
                                mov_target_positions.update({movement+SUR:self.boardRects[movement+SUR]})
                    else:
                        mov_target_positions.update({movement:self.boardRects[movement]})

            # kill positions
            # Verificamos que el movimiento no rompa los límites del tablero
            if piece_standpoint+OESTE not in row_of_(piece_standpoint):
                kill_positions.append(piece_standpoint+SUR_ESTE)
            if piece_standpoint+ESTE not in row_of_(piece_standpoint):
                kill_positions.append(piece_standpoint+SUR_OESTE)
            elif len(kill_positions) == 0:
                kill_positions.extend([piece_standpoint+SUR_OESTE, piece_standpoint+SUR_ESTE])

            for kp in kill_positions:
                if kp in self.white_positions:
                    on_target_kill_positions.update({kp:self.boardRects[kp]})
                
                # King checks ------------------------------------
                if kp in self.defender_kingLegalMoves:
                    self.attacker_threatOnDefender['Peón'].append(kp)
                # ------------------------------------------------

        if self.turn_defender == 'Black': 
            # NORTE
            movement: int = piece_standpoint+NORTE
            # piece block condition
            if movement >= 0: # NORTE LIMIT

                # Attacker piece blocking Defender direct threat case lookup
                for threat_pos_list in self.defender_threatOnAttacker.values():
                    for _pos in threat_pos_list:
                        if piece_standpoint == _pos:
                            _blocking_threat = True
                        if self.attacker_positions[_pos] == 'Rey' and _blocking_threat:
                            # La pieza está bloqueando un threat directo al rey
                            _single_origin_threat = True
                            # Aún puedo matar la amenaza.
                            # El orígen de la amenaza es el mínimo o máximo de
                            # la lista de posiciones-amenaza.
                            if movement == max(threat_pos_list):
                                _threat_origin_pos = max(threat_pos_list)
                            elif movement == min(threat_pos_list): 
                                _threat_origin_pos = min(threat_pos_list)
                            continue #skip to next iteration
                        # PERO si hay MAS DE UN origen de amenaza DIRECTA,
                        # invalidar todos los objetivos.
                        # (ninguna pieza puede eliminar dos o más orígenes de amenaza).
                        if self.attacker_positions[_pos] == 'Rey' and _single_origin_threat:
                            _single_origin_threat == False
                            return {}, {}
                # sino, devolver la única opcion de movimiento posible (matar amenaza)
                if _single_origin_threat and _threat_origin_pos != None:
                    on_target_kill_positions.update({_threat_origin_pos:self.boardRects[_threat_origin_pos]})
                    return mov_target_positions, on_target_kill_positions
                # ------------------------------------------------

                # Movement
                if movement not in self.black_positions and movement not in self.white_positions:
                    if piece_standpoint in self.in_base_Wpawns:
                        mov_target_positions.update({movement:self.boardRects[movement]})

                        # 2nd piece block condition
                        if movement+NORTE >= 0: # NORTE LIMIT

                            # Movement
                            if movement+NORTE not in self.black_positions and movement+NORTE not in self.white_positions:
                                mov_target_positions.update({movement+NORTE:self.boardRects[movement+NORTE]})
                    else:
                        mov_target_positions.update({movement:self.boardRects[movement]})
            
            # kill positions
            # Verificamos que el movimiento no rompa los límites del tablero
            if piece_standpoint+OESTE not in row_of_(piece_standpoint):
                kill_positions.append(piece_standpoint+NOR_ESTE)
            if piece_standpoint+ESTE not in row_of_(piece_standpoint):
                kill_positions.append(piece_standpoint+NOR_OESTE)
            elif len(kill_positions) == 0:
                kill_positions.extend([piece_standpoint+NOR_OESTE, piece_standpoint+NOR_ESTE])

            for kp in kill_positions:
                if kp in self.black_positions:
                    on_target_kill_positions.update({kp:self.boardRects[kp]})

                # King checks ------------------------------------
                if kp in self.defender_kingLegalMoves:
                    self.attacker_threatOnDefender['Peón'].append(kp)
                # ------------------------------------------------

        return mov_target_positions, on_target_kill_positions

    def tower_objectives(self, piece_standpoint: int) -> dict[int,pygame.Rect]:
        '''Movimiento Torre:
        +NORTE
        +SUR
        +ESTE
        +OESTE 
        "recursivo" hasta limite tablero o pieza aliada/enemiga.
        La torre mata como se mueve.
        '''

        # Visual feedback utils
        mov_target_positions: dict[int,pygame.Rect] = {piece_standpoint:self.boardRects[piece_standpoint]} # standpoint is always first pos
        on_target_kill_positions: dict[int,pygame.Rect] = {}
        
        # Objectives
        _threat_emission: list[int] = []
        _threatening: bool = False
        _single_origin_threat: bool | None = None
        _threat_origin_pos: int | None = None
        _blocking_threat: bool = False
        tower_directions = [NORTE,SUR,ESTE,OESTE]

        for direction in tower_directions:
            for mult in range(1,8): # 1 to board size
                movement = piece_standpoint+direction*mult
                if direction == ESTE or direction == OESTE:
                    if movement not in row_of_(piece_standpoint):
                        break
                if 0 <= movement <= 63: # VALID SQUARE

                    # Threat on defender updates ---------------------
                    _threat_emission.append(movement)
                    # King checks
                    if movement in self.defender_kingLegalMoves:
                        # Encontramos un spot de interés, eso significa que
                        # hay threat.
                        _threatening = True
                    # Luego de esto corresponde encontrar un STOP:
                    # > king standpoint O  > ya-no-hay-moves,
                    if _threatening and self.defender_positions[movement] == 'Rey': # chocamos contra rey
                        # STOP: adjuntar toda la traza threat.
                        self.attacker_threatOnDefender['Torre'].append(_threat_emission)
                        _threatening = False
                    elif _threatening and movement not in self.defender_kingLegalMoves: # fin del área de amenaza
                        # STOP: adjuntar toda la traza threat.
                        self.attacker_threatOnDefender['Torre'].append(_threat_emission)
                        _threatening = False
                    # ------------------------------------------------

                    # Attacker piece blocking Defender direct threat case lookup
                    for threat_pos_list in self.defender_threatOnAttacker.values():
                        for _pos in threat_pos_list:
                            if piece_standpoint == _pos:
                                _blocking_threat = True
                            if self.attacker_positions[_pos] == 'Rey' and _blocking_threat:
                                # La pieza está bloqueando un threat directo al rey
                                _single_origin_threat = True
                                # Aún puedo matar la amenaza.
                                # El orígen de la amenaza es el mínimo o máximo de
                                # la lista de posiciones-amenaza.
                                if movement == max(threat_pos_list):
                                    _threat_origin_pos = max(threat_pos_list)
                                elif movement == min(threat_pos_list): 
                                    _threat_origin_pos = min(threat_pos_list)
                                continue #skip to next iteration
                            # PERO si hay MAS DE UN origen de amenaza DIRECTA,
                            # invalidar todos los objetivos.
                            # (ninguna pieza puede eliminar dos o más orígenes de amenaza).
                            if self.attacker_positions[_pos] == 'Rey' and _single_origin_threat:
                                _single_origin_threat == False
                                return {}, {}
                    # sino, devolver la única opcion de movimiento posible (matar amenaza)
                    if _single_origin_threat and _threat_origin_pos != None:
                        on_target_kill_positions.update({_threat_origin_pos:self.boardRects[_threat_origin_pos]})
                        return mov_target_positions, on_target_kill_positions
                    # ------------------------------------------------

                    # Movement
                    if movement not in self.black_positions and movement not in self.white_positions:
                        mov_target_positions.update({movement:self.boardRects[movement]})
                    
                    # Kill-movement
                    elif movement in self.defender_positions:
                        on_target_kill_positions.update({movement:self.boardRects[movement]})
                        break   
                    break #previene propagación mas allá del primer bloqueo - rompe el mult
        return mov_target_positions, on_target_kill_positions

    def horse_objectives(self, piece_standpoint: int) -> dict[int,pygame.Rect]:
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
        mov_target_positions: dict[int,pygame.Rect] = {piece_standpoint:self.boardRects[piece_standpoint]} # standpoint is always first pos
        on_target_kill_positions: dict[int,pygame.Rect] = {}

        # Objectives
        _single_origin_threat: bool | None = None
        _threat_origin_pos: int | None = None
        _blocking_threat: bool = False
        horse_movements = []

        # ESTE / OESTE LIMITS
        if piece_standpoint+ESTE in row_of_(piece_standpoint):
            horse_movements.extend([piece_standpoint+NORTE+NOR_ESTE,
                                    piece_standpoint+SUR+SUR_ESTE])
            if piece_standpoint+ESTE*2 in row_of_(piece_standpoint):
                horse_movements.extend([piece_standpoint+ESTE+NOR_ESTE,
                                        piece_standpoint+ESTE+SUR_ESTE])
        if piece_standpoint+OESTE in row_of_(piece_standpoint):
            horse_movements.extend([piece_standpoint+NORTE+NOR_OESTE,
                                    piece_standpoint+SUR+SUR_OESTE])
            if piece_standpoint+OESTE*2 in row_of_(piece_standpoint):
                horse_movements.extend([piece_standpoint+OESTE+NOR_OESTE,
                                        piece_standpoint+OESTE+SUR_OESTE])
        
        for movement in horse_movements:
            if 0 <= movement <= 63: # NORTE/SUR LIMIT 

                # Threat on defender updates ---------------------
                if movement in self.defender_kingLegalMoves: 
                    self.attacker_threatOnDefender['Caballo'].append(movement)
                # ------------------------------------------------

                # Attacker piece blocking Defender direct threat case lookup
                    for threat_pos_list in self.defender_threatOnAttacker.values():
                        for _pos in threat_pos_list:
                            if piece_standpoint == _pos:
                                _blocking_threat = True
                            if self.attacker_positions[_pos] == 'Rey' and _blocking_threat:
                                # La pieza está bloqueando un threat directo al rey
                                _single_origin_threat = True
                                # Aún puedo matar la amenaza.
                                # El orígen de la amenaza es el mínimo o máximo de
                                # la lista de posiciones-amenaza.
                                if movement == max(threat_pos_list):
                                    _threat_origin_pos = max(threat_pos_list)
                                elif movement == min(threat_pos_list): 
                                    _threat_origin_pos = min(threat_pos_list)
                                continue #skip to next iteration
                            # PERO si hay MAS DE UN origen de amenaza DIRECTA,
                            # invalidar todos los objetivos.
                            # (ninguna pieza puede eliminar dos o más orígenes de amenaza).
                            if self.attacker_positions[_pos] == 'Rey' and _single_origin_threat:
                                _single_origin_threat == False
                                return {}, {}
                    # sino, devolver la única opcion de movimiento posible (matar amenaza)
                    if _single_origin_threat and _threat_origin_pos != None:
                        on_target_kill_positions.update({_threat_origin_pos:self.boardRects[_threat_origin_pos]})
                        return mov_target_positions, on_target_kill_positions
                    # ------------------------------------------------

                # Movement
                if movement not in self.black_positions and movement not in self.white_positions:
                    mov_target_positions.update({movement:self.boardRects[movement]})
                
                # Kill-movement
                elif movement in self.defender_positions:
                    on_target_kill_positions.update({movement:self.boardRects[movement]})
                    
        return mov_target_positions, on_target_kill_positions

    def bishop_objectives(self, piece_standpoint: int) -> dict[int,pygame.Rect]:
        '''Movimiento Alfil:
        +NOR_OESTE
        +NOR_ESTE
        +SUR_OESTE
        +SUR_ESTE
        "recursivo" hasta limite tablero o pieza aliada/enemiga
        '''
        
        # Visual feedback utils <- deberíamos desacoplar esto de aquí
        mov_target_positions: dict[int,pygame.Rect] = {piece_standpoint:self.boardRects[piece_standpoint]} # standpoint is always first pos
        on_target_kill_positions: dict[int,pygame.Rect] = {}
        
        # Objectives
        _threat_emission: list[int] = []
        _threatening: bool = False
        _single_origin_threat: bool | None = None
        _threat_origin_pos: int | None = None
        _blocking_threat: bool = False
        bishop_directions = [NOR_OESTE,NOR_ESTE,SUR_OESTE,SUR_ESTE]

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

                    # Threat on defender updates ---------------------
                    _threat_emission.append(movement)
                    # King checks
                    if movement in self.defender_kingLegalMoves:
                        # Encontramos un spot de interés, eso significa que
                        # hay threat.
                        _threatening = True
                    # Luego de esto corresponde encontrar un STOP:
                    # > king standpoint O  > ya-no-hay-moves,
                    if _threatening and self.defender_positions[movement] == 'Rey': # chocamos contra rey
                        # STOP: adjuntar toda la traza threat.
                        self.attacker_threatOnDefender['Alfil'].append(_threat_emission)
                        _threatening = False
                    elif _threatening and movement not in self.defender_kingLegalMoves: # fin del área de amenaza
                        # STOP: adjuntar toda la traza threat.
                        self.attacker_threatOnDefender['Alfil'].append(_threat_emission)
                        _threatening = False
                    # ------------------------------------------------

                    # Attacker piece blocking Defender direct threat case lookup
                    for threat_pos_list in self.defender_threatOnAttacker.values():
                        for _pos in threat_pos_list:
                            if piece_standpoint == _pos:
                                _blocking_threat = True
                            if self.attacker_positions[_pos] == 'Rey' and _blocking_threat:
                                # La pieza está bloqueando un threat directo al rey
                                _single_origin_threat = True
                                # Aún puedo matar la amenaza.
                                # El orígen de la amenaza es el mínimo o máximo de
                                # la lista de posiciones-amenaza.
                                if movement == max(threat_pos_list):
                                    _threat_origin_pos = max(threat_pos_list)
                                elif movement == min(threat_pos_list): 
                                    _threat_origin_pos = min(threat_pos_list)
                                continue #skip to next iteration
                            # PERO si hay MAS DE UN origen de amenaza DIRECTA,
                            # invalidar todos los objetivos.
                            # (ninguna pieza puede eliminar dos o más orígenes de amenaza).
                            if self.attacker_positions[_pos] == 'Rey' and _single_origin_threat:
                                _single_origin_threat == False
                                return {}, {}
                    # sino, devolver la única opcion de movimiento posible (matar amenaza)
                    if _single_origin_threat and _threat_origin_pos != None:
                        on_target_kill_positions.update({_threat_origin_pos:self.boardRects[_threat_origin_pos]})
                        return mov_target_positions, on_target_kill_positions
                    # ------------------------------------------------
                    
                    # Movement 
                    if movement not in self.black_positions and movement not in self.white_positions:
                        mov_target_positions.update({movement:self.boardRects[movement]})

                    # Kill-movement
                    elif movement in self.defender_positions:
                        on_target_kill_positions.update({movement:self.boardRects[movement]})
                        break
                    break #previene propagación mas allá del primer bloqueo - rompe el mult
        return mov_target_positions, on_target_kill_positions

    def king_objectives(self, piece_standpoint: int) -> dict[int,pygame.Rect]:
        '''Movimiento Rey:
        +NORTE
        +SUR
        +ESTE
        +OESTE
        +NOR_OESTE
        +NOR_ESTE
        +SUR_OESTE
        +SUR_ESTE
        1 casillero a la vez hasta limite tablero o pieza aliada/enemiga
        '''
        
        # Visual feedback utils
        mov_target_positions: dict[int,pygame.Rect] = {piece_standpoint: self.boardRects[piece_standpoint]} # standpoint is always first pos
        on_target_kill_positions: dict[int,pygame.Rect] = {}
        
        # Objectives
        king_directions = [NORTE,SUR,ESTE,OESTE,NOR_OESTE,NOR_ESTE,SUR_OESTE,SUR_ESTE]

        for direction in king_directions:
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

                '''
                
                Aquí realmente lo que debería hacer es updatear
                los conjuntos kingLegalMoves de ambos equipos.
                ^
                ^- realmente debería caer en esto o sólo
                   trabajar con una perspectiva ofensiva?
                   TODAS las otras funciones objectives()
                   están trabajando con perspectiva ofensiva
                   y pareciera que están bien.
                   Despues de todo los resultados y estados
                   siempre se deciden luego de una ofensiva,
                   lo importante es trasladar esos estados
                   al equipo que corresponda: attacker <=> defender
                
                Pero hacer eso realmente no coincide con una función
                trabajando en base a un standpoint.

                Si bien las otras funciones objectives() parecen
                funcionar, el king es distinto, ya que no
                amenaza a nadie pero recibe todas las amenazas,
                inversamente a las otras piezas.

                Para confirmar las amenazas, todas las otras
                objectives() usan defender_kingLegalMoves,
                realmente tiene uso un attacker_kingLegalMoves?
                Pareciera que no... O si...



                > defender_threatOnAttacker
                > attacker_threatOnDefender
                '''

                # Defender threat on me
                '''Puedo aquí mismo cantar jaque-mate? Debería?

                Revisando los threat-on-me puedo saber si
                estoy en amenaza directa y si puedo moverme o no,
                (puedo matar amenaza si eso no implica caer en otra
                casilla de threat).

                Lo que no estoy seguro es si debo decidir jaque-mate
                con una perspectiva totalmente global de todas las 
                variables o decidirlo en base a "pequeñas deducciones"

                
                '''
                for threat_pos_list in self.defender_threatOnAttacker.values():
                    for _pos in threat_pos_list:
                        if piece_standpoint == _pos:
                            ...

                if movement in self.defender_kingLegalMoves: #illegal movement
                    continue
                if movement not in self.black_positions and movement not in self.white_positions:
                    mov_target_positions.update({movement:self.boardRects[movement]}) 
                
                elif movement in self.defender_positions:
                    on_target_kill_positions.update({movement:self.boardRects[movement]})
                    continue

        return mov_target_positions, on_target_kill_positions

    def queen_objectives(self, piece_standpoint: int) -> dict[int,pygame.Rect]:
        '''Movimiento Reina:
        +NORTE
        +SUR
        +ESTE
        +OESTE
        +NOR_OESTE
        +NOR_ESTE
        +SUR_OESTE
        +SUR_ESTE
        "recursivo" hasta limite tablero o pieza aliada/enemiga
        '''
       
        # Visual feedback utils
        mov_target_positions: dict[int,pygame.Rect] = {piece_standpoint:self.boardRects[piece_standpoint]} # standpoint is always first pos
        on_target_kill_positions: dict[int,pygame.Rect] = {}

        # Objectives
        _threat_emission: list[int] = []
        _threatening: bool = False
        _single_origin_threat: bool | None = None
        _threat_origin_pos: int | None = None
        _blocking_threat: bool = False
        queen_directions = [NORTE,SUR,ESTE,OESTE,NOR_OESTE,NOR_ESTE,SUR_OESTE,SUR_ESTE]

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

                    # Threat on defender updates ---------------------
                    _threat_emission.append(movement)
                    # King checks
                    if movement in self.defender_kingLegalMoves:
                        # Encontramos un spot de interés, eso significa que
                        # hay threat.
                        _threatening = True
                    # Luego de esto corresponde encontrar un STOP:
                    # > king standpoint O  > ya-no-hay-moves,
                    if _threatening and self.defender_positions[movement] == 'Rey': # chocamos contra rey
                        # STOP: adjuntar toda la traza threat.
                        self.attacker_threatOnDefender['Reina'].append(_threat_emission)
                        _threatening = False
                    elif _threatening and movement not in self.defender_kingLegalMoves: # fin del área de amenaza
                        # STOP: adjuntar toda la traza threat.
                        self.attacker_threatOnDefender['Reina'].append(_threat_emission)
                        _threatening = False
                    # ------------------------------------------------

                    # Attacker piece blocking Defender direct threat case lookup
                    for threat_pos_list in self.defender_threatOnAttacker.values():
                        for _pos in threat_pos_list:
                            if piece_standpoint == _pos:
                                _blocking_threat = True
                            if self.attacker_positions[_pos] == 'Rey' and _blocking_threat:
                                # La pieza está bloqueando un threat directo al rey
                                _single_origin_threat = True
                                # Aún puedo matar la amenaza.
                                # El orígen de la amenaza es el mínimo o máximo de
                                # la lista de posiciones-amenaza.
                                if movement == max(threat_pos_list):
                                    _threat_origin_pos = max(threat_pos_list)
                                elif movement == min(threat_pos_list): 
                                    _threat_origin_pos = min(threat_pos_list)
                                continue #skip to next iteration
                            # PERO si hay MAS DE UN origen de amenaza DIRECTA,
                            # invalidar todos los objetivos.
                            # (ninguna pieza puede eliminar dos o más orígenes de amenaza).
                            if self.attacker_positions[_pos] == 'Rey' and _single_origin_threat:
                                _single_origin_threat == False
                                return {}, {}
                    # sino, devolver la única opcion de movimiento posible (matar amenaza)
                    if _single_origin_threat and _threat_origin_pos != None:
                        on_target_kill_positions.update({_threat_origin_pos:self.boardRects[_threat_origin_pos]})
                        return mov_target_positions, on_target_kill_positions
                    # ------------------------------------------------

                    # Movement
                    if movement not in self.black_positions and movement not in self.white_positions:
                        mov_target_positions.update({movement:self.boardRects[movement]}) 
                    
                    # Kill-movement
                    elif movement in self.defender_positions:
                        on_target_kill_positions.update({movement:self.boardRects[movement]})
                        break
                    break #previene propagación mas allá del primer bloqueo - rompe el mult
        return mov_target_positions, on_target_kill_positions

    def draw_board(self):

        # main board frame
        pygame.draw.rect(self.screen,(200,200,200),
                    pygame.Rect(self.board_begin.x,self.board_begin.y,
                                board.width,board.height),width=3)

        for board_index, SQUARE_RECT in enumerate(self.boardRects): #celdas que sirven por posición, índice y medida.

            # individual grid frame
            pygame.draw.rect(self.screen,(200,200,200),SQUARE_RECT,width=1)
            self.draw_text(f'{board_index}',(150,150,150),
                           SQUARE_RECT.left +3,
                           SQUARE_RECT.top + board.square_height -17,
                           center=False, font_size='medium')
            
            # Diccionarios de posiciones --------------------------
            if board_index in self.black_positions.keys():
                SQUARE_SUBTYPE = "kill-movement" if board_index in self.pieceValidKill_posDisplay.keys() else ""
                SQUARE_TYPE =  self.black_positions[board_index]
                interacted_PColor = "Black"

            elif board_index in self.white_positions.keys():
                SQUARE_SUBTYPE = "kill-movement" if board_index in self.pieceValidKill_posDisplay.keys() else ""
                SQUARE_TYPE = self.white_positions[board_index]
                interacted_PColor = "White"

            elif board_index in self.pieceValidMovement_posDisplay.keys():
                SQUARE_SUBTYPE = "valid-movement"
                SQUARE_TYPE = ""
                interacted_PColor = ""

            else: SQUARE_TYPE = "EMPTY"; interacted_PColor = ""; SQUARE_SUBTYPE = ""
            # ----------------------------------------------------

            # draw piece
            if SQUARE_TYPE != "EMPTY":
                if interacted_PColor == 'Black':
                    self.draw_text(SQUARE_TYPE,'black', SQUARE_RECT.left + board.square_width/2,
                                                        SQUARE_RECT.top + board.square_height/2)
                if interacted_PColor == 'White':
                    self.draw_text(SQUARE_TYPE,(120,120,120),
                                                      SQUARE_RECT.left + board.square_width/2,
                                                      SQUARE_RECT.top + board.square_height/2)

            # hidden/visible elements upon paused state
            if not self.master.paused:
                if SQUARE_RECT.collidepoint((self.master.mx,self.master.my)):

                    # Hover -----------------------
                    if interacted_PColor == self.turn_attacker:
                        pygame.draw.rect(self.screen,'GREEN',SQUARE_RECT,width=2) # PIECE hover
                    else:
                        pygame.draw.rect(self.screen,(150,150,150),SQUARE_RECT,width=2) # EMPTY hover
                    # Hover -----------------------
                
                    if self.master.click:

                        self.pieceValidKill_posDisplay.clear()

                        if SQUARE_SUBTYPE == "kill-movement":
                            self.killing = True
                            self.move_here = board_index

                        elif SQUARE_SUBTYPE == "valid-movement": # movimientos inválidos nunca llegan a este estado
                            self.move_here = board_index
                            if board_index in self.in_base_Bpawns:
                                self.in_base_Bpawns.remove(board_index)
                            if board_index in self.in_base_Wpawns:
                                self.in_base_Wpawns.remove(board_index)

                        else: 
                            if SQUARE_TYPE == 'Peón':
                                self.pieceValidMovement_posDisplay.clear()
                                if interacted_PColor == self.turn_attacker:
                                    self.pieceValidMovement_posDisplay, self.pieceValidKill_posDisplay = self.pawn_objectives(board_index)

                            if SQUARE_TYPE == 'Torre':
                                self.pieceValidMovement_posDisplay.clear()
                                if interacted_PColor == self.turn_attacker:
                                    self.pieceValidMovement_posDisplay, self.pieceValidKill_posDisplay = self.tower_objectives(board_index)
                            
                            if SQUARE_TYPE == 'Caballo':
                                self.pieceValidMovement_posDisplay.clear()
                                if interacted_PColor == self.turn_attacker:
                                    self.pieceValidMovement_posDisplay, self.pieceValidKill_posDisplay = self.horse_objectives(board_index)
                        
                            if SQUARE_TYPE == 'Alfil':
                                self.pieceValidMovement_posDisplay.clear()
                                if interacted_PColor == self.turn_attacker:
                                    self.pieceValidMovement_posDisplay, self.pieceValidKill_posDisplay = self.bishop_objectives(board_index)

                            if SQUARE_TYPE == 'Rey':
                                self.pieceValidMovement_posDisplay.clear()
                                if interacted_PColor == self.turn_attacker:
                                    self.pieceValidMovement_posDisplay, self.pieceValidKill_posDisplay = self.king_objectives(board_index)

                            if SQUARE_TYPE == 'Reina':
                                self.pieceValidMovement_posDisplay.clear()
                                if interacted_PColor == self.turn_attacker:
                                    self.pieceValidMovement_posDisplay, self.pieceValidKill_posDisplay = self.queen_objectives(board_index)
                                
                            if SQUARE_TYPE == "EMPTY":
                                self.pieceValidMovement_posDisplay.clear()

        # updating element's positions and game relevant state if a movement/kill was stated
        if self.move_here != None:
            ex_value: int = list(self.pieceValidMovement_posDisplay.items())[0][0]

            if self.turn_defender == 'White':
                _piece = self.black_positions.pop(ex_value)
                if self.killing:
                    self.white_positions.pop(self.move_here)
                self.black_positions.update({self.move_here:_piece})               

            if self.turn_defender == 'Black':
                _piece = self.white_positions.pop(ex_value)
                if self.killing:
                    self.black_positions.pop(self.move_here) 
                self.white_positions.update({self.move_here:_piece})

            # POST MOVIMIENTOS / ATAQUES -----------------------------------------------------------------
            # Actualizar todos los registros de posiciones 
            self.update_turn_objectives() 
            # Evaluación de posiciones 
            self.decide_check() #<- El juego debe continuar? 

            self.turn_swap()
            self.pieceValidMovement_posDisplay.clear()
            self.move_here = None
            self.killing = False

        # Pre-movements visual feedback
        if len(self.pieceValidMovement_posDisplay) > 1 or len(self.pieceValidKill_posDisplay) > 0:
            for valid_mov_RECT in self.pieceValidMovement_posDisplay.values():
                pygame.draw.rect(self.screen,'GREEN',valid_mov_RECT,width=2)
        for valid_kill_RECT in self.pieceValidKill_posDisplay.values():
            pygame.draw.rect(self.screen,'RED',valid_kill_RECT,width=2)

    def get_piece_standpoint(self, color:str, piece:str) -> list[int]:
        '''> Argumentar pieza exactamente igual que en pieces.origins
        > Utilizar .pop() en piezas singulares como Rey y Reina'''
        _actual_standpoints: list[int] = []
        if color == 'Black':
            for k,v in self.black_positions.items():
                if v == piece:
                    _actual_standpoints.append(k)
        if color == 'White':
            for k,v in self.white_positions.items():
                if v == piece:
                    _actual_standpoints.append(k)
        return _actual_standpoints

    def decide_check(self):
        '''
        Evaluar posiciones _allPositions, _checkPositions para resolver estados
        jaque/jaque-mate.

        Estoy pensando que quizás aqui mismo debería restringir movimientos inválidos,
        porque el camino lógico a deducir qué y por qué no puedo mover esta aquí.

        Es decir, en el momento en q registro un jaque, se qué unicos movimientos
        puedo hacer, o eso debería deducir.

        De todas formas siento que es mejor delegar esta acción de manipular posiciones
        a otra función porque es profunda en sí, o al menos eso parece.
        
        JAQUE > El rey es apuntado directamente, PUEDE escapar moviendose o siendo
            salvado por pieza aliada (matando o bloqueando amenaza) <- Square types?

        JAQUE-MATE > El rey es apuntado directamente, NO PUEDE escapar moviendose ni
            siendo salvado por pieza aliada. 

        STALE-MATE > Si el rey no es apuntado directamente pero no puede moverse ni
            ser salvado por pieza aliada. Estado de empate.
        '''
        if self.get_piece_standpoint(self.turn_defender,"Rey").pop() in self.targetColor_KingCHECKPOS:
            #ok, está en jaque. ¿pero tiene escapatoria?
            if set(self.targetColor_KingALLPOS) == self.targetColor_KingCHECKPOS:
                #ok tampoco puede moverse. ¿pero puede una pieza salvarlo?
                if self.targetColor_KingCHECKPOS not in self.saving_positions: # JAQUE-MATE
                    #está apuntado, está rodeado y no puede ser salvado
                    if self.turn_defender == 'Black': 
                        self.winner = True # automaticamente repercutirá draw() - 29/09 NO TESTEADA
                        self.match_state = 'White gana - Black en jaque-mate'
                    if self.turn_defender == 'White': 
                        self.winner = True # automaticamente repercutirá draw() - 29/09 NO TESTEADA
                        self.match_state = 'Black gana - White en jaque-mate'
            else: # JAQUE
                #puede ser salvado, o no todo su camino no está rodeado
                if self.turn_defender == 'Black': 
                    #alertar al jugador
                    self.match_state = 'Rey Black en jaque'
                    #modificar posiciones inválidas aquí o no? La lógica para invalidarlas "es por acá"...o no?
                if self.turn_defender == 'White': 
                    #alertar al jugador
                    self.match_state = 'Rey White en jaque'
                    #modificar posiciones inválidas aquí o no? La lógica para invalidarlas "es por acá"...o no?
        # Ahogado | stalemate (draw)
        elif set(self.targetColor_KingALLPOS).discard(self.get_piece_standpoint(self.turn_defender,"Rey").pop()) == self.targetColor_KingCHECKPOS:
            #ok, está rodeado ¿pero alguna pieza puede salvarlo?
            if self.targetColor_KingCHECKPOS not in self.saving_positions: # DRAW
                # nadie puede salvarlo tampoco
                self.stalemate == True # debería repercutir automaticamente en render()  - 15/10 PARCIALMENTE IMPLEMENTADO / NO TESTEADO
                self.match_state = 'Rey ahogado - Empate'

    def render(self):
        #hud
        self.draw_text('Match scene','black',20,20,center=False)
        self.draw_text(f'{self.match_mode['mode']}','black',200,20,center=False)
        self.draw_board()
        self.draw_text(self.turn_attacker,'black',self.midScreen_pos.x - 25, board.height+70,center=False)
        if self.master.paused:
            if not self.player_deciding_match:
                self.draw_pause_menu()
            else:
                self.draw_confirm_restart_menu()
        if self.winner or self.stalemate:
            self.draw_post_game_menu()

    def draw_confirm_restart_menu(self,width=300,height=300):
        # frame
        pygame.draw.rect(self.screen,(100,100,100),
                        pygame.Rect(self.master.screen.get_width()-400,150,width,height))
        #leyenda
        self.draw_text('¿Está seguro que quiere reiniciar la partida?','black',self.screen.get_width()-400,150,center=False)
        self.draw_confirm_match_restart_btn()
        self.draw_cancel_restart_btn()
        
    def draw_confirm_match_restart_btn(self):
        self.draw_text('Si','black',self.screen.get_width()-400,190,center=False)
        confirm_match_rect = pygame.Rect(self.screen.get_width()-400,190,200,50)
        if confirm_match_rect.collidepoint((self.master.mx,self.master.my)):
            #hover
            pygame.draw.rect(self.screen,(255,0,0),confirm_match_rect,width=1)
            if self.master.click:
                self.reset_board()
                self.player_deciding_match = False
                self.master.paused = False

    def draw_cancel_restart_btn(self):
        self.draw_text('No','black',self.screen.get_width()-400,250,center=False)
        cancel_match_rect = pygame.Rect(self.screen.get_width()-400,250,200,50)
        if cancel_match_rect.collidepoint((self.master.mx,self.master.my)):
            #hover
            pygame.draw.rect(self.screen,(255,0,0),cancel_match_rect,width=1)
            if self.master.click:
                self.player_deciding_match = False

    def draw_continue_btn(self):
        self.draw_text('Continuar','white',self.screen.get_width()-400,190,center=False)
        continue_match_rect = pygame.Rect(self.screen.get_width()-400,190,200,50)
        if continue_match_rect.collidepoint((self.master.mx,self.master.my)):
            #hover
            pygame.draw.rect(self.screen,(255,0,0),continue_match_rect,width=1)
            if self.master.click:
                self.master.paused = False

    def draw_exit_to_mainMenu_btn(self):
        self.draw_text('Salir al menú principal','white',self.screen.get_width()-400,250,center=False)
        exit_to_main_menu_rect = pygame.Rect(self.screen.get_width()-400,250,200,50)
        if exit_to_main_menu_rect.collidepoint((self.master.mx,self.master.my)):
            #hover
            pygame.draw.rect(self.screen,(255,0,0),exit_to_main_menu_rect,width=1)
            if self.master.click:
                self.master.paused = False
                self.master.scene_manager = MainMenu

    def draw_exit_game_btn(self):
        self.draw_text('Salir del juego','white',self.screen.get_width()-400,320,center=False)
        exit_game_rect = pygame.Rect(self.screen.get_width()-400,320,200,50)
        if exit_game_rect.collidepoint((self.master.mx,self.master.my)):
            #hover
            pygame.draw.rect(self.screen,(255,0,0),exit_game_rect,width=1)
            if self.master.click:
                self.master.scene_manager = 'exit'

    def draw_post_game_menu(self,width=300,height=300):
        # frame
        pygame.draw.rect(self.screen,(100,100,100),
                        pygame.Rect(self.master.screen.get_width()-400,150,width,height))
        # tooltip
        self.draw_text('$jugador wins','black',self.screen.get_width()-400,150,center=False)
        self.draw_play_again_btn()
        self.draw_exit_to_mainMenu_btn()

    def draw_pause_menu(self,width=300,height=400):
        # frame
        pygame.draw.rect(self.screen,(100,100,100),
                        pygame.Rect(self.master.screen.get_width()-400,150,width,height))
        # tooltip
        self.draw_text('Paused','black',self.screen.get_width()-400,150,center=False)
        self.draw_continue_btn()
        self.draw_play_again_btn()
        self.draw_exit_to_mainMenu_btn()
        self.draw_exit_game_btn()

    def draw_play_again_btn(self):
        self.draw_text('Reiniciar partida', 'white', self.screen.get_width()-400,400,center=False)
        play_again_rect = pygame.Rect(self.screen.get_width()-400,400,200,50)
        if play_again_rect.collidepoint((self.master.mx, self.master.my)):
            #hover
            pygame.draw.rect(self.screen,(255,0,0),play_again_rect,width=1)
            if self.master.click:
                self.player_deciding_match = True
