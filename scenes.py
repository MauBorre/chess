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
    '''Match es inicializado bajo instrucciones seleccionadas previamente en MainMenu:
        >> j1-VS-j2
        >> j1-VS-ia
        >> con/sin tiempo (duraciones variables de reloj)
    '''

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
        self.in_base_Bpawns: list[int] = [bpawn for bpawn in pieces.origins['negras']['Peón']] # no swap
        self.black_positions: dict[int, str] = pieces.black_positions
        self.black_threatOnWhite: dict[str, int] = {piece:[] for piece in pieces.origins['negras']} # {'peon': [1,2,3], 'alfil': [4,5,6]}
        self.black_kingLegalMoves: list[int] = []
        self.black_singleOriginDirectThreat: bool | None = None 
        self.black_directThreatTrace: list[int] = [] 
        
        # White
        self.in_base_Wpawns: list[int] = [wpawn for wpawn in pieces.origins['blancas']['Peón']] # no swap

        self.white_positions: dict[int, str] = pieces.white_positions
        self.white_threatOnBlack: dict[str, int] = {piece:[] for piece in pieces.origins['blancas']} # {'peon': [1,2,3], 'alfil': [4,5,6]}
        self.white_kingLegalMoves: list[int] = []
        self.white_singleOriginDirectThreat: bool | None = None 
        self.white_directThreatTrace: list[int] = [] 

        # Turn lookups --------------------------------------------------------------------------------
        self.turn_attacker: str = 'White'
        self.turn_defender: str = 'Black'

        '''Si existe múltiple orígen de amenaza NUNCA habrá legalMoves por parte.
        de las piezas defensoras.'''
        self.defender_legalMoves: set[str] = {} # NO se considera en SWAP

        '''Registro de AMENAZAS, MOVIMIENTOS LEGALES DEL REY, POSICIONES DE RESCATE: 

        >> ThreatOn attacker/defender
            kill-movement's *del enemigo* que caen en casillero rey TARGET o adyacencias legales.
            Puede ser DIRECTO (jaque) o INDIRECTO (restringe kingLegalMoves).

            ANTES DE MOVER:
                El atacante debe revisar, dentro de sus movimientos posible, si su movimiento -expone al rey-
                por defender_threatOnAttacker.

            DESPUES DE MOVER:
                El defensor debe revisar -si su movimiento expone- por threat del atacante, evaluando así
                "con qué posibilidades de movimiento quedó" por attacker_threatOnDefender.
            
            El threat puede MATARSE o BLOQUEARSE
                A menos que haya más de un orígen de amenaza DIRECTA -> solo el rey moviendose puede escapar

            Threat de bishop, queen y tower pueden bloquearse
            Threat de pawn y horse no pueden bloquearse

        >> Color-King-legalMovements
            Posición actual + posibles movimientos (bloqueos aliados / casilleros threat).

        >> defender_legalMoves (kingSupport):
            Actualizadas luego de que movió el atacante.
            Exhibe "si alguien puede hacer algo", mas no "dónde".

            Para fabricarlas correctamente, debemos comprobar y desestimar
                - Movimientos inv. por bloqueo.
                - Movimientos inv.  por exposición al rey.
            
            Al comprobarlas, debo inspeccionar primero si hay jaque (singular o multiple)
            ya que esto limita seriamente las posibilidades de legalMoves (kingSupport).
        '''
        # Defender
        self.defender_positions: dict[int, str] = self.black_positions 
        self.defender_threatOnAttacker: dict[str, list[int]] = self.black_threatOnWhite  # será siempre resultado de SWAP, contiene *posible jaque* actual.
        self.defender_kingLegalMoves: list[int] = self.black_kingLegalMoves
        self.defender_singleOriginDirectThreat: bool | None = self.black_singleOriginDirectThreat
        self.defender_directThreatTrace: list[int] = self.black_directThreatTrace
        
        # Attacker
        self.attacker_positions: dict[int, str] = self.white_positions 
        self.attacker_threatOnDefender: dict[str, list[int]] = self.white_threatOnBlack
        self.attacker_kingLegalMoves: list[int] = self.white_kingLegalMoves
        self.attacker_singleOriginDirectThreat: bool | None = self.white_singleOriginDirectThreat 
        self.attacker_directThreatTrace: list[int] = self.white_directThreatTrace

    def update_turn_objectives(self):
        '''Llama todas las funciones _objectives() con sus correctas perspectivas
        del turno en juego.

        Internamente se revisará:

            >> attacker_threatOnDefender
            >> attacker_kingLegalMoves
            >> attacker_singleOriginDirectThreat

            >> defender_threatOnAttacker
            >> defender_kingLegalMoves
            >> defender_singleOriginDirectThreat
            
            >> defender_legalMoves
        
        Antes de ser utilizadas, estas variables (excepto defender_threatOnAttacker que puede contener
        información del *jaque actual* y es resultado de transferencia/SWAP ) deben limpiarse para evitar
        un solapamiento infinito de posiciones.
        
        Primero debemos actualizar la ofensiva -siendo restringido por la defensiva-, y luego la defensiva,
        revisando especialmente si puede salvar a su rey de ser necesario por la última jugada ofensiva.

        singleOriginDirectThreat será siempre y unicamente calculado luego de evaluar la ofensiva,
        Si es NONE no hay ninguna amenaza directa, pero si es FALSE significa que HAY MULTIPLES AMENAZAS
        DIRECTAS, por lo tanto el rey depende de su propio movimiento (o será jaque-mate).

        DEBO revisar defender_threatOnAttacker en perspectivas ofensivas de piezas,
        y, si llego a su llamada y singleOriginDirectThreat es TRUE, DEBO revisar SELF.DIRECT_THREATS .
        
        Al terminar estos cálculos, la funcion decide_check() establecerá si la partida debe continuar o
        terminarse con algún veredicto.
        
        Desde perspectiva = 'attacker' es importante:
            >> Atender que si existe defender_singleOriginDirectThreat (jaque), solo puedo moverme/atacar si
                eso salva a mi rey. 
                -> if self.defender_singleOriginDirectThreat == True
                   
            >> Aunque no exista jaque, debo revisar TAMBIEN si "salirme del casillero" -moviendome o matando-
               expone a mi rey a un jaque.
               -> self.try_movement_doesnt_expose_attacker_king(movement)

            >> Actualizaremos self.attacker_threatOnDefender
               -> kill-movements aún no hechos pero que "amenazan" al rey defender
        
        Desde perspectiva = 'defender' es importante:

            >> Verificar y validar LEGAL-MOVES, teniendo en cuenta exposiciones al rey y bloqueos
            con otras piezas.

            >> Atender el estado de attacker_singleOriginDirectThreat (jaque) y revisar la posibilidad de
               que las piezas bloqueen / maten a la pieza amenazante.
               
        '''

        self.attacker_threatOnDefender.clear()
        # self.defender_threatOnAttacker será siempre resultado de SWAP, contiene *posible jaque* actual.
        self.attacker_kingLegalMoves.clear()
        self.defender_kingLegalMoves.clear()
        self.defender_legalMoves.clear()
        self.attacker_directThreatTrace.clear()


        # Attacker ----------------------------------------------------------------------------------------
        if self.defender_singleOriginDirectThreat != False:
            pawn_standpoints: list[int] = self.get_piece_standpoint(color=self.turn_attacker,piece="Peón")
            for _pawn in pawn_standpoints:
                self.pawn_objectives(_pawn, perspective='attacker')

            rook_standpoints: list[int] = self.get_piece_standpoint(color=self.turn_attacker,piece="Torre")
            for _rook in rook_standpoints:
                self.rook_objectives(_rook, perspective='attacker')

            bishop_standpoints: list[int] = self.get_piece_standpoint(color=self.turn_attacker,piece="Alfil")
            for _bishop in bishop_standpoints:
                self.bishop_objectives(_bishop, perspective='attacker')

            horse_standpoints: list[int] = self.get_piece_standpoint(color=self.turn_attacker, piece="Caballo")
            for _horse in horse_standpoints:
                self.horse_objectives(_horse, perspective='attacker')

            queen_standpoint: int = self.get_piece_standpoint(color=self.turn_attacker, piece="Reina").pop()
            self.queen_objectives(queen_standpoint, perspective='attacker')
        # --------------------------------------------------------------------------------------------------

        # Defender -----------------------------------------------------------------------------------------
        king_standpoint: int = self.get_piece_standpoint(color=self.turn_defender, piece="Rey").pop()
        self.king_objectives(king_standpoint,perspective='defender') # genero/reviso defender_kingLegalMoves.

        for _threats_list in self.attacker_threatOnDefender.values():
            if king_standpoint in _threats_list:
                if self.attacker_singleOriginDirectThreat == True: # Solo resulta True si conecta una vez
                    self.attacker_singleOriginDirectThreat == False # False es el caso multiple origen
                else:
                    self.attacker_singleOriginDirectThreat = True
                    self.attacker_directThreatTrace = _threats_list # direct_threats solo puede contener una lista.
            else: self.attacker_singleOriginDirectThreat = None

        if self.attacker_singleOriginDirectThreat != False:

            # Defender kingSupport (Actualizan movimientos legales del defensor para ver si perdió o empató)
            pawn_standpoints = self.get_piece_standpoint(color=self.turn_defender, piece='Peón')
            for _pawn in pawn_standpoints:
                self.pawn_objectives(_pawn, perspective='defender')

            rook_standpoints = self.get_piece_standpoint(color=self.turn_defender, piece="Torre")
            for _rook in rook_standpoints:
                self.rook_objectives(_rook, perspective='defender')
            
            bishop_standpoints = self.get_piece_standpoint(color=self.turn_defender, piece='Alfil')
            for _bishop in bishop_standpoints:
                self.bishop_objectives(_bishop, perspective='defender')
            
            horse_standpoints = self.get_piece_standpoint(color=self.turn_defender, piece="Caballo")
            for _horse in horse_standpoints:
                self.horse_objectives(_horse, perspective='defender')
            
            queen_standpoint = self.get_piece_standpoint(color=self.turn_defender, piece="Reina").pop()
            self.queen_objectives(queen_standpoint, perspective='defender')
        # -------------------------------------------------------------------------------------------------

    def reset_board(self):

        '''Idealmente esta funcion reiniciaria el objeto match por completo.
        A menos que necesitemos obtener un puntaje por ejemplo, simplemente llamando
        al init deberiamos reiniciar TODo
        
        Creo que *lo ideal* es que Match exponga una API que utilizará el GameMaster
        para realizar cosas como estas... quizás...'''
        # self.__init__(master=self.master)

        # judge variables
        self.winner = False
        self.stalemate = False
        self.match_state = ''
        self.player_deciding_match = False

        # Board defaults ---------------------------------------------------------------------------
        self.boardRects: list[pygame.Rect] = board.make_rects(self.board_begin)

        # Black
        self.in_base_Bpawns = [bpawn for bpawn in pieces.origins['negras']['Peón']]
        self.black_positions: dict[int, str] = pieces.black_positions
        self.black_threatOnWhite: dict[str, int] = {piece:[] for piece in pieces.origins['negras']}
        self.black_kingLegalMoves: list[int] = []
        self.black_singleOriginDirectThreat: bool | None = None 
        self.black_directThreatTrace: list[int] = []

        # White
        self.in_base_Wpawns: list[int] = [wpawn for wpawn in pieces.origins['blancas']['Peón']]
        self.white_positions: dict[int, str] = pieces.white_positions
        self.white_threatOnBlack: dict[str, int] = {piece:[] for piece in pieces.origins['blancas']} 
        self.white_kingLegalMoves: list[int] = []
        self.white_singleOriginDirectThreat: bool | None = None 
        self.white_directThreatTrace: list[int] = [] 
    
        # Turn lookups ------------------------------------------------------------------------------
        # General
        self.turn_attacker: str = 'White'
        self.turn_defender: str = 'Black'
        self.defender_legalMoves: set[str] = {}

        # Defender
        self.defender_positions: dict[int, str] = self.black_positions 
        self.defender_threatOnAttacker: dict[str, list[int]] = self.black_threatOnWhite 
        self.defender_kingLegalMoves: list[int] = self.black_kingLegalMoves
        self.defender_singleOriginDirectThreat: bool | None = self.black_singleOriginDirectThreat
        self.defender_directThreatTrace: list[int] = self.black_directThreatTrace 
        
        # Attacker
        self.attacker_positions: dict[int, str] = self.white_positions 
        self.attacker_threatOnDefender: dict[str, list[int]] = self.white_threatOnBlack
        self.attacker_kingLegalMoves: list[int] = self.white_kingLegalMoves
        self.attacker_singleOriginDirectThreat: bool | None = self.white_singleOriginDirectThreat 
        self.attacker_directThreatTrace: list[int] = self.white_directThreatTrace 

    def turn_swap(self):
        '''
        En todo swap computamos 5 variables
        >> positions
        >> threatOn
        >> kingLegalMoves
        >> singleOriginDirectThreat
        >> directThreatTrace
        
        Match aplicará cambios siempre sobre conjuntos "generalizados" attacker/defender,
        entonces luego de realizados:

        PRIMERO los volveremos a adjudicar a su variable de color-origen. "COMO ERAN"

        LUEGO los intercambiamos por el color-equipo que corresponde. "COMO RESULTAN AHORA"
        '''

        if self.turn_attacker == 'White':

            self.turn_attacker = 'Black'
            self.turn_defender = 'White'

            # Target Transfer (white <- attacker | black <- defender) -----------------
            # > positions
            self.white_positions = self.attacker_positions
            self.black_positions = self.defender_positions

            # > threatOn
            self.white_threatOnBlack = self.attacker_threatOnDefender
            self.black_threatOnWhite = self.defender_threatOnAttacker

            # > kingLegalMoves
            self.white_kingLegalMoves = self.attacker_kingLegalMoves
            self.black_kingLegalMoves = self.defender_kingLegalMoves

            # > singleOriginDirectThreat
            self.white_singleOriginDirectThreat = self.attacker_singleOriginDirectThreat
            self.black_singleOriginDirectThreat = self.defender_singleOriginDirectThreat

            # > directThreatTrace
            self.white_directThreatTrace = self.attacker_directThreatTrace
            self.black_directThreatTrace = self.defender_directThreatTrace

            # Target Swap (attacker = black | defender = white ) ---------------------------
            # > positions
            self.attacker_positions = self.black_positions
            self.defender_positions = self.white_positions

            # > threatOn
            self.attacker_threatOnDefender = self.black_threatOnWhite
            self.defender_threatOnAttacker = self.white_threatOnBlack

            # > kingLegalMoves
            self.attacker_kingLegalMoves = self.black_kingLegalMoves
            self.defender_kingLegalMoves = self.white_kingLegalMoves

            # > singleOriginDirectThreat
            self.attacker_singleOriginDirectThreat = self.black_singleOriginDirectThreat
            self.defender_singleOriginDirectThreat = self.white_singleOriginDirectThreat

            # > directThreatTrace
            self.attacker_directThreatTrace = self.black_directThreatTrace
            self.defender_directThreatTrace = self.white_directThreatTrace

            return
        
        if self.turn_attacker == 'Black':

            self.turn_attacker = 'White'
            self.turn_defender = 'Black'

            # Target Transfer (white <- defender | black <- attacker) -----------------
            # > positions
            self.white_positions = self.defender_positions
            self.black_positions = self.attacker_positions

            # > threatOn
            self.white_threatOnBlack = self.defender_threatOnAttacker
            self.black_threatOnWhite = self.attacker_threatOnDefender

            # > kingLegalMoves
            self.white_kingLegalMoves = self.defender_kingLegalMoves
            self.black_kingLegalMoves = self.attacker_kingLegalMoves

            # > singleOriginDirectThreat
            self.white_singleOriginDirectThreat = self.defender_singleOriginDirectThreat
            self.black_singleOriginDirectThreat = self.attacker_singleOriginDirectThreat

            # > directThreatTrace
            self.white_directThreatTrace = self.defender_directThreatTrace
            self.black_directThreatTrace = self.attacker_directThreatTrace

            # Target Swap (attacker = white | defender = black) ---------------------
            # > positions
            self.attacker_positions = self.white_positions
            self.defender_positions = self.black_positions

            # > threatOn
            self.attacker_threatOnDefender = self.white_threatOnBlack
            self.defender_threatOnAttacker = self.black_threatOnWhite

            # > kingLegalMoves
            self.attacker_kingLegalMoves = self.white_kingLegalMoves
            self.defender_kingLegalMoves = self.black_kingLegalMoves

            # > singleOriginDirectThreat
            self.attacker_singleOriginDirectThreat = self.white_singleOriginDirectThreat
            self.defender_singleOriginDirectThreat = self.black_singleOriginDirectThreat

            # > directThreatTrace
            self.attacker_directThreatTrace = self.white_directThreatTrace
            self.defender_directThreatTrace = self.black_directThreatTrace

            return
    
    def exposing_direction(self, standpoint: int, direction: int, request_from: str) -> bool:
        '''Para verificar si un movimiento expone al rey aliado necesito "falsificar" 
        un movimiento contra el conjunto de piezas que corresponda.
        >> falsificar defenderMov contra attacker
        >> falsificar attackerMov contra defender

        Llamaremos a las piezas correspondientes en la :perspectiva: correspondiente:
        "fake-attackerMov-toDef"
        "fake-defenderMov-toAtt"
        E inyectandoles posiciones falsas de "quien consulta".

        Esta perspectiva devolverá:
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
            for ap in self.attacker_positions.keys():
                if standpoint != ap:
                    fake_positions.update({ap: self.attacker_positions[ap]})
                else:
                    fake_positions.update({fake_move: self.attacker_positions[ap]})
            
            # Revisar objetivos inyectando fake_positions.
            rook_standpoints: list[int] = self.get_piece_standpoint(color=self.turn_defender,piece="Torre")
            for _rook in rook_standpoints:
                if self.rook_objectives(_rook, perspective='fake-attackerMov-toDef', fake_positions=fake_positions):
                    return True

            bishop_standpoints: list[int] = self.get_piece_standpoint(color=self.turn_defender,piece="Alfil")
            for _bishop in bishop_standpoints:
                if self.bishop_objectives(_bishop, perspective='fake-attackerMov-toDef', fake_pos=fake_positions):
                    return True

            queen_standpoint: int = self.get_piece_standpoint(color=self.turn_defender, piece="Reina").pop()
            if self.queen_objectives(queen_standpoint, perspective='fake-attackerMov-toDef', fake_pos=fake_positions):
                return True
            return False

        if request_from == 'defender':
            for ap in self.defender_positions.keys():
                if standpoint != ap:
                    fake_positions.update({ap: self.defender_positions[ap]})
                else:
                    fake_positions.update({fake_move: self.defender_positions[ap]})

            # Revisar objetivos inyectando fake_positions.
            rook_standpoints: list[int] = self.get_piece_standpoint(color=self.turn_attacker,piece="Torre")
            for _rook in rook_standpoints:
                if self.rook_objectives(_rook, perspective='fake-deffenderMov-toAtt', fake_positions=fake_positions):
                    return True

            bishop_standpoints: list[int] = self.get_piece_standpoint(color=self.turn_attacker,piece="Alfil")
            for _bishop in bishop_standpoints:
                if self.bishop_objectives(_bishop, perspective='fake-deffenderMov-toAtt', fake_pos=fake_positions):
                    return True

            queen_standpoint: int = self.get_piece_standpoint(color=self.turn_attacker, piece="Reina").pop()
            if self.queen_objectives(queen_standpoint, perspective='fake-deffenderMov-toAtt', fake_pos=fake_positions):
                return True
            return False

    def pawn_objectives(self,piece_standpoint: int, perspective: str) -> dict[int,pygame.Rect] | None:
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
        kill_positions: list[int] = []
        movement: int

        if perspective == 'defender' :
            if self.turn_defender == 'Black': # defiende hacia el SUR
            
                # 1st Movement -BLOCK saving position-
                movement = piece_standpoint+SUR
                if movement <= 63: # board limit

                    '''
                    Este puede ser un movimiento legal y ya, no se si debo
                    revisar que "bloquee" tan asi.
                    O quizas si...
                    '''
                    if movement in self.attacker_directThreatTrace:
                        self.defender_legalMoves.add('Peón')

                # 2nd Movement -BLOCK saving position-
                if piece_standpoint in self.in_base_Bpawns:
                    if movement+SUR in self.attacker_directThreatTrace:
                        self.defender_legalMoves.add('Peón')

                # KILL saving positions
                # Verificamos que el movimiento no rompa los límites del tablero
                if piece_standpoint+OESTE not in row_of_(piece_standpoint):
                    kill_positions.append(piece_standpoint+SUR_ESTE)
                if piece_standpoint+ESTE not in row_of_(piece_standpoint):
                    kill_positions.append(piece_standpoint+SUR_OESTE)
                elif len(kill_positions) == 0:
                    kill_positions.extend([piece_standpoint+SUR_OESTE, piece_standpoint+SUR_ESTE])

                for kp in kill_positions:
                    if kp == max(self.attacker_directThreatTrace) or kp == min(self.attacker_directThreatTrace):
                        self.defender_legalMoves.add('Peón')

            if self.turn_defender == 'White': # defiende hacia el NORTE

                # 1st Movement -BLOCK saving position-
                movement = piece_standpoint+NORTE
                if movement <= 63: # board limit
                    if movement in self.attacker_directThreatTrace:
                        self.defender_legalMoves.add('Peón')

                # 2nd Movement -BLOCK saving position-
                if piece_standpoint in self.in_base_Bpawns:
                        if movement+NORTE in self.attacker_directThreatTrace:
                            self.defender_legalMoves.add('Peón')

                # KILL saving positions
                # Verificamos que el movimiento no rompa los límites del tablero
                if piece_standpoint+OESTE not in row_of_(piece_standpoint):
                    kill_positions.append(piece_standpoint+NOR_ESTE)
                if piece_standpoint+ESTE not in row_of_(piece_standpoint):
                    kill_positions.append(piece_standpoint+NOR_OESTE)
                elif len(kill_positions) == 0:
                    kill_positions.extend([piece_standpoint+NOR_OESTE, piece_standpoint+NOR_ESTE])

                for kp in kill_positions:
                    if kp == max(self.attacker_directThreatTrace) or kp == min(self.attacker_directThreatTrace):
                        self.defender_legalMoves.add('Peón')
            return

        if perspective == 'attacker':
            if self.turn_attacker == 'Black': # Ataca hacia el SUR
                # 1st Movement
                movement = piece_standpoint+SUR
                if movement <= 63: # board limit
    
                    if self.defender_singleOriginDirectThreat:
                        '''Entonces mis únicos movimientos posibles son bloquear o matar la amenaza.
                        > Bloquear una amenaza es movement coincidente en defender_directThreatTrace
                        > Matar la amenaza es kill-movement coincidente en min o max de defender_directThreatTrace'''
                        if movement not in self.defender_directThreatTrace:
                            #probamos con el 2do mov
                            if piece_standpoint in self.in_base_Bpawns:
                                if movement+SUR not in self.defender_directThreatTrace:
                                    #probamos con kill-positions

                                    # Verificamos que el movimiento no rompa los límites del tablero
                                    if piece_standpoint+OESTE not in row_of_(piece_standpoint):
                                        kill_positions.append(piece_standpoint+SUR_ESTE)
                                    if piece_standpoint+ESTE not in row_of_(piece_standpoint):
                                        kill_positions.append(piece_standpoint+SUR_OESTE)
                                    elif len(kill_positions) == 0:
                                        kill_positions.extend([piece_standpoint+SUR_OESTE, piece_standpoint+SUR_ESTE])
                                    
                                    for kp in kill_positions:
                                        if kp in self.white_positions: 
                                            if kp == max(self.defender_directThreatTrace) or kp == min(self.defender_directThreatTrace):
                                                on_target_kill_positions.update({kp: self.boardRects[kp]})
                                    else: # no puedo matar ni bloquear, todos los movimientos invalidados.
                                        return {}, {}
                                elif movement+SUR != max(self.defender_directThreatTrace) or movement+SUR != min(self.defender_directThreatTrace):
                                    # BLOCK saving position
                                    mov_target_positions.update({movement+SUR: self.boardRects[movement+SUR]})
                        elif movement != max(self.defender_directThreatTrace) or movement != min(self.defender_directThreatTrace):
                            # BLOCK saving position
                            mov_target_positions.update({movement: self.boardRects[movement]})
                    else:
                        if not self.exposing_direction(piece_standpoint, direction=SUR): 
                            if movement not in self.black_positions and movement not in self.white_positions: # piece block
                                if piece_standpoint in self.in_base_Bpawns:
                                    mov_target_positions.update({movement:self.boardRects[movement]})

                                    # 2nd Movement 
                                    if movement+SUR <= 63: # board limit check
                                        if movement+SUR not in self.black_positions and movement+SUR not in self.white_positions: # piece block
                                            mov_target_positions.update({movement+SUR:self.boardRects[movement+SUR]})
                                else:
                                    mov_target_positions.update({movement:self.boardRects[movement]})
                        else: pass

                        # kill positions
                        # Verificamos que el movimiento no rompa los límites del tablero
                        if piece_standpoint+OESTE not in row_of_(piece_standpoint):

                            if not self.exposing_direction(piece_standpoint, direction=SUR_ESTE):
                                kill_positions.append(piece_standpoint+SUR_ESTE)
                            else: pass

                        if piece_standpoint+ESTE not in row_of_(piece_standpoint):

                            if not self.exposing_direction(piece_standpoint, direction=SUR_OESTE):
                                kill_positions.append(piece_standpoint+SUR_OESTE)
                            else: pass

                        elif len(kill_positions) == 0:

                            if not self.exposing_direction(piece_standpoint, direction=SUR_OESTE):
                                kill_positions.append(piece_standpoint+SUR_OESTE)
                            else: pass

                            if not self.exposing_direction(piece_standpoint, direction=SUR_ESTE):
                                kill_positions.append(piece_standpoint+SUR_ESTE)
                            else: pass

                        for kp in kill_positions:

                            if kp in self.white_positions: #<- turn defender
                                on_target_kill_positions.update({kp:self.boardRects[kp]})
                            
                            # Threat on defender king ------------------------
                            if kp in self.defender_kingLegalMoves:
                                self.attacker_threatOnDefender['Peón'].append(kp)
                            # ------------------------------------------------

            if self.turn_attacker == 'White': # Ataca hacia el NORTE
                # 1st Movement
                movement = piece_standpoint+NORTE
                if movement >= 0: # board limit
                    
                    if self.defender_singleOriginDirectThreat:
                        '''Entonces mis únicos movimientos posibles son bloquear o matar la amenaza.
                        > Bloquear una amenaza es movement coincidente en defender_directThreatTrace
                        > Matar la amenaza es kill-movement coincidente en min o max de defender_directThreatTrace'''
                        if movement not in self.defender_directThreatTrace:
                            #probamos con el 2do mov
                            if piece_standpoint in self.in_base_Wpawns:
                                if movement+NORTE not in self.defender_directThreatTrace:
                                    #probamos con kill-positions

                                    # Verificamos que el movimiento no rompa los límites del tablero
                                    if piece_standpoint+OESTE not in row_of_(piece_standpoint):
                                        kill_positions.append(piece_standpoint+NOR_ESTE)
                                    if piece_standpoint+ESTE not in row_of_(piece_standpoint):
                                        kill_positions.append(piece_standpoint+NOR_OESTE)
                                    elif len(kill_positions) == 0:
                                        kill_positions.extend([piece_standpoint+NOR_OESTE, piece_standpoint+NOR_ESTE])
                                    
                                    for kp in kill_positions:
                                        if kp in self.black_positions:
                                            if kp == max(self.defender_directThreatTrace) or kp == min(self.defender_directThreatTrace):
                                                on_target_kill_positions.update({kp: self.boardRects[kp]})
                                    else: # no puedo matar ni bloquear, todos los movimientos invalidados.
                                        return {}, {}
                                elif movement+NORTE != max(self.defender_directThreatTrace) or movement+NORTE != min(self.defender_directThreatTrace):
                                    # BLOCK 2nd mov. saving position
                                    mov_target_positions.update({movement+NORTE: self.boardRects[movement+NORTE]})
                        elif movement != max(self.defender_directThreatTrace) or movement != min(self.defender_directThreatTrace):
                            # BLOCK 1st mov. saving position
                            mov_target_positions.update({movement: self.boardRects[movement]})
                    else:
                        if not self.exposing_direction(piece_standpoint, direction=NORTE):
                            if movement not in self.black_positions and movement not in self.white_positions: # piece block
                                if piece_standpoint in self.in_base_Wpawns:
                                    mov_target_positions.update({movement:self.boardRects[movement]})

                                    # 2nd Movement
                                    if movement+NORTE >= 0: # board limit check
                                        if movement+NORTE not in self.black_positions and movement+NORTE not in self.white_positions: # piece block
                                            mov_target_positions.update({movement+NORTE:self.boardRects[movement+NORTE]})
                                else:
                                    mov_target_positions.update({movement:self.boardRects[movement]})
                        else: pass
                    
                        # kill positions
                        # Verificamos que el movimiento no rompa los límites del tablero
                        if piece_standpoint+OESTE not in row_of_(piece_standpoint):
                            
                            if not self.exposing_direction(piece_standpoint, direction=NOR_ESTE):
                                kill_positions.append(piece_standpoint+NOR_ESTE)
                            else: pass

                        if piece_standpoint+ESTE not in row_of_(piece_standpoint):
                            
                            if not self.exposing_direction(piece_standpoint, direction=NOR_OESTE):
                                kill_positions.append(piece_standpoint+NOR_OESTE)
                            else: pass

                        elif len(kill_positions) == 0:
                            
                            if not self.exposing_direction(piece_standpoint, direction=NOR_OESTE):
                                kill_positions.append(piece_standpoint+NOR_OESTE)
                            else: pass

                            if not self.exposing_direction(piece_standpoint, direction=NOR_ESTE):
                                kill_positions.append(piece_standpoint+NOR_ESTE)
                            else: pass

                        for kp in kill_positions:
                                            
                            if kp in self.black_positions: #<- turn defender
                                on_target_kill_positions.update({kp:self.boardRects[kp]})

                            # Threat on defender king ------------------------
                            if kp in self.defender_kingLegalMoves:
                                self.attacker_threatOnDefender['Peón'].append(kp)
                            # ------------------------------------------------

            return mov_target_positions, on_target_kill_positions

    def rook_objectives(
        self,
        piece_standpoint: int,
        perspective: str,
        fake_positions: dict[str, list[int]] | None = None
        ) -> dict[int,pygame.Rect] | None:
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
        _can_support: bool = False
        tower_directions = [NORTE,SUR,ESTE,OESTE]

        if perspective == 'fake-defenderMov-toAtt':
            for direction in tower_directions:
                    for mult in range(1,8): # 1 to board_size
                        movement = piece_standpoint+direction*mult
                        if direction == ESTE or direction == OESTE:
                            if movement not in row_of_(piece_standpoint):
                                break
                        if 0 <= movement <= 63: # VALID SQUARE

                            # Revisar bloqueos

                            # Des-estimar kill-movements que NO sean al rey

                            # Si encontramos al rey, devolver TRUE
                            ...
            return False

        if perspective == 'fake-attackerMov-toDef':
            for direction in tower_directions:
                    for mult in range(1,8): # 1 to board_size
                        movement = piece_standpoint+direction*mult
                        if direction == ESTE or direction == OESTE:
                            if movement not in row_of_(piece_standpoint):
                                break
                        if 0 <= movement <= 63: # VALID SQUARE

                            # Revisar bloqueos
                            if movement in self.attacker_positions:
                                break 

                            # Des-estimar kill-movements que NO sean al rey
                            if movement in self.defender_positions:
                                break

                            # Si encontramos al rey, devolver TRUE
                            elif movement in fake_positions:
                                if fake_positions[movement] == 'Rey':
                                    return True
            return False
        
        if perspective == 'defender':
            for direction in tower_directions:
                for mult in range(1,8): # 1 to board_size
                    movement = piece_standpoint+direction*mult
                    if direction == ESTE or direction == OESTE:
                        if movement not in row_of_(piece_standpoint):
                            break
                    if 0 <= movement <= 63: # VALID SQUARE

                        if self.attacker_singleOriginDirectThreat == True:
                            if movement in self.attacker_directThreatTrace:
                                # Puede que esté matando o bloqueando pero ambas opciones nos bastan.
                                self.defender_legalMoves.add('Torre') 
                                return
                            else: continue
                        elif self.attacker_singleOriginDirectThreat == None:

                            # revisiones normales de movimiento
                            '''Con encontrar al menos uno sería suficiente, pero si luego queremos
                            responder visualmente en el tablero necesitaremos todos, además de pasarlo
                            a su version dict con un pygame.Rect.
                            '''

                            # no-expositivos al jaque
                            '''Necesito una nueva forma de perspectiva EN exposing_movement? porque lo estaba
                            usando solo en perspective="attacker" para SU rey pero ahora necesito checkear otro
                            conjunto de piezas.'''

                            # bloqueos <- creo que esto es primordial
                            # ...

                            # kill-movements
                            # ...
                            ...
            return

        if perspective == 'attacker': 
            if self.defender_singleOriginDirectThreat:
                '''Entonces mis únicos movimientos posibles son bloquear o matar la amenaza.
                > Bloquear una amenaza es movement coincidente en defender_directThreatTrace
                > Matar la amenaza es kill-movement coincidente en min o max de defender_directThreatTrace'''
                for direction in tower_directions:
                    for mult in range(1,8): # 1 to board_size
                        movement = piece_standpoint+direction*mult
                        if direction == ESTE or direction == OESTE:
                            if movement not in row_of_(piece_standpoint):
                                break
                        if 0 <= movement <= 63: # VALID SQUARE
                            if movement in self.defender_directThreatTrace:
                                if movement not in self.defender_positions:

                                    # BLOCK saving position.
                                    _can_support = True
                                    mov_target_positions.update({movement: self.boardRects[movement]})

                                    #attacker legal move?

                                elif movement == max(self.defender_directThreatTrace) or movement == min(self.defender_directThreatTrace):

                                    # KILL saving position.
                                    _can_support = True
                                    on_target_kill_positions.update({movement: self.boardRects[movement]})

                                    #attacker legal move?

                            else: continue        
                if not _can_support:
                    return {}, {}
            else:
                for direction in tower_directions:
                    for mult in range(1,8): # 1 to board_size
                        movement = piece_standpoint+direction*mult
                        if direction == ESTE or direction == OESTE:
                            if movement not in row_of_(piece_standpoint):
                                break
                        if 0 <= movement <= 63: # VALID SQUARE
                            
                            '''
                            BUG primero debo revisar el bloqueo antes de la exposición, de lo contrario
                            estamos comprobando contra un lugar que quizás no podemos visitar en un principio.
                            '''
                            if not self.exposing_direction(piece_standpoint, direction=direction):
                                if movement not in self.black_positions and movement not in self.white_positions:
                                    mov_target_positions.update({movement:self.boardRects[movement]})

                                    # Threat on defender king ------------------------
                                    _threat_emission.append(movement)
                                    if movement in self.defender_kingLegalMoves:
                                        # Entonces existe threat.
                                        # Luego de esto corresponde encontrar un STOP:
                                        # > king standpoint O  > ya-revisamos-todos-los-legalMoves
                                        _threatening = True

                                # Kill-movement
                                elif movement in self.defender_positions:
                                    
                                    # Threat STOP > king standpoint
                                    if _threatening and self.defender_positions[movement] == 'Rey':
                                        self.attacker_threatOnDefender['Torre'].append(_threat_emission)
                                        _threatening = False

                                    on_target_kill_positions.update({movement:self.boardRects[movement]})
                                    break
                                
                                # Threat STOP > ya-revisamos-todos-los-legalMoves
                                elif _threatening and movement not in self.defender_kingLegalMoves:
                                    self.attacker_threatOnDefender['Torre'].append(_threat_emission)
                                    _threatening = False

                                break # previene propagación mas allá del primer bloqueo - rompe el mult
                            else: break # rompe hasta la siguiente dirección.       
            return mov_target_positions, on_target_kill_positions

    def horse_objectives(self, piece_standpoint: int, perspective: str) -> dict[int,pygame.Rect] | None:
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
        _can_support: bool = False
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
        
        if perspective == 'defender':
            for movement in horse_movements:
                if 0 <= movement <= 63: # NORTE/SUR LIMIT

                    if movement in self.attacker_directThreatTrace:
                        self.defender_legalMoves.add('Caballo')
                        return
                    else: continue 
            return

        if perspective == 'attacker':
            if self.defender_singleOriginDirectThreat:
                '''Entonces mis únicos movimientos posibles son bloquear o matar la amenaza.
                > Bloquear una amenaza es movement coincidente en defender_directThreatTrace
                > Matar la amenaza es kill-movement coincidente en min o max de defender_directThreatTrace'''
                for movement in horse_movements:
                    if 0 <= movement <= 63: # NORTE/SUR LIMIT 
                        if movement in self.defender_directThreatTrace:
                            if movement not in self.defender_positions:

                                # BLOCK saving position.
                                _can_support = True
                                mov_target_positions.update({movement: self.boardRects[movement]})
                            elif movement == max(self.defender_directThreatTrace) or movement == min(self.black_directThreatTrace):

                                # KILL saving position.
                                _can_support = True
                                on_target_kill_positions.update({movement: self.boardRects[movement]})
                            else: continue
                if not _can_support:
                    return {}, {}
            else:
                for movement in horse_movements:
                    if 0 <= movement <= 63: # NORTE/SUR LIMIT 

                        '''Unica pieza la cual podemos descartar todos sus movimientos si uno solo expone.'''
                        if not self.exposing_direction(piece_standpoint, direction=movement):
                            # Threat on defender king ------------------------
                            if movement in self.defender_kingLegalMoves: 
                                self.attacker_threatOnDefender['Caballo'].append(movement)
                            # ------------------------------------------------

                            # Movement
                            if movement not in self.black_positions and movement not in self.white_positions:
                                mov_target_positions.update({movement:self.boardRects[movement]})
                            
                            # Kill-movement
                            elif movement in self.defender_positions:
                                on_target_kill_positions.update({movement:self.boardRects[movement]})
                        else: return {}, {}
                        
            return mov_target_positions, on_target_kill_positions

    def bishop_objectives(
        self,
        piece_standpoint: int,
        perspective: str,
        fake_pos: dict[str, list[int]] | None = None
        ) -> dict[int,pygame.Rect] | None:
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
        _can_support: bool = False
        bishop_directions = [NOR_OESTE,NOR_ESTE,SUR_OESTE,SUR_ESTE]

        if perspective == 'fake':
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
                        if movement in self.defender_positions:
                            break # recorrer otra posición
                        elif movement in fake_pos:
                            if fake_pos[movement] == 'Rey':
                                return True
            return False

        if perspective == 'defender':
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
                        
                        if movement in self.attacker_directThreatTrace:
                            self.defender_legalMoves.add('Alfil')
                            return
                        else: continue
            return

        if perspective == 'attacker':
            if self.defender_singleOriginDirectThreat:
                '''Entonces mis únicos movimientos posibles son bloquear o matar la amenaza.
                > Bloquear una amenaza es movement coincidente en defender_directThreatTrace
                > Matar la amenaza es kill-movement coincidente en min o max de defender_directThreatTrace'''
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
                            if movement in self.defender_directThreatTrace:
                                if movement not in self.defender_positions:

                                    # BLOCK saving position.
                                    _can_support = True
                                    mov_target_positions.update({movement: self.boardRects[movement]})
                                elif movement == max(self.defender_directThreatTrace) or movement == min(self.defender_directThreatTrace):

                                    # KILL saving position.
                                    _can_support = True
                                    on_target_kill_positions.update({movement: self.boardRects[movement]})
                            else: continue
                if not _can_support:
                    return {}, {}
            else:
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
                            
                            if not self.exposing_direction(piece_standpoint, direction=direction):
                                if movement not in self.black_positions and movement not in self.white_positions:
                                    mov_target_positions.update({movement:self.boardRects[movement]})

                                    # Threat on defender king ------------------------
                                    _threat_emission.append(movement)
                                    # King checks
                                    if movement in self.defender_kingLegalMoves:
                                        # Entonces existe threat.
                                        # Luego de esto corresponde encontrar un STOP:
                                        # > king standpoint O  > ya-revisamos-todos-los-legalMoves,
                                        _threatening = True

                                # Kill-movement
                                elif movement in self.defender_positions:
                                    
                                    # Threat STOP > king standpoint
                                    if _threatening and self.defender_positions[movement] == 'Rey':
                                        self.attacker_threatOnDefender['Alfil'].append(_threat_emission)
                                        _threatening = False

                                    on_target_kill_positions.update({movement:self.boardRects[movement]})
                                    break
                                
                                # Threat STOP > ya-revisamos-todos-los-legalMoves
                                elif _threatening and movement not in self.defender_kingLegalMoves:
                                    self.attacker_threatOnDefender['Alfil'].append(_threat_emission)
                                    _threatening = False

                                break # previene propagación mas allá del primer bloqueo - rompe el mult
                            else: break # rompe hasta la siguiente dirección.
            return mov_target_positions, on_target_kill_positions

    def queen_objectives(
        self,
        piece_standpoint: int,
        perspective: str,
        fake_pos: dict[str, list[int]] | None = None
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
            "recursivo" hasta limite tablero o pieza aliada/enemiga
            '''
        
            # Visual feedback utils
            mov_target_positions: dict[int,pygame.Rect] = {piece_standpoint:self.boardRects[piece_standpoint]} # standpoint is always first pos
            on_target_kill_positions: dict[int,pygame.Rect] = {}

            # Objectives
            _threat_emission: list[int] = []
            _threatening: bool = False
            _can_support: bool = False
            queen_directions = [NORTE,SUR,ESTE,OESTE,NOR_OESTE,NOR_ESTE,SUR_OESTE,SUR_ESTE]

            if perspective == 'fake':
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
                            if movement in self.defender_positions:
                                break # recorrer otra dirección.
                            elif movement in fake_pos:
                                if fake_pos[movement] == 'Rey':
                                    return True
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

                            if movement in self.attacker_directThreatTrace:
                                self.defender_legalMoves.add('Reina')
                                return
                            else: continue
                return
            
            if perspective == 'attacker':
                if self.defender_singleOriginDirectThreat:
                    '''Entonces mis únicos movimientos posibles son bloquear o matar la amenaza.
                    > Bloquear una amenaza es movement coincidente en defender_directThreatTrace
                    > Matar la amenaza es kill-movement coincidente en min o max de defender_directThreatTrace'''
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
                                if movement in self.defender_directThreatTrace:
                                    if movement not in self.defender_positions:

                                        # BLOCK saving position.
                                        _can_support = True
                                        mov_target_positions.update({movement: self.boardRects[movement]})
                                    elif movement == max(self.defender_directThreatTrace) or movement == min(self.defender_directThreatTrace):

                                        # KILL saving position.
                                        _can_support = True
                                        on_target_kill_positions.update({movement: self.boardRects[movement]})
                                    else: continue 
                    if not _can_support:
                        return {}, {}
                else:
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
                                
                                if not self.exposing_direction(piece_standpoint, direction=direction):
                                    # Movement
                                    if movement not in self.black_positions and movement not in self.white_positions:
                                        mov_target_positions.update({movement:self.boardRects[movement]}) 

                                        # Threat on defender king ------------------------
                                        _threat_emission.append(movement)
                                        if movement in self.defender_kingLegalMoves:
                                            # Entonces existe threat.
                                            # Luego de esto corresponde encontrar un STOP:
                                            # > king standpoint O  > ya-revisamos-todos-los-legalMoves
                                            _threatening = True

                                    # Kill-movement
                                    elif movement in self.defender_positions:
                                        
                                        # Threat STOP > king standpoint
                                        if _threatening and self.defender_positions[movement] == 'Rey':
                                            self.attacker_threatOnDefender['Reina'].append(_threat_emission)
                                            _threatening = False
                                        
                                        on_target_kill_positions.update({movement:self.boardRects[movement]})
                                        break
                                    
                                    # Threat STOP > ya-revisamos-todos-los-legalMoves
                                    elif _threatening and movement not in self.defender_kingLegalMoves:
                                        self.attacker_threatOnDefender['Reina'].append(_threat_emission)
                                        _threatening = False

                                    break # previene propagación mas allá del primer bloqueo - rompe el mult
                                else: break # rompe hasta la siguiente dirección.
                return mov_target_positions, on_target_kill_positions

    def king_objectives(self, piece_standpoint: int, perspective: str) -> dict[int,pygame.Rect]:
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

                if perspective == 'defender':
                    if movement not in self.defender_positions: # ally block
                        if movement not in self.attacker_kingLegalMoves: # Los reyes no pueden solapar sus posiciones
                            if movement not in self.attacker_threatOnDefender: # amenazas directas e indirectas
                                self.defender_kingLegalMoves.append(movement)
                
                if perspective == 'attacker':
                    if movement not in self.defender_threatOnAttacker:
                        if movement not in self.defender_kingLegalMoves:
                            if movement not in self.attacker_positions: # ally block
                                self.attacker_kingLegalMoves.append(movement)
                                mov_target_positions.update({movement:self.boardRects[movement]})
                            elif movement in self.defender_positions:
                                self.attacker_kingLegalMoves.append(movement)
                                on_target_kill_positions.update({movement:self.boardRects[movement]})

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

            # hidden/visible elements upon paused state (or finished_game state?)
            if not self.master.paused:#  and not self.winner or not self.stalemate ?
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
                                    self.pieceValidMovement_posDisplay, self.pieceValidKill_posDisplay = self.pawn_objectives(board_index, perspective='attacker')

                            if SQUARE_TYPE == 'Torre':
                                self.pieceValidMovement_posDisplay.clear()
                                if interacted_PColor == self.turn_attacker:
                                    self.pieceValidMovement_posDisplay, self.pieceValidKill_posDisplay = self.rook_objectives(board_index, perspective='attacker')
                            
                            if SQUARE_TYPE == 'Caballo':
                                self.pieceValidMovement_posDisplay.clear()
                                if interacted_PColor == self.turn_attacker:
                                    self.pieceValidMovement_posDisplay, self.pieceValidKill_posDisplay = self.horse_objectives(board_index, perspective='attacker')
                        
                            if SQUARE_TYPE == 'Alfil':
                                self.pieceValidMovement_posDisplay.clear()
                                if interacted_PColor == self.turn_attacker:
                                    self.pieceValidMovement_posDisplay, self.pieceValidKill_posDisplay = self.bishop_objectives(board_index, perspective='attacker')
                            
                            if SQUARE_TYPE == 'Reina':
                                self.pieceValidMovement_posDisplay.clear()
                                if interacted_PColor == self.turn_attacker:
                                    self.pieceValidMovement_posDisplay, self.pieceValidKill_posDisplay = self.queen_objectives(board_index, perspective='attacker')

                            if SQUARE_TYPE == 'Rey':
                                self.pieceValidMovement_posDisplay.clear()
                                if interacted_PColor == self.turn_attacker:
                                    self.pieceValidMovement_posDisplay, self.pieceValidKill_posDisplay = self.king_objectives(board_index,perspective='attacker')
                                
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

            # POST MOVIMIENTOS / ATAQUES ---------------------
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
        > Utilizar .pop() en piezas de posiciones singulares como Rey y Reina'''
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
        Evalua "cómo quedaron las piezas en el tablero despues del último movimiento"
        para resolver estados jaque/jaque-mate/stale-mate.
        Al momento de checkear este objetivo que tengo revisar el king DEFENSOR en jaque.

        JAQUE > El rey es apuntado directamente, PUEDE escapar moviendose o siendo
            salvado por pieza aliada (matando O bloqueando amenaza)

        JAQUE-MATE > El rey es apuntado directamente, NO PUEDE escapar moviendose ni
            siendo salvado por pieza aliada. 

        STALE-MATE > El rey no es apuntado directamente, pero no puede moverse ni
            ser salvado por pieza aliada. Estado de empate.        
        '''

        if self.attacker_singleOriginDirectThreat == None:
            if len(self.defender_kingLegalMoves) == 0 and len(self.defender_legalMoves) == 0:
                '''BUG hay algo más que debo verificar acá.

                El empate sucede cuando EL REY NO ESTÁ EN AMENAZA DIRECTA pero el defensor NO
                TIENE MOVIMIENTOS LEGALES (*o cualquier movimiento posible dejaría al rey
                expuesto a un JAQUE*).

                Además de los kingLegalMoves, todas sus otras piezas pueden tener o no
                movimientos legales, los cuales se basan en si MOVER-EXPONE AL REY, si
                están BLOQUEADAS (caso peón: bloqueado de frente y por aliados, resto de
                las piezas pueden estar bloqueadas por aliados).

                Es importar notar que en este estado, CUALQUIER movimiento del actual defensor,
                dejaría al rey en JAQUE.
                '''

                #STALE-MATE
                '''Termina el juego en empate.'''
                if self.turn_attacker == 'Black':
                    self.stalemate = True # repercute en render() - termina la partida
                    self.match_state = 'Rey White ahogado.  -  Empate.'

                if self.turn_attacker == 'White':
                    self.stalemate = True # repercute en render() - termina la partida
                    self.match_state = 'Rey Black ahogado.  -  Empate.'

            else: return # La partida continúa con normalidad.

        if self.attacker_singleOriginDirectThreat:
            if len(self.defender_kingLegalMoves) > 0 or len(self.defender_legalMoves) > 0:
                # JAQUE
                '''Esto requiere solo una notificación al jugador correspondiente.
                defender_color -> notificate CHECK (highlight possible solutions)'''
                ...
                if self.turn_attacker == 'Black':
                    self.match_state = 'White en jaque.'

                if self.turn_attacker == 'White':
                    self.match_state = 'Black en jaque.'

            elif len(self.defender_kingLegalMoves) == 0 and len(self.defender_legalMoves) == 0:

                #JAQUE-MATE
                '''Termina el juego con el actual atacante victorioso. -> Spawn OptionsMenu'''
                ...
                if self.turn_attacker == 'Black':
                    self.winner = True # automaticamente repercutirá draw() - 29/09 NO TESTEADA
                    self.match_state = 'Black gana.  -  White en jaque-mate.'

                if self.turn_attacker == 'White':
                    self.winner = True # automaticamente repercutirá draw() - 29/09 NO TESTEADA
                    self.match_state = 'White gana  -  Black en jaque-mate.'

        if self.attacker_singleOriginDirectThreat == False: # múltiple origen de amenaza.
            if len(self.defender_kingLegalMoves) == 0:

                #JAQUE-MATE
                '''Termina el juego con el actual atacante victorioso. -> Spawn OptionsMenu'''
                ...
                if self.turn_attacker == 'Black':
                    self.winner = True # repercute en render() - termina la partida
                    self.match_state = 'Black gana.  -  White en jaque-mate.'

                if self.turn_attacker == 'White':
                    self.winner = True # repercute en render() - termina la partida
                    self.match_state = 'White gana  -  Black en jaque-mate.'
            else:

                # JAQUE
                '''Notificar al jugador correspondiente.'''
                if self.turn_attacker == 'Black':
                    self.match_state = 'White en jaque.'
                    
                if self.turn_attacker == 'White':
                    self.match_state = 'Black en jaque.'

    def render(self):
        #hud
        self.draw_text('Match scene','black',20,20,center=False)
        self.draw_text(f'{self.match_mode['mode']}','black',200,20,center=False)
        self.draw_text(self.match_state, 'black', 400, 20, center=False)
        self.draw_board()
        self.draw_text(self.turn_attacker,'black',self.midScreen_pos.x - 25, board.height+70,center=False)
        if self.master.paused:
            if not self.player_deciding_match:
                self.draw_pause_menu()
            else:
                self.draw_confirm_restart_menu()
        if self.winner or self.stalemate:
            # self.master.paused = True
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
        self.draw_text(self.match_state, 'black', self.screen.get_width()-400, 150, center=False)
        self.draw_postgame_again_btn()
        self.draw_exit_to_mainMenu_btn()
        #opciones de cambiar equipo...
        #opciones de cambiar reglas...
        #opciones de cambiar dificultad(IA)...

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

    def draw_postgame_again_btn(self):
        self.draw_text('Jugar de nuevo', 'white', self.screen.get_width()-400,400,center=False)
        play_again_rect = pygame.Rect(self.screen.get_width()-400,400,200,50)
        if play_again_rect.collidepoint((self.master.mx, self.master.my)):
            #hover
            pygame.draw.rect(self.screen,(255,0,0),play_again_rect,width=1)
            if self.master.click:

                self.reset_board()

    def draw_play_again_btn(self):
        self.draw_text('Jugar de nuevo', 'white', self.screen.get_width()-400,400,center=False)
        play_again_rect = pygame.Rect(self.screen.get_width()-400,400,200,50)
        if play_again_rect.collidepoint((self.master.mx, self.master.my)):
            #hover
            pygame.draw.rect(self.screen,(255,0,0),play_again_rect,width=1)
            if self.master.click:
                self.player_deciding_match = True
                self.reset_board()
