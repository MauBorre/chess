import pygame
from typing import Union
#estos obj servirían por ahora como keys de configuración, pero servirían para algo mas?
from entities import Peon, Alfil, Caballo, Torre, Reina, Rey 
from entities import NORTE, NOR_ESTE, NOR_OESTE, SUR, SUR_OESTE, SUR_ESTE, ESTE, OESTE
'''Movimiento de piezas:
Las piezas pueden moverse de tres modos:
    > ADELANTE
    > ATRAS
    > IZQUIERDA
    > DERECHA
    > DIAGONAL
Definidos como:
    > NORTE = -8
    > NORESTE = -8+1
    > NOROESTE = -8-1
    > SUR = +8
    > SUROESTE = +8-1
    > SURESTE = +8+1
    > ESTE = +1
    > OESTE = -1
'''

class Scene:
    def __init__(self,master):
        self.master = master
        self.screen = self.master.screen

    def draw_text(self,text,color,x,y,center=True,font_size='large'):
        font = self.master.large_font if font_size=='large' else self.master.medium_font
        # font = pygame.font.Font(None,font_size)
        surface = self.master.screen
        textobj = font.render(text,1,color)
        text_width = textobj.get_width()
        text_height = textobj.get_height()
        textrect = textobj.get_rect()
        if center: textrect.topleft = (x - text_width/2, y - text_height/2) # points placement at center
        else: textrect.topleft = (x,y)
        surface.blit(textobj,textrect)

class MainMenuSCENE(Scene):
    '''> Escena MAIN_MENU

    Comienza con una pequeña animación
        imagen se mueve, frena repentinamente y se le pide 
        al jugador que presione una tecla cualquiera para 
        iniciar todo el resto.
            Esto tiene realmente una utilidad?
        Aguardará una señal de mostrar escena main_menu
            esta señal contiene instrucciones

    +) contiene:
        1 gran objeto *menu*
            nueva partida
                j1 vs j2 | j1 vs IA
                    modos de tiempo, modos de dificultad

            reglas
                reglas del juego...?

            opciones
                resolución
                    400x800
                    600x800
                    1280x920
                audio
                    Volumen
            salir
        Aguardará una señal de comenzar partida
            esta señal contiene instrucciones'''

    def __init__(self,master):
        super().__init__(master)
        self.view = 'main'

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
                self.master.match_mode = 'j1 vs j2'
                self.master.scene_manager = MatchSCENE

        # J1 VS IA MODE
        self.draw_text('J1 vs IA','white',50,200,center=False)
        j1_vs_ia_rect = pygame.Rect(50,200,200,50)
        if j1_vs_ia_rect.collidepoint((self.master.mx,self.master.my)):
            # hover
            pygame.draw.rect(self.master.screen,(255,0,0),j1_vs_ia_rect,width=1)
            if self.master.click:
                self.master.match_mode = 'j1 vs ia'
                self.master.scene_manager = MatchSCENE

    def draw(self):
        #hud
        self.draw_text('Main menu scene','white',20,20,center=False)
        if self.view == 'main':
            self.draw_newMatch_btn()
            self.draw_exit_btn()
        if self.view == 'mode-selection':
            self.draw_match_modes()
        #if view == 'options':
            #MainMenuSCENE.draw_options()

class MatchSCENE(Scene):
    '''> Escena JUEGO
    Es inicializada bajo una 'comanda' por el modo j1vj2 o j1via seleccionado en el menú previo
    +) contiene:
        2 actores
            cada actor tiene un color y cada color
            corresponde a un color y un lado del tablero'''

    def __init__(self,master):
        super().__init__(master)
        # position utils
        self.midScreen = (self.screen.get_width()/2, self.screen.get_height()/2)
        self.midScreen_pos = pygame.Vector2(self.midScreen)

        # board config
        self.square_width = 88
        self.square_height = self.square_width
        self.board_rows = 8
        self.board_columns = self.board_rows
        self.nested_rows = self.make_nested_rows(self.board_rows) # Fijar rows ayuda a validar movimientos.
        self.board_width = self.square_width * self.board_rows
        self.board_height = self.board_width
        self.board_begin = pygame.Vector2((self.midScreen_pos.x - self.board_width/2,
                                           self.midScreen_pos.y - self.board_height/2))
        self.boardRects: list[pygame.Rect] = self.make_boardRects()
        
        # board defaults
        self.pieces_legible_initial_positions: dict[dict[str,list[int]]] = { # forma no ideal para render, pero sí para leer
            'negras': {
                'Torre':[0,7],
                'Caballo':[1,6],
                'Alfil':[2,5],
                'Reina':[3],
                'Rey':[4],
                'Peón':[8,9,10,11,12,13,14,15]
                },
            'blancas': {
                'Torre':[63,56],
                'Caballo':[62,57],
                'Alfil':[61,58],
                'Reina':[59],
                'Rey':[60],
                'Peón':[55,54,53,52,51,50,49,48]
                }
            }
        self.in_base_Bpawns: list[int] = []
        self.in_base_Wpawns: list[int] = []
        self.black_positions: dict[int,str] = {}
        self.white_positions: dict[int,str] = {}
        self.make_board()

        self.movement_validPositions: dict[int, pygame.Rect] = {} 
        self.kill_validPositions: dict[int, pygame.Rect] = {}

        # Movimientos que no pueden realizarse porque exponen al rey a un kill-movement, o que --> DOS TIPOS DE INVALID
        # no lo salvan en caso de estar el rey ya expuesto a un kill-movement. ------------------> MOV. DISTINTOS?
        # Algunas piezas no podrán moverse en absoluto, otras podrán moverse parcialmente.
        #
        # Estos conjuntos son actualizados luego de mover una pieza (si corresponde).
        # Son tambien revisados en cada movimiento de pieza. -> Expone rey // No-salva rey
        self.white_invalid_positions: dict[str, list[int]] = {} # {'peon': [2,4], 'alfil': [12,18,24]}
        self.black_invalid_positions: dict[str, list[int]] = {}
        
        # Necesitamos saber si el rey y/o sus casillas de moviemiento
        # están en un casillero kill-position (incl. posición actual)
        # si todas las intenciones de movimiento de king
        # se encuentran en estas posiciones: entonces JAQUE-MATE
        self.Wking_check_positions: list[int] = []
        self.Bking_check_positions: list[int] = []

        self.W_check_state: str #jaque o jaque-mate o None
        self.B_check_state: str #jaque o jaque-mate o None

        self.move_here: int | None = None

        self.turn_attacker: str = 'White'
        self.turn_target: str = 'Black'
        self.winner: bool = False
        self.player_deciding_match = False
        self.killing: bool = False
        
    def make_board(self): # also used for restarting match
        self.in_base_Bpawns: list[int] = [bpawn for bpawn in self.pieces_legible_initial_positions['negras']['Peón']]
        self.in_base_Wpawns: list[int] = [wpawn for wpawn in self.pieces_legible_initial_positions['blancas']['Peón']]
        self.black_positions, self.white_positions = self.reverse_expand_team_positions(self.pieces_legible_initial_positions)
        self.turn_attacker: str = 'White'
        self.winner: bool = False

    def turn_swap(self):
        if self.turn_attacker == 'White':
            self.turn_attacker = 'Black'
            self.turn_target = 'White'
            return
        if self.turn_attacker == 'Black':
            self.turn_attacker = 'White'
            self.turn_target = 'Black'
            return

    def make_nested_rows(self,row_count: int) -> list[list[int]]:
        _rows = []
        for i in range(row_count):
            start = i*row_count
            end = start+row_count
            _rows.append(list(range(start,end)))
        return _rows

    def reverse_expand_team_positions(
        self,
        pieces_legible_origins: dict[dict[str,list[int]]]
        ) -> dict[int,str]:
        '''Transforma dict={'color...': {'peon':[0,1,2]}}
        En color-A_dict={0:peon,1:peon,2:peon}
           color-B_dict={0:peon,1:peon,2:peon}

        Uno es fácil de leer para nosotros, el otro es fácil
        de leer para el sistema.'''
        _black_positions, _white_positions = {}, {}
        dict_list = []
        for color in pieces_legible_origins.keys():
            key_val_reverse = []
            aux_d={}
            for piece in pieces_legible_origins[color].keys():
                key_val_reverse.append({num:piece for num in pieces_legible_origins[color][piece]})
            for d in key_val_reverse:
                aux_d.update(d)
            dict_list.append(aux_d)
        _black_positions, _white_positions = dict_list
        #SIEMPRE se debe devolver en esta posición, no es muy inseguro esto?
        return _black_positions, _white_positions

    def row_of_(self, position: int) -> list[int]:
        '''Devuelve el row al que corresponda la posición ingresada.
        
        '''
        for row in self.nested_rows:
            for num in row:
                if num == position:
                    return row
        else: return []
    
    def pawn_targets(
        self,
        piece_standpoint: int,
        sq_rect: pygame.Rect,
        clicked_piece_color: str
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
        mov_target_positions: dict[int,pygame.Rect] = {piece_standpoint:sq_rect} # standpoint is always first pos 
        on_target_kill_positions: dict[int,pygame.Rect] = {}
        kill_positions: list[int] = []
        if clicked_piece_color == 'Black': #target: white | turn associated evaluation
            
            # SUR
            movement: int = piece_standpoint+SUR

            if movement not in self.black_invalid_positions['peon']: ... # !! REPETIR ESTO EN CADA PIEZA !! CUIDADO COLOR !!

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
            if piece_standpoint+OESTE not in self.row_of_(piece_standpoint):
                kill_positions.append(piece_standpoint+SUR_ESTE)
            if piece_standpoint+ESTE not in self.row_of_(piece_standpoint):
                kill_positions.append(piece_standpoint+SUR_OESTE)
            elif len(kill_positions) == 0:
                kill_positions.extend([piece_standpoint+SUR_OESTE, piece_standpoint+SUR_ESTE])
            for kp in kill_positions:
                if kp in self.white_positions:
                    on_target_kill_positions.update({kp:self.boardRects[kp]})

        if clicked_piece_color == 'White': #target: black
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
            if piece_standpoint+OESTE not in self.row_of_(piece_standpoint):
                kill_positions.append(piece_standpoint+NOR_ESTE)
            if piece_standpoint+ESTE not in self.row_of_(piece_standpoint):
                kill_positions.append(piece_standpoint+NOR_OESTE)
            elif len(kill_positions) == 0:
                kill_positions.extend([piece_standpoint+NOR_OESTE, piece_standpoint+NOR_ESTE])
            for kp in kill_positions:
                if kp in self.black_positions:
                    on_target_kill_positions.update({kp:self.boardRects[kp]})

        return mov_target_positions, on_target_kill_positions

    def tower_targets(
        self,
        piece_standpoint: int,
        sq_rect: pygame.Rect,
        clicked_piece_color: str
        ) -> dict[int,pygame.Rect]:
        '''Movimiento Torre:
        +NORTE
        +SUR
        +ESTE
        +OESTE 
        "recursivo" hasta limite tablero o pieza aliada/enemiga.
        La torre mata como se mueve.
        '''
        mov_target_positions: dict[int,pygame.Rect] = {piece_standpoint:sq_rect} # standpoint is always first pos
        on_target_kill_positions: dict[int,pygame.Rect] = {}
        tower_directions = [NORTE,SUR,ESTE,OESTE]

        for direction in tower_directions:
            for mult in range(1,8): # 1 to board size
                movement = piece_standpoint+direction*mult
                if direction == ESTE or direction == OESTE:
                    if movement not in self.row_of_(piece_standpoint):
                        break
                if 0 <= movement <= 63:
                    if movement not in self.black_positions and movement not in self.white_positions:
                        mov_target_positions.update({movement:self.boardRects[movement]})
                    else:
                        if clicked_piece_color == 'Black':
                            if movement in self.white_positions:
                                on_target_kill_positions.update({movement:self.boardRects[movement]})
                                break
                        if clicked_piece_color == 'White':
                            if movement in self.black_positions:
                                on_target_kill_positions.update({movement:self.boardRects[movement]})
                                break
                        break #previene propagación mas allá del primer bloqueo - rompe el mult
        return mov_target_positions, on_target_kill_positions

    def horse_targets(
        self,
        piece_standpoint: int,
        sq_rect: pygame.Rect,
        clicked_piece_color: str
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
        mov_target_positions: dict[int,pygame.Rect] = {piece_standpoint:sq_rect} # standpoint is always first pos
        on_target_kill_positions: dict[int,pygame.Rect] = {}
        horse_movements = []
        # ESTE / OESTE LIMITS
        if piece_standpoint+ESTE in self.row_of_(piece_standpoint):
            horse_movements.extend([piece_standpoint+NORTE+NOR_ESTE,
                                    piece_standpoint+SUR+SUR_ESTE])
            if piece_standpoint+ESTE*2 in self.row_of_(piece_standpoint):
                horse_movements.extend([piece_standpoint+ESTE+NOR_ESTE,
                                        piece_standpoint+ESTE+SUR_ESTE])
        if piece_standpoint+OESTE in self.row_of_(piece_standpoint):
            horse_movements.extend([piece_standpoint+NORTE+NOR_OESTE,
                                    piece_standpoint+SUR+SUR_OESTE])
            if piece_standpoint+OESTE*2 in self.row_of_(piece_standpoint):
                horse_movements.extend([piece_standpoint+OESTE+NOR_OESTE,
                                        piece_standpoint+OESTE+SUR_OESTE])
        
        for movement in horse_movements:
            if 0 <= movement <= 63: # NORTE/SUR LIMIT
                if movement not in self.black_positions and movement not in self.white_positions:
                    mov_target_positions.update({movement:self.boardRects[movement]})
                else:
                    if clicked_piece_color == 'Black':
                        if movement in self.white_positions: #if movement in white_positions
                            on_target_kill_positions.update({movement:self.boardRects[movement]})
                    if clicked_piece_color == 'White':
                        if movement in self.black_positions:
                            on_target_kill_positions.update({movement:self.boardRects[movement]})
        return mov_target_positions, on_target_kill_positions

    def bishop_targets(
        self,
        piece_standpoint: int,
        sq_rect: pygame.Rect,
        clicked_piece_color: str
        ) -> dict[int,pygame.Rect]:
        '''Movimiento Alfil:
        +NOR_OESTE
        +NOR_ESTE
        +SUR_OESTE
        +SUR_ESTE
        "recursivo" hasta limite tablero o pieza aliada/enemiga
        '''
        mov_target_positions: dict[int,pygame.Rect] = {piece_standpoint:sq_rect} # standpoint is always first pos
        on_target_kill_positions: dict[int,pygame.Rect] = {}
        bishop_directions = [NOR_OESTE,NOR_ESTE,SUR_OESTE,SUR_ESTE]
        for direction in bishop_directions:
            for mult in range(1,8):
                movement = piece_standpoint+direction*mult
                if direction == NOR_ESTE or direction == NOR_OESTE:
                    if movement not in self.row_of_(piece_standpoint+NORTE*mult):
                        break
                if direction == SUR_ESTE or direction == SUR_OESTE:
                    if movement not in self.row_of_(piece_standpoint+SUR*mult):
                        break
                if 0 <= movement <= 63:
                    if movement not in self.black_positions and movement not in self.white_positions:
                        mov_target_positions.update({movement:self.boardRects[movement]})
                    else:
                        if clicked_piece_color == 'Black':
                            if movement in self.white_positions:
                                on_target_kill_positions.update({movement:self.boardRects[movement]})
                                break
                        if clicked_piece_color == 'White':
                            if movement in self.black_positions:
                                on_target_kill_positions.update({movement:self.boardRects[movement]})
                                break
                        break #previene propagación mas allá del primer bloqueo - rompe el mult
        return mov_target_positions, on_target_kill_positions

    def king_targets(
        self,
        piece_standpoint: int,
        sq_rect: pygame.Rect,
        clicked_piece_color: str
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
        mov_target_positions: dict[int,pygame.Rect] = {piece_standpoint:sq_rect} # standpoint is always first pos
        on_target_kill_positions: dict[int,pygame.Rect] = {}
        king_directions = [NORTE,SUR,ESTE,OESTE,NOR_OESTE,NOR_ESTE,SUR_OESTE,SUR_ESTE]
        for direction in king_directions:
            movement = piece_standpoint+direction
            if direction == ESTE or direction == OESTE:
                if movement not in self.row_of_(piece_standpoint):     
                    continue
            if direction == NOR_ESTE or direction == NOR_OESTE:
                if movement-NORTE not in self.row_of_(piece_standpoint):
                    continue
            if direction == SUR_ESTE or direction == SUR_OESTE:
                if movement-SUR not in self.row_of_(piece_standpoint):
                    continue
            if 0 <= movement <= 63:
                if movement not in self.black_positions and movement not in self.white_positions:
                    mov_target_positions.update({movement:self.boardRects[movement]}) 
                else:
                    if clicked_piece_color == 'Black':
                        if movement in self.white_positions:
                            on_target_kill_positions.update({movement:self.boardRects[movement]})
                    if clicked_piece_color == 'White':
                        if movement in self.black_positions:
                            on_target_kill_positions.update({movement:self.boardRects[movement]})
                    continue
        return mov_target_positions, on_target_kill_positions

    def queen_targets(
        self,
        piece_standpoint: int,
        sq_rect: pygame.Rect,
        clicked_piece_color: str
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
        mov_target_positions: dict[int,pygame.Rect] = {piece_standpoint:sq_rect} # standpoint is always first pos
        on_target_kill_positions: dict[int,pygame.Rect] = {}
        queen_directions = [NORTE,SUR,ESTE,OESTE,NOR_OESTE,NOR_ESTE,SUR_OESTE,SUR_ESTE]
        for direction in queen_directions:
            for mult in range(1,8):
                movement = piece_standpoint+direction*mult
                if direction == ESTE or direction == OESTE:
                    if movement not in self.row_of_(piece_standpoint):     
                        break
                if direction == NOR_ESTE or direction == NOR_OESTE:
                    if movement not in self.row_of_(piece_standpoint+NORTE*mult):
                        break
                if direction == SUR_ESTE or direction == SUR_OESTE:
                    if movement not in self.row_of_(piece_standpoint+SUR*mult):
                        break
                if 0 <= movement <= 63:
                    if movement not in self.black_positions and movement not in self.white_positions:
                        mov_target_positions.update({movement:self.boardRects[movement]}) 
                    else:
                        if clicked_piece_color == 'Black':
                            if movement in self.white_positions:
                                on_target_kill_positions.update({movement:self.boardRects[movement]})
                                break
                        if clicked_piece_color == 'White':
                            if movement in self.black_positions:
                                on_target_kill_positions.update({movement:self.boardRects[movement]})
                                break
                        break #previene propagación mas allá del primer bloqueo - rompe el mult
        return mov_target_positions, on_target_kill_positions

    def draw_board(self):

        # main board frame
        pygame.draw.rect(self.screen,(200,200,200),
                    pygame.Rect(self.board_begin.x,self.board_begin.y,
                                self.board_width,self.board_height),width=3)

        for board_index, SQUARE_RECT in enumerate(self.boardRects): #celdas que sirven por posición, índice y medida.

            # individual grid frame
            pygame.draw.rect(self.screen,(200,200,200),SQUARE_RECT,width=1)
            self.draw_text(f'{board_index}',(150,150,150),
                           SQUARE_RECT.left +3,
                           SQUARE_RECT.top + self.square_height -17,
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
                    self.draw_text(SQUARE_TYPE,'black', SQUARE_RECT.left + self.square_width/2,
                                                        SQUARE_RECT.top + self.square_height/2)
                if interacted_PColor == 'White':
                    self.draw_text(SQUARE_TYPE,(120,120,120),
                                                      SQUARE_RECT.left + self.square_width/2,
                                                      SQUARE_RECT.top + self.square_height/2)

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
                                    self.movement_validPositions, self.kill_validPositions = self.pawn_targets(board_index,
                                                                                                               SQUARE_RECT,
                                                                                                               interacted_PColor)

                            if SQUARE_TYPE == 'Torre':
                                self.movement_validPositions.clear()
                                if interacted_PColor == self.turn_attacker:
                                    self.movement_validPositions, self.kill_validPositions = self.tower_targets(board_index, SQUARE_RECT, interacted_PColor)
                            
                            if SQUARE_TYPE == 'Caballo':
                                self.movement_validPositions.clear()
                                if interacted_PColor == self.turn_attacker:
                                    self.movement_validPositions, self.kill_validPositions = self.horse_targets(board_index, SQUARE_RECT, interacted_PColor)
                        
                            if SQUARE_TYPE == 'Alfil':
                                self.movement_validPositions.clear()
                                if interacted_PColor == self.turn_attacker:
                                    self.movement_validPositions, self.kill_validPositions = self.bishop_targets(board_index, SQUARE_RECT, interacted_PColor)

                            if SQUARE_TYPE == 'Rey':
                                self.movement_validPositions.clear()
                                if interacted_PColor == self.turn_attacker:
                                    self.movement_validPositions, self.kill_validPositions = self.king_targets(board_index, SQUARE_RECT, interacted_PColor)

                            if SQUARE_TYPE == 'Reina':
                                self.movement_validPositions.clear()
                                if interacted_PColor == self.turn_attacker:
                                    self.movement_validPositions, self.kill_validPositions = self.queen_targets(board_index, SQUARE_RECT, interacted_PColor)
                                
                            if SQUARE_TYPE == "EMPTY":
                                self.movement_validPositions.clear()

        # updating element's positions and game relevant state if a movement/kill was stated
        if self.move_here != None:
            ex_value: int = list(self.movement_validPositions.items())[0][0]

            if self.turn_attacker == 'Black': # target:white
                _piece = self.black_positions.pop(ex_value)
                if self.killing:
                    self.white_positions.pop(self.move_here)
                self.black_positions.update({self.move_here:_piece})


                '''revisando jaque/jaque-mate al otro jugador''' 
                self.W_check_state = self.decide_check(target=self.turn_target) # piezas black contra king white

                #actualizando posiciones_inválidas del otro jugador
                if self.W_check_state == 'jaque': ...
                    # >> alertar al jugador <<
                    #limitar posiciones de target
                    #self.white_invalid.update(posición_deducida)

                if self.W_check_state == 'jaque-mate':
                    self.winner = True # automaticamente repercutirá draw() - 29/09 NO TESTEADA                

            if self.turn_attacker == 'White':
                _piece = self.white_positions.pop(ex_value)
                if self.killing:
                    self.black_positions.pop(self.move_here) 
                self.white_positions.update({self.move_here:_piece})

            self.turn_swap()
            self.movement_validPositions.clear()
            self.move_here = None
            self.killing = False

        # Pre-movements visual display
        if len(self.movement_validPositions) > 1 or len(self.kill_validPositions) > 0:
            for valid_mov_RECT in self.movement_validPositions.values():
                pygame.draw.rect(self.screen,'GREEN',valid_mov_RECT,width=2)
        for valid_kill_RECT in self.kill_validPositions.values():
            pygame.draw.rect(self.screen,'RED',valid_kill_RECT,width=2)

    def get_king_standpoint(self,color:str) -> int:
        '''Devuelve la posición actual del rey'''
        act_pos: int
        if color == 'Black':
            for k,v in self.black_positions.items():
                if v == 'Rey':
                    act_pos = k
        if color == 'White':
            for k,v in self.white_positions.items():
                if v == 'Rey':
                    act_pos = k
        return act_pos
    
    def get_king_movements(self, target_color:str) -> list[int]:
        '''
        Para obtener las posiciones debemos repetir parte de la misma
        acción que ya está hecha en king_targets().

        La diferencia radica en que aquella función fue pensada para
        utilizarse cuando se clickea una pieza (incl. pygame.Rect), no 
        a un nivel mas fundamental del sistema.

        En favor de revisar los jaques, solo necesitamos una lista de
        ints que correspondan a las posiciones del TARGET-rey.
        '''
        _current_king_pos: int = self.get_king_standpoint(target_color) # a partir de acá computar movements
        move_positions: list[int] = []

        if target_color == 'Black':
            #revisar límites de tablero, colisiones, etc.
            move_positions = self.king_targets()[0] #requiere square_rect y
                                                    #acá realmente eso no nos importa
        if target_color == 'White': ...
        return move_positions

    def decide_check(self, target: str) -> str:
        '''deducir jaque/jaque-mate de piezas self.turn_color contra target

        comparar las on_target_kill_positions de self.turn
        contra la posicion actual+movimientos del rey target.

        Para hacer esto debemos llamar a todas las funciones "...targets()" antes
        usadas, pero "usándolas de otra forma". -> cuidado que todas estas funciones usan
                                                   pygame.Rect...

        Puede que haya una interesante interacción invirtiendo el hecho de que
        son las piezas buscando al rey, haciendo que sea el rey quien busca a las
        piezas. -> Excelente opción? Sólo con obtener los posibles movimientos del
        rey podría deducir esto, sin llamar a todos los targets(), pero sí con una
        correcta revision categórica de "qué" pieza estoy tocando y si su movimiento
        "me puede comer"

        
        ::devuelve:-> "jaque" si encontró que el target king puede escapar
            -> repercutirá fuera de esta función mermando el movimiento del target

        ::devuelve:-> "jaque-mate" si encontró que el target king NO puede escapar
            -> repercutirá fuera de esta función finalizando la partida
        '''
        
        target_king_movements: int = self.get_king_movements(target) #movimientos de TARGET

        #lista o dict?:
        on_target_kill_positions: dict = {} #si la cantidad de elementos aqui es la misma
                                            #que en target_king_movements entonces es jaque-mate
        if self.turn_attacker == 'Black': # target: white
            #revisar qué piezas black dejan en kill-position a rey white
            '''if movement == _current_king_pos'''
            '''if movement in _king_mov_pos'''
            #pawn_targets(rey_standpoint,'black')
            #tower_targets(rey_standpoint,'black')
            #horse_targets(rey_standpoint,'black')
            #bishop_targets(rey_standpoint,'black')
            ...

        if self.turn_attacker == 'White': # target: black
            #revisar que piezas white dejan en kill-position a rey black
            #pawn_targets(rey_standpoint,'white')
            #tower_targets(rey_standpoint,'white')
            #horse_targets(rey_standpoint,'white')
            #bishop_targets(rey_standpoint,'white')            
            ...

        if len(target_king_movements) > len(on_target_kill_positions):
            # El rey puede escapar por si solo a la posición que no coincida
            # debemos obtener esta posición de escape para NO-NEGARLA de las 
            # posiciones inválidas en jaque
            return 'jaque'
        if len(target_king_movements) == len(on_target_kill_positions):
            # !! puede aún tener escapatoria si ayuda un aliado !!
            '''Ayuda aliada: un aliado puede interceptar/matar la amenaza
            > Cómo saber si un movimiento corta una amenaza?
            > Cómo saber si nuestro movimiento dejaría atrás una amenaza(a nuestro rey)?'''
            return 'jaque-mate'

    def draw(self):
        #hud
        self.draw_text('Match scene','black',20,20,center=False)
        self.draw_text(f'{self.master.match_mode}','black',200,20,center=False)
        self.draw_board()
        self.draw_text(self.turn_attacker,'black',self.midScreen_pos.x - 25, self.board_height+70,center=False)
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
                self.make_board()
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
                self.master.scene_manager = MainMenuSCENE

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

    def make_boardRects(self) -> list[pygame.Rect]:
        _boardRects = []
        startx = self.board_begin.x
        starty = self.board_begin.y
        y = starty
        for r in range(self.board_rows):
            x = startx
            for c in range(self.board_columns):
                rect = pygame.Rect(x,y,self.square_width,self.square_height)
                _boardRects.append(rect)
                x+=self.square_width
            y+=self.square_height
        return _boardRects
