from customtkinter import *
from tkinter import ttk
from PIL import Image
import database, api, helper
import traceback
from CTkMessagebox import CTkMessagebox
import serial
import time as tm
from datetime import datetime as dt, timedelta, time
import json
from pygame import mixer

class AdmInterface:
    def __init__(self, root, tela_width, tela_height, version):
        self.root = root
        self.tela_width = tela_width
        self.tela_height = tela_height
        #variaveis para controle de janelas toplevel
        self.yon = False
        self.tp_password = None
        #general estilização treeview 
        style = ttk.Style()
        style.map("Treeview", 
                background=[("selected", "orange")])
        style.configure("Treeview", font=("arial", 12))
        style.configure("Treeview.Heading", font=("Arial", 12, 'bold'))

        #relogio
        self.clock = CTkLabel(self.root, font=("Arial", 20))
        self.clock.place(relx=0.93, rely=0.95)
        self.clock.lift()
        self.update_clock()

        #outras definições
        mixer.init()
        self.formas_pgmt_ativas = ('dinheiro', 'débito', 'crédito', 'pix')
        self.general_product_id = '20'
        self.customer_id = 0
        self.oncredit_ids = []
        self.sangria_categorias = ('Pagamento de Mercadoria', 'Pagamento de Freelancer', 'Pagamento de Motoboy', 'Troca' , 'Outro')
        self.mercadoria_categorias = ('Alimento', 'Produto de limpeza', 'Higiêne / Cuidados Pessoais', 'Bebida', 'Bebida alcoólica', 'Tabacaria', 'ferragem')
        self.products_table_columns = ('id', 'barcode','descricao', 'ncm', 'ncm_desc', 'marca', 'nome', 'price', 'quantity', 'source', 'data_vencimento')
        self.version = version
        self.contato = '51 989705423'
        self.tp_password_feedback = False

        #fontes
        self.fonte_basic = CTkFont('arial', 15, 'bold')
        self.fonte_padrao_bold = CTkFont('arial', 18, 'bold')
        self.fonte_padrao = CTkFont('arial', 20)

        #imgs
        self.papainoel_img = CTkImage(light_image=Image.open(r'images\fornecedor.png'), size=(80, 80))


        self.abrir_root()

    def update_clock(self):
        now = tm.strftime("%H:%M:%S")
        self.clock.configure(text=now)
        self.root.after(1000, self.update_clock)

    def abrir_root(self):
        pady = 10 

        #Header
        self.root_title = CTkLabel(self.root, text=f'  GELA FÁCIL ADM {self.version}  ', font=CTkFont('helvetica', 60, 'bold'), compound='right', 
        fg_color='black', text_color='white', width=self.tela_width, height=150, corner_radius=10)
        self.root_title.place(relx=0.5, rely=0, anchor='n')

        #CRIACAO DOS BOTOES

        #criando o frame dos botoes
        self.root_frame_botoes = CTkFrame(self.root, width=round(self.tela_width*0.8), height=round(self.tela_height*0.7))
        self.root_frame_botoes.place(relx=0.5, y=self.root_title.cget('height')+pady, anchor='n')

        #botao abrir gdv de fornecedores
        self.root_btn_abrir_ger_fornecedores = CTkButton(self.root_frame_botoes, width=150, height=30, font=self.fonte_padrao_bold, text='Gerenciamento de Fornecedores', text_color='black', image=self.papainoel_img, compound='left', cursor='hand2', command=lambda: self.abrir_tp_gdf())

        #PLACES DOS BOTOES

        # Pega todos os widgets do frame dos botoes
        botoes = self.root_frame_botoes.winfo_children()

        for i, botao in enumerate(botoes, start=1):
            relx = i/10
            botao.place(relx=relx, rely=relx)
            






#region MODULO - GDF (GERENCIAMENTO DE FORNECEDORES)

    def abrir_tp_gdf(self):
        self.tp_gdf = CTkToplevel(self.root)
        self.tp_gdf.title('GERENCIAMENTO DE FORNECEDORES')
        self.tp_gdf.protocol('WM_DELETE_WINDOW', self.fechar_tp_gdf)
        self.tp_gdf_width = self.root.winfo_width() * 80 // 100
        self.tp_gdf_height = self.root.winfo_height()* 80 // 100
        self.tp_gdf_x = self.root.winfo_width()//2 - self.tp_gdf_width//2   #essa e algumas abaixo, sao linhas que centralizam o tp na root
        self.tp_gdf_y = self.root.winfo_height()//2 - self.tp_gdf_height//2
        self.tp_gdf.geometry(f'{self.tp_gdf_width}x{self.tp_gdf_height}+{self.tp_gdf_x}+{self.tp_gdf_y}')
        self.tp_gdf.resizable(False, False)
        self.tp_gdf.attributes('-topmost', 'true')
        self.tp_gdf.grab_set()

        #imgs
        self.fornecedores_img = Image.open(r'images\fornecedor.png')
        self.registro_fornecedores_img = Image.open(r'images\fornecedor_cadastro.png')
    
        # tp ilustração
        self.tp_gdf_ilustracao = CTkLabel(self.tp_gdf,  text='', image=CTkImage(light_image=self.fornecedores_img, size=(99, 99)))
        self.tp_gdf_ilustracao.place(relx=0.075, rely=0.05, anchor='n')

        # entry para inserir a busca
        self.tp_gdf_entry_1 = CTkEntry(self.tp_gdf, width=self.tp_gdf_width - (self.tp_gdf_width * 30 // 100), height=50, placeholder_text='Procurar por...', font=self.fonte_basic, border_color='black')
        self.tp_gdf_entry_1.place(relx=0.15, rely=0.1)
        #self.tp_gdf_entry_1.bind("<KeyRelease>", self.procurar_por())

        # Treeview para exibir os resultados de forma tabular
        self.tp_gdf_treeview_columns = ('id', 'fornecedor', 'whatsapp', 'cnpj')
        self.tp_gdf_treeview = ttk.Treeview(self.tp_gdf, columns=self.tp_gdf_treeview_columns, show="headings", height=15)
        self.tp_gdf_treeview.column(self.tp_gdf_treeview_columns[0], width=80, anchor=CENTER)
        self.tp_gdf_treeview.column(self.tp_gdf_treeview_columns[1], width=400, anchor=CENTER)
        self.tp_gdf_treeview.column(self.tp_gdf_treeview_columns[2], width=200, anchor=CENTER)
        self.tp_gdf_treeview.column(self.tp_gdf_treeview_columns[3], width=200, anchor=CENTER)
        self.tp_gdf_treeview.heading(self.tp_gdf_treeview_columns[0], text="id".capitalize(), )
        self.tp_gdf_treeview.heading(self.tp_gdf_treeview_columns[1], text="nome".capitalize(), )
        self.tp_gdf_treeview.heading(self.tp_gdf_treeview_columns[2], text="whatsapp".capitalize())
        self.tp_gdf_treeview.heading(self.tp_gdf_treeview_columns[3], text="cpf".capitalize())
        self.tp_gdf_treeview.place(relx=0.5, rely=0.25, anchor='n')

        # Cria a Scrollbar e associa à Treeview
        scrollbar = CTkScrollbar(self.tp_gdf, orientation="vertical", command=self.tp_gdf_treeview.yview)
        scrollbar.place(relx=0.92, rely=0.35)
        self.tp_gdf_treeview.configure(yscrollcommand=scrollbar.set)

        # botao registrar cliente
        self.tp_gdf_button_novoregistro = CTkButton(self.tp_gdf,  text='NOVO CADASTRO', image=CTkImage(light_image=self.registro_fornecedores_img, size=(60, 60)), font=self.fonte_basic, text_color='black', fg_color='transparent', width=0, command=lambda:self.abrir_tp_gdf_novocadastro(0))
        self.tp_gdf_button_novoregistro.place(relx=0.03, rely=0.86)

        #binds
        self.tp_gdf_treeview.bind('<Double-1>', lambda event:self.abrir_tp_gdf_novocadastro(1))

    def abrir_tp_gdf_novocadastro(self, tipo): # 0 para novo cadastro e 1 para edicao de cadastro 
        if tipo: #Se for abrir  no modo edição
            titlo_janela = 'Editar Dados do Fornecedor'
            if not self.tp_gdf_treeview.selection(): #trata o caso de o usuario nao identificar o cliente que gostaria de editar os dados
                msg = CTkMessagebox(self.tp_gdf, message=f'Selecione um fornecedor antes de utilizar essa função.', icon='warning', title='Atenção')
                self.tp_gdf.wait_window(msg)
                return
            #coletando o id do fornecedor selecionado
            selected_item = self.tp_gdf_treeview.focus()
            item_values = self.tp_gdf_treeview.item(selected_item, "values")
            dados_fornecedor = database.get_fornecedor_by_id(item_values[0])
            if not dados_fornecedor:
                CTkMessagebox(self.tp_gdf, message=f'Não foi possível encontrar os dados deste fornecedor.', icon='cancel', title='Erro')
                return
        else:
            titlo_janela = 'Registrar Fornecedor'

        self.tp_gdf_novocadastro = CTkToplevel(self.tp_gdf)
        self.tp_gdf_novocadastro.title(titlo_janela)
        self.tp_gdf_novocadastro.protocol('WM_DELETE_WINDOW', self.fechar_tp_gdf_novocadastro)
        self.tp_gdf_novocadastro_width = self.root.winfo_width() * 70 // 100
        self.tp_gdf_novocadastro_height = self.root.winfo_height()* 70 // 100
        self.tp_gdf_novocadastro_x = self.root.winfo_width()//2 - self.tp_gdf_novocadastro_width//2   #essa e algumas abaixo, sao linhas que centralizam o tp na root
        self.tp_gdf_novocadastro_y = self.root.winfo_height()//2 - self.tp_gdf_novocadastro_height//2
        self.tp_gdf_novocadastro.geometry(f'{self.tp_gdf_novocadastro_width}x{self.tp_gdf_novocadastro_height}+{self.tp_gdf_novocadastro_x}+{self.tp_gdf_novocadastro_y}')
        self.tp_gdf_novocadastro.resizable(False, False)
        self.tp_gdf_novocadastro.attributes('-topmost', 'true')
        self.tp_gdf_novocadastro.grab_set()

        self.clientes_cadastro_img = Image.open(r'images\fornecedor_cadastro.png')

        #variveis de controle
        self.tp_gdf_novocadastro_entry_nome_keyrelease_block = False
        self.tp_gdf_novocadastro_entry_cpf_keyrelease_block = False
        self.tp_gdf_novocadastro_entry_whatsapp_keyrelease_block = False
        self.tp_gdf_novocadastro_entry_email_keyrelease_block = False
        self.tp_gdf_novocadastro_entry_endereco_keyrelease_block = False
        self.tp_gdf_novocadastro_entry_datanascimento_keyrelease_block = False
        self.tp_gdf_novocadastro_entry_limite_keyrelease_block = False

        #definindo as variaveis de controle (inicialmente como True)
        self.tp_gdf_novocadastro_nome_validado = self.tp_gdf_novocadastro_cpf_validado = self.tp_gdf_novocadastro_whatsapp_validado = self.tp_gdf_novocadastro_email_validado = self.tp_gdf_novocadastro_endereco_validado = self.tp_gdf_novocadastro_datanascimento_validado = self.tp_gdf_novocadastro_limite_validado = True 
        
        if not tipo:# ao abrir no modo novo registro           
            #tornando False as variaveis de controle ref à campos obrigatorios
            self.tp_gdf_novocadastro_nome_validado = False
            self.tp_gdf_novocadastro_cpf_validado = False
            self.tp_gdf_novocadastro_whatsapp_validado = False 

        # tp ilustração
        self.tp_gdf_novocadastro_ilustracao = CTkLabel(self.tp_gdf_novocadastro,  text='', image=CTkImage(light_image=self.clientes_cadastro_img, size=(99, 99)))
        self.tp_gdf_novocadastro_ilustracao.place(relx=0.075, rely=0.02)

        #titlo
        self.tp_gdf_novocadastro_titlo = CTkLabel(self.tp_gdf_novocadastro,  text=titlo_janela, font=CTkFont('arial', 35, 'bold'), compound='left')
        self.tp_gdf_novocadastro_titlo.place(relx=0.5, rely=0.05, anchor='n')

        #campo nome
        self.tp_gdf_novocadastro_label_nome = CTkLabel(self.tp_gdf_novocadastro, text='NOME * :', font=self.fonte_basic)
        self.tp_gdf_novocadastro_label_nome.place(relx=0.05, rely=0.325)
        self.tp_gdf_novocadastro_entry_nome = CTkEntry(self.tp_gdf_novocadastro, font=self.fonte_basic, width=300, height=35)
        self.tp_gdf_novocadastro_entry_nome.place(relx=0.15, rely=0.325)
        self.tp_gdf_novocadastro_entry_nome_sinalizer = CTkLabel(self.tp_gdf_novocadastro ,text_color='red', height=0)

        self.tp_gdf_novocadastro_entry_nome.bind('<KeyRelease>', lambda event:self.tp_gdf_novocadastro_entry_nome_keyrelease())

        #campo cpf
        self.tp_gdf_novocadastro_label_cpf = CTkLabel(self.tp_gdf_novocadastro, text='CPF *:', font=self.fonte_basic)
        self.tp_gdf_novocadastro_label_cpf.place(relx=0.05, rely=0.45)
        self.tp_gdf_novocadastro_entry_cpf = CTkEntry(self.tp_gdf_novocadastro, font=self.fonte_basic, width=300, height=35)
        self.tp_gdf_novocadastro_entry_cpf.place(relx=0.15, rely=0.45)
        self.tp_gdf_novocadastro_entry_cpf_sinalizer = CTkLabel(self.tp_gdf_novocadastro ,text_color='red', height=0)

        self.tp_gdf_novocadastro_entry_cpf.bind('<KeyRelease>', lambda event:self.tp_gdf_novocadastro_entry_cpf_keyrelease())

        #campo whatsapp
        self.tp_gdf_novocadastro_label_whatsapp = CTkLabel(self.tp_gdf_novocadastro, text='WHATSAPP:*', font=self.fonte_basic)
        self.tp_gdf_novocadastro_label_whatsapp.place(relx=0.05, rely=0.575)
        self.tp_gdf_novocadastro_entry_whatsapp = CTkEntry(self.tp_gdf_novocadastro, font=self.fonte_basic, width=300, height=35)
        self.tp_gdf_novocadastro_entry_whatsapp.place(relx=0.15, rely=0.575)
        self.tp_gdf_novocadastro_entry_whatsapp_sinalizer = CTkLabel(self.tp_gdf_novocadastro ,text_color='red', height=0)
        
        self.tp_gdf_novocadastro_entry_whatsapp.bind('<KeyRelease>', lambda event:self.tp_gdf_novocadastro_entry_whatsapp_keyrelease())

        #campo e-mail
        self.tp_gdf_novocadastro_label_email = CTkLabel(self.tp_gdf_novocadastro, text='E-MAIL:', font=self.fonte_basic)
        self.tp_gdf_novocadastro_label_email.place(relx=0.05, rely=0.7)
        self.tp_gdf_novocadastro_entry_email = CTkEntry(self.tp_gdf_novocadastro, font=self.fonte_basic, width=300, height=35)
        self.tp_gdf_novocadastro_entry_email.place(relx=0.15, rely=0.7)
        self.tp_gdf_novocadastro_entry_email_sinalizer = CTkLabel(self.tp_gdf_novocadastro ,text_color='red', height=0)

        self.tp_gdf_novocadastro_entry_email.bind('<KeyRelease>', lambda event:self.tp_gdf_novocadastro_entry_email_keyrelease())

        #campo genero
        self.tp_gdf_novocadastro_genero_var = StringVar(value='masculino')

        self.tp_gdf_novocadastro_label_genero = CTkLabel(self.tp_gdf_novocadastro, text='SEXO:', font=self.fonte_basic)
        self.tp_gdf_novocadastro_label_genero.place(relx=0.5, rely=0.325)
        self.tp_gdf_novocadastro_radiobutton_genero_masculino = CTkRadioButton(self.tp_gdf_novocadastro, text='MASCULINO', variable=self.tp_gdf_novocadastro_genero_var, value='masculino', border_width_checked=10)
        self.tp_gdf_novocadastro_radiobutton_genero_masculino.place(relx=0.65, rely=0.325)
        self.tp_gdf_novocadastro_radiobutton_genero_feminino = CTkRadioButton(self.tp_gdf_novocadastro, text='FEMININO', variable=self.tp_gdf_novocadastro_genero_var, value='feminino', border_width_checked=10)
        self.tp_gdf_novocadastro_radiobutton_genero_feminino.place(relx=0.8, rely=0.325)

        #campo endereco
        self.tp_gdf_novocadastro_label_endereco = CTkLabel(self.tp_gdf_novocadastro, text='ENDEREÇO:', font=self.fonte_basic)
        self.tp_gdf_novocadastro_label_endereco.place(relx=0.5, rely=0.45)
        self.tp_gdf_novocadastro_entry_endereco = CTkEntry(self.tp_gdf_novocadastro, font=self.fonte_basic, width=300, height=35)
        self.tp_gdf_novocadastro_entry_endereco.place(relx=0.62, rely=0.45)
        self.tp_gdf_novocadastro_entry_endereco_sinalizer = CTkLabel(self.tp_gdf_novocadastro ,text_color='red', height=0)

        self.tp_gdf_novocadastro_entry_endereco.bind('<KeyRelease>', lambda event:self.tp_gdf_novocadastro_entry_endereco_keyrelease())

        #campo data nascimento
        self.tp_gdf_novocadastro_label_datanascimento = CTkLabel(self.tp_gdf_novocadastro, text='DATA NASC.:', font=self.fonte_basic)
        self.tp_gdf_novocadastro_label_datanascimento.place(relx=0.5, rely=0.575)
        self.tp_gdf_novocadastro_entry_datanascimento = CTkEntry(self.tp_gdf_novocadastro, font=self.fonte_basic, width=300, height=35, placeholder_text='Ex: 19/06/1999', placeholder_text_color='gray')
        self.tp_gdf_novocadastro_entry_datanascimento.place(relx=0.62, rely=0.575)
        self.tp_gdf_novocadastro_entry_datanascimento_sinalizer = CTkLabel(self.tp_gdf_novocadastro ,text_color='red', height=0)

        self.tp_gdf_novocadastro_entry_datanascimento.bind('<KeyRelease>', lambda event:self.tp_gdf_novocadastro_entry_datanascimento_keyrelease())
    
        #campo limite
        self.tp_gdf_novocadastro_label_limite = CTkLabel(self.tp_gdf_novocadastro, text='LIMITE:', font=self.fonte_basic)
        self.tp_gdf_novocadastro_label_limite.place(relx=0.5, rely=0.7)
        self.tp_gdf_novocadastro_entry_limite = CTkEntry(self.tp_gdf_novocadastro, font=self.fonte_basic, width=300, height=35)
        self.tp_gdf_novocadastro_entry_limite.place(relx=0.62, rely=0.7)
        self.tp_gdf_novocadastro_entry_limite_sinalizer = CTkLabel(self.tp_gdf_novocadastro ,text_color='red', height=0)
        if not tipo:
            self.tp_gdf_novocadastro_entry_limite.insert(0, '0')

        self.tp_gdf_novocadastro_entry_limite.bind('<KeyRelease>', lambda event:self.tp_gdf_novocadastro_entry_limite_keyrelease())

        #botao
        if tipo:
            self.tp_gdf_novocadastro_button = CTkButton(self.tp_gdf_novocadastro, font=self.fonte_basic, text='ATUALIZAR', command=lambda:self.tp_gdf_novocadastro_editar_cliente(dados_fornecedor[0]), state='disabled', fg_color='gray')

        else:
            self.tp_gdf_novocadastro_button = CTkButton(self.tp_gdf_novocadastro, font=self.fonte_basic, text='CADASTRAR', command=lambda:self.tp_gdf_novocadastro_registrar_cliente(), state='disabled', fg_color='gray')
        
        self.tp_gdf_novocadastro_button.place(relx=0.5, rely=0.85, anchor='n')

        #dica
        self.tp_gdf_novocadastro_label_dica = CTkLabel(self.tp_gdf_novocadastro, text='Campos com * são obrigatórios.', font=self.fonte_basic, height=0)
        self.tp_gdf_novocadastro_label_dica.place(relx=0.05, rely=0.925)

        if tipo: #inserir os dados do cliente selecionado nos campos correspondentes
            #nome
            self.tp_gdf_novocadastro_entry_nome.insert(0, dados_fornecedor[1])
            #cpf
            self.tp_gdf_novocadastro_entry_cpf.insert(0, dados_fornecedor[2])
            #whats
            self.tp_gdf_novocadastro_entry_whatsapp.insert(0, dados_fornecedor[3])
            #email
            email = dados_fornecedor[4] if dados_fornecedor[4] else '' #gambiarra para contornar o erro de o Email ser NULL no database
            self.tp_gdf_novocadastro_entry_email.insert(0, email)
            #genero
            self.tp_gdf_novocadastro_genero_var.set(dados_fornecedor[5])
            #endereco
            self.tp_gdf_novocadastro_entry_endereco.insert(0, dados_fornecedor[6])
            #data de nascimento
            self.tp_gdf_novocadastro_entry_datanascimento.insert(0, dados_fornecedor[7])
            #limite
            self.tp_gdf_novocadastro_entry_limite.insert(0, dados_fornecedor[8])
            #disparando o check das variaseis para ativar o botao do formulario
            self.tp_gdf_novocadastro_check_campos_obrigatorios()

        #bind's
        self.tp_gdf_novocadastro.bind('<Escape>', lambda event: self.fechar_tp_gdf_novocadastro())
        self.tp_gdf_novocadastro.bind('<Return>', lambda event: self.tp_gdf_novocadastro_button.invoke())

        self.tp_gdf_novocadastro.after(100, self.tp_gdf_novocadastro_label_nome.focus_set())

    def tp_gdf_novocadastro_check_campos_obrigatorios(self):
        items = (self.tp_gdf_novocadastro_nome_validado,  self.tp_gdf_novocadastro_cpf_validado, self.tp_gdf_novocadastro_whatsapp_validado, self.tp_gdf_novocadastro_email_validado, self.tp_gdf_novocadastro_endereco_validado, self.tp_gdf_novocadastro_datanascimento_validado, self.tp_gdf_novocadastro_limite_validado) 
        for item in items:
            if item == False:
                self.tp_gdf_novocadastro_button.configure(state='disabled')
                self.tp_gdf_novocadastro_button.configure(fg_color='gray')
                return
        self.tp_gdf_novocadastro_button.configure(state='normal')
        self.tp_gdf_novocadastro_button.configure(fg_color='blue')

    def fechar_tp_gdf_novocadastro(self):
        self.tp_gdf_novocadastro.destroy()

    def fechar_tp_gdf(self):
        self.tp_gdf.destroy()
    

#endregion