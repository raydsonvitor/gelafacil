from datetime import datetime, timedelta, time
import time as tm
import pandas as pd

def get_data_comercial(ref_hora, ref_datetime_str):
    try:
        ref_datetime = datetime.strptime(ref_datetime_str, '%Y-%m-%d %H:%M:%S')

        if ref_datetime.time() < time(int(ref_hora), 0):
            dia_atual_comercial = (ref_datetime - pd.Timedelta(days=1)).date()
        else:
            dia_atual_comercial = ref_datetime.date()

        return str(dia_atual_comercial)

    except Exception as e:
        print(f'Erro ao obter data comercial: {e}')
        return False

def change_date_to_br_date(date):
    ano, mes, dia = date.split('-')
    return '/'.join((dia, mes, ano))

if __name__ == '__main__':
    pass
