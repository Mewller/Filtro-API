import requests
import json
from datetime import datetime, timedelta, date
import PySimpleGUI as sg
import os
import threading


apikey = ''
token = ''

layout = [
    [sg.Text('Data de Início:'), sg.Input(key='-DATA_INICIO-', enable_events=True), sg.CalendarButton('Selecionar', target='-DATA_INICIO-', format='%Y-%m-%d')],
    [sg.Text('  Data Final:   '), sg.Input(key='-DATA_FINAL-', enable_events=True), sg.CalendarButton('Selecionar', target='-DATA_FINAL-', format='%Y-%m-%d')],
    [sg.Text('Onde Salvar? '), sg.Input(key='-PASTA_DESTINO-', enable_events=True), sg.FolderBrowse('Selecionar')],
    [sg.Output(size=(68, 6))],
    [sg.Button('Baixar', button_color=('white', 'Darkblue'), image_size=(50, 25), border_width=5, key='-BAIXAR-'), sg.Text('                                                                                              '),sg.Button('Sair', button_color=('Darkred'))]
    
]
janela = sg.Window('Filtro', layout)

def baixar_anexos(data_inicio, data_final, pasta_destino):
    try:
        request = requests.get(f"https://api.auvo.com.br/v2/login/?apiKey={apikey}&apiToken={token}")
        certo = json.loads(request.content)
        access_token = certo['result']['accessToken']
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + access_token}
        
        dt_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        dt_final = datetime.strptime(data_final, '%Y-%m-%d').date()
        
        dt_atual = date.today() + timedelta(days=1)
        if dt_inicio > dt_atual:
            janela.write_event_value('-POPUP-', 'A data de início pode ser no máximo hoje.')
            return
        
        if dt_final > dt_atual:
            janela.write_event_value('-POPUP-', 'A data final pode ser no máximo hoje.')
            return
        
        if dt_inicio > dt_final:
            janela.write_event_value('-POPUP-', 'A data de início deve ser anterior ou igual à data final.')
            return
        
        if dt_final - dt_inicio > timedelta(days=7):
            janela.write_event_value('-POPUP-', 'O período selecionado não pode ser maior que 1 semana.')
            return
        
        data = {'startDate': f'{data_inicio}T00:00:00', 'endDate': f'{data_final}T23:59:59'}
        page = 1
        pageSize = 100
        order = 'asc'
        selectfields = ''
        numero_solicitacao = 0
        
        while True:
            if page != 100:
                numero_solicitacao += 1
                lista = requests.get(f'https://api.auvo.com.br/v2/tasks/?paramFilter={data}&page={page}&pageSize={pageSize}&order={order}&selectfields={selectfields}', headers=headers)
                if numero_solicitacao == 100:
                    break
                page += 1
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
                    while True:
                        tasks = lista1['result']['entityList'][tarefa]
                        tarefa += 1
                        if tarefa != numero_ids:
                            numero += 1
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
                                        numero_imagens += 1
                                        filename = f"{user}.png"
                                        if imagem.endswith('.pdf'):
                                            filename = f"{user}.pdf" 
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
                page += 1
                break
        janela.write_event_value('-POPUP-', 'Todas as tarefas vistas 😁')
    except Exception as e:
        janela.write_event_value('-POPUP-', f"ERRO:{str(e)} (me chame!)")

def baixar_anexos_thread(data_inicio, data_final, pasta_destino):
    baixar_anexos(data_inicio, data_final, pasta_destino)

while True:
    eventos, valores = janela.read()
    if eventos == sg.WINDOW_CLOSED or eventos == 'Sair':
        break
    elif eventos == '-BAIXAR-':
        janela['-BAIXAR-'].update(disabled=True)  
        data_inicio = valores['-DATA_INICIO-']
        data_final = valores['-DATA_FINAL-']
        pasta_destino = valores['-PASTA_DESTINO-']
        thread = threading.Thread(target=baixar_anexos_thread, args=(data_inicio, data_final, pasta_destino))
        thread.start()
    elif eventos == '-POPUP-':
        sg.popup_ok(valores['-POPUP-'])
        janela['-BAIXAR-'].update(disabled=False)  

janela.close()
