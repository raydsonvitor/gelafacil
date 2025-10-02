import subprocess
import sys
import os
from customtkinter import *
from PIL import Image
from time import sleep
import shutil, psutil, ctypes, win32com.client

# Caminho base: pasta onde o script está
BASE_DIR = os.path.dirname(__file__)  # mesmo que a pasta do script

# Caminhos relativos
ARQUIVO_NOVO = os.path.join(BASE_DIR, 'dist', 'app.exe')
ARQUIVO_DESTINO = os.path.join(BASE_DIR, 'app.exe')  # ou outra pasta ao lado
NOME_EXE = 'app'

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

    def alerta_popup(self, titulo, mensagem):
        ctypes.windll.user32.MessageBoxW(0, mensagem, titulo, 0x30)  # 0x30 = ícone de aviso (ícone amarelo)

    def esta_em_execucao(self, nome_exe):
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] == nome_exe+'.exe':
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False

    def start_manager(self):
        #verifica se o app está aberto
        if self.esta_em_execucao(NOME_EXE):
            self.alerta_popup("Atualização bloqueada", "Por favor, feche o programa antes de atualizar.")
            self.fechar_instalador()
            return  
        
        self.root_label_2.configure(text='Instalando atualização...')
        cfm = self.criar_executavel()
        if cfm:
            self.mover_executavel()
        else:
            self.alerta_popup("Erro", "Erro ao criar o executavel.")

    def criar_executavel(self, icone=r"images\icone.ico" ,script=r"app.py"):
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
        
    def criar_atalho(self, nome_exe, destino_final):
        desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        caminho_atalho = os.path.join(desktop, f'{nome_exe}.lnk')

        shell = win32com.client.Dispatch("WScript.Shell")
        atalho = shell.CreateShortCut(caminho_atalho)
        atalho.Targetpath = destino_final
        atalho.WorkingDirectory = os.path.dirname(destino_final)
        atalho.IconLocation = destino_final  # Pode usar o próprio .exe como ícone
        atalho.save()

        self.fechar_instalador()

        self.alerta_popup("Sucesso", "Atualização concluída com sucesso.")

    def mover_executavel(self):
        #exclui o app antigo
        if os.path.exists(ARQUIVO_DESTINO):
            os.remove(ARQUIVO_DESTINO)

        #move o app para a pasta principal do projeto
        shutil.move(ARQUIVO_NOVO, ARQUIVO_DESTINO)

        #cria um aalho para o executavel gerado e fechao a janela do instalador
        self.criar_atalho(NOME_EXE, ARQUIVO_DESTINO)
        

    def fechar_instalador(self):
        self.root.destroy()

if __name__=='__main__':
    InstalerInterface()
    


