#importando bibliotecas necessárias 
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
import pyautogui
import os
import io
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
import mysql.connector
from dotenv import load_dotenv
from datetime import datetime

#carregando as variaveis de ambiente
load_dotenv(override=True)

#API DRIVE
TOKEN = os.getenv('TOKEN')

#SERVICE_DESK
SD_USER = os.getenv('SD_USER')
SD_PASSWORD = os.getenv('SD_PASSWORD')

#BANCO DE DADOS
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB = os.getenv('DB')

SCOPES = ["https://www.googleapis.com/auth/drive"] #escopo de permissão que o codigo tem sobre o drive
SERVICE_ACCOUNT_FILE = '.venv/CHAVES/token.json' #token para acesso drive

pasta_downloads = os.path.join(os.path.expanduser("~"), "Downloads") #declarando automaticamente o caminho até a pasta de downloads de qualquer maquina 

calendario = [(1, "jan"), (2, "fev"), (3, "mar"), (4, "abr"), (5, "mai"), (6, "jun"), (7, "jul"), (8, "ago"), (9, "set"), (10, "out"), (11, "nov"), (12, "dez")] #lista para tratamento de datas

dias = ['01', '02', '03', '04', '05', '06', '07', '08', '09']

cores_validas = [("rgba(226, 226, 226, 1)"), ("rgba(255, 136, 136, 1)"), ("rgba(225, 68, 56, 1)"), ("rgba(96, 171, 213, 1)"), ("rgba(255, 255, 255, 1)")] #lista com cores para o bot identificar qual opção é valida no calendario

#Lista com numeros de conta e seus respectivos chamados
chamados = [(111976907, "Claro GR Serviço - SP - 1"), (111978575, "Claro GR Serviço - SP - 2"), (113382489, "Claro GR Segurança - PA"), (115726279, "Claro GR Segurança - BA"), 
            (116120396, "Claro GR Segurança - ES"), (117219762, "Claro GR Segurança - SP - 1"), (130908634, "Claro GR Segurança - SP - 3"), (131069394, "Claro GR Segurança - SP - 2"),
            (117273652, "Claro GR Segurança - RJ"), (118684850, "Claro GR Segurança - MA"), (118439059, "Claro GR Segurança - AM"), (117347586, "Claro GR Segurança - PI"),
            (117349213, "Claro GR Segurança - PE - 1"), (120814993, "Claro GR Segurança - PE - 2"), (125609166, "Claro GR Segurança - MG"), (131334756, "Claro GR Segurança - CE") ]


#configurando navegador
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
#servico = Service(ChromeDriverManager().install()) #instalando o driver atual do chrome de forma automatica
navegador = webdriver.Chrome(options=chrome_options)


#conexão com banco de dados
db = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD, 
    database=DB)

cursor = db.cursor()

def campo_valor_total():#preenchendo o campo de valor total
    
    global valor_total
    
    #selecionando o campo e extraindo seu valor 
    navegador.find_element(By.XPATH, '//*[@id="propertyDetailForm"]/div[1]/div[4]/div[1]/div[2]/div[5]/div/p').click()
    campo_valor = navegador.find_element(By.XPATH, '//*[@id="udf_decimal_9017_control"]/input') 
    value_total = campo_valor.get_attribute("value").strip()

    if value_total != valor_total:
        for b in range(0, 12):
            pyautogui.press('backspace')
        
        #tratando o valor para formatação do service desk
        valor_total = valor_total.replace('.', '') 
        valor_total = valor_total.replace(',', '.')
        pyautogui.write(valor_total)
        pyautogui.press('enter')

def campo_competencia():#preenchendo o campo de competencia
    
    global referencia
    
    navegador.find_element(By.XPATH, '//*[@id="propertyDetailForm"]/div[1]/div[4]/div[1]/div[2]/div[10]/div/p').click()
    pyautogui.write(referencia)
    pyautogui.press('enter')

def campo_ultimo_valor(): #preenchendo o campo de ultimo valor
    #consultando a tabela 
    global valor_total
    global conta
    
    cursor.execute(f"SELECT valor FROM Ultimos_Valores WHERE conta = {conta}")
    for linha in cursor.fetchall():
        ultimo_valor = linha[0]

    #selecionando o campo e extraindo o ultimo valor 
    navegador.find_element(By.XPATH, '//*[@id="propertyDetailForm"]/div[1]/div[4]/div[1]/div[2]/div[7]/div/p').click()
    campo_ultimo = navegador.find_element(By.XPATH, '//*[@id="udf_decimal_9016_control"]/input')
    ultimo_value = campo_ultimo.get_attribute("value").strip()
    
    if ultimo_value != ultimo_valor:
        for b in range(0, 12):
            pyautogui.press('backspace')
        
        #tratando o valor para formatação do service desk
        pyautogui.write(ultimo_valor)
        pyautogui.press('enter')

    else:
        pyautogui.press('enter')

    cursor.execute(f"UPDATE Ultimos_Valores SET valor = {valor_total} WHERE conta = {conta}")
    db.commit()

def formatando_vencimento(): #tratando vencimento para selecionar no calendario 
    
    global data_vencimento
    global dia_vencimento_nota
    global mes_vencimento_nota
    global ano_vencimento_nota

    dia_vencimento_nota = str(data_vencimento.split('-')[0])
    mes_vencimento_nota = int(data_vencimento.split('-')[1])
    ano_vencimento_nota = int(data_vencimento.split('-')[2])
    
    #pegando o nome do mes no calendario
    for m in calendario:
        if m[0] == mes_vencimento_nota:
            mes_vencimento_nota = m[1]
            
    if dia_vencimento_nota in dias:
        dia_vencimento_nota = dia_vencimento_nota.strip('0')

def formatando_emissao(): #tratando emissao para selecionar no calendario 
    
    global data_emissao
    global dia_emissao_nota
    global mes_emissao_nota
    global ano_emissao_nota

    dia_emissao_nota = str(data_emissao.split('/')[0])
    mes_emissao_nota = int(data_emissao.split('/')[1])
    ano_emissao_nota = int(data_emissao.split('/')[2])
    
    #pegando o nome do mes no calendario
    for m in calendario:
        if m[0] == mes_emissao_nota:
            mes_emissao_nota = m[1]
            
    if dia_emissao_nota in dias:
        dia_emissao_nota = dia_emissao_nota.strip('0')

def campo_data_emissao(): #preenchendo o campo de data de emissao
    
    global dia_emissao_nota
    global mes_emissao_nota
    global ano_emissao_nota


    navegador.find_element(By.XPATH, '//*[@id="propertyDetailForm"]/div[1]/div[4]/div[1]/div[2]/div[4]/div/p').click() #selecionando o calendario

    #extraindo o mes do calendario
    campo_mes = str((navegador.find_element(By.CSS_SELECTOR, '#udf_date_11102_IN_calendar_parent > div.zdatetimepicker__monthcontainer.zdatetimepicker__days > div.zdatetimepicker__navbar > div.zdatetimepicker__monthyearnav.zh-cursorpointer > span.zdatetimepicker__monthnav').get_attribute("textContent")).strip(' '))
    sleep(2)

    #comparando o mes até ser o mesmo da nota
    while campo_mes != mes_emissao_nota:
                navegador.find_element(By.XPATH, '//*[@id="udf_date_11102_IN_calendar_parent-left-month-0"]').click()
                campo_mes = str((navegador.find_element(By.CSS_SELECTOR, '#udf_date_11102_IN_calendar_parent > div.zdatetimepicker__monthcontainer.zdatetimepicker__days > div.zdatetimepicker__navbar > div.zdatetimepicker__monthyearnav.zh-cursorpointer > span.zdatetimepicker__monthnav').get_attribute("textContent")).strip(' '))
                sleep(1)

    #extraindo o ano
    campo_ano = str(navegador.find_element(By.CSS_SELECTOR, '#udf_date_11102_IN_calendar_parent > div.zdatetimepicker__monthcontainer.zdatetimepicker__days > div.zdatetimepicker__navbar > div.zdatetimepicker__monthyearnav.zh-cursorpointer > span.zdatetimepicker__yearnav').get_attribute("textContent")).strip(' ')
    campo_ano = int(campo_ano)

    #comparando o ano até ser o mesmo da nota 
    while campo_ano != ano_emissao_nota: 
        if campo_ano < ano_emissao_nota:
            navegador.find_element(By.XPATH, '//*[@id="udf_date_11102_IN_calendar_parent-right-month-0"]').click()
            campo_ano = str(navegador.find_element(By.CSS_SELECTOR, '#udf_date_11102_IN_calendar_parent > div.zdatetimepicker__monthcontainer.zdatetimepicker__days > div.zdatetimepicker__navbar > div.zdatetimepicker__monthyearnav.zh-cursorpointer > span.zdatetimepicker__yearnav').get_attribute("textContent")).strip(' ')
            campo_ano = int(campo_ano)
        else:
            navegador.find_element(By.XPATH, '//*[@id="udf_date_11102_IN_calendar_parent-left-year"]').click()
            campo_ano = str(navegador.find_element(By.CSS_SELECTOR, '#udf_date_11102_IN_calendar_parent > div.zdatetimepicker__monthcontainer.zdatetimepicker__days > div.zdatetimepicker__navbar > div.zdatetimepicker__monthyearnav.zh-cursorpointer > span.zdatetimepicker__yearnav').get_attribute("textContent")).strip(' ')
            campo_ano = int(campo_ano)

    #declarando dia_selecionado = false para logica de escolher o dia 
    dia_selecionado = False

    for l in range (1, 7):
        if dia_selecionado == True:
            break
        
        #iterando sobre todos os dias do calendario extraindo o dia e a cor até serem validos para selecionar 
        for c in range (1, 8):
            campo_dia_emissao = (navegador.find_element(By.XPATH, f'//*[@id="udf_date_11102_IN_calendar_parent"]/div[1]/div[2]/table/tbody/tr[{l}]/td[{c}]'))
            dia_sdp_emissao = str(navegador.find_element(By.XPATH, f'//*[@id="udf_date_11102_IN_calendar_parent"]/div[1]/div[2]/table/tbody/tr[{l}]/td[{c}]').get_attribute("textContent").strip(' '))
            color_emissao = campo_dia_emissao.value_of_css_property("color")


            if dia_sdp_emissao == dia_emissao_nota and color_emissao in cores_validas:
                navegador.find_element(By.XPATH, f'//*[@id="udf_date_11102_IN_calendar_parent"]/div[1]/div[2]/table/tbody/tr[{l}]/td[{c}]').click()
                dia_selecionado = True #confirmando que o dia já foi selecionado 
                navegador.find_element(By.XPATH, '//*[@id="udf_date_11102_IN_calendar_parent"]/div[3]/div[3]/button[2]').click()

                #confirmando os campos
                sleep(3)
                navegador.find_element(By.XPATH, '/html/body/div[61]/div[2]/div/div/div[1]/div/div[3]/div[3]/div[1]/div[1]/div[3]/div[2]/div/div/div[1]/div[1]/div[2]/form/div[1]/div[4]/div[1]/div[2]/div[4]/div/div/div[2]/button[1]').click()
                break

def campo_data_vencimento():#preenchendo o campo de data de vencimento 
    
    global dia_vencimento_nota
    global mes_vencimento_nota
    global ano_vencimento_nota
    
    navegador.find_element(By.XPATH, '//*[@id="propertyDetailForm"]/div[1]/div[4]/div[1]/div[2]/div[9]/div/p').click() #selecionando o calendario 

    #estraindo o campo do calendario
    campo_mes = str((navegador.find_element(By.CSS_SELECTOR, '#udf_date_9008_IN_calendar_parent > div.zdatetimepicker__monthcontainer.zdatetimepicker__days > div.zdatetimepicker__navbar > div.zdatetimepicker__monthyearnav.zh-cursorpointer > span.zdatetimepicker__monthnav').get_attribute("textContent")).strip(' '))

    #comparando o mes até ser o mesmo da nota
    while campo_mes != mes_vencimento_nota:
                navegador.find_element(By.XPATH, '//*[@id="udf_date_9008_IN_calendar_parent-right-month-0"]').click()
                campo_mes = str((navegador.find_element(By.CSS_SELECTOR, '#udf_date_9008_IN_calendar_parent > div.zdatetimepicker__monthcontainer.zdatetimepicker__days > div.zdatetimepicker__navbar > div.zdatetimepicker__monthyearnav.zh-cursorpointer > span.zdatetimepicker__monthnav').get_attribute("textContent")).strip(' '))
                sleep(1)

    #extraindo o ano
    campo_ano = str(navegador.find_element(By.CSS_SELECTOR, '#udf_date_9008_IN_calendar_parent > div.zdatetimepicker__monthcontainer.zdatetimepicker__days > div.zdatetimepicker__navbar > div.zdatetimepicker__monthyearnav.zh-cursorpointer > span.zdatetimepicker__yearnav').get_attribute("textContent")).strip(' ')
    campo_ano = int(campo_ano)

    #comparando o ano até ser o mesmo da nota 
    while campo_ano != ano_vencimento_nota: 
        if campo_ano < ano_vencimento_nota:
            navegador.find_element(By.XPATH, '//*[@id="udf_date_9008_IN_calendar_parent-right-year"]').click()
            campo_ano = str(navegador.find_element(By.CSS_SELECTOR, '#udf_date_9008_IN_calendar_parent > div.zdatetimepicker__monthcontainer.zdatetimepicker__days > div.zdatetimepicker__navbar > div.zdatetimepicker__monthyearnav.zh-cursorpointer > span.zdatetimepicker__yearnav').get_attribute("textContent")).strip(' ')
            campo_ano = int(campo_ano)
        else:
            navegador.find_element(By.XPATH, '//*[@id="udf_date_9008_IN_calendar_parent-left-year"]').click()
            campo_ano = str(navegador.find_element(By.CSS_SELECTOR, '#udf_date_9008_IN_calendar_parent > div.zdatetimepicker__monthcontainer.zdatetimepicker__days > div.zdatetimepicker__navbar > div.zdatetimepicker__monthyearnav.zh-cursorpointer > span.zdatetimepicker__yearnav').get_attribute("textContent")).strip(' ')
            campo_ano = int(campo_ano)


    #declarando dia_selecionado = false para logica de escolher o dia 
    dia_selecionado = False

    for l in range (1, 7):
        if dia_selecionado == True:
            break
        
        #iterando sobre todos os dias do calendario extraindo o dia e a cor até serem validos para selecionar 
        for c in range (1, 8):
            campo_dia_vencimento = (navegador.find_element(By.XPATH, f'//*[@id="udf_date_9008_IN_calendar_parent"]/div[1]/div[2]/table/tbody/tr[{l}]/td[{c}]'))
            dia_sdp_vencimento = str(navegador.find_element(By.XPATH, f'//*[@id="udf_date_9008_IN_calendar_parent"]/div[1]/div[2]/table/tbody/tr[{l}]/td[{c}]').get_attribute("textContent").strip(' '))
            color_vencimento = campo_dia_vencimento.value_of_css_property("color")

            if dia_sdp_vencimento == dia_vencimento_nota and color_vencimento in cores_validas:
                navegador.find_element(By.XPATH, f'//*[@id="udf_date_9008_IN_calendar_parent"]/div[1]/div[2]/table/tbody/tr[{l}]/td[{c}]').click()
                sleep(2)
                dia_selecionado = True #confirmando que o dia já foi selecionado 
                navegador.find_element(By.XPATH, '//*[@id="udf_date_9008_IN_calendar_parent"]/div[3]/div[3]/button[2]').click()

                #confirmando os campos
                sleep(3)
                navegador.find_element(By.XPATH, '/html/body/div[61]/div[2]/div/div/div[1]/div/div[3]/div[3]/div[1]/div[1]/div[3]/div[2]/div/div/div[1]/div[1]/div[2]/form/div[1]/div[4]/div[1]/div[2]/div[9]/div/div/div[2]/button[1]').click()
                break

def autenticar():  #autenticando as credenciais da API do drive
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return creds

def download_file(real_file_id):
    """Downloads a file
    Args:
        real_file_id: ID of the file to download
        Returns : IO object with location.

    Load pre-authorized user credentials from the environment.
    TODO(developer) - See https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """
    creds = autenticar()

    try:
        # create drive api client
        service = build("drive", "v3", credentials=creds)

        file_id = real_file_id

    # pylint: disable=maybe-no-member
        request = service.files().get_media(fileId=file_id)
        global file
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}.")

    except HttpError as error:
        print(f"An error occurred: {error}")
        file = None

    return file.getvalue()

def download_file_os(real_file_id, save_path): 
    if file is not None:
        # Write downloaded content to the specified save path
        with open(save_path, 'wb') as f:
            f.write(file.getvalue())
        print(f"File downloaded successfully and saved to: {save_path}")

def upload_arquivo():
    lista_arquivos = os.listdir(pasta_downloads) #listando o diretorio de downloads
    lista_datas = [] #criando outra lista pata armezenar o tempo de modificação de cada arquivo em downloads

    for arquivo in lista_arquivos:
    # descobrir a data desse arquivo
        if ".pdf" in arquivo:
            data = os.path.getmtime(f"{pasta_downloads}/{arquivo}") #pegando a data de modificaçãp de cada pdf 
            lista_datas.append((data, arquivo)) #armazenadno o tempo de modificação e o nome do arquivo em formato de matriz

    #ordenando em ordem crescente e pegando o nome do primerio arquivo 
    lista_datas.sort(reverse=True)     
    global ultimo_arquivo
    ultimo_arquivo = lista_datas[0]

    #fazendo o upload do pdf da nota
    upload_pdf = navegador.find_element(By.XPATH, '//*[@id="file-browser-area"]/div/p/label/input')

    pdf = f'{pasta_downloads}/{ultimo_arquivo[1]}'

    upload_pdf.send_keys(pdf)

    sleep(4)
    for tab in range(0, 3):
        pyautogui.press('tab')
        sleep(2)

    pyautogui.press('enter')

def campo_dia_emissao():
    
    navegador.find_element(By.XPATH, '//*[@id="propertyDetailForm"]/div[1]/div[4]/div[1]/div[2]/div[2]/div/p').click()
    
    campo_emissao = navegador.find_element(By.XPATH, '//*[@id="udf_long_14710_control"]/input')
    value_emissao = campo_emissao.get_attribute("value").strip()

    if value_emissao != dia_emissao_nota:
        for b in range(0, 2):
            pyautogui.press('backspace')

        pyautogui.write(dia_emissao_nota)
        pyautogui.press('enter')


data = datetime.now().month

nome_tabela = 'Mes' +  '_' + str(data)


primeiro = False


navegador.get("https://sd.grupogr.com.br/HomePage.do?view_type=my_view")

sleep(3)

navegador.find_element(By.XPATH, '//*[@id="username"]').send_keys(SD_USER)
navegador.find_element(By.XPATH, '//*[@id="password"]').send_keys(SD_PASSWORD)
navegador.find_element(By.XPATH, '/html/body/div[1]/center/div[2]/div/div[3]/div/form/div/div[2]/div/div/div/div[18]/button').click()

sleep(10)

navegador.find_element(By.XPATH, '//*[@id="requests"]').click()

consulta = f"SELECT * FROM {nome_tabela} WHERE status = 'pendente'" 
cursor.execute(consulta)

for linha in cursor.fetchall():
    
    # Extrair valores das colunas
    id_lancamento = linha[0]
    conta = linha[1]
    nome = linha[2]
    valor_total = linha[3]
    data_vencimento = linha[4]
    referencia = linha[5]
    data_emissao = linha[6]
    id_drive = linha[7]


    lancar = False
    for c in chamados:
        if c[0] == conta:
            pesquisa = c[1]
            print(pesquisa)
            lancar = True
            break

    if lancar == True:
        sleep(3)
        navegador.find_element(By.XPATH, '//*[@id="requests_list_listSearch"]').click()
        sleep(2)
        navegador.find_element(By.XPATH, '//*[@id="requests_list_head"]/tr[2]/td[7]/div/input').click()
        navegador.find_element(By.XPATH, '//*[@id="requests_list_head"]/tr[2]/td[7]/div/input').send_keys(pesquisa + Keys.ENTER)

        sleep(5)


        if primeiro == False:
            for t in range(12):
                pyautogui.press("tab")
            pyautogui.press('enter')
            primeiro = True
        else:
            for t in range(12):
                pyautogui.press('tab')
            pyautogui.press('enter')

        sleep(10)
        
        formatando_emissao()
        sleep(4)
        campo_dia_emissao()
        sleep(4)
        campo_valor_total()
        sleep(4)
        campo_ultimo_valor()
        sleep(4)
        campo_competencia()
        sleep(4)
        formatando_vencimento()
        campo_data_emissao()
        sleep(4)
        campo_data_vencimento()
        sleep(4)
        if __name__ == "__main__":
            download_file(real_file_id=f"{id_drive}")
        sleep(3)

        if __name__ == "__main__":
            file_id = id_drive
            save_location = f"{pasta_downloads}/{file}" 
            download_file_os(file_id, save_location)

        sleep(3)
        os.rename(f'{save_location}', f'{pasta_downloads}/{pesquisa}.pdf')
        sleep(2)

        upload_arquivo()

        if os.path.exists(f'{pasta_downloads}/{pesquisa}.pdf'):
            os.remove(f'{pasta_downloads}/{pesquisa}.pdf')

        cursor.execute(f"UPDATE {nome_tabela} SET status = 'SDP' WHERE conta = {conta}")
        db.commit()

        sleep(6)
        navegador.find_element(By.XPATH, '//*[@id="back_to_list"]').click()

cursor.close()
db.close()


