import sqlite3
from datetime import datetime, timedelta, time
import helper
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt


def create_connection():
    connection = sqlite3.connect('gelafacil.db')
    return connection

# region Módulo IDV

def get_product_by_coluna(termo, coluna):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        # Executa uma consulta para procurar o produto pelo código de barras
        cursor.execute(f'SELECT * FROM products WHERE {coluna}=?', (termo,))
        return cursor.fetchone()
    except Exception as e:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('txts/errors.txt', 'a') as a:
            a.write(f'{current_time} - backend.py - modulo idv - get_product_by_coluna: {e}\n')
    finally:
        conn.close()

def insert_sale_into_tables(items, payments, troco, desconto):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        # Calcular o total da venda
        total_amount = 0
        forma_pgmts = []
        for item in items:
            print(item['quantity'], item['price'])
            total_amount += item['quantity'] * item['price']
        total_amount = total_amount - desconto
        # resumir as formas de pgmt
        for payment in payments:
            forma_pgmts.append(payment['method'])
        forma_pgmts = ' + '.join(forma_pgmts)
        # 1. Inserir a venda na tabela `sales`
        sale_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            INSERT INTO sales (sale_date, total_amount, troco, desconto, pagamento_modo)
            VALUES (?, ?, ?, ?, ?)
        ''', (sale_date, total_amount, troco, desconto, forma_pgmts))
        
        sale_id = cursor.lastrowid

        # 2. Inserir os itens na tabela `sales_items`
        for item in items:
            cursor.execute('''
                INSERT INTO sales_items (sale_id, product_id, quantity, price)
                VALUES (?, ?, ?, ?)
            ''', (sale_id, item['product_id'], item['quantity'], item['price']))

        # 3. Inserir as formas de pagamento na tabela `payment_methods`
        for payment in payments:
            cursor.execute('''
                INSERT INTO payment_methods (sale_id, method, amount)
                VALUES (?, ?, ?)
            ''', (sale_id, payment['method'], payment['amount']))

        conn.commit()
        print("Venda registrada com sucesso!")
        return True

    except sqlite3.Error as e:
        print(f"Erro ao registrar a venda: {e}")
        conn.rollback()
    
    finally:
        conn.close()
    return False

def delete_oncredits_by_customer_id_and_insert_sale_into_tables(customer_id, items, payments, troco, desconto):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        date = helper.get_date()
        cursor.execute(f'''
            DELETE FROM on_credit WHERE cliente_id = '{customer_id}';
            ''')
        with open('txts/historic_oncredits_deleted.txt', 'a') as a:
            a.write(f'{date}_{customer_id} = {items}\n')

        ##insert_sale_into_tables    
        # Calcular o total da venda
        total_amount = 0
        forma_pgmts = []
        for item in items:
            total_amount += item['quantity'] * item['price']
        # resumir as formas de pgmt
        for payment in payments:
            forma_pgmts.append(payment['method'])
        forma_pgmts = ' + '.join(forma_pgmts)
        # 1. Inserir a venda na tabela `sales`
        sale_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
            INSERT INTO sales (sale_date, total_amount, troco, desconto, pagamento_modo)
            VALUES (?, ?, ?, ?, ?)
        ''', (sale_date, total_amount, troco, desconto, forma_pgmts))
        
        sale_id = cursor.lastrowid

        # 2. Inserir os itens na tabela `sales_items`
        for item in items:
            cursor.execute('''
                INSERT INTO sales_items (sale_id, product_id, quantity, price)
                VALUES (?, ?, ?, ?)
            ''', (sale_id, item['product_id'], item['quantity'], item['price']))

        # 3. Inserir as formas de pagamento na tabela `payment_methods`
        for payment in payments:
            cursor.execute('''
                INSERT INTO payment_methods (sale_id, method, amount)
                VALUES (?, ?, ?)
            ''', (sale_id, payment['method'], payment['amount']))

        conn.commit()
        print("Venda registrada com sucesso!")
        return True

    except sqlite3.OperationalError as e:
        print(f"Erro operacional na hora de deletar os valores do clinte de id {customer_id}: {e}")
        return False
    finally:
        conn.close()

#endregion

# region Módulo CDM

def insert_product(row):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO products (barcode, descricao, categoria, marca, precocompra, precovenda, estoque, fornecedor, status, dataregistro, dataultimaalteracao)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]))
        conn.commit()
        return True
    except Exception as e:
        return f'Erro na hora de registrar a mercadoria no banco de dados: {e}'
    finally:
        conn.close()  

# endregion

# region Módulo GDM

def get_all_products():
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM products LIMIT 30")  # Obtenha todos os produtos ou a consulta que você precisa
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        conn.rollback()
        print(f"Erro buscar todos os produtos: {e}")
        return False
    finally:
        conn.close()

def search_products(search_term, search_by):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT * FROM products WHERE {search_by} LIKE ? LIMIT 30", ('%' + search_term + '%',))
        results = cursor.fetchall()
        return results
    except sqlite3.Error as e:
        print(f"Erro ao procurar produtos: {e}")
    finally:
        conn.close()

def update_product(row):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        UPDATE products
        SET barcode = ?, descricao=?, categoria=?, marca=?, precocompra = ?, precovenda = ?, estoque = ?, fornecedor = ?, status=?, dataultimaalteracao= ?
        WHERE id = ?
    ''', row)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Erro ao atualizar o produto: {e}")
        return False
    finally:
        conn.close()

def delete_product_by_id(id):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f'''
                DELETE FROM products WHERE id = '{id}';
                ''')
        conn.commit()
        return True
    except Exception as e:
        print('Erro na hora de excluir o product no database.')
        print(e)
        conn.rollback()

#endregion

# region Módulo GDV

def get_all_sales_by_month(ano, mes):
    try:
        # Definir mes (com o ano) em questão
        mes_formatado = f"{ano:04d}-{mes:02d}"  # Garante o formato 'YYYY-MM'

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM sales WHERE strftime('%Y-%m', sale_date) = '{mes_formatado}'"
)
        return cursor.fetchall()
    except Exception as e:
        print(f'Erro na hora obter todas as vendas {e}')
        return False
    finally:
        conn.close()

def get_all_sales_from_base_day(base_day):
    try:
        hora_base = '06:00:00'
        dia_base = base_day
        # Definindo o inicio e fim da filtro de vendas
        inicio = f"{dia_base} {hora_base}"  # Garante o formato 'YYYY-MM'
        dia_seguinte = (datetime.strptime(dia_base, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
        fim = f'{dia_seguinte} {hora_base}'
        conn = create_connection()
        cursor = conn.cursor()
        # Executa uma consulta para procurar o produto pelo código de barras
        cursor.execute(f"SELECT * FROM sales WHERE sale_date >= '{inicio}' AND sale_date < '{fim}'")
        return cursor.fetchall()
    
    
    except Exception as e:
        print(f'Erro na hora obter todas as vendas {e}')
        return False
    finally:
        conn.close()

def get_sales_items_by_sale_id(id):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM sales_items WHERE sale_id = '{id}';"
)
        return cursor.fetchall()
    except Exception as e:
        print(f'Erro na hora obter os sales_items pelo sale_id: database.py - get_sales_items_by_sale_id: {e}')
        return False
    finally:
        conn.close()


from datetime import datetime, time
import pandas as pd
from sklearn.linear_model import LinearRegression

def get_previsao_faturamento_dia():
    conn = create_connection()
    query = 'SELECT sale_date, total_amount FROM sales'
    df = pd.read_sql(query, conn)

    if df.empty:
        print("Sem dados de vendas para realizar a previsão.")
        return 0.0

    df['sale_date'] = pd.to_datetime(df['sale_date'])

    df['data_comercial'] = df['sale_date'].apply(
        lambda dt: (dt - pd.Timedelta(days=1)).date() if dt.hour < 6 else dt.date()
    )

    df_diario = df.groupby('data_comercial')['total_amount'].sum().reset_index().copy()

    df_diario['data_comercial'] = pd.to_datetime(df_diario['data_comercial'])
    df_diario['dias'] = (df_diario['data_comercial'] - df_diario['data_comercial'].min()).dt.days

    agora = datetime.now()
    if agora.time() < time(6, 0):
        dia_atual_comercial = (agora - pd.Timedelta(days=1)).date()
    else:
        dia_atual_comercial = agora.date()

    df_diario_filtrado = df_diario[df_diario['data_comercial'] < pd.to_datetime(dia_atual_comercial)].copy()

    if df_diario_filtrado.empty:
        print("Sem dados históricos suficientes para realizar a previsão.")
        return 0.0

    df_diario_filtrado['dia_semana'] = df_diario_filtrado['data_comercial'].dt.weekday

    X = df_diario_filtrado[['dias', 'dia_semana']]
    y = df_diario_filtrado['total_amount']

    if len(X) < 1:
        print("Dados insuficientes para treinar o modelo.")
        return 0.0

    modelo = LinearRegression()
    modelo.fit(X, y)

    dias_hoje = (pd.to_datetime(dia_atual_comercial) - df_diario_filtrado['data_comercial'].min()).days
    dia_semana_hoje = pd.to_datetime(dia_atual_comercial).weekday()

    previsao_hoje = modelo.predict([[dias_hoje, dia_semana_hoje]])

    return previsao_hoje[0]

    #print(f"📈 Previsão para hoje ({dia_atual_comercial}): R$ {previsao_hoje[0]:.2f}")

    # Plotando o gráfico
    #plt.figure(figsize=(10, 5))
    #plt.plot(df_diario_filtrado['data_comercial'], df_diario_filtrado['total_amount'], label='Faturamento real', marker='o')
    #plt.plot(df_diario_filtrado['data_comercial'], df_diario_filtrado['previsao'], label='Regressão Linear', linestyle='--')
    #plt.legend()
    #plt.xlabel('Data')
    #plt.ylabel('Faturamento (R$)')
    #plt.title('Faturamento Diário com Regressão Linear')
    #plt.grid(True)
    #plt.show()

    # Exibindo o dataframe com as previsões
    #print(df_diario_filtrado)

def get_previsao_faturamento_mes():
    # Coletando os dados do banco de dados
    conn = create_connection()
    query = 'SELECT sale_date, total_amount FROM sales'
    df = pd.read_sql(query, conn)

    # Convertendo as datas
    df['sale_date'] = pd.to_datetime(df['sale_date'])

    # Ajustando para "dia comercial" que começa às 6h da manhã
    df['data_comercial'] = df['sale_date'].apply(
        lambda dt: (dt - pd.Timedelta(days=1)).date() if dt.hour < 6 else dt.date()
    )

    # Agrupando pela data comercial e somando o valor total
    df = df.groupby('data_comercial')['total_amount'].sum().reset_index()
    df['data_comercial'] = pd.to_datetime(df['data_comercial'])

    # Agrupando por mês
    df['mes_comercial'] = df['data_comercial'].dt.to_period('M')
    df = df.groupby('mes_comercial')['total_amount'].sum().reset_index()

    # Removendo o primeiro e o último mês
    primeiro_mes = df['mes_comercial'].min()
    ultimo_mes = df['mes_comercial'].max()
    df = df[(df['mes_comercial'] > primeiro_mes) & (df['mes_comercial'] < ultimo_mes)].copy()

    # Transformando os meses para int (ex: 202405)
    df['mes_comercial'] = df['mes_comercial'].astype(str).str.replace('-', '').astype(int)

    # Treinando o modelo
    X = df[['mes_comercial']].values
    y = df['total_amount'].values

    if len(X) < 1:
        print("Dados insuficientes para treinar o modelo.")
        return 0.0

    modelo = LinearRegression()
    modelo.fit(X, y)

    # Prevendo o mês atual
    mes_para_prever = int(str(ultimo_mes).replace('-', ''))
    X_novo = [[mes_para_prever]]
    previsao = modelo.predict(X_novo)[0]

    # Exibindo no formato brasileiro
    print(f"Previsão de faturamento para {ultimo_mes}: R$ {previsao:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    return previsao


#endregion

# region Módulo Clientes

def create_table_clients():
    conn = create_connection()
    if not conn:
        print('Erro ao conectar com o database')
        return
    cursor = conn.cursor()
    try:
        cursor.execute('''
            CREATE TABLE "clientes" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf TEXT UNIQUE,
            whatsapp TEXT,
            endereco TEXT,
            email TEXT UNIQUE,
            genero TEXT,
            datanascimento TEXT, 
            dataregistro TEXT,
            dataultimaalteracao TEXT
    );
                ''')
        conn.commit()
        print('sucesso em criar a tabela: clientes')
        return True

    except Exception as e:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('txts/errors.txt', 'a') as a:
            a.write(f'{current_time} - backend.py - create_table_clients: {e}\n')
        return False
    finally:
        conn.close()

def get_clientes_by_coluna(coluna, termo):
    conn = create_connection()
    if not conn:
        return
    cursor = conn.cursor()
    try:
        cursor.execute(f'SELECT * FROM clientes WHERE {coluna} LIKE ? LIMIT 30', ('%' + termo + '%',))
        return cursor.fetchall()
    except Exception as e:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('txts/errors.txt', 'a') as a:
            a.write(f'{current_time} - databse.py - get_clientes_by_coluna: {e}\n')
        return False
    finally:
        conn.close()

def insert_new_client(row):
    conn = create_connection()
    if not conn:
        return
    cursor = conn.cursor()
    try:
        cursor.execute('''
                INSERT INTO clientes (nome, cpf, whatsapp, email, genero, endereco, datanascimento, limite_credito, dataregistro, dataultimaalteracao)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', row)
        conn.commit()
        return True
    except Exception as e:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('txts/errors.txt', 'a') as a:
            a.write(f'{current_time} - database.py - insert_new_client: {e}\n')
        conn.rollback()
        return False
    finally:
        conn.close()

def update_client(row):
    conn = create_connection()
    if not conn:
        return
    cursor = conn.cursor()
    try:
        cursor.execute('''
        UPDATE clientes SET nome = ?, cpf=?, whatsapp=?, email=?, genero = ?, endereco = ?, datanascimento = ?, limite_credito = ?, dataregistro=?, dataultimaalteracao= ?
        WHERE id = ?''', row)
        conn.commit()
        return True
    except Exception as e:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open('txts/errors.txt', 'a') as a:
            a.write(f'{current_time} - database.py - update_client: {e}\n')
        conn.rollback()
        return False
    finally:
        conn.close()

def get_all_clientes():
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM clientes LIMIT 30")  # Obtenha todos os clientes ou a consulta que você precisa
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        conn.rollback()
        print(f"Erro ao buscar todos os clientes: {e}")
        return False
    finally:
        conn.close()

def get_cliente_by_id(id):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT * FROM clientes WHERE id = '{id}';")  # Obtenha todos os produtos ou a consulta que você precisa
        row = cursor.fetchone()
        return row
    except Exception as e:
        conn.rollback()
        print(f"Erro ao buscar o cliente pelo id: {e}")
        return False
    finally:
        conn.close()

#endregion

# region Modulo FIAR COMPRA

def create_tabela_oncredit():
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
    CREATE TABLE on_credit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente_id TEXT NOT NULL,
        carrinho TEXT,
        data TEXT
    );''')
        conn.commit()
        print('sucesso')
    except sqlite3.OperationalError as e:
        print(f"Erro operacional: {e}")
    finally:
        conn.close()

def get_clientes():
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT nome FROM clientes;')
        return cursor.fetchall()
    except Exception as e:
        print(f'Erro na hora de obter a lista de clientes registrados: {e}')
        return False
    finally:
        conn.close()

def get_cliente_id_by_name(nome):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        # Executa uma consulta para procurar o produto pelo código de barras
        cursor.execute(f'SELECT id FROM clientes WHERE nome = ?', (nome,))
        return cursor.fetchone()
    except Exception as e:
        print(f'Erro na hora de obter ID do cliente selecionado: {e}')
        return False
    finally:
        conn.close()

def insert_into_oncredit(customer_id, items, data):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO on_credit (cliente_id, carrinho, data)
            VALUES (?, ?, ?)
        ''', (customer_id, items, data))
        conn.commit()
        with open('txts/historic_oncredits.txt', 'a') as a:
            a.write(f'{data}_{customer_id} = {items}\n')
        return True
    except Exception as e:
        print(f"Erro ao registrar a fiação: {e}")
        conn.rollback()
    finally:
        conn.close()

def get_all_data_from_customer_by_id(id):
    try:
        conn = create_connection()
        cursor = conn.cursor()
        # Executa uma consulta para procurar o produto pelo código de barras
        cursor.execute(f'SELECT * FROM on_credit WHERE cliente_id = ?', (id,))
        return cursor.fetchall()
    except Exception as e:
        print(f'Erro na hora de obter ID do cliente selecionado: {e}')
        return False
    finally:
        conn.close()

# endregion

# region Demais funções


def get_product_name_by_id(id):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f'SELECT descricao FROM products WHERE id = ?', (id,))
        row = cursor.fetchone()
        return row
    except sqlite3.Error as e:
        print(f"Erro ao buscar a descricao do produto pelo id: {e}")
        conn.rollback()
    finally:
        conn.close()

def get_payments_by_date(date):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT * FROM payment_methods WHERE sale_id IN (SELECT sale_id FROM sales WHERE DATE(sale_date) = '{date}');")
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        conn.rollback()
        print(f"Erro buscar os pagamentos: {e}")
        return False
    finally:
        conn.close()

def get_payments_by_sale_id(id):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT method, amount FROM payment_methods WHERE sale_id = ?", (id,))
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        conn.rollback()
        print(f"Erro buscar os pagamentos: {e}")
        return False
    finally:
        conn.close()

def get_sangrias_by_date(date_time):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM sangria WHERE datetime(date) > ?", (date_time,))
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        conn.rollback()
        print(f"Erro ao buscar dados de sangrias: {e}")
        return False
    finally:
        conn.close()

def get_supriments_by_date(date_time):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM supriments WHERE datetime(date) > ?", (date_time,))
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        conn.rollback()
        print(f"Erro ao buscar dados de suprimentos: {e}")
        return False
    finally:
        conn.close()

def get_sales_by_date(date_time):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM sales WHERE datetime(sale_date) > ?", (date_time,))
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        conn.rollback()
        print(f"Erro ao buscar dados de vendas (sales): {e}")
        return False
    finally:
        conn.close()

def get_sales_date_troco_by_id(id):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f'SELECT sale_date, troco FROM sales WHERE sale_id = ?', (id,))
        row = cursor.fetchone()
        return row
    except sqlite3.Error as e:
        print(f"Erro ao buscar dados da tabela de vendas: {e}")
        conn.rollback()
    finally:
        conn.close()

def get_sales_items_by_sale_id(id):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f'SELECT product_id, quantity, price FROM sales_items WHERE sale_id = ?', (id,))
        rows = cursor.fetchall()
        return rows
    except sqlite3.Error as e:
        print(f"Erro ao buscar dados da  tabela items da venda: {e}")
        conn.rollback()
    finally:
        conn.close()

def record_customer(name, whats, adress):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
                INSERT INTO customers (name, number, adress)
                VALUES (?, ?, ?)
            ''', (name, whats, adress))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erro ao registrar a venda: {e}")
        conn.rollback()
    finally:
        conn.close()
    return False

def insert_sangria(amount, classe):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
                INSERT INTO sangria (amount, class, date)
                VALUES (?, ?, ?)
            ''', (amount, classe, date))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erro ao registrar a sangria: {e}")
        conn.rollback()
    finally:
        conn.close()
    return False

def insert_supriment(amount):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
                INSERT INTO supriments (amount, date)
                VALUES (?, ?)
            ''', (amount, date))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erro ao registrar o suprimento: {e}")
        conn.rollback()
    finally:
        conn.close()
    return False

def create_tabela_sangrias():
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sangria (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                class TEXT,
                date TEXT NOT NULL);
                ''')
        conn.commit()
        print('sucesso')

    except sqlite3.OperationalError as e:
        print(f"Erro operacional: {e}")
    finally:
        conn.close()

def create_tabela_supriments():
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS supriments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                date TEXT NOT NULL);
                ''')
        conn.commit()
        print('sucesso')
        return True
    except sqlite3.OperationalError as e:
        print(f"Erro operacional: {e}")
    finally:
        conn.close()



def create_tabela_payment_methods():
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payment_methods (
                payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER NOT NULL,
                method TEXT NOT NULL,
                amount REAL NOT NULL,
                troco REAL NOT NULL,
                FOREIGN KEY (sale_id) REFERENCES sales(sale_id));
            ''')
        conn.commit()
        print('sucesso')

    except sqlite3.OperationalError as e:
        print(f"Erro operacional: {e}")
    finally:
        conn.close()

def create_tabela_products():
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT UNIQUE NOT NULL,
                descricao TEXT NOT NULL,
                ncm TEXT NOT NULL,
                ncm_desc TEXT,  
                marca TEXT,
                nome TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER,
                source TEXT,
                data_vencimento TEXT);
            ''')
        conn.commit()
        print('sucesso ao criar tabela')
        insert_product(('0000000000000', 'produto geral', '', '', '', '0', '', '', '', '', ''))
        print('Sucesso ao registrar o produto geral')

    except sqlite3.OperationalError as e:
        print(f"Erro operacional: {e}")
    finally:
        conn.close()
    
def delete_sale_by_id(id):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f'''
                DELETE FROM sales WHERE sale_id = '{id}';
                ''')
        cursor.execute(f'''
                DELETE FROM sales_items WHERE sale_id = '{id}';
                ''')
        cursor.execute(f'''
                DELETE FROM payment_methods WHERE sale_id = '{id}';
                ''')
        conn.commit()
        return True
    except Exception as e:
        print('Erro na hora de excluir a venda no database.')
        print(e)
        conn.rollback()

def delete_sangria_by_id(id):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f'''
                DELETE FROM sangria WHERE id = '{id}';
                ''')
        conn.commit()
        return True
    except Exception as e:
        print('Erro na hora de excluir a sangria no database.')
        print(e)
        conn.rollback()

def delete_suprimento_by_id(id):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f'''
                DELETE FROM supriments WHERE id = '{id}';
                ''')
        conn.commit()
        return True
    except Exception as e:
        print('Erro na hora de excluir o suprimento no database.')
        print(e)
        conn.rollback()

#endregion

# region \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\ ESPECIAL FUNCTIONS \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


def recriar_sales_table():
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f'''
            CREATE TABLE sales_new (
            sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_date TEXT NOT NULL,
            total_amount REAL NOT NULL,
            troco REAL,
            desconto REAL,
            pagamento_modo TEXT
    );
            ''')
        cursor.execute(f'''INSERT INTO sales_new (sale_id, sale_date, total_amount, troco, desconto, pagamento_modo)
            SELECT sale_id, sale_date, total_amount, troco, desconto, pagamento_modo FROM sales;''')
        
        cursor.execute(f'DROP TABLE sales;')

        cursor.execute(f'ALTER TABLE sales_new RENAME TO sales;')

        conn.commit()
        print('sucesso!')
        return True
    except Exception as e:
        print(f"Erro ao recriar a tabela sale_items: {e}")
        conn.rollback()

def recriar_products_table():
    conn = create_connection()
    cursor = conn.cursor()
    try:
        #criar uma nova tabela
        cursor.execute(f'''
            CREATE TABLE products_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT UNIQUE NOT NULL,
                descricao TEXT NOT NULL,
                categoria TEXT NOT NULL,
                marca TEXT,
                precocompra REAL NOT NULL,
                precovenda REAL NOT NULL,
                estoque INTEGER,
                fornecedor TEXT,
                status TEXT NOT NULL,
                dataregistro TEXT,
                dataultimaalteracao TEXT
                       );
            ''')
        #coloca os dados da tabela antiga na novas
        cursor.execute(f'''INSERT INTO products_new (id, barcode, descricao, categoria, marca,  precocompra, precovenda, estoque, fornecedor, status, dataregistro, dataultimaalteracao)
            SELECT id, barcode, descricao, '', '', '0', price, '', '', '', '', ''  FROM products;''')
        #exclui a tabela anterior
        cursor.execute(f'DROP TABLE products;')
        #renomeia a nova tabela com o nome da antiga
        cursor.execute(f'ALTER TABLE products_new RENAME TO products;')
        #salva as modificações no database
        conn.commit()
        print('sucesso!')
        return True
        
    except Exception as e:
        print(f"Erro ao recriar a tabela sale_items: {e}")
        conn.rollback()


def recriar_oncredit_table():
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(f'''
            CREATE TABLE payment_methods_new (
                payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER NOT NULL,
                method TEXT NOT NULL,
                amount REAL NOT NULL
    );
            ''')
        cursor.execute(f'''INSERT INTO payment_methods_new (payment_id, sale_id, method, amount)
            SELECT payment_id, sale_id, method, amount FROM payment_methods;''')
        
        cursor.execute(f'DROP TABLE payment_methods;')

        cursor.execute(f'ALTER TABLE payment_methods_new RENAME TO payment_methods;')

        conn.commit()
        print('sucesso!')
        return True
    except Exception as e:
        print(f"Erro ao recriar a tabela oncredit: {e}")
        conn.rollback()

def recriar_clientes_table():
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            CREATE TABLE "clientes_new" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf TEXT UNIQUE,
            whatsapp TEXT,
            email TEXT UNIQUE,
            genero TEXT,
            endereco TEXT,
            datanascimento TEXT, 
            limite_credito TEXT,
            dataregistro TEXT,
            dataultimaalteracao TEXT
    );
                ''')
        cursor.execute(f'''INSERT INTO clientes_new (id, nome, cpf, whatsapp, email, genero, endereco, datanascimento, limite_credito, dataregistro, dataultimaalteracao)
            SELECT id, nome, cpf, whatsapp, email, genero, endereco, datanascimento, limite_credito, dataregistro, dataultimaalteracao FROM clientes;''')
        
        cursor.execute(f'DROP TABLE clientes;')

        cursor.execute(f'ALTER TABLE clientes_new RENAME TO clientes;')

        conn.commit()
        print('sucesso!')
        return True
    except Exception as e:
        print(f"Erro ao recriar a tabela oncredit: {e}")
        conn.rollback()


def limpar_database():
    conn = create_connection()
    cursor = conn.cursor()

    # Desabilita chave estrangeira temporariamente para evitar problemas na exclusão
    cursor.execute("PRAGMA foreign_keys = OFF;")
    conn.commit()

    # Obtém todas as tabelas do banco, exceto as internas do SQLite
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tabelas = cursor.fetchall()

    for tabela in tabelas:
        nome_tabela = tabela[0]
        print(f"Apagando dados da tabela: {nome_tabela}")
        cursor.execute(f"DELETE FROM {nome_tabela};")
        conn.commit()

    # Reseta a sequência do AUTOINCREMENT
    cursor.execute("DELETE FROM sqlite_sequence;")
    conn.commit()

    # Reabilita chave estrangeira
    cursor.execute("PRAGMA foreign_keys = ON;")
    conn.commit()

    conn.close()
    print("Banco de dados limpo com sucesso, estrutura mantida.")

#endregion
