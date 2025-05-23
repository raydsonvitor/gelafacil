import subprocess
import sys
import os
from customtkinter import *
from PIL import Image
from time import sleep

class InstalerInterface:
    def __init__(self):
        set_appearance_mode("dark")  # Modo escuro (opcional)
        set_default_color_theme("blue")  # Tema (opcional)

        self.root = CTk()  # Cria a janela principal
        self.root.title("Janela Centralizada")  # Título da janela
        largura = 400
        altura = 300
        self.root.geometry(f"{largura}x{altura}")
        largura_tela = self.root.winfo_screenwidth()
        altura_tela = self.root.winfo_screenheight()
        x = (largura_tela // 2) - (largura // 2)
        y = (altura_tela // 2) - (altura // 2)
        self.root.geometry(f"{largura}x{altura}+{x}+{y}")
        self.root.overrideredirect(True)

        logotipo = CTkImage(light_image=Image.open(r'C:\Users\vitor\Documents\projetos\mercadoemergencial_1.1\images\raytec_logo.png'), size=(180, 180))
        self.root_label_logo = CTkLabel(self.root, text='', image=logotipo)
        self.root_label_logo.place(relx=0.5, rely=0.0, anchor='n')

        self.root_label_1 = CTkLabel(self.root, text='Atualizando...', font=CTkFont('Arial', 35, 'bold'))
        self.root_label_1.place(relx=0.5, rely=0.5, anchor='n')
        self.root_label_1 = CTkLabel(self.root, text='Por favor, aguarde até o processo ser finalizado.')
        self.root_label_1.place(relx=0.5, rely=0.75, anchor='n')

        self.root_progressbar = CTkProgressBar(self.root, width= 300, orientation='horizontal')
        self.root_progressbar.place(relx=0.5, rely=0.85, anchor='n')
        self.root_progressbar.set(0)

        self.root_label_2 = CTkLabel(self.root, text='Iniciando...')
        self.root_label_2.place(relx=0.5, rely=0.9, anchor='n')

        self.root.after(100, self.start_manager())

        self.root.mainloop()

    def start_manager(self):
        self.root_label_2.configure(text='Instalando atualização...')
        cfm = self.criar_executavel()
        if cfm:
            self.root_label_2.configure(text='Finalizado.')
            self.root_label_2.configure(text='Pronto.')
            self.root.update()
            self.root.destroy()

    def criar_executavel(self, icone=r"C:\Users\vitor\Documents\projetos\mercadoemergencial_1.1\images\icone.ico" ,script=r"C:\Users\vitor\Documents\projetos\mercadoemergencial_1.1\app.py"):
        self.root_label_2.configure(text='Instalando arquivos...')
        try:
            # Define o comando com Python explícito e executa o PyInstaller com o ícone
            comando = [
                sys.executable, "-m", "PyInstaller", '--noconsole',
                "--onefile", f"--icon={icone}", script
            ]
            subprocess.check_call(comando)

            print(f"Executável criado com sucesso para o script '{script}' com o ícone '{icone}'.")
            self.root_progressbar.set(0.66)
            self.root.update()
            return True
        except subprocess.CalledProcessError as e:
            print("Falha ao criar o executável. Verifique o script e o PyInstaller.")
            print(e)
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}")
        


if __name__=='__main__':
    InstalerInterface()
    


