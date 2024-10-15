origins: dict[str,dict[str,list[int]]] = { #Legible pero no ideal para render
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

def reverse_expand_origins(
    pieces_legible_origins: dict[str,dict[str,list[int]]]
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
    _black_positions, _white_positions = dict_list #unpack from list
    return _black_positions, _white_positions #SIEMPRE se debe devolver en esta posición

black_positions, white_positions = reverse_expand_origins(origins)
