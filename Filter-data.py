import requests
import json
from datetime import datetime
import PySimpleGUI as sg
import os
from TOKEN import apikey, token

layout = [
    [sg.Text('Data de Início:'), sg.Input(key='-DATA_INICIO-', enable_events=True), sg.CalendarButton('Selecionar', target='-DATA_INICIO-', format='%Y-%m-%d')],
    [sg.Text('  Data Final:   '), sg.Input(key='-DATA_FINAL-', enable_events=True), sg.CalendarButton('Selecionar', target='-DATA_FINAL-', format='%Y-%m-%d')],
    [sg.Text('Onde Salvar? '), sg.Input(key='-PASTA_DESTINO-', enable_events=True), sg.FolderBrowse('Selecionar')],
    [sg.Text('Informações:  '), sg.Output(size=(45, 15))],
    [sg.Button('Baixar'),sg.Text('                                                                                                  '), sg.Button('Sair')]
]
janela = sg.Window('Filtro', layout)
while True:
    eventos, valores = janela.read()
    if eventos == sg.WINDOW_CLOSED or eventos == 'Sair':
        break
    elif eventos == 'Baixar':
        request = requests.get(f"https://api.auvo.com.br/v2/login/?apiKey={apikey}&apiToken={token}")
        certo = json.loads(request.content)
        token = certo['result']['accessToken']
        data_inicio = valores['-DATA_INICIO-']
        data_final = valores['-DATA_FINAL-']
        pasta_destino = valores['-PASTA_DESTINO-']
        data = {
        'startDate': f'{data_inicio}T00:00:00','endDate': f'{data_final}T00:00:00'

        }
        headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
        }

        paramFilter = json.dumps(data)
        page = 1
        pageSize = 100
        order = 'asc'
        selectfields = 'selectfields'
        numero_solicitacao = 0 


        while True: #solicita Lista de IDS
            if page != 100:
                numero_solicitacao = numero_solicitacao + 1
                lista = requests.get(f'https://api.auvo.com.br/v2/tasks/?paramFilter={data}&page={page}&pageSize={pageSize}&order={order}&selectfields={selectfields}?starDate=2023-06-06T00:00:00', headers=headers)
                if numero_solicitacao == 100:
                    break
                page = page + 1 
                if lista.status_code == 200:
                    lista1 = json.loads(lista.content)
                    tasks = lista1['result']['entityList']
                    numero = 0
                    numero_ids = len(tasks) # vefica o numero de IDs
                else:
                    break
                if numero_ids == 0:
                    print("todas as tarefas foram vistas :)")
                else:
                    while True: # seleciona a tarefa
                        if numero != numero_ids:
                            id_task = tasks[numero]['taskID']
                            numero = numero + 1
                            headers = {
                            'Content-Type': 'application/json',
                            'Authorization': 'Bearer ' + token  
                            }
                            requisicao = requests.get(f'https://api.auvo.com.br/v2/tasks/{id_task}', headers=headers) # abre a tarefa 
                            resposta = json.loads(requisicao.content)
                            if resposta['result']['attachments'] == []: #vefica se possui anexos
                                user = resposta['result']['userToName']
                                print(f'colarador {user} sem anexo')
                                event, values = janela.read(timeout=100)
                            else: 
                                imagens = resposta["result"]["attachments"]
                                imagens = len(imagens) #verifica quantos anexos tem 
                                numero_imagens = 0
                                while True:
                                    if numero_imagens != imagens:
                                        imagem = resposta['result']['attachments'][numero_imagens]['url'] #baixa a imagem 
                                        user = resposta['result']['userToName']
                                        data_tarefa = resposta['result']['taskDate']
                                        dt = datetime.strptime(data_tarefa, '%Y-%m-%dT%H:%M:%S')
                                        dia_mes = f'{dt.month:02d}-{dt.day:02d}'
                                        user = f"{dia_mes}-{user}-{numero_imagens}"
                                        numero_imagens = numero_imagens + 1
                                        filename = f"{user}.png" #salva o nome da imagem
                                        caminho_arquivo = os.path.join(pasta_destino, filename)
                                        response = requests.get(imagem)
                                        response.raise_for_status() 
                                        with open(caminho_arquivo, "wb") as file:
                                            file.write(response.content)
                                            print(f"Anexo encontrado! {user} OK!")
                                    else:
                                        break 
                        else:
                            break     
            else:
                janela['-ELEMENTO_DA_INTERFACE-'].update('Novo valor')
                page = page + 1 # vai para a proxima pagina 
                break      
        print("todas as tarefas foram vistas :)")
        
janela.close()