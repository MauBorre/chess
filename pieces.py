origins: dict[str,dict[str,list[int]]] = { #Legible pero no ideal para render
    'black': {
        'rook':[0,7],
        'horse':[1,6],
        'bishop':[2,5],
        'queen':[3],
        'king':[4],
        'pawn':[8,9,10,11,12,13,14,15]
        },
    'white': {
        'rook':[63,56],
        'horse':[62,57],
        'bishop':[61,58],
        'queen':[59],
        'king':[60],
        'pawn':[55,54,53,52,51,50,49,48]
        }
    }

def reverse_expand_origins(
    pieces_legible_origins: dict[str,dict[str,list[int]]]
    ) -> dict[int,str]:
    '''Transforma dict={'color...': {'pawn':[0,1,2]}}
    En color-A_dict={0:pawn,1:pawn,2:pawn}
        color-B_dict={0:pawn,1:pawn,2:pawn}

    Uno es fácil de leer para nosotros, el otro es fácil
    de leer para el sistema.'''
    _black_positions: dict[int, str] = {}
    _white_positions: dict[int, str] = {}
    dict_list: list[dict[int, str]] = []
    for color in pieces_legible_origins.keys():
        key_val_reverse = []
        aux_d={}
        for piece in pieces_legible_origins[color].keys():
            key_val_reverse.append({num:piece for num in pieces_legible_origins[color][piece]})
        for d in key_val_reverse:
            aux_d.update(d)
        dict_list.append(aux_d)
    _black_positions, _white_positions = dict_list #unpack from list
    return _black_positions, _white_positions #SIEMPRE se debe devolver en esta posición

black_positions, white_positions = reverse_expand_origins(origins)
