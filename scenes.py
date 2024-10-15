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
    def __init__(self,master):
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

        # game variables
        self.match_mode: dict = self.master.game_variables
        self.move_here: int | None = None
        self.turn_attacker: str = 'White'
        self.turn_target: str = 'Black'
        self.winner: bool = False
        self.player_deciding_match = False
        self.killing: bool = False
        self.W_check_state: str | None = None #jaque o jaque-mate o None
        self.B_check_state: str | None = None #jaque o jaque-mate o None
        self.movement_validPositions: dict[int, pygame.Rect] = {} 
        self.kill_validPositions: dict[int, pygame.Rect] = {}

        # Previo a un movimiento: conocer mis movimientos-inválidos
        # Movimientos que no pueden realizarse porque exponen al rey a un kill-movement, o que --> DOS TIPOS DE INVALID
        # no lo salvan en caso de estar el rey ya expuesto a un kill-movement. ------------------> MOV. DISTINTOS?
        # Algunas piezas no podrán moverse en absoluto, otras podrán moverse parcialmente.
        #
        # Estos conjuntos son actualizados luego de mover una pieza (si corresponde).
        # Son tambien revisados en cada movimiento de pieza. -> Expone rey // No-salva rey
        self.white_invalid_positions: dict[str, list[int]] = {} # {'peon': [2,4], 'alfil': [12,18,24]}
        self.black_invalid_positions: dict[str, list[int]] = {}

        # board config
        self.board_begin = pygame.Vector2(
            (self.midScreen_pos.x - board.width/2,
            self.midScreen_pos.y - board.height/2))
        self.boardRects: list[pygame.Rect] = board.make_rects(self.board_begin)
        
        # board set defaults
        self.in_base_Bpawns: list[int] = [bpawn for bpawn in pieces.origins['negras']['Peón']]
        self.in_base_Wpawns: list[int] = [wpawn for wpawn in pieces.origins['blancas']['Peón']]

        self.blackKing_allPositions: list[int] = [bk for bk in pieces.origins['negras']['Rey']] # stndpoint (luego + movimientos)
        self.whiteKing_allPositions: list[int] = [wk for wk in pieces.origins['blancas']['Rey']] # stndpoint (luego + movimientos)
        self.blackKing_checkPositions: set[int] = {} #set que si iguala a blackKing_allPositions es JAQUE MATE
        self.whiteKing_checkpositions: set[int] = {} #set que si iguala a whiteKing_allPositions es JAQUE MATE
        
        self.black_positions: dict[int,str] = pieces.black_positions
        self.white_positions: dict[int,str] = pieces.white_positions
        
        # turn lookups
        '''Estas variables serán actualizadas por:
        update_target_king() y make_targets()'''
        self.turnTarget_checkState = None
        self.targetcolor_kingCheckPos: set[int] = self.blackKing_checkPositions # default
        self.targetcolor_kingAllPositions: list[int] = self.blackKing_allPositions # default

    def make_targets(self):
        pawn_standpoints: list[int] = self.get_piece_standpoint(color=self.turn_attacker,piece="Peón")
        for _pawn in pawn_standpoints:
            self.pawn_targets(_pawn)

        tower_standpoints: list[int] = self.get_piece_standpoint(color=self.turn_attacker,piece="Torre")
        for _tower in tower_standpoints:
            self.tower_targets(_tower)

        bishop_standpoints: list[int] = self.get_piece_standpoint(color=self.turn_attacker,piece="Alfil")
        for _bishop in bishop_standpoints:
            self.bishop_targets(_bishop)

        horse_standpoints: list[int] = self.get_piece_standpoint(color=self.turn_attacker,piece="Caballo")
        for _horse in horse_standpoints:
            self.horse_targets(_horse)

        queen_standpoint: int = self.get_piece_standpoint(color=self.turn_attacker,piece="Reina").pop()
        self.queen_targets(queen_standpoint)
        
    def update_target_king(self): #debe ser llamado DESPUES DE QUE SE MOVIÓ ALGO 
        #nuevas all_positions
        self.targetcolor_kingAllPositions = self.get_king_movements(self.turn_target)
        #actualizando nuevas check positions
        self.make_targets()

    def reset_board(self):
        self.in_base_Bpawns = [bpawn for bpawn in pieces.origins['negras']['Peón']]
        self.in_base_Wpawns = [wpawn for wpawn in pieces.origins['blancas']['Peón']]
        self.blackKing_allPositions = [bk for bk in pieces.origins['negras']['Rey']] #standpoint sin movimiento
        self.whiteKing_allPositions = [wk for wk in pieces.origins['blancas']['Rey']] #standpoint sin movimiento
        self.targetcolor_kingAllPositions = self.whiteKing_allPositions # default
        self.black_positions = pieces.black_positions
        self.white_positions = pieces.white_positions
        self.blackKing_checkPositions = []
        self.whiteKing_checkpositions = []
        self.targetcolor_kingCheckPos = self.whiteKing_checkpositions
        self.turn_attacker = 'White'
        self.winner = False

    def turn_swap(self):
        if self.turn_attacker == 'White':
            self.turn_attacker = 'Black'
            self.turn_target = 'White'
            #1ro transfiero targets
            self.blackKing_allPositions = self.targetcolor_kingAllPositions
            self.blackKing_checkPositions = self.targetcolor_kingCheckPos
            #luego intercambio targets lists
            self.targetcolor_kingCheckPos = self.whiteKing_checkpositions
            self.targetcolor_kingAllPositions = self.whiteKing_allPositions
            return
        if self.turn_attacker == 'Black':
            self.turn_attacker = 'White'
            self.turn_target = 'Black'
            #1ro transfiero targets
            self.whiteKing_allPositions = self.targetcolor_kingAllPositions
            self.whiteKing_checkpositions = self.targetcolor_kingCheckPos
            #luego intercambio targets lists
            self.targetcolor_kingCheckPos = self.blackKing_checkPositions
            self.targetcolor_kingAllPositions = self.blackKing_allPositions
            return
    
    def pawn_targets(
        self,
        piece_standpoint: int,
        ) -> dict[int,pygame.Rect]:
        '''Movimiento Peón:
        NORTE (white)
        SUR (black)
        1 casillero por vez, excepto que sea su primer movimiento,
        lo que hará que pueda moverse 2 casilleros a la vez.
        Kill mov. Peón:
        Peon NEGRO: SUR_OESTE, SUR_ESTE
        Peon BLANCO: NOR_OESTE, NOR_ESTE
        '''
        mov_target_positions: dict[int,pygame.Rect] = {piece_standpoint:self.boardRects[piece_standpoint]} # standpoint is always first pos 
        on_target_kill_positions: dict[int,pygame.Rect] = {}
        kill_positions: list[int] = []

        if self.turn_target == 'White':
            # SUR
            movement: int = piece_standpoint+SUR

            # --- no implementado ---
            if movement not in self.black_invalid_positions['peon']: ... # !! REPETIR ESTO EN CADA PIEZA !! CUIDADO COLOR !!
            # --- no implementado ---

            # piece block condition
            if movement <= 63: # SUR LIMIT
                if movement not in self.black_positions and movement not in self.white_positions:
                    if piece_standpoint in self.in_base_Bpawns:
                        mov_target_positions.update({movement:self.boardRects[movement]})
                        # 2nd piece block condition
                        if movement+SUR <= 63: #board limit check
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
                
                # repetir en toda función _targets()
                if kp in self.targetcolor_kingAllPositions:
                    self.targetcolor_kingCheckPos.add(kp)

        if self.turn_target == 'Black': 
            # NORTE
            movement: int = piece_standpoint+NORTE
            # piece block condition
            if movement >= 0: # NORTE LIMIT
                if movement not in self.black_positions and movement not in self.white_positions:
                    if piece_standpoint in self.in_base_Wpawns:
                        mov_target_positions.update({movement:self.boardRects[movement]})
                        # 2nd piece block condition
                        if movement+NORTE >= 0: # NORTE LIMIT
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

                if kp in self.targetcolor_kingAllPositions:
                    self.targetcolor_kingCheckPos.add(kp)

        return mov_target_positions, on_target_kill_positions

    def tower_targets(
        self,
        piece_standpoint: int,
        ) -> dict[int,pygame.Rect]:
        '''Movimiento Torre:
        +NORTE
        +SUR
        +ESTE
        +OESTE 
        "recursivo" hasta limite tablero o pieza aliada/enemiga.
        La torre mata como se mueve.
        '''
        mov_target_positions: dict[int,pygame.Rect] = {piece_standpoint:self.boardRects[piece_standpoint]} # standpoint is always first pos
        on_target_kill_positions: dict[int,pygame.Rect] = {}
        tower_directions = [NORTE,SUR,ESTE,OESTE]

        for direction in tower_directions:
            for mult in range(1,8): # 1 to board size
                movement = piece_standpoint+direction*mult
                if direction == ESTE or direction == OESTE:
                    if movement not in row_of_(piece_standpoint):
                        break
                if 0 <= movement <= 63:
                    if movement in self.targetcolor_kingAllPositions:
                        self.targetcolor_kingCheckPos.add(movement)
                    if movement not in self.black_positions and movement not in self.white_positions:
                        mov_target_positions.update({movement:self.boardRects[movement]})
                    else:
                        if self.turn_target == 'Black':
                            if movement in self.black_positions:
                                on_target_kill_positions.update({movement:self.boardRects[movement]})
                                break
                        if self.turn_target == 'White':
                            if movement in self.white_positions:
                                on_target_kill_positions.update({movement:self.boardRects[movement]})
                                break
                        break #previene propagación mas allá del primer bloqueo - rompe el mult
        return mov_target_positions, on_target_kill_positions

    def horse_targets(
        self,
        piece_standpoint: int,
        ) -> dict[int,pygame.Rect]:
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
        mov_target_positions: dict[int,pygame.Rect] = {piece_standpoint:self.boardRects[piece_standpoint]} # standpoint is always first pos
        on_target_kill_positions: dict[int,pygame.Rect] = {}
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
                if movement in self.targetcolor_kingAllPositions:
                    self.targetcolor_kingCheckPos.add(movement)
                if movement not in self.black_positions and movement not in self.white_positions:
                    mov_target_positions.update({movement:self.boardRects[movement]})
                else:
                    if self.turn_target == 'White':
                        if movement in self.white_positions:
                            on_target_kill_positions.update({movement:self.boardRects[movement]})
                    if self.turn_target == 'Black':
                        if movement in self.black_positions:
                            on_target_kill_positions.update({movement:self.boardRects[movement]})
        return mov_target_positions, on_target_kill_positions

    def bishop_targets(
        self,
        piece_standpoint: int,
        ) -> dict[int,pygame.Rect]:
        '''Movimiento Alfil:
        +NOR_OESTE
        +NOR_ESTE
        +SUR_OESTE
        +SUR_ESTE
        "recursivo" hasta limite tablero o pieza aliada/enemiga
        '''
        mov_target_positions: dict[int,pygame.Rect] = {piece_standpoint:self.boardRects[piece_standpoint]} # standpoint is always first pos
        on_target_kill_positions: dict[int,pygame.Rect] = {}
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
                if 0 <= movement <= 63:
                    if movement in self.targetcolor_kingAllPositions:
                        self.targetcolor_kingCheckPos.add(movement)
                    if movement not in self.black_positions and movement not in self.white_positions:
                        mov_target_positions.update({movement:self.boardRects[movement]})
                    else:
                        if self.turn_target == 'White':
                            if movement in self.white_positions:
                                on_target_kill_positions.update({movement:self.boardRects[movement]})
                                break
                        if self.turn_target == 'Black':
                            if movement in self.black_positions:
                                on_target_kill_positions.update({movement:self.boardRects[movement]})
                                break
                        break #previene propagación mas allá del primer bloqueo - rompe el mult
        return mov_target_positions, on_target_kill_positions

    def king_targets(
        self,
        piece_standpoint: int,
        ) -> dict[int,pygame.Rect]:
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
        mov_target_positions: dict[int,pygame.Rect] = {piece_standpoint: self.boardRects[piece_standpoint]} # standpoint is always first pos
        on_target_kill_positions: dict[int,pygame.Rect] = {}
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
            if 0 <= movement <= 63:
                if movement in self.targetcolor_kingAllPositions: #illegal movement
                    continue
                if movement not in self.black_positions and movement not in self.white_positions:
                    mov_target_positions.update({movement:self.boardRects[movement]}) 
                else:
                    if self.turn_target == 'White':
                        if movement in self.white_positions:
                            on_target_kill_positions.update({movement:self.boardRects[movement]})
                    if self.turn_target == 'Black':
                        if movement in self.black_positions:
                            on_target_kill_positions.update({movement:self.boardRects[movement]})
                    continue
        return mov_target_positions, on_target_kill_positions

    def queen_targets(
        self,
        piece_standpoint: int,
        ) -> dict[int,pygame.Rect]:
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
        mov_target_positions: dict[int,pygame.Rect] = {piece_standpoint:self.boardRects[piece_standpoint]} # standpoint is always first pos
        on_target_kill_positions: dict[int,pygame.Rect] = {}
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
                if 0 <= movement <= 63:
                    if movement in self.targetcolor_kingAllPositions:
                        self.targetcolor_kingCheckPos.add(movement)
                    if movement not in self.black_positions and movement not in self.white_positions:
                        mov_target_positions.update({movement:self.boardRects[movement]}) 
                    else:
                        if self.turn_target == 'White':
                            if movement in self.white_positions:
                                on_target_kill_positions.update({movement:self.boardRects[movement]})
                                break
                        if self.turn_target == 'Black':
                            if movement in self.black_positions:
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
                SQUARE_SUBTYPE = "kill-movement" if board_index in self.kill_validPositions.keys() else ""
                SQUARE_TYPE =  self.black_positions[board_index]
                interacted_PColor = "Black"

            elif board_index in self.white_positions.keys():
                SQUARE_SUBTYPE = "kill-movement" if board_index in self.kill_validPositions.keys() else ""
                SQUARE_TYPE = self.white_positions[board_index]
                interacted_PColor = "White"

            elif board_index in self.movement_validPositions.keys():
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

                        self.kill_validPositions.clear()

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
                                self.movement_validPositions.clear()
                                if interacted_PColor == self.turn_attacker:
                                    self.movement_validPositions, self.kill_validPositions = self.pawn_targets(board_index)

                            if SQUARE_TYPE == 'Torre':
                                self.movement_validPositions.clear()
                                if interacted_PColor == self.turn_attacker:
                                    self.movement_validPositions, self.kill_validPositions = self.tower_targets(board_index)
                            
                            if SQUARE_TYPE == 'Caballo':
                                self.movement_validPositions.clear()
                                if interacted_PColor == self.turn_attacker:
                                    self.movement_validPositions, self.kill_validPositions = self.horse_targets(board_index)
                        
                            if SQUARE_TYPE == 'Alfil':
                                self.movement_validPositions.clear()
                                if interacted_PColor == self.turn_attacker:
                                    self.movement_validPositions, self.kill_validPositions = self.bishop_targets(board_index)

                            if SQUARE_TYPE == 'Rey':
                                self.movement_validPositions.clear()
                                if interacted_PColor == self.turn_attacker:
                                    self.movement_validPositions, self.kill_validPositions = self.king_targets(board_index)

                            if SQUARE_TYPE == 'Reina':
                                self.movement_validPositions.clear()
                                if interacted_PColor == self.turn_attacker:
                                    self.movement_validPositions, self.kill_validPositions = self.queen_targets(board_index)
                                
                            if SQUARE_TYPE == "EMPTY":
                                self.movement_validPositions.clear()

        # >> Previo a un movimiento: conocer mis movimientos-inválidos <<
        # updating element's positions and game relevant state if a movement/kill was stated
        if self.move_here != None:
            ex_value: int = list(self.movement_validPositions.items())[0][0]

            if self.turn_target == 'White':
                _piece = self.black_positions.pop(ex_value)
                if self.killing:
                    self.white_positions.pop(self.move_here)
                self.black_positions.update({self.move_here:_piece})               

            if self.turn_target == 'Black':
                _piece = self.white_positions.pop(ex_value)
                if self.killing:
                    self.black_positions.pop(self.move_here) 
                self.white_positions.update({self.move_here:_piece})

            # POST MOVIMIENTOS / ATAQUES -----------------------------------------------------------------
            self.update_target_king() # renovación de posiciones-rey y sus nuevos checks
            self.update_invalid_movements() # renovación de movimientos-inválidos
            self.decide_check() # <- evaluación de posiciones incl. movimientos-inválidos | modifica self.turnTarget_checkState

            if self.turnTarget_checkState == 'jaque':
                #alertar al jugador -los movimientos inválidos ya fueron computados-
                if self.turn_target == 'Black': ...
                if self.turn_target == 'White': ...
            if self.turnTarget_checkState == 'jaque-mate':
                self.winner = True # automaticamente repercutirá draw() - 29/09 NO TESTEADA
                #color_winner? 
                if self.turn_target == 'Black': ...
                if self.turn_target == 'White': ...

            self.turn_swap()
            self.movement_validPositions.clear()
            self.move_here = None
            self.killing = False

        # Pre-movements visual feedback
        if len(self.movement_validPositions) > 1 or len(self.kill_validPositions) > 0:
            for valid_mov_RECT in self.movement_validPositions.values():
                pygame.draw.rect(self.screen,'GREEN',valid_mov_RECT,width=2)
        for valid_kill_RECT in self.kill_validPositions.values():
            pygame.draw.rect(self.screen,'RED',valid_kill_RECT,width=2)

    '''targetKing_allPositions necesita actualización continua, la cual
    se accionará/revisará-si-corresponde luego de realizar un movimiento
    
    qué cosas cambian?

    _allPositions puede cambiar si el rey se mueve, o si una casilla
    aledaña se desocupa.

    si _allPositions cambia, es probable que _checkPositions también lo haga,
    pero cuándo lo sabremos/evaluaremos?
        Esto está relacionado con movimientos-inválidos.

    Previo a un movimiento: conocer mis movimientos-inválidos
    Luego de un movimiento: actualizar _allPositions
                            actualizar contraste _checkPositions
                                decidir cosas...
        
    Para checkear y re-checkear esto debemos llamar a los _targets() "al aire",
    sin capturar su retorno, las cuales internamente imprimirán los valores 
    targetPositions -EN LA NUEVA Y ACTUALIZADA _ALLPOSITIONS.

    Debemos usar get_king_movements, es precisamente la actualización
    de _allPositions

    '''

    def get_piece_standpoint(self,color:str,piece:str) -> list[int]:
        '''Argumentar pieza exactamente igual que en pieces.origins'''
        act_posLIST: list[int] #grupo de piezas
        if color == 'Black':
            for k,v in self.black_positions.items():
                if v == piece:
                    act_posLIST.append(k)
        if color == 'White':
            for k,v in self.white_positions.items():
                if v == piece:
                    act_posLIST.append(k)
        return act_posLIST
    
    def get_king_movements(self, target_color:str) -> list[int]:
        '''Extrayendo sólo posiciones de movimiento del rey target desde
        king_targets().'''
        _current_king_pos: int = self.get_piece_standpoint(color=target_color,piece="Rey").pop()
        move_positions, _ = self.king_targets(_current_king_pos) #descartamos el retorno de on_target_kill_positions
        return list(move_positions.keys()) #king_targets() ya consideró bloqueos.

    def decide_check(self):
        '''
        Evaluar posiciones _allPositions, _checkPositions y invalid-movements
        para resolver estados jaque/jaque-mate. (self.turnTarget_checkState)

        ::RESUELVE:-> "jaque"
            -Si encontró que el target king puede escapar (invalid pos NO-IGUALA a valid pos).
            -O si encontró que el king no puede escapar PERO puede ser salvado por un aliado.
                (MATANDO AMENAZA o TAPANDO CAMINO) -> dos "tipos" de SALVAR? salvar = SQUARE_TYPE
            
        ::RESUELVE:-> "jaque-mate"
            Si encontró que el target king NO puede escapar (posiciones válidas son las mismas que las inválidas)
                Este procedimiento va despues de almacenar perfectamente las posiciones inválidas *actuales*
        
        **Debo resumir B_check_state y W_check_state en self.turnTarget_checkState
        '''
        if len(self.targetcolor_kingCheckPos) == 0: # nada que hacer
            return

        elif self.targetcolor_kingAllPositions == self.targetcolor_kingCheckPos: #revisar si hay MISMOS-ELEMENTOS
            if self.targetcolor_kingCheckPos in self.saving_positions:
                #target está en jaque
                self.turnTarget_checkState == 'jaque'
            else:
                #target está en jaque mate
                self.turnTarget_checkState == 'jaque-mate'
            return
        
        if len(self.targetcolor_kingAllPositions) - len(self.targetcolor_kingCheckPos)  > 0: #<- este caso NUNCA ES JAQUE-MATE
            # ^^ si esta diferencia existe es jaque, lo único que me compete aquí es declarar 
            #    estados check para ver si el juego o sucede otra acción.
            self.turnTarget_checkState == 'jaque'
            return

    def update_valid_movements(self):
        '''
        Resuelve *quién* y *cómo* puede moverse.

        Los movimientos denegados deducidos serán registrados en los correspondientes
        diccionarios *de color* sin contar al rey que tiene el suyo:
        >>self.white_invalid_positions = {'peon': [2,4], 'alfil': [12,18,24]}

        Creo que no todos los movimientos invalidos corresponden, teóricamente, a la misma categoría,
        pero debemos definir si se evaluan en el mismo lugar y al mismo tiempo.
        > INVALID_MOV_T1: Tu rey (rey de self.turnColor) esta en jaque, solo podrás moverte si eso quita
            su estado de jaque.
            Requiere que primero evaluemos el jaque. -> POST-JAQUE_INVALID
        > INVALID_MOV_T2: Tu rey no esta en jaque, pero *el movimiento que querés hacer* lo deja en jaque. 
            No requiere evaluar previamente el jaque? Pero y si lo sabemos de antemano y ya? -> PRE-JAQUE_INVALID

        Ayuda aliada: un aliado puede interceptar/matar la amenaza
                    > Cómo saber si un movimiento corta una amenaza?
                        SI *este movimiento* elimina kill-movement crítico al rey...

                    > Cómo saber si nuestro movimiento dejaría atrás una amenaza(a nuestro rey)?
                        SI *este movimiento* deja atrás un kill-movement DIRECTO al rey...
                        ^^^ esta evaluación "corresponde" a decide_check(), pero es EVALUADA
                            cada vez que querramos mover una pieza.
                    
                    Hay dos tipos de movimientos inválidos? O es todo parte de lo mismo?
                    Un tipo de "movimiento inválido" es -> sólo podes salvar a tu rey
                    Otro tipo de "movimiento inválido" es -> ese mov. expone a tu rey
                    Pero se evalúan de igual forma y al mismo tiempo? se agrupan en el mismo dict?
        '''
        ...

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
        if self.winner:
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
