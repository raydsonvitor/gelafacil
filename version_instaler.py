import database, app

MODIFICACAO_VERSAO = '1.0'

try:
    cfm = database.recriar_products_table()
    if not cfm:
        raise Exception
    
    app.alerta_popup(f'Alterações decorrentes da nova versão {MODIFICACAO_VERSAO} realizadas com sucesso.', icone=0x40)

except Exception as e:
    app.alerta_popup(f'Erro na hora de realizar a alterações decorrentes da versão {MODIFICACAO_VERSAO}.')