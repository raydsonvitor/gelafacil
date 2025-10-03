from customtkinter import *
from tkinter import ttk
from PIL import Image
import database, api, helper, backend
from updater import InstalerInterface
import traceback
from CTkMessagebox import CTkMessagebox
import serial
import time as tm
from datetime import datetime as dt, timedelta, time
import json
from pygame import mixer
import ast

NOME_TITULO = 'GELA FÁCIL'
HORA_VIRADA_DATA_COMERCIAL = 6 #6 horas da manhã
AFTER_INTERVALO = 100 #intervalo em ms (parametro da funcao after ao longo do codigo)

# region Init

class TrueBuyInterface:
    def __init__(self, root, tela_width, tela_height, version):
        self.root = root
        self.tela_width = tela_width
        self.tela_height = tela_height

        #variaveis para controle de janelas toplevel
        self.yon = False
        self.tp_cdm = self.tp_idv_1 = self.tp_idv_2 = self.tp_gdm = self.tp_gdm_tp_editar_mercadoria = self.tp_5 = self.tp_6 = self.tp_7 = self.tp_gdc = self.tp_9 = self.tp_gdv = self.tp_clientes = None
        self.tp_password = self.tp_loading = None

        #varivaveis para controle de labels content
        self.current_subtotal = helper.format_to_moeda(0) #subtotal atual

        #general estilização treeview 
        style = ttk.Style()
        style.map("Treeview", 
                background=[("selected", "orange")])
        style.configure("Treeview", font=("arial", 12))
        style.configure("Treeview.Heading", font=("Arial", 12, 'bold'))
        #hidden treeview
        style.configure("Hidden.Treeview", font=("arial", 18), rowheight=50)

        #data comercial e previsao de faturamento para a data em questao
        now = dt.now().strftime('%Y-%m-%d %H:%M:%S')
        self.data_comercial = backend.get_data_comercial(HORA_VIRADA_DATA_COMERCIAL, now)
        self.mes_comercial = self.data_comercial[:4]+self.data_comercial[5:7]
        if not self.data_comercial:
            msg = CTkMessagebox(self.root, message=f'Inicialização do sistema abortada por conta de erro na identificação da data comercial.', icon='cancel', title='Erro')
            self.root.wait_window(msg)
            self.root.destroy()
            return

        self.datacomercial_label = CTkLabel(self.root, font=("Arial", 14), text=f'Data Comercial: {backend.change_date_to_br_date(self.data_comercial)}', text_color='black')
        self.datacomercial_label.place(relx=0.01, rely=0.917)
        self.datacomercial_label.lift()

        self.previsao_fat_dia = database.get_previsao_faturamento_dia(self.data_comercial)
        self.previsao_fat_mes = database.get_previsao_faturamento_mes(self.data_comercial[:4]+self.data_comercial[5:7]) 

        #relogio
        self.clock = CTkLabel(self.root, font=("Arial", 20))
        self.clock.place(relx=0.83, rely=0.915)
        self.clock.lift()

        #sistem constant updater
        self.sisten_constant_updater()

        #outras definições
        mixer.init()
        self.formas_pgmt_ativas = ('dinheiro', 'débito', 'crédito', 'pix')
        self.fonte_basic = CTkFont('arial', 15, 'bold')
        self.general_product_id = '20'
        self.customer_id = 0
        self.oncredit_ids = []
        self.sangria_categorias = ('Pagamento de Mercadoria', 'Pagamento de Freelancer', 'Pagamento de Motoboy', 'Troca' , 'Outro')
        self.mercadoria_categorias = ('Alimento', 'Produto de limpeza', 'Higiêne / cuidados pessoais', 'Bebida', 'Bebida alcoólica', 'Tabacaria', 'Ferragem', 'Outro')
        self.fornecedores = ('Bees', 'Femsa', 'Djalma', 'Bicudo', 'Estação dos doces', 'Zanella', 'Nascar', 'Volnei', 'Wg Gelo', 'Outro', 'Sem fornecedor')
        self.version = version
        self.contato = '51 989705423'
        self.tp_password_feedback = False
        self.set_idv_conta_cliente = False
        self.encerrar_finzalização_da_compra_block = False

        #fontes
        self.tp_cdm_fonte_padrao_bold = CTkFont('arial', 18, 'bold')
        self.tp_cdm_fonte_padrao = CTkFont('arial', 20)

        self.last_venda_time = tm.time()

        self.abrir_idv_interface()
        self.root.after_idle(self.decoration_checker)

    def sisten_constant_updater(self):
        # hora update
        now = tm.strftime("%Y-%m-%d %H:%M:%S")
        data, hora = now.split(' ')
        self.clock.configure(text=hora)
        self.root.after(1000, self.sisten_constant_updater)

        #data comercial update
        if backend.get_data_comercial(HORA_VIRADA_DATA_COMERCIAL, now) != self.data_comercial:
            #atualiza a data comercial
            self.data_comercial = backend.get_data_comercial(HORA_VIRADA_DATA_COMERCIAL, now)
            self.datacomercial_label.configure(text=f'Data Comercial: {backend.change_date_to_br_date(self.data_comercial)}')

            #faz as previsoes para a nova data comercial
            self.previsao_fat_dia = database.get_previsao_faturamento_dia(self.data_comercial)
            if self.mes_comercial != self.data_comercial[:4]+self.data_comercial[5:7]:
                print('trocou o mes comercial')
                self.previsao_fat_mes = database.get_previsao_faturamento_mes(self.data_comercial[:4]+self.data_comercial[5:7]) 

    ### decoration functions
    def decoration_checker(self):
        today = dt.now()
        if today.month == 12 and 1 <= today.day <= 25:
            self.natal_decoration_setter()
        elif (today.month == 12 and 26 <= today.day <= 31) or (today.month == 1 and 1<= today.day <= 5):
            self.ano_novo_decoration_setter(today.year, today.month)

    def natal_decoration_setter(self):
        papainoel_img = CTkImage(light_image=Image.open(r'images\natal_decoration\papainoel.png'), size=(140, 140))
        deco_1 = CTkLabel(self.root, text='', fg_color='black', image=papainoel_img)
        deco_1.place(relx=0.05, rely=0)

        self.tp_idv_frame_footer_label.place_forget()

        self.label_title.configure(text='     UM  FELIZ  NATAL !    ')

        fundo_img = CTkImage(light_image=Image.open(r'images\natal_decoration\fundo.png'), size=(self.tela_width, self.tela_height))


        background_label = CTkLabel(self.root, image=fundo_img, text="", fg_color="transparent", bg_color="transparent")
        background_label.place(x=0, y=0, relwidth=1, relheight=1)  # Define o tamanho da imagem de fundo
        background_label.lower()

        self.tp_idv_frame_status.configure(fg_color='transparent')
        self.root.after(AFTER_INTERVALO, self.tp_idv_entry_codbar.focus_set)

    def ano_novo_decoration_setter(self, year, month):
        if month == 12:    
            ano_novo = year+1
        else:
            ano_novo = year

        tacas_img = CTkImage(light_image=Image.open(r'images\newyear_decoration\tacas.png'), size=(125, 125))
        deco_1 = CTkLabel(self.root, text='', fg_color='black', image=tacas_img)
        deco_1.place(relx=0.05, rely=0.02)
        self.tp_idv_frame_footer_label.place_forget()

        self.label_title.configure(text=f'    UM FELIZ {ano_novo} !    ')

        fundo_img = CTkImage(light_image=Image.open(r'images\newyear_decoration\fundo.png'), size=(self.tela_width, self.tela_height))


        background_label = CTkLabel(self.root, image=fundo_img, text="", fg_color="transparent", bg_color="transparent")
        background_label.place(x=0, y=0, relwidth=1, relheight=1)  # Define o tamanho da imagem de fundo
        background_label.lower()

        self.tp_idv_frame_status.configure(fg_color='transparent')
        self.tp_idv_entry_codbar.configure(bg_color='black')
        self.root.after(AFTER_INTERVALO, self.tp_idv_entry_codbar.focus_set)

    def tocar_notificacao(self):
        mixer.music.load("not.mp3")  # seu arquivo aqui
        mixer.music.play()  # toca só uma vez

    # normal function

    def abrir_gaveta(self):
        return
        # Ajuste a porta COM conforme necessário
        com_port = 'COM2'  # Substitua pela sua porta correta
        baud_rate = 9600

        # Comando para abrir a gaveta
        open_drawer_command = b'\x1B\x70\x00\x19\xFA'  # ESC p 0 25 250

        # Enviar comando
        try:
            with serial.Serial(com_port, baud_rate, timeout=1) as printer:
                printer.write(open_drawer_command)
                printer.flush()
                time.sleep(1)  # Aguarda um segundo
                print("Gaveta de caixa aberta.")
        except Exception as e:
            print(f"Erro ao abrir a gaveta: {e}")


    def get_yes_or_not(self, janela, ask='Confirmar esta operação?'):
        try:
            if self.yon == False:
                msg = CTkMessagebox(janela, title="Confirmar operação?", message=ask,
                                icon="question", option_2="Sim", option_1="Não", option_focus=2, font=self.fonte_basic)
                self.yon = True
                msg.grab_set()
                response = msg.get()
                if response == 'Sim':
                    self.yon = False
                    return True
                self.yon = False
                return False
        except Exception as e:
            print(f'Erro na funcao get_yes_or_not')
        finally:
            self.yon = False

    def abrir_tp_password(self, janela):
        self.tp_password = CTkToplevel(janela)
        self.tp_password.attributes('-topmost', 'true')
        self.tp_password.title('Inserir Senha')
        self.tp_password_width = 500
        self.tp_password_height = 250
        self.tp_password_x = self.root.winfo_width()//2 - self.tp_password_width//2   #essa e algumas abaixo, sao linhas que centralizam o tp na root
        self.tp_password_y = self.root.winfo_height()//2 - self.tp_password_height//2
        self.tp_password.geometry(f'{self.tp_password_width}x{self.tp_password_height}+{self.tp_password_x}+{self.tp_password_y}')
        self.tp_password.resizable(False, False)
        self.tp_password.grab_set()

        
        titlo = CTkLabel(self.tp_password, text='Inserir senha para prosseguir:', font=CTkFont('arial', 30, 'bold'))
        titlo.place(relx=0.5, rely=0.05, anchor='n')

        self.tp_password_entry = CTkEntry(self.tp_password, width=400, height=50, font=self.tp_cdm_fonte_padrao_bold, show='*')
        self.tp_password_entry.place(relx=0.5, rely=0.3, anchor='n')
        self.tp_password_entry_sinalizer = CTkLabel(self.tp_password, text='Senha inválida', text_color='red')

        button_ok=CTkButton(self.tp_password, text='Confirmar', font=self.tp_cdm_fonte_padrao_bold, height = 50, command=lambda:self.tp_password_confirma(), fg_color='green', hover_color='green')
        button_ok.place(relx=0.18, rely=0.7)
        button_cancel=CTkButton(self.tp_password, text='Cancelar', font=self.tp_cdm_fonte_padrao_bold, height = 50, command=lambda:self.tp_password_cancel(), fg_color='green', hover_color='green')
        button_cancel.place(relx=0.57, rely=0.7)

        self.tp_password.after(AFTER_INTERVALO, self.tp_password_entry.focus_set)
        self.tp_password.bind('<Return>', lambda event: button_ok.invoke())
        self.tp_password.bind('<Escape>', lambda event: button_cancel.invoke())

        self.root.wait_window(self.tp_password)

    def tp_password_confirma(self):
        try:
            senha_inserida = self.tp_password_entry.get()
            if senha_inserida == '64286428':
                self.tp_password_feedback = True
                self.fechar_tp_password()                                                                                                                                                   
            else:
                self.tp_password_entry_sinalizer.place(relx=0.5, rely=0.5, anchor='n')
        except:
                self.tp_password_feedback = False

    def tp_password_cancel(self):
        yon = self.get_yes_or_not(self.tp_password, 'Calcelar a inserção da senha?')
        if yon:
            self.fechar_tp_password()
    
    def fechar_tp_password(self):
        if self.tp_password:
            self.tp_password.destroy()

    def imprimir_notas(self, text):
        com_port = 'COM2'  # Ajuste a porta conforme necessário
        baud_rate = 9600
        try:
            with serial.Serial(com_port, baud_rate, timeout=1) as printer:
                # Configurações da impressora
                printer.write(b'\x1B\x21\x00')  # Normal size
                printer.write(text.encode('utf-8'))  # Envia o texto para imprimir
                printer.write(b'\n')  # Quebra de linha
                printer.write(b'\x1D\x56\x41\x00')  # Corte do papel
                print("Nota impressa com sucesso.")
        except Exception as e:
            print(f"Erro ao imprimir a nota: {e}")

    def imprimir_cupom(self, itens, payments ,total_geral, troco, data):
        return
        try:
            nota = []
            # Cabeçalho
            nota.append("***** Ceceu Mini Mercado *****")
            nota.append("Data: " + data)
            nota.append("************************")
            nota.append("\nItem            Qtde   Valor Unit   Total")
            nota.append("------------------------------------------")
            
            # Itens da venda
            for item in itens:
                descricao = item['product_name'][:15]
                quantidade = helper.format_to_float(item['quantity'])
                preco_unitario = helper.format_to_float(item['price'])
                total_item = quantidade * preco_unitario
                nota.append(f"{descricao:<12}   {int(quantidade):<8} R${preco_unitario:<10.2f} R${total_item:.2f}")
            
            nota.append("------------------------------------------")
            nota.append("Forma Pgmt     Valor Pago")
            nota.append("------------------------------------------")

            #forms pgmt
            for payment in payments:
                metodo = payment['method']
                if metodo != 'Dinheiro':
                    if metodo == 'Débito':
                        metodo = 'Cartao Deb.'
                    else:
                        metodo = 'Cartao Cred.'
                    amount = payment['amount']
                else:
                    amount = payment['valor_pago']
                nota.append(f'         {metodo:<15} R${helper.format_to_float(amount):<10.2f}')

            nota.append("------------------------------------------")
            nota.append(f"Total Geral: R${helper.format_to_float(total_geral):<12.2f}")
            nota.append(f'Troco: R${troco:<12.2f}')
            nota.append("\nObrigado pela preferencia!")
            nota.append("************************")
            
            self.imprimir_notas("\n".join(nota))
        except Exception as e:
            CTkMessagebox(self.root, message=f'Erro ao imprimir cupom: {e}', icon='cancel', title='Erro')



    # endregion

    # region MÓDULO IDV

    def abrir_idv_interface(self):
        #Header
        self.tp_idv_label_title = CTkLabel(self.root, text=f'  {NOME_TITULO} {self.version}  ', font=CTkFont('helvetica', 80, 'bold'), compound='right', 
        fg_color='blue', text_color='white', width=self.tela_width, height=150, corner_radius=10)
        self.tp_idv_label_title.place(relx=0.5, rely=0, anchor='n')

        #Treeview para exibir a lista de produtos
        colunas_treeview = ('Código', 'Item', 'Valor Unitário', 'Quantidade', 'Total')
        self.tp_idv_treeview = ttk.Treeview(self.root, columns=colunas_treeview, show='headings',height=20)
        self.tp_idv_treeview.place(relx=0.05, rely=0.23)
        self.tp_idv_treeview.column('Código', width=70, anchor=CENTER)
        self.tp_idv_treeview.column('Item', width=350, anchor=CENTER)
        self.tp_idv_treeview.column('Valor Unitário', width=120, anchor=CENTER)
        self.tp_idv_treeview.column('Quantidade', width=120, anchor=CENTER)
        self.tp_idv_treeview.column('Total', width=120, anchor=CENTER)
        self.tp_idv_treeview.heading('Código', text='CÓD.')
        self.tp_idv_treeview.heading('Item', text='ITEM')
        self.tp_idv_treeview.heading('Valor Unitário', text='VALOR ÚNIT')
        self.tp_idv_treeview.heading('Quantidade', text='QUANT/KG')
        self.tp_idv_treeview.heading('Total', text='TOTAL')

        #treeview busco por nome (fica inativa ate o usuario fazer uso de pesquisa por nome)
        self.tp_idv_hidden_treeview = ttk.Treeview(self.root, style='Hidden.Treeview', columns=(), show='tree',height=6)
        self.tp_idv_hidden_treeview.column('#0', width=700, anchor='w')

        #carrinho variavel
        self.carrinho = []

        #Entry do codbar frame
        self.tp_idv_ilus_codbar = CTkImage(light_image=Image.open(r'images\codbar_ilus.png'), size=(30, 30))
        self.tp_idv_label_ilust_codbar = CTkLabel(self.root, image=self.tp_idv_ilus_codbar, text='')
        self.tp_idv_label_ilust_codbar.place(relx=0.05, rely=0.87)

        self.tp_idv_entry_codbar = CTkEntry(self.root, width=700, height=35, border_color='blue')
        self.tp_idv_entry_codbar.place(relx=0.08, rely=0.87)
        self.tp_idv_entry_codbar.focus_force()

        #Frame preço unitário
        self.tp_idv_frame_status_preco_unitario = CTkFrame(self.root, width=400, height=200, fg_color='white', corner_radius=10)
        self.tp_idv_frame_status_preco_unitario.place(relx=0.65,rely=0.23)
        self.tp_idv_frame_status_preco_unitario_label_0 = CTkLabel(self.tp_idv_frame_status_preco_unitario, text='PREÇO UNIT/KG', font=CTkFont('arial', 35, 'bold'))
        self.tp_idv_frame_status_preco_unitario_label_0.place(relx=0.5,rely=0.02, anchor='n' )
        self.tp_idv_frame_status_preco_unitario_label_1 = CTkLabel(self.tp_idv_frame_status_preco_unitario, text='0,00', font=CTkFont('courier', 80, 'bold'))
        self.tp_idv_frame_status_preco_unitario_label_1.place(relx=0.5,rely=0.4, anchor='n' )

        #Frame preço total
        self.tp_idv_frame_status_subtotal = CTkFrame(self.root, width=400, height=200, fg_color='white', corner_radius=10)
        self.tp_idv_frame_status_subtotal.place(relx=0.65,rely=0.55)
        self.tp_idv_frame_status_subtotal_label_0 = CTkLabel(self.tp_idv_frame_status_subtotal,text='SUBTOTAL', font=CTkFont('arial', 35, 'bold'))
        self.tp_idv_frame_status_subtotal_label_0.place(relx=0.5,rely=0.02, anchor='n' )
        self.tp_idv_frame_status_subtotal_label_1 = CTkLabel(self.tp_idv_frame_status_subtotal, text='0,00', font=CTkFont('courier new', 80, 'bold'))
        self.tp_idv_frame_status_subtotal_label_1.place(relx=0.5,rely=0.4, anchor='n' )

        #frame status
        self.tp_idv_frame_status = CTkFrame(self.root, width=400, height=35, fg_color='transparent')
        self.tp_idv_frame_status.place(relx=0.65, rely=0.87)
        self.tp_idv_frame_status_label = CTkLabel(self.tp_idv_frame_status, text ='Aguardando Código de barras...',font=CTkFont('arial', 20, 'bold'))
        self.tp_idv_frame_status_label.place(relx=0.5, rely=0.02, anchor='n' )

        #footer frame
        self.tp_idv_footer_fonte = CTkFont('arial', 12, 'bold')
        self.tp_idv_footer_width = self.root.winfo_width()
        self.tp_idv_footer_height = 30
        self.tp_idv_footer_y_cordinate = self.root.winfo_height()-self.tp_idv_footer_height

        #limite_disponivel_widgets (usado por pelo modulo Clientes)
        self.tp_idv_limite_disponivel = CTkLabel(self.root, text='Limite disponível:', font=self.tp_cdm_fonte_padrao_bold, fg_color='black', text_color='white')
        self.tp_idv_limite_disponivel_1 = CTkLabel(self.root, text='-', font=CTkFont('arial', 35, 'bold'), fg_color='black', text_color='green')

        self.tp_idv_frame_footer = CTkFrame(self.root, width=self.tp_idv_footer_width, height=self.tp_idv_footer_height, fg_color='blue')
        self.tp_idv_frame_footer.place(relx=0, y=self.tp_idv_footer_y_cordinate)
        self.tp_idv_frame_footer_label_0 = CTkLabel(self.tp_idv_frame_footer, text='F1 - Cadastrar Mercadoria     F2 - Remover item da compra     F3 - Finalizar Compra     F4 - Gerenciar Mercadoria     F5 - Gerenciamento de Clientes     F6 - Fiar Compra       F11 - Gerenciamento de Vendas      F12 - Gerenciar Caixa', 
        font=self.tp_idv_footer_fonte, text_color='white')
        self.tp_idv_frame_footer_label_0.place(relx=0.01)

        #Teclas Config
        self.root.bind('<F1>', lambda event: self.abrir_janela_cadastro_mercadoria())
        self.root.bind('<F2>', lambda event: self.remover_item_da_compra())
        #self.root.bind('<F3>', lambda event: self.finalizar_compra())
        self.root.bind('<F4>', lambda event: self.abrir_gdm())
        self.root.bind('<F5>', lambda event: self.abrir_clientes())
        self.root.bind('<F6>', lambda event: self.abrir_tp_fiar_compra())
        self.root.bind('<F9>', lambda event: self.abrir_gaveta())
        self.root.bind('<F11>', lambda event: self.abrir_tp_gdv())
        self.root.bind('<F12>', lambda event: self.abrir_tp_gdc())
        self.root.bind('<Escape>', lambda event: self.cancelar_compra())
        self.tp_idv_treeview.bind('<Escape>', lambda event: self.cancel_remover_item_na_compra())
        self.tp_idv_hidden_treeview.bind('<Double-1>', lambda event: self.get_product_from_hidden_treeview())
        self.tp_idv_entry_codbar.bind('<Return>', lambda event: self.check_action_to_take())
        self.tp_idv_entry_codbar.bind('<KeyRelease>', lambda event: self.codbar_entry_keyrelease())
        self.tp_idv_treeview.bind('<Return>', lambda event: self.remove_item_selecionado())

        #setando o foco
        self.root.after(AFTER_INTERVALO, self.tp_idv_entry_codbar.focus_set)

    def check_action_to_take(self):
        if tm.time() - self.last_venda_time < 0.5:#vedacao para evitar erro imediatamente apos a finalizacao da compra
            return
        
        if self.tp_idv_entry_codbar.get() == '' and self.get_treeview_itens_number() > 0:
            self.finalizar_compra()
            return

        if self.tp_idv_hidden_treeview.winfo_ismapped():
            self.get_product_from_hidden_treeview()
        else:
            self.read_codbar()

    def codbar_entry_keyrelease(self):
        def limpar_treeview():
            for i in self.tp_idv_hidden_treeview.get_children():
                self.tp_idv_hidden_treeview.delete(i)
        codbar_inserido = self.tp_idv_entry_codbar.get().strip()
        #aqui o sistema checka se existe algum charactere do tipo letra
        check = False
        for char in codbar_inserido:
            if char == '=':
                return
            if char.isalpha():
                check = True
        if check:
            #mostra a treeview
            self.tp_idv_hidden_treeview.place(relx=0.5, rely=0.35, anchor='n')
            self.tp_idv_hidden_treeview.lift()
            #obtem o termo de pesquisa (do codbar entry)
            pesquisa_termo = self.tp_idv_entry_codbar.get()
            # insere resultados
            limpar_treeview()
            pesquisa_resultados = database.search_products(pesquisa_termo, 'descricao')
            for item in pesquisa_resultados:
                self.tp_idv_hidden_treeview.insert('','end', text=item[2])
            #aqui a funcao deixa o primeiro item selecionado (selection_set)
            if self.tp_idv_hidden_treeview.get_children():
                primeiro_item = self.tp_idv_hidden_treeview.get_children()[0]  # Pega o primeiro item
                self.tp_idv_hidden_treeview.selection_set(primeiro_item)  
        else:
            self.tp_idv_hidden_treeview.place_forget()
            
    def get_product_from_hidden_treeview(self):
        if not self.tp_idv_hidden_treeview.selection(): #trata o caso de nao ter nada na treeview
                return
        else:
            #obtendo o sale_id da venda
            selected_item = self.tp_idv_hidden_treeview.selection()
            item_text = self.tp_idv_hidden_treeview.item(selected_item, "text")
            product = database.get_product_by_coluna(item_text, 'descricao')
            self.inserir_item_na_compra(product, 1)
            self.tp_idv_hidden_treeview.place_forget()
            self.tp_idv_entry_codbar.delete(0, END)
            self.tp_idv_entry_codbar.focus_set()

    def read_codbar(self):
        codbar_inserido = self.tp_idv_entry_codbar.get().strip()
        try:
            if '.' in codbar_inserido:#o programa entende aqui quando o usuario está utilizando produto genérico
                #valindando o multiplicador
                multiplicador, valor = codbar_inserido.split('.', 1)
                multiplicador = helper.format_to_float(multiplicador)
                #identificando se tem nome
                nome = None
                if '=' in valor:
                    valor, nome = valor.split('=')
                    if nome.isdigit() and len(nome) < 3:
                        msg = CTkMessagebox(self.root, message=f'Nome do produto genérico não válido', icon='cancel', title='Erro')
                        self.root.wait_window(msg)
                        self.tp_idv_entry_codbar.focus_set()
                        return
                if str(multiplicador).replace('.', '').isdigit() and multiplicador > 0:
                    #validando o valor inserido
                    try:
                        valor = valor.replace(',', '.')
                        float(valor)
                        feedback = list(database.get_product_by_coluna('0000000000000', 'barcode'))
                        feedback[5] = valor
                        #inserindo o nome se tiver
                        if nome:
                            feedback[2] = nome
                        self.inserir_item_na_compra(tuple(feedback), quantidade=multiplicador)
                    except Exception as e:
                        msg = CTkMessagebox(self.root, message=f'Valor do produto genérico não válido', icon='cancel', title='Erro')
                        print(e)
                        self.root.wait_window(msg)
                        self.tp_idv_entry_codbar.focus_set()
                        return
                else:
                    msg = CTkMessagebox(self.root, message=f'O múltiplicador deve ser um NÚMERO INTEIRO.', icon='cancel', title='Erro')
                    self.root.wait_window(msg)
                    self.tp_idv_entry_codbar.focus_set()
                    return
            elif '*' in codbar_inserido:#o programa entende aqui quando o usuario está utilizando multiplicador
                multiplicador, codbar_inserido = codbar_inserido.split('*')
                #validacao do multiplicardor
                if multiplicador.isdigit() and int(multiplicador) > 0:
                    #validacao do codbar
                    if codbar_inserido.isdigit():
                        feedback = database.get_product_by_coluna(codbar_inserido, 'barcode')
                        if not feedback:     
                            self.tp_idv_entry_codbar.delete(0, END)
                            msg = CTkMessagebox(self.root, message=f'Código de barras NÃO encontrado.', icon='cancel', title='Erro')
                            self.root.wait_window(msg)
                            self.tp_idv_entry_codbar.focus_set()
                        else:
                            self.inserir_item_na_compra(feedback, quantidade=multiplicador)
                    else:
                        self.tp_idv_entry_codbar.delete(0, END)
                        msg = CTkMessagebox(self.root, message=f'Código de barras inválido.', icon='cancel', title='Erro')
                        self.root.wait_window(msg)
                        self.tp_idv_entry_codbar.focus_set()
                else:
                    self.tp_idv_entry_codbar.delete(0, END)
                    msg = CTkMessagebox(self.root, message=f'O múltiplicador deve ser um NÚMERO INTEIRO.', icon='cancel', title='Erro')
                    self.root.wait_window(msg)
                    self.tp_idv_entry_codbar.focus_set()
                    return
            else:
                if codbar_inserido.isdigit(): #or codbar_inserido == '0000000000000':
                    feedback = database.get_product_by_coluna(codbar_inserido, 'barcode')
                    self.tp_idv_entry_codbar.delete(0, END)
                    if not feedback:     
                        msg = CTkMessagebox(self.root, message=f'Código de barras NÃO encontrado.', icon='cancel', title='Erro')
                        self.root.wait_window(msg)
                        self.tp_idv_entry_codbar.focus_set()
                    else:
                        self.inserir_item_na_compra(feedback)
                elif codbar_inserido.strip() == None:
                    msg = CTkMessagebox(self.root, message=f'Código de barras NÃO inserido.', icon='cancel', title='Erro')
                    self.root.wait_window(msg) 
                    self.tp_idv_entry_codbar.focus_set()
                else:
                    self.tp_idv_entry_codbar.delete(0, END)
                    msg = CTkMessagebox(self.root, message=f'Código de barras inválido.', icon='cancel', title='Erro')
                    self.root.wait_window(msg)
                    self.tp_idv_entry_codbar.focus_set()

        except Exception as e:
            self.tp_idv_entry_codbar.delete(0, END)
            msg = CTkMessagebox(self.root, message=f'Erro ao buscar a mercadoria no banco de dados: {e}', icon='cancel', title='Erro*')
            self.root.wait_window(msg)
            self.tp_idv_entry_codbar.focus_set()

        finally:
            self.root.after(AFTER_INTERVALO, self.tp_idv_entry_codbar.focus_set)
            
    def inserir_item_na_compra(self, feedback, quantidade=1):
        try:
            #inserir no carrinho
            self.carrinho.append(feedback+ (quantidade, ))
            #obter o index para o item
            index = self.get_treeview_itens_number()+1

            #inserir na treeview
            print(feedback)
            row = helper.formatar_row_para_treeview_da_root(feedback, index, quantidade)
            self.tp_idv_treeview.insert('','end', values=row)
            
            #atualizando o valor unitario
            self.tp_idv_frame_status_preco_unitario_label_1.configure(text=helper.format_to_moeda(row[2]))
            
            #atualizando o subtotal
            self.somar_ao_subtotal(helper.format_to_float(row[-1]))
            self.tp_idv_entry_codbar.delete(0, END)
            self.root.after(AFTER_INTERVALO, self.tp_idv_treeview.yview_moveto(1.0))

        except Exception as e:
            current_time = dt.now().strftime('%Y-%m-%d %H:%M:%S')
            with open('txts/errors.txt', 'a') as a:
                a.write(f'{current_time} - interface.py - inserir item na compra: {e}\n')
            return False
    
    def remover_item_da_compra(self):
        # Verifica se a Treeview não está vazia
        if self.tp_idv_treeview.get_children():
            self.tp_idv_treeview.bind('<Escape>', lambda event: self.cancel_remover_item_na_compra())
            self.tp_idv_frame_status_label.configure(text='Selecione o item a ser removido.')
            self.tp_idv_entry_codbar.configure(state='disabled')
            # Foca na Treeview
            self.tp_idv_treeview.focus_set()
            # Seleciona o primeiro item
            first_item = self.tp_idv_treeview.get_children()[-1]
            self.tp_idv_treeview.selection_set(first_item)
            # Move o foco para o item selecionado
            self.tp_idv_treeview.focus(first_item)
            #apos isso o ENTER acionara a funcao remove_item_selecionado
        else:
            msg = CTkMessagebox(self.root, message=f'Nenhum item foi adicionado à compra.', icon='warning', title='Atenção')
            self.root.wait_window(msg)
            self.tp_idv_entry_codbar.focus_set()
            
        
    def remove_item_selecionado(self):
        selected_item = self.tp_idv_treeview.selection()
        if selected_item:
            item_values = self.tp_idv_treeview.item(selected_item)['values']
            yon_0 = self.get_yes_or_not(self.root, f'Confirmar exclusão do item: {item_values[1]}')
            if yon_0:
                #removen item do carrinho 
                index_to_remove = int(item_values[0])-1
                if self.set_idv_conta_cliente and len(self.oncredit_ids) == len(self.carrinho):
                    self.oncredit_ids.pop(index_to_remove)
                item_removido = self.carrinho.pop(index_to_remove)
                #remove da treeview
                self.tp_idv_treeview.delete(selected_item)
                if self.get_treeview_itens_number() == 0:
                    self.reset_root()
                    return
                #redefinir os items_ids
                self.redefinir_item_indexs_da_compra()
                #subrai do subtotal o total do item
                self.subtrair_do_subtotal(item_values[-1])
                #atualiza o valor unit
                self.update_valor_unit_label()
                #aproveita a funcao abaixo para reverter os efeitos do f'sistema remover item da lista de compras
                self.cancel_remover_item_na_compra()
                        
        else:
            msg = CTkMessagebox(self.root, message=f'Nenhum item selecionado para exclusão', icon='warning', title='Atenção')
            self.root.wait_window(msg)
            self.tp_idv_entry_codbar.focus_set()
            #aproveita a funcao abaixo para reverter os efeitos do f'sistema remover item da lista de compras
            self.cancel_remover_item_na_compra()

    def cancel_remover_item_na_compra(self):
        selected_item = self.tp_idv_treeview.selection()
        self.tp_idv_treeview.selection_remove(selected_item)
        #reabilitar e foca o codbar entry
        self.tp_idv_entry_codbar.configure(state='normal')
        self.root.after(AFTER_INTERVALO, self.tp_idv_entry_codbar.focus_set)
        #reescrever o status label
        self.tp_idv_frame_status_label.configure(text='Aguardando código de barras...')

    def redefinir_item_indexs_da_compra(self):
        # Copiar os valores atuais antes de remover
        itens = []
        for child in self.tp_idv_treeview.get_children():
            valores = self.tp_idv_treeview.item(child, 'values')[1:]  # Ignora o index antigo
            itens.append(valores)

        # Limpa tudo
        for child in self.tp_idv_treeview.get_children():
            self.tp_idv_treeview.delete(child)
            print(f'removi o {child}')

        # Reinsere com novos índices e iids manuais
        for index, valores in enumerate(itens, start=1):
            item = (str(index),) + tuple(valores)
            self.tp_idv_treeview.insert('', 'end', iid=str(index), values=item)
            print(f'Inserí o {item} no iid {index}')


    def update_valor_unit_label(self):
        if self.get_treeview_itens_number() > 0:
            last_item = self.tp_idv_treeview.get_children()[-1] 
            last_unit_value = self.tp_idv_treeview.item(last_item)['values'][-3]
            self.tp_idv_frame_status_preco_unitario_label_1.configure(text=helper.format_to_moeda(last_unit_value))
        else:
            self.tp_idv_frame_status_preco_unitario_label_1.configure(text=helper.format_to_moeda(0))

    def get_treeview_itens_number(self):
        items_len = len(self.tp_idv_treeview.get_children())    
        return items_len

    def somar_ao_subtotal(self, valor):
        self.new_subtotal = helper.format_to_float(self.current_subtotal) + helper.format_to_float(valor)
        if abs(self.new_subtotal) < 1e-10:
            self.new_subtotal = 0.0
        self.tp_idv_frame_status_subtotal_label_1.configure(text=helper.format_to_moeda(self.new_subtotal))
        self.current_subtotal = self.new_subtotal

    def subtrair_do_subtotal(self, valor):
        self.new_subtotal = helper.format_to_float(self.current_subtotal) - helper.format_to_float(valor)
        if abs(self.new_subtotal) < 1e-10:
            self.new_subtotal = 0.0
        self.tp_idv_frame_status_subtotal_label_1.configure(text=helper.format_to_moeda(self.new_subtotal))
        self.current_subtotal = self.new_subtotal

    def cancelar_compra(self):
        if self.tp_idv_treeview.get_children():
            if self.root.focus_get() == self.tp_idv_treeview:
                self.cancel_remover_item_na_compra()
            else:
                yon_0 = self.get_yes_or_not(self.root, f'Confirmar o cancelamnto da compra?')
                if yon_0:
                    self.reset_root()
        else: 
            msg = CTkMessagebox(self.root, message=f'Nenhum item foi adicionado à compra.', icon='warning', title='Atenção')
            self.root.wait_window(msg)
            self.tp_idv_entry_codbar.focus_set()

    def finalizar_compra(self):  
        #verifica se a treeview esta vazia
        if self.get_treeview_itens_number() == 0:
            msg = CTkMessagebox(self.root, message=f'Nenhum item foi adicionado à compra.', icon='warning', title='Atenção')
            self.root.wait_window(msg)
            self.tp_idv_entry_codbar.focus_set()
            return
        if self.yon:
            return
        x = self.abrir_tp_idv_1_0()

    # TP FORMA DE PAGAMENTO

    def abrir_tp_idv_1_0(self):
        self.tp_idv_frame_status_label.configure(text='Finalizando Compra...')
        self.tp_idv_1 = CTkToplevel(self.root)
        self.tp_idv_1.title('Selecionar Forma de Pagamento')
        self.tp_idv_1.protocol('WM_DELETE_WINDOW', self.fechar_tp_idv_1)
        self.tp_idv_1_width = 500
        self.tp_idv_1_height = 500
        self.tp_idv_1_x = self.root.winfo_width()//2 - self.tp_idv_1_width//2   #essa e algumas abaixo, sao linhas que centralizam o tp na root
        self.tp_idv_1_y = self.root.winfo_height()//2 - self.tp_idv_1_height//2
        self.tp_idv_1.geometry(f'{self.tp_idv_1_width}x{self.tp_idv_1_height}+{self.tp_idv_1_x}+{self.tp_idv_1_y}')
        self.tp_idv_1.resizable(False, False)
        self.tp_idv_1.attributes('-topmost', 'true')
        self.tp_idv_1_tp_cdm_fonte_padrao_bold = CTkFont('arial', 20, 'bold')
        self.tp_idv_1_fonte_padrao = CTkFont('arial', 30)
        self.tp_idv_1.grab_set()

        self.total_restante = helper.format_to_float(self.tp_idv_frame_status_subtotal_label_1.cget('text'))
        self.valor_restante_original = self.total_restante
        self.payments = []
        self.troco = 0
        self.desconto = 0

        #widgets config
        
        self.tp_idv_1_label_titlo_seg_button = CTkLabel(self.tp_idv_1, text='Forma de Pagamento:', font=self.tp_idv_1_tp_cdm_fonte_padrao_bold)
        self.tp_idv_1_label_titlo_seg_button.place(relx = 0.5, rely=0.05, anchor='n')

        self.formas_pgmt_ativas_cap = tuple(form_pgmt.capitalize() for form_pgmt in self.formas_pgmt_ativas)
        self.tp_idv_1_form_pgmt_seg_button =CTkSegmentedButton(self.tp_idv_1, values=self.formas_pgmt_ativas_cap, font=self.tp_idv_1_fonte_padrao, text_color='black', fg_color='white', unselected_color='white', unselected_hover_color='white', selected_color='green', selected_hover_color='green')
        self.tp_idv_1_form_pgmt_seg_button.place(relx=0.5, rely=0.2, anchor='n')
        self.tp_idv_1_form_pgmt_seg_button.set(self.formas_pgmt_ativas_cap[0])

        #self.tp_idv_1_valor_entry_label = CTkLabel(self.tp_idv_1, text='', font=self.tp_idv_1_tp_cdm_fonte_padrao_bold)
        #self.tp_idv_1_valor_entry_label.place(relx=0.5, rely=0.4)
        self.tp_idv_1_valor_entry = CTkEntry(self.tp_idv_1, font=CTkFont('courier', 50, 'bold'), width=250)
        self.tp_idv_1_valor_entry.place(relx=0.5, rely=0.4, anchor='n')
        self.tp_idv_1_valor_entry_sinalizer = CTkLabel(self.tp_idv_1, text_color='red', text='Insira um valor válido')

        #self.tp_idv_1_desconto_label = CTkLabel(self.tp_idv_1, text='Desc.: ', font=self.tp_idv_1_tp_cdm_fonte_padrao_bold)
        #self.tp_idv_1_desconto_label.place(relx=0.1, rely=0.6)
        self.tp_idv_1_desconto_entry = CTkEntry(self.tp_idv_1, font=CTkFont('courier', 35, 'bold'), width=250, placeholder_text='Desconto')
        self.tp_idv_1_desconto_entry.place(relx=0.5, rely=0.6, anchor='n')
        self.tp_idv_1_desconto_entry.bind('<KeyRelease>', self.desconto_entry_key_release)
        self.tp_idv_1_desconto_entry_sinalizer = CTkLabel(self.tp_idv_1, text_color='red', text='Insira um desconto válido')

        self.tp_idv_1_valor_restante_titlo = CTkLabel(self.tp_idv_1, text='TOTAL: ', font=self.tp_idv_1_tp_cdm_fonte_padrao_bold)
        self.tp_idv_1_valor_restante_titlo.place(relx=0.25, rely=0.85, anchor='n')
        self.tp_idv_1_valor_restante = CTkLabel(self.tp_idv_1, font=CTkFont('courier', 50, 'bold'), text=helper.format_to_moeda(self.total_restante))
        self.tp_idv_1_valor_restante.place(relx=0.55, rely=0.8, anchor='n')

        #ajuste de foco ao abrir
        self.tp_idv_1.after(AFTER_INTERVALO, self.tp_idv_1_valor_entry.focus_set)

        self.tp_idv_entry_codbar.configure(state='disabled')

        #vinculação de teclas
        self.tp_idv_1.bind('<Escape>', lambda event: self.cancelar_finalizacao_compra(self.tp_idv_1))
        self.tp_idv_1.bind('<Return>', lambda event: self.validate_tp_idv_1())
        self.tp_idv_1.bind('<Right>', lambda event: self.move_to_next_form_pgmt())
        self.tp_idv_1.bind('<Left>', lambda event: self.move_to_previous_form_pgmt())

    def desconto_entry_key_release(self, event=None):
        try:
            #capturando o valor do desconto inserido no entry
            self.tp_idv_1_desconto_entry_sinalizer.place_forget()
            desconto = self.tp_idv_1_desconto_entry.get().replace(',', '.')
            #validando o desconto
            if desconto:
                self.desconto = float(desconto)
            else:
                self.reverter_desconto()
                return
            #subtraindo o valor do desconto do valor a ser pago
            novo_valor_restante = self.total_restante - self.desconto
            if novo_valor_restante < 0:
                novo_valor_restante = 0
            self.tp_idv_1_valor_restante.configure(text=helper.format_to_moeda(novo_valor_restante))

        except Exception as e:#para o caso de valor inválido
            self.tp_idv_1_desconto_entry_sinalizer.place(relx=0.5, rely=0.7, anchor='n')
            self.reverter_desconto()
            print({e})                                                                                                                              

    def reverter_desconto(self):
        self.tp_idv_1_desconto_entry.delete(0, END)
        self.tp_idv_1_valor_restante.configure(text=helper.format_to_moeda(self.valor_restante_original))
        self.total_restante = self.valor_restante_original
        self.desconto = 0

    def validate_tp_idv_1(self):  # forms pgmt
        self.total_restante = helper.format_to_float(self.tp_idv_1_valor_restante.cget('text'))
        self.tp_idv_1_valor_entry_sinalizer.place_forget()
        self.selected_form_pgmt = self.tp_idv_1_form_pgmt_seg_button.get()
        self.valor_inserido = self.tp_idv_1_valor_entry.get().strip().replace(',', '.').replace('-', '')
        self.abrir_gaveta_check = False
        try:
            if not self.valor_inserido:
                self.tp_idv_1_valor_entry.insert(0, helper.format_to_moeda(self.total_restante))
                return
            self.valor_inserido = float(self.valor_inserido)
            if self.selected_form_pgmt == 'Dinheiro':
                # Aqui não bloqueamos pagar dinheiro antes, só checamos valor inválido se quiser
                pass
            else:  # se pgmt NÃO for em dinheiro
                if self.valor_inserido > self.total_restante:
                    # Não pode pagar mais que o restante nas outras formas
                    self.valor_inserido = self.total_restante

            # Confirma operação
            yon_0 = self.get_yes_or_not(self.tp_idv_1, f'Confirmar Operação? {helper.format_to_moeda(self.valor_inserido)} no {self.selected_form_pgmt}.')
            if yon_0:
                self.troco = 0
                if self.selected_form_pgmt == 'Dinheiro':
                    # Troco só se pagamento em dinheiro e valor maior que o restante (última parcela)
                    if self.valor_inserido > self.total_restante:
                        self.troco = self.valor_inserido - self.total_restante
                    else:
                        self.troco = 0
                    self.abrir_gaveta_check = True
                else:
                    self.troco = 0  # Em outras formas não tem troco

                # Aqui registra o pagamento com valor efetivo abatido = valor pago - troco
                pago_abatido = self.valor_inserido - self.troco

                self.payments.append({
                    'method': self.selected_form_pgmt,
                    'amount': helper.format_to_float(pago_abatido),  # valor efetivamente abatido
                    'valor_pago': self.valor_inserido,               # valor que cliente deu
                    'troco': self.troco
                })

                # Atualiza valor restante depois do pagamento
                self.total_restante = round(helper.format_to_float(self.total_restante) - pago_abatido, 2)

                if self.total_restante <= 0:
                    self.fechar_tp_idv_1()
                    self.abrir_tp_idv_2()  # tp_idv_2 == tp_cpf
                else:
                    self.tp_idv_1_valor_restante_titlo.configure(text='Restante:')
                    self.tp_idv_1_valor_restante.configure(text=helper.format_to_moeda(self.total_restante))
                    self.tp_idv_1_valor_entry.delete(0, END)
                    self.tp_idv_1_desconto_entry.destroy()
                    self.tp_idv_1_valor_entry.focus_set()
            else:
                return
        except Exception as e:  # para o caso de valor inválido
            self.tp_idv_1_valor_entry_sinalizer.place(relx=0.5, rely=0.525, anchor='n')
            self.tp_idv_1_valor_entry.focus_set()
            print({e})


    def move_to_next_form_pgmt(self):
        current_value_index = self.formas_pgmt_ativas_cap.index(self.tp_idv_1_form_pgmt_seg_button.get())
        next_index = (current_value_index + 1) % len(self.formas_pgmt_ativas_cap)
        self.tp_idv_1_form_pgmt_seg_button.set(self.formas_pgmt_ativas_cap[next_index])
        if next_index != 0:
            self.tp_idv_1_valor_entry.delete(0, END)
            self.tp_idv_1_valor_entry.insert(0, self.tp_idv_1_valor_restante.cget('text'))
        else:
            self.tp_idv_1_valor_entry.delete(0, END)

    def move_to_previous_form_pgmt(self):
        current_value_index = self.formas_pgmt_ativas_cap.index(self.tp_idv_1_form_pgmt_seg_button.get())
        next_index = (current_value_index - 1) % len(self.formas_pgmt_ativas_cap)
        self.tp_idv_1_form_pgmt_seg_button.set(self.formas_pgmt_ativas_cap[next_index])
        if next_index != 0:
            self.tp_idv_1_valor_entry.delete(0, END)
            self.tp_idv_1_valor_entry.insert(0, self.tp_idv_1_valor_restante.cget('text'))
        else:
            self.tp_idv_1_valor_entry.delete(0, END)

    def cancelar_finalizacao_compra(self, janela):
        yon= self.get_yes_or_not(janela, 'Cancelar a finalização da compra?')
        if yon:
            if self.tp_idv_1:
                self.tp_idv_1.destroy()
            if self.tp_idv_2:
                self.tp_idv_2.destroy()
            self.tp_idv_frame_status_label.configure(text='Aguardando Código de barras...')
            self.tp_idv_entry_codbar.configure(state='normal')

    def fechar_tp_idv_1(self):
        if self.tp_idv_1:
            self.tp_idv_1.destroy()
            self.tp_idv_1 = None
            self.tp_idv_entry_codbar.configure(state='normal')  

    # TP CPF

    def abrir_tp_idv_2(self):
        #janela toplevel para cadastro de produtos
        self.tp_idv_2 = CTkToplevel(self.root)
        self.tp_idv_2.title('Inserir CPF')
        self.tp_idv_2.protocol('WM_DELETE_WINDOW', self.fechar_tp_idv_1)
        self.tp_idv_2_width = 350
        self.tp_idv_2_height = 250
        self.tp_idv_2_x = self.root.winfo_width()//2 - self.tp_idv_2_width//2   #essa e algumas abaixo, sao linhas que centralizam o tp na root
        self.tp_idv_2_y = self.root.winfo_height()//2 - self.tp_idv_2_height//2
        self.tp_idv_2.geometry(f'{self.tp_idv_2_width}x{self.tp_idv_2_height}+{self.tp_idv_2_x}+{self.tp_idv_2_y}')
        self.tp_idv_2.resizable(False, False)
        self.tp_idv_2.attributes('-topmost', 'true')
        self.tp_idv_2_tp_cdm_fonte_padrao_bold = CTkFont('arial', 20, 'bold')
        self.tp_idv_2_fonte_padrao = CTkFont('arial', 30)
        self.tp_idv_2.grab_set()

        self.tp_idv_2_titlo = CTkLabel(self.tp_idv_2, text='Inserir CPF', font=self.tp_idv_2_tp_cdm_fonte_padrao_bold)
        self.tp_idv_2_titlo.place(relx=0.5,rely=0.1, anchor='n')

        self.tp_idv_2_entry = CTkEntry(self.tp_idv_2, font=self.tp_idv_2_fonte_padrao, width=250)
        self.tp_idv_2_entry.place(relx=0.5,rely=0.3, anchor='n')
        self.tp_idv_2_entry_sinalizer = CTkLabel(self.tp_idv_2, text='CPF inválido', text_color='red')

        self.tp_idv_2_troco_restante_titlo = CTkLabel(self.tp_idv_2, text='TROCO:', font=self.tp_idv_1_tp_cdm_fonte_padrao_bold)
        self.tp_idv_2_troco_restante_titlo.place(relx=0.2, rely=0.75, anchor='n')
        self.tp_idv_2_troco_restante = CTkLabel(self.tp_idv_2, font=CTkFont('courier', 50, 'bold'), text=helper.format_to_moeda(self.troco))
        self.tp_idv_2_troco_restante.place(relx=0.6, rely=0.7, anchor='n')

        self.tp_idv_2.after(AFTER_INTERVALO, self.tp_idv_2_entry.focus_set)

        self.tp_idv_2.bind('<Return>', lambda event: self.tp_idv_2_validate())
        self.tp_idv_2.bind('<Escape>', lambda event: self.cancelar_finalizacao_compra(self.tp_idv_2))


    def tp_idv_2_validate(self):#cpf
        self.cpf_inserido = self.tp_idv_2_entry.get().strip()
        if self.cpf_inserido:#se haver cpf
            if self.cpf_inserido.isdigit() and len(self.cpf_inserido) == 11:
                yon = self.get_yes_or_not(self.tp_idv_2, f'Inserir o CPF: {self.cpf_inserido} e finalizar a compra?')
                if yon:
                    self.encerrar_finzalização_da_compra()
                    self.tp_idv_2_fechar
            else:
                self.tp_idv_2_entry_sinalizer.place(relx=0.5,rely=0.7, anchor='n')
        else:
            self.encerrar_finzalização_da_compra()

    def encerrar_finzalização_da_compra(self):
        if self.encerrar_finzalização_da_compra_block:
            return
        try:
            self.encerrar_finzalização_da_compra_block = True
            items = self.get_carrinho_data()#agrupando os dados
            total = self.valor_restante_original
            if self.customer_id:
                self.abrir_tp_password(self.tp_gdc)
                if self.tp_password_feedback:
                    cfm = database.delete_oncredits_by_id_and_insert_sale_into_tables(self.oncredit_ids, self.customer_id, items, self.payments, self.troco, self.desconto)
                    if cfm:
                        self.tocar_notificacao()
                        self.last_venda_time = tm.time()         
                        self.reset_root()
                        msg = CTkMessagebox(self.root, message=f"Os valores foram descontados da conta do cliente de id: {self.customer_id}", icon='check', title='')
                        self.root.wait_window(msg)
                        self.tp_idv_entry_codbar.focus_set()
                        #abrir a gaveta se a condicao estiver satisfeita
                        if self.abrir_gaveta_check:
                            self.abrir_gaveta()
                    else:
                        CTkMessagebox(self.root, message='Erro na hora de descontar os valores da conta do cliente e registrar venda. Operação CANCELADA.', icon='cancel', title='Erro')
                else:
                    print('Senha nao aceita. Operacao descontinuada.')
            else:
                feedback = database.insert_sale_into_tables(items, self.payments, self.troco, self.desconto)#lancar no database
                if not feedback:
                    raise Exception('Erro ao inserir venda no database')
                self.tocar_notificacao()
                self.last_venda_time = tm.time()    
                #self.imprimir_cupom(items, self.payments, total, self.troco, self.desconto, time.strftime("%d/%m/%Y %H:%M"))
                self.reset_root()

        except Exception as e:
            print(e)
            CTkMessagebox(self.root, message=f'Erro na hora de finalizar compra: contate: {self.contato} ou reinicie o PDV.', icon='cancel', title='Erro')
        finally:
            self.encerrar_finzalização_da_compra_block = False


    def limpar_treeview(self):
        try:
            for i in self.tp_idv_treeview.get_children():
                self.tp_idv_treeview.delete(i)
        except:
            print('Erro na hora de limpar treeview')
            return

    def get_carrinho_data(self):
        # Função para extrair os dados do carrinho (cujos items estão demonstrados na treeview)
        items = []
        for index, item in enumerate(self.carrinho, start=1):#percorrendo o carrinho e criando um dict para cada item
            product_id = item[0]
            product_name = item[2]
            quantity = item[-1]
            price = item[5]
            
            items.append({
                'product_id': product_id,
                'item_id': index,
                'product_name': product_name,
                'quantity': int(quantity),
                'price': float(price)
            })
        return items

    def tp_idv_2_fechar(self):
        if self.tp_idv_2:
            self.tp_idv_2.destroy()
            self.tp_idv_2 = None

    def reset_root(self, event=None):
        self.tp_idv_label_title.configure(text=f'  {NOME_TITULO} {self.version}  ')
        self.tp_idv_frame_status_label.configure(text='Aguardando Código de barras...')
        self.tp_idv_frame_status_subtotal_label_1.configure(text='0,00')
        self.tp_idv_frame_status_preco_unitario_label_1.configure(text='0,00')
        self.current_subtotal = helper.format_to_moeda(0) #subtotal atual
        self.desconto_inserido = 0
        self.limpar_treeview()
        self.tp_idv_2_fechar()  
        self.fechar_tp_idv_1()
        self.tp_idv_entry_codbar.configure(state='normal')
        self.customer_id = 0
        self.oncredit_ids = []
        self.tp_password_feedback = False
        self.set_idv_conta_cliente = False
        self.cliente_selecionado = ''
        self.yon = False
        self.carrinho = []
        self.tp_idv_limite_disponivel.place_forget()
        self.tp_idv_limite_disponivel_1.place_forget()

        self.root.after(AFTER_INTERVALO, self.tp_idv_entry_codbar.focus_set)

    def imprimir_cupom(self, itens, payments ,total_geral, troco, desconto, data):
        return
        try:
            nota = []
            # Cabeçalho
            nota.append("***** Ceceu Mini Mercado *****")
            nota.append("Data: " + data)
            nota.append("************************")
            nota.append("\nItem            Qtde   Valor Unit   Total")
            nota.append("------------------------------------------")
            
            # Itens da venda
            for item in itens:
                descricao = item['product_name'][:15]
                quantidade = helper.format_to_float(item['quantity'])
                preco_unitario = helper.format_to_float(item['price'])
                total_item = quantidade * preco_unitario
                nota.append(f"{descricao:<15}   {int(quantidade):<8} R${preco_unitario:<10.2f} R${total_item:.2f}")
            
            nota.append("------------------------------------------")
            nota.append("Forma Pgmt     Valor Pago")
            nota.append("------------------------------------------")

            #forms pgmt
            for payment in payments:
                metodo = payment['method']
                if metodo != 'Dinheiro':
                    if metodo == 'Débito':
                        metodo = 'Cartao Deb.'
                    else:
                        metodo = 'Cartao Cred.'
                    amount = payment['amount']
                else:
                    amount = payment['valor_pago']
                nota.append(f'         {metodo:<15} R${helper.format_to_float(amount):<10.2f}')

            total_geral = helper.format_to_float(total_geral)
            desconto = helper.format_to_float(desconto)
            total_final = total_geral - desconto

            nota.append("------------------------------------------")
            nota.append(f"Total Geral: R${total_geral:<12.2f}")
            nota.append(f'Desconto: R${desconto:<12.2f}')
            nota.append(f"Total Final: R${total_final:<12.2f}")
            nota.append(f'Troco: R${troco:<12.2f}')
            nota.append("\nObrigado pela preferencia!")
            nota.append("************************")
            
            self.imprimir_notas("\n".join(nota), cupom=True)
        except Exception as e:
            CTkMessagebox(self.root, message=f'Erro ao imprimir cupom: {e}', icon='cancel', title='Erro')

    def imprimir_notas(self, text, cupom=False):
        print(text)
        com_port = 'COM2'  # Ajuste a porta conforme necessário
        baud_rate = 96005
        try:
            with serial.Serial(com_port, baud_rate, timeout=1) as printer:
                # Configurações da impressora
                printer.write(b'\x1B\x21\x00')  # Normal size
                printer.write(text.encode('utf-8'))  # Envia o texto para imprimir
                printer.write(b'\n')  # Quebra de linha
                printer.write(b'\x1D\x56\x41\x00')  # Corte do papel
                print("Nota impressa com sucesso.")
        except Exception as e:
            print(f"Erro ao imprimir a nota: {e}")

    # endregion

    # region MODULO CDM (CADASTRO DE MERCADORIA)

    def abrir_janela_cadastro_mercadoria(self, event=None):
        #cond que verifica se a janela ja existe antes de abri-la novamente
        if self.tp_cdm is not None:
            print('A janela não pode ser aberta pois já existe')
            return

        ilust_titlo = CTkImage(light_image=Image.open(r'images\ilustracao_registro_mercadoria.png'), size=(100, 100))
        ilust_lupa = CTkImage(light_image=Image.open(r'images\websearch.png'), size=(40, 40))

        #configuração do tp
        self.tp_cdm = CTkToplevel(self.root)
        self.tp_cdm.title('Cadastro de Produto')
        self.tp_cdm.protocol('WM_DELETE_WINDOW', self.fechar_janela_cadastro)
        self.tp_cdm.resizable(False, False)
        self.tp_cdm_width = 1200
        self.tp_cdm_height = 650
        self.tp_cdm_x = self.root.winfo_width()//2 - self.tp_cdm_width//2
        self.tp_cdm_y = self.root.winfo_height()//2 - self.tp_cdm_height//2
        self.tp_cdm.geometry(f'{self.tp_cdm_width}x{self.tp_cdm_height}+{self.tp_cdm_x}+{self.tp_cdm_y}')
        self.tp_cdm.attributes('-topmost', 'true')
        #variaveis de controle de tp
        self.check_cod_block = False
        self.tp_cdm_validate_block = False
        self.first_enter = False
        #fontes
        #coloquei no top do codigo geral

	#widgets
        self.tp_cdm_label_titlo = CTkLabel(self.tp_cdm, text='Registro de Mercadoria:', font=CTkFont('arial', 35, 'bold'), image=ilust_titlo, compound='left')
        self.tp_cdm_label_titlo.place(relx = 0.5, rely=0.02, anchor='n')

        self.tp_cdm_label_codbar = CTkLabel(self.tp_cdm, text='Cód. barras:', font=self.tp_cdm_fonte_padrao_bold)
        self.tp_cdm_label_codbar.place(relx=0.02, rely=0.32)
        self.tp_cdm_entry_codbar = CTkEntry(self.tp_cdm, font=self.tp_cdm_fonte_padrao_bold, width=400, height=50)
        self.tp_cdm_entry_codbar.place(relx=0.13, rely=0.30)
        self.tp_cdm_entry_codbar_sinalizer = CTkLabel(self.tp_cdm ,text_color='red')
        self.tp_cdm_ignore_enter = False

        self.tp_cdm_label_descricao = CTkLabel(self.tp_cdm, text='Descrição:', font=self.tp_cdm_fonte_padrao_bold)
        self.tp_cdm_label_descricao.place(relx=0.02, rely=0.45)
        self.tp_cdm_combobox_descricao = CTkEntry(self.tp_cdm, font=self.tp_cdm_fonte_padrao_bold, width=400, height=50)
        self.tp_cdm_combobox_descricao.place(relx=0.13, rely=0.43)
        self.tp_cdm_combobox_descricao_sinalizer = CTkLabel(self.tp_cdm ,text_color='red')

        self.tp_cdm_label_categoria = CTkLabel(self.tp_cdm, text='Categoria:', font=self.tp_cdm_fonte_padrao_bold)
        self.tp_cdm_label_categoria.place(relx=0.02, rely=0.58)
        self.tp_cdm_combobox_categoria = CTkComboBox(self.tp_cdm, values= self.mercadoria_categorias, font=self.tp_cdm_fonte_padrao_bold, width=400, height=50)
        self.tp_cdm_combobox_categoria.place(relx=0.13, rely=0.56)
        self.tp_cdm_combobox_categoria.set('')
        self.tp_cdm_combobox_categoria_sinalizer = CTkLabel(self.tp_cdm ,text_color='red')

        #COLUMN 2

        self.tp_cdm_label_precocompra = CTkLabel(self.tp_cdm, text='Preço Compra:', font=self.tp_cdm_fonte_padrao_bold)
        self.tp_cdm_label_precocompra.place(relx=0.52, rely=0.32)
        self.tp_cdm_entry_precocompra = CTkEntry(self.tp_cdm, font=self.tp_cdm_fonte_padrao_bold, width=400, height=50)
        self.tp_cdm_entry_precocompra.place(relx=0.64, rely=0.30)
        self.tp_cdm_entry_precocompra_sinalizer = CTkLabel(self.tp_cdm ,text_color='red')

        self.tp_cdm_label_precovenda = CTkLabel(self.tp_cdm, text='Preço Venda:', font=self.tp_cdm_fonte_padrao_bold)
        self.tp_cdm_label_precovenda.place(relx=0.52, rely=0.45)
        self.tp_cdm_entry_precovenda = CTkEntry(self.tp_cdm, font=self.tp_cdm_fonte_padrao_bold, width=400, height=50)
        self.tp_cdm_entry_precovenda.place(relx=0.64, rely=0.43)
        self.tp_cdm_entry_precovenda_sinalizer = CTkLabel(self.tp_cdm ,text_color='red')

        self.tp_cdm_label_fornecedor = CTkLabel(self.tp_cdm, text='Fornecedor:', font=self.tp_cdm_fonte_padrao_bold)
        self.tp_cdm_label_fornecedor.place(relx=0.52, rely=0.58)
        self.tp_cdm_combobox_fornecedor = CTkComboBox(self.tp_cdm, values= self.fornecedores, font=self.tp_cdm_fonte_padrao_bold, width=400, height=50)
        self.tp_cdm_combobox_fornecedor.place(relx=0.64, rely=0.56)
        self.tp_cdm_combobox_fornecedor.set('')
        self.tp_cdm_combobox_fornecedor_sinalizer = CTkLabel(self.tp_cdm ,text_color='red')

        #campo para botão de registro
        self.tp_cdm_botao_registrar_mercadoria = CTkButton(self.tp_cdm, width=200 ,height=50,text='Registrar', font=self.tp_cdm_fonte_padrao_bold, 
        command=lambda: self.validar_dados_do_registro_de_mercadorias(), text_color='black', fg_color='orange', hover_color='orange')
        self.tp_cdm_botao_registrar_mercadoria.place(relx=0.5, rely=0.95, anchor='s')

        self.tp_cdm.after(AFTER_INTERVALO, self.tp_cdm_entry_codbar.focus_set)

        #vinculações de teclas
        self.tp_cdm.bind('<Escape>', lambda event: self.fechar_janela_cadastro())
        self.tp_cdm.bind('<Return>', lambda event: self.tp_cdm_botao_registrar_mercadoria.invoke())

    def validar_dados_do_registro_de_mercadorias(self):
        if not self.first_enter:
            self.first_enter = True
            return
        if self.tp_cdm_validate_block:
            return
        try:
            self.tp_cdm_validate_block=True
            self.tp_cdm_clear_sinalizers()
            codbar_inserido = self.tp_cdm_entry_codbar.get().strip()
            if not codbar_inserido:
                self.tp_cdm_entry_codbar_sinalizer.configure(text='O código de barras não foi inserido.')
                self.tp_cdm_entry_codbar_sinalizer.place(relx=0.13, rely=0.38)
                self.tp_cdm_entry_codbar.focus_set()
                return
            elif not codbar_inserido.isdigit():
                self.tp_cdm_entry_codbar_sinalizer.configure(text='O código de barras deve ser numérico.')
                self.tp_cdm_entry_codbar_sinalizer.place(relx=0.13, rely=0.38)
                self.tp_cdm_entry_codbar.focus_set()
                return
            elif len(codbar_inserido) < 1:
                self.tp_cdm_entry_codbar_sinalizer.configure(text='O código de barras deve conter 13 dígitos.')
                self.tp_cdm_entry_codbar_sinalizer.place(relx=0.13, rely=0.38)
                self.tp_cdm_entry_codbar.focus_set()
                return
            codbar_check = database.get_product_by_coluna(codbar_inserido, 'barcode')
            if codbar_check:
                CTkMessagebox(self.tp_cdm, title='Erro.', message=f'O Código de barras informado já está cadastrado para o produto {codbar_check[2].upper()}.')
            desc_inserida = self.tp_cdm_combobox_descricao.get().strip()
            if not desc_inserida:
                self.tp_cdm_combobox_descricao_sinalizer.configure(text='A descrição da mercadoria não foi inserida.')
                self.tp_cdm_combobox_descricao_sinalizer.place(relx=0.13, rely=0.51)
                self.tp_cdm_combobox_descricao.focus_set()
                return
            elif desc_inserida.isdigit():
                self.tp_cdm_combobox_descricao_sinalizer.configure(text='A descrição da mercadoria deve conter letras.')
                self.tp_cdm_combobox_descricao_sinalizer.place(relx=0.13, rely=0.51)
                self.tp_cdm_combobox_descricao.focus_set()
                return
            categoria_inserida = self.tp_cdm_combobox_categoria.get().strip()
            if categoria_inserida not in self.mercadoria_categorias:
                self.tp_cdm_combobox_categoria_sinalizer.configure(text='Selecione uma categoria válida.')
                self.tp_cdm_combobox_categoria_sinalizer.place(relx=0.13, rely=0.64)
                self.tp_cdm_combobox_categoria.focus_set()
                return
            precocompra_inserido = self.tp_cdm_entry_precocompra.get().replace(',', '.').strip()
            if not precocompra_inserido:
                self.tp_cdm_entry_precocompra_sinalizer.configure(text='O preco de compra não foi inserido')
                self.tp_cdm_entry_precocompra_sinalizer.place(relx=0.70, rely=0.38)
                self.tp_cdm_entry_precocompra.focus_set()
                return
            if precocompra_inserido:            
                try:
                    if float(precocompra_inserido) < 0:
                        raise Exception
                except:
                    self.tp_cdm_entry_precocompra_sinalizer.configure(text='Preço inválido')
                    self.tp_cdm_entry_precocompra_sinalizer.place(relx=0.70, rely=0.38)
                    self.tp_cdm_entry_precocompra.focus_set()
                    return
            
            precovenda_inserido = self.tp_cdm_entry_precovenda.get().replace(',', '.').strip()
            if not precovenda_inserido:
                self.tp_cdm_entry_precovenda_sinalizer.configure(text='O preco de venda não foi inserido')
                self.tp_cdm_entry_precovenda_sinalizer.place(relx=0.70, rely=0.51)
                self.tp_cdm_entry_precovenda.focus_set()
                return
            if precovenda_inserido:            
                try:
                    if float(precovenda_inserido) < 0:
                        raise Exception
                except:
                    self.tp_cdm_entry_precovenda_sinalizer.configure(text='Preço inválido')
                    self.tp_cdm_entry_precovenda_sinalizer.place(relx=0.70, rely=0.51)
                    self.tp_cdm_entry_precovenda.focus_set()
                    return
            fornecedor_inserido = self.tp_cdm_combobox_fornecedor.get().strip()
            if fornecedor_inserido not in self.fornecedores:
                self.tp_cdm_combobox_fornecedor_sinalizer.configure(text='Selecione um fornecedor válido.')
                self.tp_cdm_combobox_fornecedor_sinalizer.place(relx=0.70, rely=0.64)
                self.tp_cdm_combobox_fornecedor.focus_set()
                return
      
            row = (codbar_inserido, desc_inserida.lower(),  categoria_inserida.lower(), precocompra_inserido, precovenda_inserido, '0', '0', fornecedor_inserido.lower(), dt.now().strftime('%Y-%m-%d %H:%M:%S'), dt.now().strftime('%Y-%m-%d %H:%M:%S'))
            cfm_1 = self.get_yes_or_not(self.tp_cdm)
            if cfm_1:
                cfm_2 = database.insert_product(row)
                if cfm_2 == True:
                    CTkMessagebox(self.tp_cdm, message="Produto cadastrado com sucesso!", icon='check', title='')
                    self.tp_cdm_widgets_clear()
                    return
                else:
                    CTkMessagebox(self.tp_cdm, title='Erro.', message=f'Erro ao registrar mercadoria: Considere contatar a assistência: {self.contato}.')
            else:
                return
        except Exception as e:
            print(e)
            CTkMessagebox(self.tp_cdm, title='Erro.', message=f'Erro ao validar os dados inseridos: {e}. Considere contatar a assistência: {self.contato}')
        finally:
            self.tp_cdm_validate_block = False

    def tp_cdm_clear_sinalizers(self):
        #removendo os sinalizers labels
        self.tp_cdm_entry_codbar_sinalizer.place_forget()
        self.tp_cdm_combobox_descricao_sinalizer.place_forget()
        self.tp_cdm_combobox_categoria_sinalizer.place_forget()
        self.tp_cdm_entry_precocompra_sinalizer.place_forget()
        self.tp_cdm_entry_precovenda_sinalizer.place_forget()
        self.tp_cdm_combobox_fornecedor_sinalizer.place_forget()

    def tp_cdm_widgets_clear(self):
        #clearning entrys 
        self.tp_cdm_entry_codbar.delete(0, END)
        self.tp_cdm_combobox_descricao.delete(0, END)
        self.tp_cdm_combobox_categoria.set('')
        self.tp_cdm_entry_precocompra.delete(0, END)
        self.tp_cdm_entry_precovenda.delete(0, END)
        self.tp_cdm_combobox_fornecedor.set('')

    def fechar_janela_cadastro(self):
        if self.tp_cdm:
            self.tp_cdm.destroy()
            self.tp_cdm = None

    # endregion

    # region MODULO GDM (GERENCIAMENTO DE MERCADORIA)

    def abrir_gdm(self):
        if not self.tp_gdm:
            self.tp_gdm = CTkToplevel(self.root)
            self.tp_gdm.title('Visualizar e Editar Mercadoria')
            self.tp_gdm.protocol('WM_DELETE_WINDOW', self.fechar_gdm)
            self.tp_gdm_width = 1200
            self.tp_gdm_height = 600
            self.tp_gdm_x = self.root.winfo_width()//2 - self.tp_gdm_width//2   #essa e algumas abaixo, sao linhas que centralizam o tp na root
            self.tp_gdm_y = self.root.winfo_height()//2 - self.tp_gdm_height//2
            self.tp_gdm.geometry(f'{self.tp_gdm_width}x{self.tp_gdm_height}+{self.tp_gdm_x}+{self.tp_gdm_y}')
            self.tp_gdm.resizable(False, False)
            self.tp_gdm.attributes('-topmost', 'true')

            ilust_titlo = CTkImage(light_image=Image.open(r'images\ilustracao_pesquisa_mercadoria.png'), size=(100, 100))

            self.tp_gdm_label_titlo = CTkLabel(self.tp_gdm,  text='', image=ilust_titlo)
            self.tp_gdm_label_titlo.place(relx = 0.1, rely=0.05, anchor='n')

            # Entry para inserir a busca
            self.search_entry = CTkEntry(self.tp_gdm, width=750, height=50, placeholder_text="Nome ou código de barras...", font=self.fonte_basic, border_color='green')
            self.search_entry.place(relx=0.2,rely=0.1)
            self.search_entry.bind("<KeyRelease>", self.search_product)
            
            # Treeview para exibir os resultados de forma tabular
            self.tp_gdm_treeview_search_columns = ('id', 'barcode','descricao', 'categoria', 'precocompra', 'precovenda', 'estoque', 'fornecedor')
            self.tp_gdm_treeview_search = ttk.Treeview(self.tp_gdm, columns=self.tp_gdm_treeview_search_columns, show="headings", height=20)
            self.tp_gdm_treeview_search.column(self.tp_gdm_treeview_search_columns[0], width=50, anchor=CENTER)
            self.tp_gdm_treeview_search.column(self.tp_gdm_treeview_search_columns[1], width=135, anchor=CENTER)
            self.tp_gdm_treeview_search.column(self.tp_gdm_treeview_search_columns[2], width=280, anchor=CENTER)
            self.tp_gdm_treeview_search.column(self.tp_gdm_treeview_search_columns[3], width=125, anchor=CENTER)
            self.tp_gdm_treeview_search.column(self.tp_gdm_treeview_search_columns[4], width=100, anchor=CENTER)
            self.tp_gdm_treeview_search.column(self.tp_gdm_treeview_search_columns[5], width=100, anchor=CENTER)
            self.tp_gdm_treeview_search.column(self.tp_gdm_treeview_search_columns[6], width=100, anchor=CENTER)
            self.tp_gdm_treeview_search.column(self.tp_gdm_treeview_search_columns[7], width=100, anchor=CENTER)
            self.tp_gdm_treeview_search.heading(self.tp_gdm_treeview_search_columns[0], text="ID", )
            self.tp_gdm_treeview_search.heading(self.tp_gdm_treeview_search_columns[1], text="Cód. Barras", )
            self.tp_gdm_treeview_search.heading(self.tp_gdm_treeview_search_columns[2], text="Descrição")
            self.tp_gdm_treeview_search.heading(self.tp_gdm_treeview_search_columns[3], text="Categoria")
            self.tp_gdm_treeview_search.heading(self.tp_gdm_treeview_search_columns[4], text="Preço Compra")
            self.tp_gdm_treeview_search.heading(self.tp_gdm_treeview_search_columns[5], text="Preço venda")
            self.tp_gdm_treeview_search.heading(self.tp_gdm_treeview_search_columns[6], text='Estoque')
            self.tp_gdm_treeview_search.heading(self.tp_gdm_treeview_search_columns[7], text='Fornecedor') 
            self.tp_gdm_treeview_search.place(relx=0.5, rely=0.25, anchor='n')

            self.update_search_treeview()

            self.tp_gdm.after(AFTER_INTERVALO, self.search_entry.focus_set)

            self.tp_gdm.bind('<Escape>', self.fechar_gdm)
            self.tp_gdm_treeview_search.bind('<Double-1>', self.abrir_tp_gdm_tp_editar_mercadoria)

    def search_product(self, event=None):
        search_term = self.search_entry.get()
        if search_term.isdigit():   #para o caso de ser código de barras
            search_by = 'barcode'
        else:                       #para o caso de ser pelo nome
            search_by = 'descricao'
        # Limpa a Treeview antes de exibir os novos resultados
        for item in self.tp_gdm_treeview_search.get_children():
            self.tp_gdm_treeview_search.delete(item)
        # Chama a função de busca no banco de dados do backend
        results = database.search_products(search_term, search_by)
        if results:
            # Adiciona os resultados na Treeview
            for row in results:
                self.tp_gdm_treeview_search.insert('', END, values=helper.formatar_row_para_treeview_da_busca(row))
        
    def update_search_treeview(self):
        # Limpa a Treeview antes de exibir os novos resultados
        for item in self.tp_gdm_treeview_search.get_children():
            self.tp_gdm_treeview_search.delete(item)
        # Chama a função de busca no banco de dados do backend
        results = database.get_all_products()
        if results:
            # Adiciona os resultados na Treeview
            for row in results:
                self.tp_gdm_treeview_search.insert('', END, values=helper.formatar_row_para_treeview_da_busca(row))

    def fechar_gdm(self, event=None):
        if self.tp_gdm:
            self.tp_gdm.destroy()
            self.tp_gdm = None

    def abrir_tp_gdm_tp_editar_mercadoria(self, event=None):
        selected_item = self.tp_gdm_treeview_search.focus()
        self.item_values = self.tp_gdm_treeview_search.item(selected_item, "values")
        self.item_values = database.get_product_by_coluna(self.item_values[0], 'id')
        if not self.item_values:
            self.search_entry.focus_set()
            return
        if self.tp_gdm_tp_editar_mercadoria:
            return
        
        #janela toplevel para edição dos dados da mercadoria
        self.tp_gdm_tp_editar_mercadoria = CTkToplevel(self.root)
        self.tp_gdm_tp_editar_mercadoria.title('Editar Mercadoria')
        self.tp_gdm_tp_editar_mercadoria.protocol('WM_DELETE_WINDOW', self.fechar_tp_gdm_tp_editar_mercadoria)
        self.tp_gdm_tp_editar_mercadoria.resizable(False, False)
        self.tp_gdm_tp_editar_mercadoria_width = 1200
        self.tp_gdm_tp_editar_mercadoria_height = 650
        self.tp_gdm_tp_editar_mercadoria_x = self.root.winfo_width()//2 - self.tp_gdm_tp_editar_mercadoria_width//2
        self.tp_gdm_tp_editar_mercadoria_y = self.root.winfo_height()//2 - self.tp_gdm_tp_editar_mercadoria_height//2
        self.tp_gdm_tp_editar_mercadoria.geometry(f'{self.tp_gdm_tp_editar_mercadoria_width}x{self.tp_gdm_tp_editar_mercadoria_height}+{self.tp_gdm_tp_editar_mercadoria_x}+{self.tp_gdm_tp_editar_mercadoria_y}')
        self.tp_gdm_tp_editar_mercadoria.attributes('-topmost', 'true')
        self.tp_gdm_tp_editar_mercadoria_validate_block = False

        ilust_titlo = CTkImage(light_image=Image.open(r'images\ilustracao_edita_mercadoria.png'), size=(100, 100))

        #fontes
        self.tp_gdm_fonte_padrao_bold = CTkFont('arial', 18, 'bold')
        self.tp_gdm_fonte_padrao = CTkFont('arial', 20)

        #widgets
        self.tp_gdm_tp_editar_mercadoria_label_titlo = CTkLabel(self.tp_gdm_tp_editar_mercadoria, text='Editar Mercadoria:', font=CTkFont('arial', 35, 'bold'), image=ilust_titlo, compound='left')
        self.tp_gdm_tp_editar_mercadoria_label_titlo.place(relx = 0.5, rely=0.02, anchor='n')

        self.tp_gdm_tp_editar_mercadoria_label_codbar = CTkLabel(self.tp_gdm_tp_editar_mercadoria, text='Cód. barras:', font=self.tp_gdm_fonte_padrao_bold)
        self.tp_gdm_tp_editar_mercadoria_label_codbar.place(relx=0.02, rely=0.22)
        self.tp_gdm_tp_editar_mercadoria_entry_codbar = CTkEntry(self.tp_gdm_tp_editar_mercadoria, font=self.tp_gdm_fonte_padrao, width=400, height=50)
        self.tp_gdm_tp_editar_mercadoria_entry_codbar.place(relx=0.13, rely=0.20)
        self.tp_gdm_tp_editar_mercadoria_entry_codbar_sinalizer = CTkLabel(self.tp_gdm_tp_editar_mercadoria ,text_color='red')
        self.tp_gdm_tp_editar_mercadoria_entry_codbar.insert(0, self.item_values[1])
        self.tp_gdm_tp_editar_mercadoria_entry_codbar.configure(state='disabled')

        self.tp_gdm_tp_editar_mercadoria_label_descricao = CTkLabel(self.tp_gdm_tp_editar_mercadoria, text='Descrição:', font=self.tp_gdm_fonte_padrao_bold)
        self.tp_gdm_tp_editar_mercadoria_label_descricao.place(relx=0.02, rely=0.35)
        self.tp_gdm_tp_editar_mercadoria_entry_descricao = CTkEntry(self.tp_gdm_tp_editar_mercadoria, font=self.tp_gdm_fonte_padrao, width=400, height=50)
        self.tp_gdm_tp_editar_mercadoria_entry_descricao.place(relx=0.13, rely=0.33)
        self.tp_gdm_tp_editar_mercadoria_entry_descricao_sinalizer = CTkLabel(self.tp_gdm_tp_editar_mercadoria ,text_color='red')
        self.tp_gdm_tp_editar_mercadoria_entry_descricao.insert(0, self.item_values[2].capitalize())


        self.tp_gdm_tp_editar_mercadoria_label_categoria = CTkLabel(self.tp_gdm_tp_editar_mercadoria, text='Categoria:', font=self.tp_gdm_fonte_padrao_bold)
        self.tp_gdm_tp_editar_mercadoria_label_categoria.place(relx=0.02, rely=0.48)
        self.tp_gdm_tp_editar_mercadoria_combobox_categoria = CTkComboBox(self.tp_gdm_tp_editar_mercadoria, values= self.mercadoria_categorias, font=self.tp_gdm_fonte_padrao, width=400, height=50)
        self.tp_gdm_tp_editar_mercadoria_combobox_categoria.place(relx=0.13, rely=0.46)
        self.tp_gdm_tp_editar_mercadoria_combobox_categoria_sinalizer = CTkLabel(self.tp_gdm_tp_editar_mercadoria ,text_color='red')
        self.tp_gdm_tp_editar_mercadoria_combobox_categoria.set(self.item_values[3].capitalize())

        self.tp_gdm_tp_editar_mercadoria_label_fornecedor = CTkLabel(self.tp_gdm_tp_editar_mercadoria, text='Fornecedor:', font=self.tp_gdm_fonte_padrao_bold)
        self.tp_gdm_tp_editar_mercadoria_label_fornecedor.place(relx=0.02, rely=0.61)
        self.tp_gdm_tp_editar_mercadoria_combobox_fornecedor = CTkComboBox(self.tp_gdm_tp_editar_mercadoria, values= self.fornecedores, font=self.tp_gdm_fonte_padrao, width=400, height=50)
        self.tp_gdm_tp_editar_mercadoria_combobox_fornecedor.place(relx=0.13, rely=0.59)
        self.tp_gdm_tp_editar_mercadoria_combobox_fornecedor_sinalizer = CTkLabel(self.tp_gdm_tp_editar_mercadoria ,text_color='red')
        self.tp_gdm_tp_editar_mercadoria_combobox_fornecedor.set(self.item_values[8].capitalize())


        #COLUMN 2

        self.tp_gdm_tp_editar_mercadoria_label_precocompra = CTkLabel(self.tp_gdm_tp_editar_mercadoria, text='Preço Compra:', font=self.tp_gdm_fonte_padrao_bold)
        self.tp_gdm_tp_editar_mercadoria_label_precocompra.place(relx=0.52, rely=0.22)
        self.tp_gdm_tp_editar_mercadoria_entry_precocompra = CTkEntry(self.tp_gdm_tp_editar_mercadoria, font=self.tp_gdm_fonte_padrao, width=400, height=50)
        self.tp_gdm_tp_editar_mercadoria_entry_precocompra.place(relx=0.64, rely=0.20)
        self.tp_gdm_tp_editar_mercadoria_entry_precocompra_sinalizer = CTkLabel(self.tp_gdm_tp_editar_mercadoria ,text_color='red')
        self.tp_gdm_tp_editar_mercadoria_entry_precocompra.insert(0, self.item_values[4])


        self.tp_gdm_tp_editar_mercadoria_label_precovenda = CTkLabel(self.tp_gdm_tp_editar_mercadoria, text='Preço Venda:', font=self.tp_gdm_fonte_padrao_bold)
        self.tp_gdm_tp_editar_mercadoria_label_precovenda.place(relx=0.52, rely=0.35)
        self.tp_gdm_tp_editar_mercadoria_entry_precovenda = CTkEntry(self.tp_gdm_tp_editar_mercadoria, font=self.tp_gdm_fonte_padrao, width=400, height=50)
        self.tp_gdm_tp_editar_mercadoria_entry_precovenda.place(relx=0.64, rely=0.33)
        self.tp_gdm_tp_editar_mercadoria_entry_precovenda_sinalizer = CTkLabel(self.tp_gdm_tp_editar_mercadoria ,text_color='red')
        self.tp_gdm_tp_editar_mercadoria_entry_precovenda.insert(0, self.item_values[5])


        self.tp_gdm_tp_editar_mercadoria_label_estoque = CTkLabel(self.tp_gdm_tp_editar_mercadoria, text='Estoque:', font=self.tp_gdm_fonte_padrao_bold)
        self.tp_gdm_tp_editar_mercadoria_label_estoque.place(relx=0.52, rely=0.48)
        self.tp_gdm_tp_editar_mercadoria_entry_estoque = CTkEntry(self.tp_gdm_tp_editar_mercadoria, font=self.tp_gdm_fonte_padrao, width=400, height=50)
        self.tp_gdm_tp_editar_mercadoria_entry_estoque.place(relx=0.64, rely=0.46)
        self.tp_gdm_tp_editar_mercadoria_entry_estoque_sinalizer = CTkLabel(self.tp_gdm_tp_editar_mercadoria ,text_color='red')
        self.tp_gdm_tp_editar_mercadoria_entry_estoque.insert(0, self.item_values[6])


        self.tp_gdm_tp_editar_mercadoria_label_estoqueminimo = CTkLabel(self.tp_gdm_tp_editar_mercadoria, text='Estoque Min.:', font=self.tp_gdm_fonte_padrao_bold)
        self.tp_gdm_tp_editar_mercadoria_label_estoqueminimo.place(relx=0.52, rely=0.61)
        self.tp_gdm_tp_editar_mercadoria_entry_estoqueminimo = CTkEntry(self.tp_gdm_tp_editar_mercadoria, font=self.tp_gdm_fonte_padrao, width=400, height=50)
        self.tp_gdm_tp_editar_mercadoria_entry_estoqueminimo.place(relx=0.64, rely=0.59)
        self.tp_gdm_tp_editar_mercadoria_entry_estoqueminimo_sinalizer = CTkLabel(self.tp_gdm_tp_editar_mercadoria ,text_color='red')
        self.tp_gdm_tp_editar_mercadoria_entry_estoqueminimo.insert(0, self.item_values[7])

        #campo para botões
        self.tp_gdm_tp_editar_mercadoria_botao_registrar_mercadoria = CTkButton(self.tp_gdm_tp_editar_mercadoria, width=200 ,height=50,text='Atualizar', font=self.tp_gdm_fonte_padrao, 
        command=lambda: self.validate_tp_gdm_tp_editar_mercadoria(), text_color='black', fg_color='green', hover_color='green')
        self.tp_gdm_tp_editar_mercadoria_botao_registrar_mercadoria.place(relx=0.5, rely=0.95, anchor='s')

        lixeira_img = CTkImage(light_image=Image.open(r'images\lixeira.png'), size=(30, 30))
        self.tp_gdm_button_1 = CTkButton(self.tp_gdm_tp_editar_mercadoria, text='Deletar Mercadoria',  text_color='black', font=self.tp_gdm_fonte_padrao_bold, command=lambda:self.tp_gdm_tp_editar_mercadoria_excluir_product(), width=50, image=lixeira_img, fg_color='transparent')
        self.tp_gdm_button_1.place(relx=0.05, rely=0.87)

        fornecedor_img = CTkImage(light_image=Image.open(r'images\fornecedor.png'), size=(60, 60))
        self.tp_gdm_button_2 = CTkButton(self.tp_gdm_tp_editar_mercadoria, text='Suprimento de Mercadoria',  text_color='black', font=self.tp_gdm_fonte_padrao_bold, command=lambda:self.tp_gdm_abrir_tp_suprimentodemercadoria(), width=50, image=fornecedor_img, fg_color='transparent')
        self.tp_gdm_button_2.place(relx=0.70, rely=0.84)

        #binds
        self.tp_gdm_tp_editar_mercadoria.bind('<Escape>', self.fechar_tp_gdm_tp_editar_mercadoria)
        self.tp_gdm_tp_editar_mercadoria.bind('<Return>', self.validate_tp_gdm_tp_editar_mercadoria)

    def tp_gdm_abrir_tp_suprimentodemercadoria(self):
        self.tp_suprimentodemercadoria = CTkToplevel(self.tp_gdm_tp_editar_mercadoria)
        self.tp_suprimentodemercadoria.protocol('WM_DELETE_WINDOW', self.tp_gdm_fechar_tp_suprimentodemercadoria)
        self.tp_suprimentodemercadoria.attributes('-topmost', 'true')
        self.tp_suprimentodemercadoria.title('Inserir Senha')
        self.tp_suprimentodemercadoria_width = 500
        self.tp_suprimentodemercadoria_height = 250
        self.tp_suprimentodemercadoria_x = self.root.winfo_width()//2 - self.tp_suprimentodemercadoria_width//2   #essa e algumas abaixo, sao linhas que centralizam o tp na root
        self.tp_suprimentodemercadoria_y = self.root.winfo_height()//2 - self.tp_suprimentodemercadoria_height//2
        self.tp_suprimentodemercadoria.geometry(f'{self.tp_suprimentodemercadoria_width}x{self.tp_suprimentodemercadoria_height}+{self.tp_suprimentodemercadoria_x}+{self.tp_suprimentodemercadoria_y}')
        self.tp_suprimentodemercadoria.resizable(False, False)
        self.tp_suprimentodemercadoria.grab_set()

        
        titlo = CTkLabel(self.tp_suprimentodemercadoria, text='Inserir quantidade:', font=CTkFont('arial', 30, 'bold'))
        titlo.place(relx=0.5, rely=0.05, anchor='n')

        self.tp_suprimentodemercadoria_entry = CTkEntry(self.tp_suprimentodemercadoria, width=400, height=50, font=self.tp_cdm_fonte_padrao_bold)
        self.tp_suprimentodemercadoria_entry.place(relx=0.5, rely=0.3, anchor='n')
        self.tp_suprimentodemercadoria_entry_sinalizer = CTkLabel(self.tp_suprimentodemercadoria, text='', text_color='red')

        button_ok=CTkButton(self.tp_suprimentodemercadoria, text='Confirmar', font=self.tp_cdm_fonte_padrao_bold, height = 50, command=lambda:self.tp_suprimentodemercadoria_confirma(), fg_color='orange', hover_color='orange')
        button_ok.place(relx=0.18, rely=0.7)
        button_cancel=CTkButton(self.tp_suprimentodemercadoria, text='Cancelar', font=self.tp_cdm_fonte_padrao_bold, height = 50, command=lambda:self.tp_suprimentodemercadoria_cancel(), fg_color='orange', hover_color='orange')
        button_cancel.place(relx=0.57, rely=0.7)

        self.tp_suprimentodemercadoria.after(AFTER_INTERVALO, self.tp_suprimentodemercadoria_entry.focus_set)
        self.tp_suprimentodemercadoria.bind('<Return>', lambda event: button_ok.invoke())
        self.tp_suprimentodemercadoria.bind('<Escape>', lambda event: button_cancel.invoke())

        self.root.wait_window(self.tp_suprimentodemercadoria)

    def tp_suprimentodemercadoria_confirma(self):
        try:
            self.tp_suprimentodemercadoria_entry_sinalizer.place_forget()
            #tratar se é int
            valor_inserido = self.tp_suprimentodemercadoria_entry.get()
            if int(valor_inserido) <= 0:
                raise ValueError

            #lançar no database
            cfm = database.add_suprimentodemercadoria(self.item_values[0], valor_inserido)    
            if cfm:
                self.tp_gdm_fechar_tp_suprimentodemercadoria()
                self.fechar_tp_gdm_tp_editar_mercadoria()
                msg = CTkMessagebox(self.tp_gdm, message=f"Mercadoria atualizada com sucesso!", icon='check', title='Sucesso')
                self.tp_gdm.wait_window(msg)
                #fechar o tp_suprimento de mercadoria
                self.update_search_treeview()
            else:
                msg = CTkMessagebox(self.tp_suprimentodemercadoria, message=f"Erro na hora de realizar o suprimento de mercadoria!", icon='cancel', title='Erro')
                self.tp_gdm.wait_window(msg)

        except ValueError:
            self.tp_suprimentodemercadoria_entry_sinalizer.configure(text='Insira um valor inteiro.')
            self.tp_suprimentodemercadoria_entry_sinalizer.place(relx=0.5, rely=0.5, anchor='n')
            self.tp_suprimentodemercadoria_entry.delete(0, END)

        except Exception as e:
            self.tp_suprimentodemercadoria_entry_sinalizer.configure(f'Há um erro em fazer o suprimento de mercadoria: {e}')
            self.tp_suprimentodemercadoria_entry_sinalizer.place(relx=0.5, rely=0.5, anchor='n')

    def tp_suprimentodemercadoria_cancel(self):
        cfm = self.get_yes_or_not(self.tp_suprimentodemercadoria, 'Cancelar a operação?') 
        if cfm:
            self.tp_gdm_fechar_tp_suprimentodemercadoria()

    def tp_gdm_fechar_tp_suprimentodemercadoria(self):
        self.tp_suprimentodemercadoria.destroy()

    def validate_tp_gdm_tp_editar_mercadoria(self, event=None):
        if self.tp_gdm_tp_editar_mercadoria_validate_block:
            return
        try:
            self.tp_gdm_tp_editar_mercadoria_validate_block=True
            self.tp_gdm_tp_editar_mercadoria_clear_sinalizers()
            codbar_inserido = self.tp_gdm_tp_editar_mercadoria_entry_codbar.get().strip()

            desc_inserida = self.tp_gdm_tp_editar_mercadoria_entry_descricao.get().strip()
            if not desc_inserida:
                self.tp_gdm_tp_editar_mercadoria_entry_descricao_sinalizer.configure(text='A descrição da mercadoria não foi inserida.')
                self.tp_gdm_tp_editar_mercadoria_entry_descricao_sinalizer.place(relx=0.13, rely=0.41)
                self.tp_gdm_tp_editar_mercadoria_entry_descricao.focus_set()
                return
            elif desc_inserida.isdigit():
                self.tp_gdm_tp_editar_mercadoria_entry_descricao_sinalizer.configure(text='A descrição da mercadoria deve conter letras.')
                self.tp_gdm_tp_editar_mercadoria_entry_descricao_sinalizer.place(relx=0.13, rely=0.41)
                self.tp_gdm_tp_editar_mercadoria_entry_descricao.focus_set()
                return
            
            categoria_inserida = self.tp_gdm_tp_editar_mercadoria_combobox_categoria.get().strip()
            if categoria_inserida not in self.mercadoria_categorias:
                self.tp_gdm_tp_editar_mercadoria_combobox_categoria_sinalizer.configure(text='Selecione uma categoria válida.')
                self.tp_gdm_tp_editar_mercadoria_combobox_categoria_sinalizer.place(relx=0.13, rely=0.54)
                self.tp_gdm_tp_editar_mercadoria_combobox_categoria.focus_set()
                return
            
            precocompra_inserido = self.tp_gdm_tp_editar_mercadoria_entry_precocompra.get().replace(',', '.').strip()
            if not precocompra_inserido:
                self.tp_gdm_tp_editar_mercadoria_entry_precocompra_sinalizer.configure(text='O preco de compra não foi inserido')
                self.tp_gdm_tp_editar_mercadoria_entry_precocompra_sinalizer.place(relx=0.70, rely=0.28)
                self.tp_gdm_tp_editar_mercadoria_entry_precocompra.focus_set()
                return
            if precocompra_inserido:            
                try:
                    if float(precocompra_inserido) < 0:
                        raise Exception
                except:
                    self.tp_gdm_tp_editar_mercadoria_entry_precocompra_sinalizer.configure(text='Preço inválido')
                    self.tp_gdm_tp_editar_mercadoria_entry_precocompra_sinalizer.place(relx=0.70, rely=0.28)
                    self.tp_gdm_tp_editar_mercadoria_entry_precocompra.focus_set()
                    return
                
            precovenda_inserido = self.tp_gdm_tp_editar_mercadoria_entry_precovenda.get().replace(',', '.').strip()
            if not precovenda_inserido:
                self.tp_gdm_tp_editar_mercadoria_entry_precovenda_sinalizer.configure(text='O preco de venda não foi inserido')
                self.tp_gdm_tp_editar_mercadoria_entry_precovenda_sinalizer.place(relx=0.70, rely=0.41)
                self.tp_gdm_tp_editar_mercadoria_entry_precovenda.focus_set()
                return
            if precovenda_inserido:            
                try:
                    if float(precovenda_inserido) < 0:
                        raise Exception
                except:
                    self.tp_gdm_tp_editar_mercadoria_entry_precovenda_sinalizer.configure(text='Preço inválido')
                    self.tp_gdm_tp_editar_mercadoria_entry_precovenda_sinalizer.place(relx=0.70, rely=0.41)
                    self.tp_gdm_tp_editar_mercadoria_entry_precovenda.focus_set()
                    return
                
            estoque_inserido = self.tp_gdm_tp_editar_mercadoria_entry_estoque.get().strip()
            try:
                estoque_inserido = int(estoque_inserido)
                if estoque_inserido < 0:
                    raise ValueError
            except Exception as e:
                self.tp_gdm_tp_editar_mercadoria_entry_estoque_sinalizer.configure(text='A quantidade deve ser um numero inteiro.')
                self.tp_gdm_tp_editar_mercadoria_entry_estoque_sinalizer.place(relx=0.70, rely=0.54)
                self.tp_gdm_tp_editar_mercadoria_entry_estoque.focus_set()
                return
            
            estoqueminimo_inserido = self.tp_gdm_tp_editar_mercadoria_entry_estoqueminimo.get().strip()
            try:
                estoqueminimo_inserido = int(estoqueminimo_inserido)
                if estoqueminimo_inserido < 0:
                    raise ValueError
            except Exception as e:
                self.tp_gdm_tp_editar_mercadoria_entry_estoqueminimo_sinalizer.configure(text='O estoque mínimo deve ser um numero inteiro.')
                self.tp_gdm_tp_editar_mercadoria_entry_estoqueminimo_sinalizer.place(relx=0.70, rely=0.67)
                self.tp_gdm_tp_editar_mercadoria_entry_estoqueminimo.focus_set()
                return
            
            fornecedor_inserido = self.tp_gdm_tp_editar_mercadoria_combobox_fornecedor.get().strip()
            if fornecedor_inserido not in self.fornecedores:
                self.tp_gdm_tp_editar_mercadoria_combobox_fornecedor_sinalizer.configure(text='Selecione um fornecedor válido.')
                self.tp_gdm_tp_editar_mercadoria_combobox_fornecedor_sinalizer.place(relx=0.13, rely=0.67)
                self.tp_gdm_tp_editar_mercadoria_combobox_fornecedor.focus_set()
                return

            #atualizacao dos dados no banco de dados
            cfm = self.get_yes_or_not(self.tp_gdm_tp_editar_mercadoria)
            if cfm:
                fb = database.update_product((codbar_inserido, desc_inserida.lower(), categoria_inserida.lower(), precocompra_inserido, precovenda_inserido, estoque_inserido, estoqueminimo_inserido, fornecedor_inserido.lower(), dt.now().strftime('%Y-%m-%d %H:%M:%S'), self.item_values[0]))
                if fb:
                    self.fechar_tp_gdm_tp_editar_mercadoria()
                    msg = CTkMessagebox(self.tp_gdm, message=f"Mercadoria atualizada com sucesso!", icon='check', title='Sucesso')
                    self.tp_gdm.wait_window(msg)
                    self.update_search_treeview()
                else:
                    CTkMessagebox(self.tp_gdm_tp_editar_mercadoria, message=f'Não foi possível atualizar a mercadoria.', icon='cancel', title='Erro')
            else:
                pass
        except Exception as e:
            print(e)
            CTkMessagebox(self.tp_gdm_tp_editar_mercadoria, title='Erro.', message=f'Erro ao validar os dados inseridos: {e}. Considere contatar a assistência: {self.contato}')
        finally:
            self.tp_gdm_tp_editar_mercadoria_validate_block = False

    def tp_gdm_tp_editar_mercadoria_clear_sinalizers(self):
        self.tp_gdm_tp_editar_mercadoria_entry_codbar_sinalizer.place_forget()
        self.tp_gdm_tp_editar_mercadoria_entry_descricao_sinalizer.place_forget()
        self.tp_gdm_tp_editar_mercadoria_combobox_categoria_sinalizer.place_forget()
        self.tp_gdm_tp_editar_mercadoria_entry_precocompra_sinalizer.place_forget()
        self.tp_gdm_tp_editar_mercadoria_entry_precovenda_sinalizer.place_forget()
        self.tp_gdm_tp_editar_mercadoria_entry_estoque_sinalizer.place_forget()
        self.tp_gdm_tp_editar_mercadoria_entry_estoqueminimo_sinalizer.place_forget()
        self.tp_gdm_tp_editar_mercadoria_combobox_fornecedor_sinalizer.place_forget()

    def tp_gdm_tp_editar_mercadoria_excluir_product(self):
        try:
            #captura o id da mercadoria em questão
            product_id = self.item_values[0]
            #confirma se o usuario realmente quer excluir a mercadoria
            cfm = self.get_yes_or_not(self.tp_gdm_tp_editar_mercadoria, f'Confirma a exclusão de {self.item_values[2]}?')
            if cfm:
                #excluir o item através de uma função database.py
                fb = database.delete_product_by_id(product_id)
                if fb:
                    self.fechar_tp_gdm_tp_editar_mercadoria()
                    msg = CTkMessagebox(self.tp_gdm, message=f"Mercadoria deletada com sucesso!", icon='check', title='Sucesso')
                    self.tp_gdm.wait_window(msg)
                    self.update_search_treeview()
                else:
                    CTkMessagebox(self.tp_gdm_tp_editar_mercadoria, message=f'Não foi possível deletar a mercadoria.', icon='cancel', title='Erro')
        except:
            CTkMessagebox(self.root, message=f'Erro na funcionalidade de excluir mercadoria. Contate assistência: {self.contato}', icon='cancel', title='Erro')

        

    def fechar_tp_gdm_tp_editar_mercadoria(self, event=None):
        if self.tp_gdm_tp_editar_mercadoria:
            self.tp_gdm_tp_editar_mercadoria.destroy()
            self.tp_gdm_tp_editar_mercadoria = None

    #endregion

    # region MODULO Fiar compra

    def abrir_tp_fiar_compra(self):
        if self.tp_clientes:
            return
        if self.get_treeview_itens_number() <= 0:
            CTkMessagebox(self.root, message=f'Insira um item na compra para realizar essa ação.', icon='warning', title='Atenção')
            return
        
        self.tp_clientes = CTkToplevel(self.root)
        self.tp_clientes.title('Clientes')
        self.tp_clientes.protocol('WM_DELETE_WINDOW', self.fechar_tp_clientes)
        self.tp_clientes_width = self.root.winfo_width() * 80 // 100
        self.tp_clientes_height = self.root.winfo_height()* 80 // 100
        self.tp_clientes_x = self.root.winfo_width()//2 - self.tp_clientes_width//2   #essa e algumas abaixo, sao linhas que centralizam o tp na root
        self.tp_clientes_y = self.root.winfo_height()//2 - self.tp_clientes_height//2
        self.tp_clientes.geometry(f'{self.tp_clientes_width}x{self.tp_clientes_height}+{self.tp_clientes_x}+{self.tp_clientes_y}')
        self.tp_clientes.resizable(False, False)
        self.tp_clientes.attributes('-topmost', 'true')
        self.tp_clientes.grab_set()

        self.clientes_img = Image.open(r'images\clientes.png')
        registro_cliente_img = Image.open(r'images\clientes_cadastro.png')
        pesquisa_img = Image.open(r'images\ilustracao_pesquisa_mercadoria.png')

        # tp ilustração
        self.tp_clientes_ilustracao = CTkLabel(self.tp_clientes,  text='   Inserir na conta do cliente:', image=CTkImage(light_image=self.clientes_img, size=(99, 99)), font=CTkFont('arial', 35, 'bold'), compound='left')
        self.tp_clientes_ilustracao.place(relx=0.5, rely=0.01, anchor='n')

        # entry para inserir a busca
        self.tp_clientes_entry_1 = CTkEntry(self.tp_clientes, width=self.tp_clientes_width - (self.tp_clientes_width * 30 // 100), height=50, placeholder_text='Procurar cliente por nome ou CPF...', font=self.fonte_basic, border_color='black')
        self.tp_clientes_entry_1.place(relx=0.15, rely=0.2)
        self.tp_clientes_entry_1.bind("<KeyRelease>", self.procurar_cliente)

        # Treeview para exibir os resultados de forma tabular
        self.clientes_treeview_columns = ('id', 'nome', 'whatsapp', 'cpf')
        self.clientes_treeview = ttk.Treeview(self.tp_clientes, columns=self.clientes_treeview_columns, show="headings", height=12)
        self.clientes_treeview.column(self.clientes_treeview_columns[0], width=80, anchor=CENTER)
        self.clientes_treeview.column(self.clientes_treeview_columns[1], width=400, anchor=CENTER)
        self.clientes_treeview.column(self.clientes_treeview_columns[2], width=200, anchor=CENTER)
        self.clientes_treeview.column(self.clientes_treeview_columns[3], width=200, anchor=CENTER)
        self.clientes_treeview.heading(self.clientes_treeview_columns[0], text="id".capitalize(), )
        self.clientes_treeview.heading(self.clientes_treeview_columns[1], text="nome".capitalize(), )
        self.clientes_treeview.heading(self.clientes_treeview_columns[2], text="whatsapp".capitalize())
        self.clientes_treeview.heading(self.clientes_treeview_columns[3], text="cpf".capitalize())
        self.clientes_treeview.place(relx=0.5, rely=0.35, anchor='n')

        # Cria a Scrollbar e associa à Treeview
        scrollbar = CTkScrollbar(self.tp_clientes, orientation="vertical", command=self.clientes_treeview.yview)
        scrollbar.place(relx=0.92, rely=0.35)
        self.clientes_treeview.configure(yscrollcommand=scrollbar.set)

        self.tp_clientes.bind('<Escape>', lambda event: self.fechar_tp_clientes())

        # botao registrar cliente
        self.tp_clientes_ilustracao = CTkButton(self.tp_clientes,  text='Confimar', font=self.tp_cdm_fonte_padrao, width=150, height=50, cursor='hand2', command=lambda:self.lancar_na_conta_do_cliente())
        self.tp_clientes_ilustracao.place(relx=0.5, rely=0.875, anchor='n')

        self.tp_clientes_treeview_update()

    def procurar_cliente(self, event=None):
        search_term = self.tp_clientes_entry_1.get()
        if search_term.strip().isdigit():
            results = database.get_clientes_by_coluna('cpf', search_term)
        else: 
            results = database.get_clientes_by_coluna('nome', search_term)

        #limpando a treeview
        for item in self.clientes_treeview.get_children():
            self.clientes_treeview.delete(item)
        #inserindo os dados na nova busca
        for row in results:
            self.clientes_treeview.insert('', END, values=helper.formatar_row_para_treeview_clientes(row))

    def tp_clientes_treeview_update(self):
        # Limpa a Treeview antes de exibir os novos resultados
        for item in self.clientes_treeview.get_children():
            self.clientes_treeview.delete(item)
        # Chama a função de busca no banco de dados do backend
        results = database.get_all_clientes()
        if results:
            # Adiciona os resultados na Treeview
            for row in results:
                self.clientes_treeview.insert('', END, values=helper.formatar_row_para_treeview_clientes(row))

    def lancar_na_conta_do_cliente(self):
        try:
            if not self.clientes_treeview.selection(): #trata o caso de o usuario nao identificar o cliente que gostaria de editar os dados
                msg = CTkMessagebox(self.tp_clientes, message=f'Selecione um cliente antes de confirmar.', icon='warning', title='Atenção')
                self.tp_clientes.wait_window(msg)
                return

            #captura o id do cliente (apartir da treeview)
            selected_item = self.clientes_treeview.focus()
            item_values = self.clientes_treeview.item(selected_item, "values")
            cliente_id = item_values[0]

            #verifica se o total da compra em questão (que será lançada) é menor que o limite disponível do cliente
            total_da_compra = helper.format_to_float(self.tp_idv_frame_status_subtotal_label_1.cget('text'))
            limite_disponivel = database.get_limite_disponivel_do_cliente(cliente_id, database.get_limite_consumido_do_cliente(cliente_id))

            if total_da_compra > limite_disponivel:
                CTkMessagebox(self.tp_clientes, message=f'Limite insuficiente para essa compra.\nLimite disponível: {helper.format_to_moeda(limite_disponivel)}.', icon='warning', title='Atenção', font=self.tp_cdm_fonte_padrao)
                return

            for item in self.carrinho:
                #chama a funcao que de fato lanca na conta do cliente (backend)
                cfm = database.insert_into_oncredit(item_values[0], json.dumps(item), dt.now().strftime('%Y-%m-%d %H:%M:%S'))
                if not cfm:
                    raise Exception
                 
            #sinaliza sucesso/fracasso
            msg = CTkMessagebox(message=f"Compra lançada na conta do cliente: {item_values[1]}!", icon='check', title='Sucesso')
            self.tp_clientes.wait_window(msg)
            self.fechar_tp_clientes()
            self.reset_root()
        except Exception as e:
            print(e)
            CTkMessagebox(self.tp_clientes, message=f'Ocorreu um erro ao laçar na conta do cliente. Verifique a conta do mesmo para evitar erros.', icon='cancel', title='Erro')
        
        #endregion

    # region MÓDULO GDC (GERENCIAMENTO DE CAIXA)

    def abrir_tp_gdc(self):
        if self.tp_gdc:
            return
        if (self.get_treeview_itens_number()) > 0:
            CTkMessagebox(self.root, message=f'Finalize ou cancele a compra atual antes de realizar esta operação.', icon='warning', title='Atenção')
            return
        dados = self.get_widget_data()
        if not dados:
            CTkMessagebox(self.root, message=f'Erro na hora de obter os dados do caixa.', icon='warning', title='Atenção')
            return
        self.tp_gdc = CTkToplevel(self.root)
        self.tp_gdc.grab_set()
        self.tp_gdc.title('Gerenciamento de Caixa')
        self.tp_gdc.protocol('WM_DELETE_WINDOW', self.fechar_tp_gdc)
        self.tp_gdc_width = 1200
        self.tp_gdc_height = 700
        self.tp_gdc_x = self.root.winfo_width()//2 - self.tp_gdc_width//2   #essa e algumas abaixo, sao linhas que centralizam o tp na root
        self.tp_gdc_y = self.root.winfo_height()//2 - self.tp_gdc_height//2
        self.tp_gdc.geometry(f'{self.tp_gdc_width}x{self.tp_gdc_height}+{self.tp_gdc_x}+{self.tp_gdc_y}')
        self.tp_gdc.resizable(False, False)
        self.tp_gdc.attributes('-topmost', 'true')
        self.tp_gdc_ignore_enter = False
        self.tp_gdc_validate_sangria_block = False
        self.tp_gdc_validate_suprimento_block = False
        self.tp_gdc_fonte = CTkFont('arial', 35, 'bold')

        #titlo
        self.tp_gdc_titlo = CTkLabel(self.tp_gdc, text='Gerenciamento de Caixa:', font=CTkFont('arial', 35, 'bold'))
        self.tp_gdc_titlo.place(relx=0.5, rely=0.02, anchor='n')

        # Treeview para exibir os resultados de forma tabular
        self.tp_gdc_dia_tree_label = CTkLabel(self.tp_gdc, text=f'Movimentação do Caixa desde: {dados[-1]}', font=self.tp_cdm_fonte_padrao_bold)
        self.tp_gdc_dia_tree_label.place(relx=0.515, rely=0.11)
        self.tp_gdm_treeview_search_columns = ('id', 'descricao', 'valor', 'hora')
        self.tp_gdc_dia_tree = ttk.Treeview(self.tp_gdc, columns=self.tp_gdm_treeview_search_columns, show="headings", height=20)
        self.tp_gdc_dia_tree.column(self.tp_gdm_treeview_search_columns[0], width=100, anchor=CENTER)
        self.tp_gdc_dia_tree.column(self.tp_gdm_treeview_search_columns[1], width=200, anchor=CENTER)
        self.tp_gdc_dia_tree.column(self.tp_gdm_treeview_search_columns[2], width=170, anchor=CENTER)
        self.tp_gdc_dia_tree.column(self.tp_gdm_treeview_search_columns[3], width=150, anchor=CENTER)
        self.tp_gdc_dia_tree.heading(self.tp_gdm_treeview_search_columns[0], text="ID", )
        self.tp_gdc_dia_tree.heading(self.tp_gdm_treeview_search_columns[1], text="Descrição", )
        self.tp_gdc_dia_tree.heading(self.tp_gdm_treeview_search_columns[2], text="Valor", )
        self.tp_gdc_dia_tree.heading(self.tp_gdm_treeview_search_columns[3], text="Hora", )
        self.tp_gdc_dia_tree.place(relx=0.47, rely=0.16)

        # Cria a Scrollbar e associa à Treeview
        scrollbar = CTkScrollbar(self.tp_gdc, orientation="vertical", command=self.tp_gdc_dia_tree.yview)
        scrollbar.place(relx=0.95, rely=0.3)
        self.tp_gdc_dia_tree.configure(yscrollcommand=scrollbar.set)


        #registro de sangria widgets
        self.tp_gdc_frame_0 = CTkFrame(self.tp_gdc, width=450, height=300, fg_color='white')
        self.tp_gdc_frame_0.place(relx=0.05, rely=0.12)

        self.tp_gdc_sangria_titlo = CTkLabel(self.tp_gdc_frame_0, text='Sangria de Caixa:', font=self.tp_cdm_fonte_padrao_bold)
        self.tp_gdc_sangria_titlo.place(relx=0.5, rely=0.02, anchor='n')

        self.tp_gdc_combobox_1_var = StringVar(value='Selecionar Categoria')
        self.tp_gdc_combobox_1 = CTkComboBox(self.tp_gdc_frame_0, variable=self.tp_gdc_combobox_1_var, width=400, height=50, values=self.sangria_categorias, 
        font=self.tp_cdm_fonte_padrao_bold, dropdown_font=self.tp_cdm_fonte_padrao_bold)
        self.tp_gdc_combobox_1_sinalizer = CTkLabel(self.tp_gdc_frame_0, text_color='red')
        self.tp_gdc_combobox_1.place(relx=0.5, rely=0.2, anchor='n')

        self.tp_gdc_label_1 = CTkLabel(self.tp_gdc_frame_0, text=f'Valor:', font=self.tp_cdm_fonte_padrao_bold, height = 50)
        self.tp_gdc_label_1.place(relx=0.05, rely=0.5)
        self.tp_gdc_entry_1 = CTkEntry(self.tp_gdc_frame_0, font=self.tp_cdm_fonte_padrao_bold, height = 50, width = 250)
        self.tp_gdc_entry_1.place(relx=0.25, rely=0.5)
        self.tp_gdc_entry_1_sinalizer = CTkLabel(self.tp_gdc_frame_0, text_color='red')

        self.tp_gdc_button_1 = CTkButton(self.tp_gdc_frame_0, text='Registrar Sangria', font=self.tp_cdm_fonte_padrao_bold, height = 50, command=lambda:self.tp_gdc_validate_sangria(), fg_color='green', hover_color='green')
        self.tp_gdc_button_1.place(relx=0.5, rely=0.8, anchor='n')

        #registro de suprimento widgets
        self.tp_gdc_frame_1 = CTkFrame(self.tp_gdc, width=450, height=250, fg_color='white')
        self.tp_gdc_frame_1.place(relx=0.05, rely=0.57)

        self.tp_gdc_sangria_titlo = CTkLabel(self.tp_gdc_frame_1, text='Suprimento de Caixa:', font=self.tp_cdm_fonte_padrao_bold)
        self.tp_gdc_sangria_titlo.place(relx=0.5, rely=0.02, anchor='n')

        self.tp_gdc_label_2 = CTkLabel(self.tp_gdc_frame_1, text=f'Valor:', font=self.tp_cdm_fonte_padrao_bold, height = 50)
        self.tp_gdc_label_2.place(relx=0.05, rely=0.3)
        self.tp_gdc_entry_2 = CTkEntry(self.tp_gdc_frame_1, font=self.tp_cdm_fonte_padrao_bold, height = 50, width = 250)
        self.tp_gdc_entry_2.place(relx=0.25, rely=0.3)
        self.tp_gdc_entry_2_sinalizer = CTkLabel(self.tp_gdc_frame_1, text_color='red')

        self.tp_gdc_button_2 = CTkButton(self.tp_gdc_frame_1, text='Registrar Suprimento', font=self.tp_cdm_fonte_padrao_bold, height = 50, command=lambda:self.tp_gdc_validate_suprimento(), fg_color='green', hover_color='green')
        self.tp_gdc_button_2.place(relx=0.5, rely=0.7, anchor='n')

        #caixa widgets

        self.tp_gdc_label_3 = CTkLabel(self.tp_gdc, text=f'Valor em Caixa:', font=self.tp_cdm_fonte_padrao_bold)
        self.tp_gdc_label_3.place(relx=0.6, rely=0.79)
        self.tp_gdc_label_4 = CTkLabel(self.tp_gdc, text=f'{helper.format_to_moeda(self.caixa)}', font=CTkFont('arial', 35, 'bold'), text_color='green')
        self.tp_gdc_label_4.place(relx=0.73, rely=0.784)

        self.tp_gdc_button_3 = CTkButton(self.tp_gdc, text='Fechar Caixa', font=self.tp_cdm_fonte_padrao_bold, height = 50, command=lambda:self.tp_gdc_validate_fechar_caixa(), fg_color='green', hover_color='green')
        self.tp_gdc_button_3.place(relx=0.5, rely=0.85)
        self.tp_gdc_entry_3 = CTkEntry(self.tp_gdc, font=self.tp_cdm_fonte_padrao_bold, height = 50, width=280, placeholder_text='Informar o caixa restante')
        self.tp_gdc_entry_3.place(relx=0.65, rely=0.85)
        self.tp_gdc_entry_3_sinalizer = CTkLabel(self.tp_gdc, text_color='red')

        self.tp_gdc.bind('<Escape>', self.fechar_tp_gdc)
        self.tp_gdc_dia_tree.bind('<Double-1>', self.abrir_tp_gdc_1)

        self.update_tp_gdc_dia_tree(dados)

    
    def get_widget_data(self):
        try:
            self.caixa = 0
            #obtendo o troco
            with open('txts/troco.txt', 'r') as a:
                self.caixa_de_giro = helper.format_to_float(a.readline()) 
            with open('txts/fechamentodecaixa_lastdt.txt', 'r') as a:
                date_str = a.readline()
            date = dt.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            #obtendo sangrias
            sangrias = database.get_sangrias_by_date(date)
            #obtendo supriments
            suprimentos = database.get_supriments_by_date(date)
            #obtendo sales
            sales = database.get_sales_by_date(date)

            return(sangrias, suprimentos, sales, date_str)

        except Exception as e:
            print(e)
            return False

    def update_tp_gdc_dia_tree(self, dados):
        # Limpa a Treeview antes de exibir os novos resultados
        for item in self.tp_gdc_dia_tree.get_children():
            self.tp_gdc_dia_tree.delete(item)
        #inserindo o troco
        self.tp_gdc_dia_tree.insert('', END, values=('-', 'Caixa de Giro', helper.format_to_moeda(self.caixa_de_giro, 'R$'), '-'))
        #updating sangrias do dia
        self.sangria = 0
        for i, item in enumerate(dados[0], 1):
            self.sangria += helper.format_to_float(item[1])
            self.tp_gdc_dia_tree.insert('', END, values=(item[0], 'Sangria: '+item[2], helper.format_to_moeda(item[1], 'R$'), item[3][10:-3]))
            self.tp_gdc_dia_tree.yview_moveto(1.0)
        #updating suprimentos do dia
        self.suprimento = 0
        for i, item in enumerate(dados[1], 1):
            self.suprimento += helper.format_to_float(item[1])
            self.tp_gdc_dia_tree.insert('', END, values=(item[0], 'Suprimento n°'+str(i), helper.format_to_moeda(item[1], 'R$'), item[2][10:-3]))
            self.tp_gdc_dia_tree.yview_moveto(1.0)
        #updating vendas do dia
        self.entrada_dinheiro = self.entrada_cartao = 0
        for i, item in enumerate(dados[2], 1):
            payments = database.get_payments_by_sale_id(item[0])
            payment_entrada_dinheiro_total = 0
            payment_entrada_cartao_total = 0
            payments_methods_counter = 0 # variavel que armazena a quantidade de formas de pagamento da venda
            for payment in payments:
                if payment[0] == 'Dinheiro':
                    self.entrada_dinheiro += helper.format_to_float(payment[1])
                    payment_entrada_dinheiro_total += helper.format_to_float(payment[1])
                else:
                    self.entrada_cartao += helper.format_to_float(payment[1])
                    payment_entrada_cartao_total += helper.format_to_float(payment[1])
                payments_methods_counter += 1
            if payment_entrada_dinheiro_total and payments_methods_counter == 1:
                self.tp_gdc_dia_tree.insert('', END, values=(item[0], 'Venda Realizada n°'+str(i), helper.format_to_moeda(payment_entrada_dinheiro_total, 'R$'), item[1][10:-3]))
            if payment_entrada_cartao_total and payments_methods_counter > 1:
                total_payments = payment_entrada_dinheiro_total + payment_entrada_cartao_total
                self.tp_gdc_dia_tree.insert('', END, values=(item[0], 'Venda Realizada n°'+str(i), helper.format_to_moeda(payment_entrada_dinheiro_total, 'R$')+f'(De R${total_payments})', item[1][10:-3]))
       
        self.tp_gdc_dia_tree.yview_moveto(1.0)
        self.caixa = self.caixa_de_giro + self.entrada_dinheiro + self.suprimento - self.sangria
        self.tp_gdc_label_4.configure(text=f'{helper.format_to_moeda(self.caixa)}')
        self.tp_gdc_reset_widgets()

    def tp_gdc_validate_sangria(self):
        if self.tp_gdc_validate_sangria_block == True:
            return
        try:
            self.tp_gdc_validate_sangria_block = True
            self.tp_gdc_validate_sangria_clear_sinalizers()
            #validando categoria
            categoria_selcionada = self.tp_gdc_combobox_1_var.get()
            if categoria_selcionada not in self.sangria_categorias:
                self.tp_gdc_combobox_1_sinalizer.configure(text='Por favor, inserir uma categoria válida.')
                self.tp_gdc_combobox_1_sinalizer.place(relx=0.5, rely=0.4, anchor='n')
                return
            #validando valor
            valor_inserido = self.tp_gdc_entry_1.get().replace(',', '.')
            if valor_inserido:
                try:
                    float(valor_inserido)
                except:
                    self.tp_gdc_entry_1_sinalizer.configure(text='Insira um valor válido.')
                    self.tp_gdc_entry_1_sinalizer.place(relx=0.5, rely=0.7, anchor='n')
                    return
            else:
                self.tp_gdc_entry_1_sinalizer.configure(text='Por favor insira um valor.')
                self.tp_gdc_entry_1_sinalizer.place(relx=0.5, rely=0.7, anchor='n')
                return
            yon = self.get_yes_or_not(self.tp_gdc, 'Confirmar o registro da Sangria de caixa?')
            if not yon:
                return
            cfm = database.insert_sangria(valor_inserido, categoria_selcionada)
            if cfm:
                CTkMessagebox(self.tp_gdc, message="Sangria registrada com sucesso!", icon='check', title='')
                self.update_tp_gdc_dia_tree(self.get_widget_data())
            else:  
                CTkMessagebox(self.tp_gdc, message='Erro na hora de registrar a sangria.', icon='cancel', title='Erro')
        except:
            CTkMessagebox(self.tp_gdc, message='Erro na hora de validar os dados da sangria. Sangria NÃO REGISTRADA.', icon='cancel', title='Erro')
        finally:
            self.tp_gdc_validate_sangria_block = False

    def tp_gdc_validate_sangria_clear_sinalizers(self):
        self.tp_gdc_combobox_1_sinalizer.place_forget()
        self.tp_gdc_entry_1_sinalizer.place_forget()

    def tp_gdc_validate_suprimento(self):
        if self.tp_gdc_validate_suprimento_block == True:
            return
        try:
            self.tp_gdc_validate_suprimento_block = True
            self.tp_gdc_entry_2_sinalizer.place_forget()
            #validando valor
            valor_inserido = self.tp_gdc_entry_2.get().replace(',', '.')
            if valor_inserido:
                try:
                    float(valor_inserido)
                except:
                    self.tp_gdc_entry_2_sinalizer.configure(text='Insira um valor válido.')
                    self.tp_gdc_entry_2_sinalizer.place(relx=0.5, rely=0.5, anchor='n')
                    return
            else:
                self.tp_gdc_entry_2_sinalizer.configure(text='Por favor insira um valor.')
                self.tp_gdc_entry_2_sinalizer.place(relx=0.5, rely=0.5, anchor='n')
                return
            yon = self.get_yes_or_not(self.tp_gdc, 'Confirmar o registro do Suprimento de caixa?')
            if not yon:
                return
            cfm = database.insert_supriment(valor_inserido)
            if cfm:
                CTkMessagebox(self.tp_gdc, message="Suprimento registrado com sucesso!", icon='check', title='')
                self.update_tp_gdc_dia_tree(self.get_widget_data())
            else:  
                CTkMessagebox(self.tp_gdc, message='Erro na hora de registrar o suprimento.', icon='cancel', title='Erro')
        except:
            CTkMessagebox(self.tp_gdc, message='Erro na hora de validar os dados do suprimento. Suprimento NÃO REGISTRADO.', icon='cancel', title='Erro')
        finally:
            self.tp_gdc_validate_suprimento_block = False

    def tp_gdc_validate_supriments_clear_sinalizers(self):
        self.tp_gdc_entry_2_sinalizer.place_forget()

    def tp_gdc_validate_fechar_caixa(self):
        if self.tp_gdc_ignore_enter:
            return
        self.tp_gdc_ignore_enter = True
        try:
            self.tp_gdc_clear_sinalizers()
            valor_inserido = self.tp_gdc_entry_3.get().strip().replace(',', '.')
            if not valor_inserido:
                self.tp_gdc_entry_3_sinalizer.configure(text='Por favor insira o valor que ficará no caixa.')
                self.tp_gdc_entry_3_sinalizer.place(relx=0.65, rely=0.93)
                return
            try:
                float(valor_inserido)
                yon_1 = self.get_yes_or_not(self.tp_gdc, 'Confirmar o fechamento de caixa?')
                if yon_1:
                    key = self.abrir_tp_password(self.tp_gdc)
                    if self.tp_password_feedback:
                        self.fechar_caixa(valor_inserido)
                    else:
                        print('Senha não aceita.')
            except Exception as e:   
                print(e) 
                self.tp_gdc_entry_3_sinalizer.configure(text='Por favor insira um valor válido.')
                self.tp_gdc_entry_3_sinalizer.place(relx=0.65, rely=0.93)  
        except Exception as e:
            msg = CTkMessagebox(self.tp_gdc, message=f'Erro na hora de validar os dados para fechamento de caixa. Erro: {e}', icon='cancel', title='Erro')
            self.tp_gdc.wait_window(msg)
            self.tp_gdc_entry_3.focus_set()
        finally:
            self.tp_gdc_ignore_enter = False

    def fechar_caixa(self, valor_inserido):
        try:
            dt_registro = dt.now().strftime('%Y-%m-%d %H:%M:%S')
            dados = {'entrada_dinheiro': self.entrada_dinheiro, 'entrada_cartao': self.entrada_cartao, 'sangrias':self.sangria,  'suprimentos': self.suprimento, 'caixa_restante': valor_inserido}
            with open('txts/historic_fechamentos_de_caixa.txt', 'a') as a:
                a.write(f'{dt_registro} - {dados}\n')
            with open('txts/troco.txt', 'w') as a:
                a.write(f'{valor_inserido}')
            with open('txts/fechamentodecaixa_lastdt.txt', 'w') as a:
                a.write(f'{dt_registro}')
            with open('txts/envelope.txt', 'a') as a:
                valor_envelope = self.caixa - helper.format_to_float(valor_inserido)
                a.write(f'{dt_registro}: {valor_envelope}\n')
            self.fechar_tp_gdc()
            yon_1 = self.get_yes_or_not(self.root, 'Imprimir o resumo do fechamento de caixa?')
            if yon_1:        
                self.imprimir_resumo_fechamento_de_caixa(dados)
            CTkMessagebox(self.root, message=f"Caixa fechado com sucesso!", icon='check', title='Sucesso')
        except Exception as e:
            CTkMessagebox(self.tp_gdc, message=f'Erro na hora fazer o fechamento de caixa ou imprimir o resumo. Erro: {e}', icon='cancel', title='Erro')
        finally:
            self.tp_password_feedback = False

    def tp_gdc_clear_sinalizers(self):
        self.tp_gdc_entry_1_sinalizer.place_forget()
        self.tp_gdc_entry_2_sinalizer.place_forget()
        self.tp_gdc_entry_3_sinalizer.place_forget()
        self.tp_gdc_combobox_1_sinalizer.place_forget()

    def imprimir_resumo_fechamento_de_caixa(self, dados):
        return
        
        #por causa da versao do python ou windows
        entrada_dinheiro = dados['entrada_dinheiro']
        entrada_cartao = dados['entrada_cartao']
        entrada_sangrias = dados['sangrias']
        entrada_suprimentos = dados['suprimentos']
        caixa_restante = dados['caixa_restante']
        #\


        nota = []
    
        # Cabeçalho
        nota.append("***** Fechamento de Caixa *****")
        nota.append("Data: " + time.strftime("%d/%m/%Y %H:%M"))
        nota.append("************************")
        
        nota.append("------------------------------------------")
        nota.append(f"Entrada Dinheiro: R${helper.format_to_moeda(entrada_dinheiro):>15}")
        nota.append(f'Entrada Cartao:   R${helper.format_to_moeda(entrada_cartao):>15}')
        nota.append(f'Sangrias:         R${helper.format_to_moeda(entrada_sangrias):>15}')
        nota.append(f'Suprimentos:      R${helper.format_to_moeda(entrada_suprimentos):>15}')
        nota.append("------------------------------------------")
        nota.append(f'Caixa restante:   R${helper.format_to_moeda(caixa_restante):<15}')
        nota.append("************************")

        print(nota)
        #self.imprimir_notas("\n".join(nota))

    def abrir_tp_gdc_1(self, event=None):
        selected_item = self.tp_gdc_dia_tree.focus()
        self.item_values = self.tp_gdc_dia_tree.item(selected_item, "values")

        if not self.item_values:
            return

        self.tp_gdc_1 = CTkToplevel(self.tp_gdc)
        self.tp_gdc_1.grab_set()
        self.tp_gdc_1.title('')
        self.tp_gdc_1.protocol('WM_DELETE_WINDOW', self.fechar_tp_gdc_1)
        self.tp_gdc_1_width = 300
        self.tp_gdc_1_height = 150
        self.tp_gdc_1_x = self.root.winfo_width()//2 - self.tp_gdc_1_width//2   #essa e algumas abaixo, sao linhas que centralizam o tp na root
        self.tp_gdc_1_y = self.root.winfo_height()//2 - self.tp_gdc_1_height//2
        self.tp_gdc_1.geometry(f'{self.tp_gdc_1_width}x{self.tp_gdc_1_height}+{self.tp_gdc_1_x}+{self.tp_gdc_1_y}')
        self.tp_gdc_1.resizable(False, False)
        self.tp_gdc_1.attributes('-topmost', 'true')

        self.tp_gdc_1.bind('<Escape>', self.fechar_tp_gdc_1)

        lixeira_img = CTkImage(light_image=Image.open(r'images\lixeira.png'), size=(30, 30))
        impressora_img = CTkImage(light_image=Image.open(r'images\impressora.png'), size=(30, 30))

        self.tp_gdc_1_button_1 = CTkButton(self.tp_gdc_1, text='Excluir', command=lambda:self.tp_gdc_1_excluir_item(), width=50, image=lixeira_img)
        self.tp_gdc_1_button_1.place(relx=0.3, rely=0.4, anchor='n')

        self.tp_gdc_1_button_1 = CTkButton(self.tp_gdc_1, text='Imprimir', command=lambda:self.tp_gdc_1_imprimir_item(), width=50, image=impressora_img)
        self.tp_gdc_1_button_1.place(relx=0.7, rely=0.4, anchor='n')

    def tp_gdc_1_imprimir_item(self):
        return True
        try:
            if 'Venda' in self.item_values[1]:
                item_id = self.item_values[0]
                data, troco = database.get_sales_date_troco_by_id(item_id)
                items_prev = database.get_sales_items_by_sale_id(item_id)
                items = []
                for item in items_prev:
                    item_items = {}
                    item_items['product_name'] = database.get_product_name_by_id(item[0])[0]
                    item_items['quantity'] = item[1]
                    item_items['price'] = item[2]
                    items.append(item_items)
                payments_prev = database.get_payments_by_sale_id(item_id)
                payments = []
                total_geral = 0
                for payment in payments_prev:
                    payments_item = {}
                    payments_item['method'] = payment[0]
                    payments_item['amount'] = payment[1]
                    if payment[0] != 'Dinheiro':
                        payments_item['valor_pago'] = payment[1]
                    else:
                        payments_item['valor_pago'] = helper.format_to_float(payment[1]) + helper.format_to_float(troco)
                    payments.append(payments_item)
                    total_geral += helper.format_to_float(payment[1])
                print(items, payments, total_geral, troco, data)
                self.imprimir_cupom(items, payments, total_geral, troco, data)
                self.fechar_tp_gdc_1()
            else:
                CTkMessagebox(message=f'Só é possível imprimir as Notas de Vendas realizadas.', icon='warning', title='Atenção')
                return
        except Exception as e:
            print(e)

    def tp_gdc_reset_widgets(self):
        self.tp_gdc_combobox_1_var.set(value='Selecionar Categoria')
        self.tp_gdc_entry_1.delete(0, END)
        self.tp_gdc_entry_2.delete(0, END)
        self.tp_gdc_clear_sinalizers()

    def fechar_tp_gdc_1(self):
        if self.tp_gdc_1:
            self.tp_gdc_1.destroy()
            self.update_tp_gdc_dia_tree(self.get_widget_data())

    def fechar_tp_gdc(self, event=None):
        if self.tp_gdc:
            self.tp_gdc.destroy()
            self.tp_gdc = None

    #endregion

    # region MÓDULO GDV (GERENCIAMENTO DE VENDAS)

    def abrir_tp_gdv(self):
        if self.tp_gdv:
            self.fechar_tp_gdv()
            return
        self.tp_gdv = CTkToplevel(self.root)
        self.tp_gdv.grab_set()
        self.tp_gdv.title('Gerenciamento de Vendas')
        self.tp_gdv.protocol('WM_DELETE_WINDOW', self.fechar_tp_gdv)
        self.tp_gdv_width = 1200
        self.tp_gdv_height = 700
        self.tp_gdv_x = self.root.winfo_width()//2 - self.tp_gdv_width//2   #essa e algumas abaixo, sao linhas que centralizam o tp na root
        self.tp_gdv_y = self.root.winfo_height()//2 - self.tp_gdv_height//2
        self.tp_gdv.geometry(f'{self.tp_gdv_width}x{self.tp_gdv_height}+{self.tp_gdv_x}+{self.tp_gdv_y}')
        self.tp_gdv.resizable(False, False)
        self.tp_gdv.attributes('-topmost', 'true')
        self.tp_gdv_ignore_enter = False
        self.tp_gdv_fonte = CTkFont('arial', 35, 'bold')

        #images
        previsao_img = CTkImage(light_image=Image.open(r'images\previsao.png'), size=(70, 70))

        #titlo
        self.tp_gdv_titlo = CTkLabel(self.tp_gdv, text='Gerenciamento de Vendas:', font=CTkFont('arial', 35, 'bold'))
        self.tp_gdv_titlo.place(relx=0.5, rely=0.02, anchor='n')

        #treeview wdgs
        self.tp_gdv_dia_tree_label = CTkLabel(self.tp_gdv, text=f'Vendas referentes ao dia: -', font=self.tp_cdm_fonte_padrao_bold)
        self.tp_gdv_dia_tree_label.place(relx=0.5, rely=0.11, anchor='n')
        self.tp_gdv_treeview_search_columns = ('id', 'descricao', 'valor', 'hora', 'desconto', 'troco', 'modo_pagamento')
        self.tp_gdv_dia_tree = ttk.Treeview(self.tp_gdv, columns=self.tp_gdv_treeview_search_columns, show="headings", height=20)
        self.tp_gdv_dia_tree.column(self.tp_gdv_treeview_search_columns[0], width=100, anchor=CENTER)
        self.tp_gdv_dia_tree.column(self.tp_gdv_treeview_search_columns[1], width=200, anchor=CENTER)
        self.tp_gdv_dia_tree.column(self.tp_gdv_treeview_search_columns[2], width=170, anchor=CENTER)
        self.tp_gdv_dia_tree.column(self.tp_gdv_treeview_search_columns[3], width=150, anchor=CENTER)
        self.tp_gdv_dia_tree.column(self.tp_gdv_treeview_search_columns[4], width=150, anchor=CENTER)
        self.tp_gdv_dia_tree.column(self.tp_gdv_treeview_search_columns[5], width=150, anchor=CENTER)
        self.tp_gdv_dia_tree.column(self.tp_gdv_treeview_search_columns[6], width=150, anchor=CENTER)
        self.tp_gdv_dia_tree.heading(self.tp_gdv_treeview_search_columns[0], text="ID", )
        self.tp_gdv_dia_tree.heading(self.tp_gdv_treeview_search_columns[1], text="Descrição", )
        self.tp_gdv_dia_tree.heading(self.tp_gdv_treeview_search_columns[2], text="Valor", )
        self.tp_gdv_dia_tree.heading(self.tp_gdv_treeview_search_columns[3], text="Hora", )
        self.tp_gdv_dia_tree.heading(self.tp_gdv_treeview_search_columns[4], text="Desconto", )
        self.tp_gdv_dia_tree.heading(self.tp_gdv_treeview_search_columns[5], text="Troco", )
        self.tp_gdv_dia_tree.heading(self.tp_gdv_treeview_search_columns[6], text="Modo Pgmt.", )
        self.tp_gdv_dia_tree.place(relx=0.5, rely=0.16, anchor='n')

        # Cria a Scrollbar e associa à Treeview
        self.gdv_scrollbar = CTkScrollbar(self.tp_gdv, orientation="vertical", command=self.tp_gdv_dia_tree.yview)
        self.gdv_scrollbar.place(relx=0.95, rely=0.3)
        self.tp_gdv_dia_tree.configure(yscrollcommand=self.gdv_scrollbar.set)

        #faturamento diario wdgts
        self.tp_gdv_faturamento_dia_label = CTkLabel(self.tp_gdv, text='Faturamento total do Dia:', font=self.tp_cdm_fonte_padrao_bold)
        self.tp_gdv_faturamento_dia_label.place(relx=0.1, rely=0.83)
        self.tp_gdv_faturamento_dia_label_1 = CTkLabel(self.tp_gdv, text='-', font=CTkFont('arial', 35, 'bold'), text_color='blue')
        self.tp_gdv_faturamento_dia_label_1.place(relx=0.32, rely=0.82)

        #faturamento diario previsao wdgts
        self.tp_gdv_previsao_dia_label_1 = CTkLabel(self.tp_gdv, text='Faturamento Previsto do Dia:', font=self.tp_cdm_fonte_padrao_bold)
        self.tp_gdv_previsao_dia_label_1.place(relx=0.5, rely=0.83)
        self.tp_gdv_previsao_dia_label_1 = CTkLabel(self.tp_gdv, text=f'R${helper.format_to_moeda(self.previsao_fat_dia)}', font=CTkFont('arial', 35, 'bold'), text_color='orange', image=previsao_img, compound='left')
        self.tp_gdv_previsao_dia_label_1.place(relx=0.75, rely=0.79)

        #faturamento mensal wdgts
        self.tp_gdv_faturamento_mensal_label = CTkLabel(self.tp_gdv, text='Faturamento total do Mês:', font=self.tp_cdm_fonte_padrao_bold)
        self.tp_gdv_faturamento_mensal_label.place(relx=0.1, rely=0.92)
        self.tp_gdv_faturamento_mensal_label_1 = CTkLabel(self.tp_gdv, text='-', font=CTkFont('arial', 35, 'bold'), text_color='blue')
        self.tp_gdv_faturamento_mensal_label_1.place(relx=0.32, rely=0.91)

        #faturamento mensal previsao wdgts
        self.tp_gdv_previsao_mes_label = CTkLabel(self.tp_gdv, text='Faturamento Previsto do Mês:', font=self.tp_cdm_fonte_padrao_bold)
        self.tp_gdv_previsao_mes_label.place(relx=0.5, rely=0.92)
        self.tp_gdv_previsao_mes_label_1 = CTkLabel(self.tp_gdv, text=f'R${helper.format_to_moeda(self.previsao_fat_mes)}', font=CTkFont('arial', 35, 'bold'), text_color='orange', image=previsao_img, compound='left')
        self.tp_gdv_previsao_mes_label_1.place(relx=0.75, rely=0.88)
        
        self.update_tp_gdv()

        #bind's
        self.tp_gdv.bind('<Escape>', self.fechar_tp_gdv)
        self.tp_gdv_dia_tree.bind('<Double-1>', self.tp_gdv_abrir_venda)

    def get_tp_gdv_widget_data(self):
        try:
            #definido a data atual do computador
            date = helper.get_date()
            dia = int(date[8:10])
            mes = int(date[5:7])
            ano = int(date[:4])

            #coletar e calcular o faturamento mensal
            total_amount_mes = 0
            sales_mes = database.get_all_sales_by_month(ano, mes)
            for sales in sales_mes:
                total_amount_mes += float(sales[2])

            #coletar e calcular o faturamento diário
            total_amount_base_day = 0
            hora = int(helper.get_horario()[:2])
            if 0 <= hora < 6: #se for madrugada (o dia base é o anterior)
                base_day = dt.strptime(date, '%Y-%m-%d') - timedelta(days=1)
                base_day = dt.strftime(base_day, '%Y-%m-%d')
            else:
                base_day = date
            sales_base_day = database.get_all_sales_from_base_day(base_day)
            for i, sale_base_day in enumerate(sales_base_day, start=1):#aproveitor essefor tanto para somar o total_amount_base_day como para inserir as vendas na tv
                self.tp_gdv_dia_tree.insert('', END, values=(sale_base_day[0], 'Venda Realizada n°'+str(i), helper.format_to_moeda(sale_base_day[2], 'R$'), sale_base_day[1][10:-3], helper.format_to_moeda(sale_base_day[4]), helper.format_to_moeda(sale_base_day[3]), sale_base_day[5]))
                total_amount_base_day += float(sale_base_day[2])
            #return da funcao
            return [total_amount_mes, total_amount_base_day, base_day]

        except Exception as e:
            print(e)
            CTkMessagebox(self.tp_gdc, message=f'Erro ao obter os dados do gerenciamneto de vendas.: {e}', icon='cancel', title='Erro')
            return False

    def update_tp_gdv(self):
        #recalcular os dados
        dados = self.get_tp_gdv_widget_data()

        #inserir os faturamentos e o base_day
        self.tp_gdv_dia_tree_label.configure(text=f'Vendas referentes ao dia: {dados[2]}')
        self.tp_gdv_faturamento_dia_label_1.configure(text=f'{helper.format_to_moeda(dados[1])}')
        self.tp_gdv_faturamento_mensal_label_1.configure(text=f'{helper.format_to_moeda(dados[0])}')

        self.tp_gdv_dia_tree.yview_moveto(1.0)


    def tp_gdv_abrir_venda(self, event=None):
        #pr
        if not self.tp_gdv_dia_tree.selection(): #trata o caso de o usuario nao identificar o a venda que gostaria de abrir os dados
                return
        else:
            #obtendo o sale_id da venda
            selected_venda = self.tp_gdv_dia_tree.focus()
            venda_values = self.tp_gdv_dia_tree.item(selected_venda, "values")
            venda_id = venda_values[0]
                
        self.tp_gdv_venda = CTkToplevel(self.root)
        self.tp_gdv_venda.title('DETALHES DE VENDA')
        self.tp_gdv_venda.protocol('WM_DELETE_WINDOW', self.fechar_tp_gdv_venda)
        self.tp_gdv_venda_width = self.root.winfo_width() * 80 // 100
        self.tp_gdv_venda_height = self.root.winfo_height()* 80 // 100
        self.tp_gdv_venda_x = self.root.winfo_width()//2 - self.tp_gdv_venda_width//2   #essa e algumas abaixo, sao linhas que centralizam o tp na root
        self.tp_gdv_venda_y = self.root.winfo_height()//2 - self.tp_gdv_venda_height//2
        self.tp_gdv_venda.geometry(f'{self.tp_gdv_venda_width}x{self.tp_gdv_venda_height}+{self.tp_gdv_venda_x}+{self.tp_gdv_venda_y}')
        self.tp_gdv_venda.resizable(False, False)
        self.tp_gdv_venda.attributes('-topmost', 'true')
        self.tp_gdv_venda.grab_set()

        #titlo
        self.tp_gdv_venda_titlo = CTkLabel(self.tp_gdv_venda, text=f'Detalhes da Venda {venda_id}:', font=CTkFont('arial', 35, 'bold'))
        self.tp_gdv_venda_titlo.place(relx=0.5, rely=0.01, anchor='n')

        #Treeview para exibir a lista de produtos
        colunas_treeview = ('Código', 'Item', 'Valor Unitário', 'Quantidade', 'Total')
        self.tp_gdv_venda_treeview = ttk.Treeview(self.tp_gdv_venda, columns=colunas_treeview, show='headings',height=20)
        self.tp_gdv_venda_treeview.place(relx=0.05, rely=0.23)
        self.tp_gdv_venda_treeview.column(colunas_treeview[0], width=70, anchor=CENTER)
        self.tp_gdv_venda_treeview.column(colunas_treeview[1], width=250, anchor=CENTER)
        self.tp_gdv_venda_treeview.column(colunas_treeview[2], width=120, anchor=CENTER)
        self.tp_gdv_venda_treeview.column(colunas_treeview[3], width=120, anchor=CENTER)
        self.tp_gdv_venda_treeview.column(colunas_treeview[4], width=120, anchor=CENTER)
        self.tp_gdv_venda_treeview.heading(colunas_treeview[0], text='CÓD.')
        self.tp_gdv_venda_treeview.heading(colunas_treeview[1], text='ITEM')
        self.tp_gdv_venda_treeview.heading(colunas_treeview[2], text='VALOR ÚNIT')
        self.tp_gdv_venda_treeview.heading(colunas_treeview[3], text='QUANT/KG')
        self.tp_gdv_venda_treeview.heading(colunas_treeview[4], text='TOTAL')
        self.tp_gdv_venda_treeview.place(relx=0.02, rely=0.125)

        
        # inserindo os valores na treeview
        sales_items = database.get_sales_items_by_sale_id(venda_id)
        preco_total = 0
        for i, item in enumerate(sales_items, start=1):
            produto_id, quantidade, preco = item
            total = helper.format_to_float(quantidade) * helper.format_to_float(preco)
            preco_total += total
            self.tp_gdv_venda_treeview.insert('','end', values=(i, database.get_product_name_by_id(produto_id)[0].upper(), helper.format_to_moeda(preco), quantidade, helper.format_to_moeda(total)))
        
        # preço total da venda
        self.tp_gdv_venda_total = CTkLabel(self.tp_gdv_venda, text='Total da Compra:', font=self.tp_cdm_fonte_padrao_bold)
        self.tp_gdv_venda_total.place(relx=0.675, rely=0.125)
        self.tp_gdv_venda_total = CTkLabel(self.tp_gdv_venda, text=f'{helper.format_to_moeda(preco_total)}', text_color='blue', font=self.tp_cdm_fonte_padrao_bold)
        self.tp_gdv_venda_total.place(relx=0.85, rely=0.125)

        # desconto
        self.tp_gdv_venda_total = CTkLabel(self.tp_gdv_venda, text='Desconto Aplicado:', font=self.tp_cdm_fonte_padrao_bold)
        self.tp_gdv_venda_total.place(relx=0.675, rely=0.225)
        self.tp_gdv_venda_total = CTkLabel(self.tp_gdv_venda, text=f'-R${venda_values[4]}', text_color='orange', font=self.tp_cdm_fonte_padrao_bold)
        self.tp_gdv_venda_total.place(relx=0.85, rely=0.225)
        
        # preço final da venda
        
        preco_final = helper.format_to_moeda(helper.format_to_float(preco_total) - helper.format_to_float(venda_values[4]))
        self.tp_gdv_venda_total = CTkLabel(self.tp_gdv_venda, text='Total Final:', font=self.tp_cdm_fonte_padrao_bold)
        self.tp_gdv_venda_total.place(relx=0.675, rely=0.325)
        self.tp_gdv_venda_total = CTkLabel(self.tp_gdv_venda, text=f'R${preco_final}', text_color='blue', font=self.tp_cdm_fonte_padrao_bold)
        self.tp_gdv_venda_total.place(relx=0.85, rely=0.325)

        #modos de pagamento
        last_rel_y = 0.425
        self.tp_gdv_venda_total = CTkLabel(self.tp_gdv_venda, text='Forma(s) de Pagamento:', font=self.tp_cdm_fonte_padrao_bold)
        self.tp_gdv_venda_total.place(relx=0.675, rely=0.425)

        payments = database.get_payments_by_sale_id(venda_id)

        last_rel_y = 0.435
        for payment in payments:
            last_rel_y += 0.05
            self.tp_gdv_venda_total = CTkLabel(self.tp_gdv_venda, text=f'+ R${helper.format_to_moeda(payment[1])} no {payment[0]}', text_color='green', font=self.tp_cdm_fonte_padrao_bold)
            self.tp_gdv_venda_total.place(relx=0.7, rely=last_rel_y)

        # troco
        self.tp_gdv_venda_total = CTkLabel(self.tp_gdv_venda, text='Troco Devolvido:', font=self.tp_cdm_fonte_padrao_bold)
        self.tp_gdv_venda_total.place(relx=0.675, rely=0.625)
        self.tp_gdv_venda_total = CTkLabel(self.tp_gdv_venda, text=f'R${venda_values[5]}', text_color='blue', font=self.tp_cdm_fonte_padrao_bold)
        self.tp_gdv_venda_total.place(relx=0.85, rely=0.625)

        # botao excluir

        lixeira_img = CTkImage(light_image=Image.open(r'images\lixeira.png'), size=(30, 30))

        self.tp_gdv_venda_button_deletar = CTkButton(self.tp_gdv_venda, text='Excluir', command=lambda:self.excluir_venda(venda_id), width=50, image=lixeira_img)
        self.tp_gdv_venda_button_deletar.place(relx=0.75, rely=0.85)

        #binds
        self.tp_gdv_venda.bind('<Escape>', self.fechar_tp_gdv_venda)

    def excluir_venda(self, venda_id):
        try:
            key = self.abrir_tp_password(self.tp_gdv_venda)
            if self.tp_password_feedback:
                cfm = database.delete_sale_by_id(venda_id)
                if cfm:
                    #fecha o tp
                    self.fechar_tp_gdv_venda()
                    #show cfm
                    msg = CTkMessagebox(self.tp_gdv_venda, message=f"Venda excluida com sucesso!", icon='check', title='Sucesso')
                    self.tp_gdv.wait_window(msg)
                    #atualizar a treeview clientes
                    self.update_tp_gdv()
                else:
                    raise Exception('Erro: Exclusão da venda não confirmada.')
    
        except Exception as e:
            CTkMessagebox(self.tp_gdv_venda, message=f'Erro: {e}', icon='cancel', title='Erro')
            return
        finally:
            self.tp_password_feedback == False
        
    def fechar_tp_gdv_venda(self, event=None):
        self.tp_gdv_venda.destroy()
        self.tp_gdv_venda = None

    def fechar_tp_gdv(self, event=None):
        self.tp_gdv.destroy()
        self.tp_gdv = None

    #endregion

    # region MÓDULO Clientes
    def abrir_clientes(self):
        self.tp_clientes = CTkToplevel(self.root)
        self.tp_clientes.title('Clientes')
        self.tp_clientes.protocol('WM_DELETE_WINDOW', self.fechar_tp_clientes)
        self.tp_clientes_width = self.root.winfo_width() * 80 // 100
        self.tp_clientes_height = self.root.winfo_height()* 80 // 100
        self.tp_clientes_x = self.root.winfo_width()//2 - self.tp_clientes_width//2   #essa e algumas abaixo, sao linhas que centralizam o tp na root
        self.tp_clientes_y = self.root.winfo_height()//2 - self.tp_clientes_height//2
        self.tp_clientes.geometry(f'{self.tp_clientes_width}x{self.tp_clientes_height}+{self.tp_clientes_x}+{self.tp_clientes_y}')
        self.tp_clientes.resizable(False, False)
        self.tp_clientes.attributes('-topmost', 'true')
        self.tp_clientes.grab_set()

        self.clientes_img = Image.open(r'images\clientes.png')
        registro_cliente_img = Image.open(r'images\clientes_cadastro.png')
        pesquisa_img = Image.open(r'images\ilustracao_pesquisa_mercadoria.png')

        # tp ilustração
        self.tp_clientes_ilustracao = CTkLabel(self.tp_clientes,  text='', image=CTkImage(light_image=self.clientes_img, size=(99, 99)))
        self.tp_clientes_ilustracao.place(relx=0.075, rely=0.05, anchor='n')

        # entry para inserir a busca
        self.tp_clientes_entry_1 = CTkEntry(self.tp_clientes, width=self.tp_clientes_width - (self.tp_clientes_width * 30 // 100), height=50, placeholder_text='Procurar cliente por nome ou CPF...', font=self.fonte_basic, border_color='black')
        self.tp_clientes_entry_1.place(relx=0.15, rely=0.1)
        self.tp_clientes_entry_1.bind("<KeyRelease>", self.procurar_cliente)

        # Treeview para exibir os resultados de forma tabular
        self.clientes_treeview_columns = ('id', 'nome', 'whatsapp', 'cpf')
        self.clientes_treeview = ttk.Treeview(self.tp_clientes, columns=self.clientes_treeview_columns, show="headings", height=15)
        self.clientes_treeview.column(self.clientes_treeview_columns[0], width=80, anchor=CENTER)
        self.clientes_treeview.column(self.clientes_treeview_columns[1], width=400, anchor=CENTER)
        self.clientes_treeview.column(self.clientes_treeview_columns[2], width=200, anchor=CENTER)
        self.clientes_treeview.column(self.clientes_treeview_columns[3], width=200, anchor=CENTER)
        self.clientes_treeview.heading(self.clientes_treeview_columns[0], text="id".capitalize(), )
        self.clientes_treeview.heading(self.clientes_treeview_columns[1], text="nome".capitalize(), )
        self.clientes_treeview.heading(self.clientes_treeview_columns[2], text="whatsapp".capitalize())
        self.clientes_treeview.heading(self.clientes_treeview_columns[3], text="cpf".capitalize())
        self.clientes_treeview.place(relx=0.5, rely=0.25, anchor='n')

        # Cria a Scrollbar e associa à Treeview
        scrollbar = CTkScrollbar(self.tp_clientes, orientation="vertical", command=self.clientes_treeview.yview)
        scrollbar.place(relx=0.92, rely=0.35)
        self.clientes_treeview.configure(yscrollcommand=scrollbar.set)

        # botao registrar cliente
        self.tp_clientes_ilustracao = CTkButton(self.tp_clientes,  text='Cadastrar Novo Cliente', image=CTkImage(light_image=registro_cliente_img, size=(60, 60)), font=self.tp_cdm_fonte_padrao, text_color='black', fg_color='transparent', width=0, command=lambda:self.abrir_clientes_registro(0))
        self.tp_clientes_ilustracao.place(relx=0.03, rely=0.86)

        # botao buscar conta do cliente
        self.tp_clientes_buscar_conta_cliente = CTkButton(self.tp_clientes,  text='Buscar conta do cliente', image=CTkImage(light_image=pesquisa_img, size=(60, 60)), font=self.tp_cdm_fonte_padrao, text_color='black' ,fg_color='transparent', width=0, command=lambda:self.buscar_conta_cliente())
        self.tp_clientes_buscar_conta_cliente.place(relx=0.37, rely=0.86)

        # Editar dados do cliente
        self.tp_clientes_buscar_conta_cliente = CTkButton(self.tp_clientes,  text='Editar dados do cliente', image=CTkImage(light_image=pesquisa_img, size=(60, 60)), font=self.tp_cdm_fonte_padrao, text_color='black' ,fg_color='transparent', width=0, command=lambda:self.abrir_clientes_registro(1))
        self.tp_clientes_buscar_conta_cliente.place(relx=0.7, rely=0.86)

        self.tp_clientes.bind('<Escape>', lambda event: self.fechar_tp_clientes())
        self.tp_clientes.bind('<Double-1>', lambda event: self.abrir_clientes_registro(1))

        self.tp_clientes_treeview_update()

    def procurar_cliente(self, event=None):
        search_term = self.tp_clientes_entry_1.get()
        if search_term.strip().isdigit():
            results = database.get_clientes_by_coluna('cpf', search_term)
        else: 
            results = database.get_clientes_by_coluna('nome', search_term)

        #limpando a treeview
        for item in self.clientes_treeview.get_children():
            self.clientes_treeview.delete(item)
        #inserindo os dados na nova busca
        for row in results:
            self.clientes_treeview.insert('', END, values=helper.formatar_row_para_treeview_clientes(row))

    def tp_clientes_treeview_update(self):
        # Limpa a Treeview antes de exibir os novos resultados
        for item in self.clientes_treeview.get_children():
            self.clientes_treeview.delete(item)
        # Chama a função de busca no banco de dados do backend
        results = database.get_all_clientes()
        if results:
            # Adiciona os resultados na Treeview
            for row in results:
                self.clientes_treeview.insert('', END, values=helper.formatar_row_para_treeview_clientes(row))

    def abrir_clientes_registro(self, edit, event=None):
        if edit: #Se for abrir  no modo edição
            titlo_janela = 'Editar Dados do Cliente'
            if not self.clientes_treeview.selection(): #trata o caso de o usuario nao identificar o cliente que gostaria de editar os dados
                msg = CTkMessagebox(self.tp_clientes, message=f'Selecione um cliente antes de utilizar essa função.', icon='warning', title='Atenção')
                self.tp_clientes.wait_window(msg)
                return
            #coletando o id do cliente selecionado
            selected_item = self.clientes_treeview.focus()
            item_values = self.clientes_treeview.item(selected_item, "values")
            dados_cliente = database.get_cliente_by_id(item_values[0])
            if not dados_cliente:
                CTkMessagebox(self.tp_clientes, message=f'Não foi possível registrar o cliente.', icon='cancel', title='Erro')
                return
        else:
            titlo_janela = 'Registrar Cliente'
        self.tp_clientes_registro = CTkToplevel(self.tp_clientes)
        self.tp_clientes_registro.title(titlo_janela)
        self.tp_clientes_registro.protocol('WM_DELETE_WINDOW', self.fechar_tp_clientes_registro)
        self.tp_clientes_registro_width = self.root.winfo_width() * 70 // 100
        self.tp_clientes_registro_height = self.root.winfo_height()* 70 // 100
        self.tp_clientes_registro_x = self.root.winfo_width()//2 - self.tp_clientes_registro_width//2   #essa e algumas abaixo, sao linhas que centralizam o tp na root
        self.tp_clientes_registro_y = self.root.winfo_height()//2 - self.tp_clientes_registro_height//2
        self.tp_clientes_registro.geometry(f'{self.tp_clientes_registro_width}x{self.tp_clientes_registro_height}+{self.tp_clientes_registro_x}+{self.tp_clientes_registro_y}')
        self.tp_clientes_registro.resizable(False, False)
        self.tp_clientes_registro.attributes('-topmost', 'true')
        self.tp_clientes_registro.grab_set()

        self.clientes_cadastro_img = Image.open(r'images\clientes_cadastro.png')

        #variveis de controle
        self.tp_clientes_registro_entry_nome_keyrelease_block = False
        self.tp_clientes_registro_entry_cpf_keyrelease_block = False
        self.tp_clientes_registro_entry_whatsapp_keyrelease_block = False
        self.tp_clientes_registro_entry_email_keyrelease_block = False
        self.tp_clientes_registro_entry_endereco_keyrelease_block = False
        self.tp_clientes_registro_entry_datanascimento_keyrelease_block = False
        self.tp_clientes_registro_entry_limite_keyrelease_block = False

        if edit:
            self.tp_clientes_registro_nome_validado = True
            self.tp_clientes_registro_cpf_validado = True
            self.tp_clientes_registro_whatsapp_validado = True
            self.tp_clientes_registro_email_validado = True
            self.tp_clientes_registro_endereco_validado = True
            self.tp_clientes_registro_datanascimento_validado = True
            self.tp_clientes_registro_limite_validado = True
        else:
            self.tp_clientes_registro_nome_validado = False #Usar False para as variaveis ref à campos obrigatórios ;)
            self.tp_clientes_registro_cpf_validado = False
            self.tp_clientes_registro_whatsapp_validado = False
            self.tp_clientes_registro_email_validado = True
            self.tp_clientes_registro_endereco_validado = True
            self.tp_clientes_registro_datanascimento_validado = True
            self.tp_clientes_registro_limite_validado = True

        # tp ilustração
        self.tp_clientes_registro_ilustracao = CTkLabel(self.tp_clientes_registro,  text='', image=CTkImage(light_image=self.clientes_cadastro_img, size=(99, 99)))
        self.tp_clientes_registro_ilustracao.place(relx=0.075, rely=0.02)

        #titlo
        self.tp_clientes_registro_titlo = CTkLabel(self.tp_clientes_registro,  text=titlo_janela, font=CTkFont('arial', 35, 'bold'), compound='left')
        self.tp_clientes_registro_titlo.place(relx=0.5, rely=0.05, anchor='n')

        #campos: id, nome, cpf, whatsapp, endereço, email, genero, data_registro

        #campo nome
        self.tp_clientes_registro_label_nome = CTkLabel(self.tp_clientes_registro, text='NOME * :', font=self.fonte_basic)
        self.tp_clientes_registro_label_nome.place(relx=0.05, rely=0.325)
        self.tp_clientes_registro_entry_nome = CTkEntry(self.tp_clientes_registro, font=self.fonte_basic, width=300, height=35)
        self.tp_clientes_registro_entry_nome.place(relx=0.15, rely=0.325)
        self.tp_clientes_registro_entry_nome_sinalizer = CTkLabel(self.tp_clientes_registro ,text_color='red', height=0)

        self.tp_clientes_registro_entry_nome.bind('<KeyRelease>', lambda event:self.tp_clientes_registro_entry_nome_keyrelease())

        #campo cpf
        self.tp_clientes_registro_label_cpf = CTkLabel(self.tp_clientes_registro, text='CPF *:', font=self.fonte_basic)
        self.tp_clientes_registro_label_cpf.place(relx=0.05, rely=0.45)
        self.tp_clientes_registro_entry_cpf = CTkEntry(self.tp_clientes_registro, font=self.fonte_basic, width=300, height=35)
        self.tp_clientes_registro_entry_cpf.place(relx=0.15, rely=0.45)
        self.tp_clientes_registro_entry_cpf_sinalizer = CTkLabel(self.tp_clientes_registro ,text_color='red', height=0)

        self.tp_clientes_registro_entry_cpf.bind('<KeyRelease>', lambda event:self.tp_clientes_registro_entry_cpf_keyrelease())

        #campo whatsapp
        self.tp_clientes_registro_label_whatsapp = CTkLabel(self.tp_clientes_registro, text='WHATSAPP:*', font=self.fonte_basic)
        self.tp_clientes_registro_label_whatsapp.place(relx=0.05, rely=0.575)
        self.tp_clientes_registro_entry_whatsapp = CTkEntry(self.tp_clientes_registro, font=self.fonte_basic, width=300, height=35)
        self.tp_clientes_registro_entry_whatsapp.place(relx=0.15, rely=0.575)
        self.tp_clientes_registro_entry_whatsapp_sinalizer = CTkLabel(self.tp_clientes_registro ,text_color='red', height=0)
        
        self.tp_clientes_registro_entry_whatsapp.bind('<KeyRelease>', lambda event:self.tp_clientes_registro_entry_whatsapp_keyrelease())

        #campo e-mail
        self.tp_clientes_registro_label_email = CTkLabel(self.tp_clientes_registro, text='E-MAIL:', font=self.fonte_basic)
        self.tp_clientes_registro_label_email.place(relx=0.05, rely=0.7)
        self.tp_clientes_registro_entry_email = CTkEntry(self.tp_clientes_registro, font=self.fonte_basic, width=300, height=35)
        self.tp_clientes_registro_entry_email.place(relx=0.15, rely=0.7)
        self.tp_clientes_registro_entry_email_sinalizer = CTkLabel(self.tp_clientes_registro ,text_color='red', height=0)

        self.tp_clientes_registro_entry_email.bind('<KeyRelease>', lambda event:self.tp_clientes_registro_entry_email_keyrelease())

        #campo genero
        self.tp_clientes_registro_genero_var = StringVar(value='masculino')

        self.tp_clientes_registro_label_genero = CTkLabel(self.tp_clientes_registro, text='SEXO:', font=self.fonte_basic)
        self.tp_clientes_registro_label_genero.place(relx=0.5, rely=0.325)
        self.tp_clientes_registro_radiobutton_genero_masculino = CTkRadioButton(self.tp_clientes_registro, text='MASCULINO', variable=self.tp_clientes_registro_genero_var, value='masculino', border_width_checked=10)
        self.tp_clientes_registro_radiobutton_genero_masculino.place(relx=0.65, rely=0.325)
        self.tp_clientes_registro_radiobutton_genero_feminino = CTkRadioButton(self.tp_clientes_registro, text='FEMININO', variable=self.tp_clientes_registro_genero_var, value='feminino', border_width_checked=10)
        self.tp_clientes_registro_radiobutton_genero_feminino.place(relx=0.8, rely=0.325)

        #campo endereco
        self.tp_clientes_registro_label_endereco = CTkLabel(self.tp_clientes_registro, text='ENDEREÇO:', font=self.fonte_basic)
        self.tp_clientes_registro_label_endereco.place(relx=0.5, rely=0.45)
        self.tp_clientes_registro_entry_endereco = CTkEntry(self.tp_clientes_registro, font=self.fonte_basic, width=300, height=35)
        self.tp_clientes_registro_entry_endereco.place(relx=0.62, rely=0.45)
        self.tp_clientes_registro_entry_endereco_sinalizer = CTkLabel(self.tp_clientes_registro ,text_color='red', height=0)

        self.tp_clientes_registro_entry_endereco.bind('<KeyRelease>', lambda event:self.tp_clientes_registro_entry_endereco_keyrelease())

        #campo data nascimento
        self.tp_clientes_registro_label_datanascimento = CTkLabel(self.tp_clientes_registro, text='DATA NASC.:', font=self.fonte_basic)
        self.tp_clientes_registro_label_datanascimento.place(relx=0.5, rely=0.575)
        self.tp_clientes_registro_entry_datanascimento = CTkEntry(self.tp_clientes_registro, font=self.fonte_basic, width=300, height=35, placeholder_text='Ex: 19/06/1999', placeholder_text_color='gray')
        self.tp_clientes_registro_entry_datanascimento.place(relx=0.62, rely=0.575)
        self.tp_clientes_registro_entry_datanascimento_sinalizer = CTkLabel(self.tp_clientes_registro ,text_color='red', height=0)

        self.tp_clientes_registro_entry_datanascimento.bind('<KeyRelease>', lambda event:self.tp_clientes_registro_entry_datanascimento_keyrelease())
    
        #campo limite
        self.tp_clientes_registro_label_limite = CTkLabel(self.tp_clientes_registro, text='LIMITE:', font=self.fonte_basic)
        self.tp_clientes_registro_label_limite.place(relx=0.5, rely=0.7)
        self.tp_clientes_registro_entry_limite = CTkEntry(self.tp_clientes_registro, font=self.fonte_basic, width=300, height=35)
        self.tp_clientes_registro_entry_limite.place(relx=0.62, rely=0.7)
        self.tp_clientes_registro_entry_limite_sinalizer = CTkLabel(self.tp_clientes_registro ,text_color='red', height=0)
        if not edit:
            self.tp_clientes_registro_entry_limite.insert(0, '0')

        self.tp_clientes_registro_entry_limite.bind('<KeyRelease>', lambda event:self.tp_clientes_registro_entry_limite_keyrelease())

        #botao
        if edit:
            self.tp_clientes_registro_button = CTkButton(self.tp_clientes_registro, font=self.fonte_basic, text='ATUALIZAR', command=lambda:self.tp_clientes_registro_editar_cliente(dados_cliente[0]), state='disabled', fg_color='gray')

        else:
            self.tp_clientes_registro_button = CTkButton(self.tp_clientes_registro, font=self.fonte_basic, text='CADASTRAR', command=lambda:self.tp_clientes_registro_registrar_cliente(), state='disabled', fg_color='gray')
        
        self.tp_clientes_registro_button.place(relx=0.5, rely=0.85, anchor='n')

        #dica
        self.tp_clientes_registro_label_dica = CTkLabel(self.tp_clientes_registro, text='Campos com * são obrigatórios.', font=self.fonte_basic, height=0)
        self.tp_clientes_registro_label_dica.place(relx=0.05, rely=0.925)

        if edit: #inserir os dados do cliente selecionado nos campos correspondentes
            #nome
            self.tp_clientes_registro_entry_nome.insert(0, dados_cliente[1])
            #cpf
            self.tp_clientes_registro_entry_cpf.insert(0, dados_cliente[2])
            #whats
            self.tp_clientes_registro_entry_whatsapp.insert(0, dados_cliente[3])
            #email
            email = dados_cliente[4] if dados_cliente[4] else '' #gambiarra para contornar o erro de o Email ser NULL no database
            self.tp_clientes_registro_entry_email.insert(0, email)
            #genero
            self.tp_clientes_registro_genero_var.set(dados_cliente[5])
            #endereco
            self.tp_clientes_registro_entry_endereco.insert(0, dados_cliente[6])
            #data de nascimento
            self.tp_clientes_registro_entry_datanascimento.insert(0, dados_cliente[7])
            #limite
            self.tp_clientes_registro_entry_limite.insert(0, dados_cliente[8])

            #disparando o check das variaseis para ativar o botao do formulario
            self.tp_clientes_registro_check_campos_obrigatorios()

        #bind's
        self.tp_clientes_registro.bind('<Escape>', lambda event: self.fechar_tp_clientes_registro())
        self.tp_clientes_registro.bind('<Return>', lambda event: self.tp_clientes_registro_button.invoke())

        self.tp_clientes_registro.after(AFTER_INTERVALO, self.tp_clientes_registro_label_nome.focus_set())

    def tp_clientes_registro_entry_nome_keyrelease(self):
        if self.tp_clientes_registro_entry_nome_keyrelease_block:
            return
        self.tp_clientes_registro_entry_nome_keyrelease_block = True
        self.tp_clientes_registro_nome_validado = False

        #limpador de sinalizadores
        self.tp_clientes_registro_entry_nome.configure(border_color='gray')
        self.tp_clientes_registro_entry_nome_sinalizer.place_forget()
       
        #definindo variaveis
        try:
            inserido = self.tp_clientes_registro_entry_nome.get()
            if inserido.strip() == '':
                self.tp_clientes_registro_nome_validado = False
                return

            inserido_cru = inserido.replace(' ', '')
            inserido_cru_len = len(inserido_cru)
            #validador
            if inserido_cru_len > 8 and inserido_cru.isalpha():
                    self.tp_clientes_registro_nome_validado = True
                    self.tp_clientes_registro_entry_nome.configure(border_color='green')
            elif not inserido_cru.isalpha():
                self.tp_clientes_registro_entry_nome.configure(border_color='red')
                self.tp_clientes_registro_entry_nome_sinalizer.configure(text='O nome deve conter apenas letras.')
                self.tp_clientes_registro_entry_nome_sinalizer.place(relx=0.15, rely=0.4)
            elif inserido_cru_len < 8:
                self.tp_clientes_registro_entry_nome.configure(border_color='red')
                self.tp_clientes_registro_entry_nome_sinalizer.configure(text='O nome deve conter ao menos 8 letras.')
                self.tp_clientes_registro_entry_nome_sinalizer.place(relx=0.15, rely=0.4)

        except Exception as e:
            current_time = dt.now().strftime('%Y-%m-%d %H:%M:%S')
            with open('txts/errors.txt', 'a') as a:
                a.write(f'{current_time} - Interface.py - Cliente Modulo - tp_clientes_registro_entry_nome_keyrelease: {e}\n')
        finally:
            self.tp_clientes_registro_check_campos_obrigatorios()
            self.tp_clientes_registro_entry_nome_keyrelease_block = False

    def tp_clientes_registro_entry_cpf_keyrelease(self):
        if self.tp_clientes_registro_entry_cpf_keyrelease_block:
            return
        self.tp_clientes_registro_entry_cpf_keyrelease_block = True
        self.tp_clientes_registro_cpf_validado = False

        
        #limpador de sinalizadores
        self.tp_clientes_registro_entry_cpf.configure(border_color='gray')
        self.tp_clientes_registro_entry_cpf_sinalizer.place_forget()
        try:
            #definindo variaveis
            inserido = self.tp_clientes_registro_entry_cpf.get()
            if inserido.strip() == '':#antecipacao do fim da funcao para o caso de campo vazio
                self.tp_clientes_registro_cpf_validado = True
                return
            inserido_cru = inserido.replace('.', '').replace('-', '')
            inserido_cru_len = len(inserido_cru)
            #formatador 
            conteudo_formatado = ''
            for i, char in enumerate(inserido_cru):
                if i in (3, 6):
                    char= '.'+char
                elif i == 9:
                    char= '-'+char
                conteudo_formatado = conteudo_formatado+char
            self.tp_clientes_registro_entry_cpf.delete(0, END)
            self.tp_clientes_registro_entry_cpf.insert(0, conteudo_formatado)

            #validador
            print(inserido_cru)
            if inserido_cru_len == 11 and inserido_cru.isdigit():
                if database.get_clientes_by_coluna('cpf', conteudo_formatado):#verifica se contém algum cliente com o CPF inserido na base de dados
                    self.tp_clientes_registro_entry_cpf_sinalizer.configure(text='O CPF informado já está cadastrado.')
                    self.tp_clientes_registro_entry_cpf_sinalizer.place(relx=0.15, rely=0.53)
                else:#para o caso de não estar registrado
                    self.tp_clientes_registro_cpf_validado = True
                    self.tp_clientes_registro_entry_cpf.configure(border_color='green')
                    self.tp_clientes_registro_entry_cpf.event_generate('<Tab>')
                    
            else:
                self.tp_clientes_registro_entry_cpf.configure(border_color='red')
                self.tp_clientes_registro_entry_cpf_sinalizer.configure(text='O CPF deve conter 11 caracteres numéricos.')
                self.tp_clientes_registro_entry_cpf_sinalizer.place(relx=0.15, rely=0.53)

        except Exception as e:
            current_time = dt.now().strftime('%Y-%m-%d %H:%M:%S')
            with open('txts/errors.txt', 'a') as a:
                a.write(f'{current_time} - Interface.py - Cliente Modulo - tp_clientes_registro_entry_cpf_keyrelease: {e}\n')
        finally:
            self.tp_clientes_registro_check_campos_obrigatorios()
            self.tp_clientes_registro_entry_cpf_keyrelease_block = False

    def tp_clientes_registro_entry_whatsapp_keyrelease(self):
        if self.tp_clientes_registro_entry_whatsapp_keyrelease_block:
            return
        self.tp_clientes_registro_entry_whatsapp_keyrelease_block = True
        self.tp_clientes_registro_whatsapp_validado = False
        
        #limpador de sinalizadores
        self.tp_clientes_registro_entry_whatsapp.configure(border_color='gray')
        self.tp_clientes_registro_entry_whatsapp_sinalizer.place_forget()
       
        try:
            #inicio da funcao propriamente dita
            inserido = self.tp_clientes_registro_entry_whatsapp.get()
            if inserido.strip() == '':
                self.tp_clientes_registro_whatsapp_validado = True
                return
            inserido_cru = inserido.replace('(', '').replace(')', '').replace(' ', '')
            inserido_cru_len = len(inserido_cru)
            #formatador 
            conteudo_formatado = ''
            for i, char in enumerate(inserido_cru):
                if i == 0:
                    conteudo_formatado = conteudo_formatado+'('
                elif i == 2:     
                    conteudo_formatado = conteudo_formatado+') '
                conteudo_formatado = conteudo_formatado+char
            self.tp_clientes_registro_entry_whatsapp.delete(0, END)
            self.tp_clientes_registro_entry_whatsapp.insert(0, conteudo_formatado)

            #validador
            if inserido_cru_len == 11 and inserido_cru.isdigit():
                if database.get_clientes_by_coluna('whatsapp', inserido_cru):#verifica se contém algum cliente com esse whatsapp na base de dados
                    self.tp_clientes_registro_entry_whatsapp_sinalizer.configure(text='O número informado já está cadastrado.')
                    self.tp_clientes_registro_entry_whatsapp_sinalizer.place(relx=0.15, rely=0.65)
                else:#para o caso de não estar registrado
                    self.tp_clientes_registro_entry_whatsapp.configure(border_color='green')
                    self.tp_clientes_registro_entry_whatsapp.event_generate('<Tab>')
                    self.tp_clientes_registro_whatsapp_validado = True
            else:
                self.tp_clientes_registro_entry_whatsapp.configure(border_color='red')
                self.tp_clientes_registro_entry_whatsapp_sinalizer.configure(text='O número deve conter 11 caracteres numéricos.')
                self.tp_clientes_registro_entry_whatsapp_sinalizer.place(relx=0.15, rely=0.65)

        except Exception as e:
            current_time = dt.now().strftime('%Y-%m-%d %H:%M:%S')
            with open('txts/errors.txt', 'a') as a:
                a.write(f'{current_time} - Interface.py - Cliente Modulo - tp_clientes_registro_entry_whatsapp_keyrelease: {e}\n')
        finally:
            self.tp_clientes_registro_check_campos_obrigatorios()
            self.tp_clientes_registro_entry_whatsapp_keyrelease_block = False

    def tp_clientes_registro_entry_email_keyrelease(self):
        if self.tp_clientes_registro_entry_email_keyrelease_block:
            return
        self.tp_clientes_registro_entry_email_keyrelease_block = True
        self.tp_clientes_registro_email_validado = False
        
        #limpador de sinalizadores
        self.tp_clientes_registro_entry_email.configure(border_color='gray')
        self.tp_clientes_registro_entry_email_sinalizer.place_forget()
       
        try:
            #inicio da funcao propriamente dita
            inserido = self.tp_clientes_registro_entry_email.get()
            if inserido.strip() == '':
                self.tp_clientes_registro_email_validado = True
                return
            #validador
            if '@' in inserido and '.com' in inserido:
                if len(inserido.split('@')) == 2  and inserido[-4:] == '.com':
                    if database.get_clientes_by_coluna('email', inserido):#verifica se contém algum cliente com esse whatsapp na base de dados
                        self.tp_clientes_registro_entry_email.configure(border_color='red')
                        self.tp_clientes_registro_entry_email_sinalizer.configure(text='O E-mail informado já está cadastrado.')
                        self.tp_clientes_registro_entry_email_sinalizer.place(relx=0.15, rely=0.775)
                    else:       
                        self.tp_clientes_registro_entry_email.configure(border_color='green')
                        self.tp_clientes_registro_entry_email.event_generate('<Tab>')
                        self.tp_clientes_registro_email_validado = True
                else:
                    self.tp_clientes_registro_entry_email.configure(border_color='red')
                    self.tp_clientes_registro_entry_email_sinalizer.configure(text='E-mail inválido.')
                    self.tp_clientes_registro_entry_email_sinalizer.place(relx=0.15, rely=0.775)
            else:
                self.tp_clientes_registro_entry_email.configure(border_color='red')
                self.tp_clientes_registro_entry_email_sinalizer.configure(text='E-mail inválido.')
                self.tp_clientes_registro_entry_email_sinalizer.place(relx=0.15, rely=0.775)

        except Exception as e:
            current_time = dt.now().strftime('%Y-%m-%d %H:%M:%S')
            with open('txts/errors.txt', 'a') as a:
                a.write(f'{current_time} - Interface.py - Cliente Modulo - tp_clientes_registro_entry_email_keyrelease: {e}\n')
        finally:
            self.tp_clientes_registro_check_campos_obrigatorios()
            self.tp_clientes_registro_entry_email_keyrelease_block = False

    def tp_clientes_registro_entry_endereco_keyrelease(self):
        if self.tp_clientes_registro_entry_endereco_keyrelease_block:
            return
        self.tp_clientes_registro_entry_endereco_keyrelease_block = True
        self.tp_clientes_registro_endereco_validado = False
        
        #limpador de sinalizadores
        self.tp_clientes_registro_entry_endereco.configure(border_color='gray')
        self.tp_clientes_registro_entry_endereco_sinalizer.place_forget()
        
        #inicio da funcao propriamente dita
        try:
            inserido = self.tp_clientes_registro_entry_endereco.get()
            if inserido.strip() == '':
                self.tp_clientes_registro_endereco_validado = True
                return
            inserido_len = len(inserido)
            #validador
            numero_check = False
            alpha_check = False
            for char in inserido:
                if char.isdigit():
                    numero_check = True
                elif char.isalpha():
                    alpha_check = True
            if numero_check and alpha_check and inserido_len > 5:
                self.tp_clientes_registro_entry_endereco.configure(border_color='green')
                self.tp_clientes_registro_endereco_validado = True
            else:
                self.tp_clientes_registro_entry_endereco.configure(border_color='red')
                self.tp_clientes_registro_entry_endereco_sinalizer.configure(text='Endereço inválido')
                self.tp_clientes_registro_entry_endereco_sinalizer.place(relx=0.62, rely=0.53)

        except Exception as e:
            current_time = dt.now().strftime('%Y-%m-%d %H:%M:%S')
            with open('txts/errors.txt', 'a') as a:
                a.write(f'{current_time} - Interface.py - Cliente Modulo - tp_clientes_registro_entry_endereco_keyrelease: {e}\n')
        finally:
            self.tp_clientes_registro_check_campos_obrigatorios()
            self.tp_clientes_registro_entry_endereco_keyrelease_block = False

    def tp_clientes_registro_entry_datanascimento_keyrelease(self):
        if self.tp_clientes_registro_entry_datanascimento_keyrelease_block:
            return
        self.tp_clientes_registro_entry_datanascimento_keyrelease_block = True
        self.tp_clientes_registro_datanascimento_validado = False
        
        #limpador de sinalizadores
        self.tp_clientes_registro_entry_datanascimento.configure(border_color='gray')
        self.tp_clientes_registro_entry_datanascimento_sinalizer.place_forget()
       
        try:
            #definindo variaveis
            inserido = self.tp_clientes_registro_entry_datanascimento.get()
            if inserido.strip() == '':
                self.tp_clientes_registro_datanascimento_validado = True
                return
            inserido_cru = inserido.replace('/', '')
            #formatador 
            conteudo_formatado = ''
            for i, char in enumerate(inserido_cru):
                if i in (2, 4):
                    char= '/'+char
                conteudo_formatado = conteudo_formatado+char
            self.tp_clientes_registro_entry_datanascimento.delete(0, END)
            self.tp_clientes_registro_entry_datanascimento.insert(0, conteudo_formatado)

            #validador
            if helper.check_date(conteudo_formatado)[0]:
                    self.tp_clientes_registro_datanascimento_validado = True
                    self.tp_clientes_registro_entry_datanascimento.configure(border_color='green')
            else:
                self.tp_clientes_registro_entry_datanascimento.configure(border_color='red')
                self.tp_clientes_registro_entry_datanascimento_sinalizer.configure(text='Data inválida. Use: DD/MM/AAAA.')
                self.tp_clientes_registro_entry_datanascimento_sinalizer.place(relx=0.5, rely=0.65)

        except Exception as e:
            current_time = dt.now().strftime('%Y-%m-%d %H:%M:%S')
            with open('txts/errors.txt', 'a') as a:
                a.write(f'{current_time} - Interface.py - Cliente Modulo - tp_clientes_registro_entry_cpf_keyrelease: {e}\n')
        finally:
            self.tp_clientes_registro_check_campos_obrigatorios()
            self.tp_clientes_registro_entry_datanascimento_keyrelease_block = False

    def tp_clientes_registro_entry_limite_keyrelease(self):
        if self.tp_clientes_registro_entry_limite_keyrelease_block:
            return
        self.tp_clientes_registro_entry_limite_keyrelease_block = True
        self.tp_clientes_registro_limite_validado = False
        
        #limpador de sinalizadores
        self.tp_clientes_registro_entry_limite.configure(border_color='gray')
        self.tp_clientes_registro_entry_limite_sinalizer.place_forget()
       
        try:
            #definindo variaveis
            inserido = self.tp_clientes_registro_entry_limite.get()
            if inserido.strip() == '':
                self.tp_clientes_registro_limite_validado = True #quer dizer que nada foi inserido e o campo nao é obrigatorio (até entao). por o campo é dado como validado
                return
            inserido_cru = inserido.replace(',', '').replace('.', '').strip()
            #formatador
            conteudo_formatado = inserido.strip()
            self.tp_clientes_registro_entry_limite.delete(0, END)
            self.tp_clientes_registro_entry_limite.insert(0, conteudo_formatado)
            #validador
            if inserido_cru.isdigit():
                    self.tp_clientes_registro_limite_validado = True
                    self.tp_clientes_registro_entry_limite.configure(border_color='green')
            else:
                self.tp_clientes_registro_entry_limite.configure(border_color='red')
                self.tp_clientes_registro_entry_limite_sinalizer.configure(text='Valor inválido.')
                self.tp_clientes_registro_entry_limite_sinalizer.place(relx=0.5, rely=0.77)

        except Exception as e:
            current_time = dt.now().strftime('%Y-%m-%d %H:%M:%S')
            with open('txts/errors.txt', 'a') as a:
                a.write(f'{current_time} - Interface.py - Cliente Modulo - tp_clientes_registro_entry_cpf_keyrelease: {e}\n')
        finally:
            self.tp_clientes_registro_check_campos_obrigatorios()
            self.tp_clientes_registro_entry_limite_keyrelease_block = False        

    def tp_clientes_registro_check_campos_obrigatorios(self):
        items = (self.tp_clientes_registro_nome_validado, self.tp_clientes_registro_cpf_validado, self.tp_clientes_registro_whatsapp_validado, self.tp_clientes_registro_email_validado, self.tp_clientes_registro_endereco_validado, self.tp_clientes_registro_datanascimento_validado, self.tp_clientes_registro_limite_validado) 
        for item in items:
            if item == False:
                self.tp_clientes_registro_button.configure(state='disabled')
                self.tp_clientes_registro_button.configure(fg_color='gray')
                return
        self.tp_clientes_registro_button.configure(state='normal')
        self.tp_clientes_registro_button.configure(fg_color='blue')

    def tp_clientes_registro_registrar_cliente(self):
        #get os dados
        nome = self.tp_clientes_registro_entry_nome.get()
        cpf = self.tp_clientes_registro_entry_cpf.get().replace('.', '').replace('-', '')
        whatsapp = self.tp_clientes_registro_entry_whatsapp.get()
        email = self.tp_clientes_registro_entry_email.get()
        email = email if email else None
        sexo = self.tp_clientes_registro_genero_var.get()
        endereco = self.tp_clientes_registro_entry_endereco.get()
        data_nascimento = self.tp_clientes_registro_entry_datanascimento.get()
        limite = self.tp_clientes_registro_entry_limite.get().replace(',', '.')

        row = (nome, cpf, whatsapp, email,  sexo,  endereco, data_nascimento, limite, dt.now().strftime('%Y-%m-%d %H:%M:%S'), dt.now().strftime('%Y-%m-%d %H:%M:%S'))

        #chamar database function
        cfm = database.insert_new_client(row)
        if cfm:
            self.fechar_tp_clientes_registro()
            msg = CTkMessagebox(self.tp_clientes, message=f"Cliente registrado com sucesso!", icon='check', title='Sucesso')
            self.tp_clientes.wait_window(msg)
            #atualizar a treeview clientes
            self.tp_clientes_treeview_update()
        else:
            CTkMessagebox(self.tp_clientes_registro, message=f'Não foi possível registrar o cliente.', icon='cancel', title='Erro')
    
    def tp_clientes_registro_editar_cliente(self, cliente_id):
        #get os dados
        nome = self.tp_clientes_registro_entry_nome.get()
        cpf = self.tp_clientes_registro_entry_cpf.get().replace('.', '').replace('-', '')
        whatsapp = self.tp_clientes_registro_entry_whatsapp.get()
        email = self.tp_clientes_registro_entry_email.get()
        email = email if email else None
        sexo = self.tp_clientes_registro_genero_var.get()
        endereco = self.tp_clientes_registro_entry_endereco.get()
        data_nascimento = self.tp_clientes_registro_entry_datanascimento.get()
        limite = self.tp_clientes_registro_entry_limite.get().replace(',', '.')

        row = (nome, cpf, whatsapp, email,  sexo, endereco, data_nascimento, limite, dt.now().strftime('%Y-%m-%d %H:%M:%S'), dt.now().strftime('%Y-%m-%d %H:%M:%S'), cliente_id)

       # if limite != database.get_limite_do_cliente(str(cliente_id))[0]:
            #key = self.abrir_tp_password(self.tp_clientes_registro)
            #if not self.tp_password_feedback:
                #return

        #chamar database function
        cfm = database.update_client(row)
        if cfm:
            self.fechar_tp_clientes_registro()
            msg = CTkMessagebox(self.tp_clientes, message=f"Dados do cliente atualizados com sucesso!", icon='check', title='Sucesso')
            self.tp_clientes.wait_window(msg)
            #atualizar a treeview clientes
            self.tp_clientes_treeview_update()
        else:
            CTkMessagebox(self.tp_clientes_registro, message=f'Não foi possível registrar o cliente.', icon='cancel', title='Erro')

    def buscar_conta_cliente(self, event=None):
        try:
            if not self.clientes_treeview.selection(): #trata o caso de o usuario nao identificar o cliente que gostaria de editar os dados
                msg = CTkMessagebox(self.tp_clientes, message=f'Selecione um cliente antes de utilizar essa função.', icon='warning', title='Atenção')
                self.tp_clientes.wait_window(msg)
                return
            self.reset_root()
            selected_item = self.clientes_treeview.focus()
            item_values = self.clientes_treeview.item(selected_item, "values")
            on_credit_data = database.get_all_data_from_customer_by_id(item_values[0])
            self.tp_idv_label_title.configure(text=f'Buscando...')  
            self.root.update()
            if not on_credit_data:
                msg = CTkMessagebox(self.root, message=f'Nenhum dado encontrado para o(a) cliente: {item_values[1]}', icon='warning', title='Atenção')
                self.tp_idv_label_title.configure(text=f' {NOME_TITULO} {self.version}  ')     
                return
            
            self.fechar_tp_clientes()

            #cria a lista com os oncredit_id
            self.oncredit_ids = []

            #lançãndo na treeview do IDV e somando
            for i, item in enumerate(on_credit_data): #percorre a lista de items das compras feitas pelo cliente
                self.oncredit_ids.append(item[0])
                item = tuple(ast.literal_eval(item[2]))
                quantidade = item[-1]
                produto = item[:-1]
                print(quantidade, produto)
                self.inserir_item_na_compra(produto, quantidade)
            
            #capturando o total da compra
            limite_consumido = helper.format_to_float(self.tp_idv_frame_status_subtotal_label_1.cget('text'))

            #configura o idv para o modo conta cliente
            self.set_idv_conta_cliente_modo(item_values[1], item_values[0], limite_consumido)

        except Exception as e:
            print(e)
            self.reset_root()

    def set_idv_conta_cliente_modo(self, cliente_nome, cliente_id, limite_consumido):
        if len(cliente_nome) > 18:
            cliente_nome = cliente_nome[:17]
       
        #modificando o titlo do IDV
        self.tp_idv_label_title.configure(text=f'Conta: {cliente_nome}')
        
        #adicionando o labels do limite disponivel
        limite_disponivel = database.get_limite_disponivel_do_cliente(cliente_id, limite_consumido)

        self.tp_idv_limite_disponivel.place(relx=0.4, rely=0.1675)
        self.tp_idv_limite_disponivel_1.place(relx=0.525, rely=0.155)
        self.tp_idv_limite_disponivel_1.configure(text=helper.format_to_moeda(limite_disponivel))
        
        #informando ao sistema o id do cliente para o momento de finalização da compra (remover as compras da tabela on_credit)
        self.customer_id = cliente_id

        self.set_idv_conta_cliente = True

    def fechar_tp_clientes_registro(self):
        self.tp_clientes_registro.destroy()
        selected_item = self.clientes_treeview.selection()
        self.clientes_treeview.selection_remove(selected_item)


    def fechar_tp_clientes(self, event=None):
        if self.tp_clientes:
            self.tp_clientes.destroy()
            self.tp_clientes = None

    # endregion







    