    

    def handle_delete_row_from_treeview(self):
        # Verifica se a Treeview não está vazia
        if self.tp_idv_treeview.get_children():
            self.tp_idv_treeview.bind('<Escape>', lambda event: self.cancel_handle_delete_row_from_treeview())
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
            CTkMessagebox(self.root, message=f'Nenhum item foi adicionado à compra.', icon='warning', title='Atenção')

    

    def cancel_handle_delete_row_from_treeview(self):
        selected_item = self.tp_idv_treeview.selection()
        self.tp_idv_treeview.selection_remove(selected_item)
        #reabilitar e foca o codbar entry
        self.tp_idv_entry_codbar.configure(state='normal')
        self.root.after(100, self.tp_idv_entry_codbar.focus_set)
        #reescrever o status label
        self.tp_idv_frame_status_label.configure(text='Aguardando código de barras...')

    def remove_item_selecionado(self):
        selected_item = self.tp_idv_treeview.selection()
        item_values = self.tp_idv_treeview.item(selected_item)['values']
        if selected_item:
            yon_0 = self.get_yes_or_not(self.root, f'Confirmar exclusão do item: {item_values[1]}')
            if yon_0:
                self.subtrair_do_subtotal(item_values[-1])
                self.tp_idv_treeview.delete(selected_item)#deleta da treeview
                removed_item_id = self.lista_product_ids.pop(int(item_values[0])-1)#deleta da lista de products_ids
                print(f'Item excluido da treeview: {selected_item}, product_id:{removed_item_id}')
                #atualiza o valor unit
                self.update_valor_unit_label()
                #aproveita a funcao abaixo para reverter os efeitos do f'sistema remover item da lista de compras
                self.cancel_handle_delete_row_from_treeview()            
        else:
            CTkMessagebox(self.root, message=f'Nenhum item selecionado para exclusão', icon='warning', title='Atenção')
            #aproveita a funcao abaixo para reverter os efeitos do f'sistema remover item da lista de compras
            self.cancel_handle_delete_row_from_treeview()  

    def subtrair_do_subtotal(self, valor):
        self.new_subtotal = helper.format_to_float(self.current_subtotal) - helper.format_to_float(valor)
        if abs(self.new_subtotal) < 1e-10:
            self.new_subtotal = 0.0
        self.tp_idv_frame_status_subtotal_label_1.configure(text=helper.format_to_moeda(self.new_subtotal))
        self.current_subtotal = self.new_subtotal

    def somar_ao_subtotal(self, valor):
        self.new_subtotal = helper.format_to_float(self.current_subtotal) + helper.format_to_float(valor)
        if abs(self.new_subtotal) < 1e-10:
            self.new_subtotal = 0.0
        self.tp_idv_frame_status_subtotal_label_1.configure(text=helper.format_to_moeda(self.new_subtotal))
        self.current_subtotal = self.new_subtotal

    def get_treeview_itens_number(self):
        items_len = len(self.tp_idv_treeview.get_children())    
        return items_len

    def update_valor_unit_label(self):
        print(self.get_treeview_itens_number())
        if self.get_treeview_itens_number() > 0:
            last_item = self.tp_idv_treeview.get_children()[-1]
            last_unit_value = self.tp_idv_treeview.item(last_item)['values'][-3]
            self.tp_idv_frame_status_preco_unitario_label_1.configure(text=helper.format_to_moeda(last_unit_value))
        else:
            self.tp_idv_frame_status_preco_unitario_label_1.configure(text=helper.format_to_moeda(0))

    def finalizar_compra(self):  
        #verifica se a treeview esta vazia
        if self.get_treeview_itens_number() == 0:
            msg = CTkMessagebox(self.root, message=f'Nenhum item foi adicionado à compra.', icon='warning', title='Atenção')
            self.root.wait_window(msg)
            self.tp_idv_entry_codbar.focus_set()
            return   
        x = self.abrir_tp_1_0()

    # TOPLEVEL 1    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   JANELA SELECIONAR FORMA DE PAGAMENTO 

    def abrir_tp_1_0(self):
        self.tp_idv_frame_status_label.configure(text='Finalizando Compra...')
        self.tp_idv_1 = CTkToplevel(self.root)
        self.tp_idv_1.title('Selecionar Forma de Pagamento')
        self.tp_idv_1.protocol('WM_DELETE_WINDOW', self.fechar_tp_1)
        self.tp_idv_1_width = 500
        self.tp_idv_1_height = 300
        self.tp_idv_1_x = self.root.winfo_width()//2 - self.tp_idv_1_width//2   #essa e algumas abaixo, sao linhas que centralizam o tp na root
        self.tp_idv_1_y = self.root.winfo_height()//2 - self.tp_idv_1_height//2
        self.tp_idv_1.geometry(f'{self.tp_idv_1_width}x{self.tp_idv_1_height}+{self.tp_idv_1_x}+{self.tp_idv_1_y}')
        self.tp_idv_1.resizable(False, False)
        self.tp_idv_1.attributes('-topmost', 'true')
        self.tp_idv_1_fonte_padrao_bold = CTkFont('arial', 20, 'bold')
        self.tp_idv_1_fonte_padrao = CTkFont('arial', 30)
        self.tp_idv_1.grab_set()

        self.total_restante = helper.format_to_float(self.tp_idv_frame_status_subtotal_label_1.cget('text'))
        self.payments = []
        self.troco = 0

        #widgets config
        
        self.tp_idv_1_label_titlo_seg_button = CTkLabel(self.tp_idv_1, text='Forma de Pagamento:', font=self.tp_idv_1_fonte_padrao_bold)
        self.tp_idv_1_label_titlo_seg_button.place(relx = 0.5, rely=0.05, anchor='n')

        self.formas_pgmt_ativas_cap = tuple(form_pgmt.capitalize() for form_pgmt in self.formas_pgmt_ativas)
        self.tp_idv_1_form_pgmt_seg_button =CTkSegmentedButton(self.tp_idv_1, values=self.formas_pgmt_ativas_cap, font=self.tp_idv_1_fonte_padrao, text_color='black', fg_color='white', unselected_color='white', unselected_hover_color='white', selected_color='green', selected_hover_color='green')
        self.tp_idv_1_form_pgmt_seg_button.place(relx=0.5, rely=0.2, anchor='n')
        self.tp_idv_1_form_pgmt_seg_button.set(self.formas_pgmt_ativas_cap[0])

        self.tp_idv_1_valor_entry = CTkEntry(self.tp_idv_1, font=CTkFont('courier', 50, 'bold'), width=250)
        self.tp_idv_1_valor_entry.place(relx=0.5, rely=0.5, anchor='n')
        self.tp_idv_1_valor_entry_sinalizer = CTkLabel(self.tp_idv_1, text_color='red', text='Insira um valor válido')

        self.tp_idv_1_valor_restante_titlo = CTkLabel(self.tp_idv_1, text='TOTAL: ', font=self.tp_idv_1_fonte_padrao_bold)
        self.tp_idv_1_valor_restante_titlo.place(relx=0.25, rely=0.85, anchor='n')
        self.tp_idv_1_valor_restante = CTkLabel(self.tp_idv_1, font=CTkFont('courier', 50, 'bold'), text=helper.format_to_moeda(self.total_restante))
        self.tp_idv_1_valor_restante.place(relx=0.55, rely=0.8, anchor='n')

        #ajuste de foco ao abrir
        self.tp_idv_1.after(100, self.tp_idv_1_valor_entry.focus_set)

        #block de entrada de dados
        self.root.bind('<Return>', lambda event: self.return_holder())
        self.tp_idv_entry_codbar.configure(state='disabled')

        #vinculação de teclas
        self.tp_idv_1.bind('<Escape>', lambda event: self.cancelar_finalizacao_compra(self.tp_idv_1))
        self.tp_idv_1.bind('<Return>', lambda event: self.validate_tp_1_0())
        self.tp_idv_1.bind('<Right>', lambda event: self.move_to_next_form_pgmt())
        self.tp_idv_1.bind('<Left>', lambda event: self.move_to_previous_form_pgmt())

    def return_holder(self):
        print('Return segurado.')

    def validate_tp_1_0(self):#forms pgmt
        self.tp_idv_1_valor_entry_sinalizer.place_forget()
        self.selected_form_pgmt = self.tp_idv_1_form_pgmt_seg_button.get()
        self.valor_inserido = self.tp_idv_1_valor_entry.get().strip().replace(',', '.').replace('-', '')
        self.abrir_gaveta_check = False
        try:
            self.valor_inserido = float(self.valor_inserido)
            if self.selected_form_pgmt == 'Dinheiro':
                if self.valor_inserido < self.total_restante:
                    msg = CTkMessagebox(self.root, message=f'Se houver mais de uma forma de pagamento, deixe a em DINHEIRO por último.', icon='warning', title='Atenção')
                    self.tp_idv_1.wait_window(msg)
                    self.tp_idv_1_valor_entry.focus_set()
                    return
            else:
                if self.valor_inserido > self.total_restante:
                    self.valor_inserido = self.total_restante
            yon_0 = self.get_yes_or_not(self.tp_idv_1, f'Confirmar Operação? {helper.format_to_moeda(self.valor_inserido)} no {self.selected_form_pgmt}.')
            if yon_0:
                self.troco = 0
                if 'Dinheiro' == self.selected_form_pgmt:#calculador do troco
                    self.troco = self.valor_inserido - self.total_restante
                    self.abrir_gaveta_check = True
                self.payments.append({'method': self.selected_form_pgmt, 'amount': helper.format_to_float(self.valor_inserido - self.troco), 'valor_pago': self.valor_inserido, 'troco': self.troco}) 
                if helper.format_to_float(self.total_restante) - self.valor_inserido  <= float(0): #para de uma forma de pagamento
                    self.fechar_tp_1()
                    print('fechei o tp_1')
                    self.abrir_tp_2()#tp_2 == tp_cpf
                else: #para o caso de mais de uma forma de pagamento \ recalculo do valor restante
                    self.tp_idv_1_valor_restante_titlo.configure(text='Restante:')
                    self.total_restante = helper.format_to_float(self.total_restante) - float(self.valor_inserido)
                    self.tp_idv_1_valor_restante.configure(text=helper.format_to_moeda(self.total_restante))
                    self.tp_idv_1_valor_entry.delete(0, END)
                    self.tp_idv_1_valor_entry.focus_set()
            else:
                return
        except Exception as e:#para o caso de valor inválido
            self.tp_idv_1_valor_entry_sinalizer.place(relx=0.5, rely=0.725, anchor='n')
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

    def fechar_tp_1(self):
        if self.tp_idv_1:
            self.tp_idv_1.destroy()
            self.tp_idv_1 = None
            self.tp_idv_entry_codbar.configure(state='normal')  

    # TOPLEVEL 2    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>   JANELA INSERIR CPF

    def abrir_tp_2(self):
        x = self.get_treeview_data()
        print(x)
        #janela toplevel para cadastro de produtos
        self.tp_idv_2 = CTkToplevel(self.root)
        self.tp_idv_2.title('Inserir CPF')
        self.tp_idv_2.protocol('WM_DELETE_WINDOW', self.fechar_tp_1)
        self.tp_idv_2_width = 350
        self.tp_idv_2_height = 250
        self.tp_idv_2_x = self.root.winfo_width()//2 - self.tp_idv_2_width//2   #essa e algumas abaixo, sao linhas que centralizam o tp na root
        self.tp_idv_2_y = self.root.winfo_height()//2 - self.tp_idv_2_height//2
        self.tp_idv_2.geometry(f'{self.tp_idv_2_width}x{self.tp_idv_2_height}+{self.tp_idv_2_x}+{self.tp_idv_2_y}')
        self.tp_idv_2.resizable(False, False)
        self.tp_idv_2.attributes('-topmost', 'true')
        self.tp_idv_2_fonte_padrao_bold = CTkFont('arial', 20, 'bold')
        self.tp_idv_2_fonte_padrao = CTkFont('arial', 30)
        self.tp_idv_2.grab_set()

        self.tp_idv_2_titlo = CTkLabel(self.tp_idv_2, text='Inserir CPF', font=self.tp_idv_2_fonte_padrao_bold)
        self.tp_idv_2_titlo.place(relx=0.5,rely=0.1, anchor='n')

        self.tp_idv_2_entry = CTkEntry(self.tp_idv_2, font=self.tp_idv_2_fonte_padrao, width=250)
        self.tp_idv_2_entry.place(relx=0.5,rely=0.3, anchor='n')
        self.tp_idv_2_entry_sinalizer = CTkLabel(self.tp_idv_2, text='CPF inválido', text_color='red')

        self.tp_idv_2_troco_restante_titlo = CTkLabel(self.tp_idv_2, text='TROCO:', font=self.tp_idv_1_fonte_padrao_bold)
        self.tp_idv_2_troco_restante_titlo.place(relx=0.2, rely=0.75, anchor='n')
        self.tp_idv_2_troco_restante = CTkLabel(self.tp_idv_2, font=CTkFont('courier', 50, 'bold'), text=helper.format_to_moeda(self.troco))
        self.tp_idv_2_troco_restante.place(relx=0.6, rely=0.7, anchor='n')

        self.tp_idv_2.after(10, self.tp_idv_2_entry.focus_set)

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
            yon = self.get_yes_or_not(self.tp_idv_2, 'Finalizar a compra sem CPF?')
            if yon:
                self.encerrar_finzalização_da_compra()

    def encerrar_finzalização_da_compra(self):
        try:
            items = self.get_treeview_data()#agrupando os dados
            total = self.tp_idv_frame_status_subtotal_label_1.cget('text')
            if self.customer_id:
                key = self.abrir_tp_password(self.tp_8)
                if self.tp_password_feedback:
                    cfm = database.delete_oncredits_by_customer_id_and_insert_sale_into_tables(self.customer_id, items, self.payments, self.troco)
                    if cfm:
                        CTkMessagebox(self.root, message=f"Os valores foram descontados da conta do cliente de id: {self.cliente_selecionado}", icon='check', title='')
                        yon = self.get_yes_or_not(self.root, 'Imprimir Cupom fiscal?')
                        if yon:
                            self.imprimir_cupom(items, self.payments, total, self.troco, time.strftime("%d/%m/%Y %H:%M"))
                            self.reset_root()
                        else:
                            self.reset_root()
                        if self.abrir_gaveta_check:
                            self.abrir_gaveta()
                    else:
                        CTkMessagebox(self.root, message='Erro na hora de descontar os valores da conta do cliente e registrar venda. Operação CANCELADA.', icon='cancel', title='Erro')
                else:
                    print('Senha nao aceita. operacao descontinuada.')
            else:
                yon = self.get_yes_or_not(self.root, 'Imprimir Cupom fiscal?')
                if yon:
                    feedback = database.insert_sale_into_tables(items, self.payments, self.troco)#lancar no database
                    if not feedback:
                        raise Exception('Erro ao inserir venda no database')
                    self.imprimir_cupom(items, self.payments, total, self.troco, time.strftime("%d/%m/%Y %H:%M"))
                    self.reset_root()
                else:
                    feedback = database.insert_sale_into_tables(items, self.payments, self.troco)#lancar no database
                    if not feedback:
                        raise Exception('Erro ao inserir venda no database')
                    self.reset_root()
                if self.abrir_gaveta_check:
                        self.abrir_gaveta()

        except Exception as e:
            print(e)
            CTkMessagebox(self.root, message=f'Erro na hora de finalizar compra: contate: {self.contato} ou reinicie o PDV.', icon='cancel', title='Erro')

    def reset_root(self):
        self.tp_idv_frame_status_label.configure(text='Aguardando Código de barras...')
        self.tp_idv_frame_status_preco_unitario_label_1.configure(text='0,00')
        self.tp_idv_frame_status_subtotal_label_1.configure(text='0,00')
        self.current_subtotal = helper.format_to_moeda(0) #subtotal atual
        self.limpar_treeview()
        self.tp_idv_2_fechar()  
        self.fechar_tp_1()
        self.tp_idv_entry_codbar.configure(state='normal')
        self.root.after(100, self.tp_idv_entry_codbar.focus_set)
        self.customer_id = 0
        self.tp_password_feedback = False
        self.cliente_selecionado = ''
        self.yon = False
        self.lista_product_ids = []

    def limpar_treeview(self):
        try:
            for i in self.tp_idv_treeview.get_children():
                self.tp_idv_treeview.delete(i)
        except:
            print('Erro na hora de limpar treeview')
            return

    def get_treeview_data(self):
        # Função para extrair os dados da Treeview
        items = []
        for index, child in enumerate(self.tp_idv_treeview.get_children()):#percorrendo a treeview e criando um dict para cada item
            product_id = self.lista_product_ids[index]
            product_name = self.tp_idv_treeview.item(child, 'values')[1].lower()  # nome do item  
            quantity = helper.format_to_float(self.tp_idv_treeview.item(child, 'values')[3])  # Quantidade
            price = helper.format_to_float(self.tp_idv_treeview.item(child, 'values')[2])  # Preço unitário
            item_id = self.tp_idv_treeview.item(child, 'values')[0]
            
            items.append({
                'product_id': product_id,
                'item_id': item_id,
                'product_name': product_name,
                'quantity': quantity,
                'price': price
            })
        return items


    def tp_idv_2_fechar(self):
        if self.tp_idv_2:
            self.tp_idv_2.destroy()
            self.tp_idv_2 = None