import requests
import json
from datetime import datetime
import PySimpleGUI as sg
import os

layout = [
    [sg.Text('Data de Início:'), sg.Input(key='-DATA_INICIO-', enable_events=True), sg.CalendarButton('Selecionar', target='-DATA_INICIO-', format='%Y-%m-%d')],
    [sg.Text('  Data Final:   '), sg.Input(key='-DATA_FINAL-', enable_events=True), sg.CalendarButton('Selecionar', target='-DATA_FINAL-', format='%Y-%m-%d')],
    [sg.Text('Onde Salvar? '), sg.Input(key='-PASTA_DESTINO-', enable_events=True), sg.FolderBrowse('Selecionar')],
    [sg.Button('Baixar', button_color=('white', 'Darkblue'), image_size=(50, 25), border_width=5, key='-BAIXAR-'), sg.Text('                                                                                              '),sg.Button('Sair', button_color=('Darkred'))]
]
sg.set_global_icon('icon.ico')
janela = sg.Window('Filtro', layout)

def baixar_anexos(data_inicio, data_final, pasta_destino):
    global token
    try:
        request = requests.get(f"https://api.auvo.com.br/v2/login/?apiKey={apikey}&apiToken={token}")
        certo = json.loads(request.content)
        access_token = certo['result']['accessToken']
        data = {'startDate': f'{data_inicio}T00:00:00','endDate': f'{data_final}T00:00:00'}
        headers = {'Content-Type': 'application/json','Authorization': 'Bearer ' + access_token}
        page = 1
        pageSize = 100
        order = 'asc'
        selectfields = ''
        numero_solicitacao = 0 
        while True:
            if page != 100:
                numero_solicitacao = numero_solicitacao + 1
                lista = requests.get(f'https://api.auvo.com.br/v2/tasks/?paramFilter={data}&page={page}&pageSize={pageSize}&order={order}&selectfields={selectfields}', headers=headers)
                if numero_solicitacao == 100:
                    break
                page = page + 1 
                if lista.status_code == 200:
                    lista1 = json.loads(lista.content)
                    
                    tarefa = 0
                    numero = 0
                    numero_ids = len(lista1['result']['entityList'])
                else:
                    break
                if numero_ids == 0:   
                    print('')
                else:
                    print(f'esse é o numero de IDs {numero_ids}')
                    while True:
                        tasks = lista1['result']['entityList'][tarefa]
                        tarefa = tarefa + 1 
                        if tarefa != numero_ids:
                            numero = numero + 1
                            resposta = tasks
                            if resposta['attachments'] == []:
                                user = resposta['userToName']
                                print(f'colaborador {user} sem anexo')
                            else:
                                imagens = resposta["attachments"]
                                imagens = len(imagens)
                                numero_imagens = 0
                                while True:
                                    if numero_imagens != imagens:
                                        imagem = resposta['attachments'][numero_imagens]['url']
                                        user = resposta['userToName']
                                        data_tarefa = resposta['taskDate']
                                        dt = datetime.strptime(data_tarefa, '%Y-%m-%dT%H:%M:%S')
                                        dia_mes = f'{dt.day:02d}-{dt.month:02d}'
                                        user = f"{dia_mes}-{user}-{numero_imagens}"
                                        numero_imagens = numero_imagens + 1
                                        filename = f"{user}.png"
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
                page = page + 1
                break      
        sg.popup_ok('Todas as tarefas vistas😁')
    except Exception as e:
        sg.popup_error(f"ERRO:{str(e)} (me chame!)")

while True:
    eventos, valores = janela.read()
    if eventos == sg.WINDOW_CLOSED or eventos == 'Sair':
        break
    elif eventos == '-BAIXAR-':
        janela['-BAIXAR-'].update(disabled=True)  # Desabilita o botão 'Baixar'
        data_inicio = valores['-DATA_INICIO-']
        data_final = valores['-DATA_FINAL-']
        pasta_destino = valores['-PASTA_DESTINO-']
        baixar_anexos(data_inicio, data_final, pasta_destino)
        janela['-BAIXAR-'].update(disabled=False)  # Habilita o botão 'Baixar'
janela.close()
