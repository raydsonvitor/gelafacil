from customtkinter import *
from interface_adm import AdmInterface
from CTkMessagebox import CTkMessagebox
import traceback
from datetime import datetime

version = '1.0'
contato = '51 989705423'

def main():         
    try:
        #criacao e configuracao da tela
        root = CTk()
        root.title(f'ADM - MERCADO EMERGENCIAL - {version} - RayTec Soluções em Software - Todos Direitos Reservados 2024 ®')
        dimensoes = get_tela_dimensoes(root)
        root.geometry(f'{dimensoes[0]}x{dimensoes[1]}+{dimensoes[2]}+0')
        root.resizable(False, False)                 
        root.iconbitmap(r'images\icone_adm.ico')            

        #play da tela    
        app = AdmInterface(root, dimensoes[0], dimensoes[1], version)
        root.mainloop()

    except Exception as e:
        print(f'Erro inesperado capturado: {e}')    
        traceback.print_exc()
        CTkMessagebox(root, title='Erro Inesperado.', message=f'Erro Inesperado: {e}. Considere contatar a assistência: {contato}')
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open("txts/error_log.txt", "a") as log_file:
            log_file.write(f"{current_time} -  {str(e)}\n")
            log_file.write(traceback.format_exc())
            log_file.write("\n---\n")

def get_tela_dimensoes(root):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root_width = screen_width
    root_height = round(screen_height*0.91)
    distancia_corretora = (screen_width*0.06)*-1

    return root_width, root_height, distancia_corretora

if __name__=='__main__':
    main()