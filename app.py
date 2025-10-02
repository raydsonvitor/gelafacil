from customtkinter import *
from interface import TrueBuyInterface
from CTkMessagebox import CTkMessagebox
import traceback
from datetime import datetime
import subprocess

#importações do sistema
import platform
import ctypes
import socket
import ntplib
import urllib.request
import json

#importacoes referentes ao google drive/cloud
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
import io

SISTEMA =  platform.system().lower()
SISTEMA_RELEASE = platform.release()
APP_VERSION = '1.2'
CONTATO = '51 989705423'

def main():   
    #CODIGO DE ABERTURA DO APP      
    try:
        root = CTk()
        root.title(f'PDV - MERCADO 15A - {APP_VERSION} - RayTec Soluções em Software - Todos Direitos Reservados 2024 ®')
        barradetarefas_height = 70  
        tela_width = root.winfo_screenwidth() - 15
        tela_height = root.winfo_screenheight() - barradetarefas_height
        root.geometry(f'{tela_width}x{tela_height}+0+0')
        root.resizable(False, False)                                     
        root.iconbitmap(r'images\icone.ico')                 
        app = TrueBuyInterface(root, tela_width, tela_height, APP_VERSION)
        root.mainloop()

    except Exception as e:
        print(f'Erro inesperado capturado: {e}')
        traceback.print_exc()
        CTkMessagebox(root, title='Erro Inesperado.', message=f'Erro Inesperado: {e}. Considere contatar a assistência: {CONTATO}')
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open("txts/error_log.txt", "a") as log_file:
            log_file.write(f"{current_time} -  {str(e)}\n")
            log_file.write(traceback.format_exc())
            log_file.write("\n---\n")
    
def check_data_computador():
    try:
        datetime_computador = datetime.now().replace(microsecond=0).replace(second=0)
        datetime_internet = datetime_from_internet().replace(second=0)
        if datetime_internet: #se o app conseguir o datetime da internet
            if datetime_computador < datetime_internet:
                alerta_popup('Corrija a hora e a data do computador antes de abrir o sistema.')
                if SISTEMA_RELEASE in ["10", "11"]:   # Windows 10 ou 11
                    subprocess.run("start ms-settings:dateandtime", shell=True)
                else:  # Windows 7, 8, ou mais antigo
                    subprocess.run("timedate.cpl", shell=True)
        else: # senao apenas compara  a datetime do computador com o lastdatetime 
            with open("txts/last_datetime.txt", "r") as log_file:
                last_datetime = datetime.strptime(log_file.read(), '%Y-%m-%d %H:%M:%S')
                if datetime_computador < last_datetime:
                    alerta_popup('Corrija a hora e a data do computador antes de abrir o sistema.')
                    if SISTEMA_RELEASE in ["10", "11"]:   # Windows 10 ou 11
                        subprocess.run("start ms-settings:dateandtime", shell=True)
                    else:  # Windows 7, 8, ou mais antigo
                        subprocess.run("timedate.cpl", shell=True)
        return datetime_computador
    except Exception as e:
        alerta_popup(f'Erro inesperado capturado na hora de checkar a data do computador: {e}.')

def internet_connection(timeout_intervalo=1):
    """
    Retorna True se houver conexão com a internet (TCP 1.1.1.1:53), False caso contrário.
    Timeout curto (1s) garante baixo custo computacional.
    """
    try:
        socket.create_connection(("1.1.1.1", 53), timeout=timeout_intervalo)
        return True    
    except OSError:
        return False

def datetime_from_internet():
    """Retorna datetime da internet sem milissegundos ou None se não conseguir."""
    
    if not internet_connection():
        return False

    # Tenta NTP
    ntp_servers = ["pool.ntp.org", "time.google.com", "time.windows.com"]
    for server in ntp_servers:
        try:
            client = ntplib.NTPClient()
            response = client.request(server, version=3, timeout=2)
            return datetime.fromtimestamp(response.tx_time).replace(microsecond=0)
        except Exception:
            continue

    # Fallback HTTP
    try:
        url = "https://worldtimeapi.org/api/ip"
        req = urllib.request.Request(url, headers={"User-Agent": "Python"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.load(resp)
            dt_str = data["datetime"]
            dt = datetime.fromisoformat(dt_str[:-6]).replace(microsecond=0)
            return dt
    except Exception:
        return False

def get_remote_app_version():
    
    # Escopo: acesso de leitura no Google Drive
    SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

    # Arquivo JSON da conta de serviço
    SERVICE_ACCOUNT_FILE = "credentials.json"  # renomeie conforme o arquivo que baixou

    # ID do arquivo (pegue na URL do Google Drive)
    FILE_ID = "12SrlexecnPG_1GS7BNR3UKNKxS343X1m"

    try:
        #CODIGO DE LEITURA DA VERSAO DO APP NA NUVEM

        # Autenticação com a conta de serviço
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)

        # Conectar ao Google Drive
        service = build("drive", "v3", credentials=creds)

        # Faz o download do arquivo
        request = service.files().get_media(fileId=FILE_ID)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)

        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Progresso: {int(status.progress() * 100)}%")

        # Volta o ponteiro do arquivo para o início
        fh.seek(0)

        # Lê o conteúdo como texto
        conteudo = fh.read().decode("utf-8")
        print("Conteúdo do arquivo:")
        print(conteudo)

    except Exception as e:
        print(f'Erro ao buscar versão remota do app: {e}')

def alerta_popup(mensagem, titulo='Atenção', icone=0x30):
    msg = ctypes.windll.user32.MessageBoxW(0, mensagem, titulo, icone)  # 0x30 = ícone de aviso (ícone amarelo)

if __name__=='__main__':
    try:
        #primeiro check se a data do computador nao esta errada
        lastappopening_datetime = check_data_computador()
        #rewrite o lastappopening_datetime
        with open("txts/lastappopening_datetime.txt", "w") as log_file:
            log_file.write(str(lastappopening_datetime))
        #abre o app
        if lastappopening_datetime:
            main()

    except Exception as e:
        alerta_popup(f'Houve um erro inesperado ao abrir o aplicativo: {e}.')   

    
