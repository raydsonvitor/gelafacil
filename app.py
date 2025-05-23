from customtkinter import *
from interface import TrueBuyInterface
from CTkMessagebox import CTkMessagebox
import traceback
from datetime import datetime

version = '1.0'
contato = '51 989705423'

def main():         
    try:
        root = CTk()
        root.title(f'PDV - GELA FACIL - {version} - RayTec Soluções em Software - Todos Direitos Reservados 2024 ®')
        barradetarefas_height = 70  
        tela_width = root.winfo_screenwidth() - 15
        tela_height = root.winfo_screenheight() - barradetarefas_height
        root.geometry(f'{tela_width}x{tela_height}+0+0')
        root.resizable(False, False)                                    
        root.iconbitmap(r'images\icone.ico')                 
        app = TrueBuyInterface(root, tela_width, tela_height, version)
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
    
if __name__=='__main__':
    main()

    
