from datetime import datetime
#import helper

def formatar_row_para_treeview_da_root(row, index_treeview, quantidade):
    descricao_item = row[2].upper()
    preco_unit = row[5]
    total = float(preco_unit) * float(quantidade)

    formated_row = [index_treeview, descricao_item, format_to_moeda(preco_unit), quantidade ,format_to_moeda(total)]
    
    return formated_row

def formatar_row_para_treeview_da_busca(row):
    formated_row = (row[0], row[1], row[2], row[3], format_to_moeda(row[4]), format_to_moeda(row[5]), row[6], row[8])
    formated_row = replace_through_a_list(formated_row, '', '-')
    formated_row = upper_through_a_list(formated_row)
    return formated_row

def formatar_row_para_treeview_clientes(row):
    formated_row = (row[0], row[1], row[3], row[2])
    formated_row = replace_through_a_list(formated_row, '', '-')
    formated_row = upper_through_a_list(formated_row)
    return (formated_row)

def format_to_moeda(x, moeda=''):
    x = format_to_float(x)
    x = f'{x:,.2f}'
    x = x.replace(",", "X").replace(".", ",").replace("X", ".")
    return f'{moeda}{x}'

def format_to_float(x):
    try:
        x = str(x).replace(',', '.')
        x = float(x)
        return x
    except:
        print('Erro na funcao format_to_float (valor retornado: 0)')
        return 0

def soma_num_lista(lista):
    total = 0
    for num in lista:
        total += format_to_float(num) 
    return total

def get_date():
    date = datetime.now().strftime('%Y-%m-%d')
    return date

def get_horario():
    horario = datetime.now().strftime('%H:%M:%S')
    return horario

def get_date_normal_shape():
    date = datetime.now().strftime('%d-%m-%Y')
    return date

def change_date_to_br_format(date):
    dia, mes, ano = date.split('-')
    
    
def zero_adder(n):
    n = int(n)
    try:
        if n > 9:
            return f'{n}'
        else:
            return f'0{n}'
    except:
        print(f'Ocorreu um erro na função Zero_adder em helper.py. Retornando {n}.')
        return n
    
def replace_through_a_list(lista, old, new):
    try:
        new_list = [new if x == old else x for x in lista]
        return new_list
    except:
        print(f'erro ao formatar lista na funcao replace_through_a_list. lista dada como paramentro retornada: {lista}')
        return lista
    
def upper_through_a_list(lista):
    try:
        if isinstance(lista, tuple):#se por acaso for tupla
            lista = list(lista)
        if isinstance(lista, list):
            new_list = [str(x).upper() for x in lista]
            return new_list
        else:#evitar erros, retorna o valor singular no upper dentro de lista
            return [lista.upper()]
    except Exception as e:
        print(e)
        print(f'erro ao formatar lista na funcao upper_through_a_list. lista dada como paramentro retornada: {lista}')
        return lista
