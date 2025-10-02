import urllib.request
import ssl
import json
import traceback
from datetime import datetime
import helper

def get_product_data_from_cosmos_by_ean(code):
    try:
        # Desabilitar a verificação SSL (não recomendado para produção)
        context = ssl._create_unverified_context()

        headers = {
            'X-Cosmos-Token': 'e1mku8LWz5Atp9KfuouG6A',
            'Content-Type': 'application/json',
            'User-Agent': 'Cosmos-API-Request'
        }

        url = f'https://api.cosmos.bluesoft.com.br/gtins/{code}.json'
        req = urllib.request.Request(url, headers=headers)
        
        # Use o contexto SSL não verificado
        with urllib.request.urlopen(req, context=context) as response:
            status_code = response.status
            if status_code == 200:
                data = json.loads(response.read().decode())
            else:
                raise Exception(f'Erro: erro do código: {status_code}')

        # Exibir o JSON formatado
            print(data)
            desc = data["description"]
            return desc
    except Exception as e:
        print(f'Erro inesperado capturado: {e}')
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open("txts/errors.txt", "a") as log_file:
            log_file.write(f"{current_time} -  {str(e)}\n")
            log_file.write(traceback.format_exc())
            log_file.write("\n---\n")
        return False
