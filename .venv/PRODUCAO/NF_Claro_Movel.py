#importando bibliotecas e funcoes necessarias 
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from time import sleep 
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account
import os
import fitz
import re
import mysql.connector
from dotenv import load_dotenv

#VARIAVEIS DE AMBIENTE
load_dotenv(override=True)

#BANCO DE DADOS
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB = os.getenv('DB')

#API DRIVE
SHARED_DRIVE_ID = os.getenv('SHARED_DRIVE_ID')
TOKEN = os.getenv('TOKEN')

#CLARO ONLINE
CLARO = os.getenv('CLARO')


#conexão com banco de dados
db = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD, 
    database=DB)

cursor = db.cursor()


SCOPES = ["https://www.googleapis.com/auth/drive"] #escopo de permissão que o codigo tem sobre o drive
SERVICE_ACCOUNT_FILE = '.venv/CHAVES/token.json' #token para acesso drive
SHARED_DRIVE_ID = SHARED_DRIVE_ID #ID da pasta no drive para armazenar as NFs PRECISA SER TROCADO A CADA ANO!!!!


#dicionario contendo XPATHs utilizados
Portal_map = {
    "buttons": {
        "download":{
            "xpath": "/html/body/center/form/table/tbody/tr[6]/td/input"
        }
    }
}


pasta_downloads = os.path.join(os.path.expanduser("~"), "Downloads") #declarando automaticamente o caminho até a pasta de downloads de qualquer maquina 


#configurando o navegador
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
#servico = Service(ChromeDriverManager().install()) #instalando o driver atual do chrome de forma automatica
navegador = webdriver.Chrome(options=chrome_options)


def reinciando(): #funçao para reiniciar o processo
    navegador.close() #fechando a aba de download
    navegador.switch_to.window(navegador.window_handles[0]) #voltando a controlar a tela de login do portal
    navegador.find_element(By.XPATH, '/html/body/center/a').click() #clicando no botao "reiniciar" para o processo de login


def verificando_conta(conta): #funçao para selecionar as contas 
    combobox_contas = navegador.find_element(By.XPATH, "/html/body/table[2]/tbody/tr[2]/td/table/tbody/tr/td[6]/form/select") #abrindo a lista de contas dentro do login
    combobox_contas.click()
    options_contas = combobox_contas.find_elements(By.TAG_NAME, "option")
    sleep(2)
    
    #extraindo o texto de cada opção na lista até bater com a conta atual
    for option in options_contas:
        if option.text == conta:
            option.click()
            break


def verificando_data(): #funçao para verificar as datas das opçoes disponiveis
    global fatura #declarando a variavel fatura (ela que diz se a fatura do mes atual está disponivel ou não)
    combobox = navegador.find_element(By.XPATH, "/html/body/center/form/table/tbody/tr[4]/td/select") #armazenando a lista de datas em uma variavel
    combobox.click() #abrindo a lista
    options = combobox.find_elements(By.TAG_NAME, "option") #passando por todas as opçoes dentro da lista da variavel de datas disponiveis
    sleep(2)
    fatura = False #recebendo false para que a cada conta logada/fatura ele tenha que verificar novamente

    #lendo todas opções disponiveis
    for option in options:
        final_option = option.text.split("/")[2] #pegando a parte final da opção (o ano e referencia estão nela)
        mounth_option = option.text.split("/")[1] #pegando a referenia da opção
        year_option = final_option.split("-")[0] #pegando o ano da opção
        
        #transformando em inteiros para comparar as datas com as atuais
        mes_option = int(mounth_option)
        ano_option = int(year_option)
        
        #pegando ao ano atual
        ano_atual = datetime.now().year
        
        #se encontrar uma fatura com o mes atual e ano atual vai selecionar ela para download
        if mes_option == data and ano_option == ano_atual :
            fatura = True
            option.click()
            break


def autenticar():  #autenticando as credenciais da API do drive
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return creds


def arquivo_recente(): #função para pegar o arquivo mais recente na pasta downloads (ultima NF baixada)
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


def extração(): #função para extrair as informações (Total a pagar, Juros, Data de Emissão) das NFs

    #abrindo o arquivo e passando as paginas
    pdf = fitz.open(f'{pasta_downloads}/{ultimo_arquivo[1]}')
    first_page = pdf[0]
    second_page = pdf[1]
    three_page = pdf[2]
    
    #obtendo os textos das paginas
    text = first_page.get_text() 
    text2 = second_page.get_text()
    text3 = three_page.get_text()
    
    global data_emissao
    data_emissao = None
        # Expressão regular para encontrar "Data de Emissão"
    match = re.search(r"Data de emissão:\s+(.+)", text2)
    if match:
        data_emissao = match.group(1)

    if data_emissao:
        print(f"data de emissão: {data_emissao}")
    else:
        match = re.search(r"Data de emissão:\s+(.+)", text3)
        if match:
            data_emissao = match.group(1)
            print(f"data de emissão: {data_emissao}")


    global valor_total
    valor_total = None
        # Expressão regular para encontrar "Total a pagar" 
    match = re.search(r"Total a pagar\s+R\$ ([\d.,]+)", text)
    if match:
        valor_total = match.group(1)

    if valor_total:
        print(f"Valor total a pagar: R$ {valor_total}")
    else:
        print("Valor total não encontrado na fatura.")
    
    print('-'*20)


def upload_drive(file_path): #função para realizar upload no drive
    creds = autenticar()
    service = build('drive', 'v3', credentials=creds)
    
    #chamando a função para checar a pasta no drive e evitar duplicação
    if drive == False:
        print(f"O arquivo '{file_name}' já existe no Drive. Pulando envio.")
        return

    else:
        #nome do arquivo e para que pasta vai
        file_metadata = {
            'name' : (f"{file_name}"),
            'parents' : [SHARED_DRIVE_ID]
        }
        
        response = service.files().create(
            supportsAllDrives=True, #linha para permitir o codigo acessar pastas compartilhadas no drive
            body=file_metadata, #corpo do arquivo no drive
            media_body=file_path #informações do arquivo no drive
            ).execute()
        
        global file_id
        file_id = response['id']
        print(f"Uploaded file ID: {file_id}")
        
        cursor.execute(f"""
                UPDATE {nome_tabela}
                SET id_drive = "{file_id}"
                WHERE conta = "{n_conta}";
                """)
        db.commit()


def insert_MySQL():

    global drive
    #dando insert na tabela criado no MySQL
    try:
        cursor.execute(f"""
            INSERT INTO {nome_tabela} (
                conta, nome_nota, valor_total, data_vencimento, ref,  data_emissao, status
            ) VALUES (
                '{n_conta}', '{nome_sql}', '{valor_total}', '{vencimento}', '{referencia}', '{data_emissao}', 'pendente'
            )
        """)
        db.commit()

        drive = True
    except:
        drive = False
        print(f"Nota já está no banco de dados")


def remover_arquivo(): #funçao para remover o pdf da nota da pasta downloads
    path = (f'{pasta_downloads}/{ultimo_arquivo[1]}')
    print(path)
    if os.path.exists(path):
        os.remove(path)


def rename_arquivo():
    #lista de contas com seus respectivos estados para nomear a NF
    estados = [ (568587748, "SP"), (106971789, "PA"), (109309116, "BA"), (109700244, "ES"), (110798646, "SP"), 
                (110851009, "RJ"), (112255858, "MA"), (110768553, "AM"), (110925066, "PI"), ('68317817000474\n', "PE"), 
                (118927427, "MG"), ('68317817001101\n', "CE"),  ('00215548000159\n', "SP")]

    #numero de conta e vencimento para nomear a NF
    global file_name
    global nome_sql
    global n_conta
    global vencimento
    global estado
    global referencia
    n_conta = ultimo_arquivo[1].split("_")[0]
    vencimento = ultimo_arquivo[1].split("_")[1]
    referencia = ultimo_arquivo[1].split("_")[2]

    #iterando sobre a lista de estados para ver qual é o estado da conta atual
    for e in estados:
        if e[0] == login:
            estado = str(e[1])
            
    #nessa conta são NFs de serviços, mans nas outra sera seguranca
    if login == '00215548000159\n':   
        file_name = os.path.basename(f"{n_conta}_Claro_GR_Servico_{estado}_{vencimento}_ref-{referencia}.pdf") #padrao para NF servico
        nome_sql = (f"Claro GR Serviço - {estado}")
    else:       
        file_name = os.path.basename(f"{n_conta}_Claro_GR_Seguranca_{estado}_{vencimento}_ref-{referencia}.pdf") #padrao para NF seguranca
        nome_sql = (f"Claro GR Segurança - {estado}")


data = datetime.now().month

nome_tabela = 'Mes' +  '_' + str(data)

#executando comando para criar a tabela do mês no MySQL
cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {nome_tabela} (
        id INT PRIMARY KEY AUTO_INCREMENT,
        conta INT NOT NULL UNIQUE,
        nome_nota VARCHAR(50) NOT NULL,
        valor_total VARCHAR(15) NOT NULL,
        data_vencimento VARCHAR (10) NOT NULL,
        ref VARCHAR (2) NOT NULL,
        data_emissao VARCHAR (10) NOT NULL,
        id_drive VARCHAR(50) UNIQUE,
        status VARCHAR (10) NOT NULL 
    );
    """)

db.commit()





#abrindo o portal da claro 
navegador.get("https://contaonline.claro.com.br/webbow/login/initPJ_oqe.do ")


#abrindo o arquivo com os logins
with open(".venv/PRODUCAO/claro.txt", 'r') as arquivo:
    for linha in arquivo:
        login_cnpj = False
        if linha == '00215548000159\n' or linha == '68317817000474\n' or linha == '68317817001101\n':
            login = linha
            login_cnpj = True
        else:
            login = int(linha) #armezando a linha atual em uma variavel int para verificar se é um login com mais de uma fatura para baixar

        #logando no portal e indo para a aba de downloads
        navegador.find_element(By.XPATH, '/html/body/form/table/tbody/tr[2]/td[2]/input').send_keys(CLARO) #preenchendo a senha
        navegador.find_element(By.XPATH, '/html/body/form/table/tbody/tr[2]/td[1]/input').send_keys(linha) #preenchendo o campo de login
        sleep(4)
        navegador.switch_to.window(navegador.window_handles[1]) #mudando a aba para ser controlada
        if      login_cnpj == True:
            None
        else:
            try:
                navegador.find_element(By.CLASS_NAME, 'close-btn').click()
            except:
                None
        sleep(3)
        navegador.find_element(By.XPATH, '/html/body/table[1]/tbody/tr/td[1]/ul/table/tbody/tr/td[5]/li/a/img').click() #indo para gerenciamento
        (sleep(2))
        navegador.find_element(By.XPATH, '/html/body/table/tbody/tr/td[1]/ul/table/tbody/tr/td[5]/li/ul/li[3]/a').click() #indo para a aba de downloads de ultimas faturas


        #caso especifico de login com mais de uma fatura
        if login == 106971789:
            verificando_conta('113382489')
            sleep(2)
            verificando_data()
            if fatura == True:
                navegador.find_element(By.XPATH, Portal_map['buttons']["download"]["xpath"]).click() #clicando em ok para download
                sleep(7)
                arquivo_recente()
                extração()
                rename_arquivo()
                insert_MySQL()
                upload_drive(f"{pasta_downloads}/{ultimo_arquivo[1]}")
                remover_arquivo()
            sleep(2)
            reinciando()
        
        elif login == 109309116:
            verificando_conta('115726279')
            sleep(2)
            verificando_data()
            if fatura == True:
                navegador.find_element(By.XPATH, Portal_map['buttons']["download"]["xpath"]).click() #clicando em ok para download
                sleep(7)
                arquivo_recente()
                extração()
                rename_arquivo()
                insert_MySQL()
                upload_drive(f"{pasta_downloads}/{ultimo_arquivo[1]}")
                remover_arquivo()
            sleep(2)
            reinciando()
        
        elif login == '00215548000159\n':  
            verificando_conta('111976907')
            sleep(2)
            verificando_data()
            if fatura == True: #se a primeira fatura não estiver disponivel ele vai selecionar a lista de faturas e ir para a segunda opção
                navegador.find_element(By.XPATH, Portal_map['buttons']["download"]["xpath"]).click() #clicando em ok para download
                sleep(7)
                arquivo_recente()
                extração()
                rename_arquivo()
                insert_MySQL()
                upload_drive(f"{pasta_downloads}/{ultimo_arquivo[1]}")
                remover_arquivo()
            verificando_conta('111978575')
            sleep(2)
            verificando_data()
            if fatura == True: #se a segunda fatura não esiver disponivel ele vai selecionar a lista de faturas e ir para a primeira opção
                navegador.find_element(By.XPATH, Portal_map['buttons']["download"]["xpath"]).click() #clicando em ok para download
                sleep(7)
                arquivo_recente()
                extração()
                rename_arquivo()
                insert_MySQL()
                upload_drive(f"{pasta_downloads}/{ultimo_arquivo[1]}")
                remover_arquivo()
            verificando_conta('111976907')
            sleep(2)
            reinciando()

        #caso especifico de login com mais de uma fatura
        elif login == 110798646:
            verificando_conta('117219762')
            sleep(2)
            verificando_data()
            if fatura == True:
                navegador.find_element(By.XPATH, Portal_map['buttons']["download"]["xpath"]).click() #clicando em ok para download
                sleep(7)
                arquivo_recente()
                extração()
                rename_arquivo()
                insert_MySQL()
                upload_drive(f"{pasta_downloads}/{ultimo_arquivo[1]}")
                remover_arquivo()
            sleep(1)
            verificando_conta('130908634')
            sleep(2)
            verificando_data()
            if fatura == True:
                navegador.find_element(By.XPATH, Portal_map['buttons']["download"]["xpath"]).click() #clicando em ok para download
                sleep(7)
                arquivo_recente()
                extração()
                rename_arquivo()
                insert_MySQL()
                upload_drive(f"{pasta_downloads}/{ultimo_arquivo[1]}")
                remover_arquivo()
            sleep(1)
            verificando_conta('131069394')
            sleep(4)
            verificando_data()
            if fatura == True:
                navegador.find_element(By.XPATH, Portal_map['buttons']["download"]["xpath"]).click() #clicando em ok para download
                sleep(7)
                arquivo_recente()
                extração()
                rename_arquivo()
                insert_MySQL()
                upload_drive(f"{pasta_downloads}/{ultimo_arquivo[1]}")
                remover_arquivo()
            verificando_conta('117219762')
            sleep(2)
            reinciando()
            
        #caso especifico de login com mais de uma fatura
        elif login == 118927427:
            verificando_conta('125609166')
            sleep(2)
            verificando_data()
            if fatura == True:
                navegador.find_element(By.XPATH, Portal_map['buttons']["download"]["xpath"]).click() #clicando em ok para download
                sleep(7)
                arquivo_recente()
                extração()
                rename_arquivo()
                insert_MySQL()
                upload_drive(f"{pasta_downloads}/{ultimo_arquivo[1]}")
                remover_arquivo()
            sleep(2)
            reinciando()

        #caso especifico de login com mais de uma fatura
        elif login == '68317817000474\n':
            verificando_conta('117349213')
            sleep(2)
            verificando_data()
            if fatura == True:
                navegador.find_element(By.XPATH, Portal_map['buttons']["download"]["xpath"]).click() #clicando em ok para download
                sleep(7)
                arquivo_recente()
                extração()
                rename_arquivo()
                insert_MySQL()
                upload_drive(f"{pasta_downloads}/{ultimo_arquivo[1]}")
                remover_arquivo()
                sleep(2)
            verificando_conta('120814993')
            sleep(2)
            verificando_data()
            if fatura == True:
                navegador.find_element(By.XPATH, Portal_map['buttons']["download"]["xpath"]).click() #clicando em ok para download
                sleep(7)
                arquivo_recente()
                extração()
                rename_arquivo()
                insert_MySQL()
                upload_drive(f"{pasta_downloads}/{ultimo_arquivo[1]}")
                remover_arquivo()
            verificando_conta('117349213')
            sleep(2)
            reinciando()

        elif login == 110925066:
            verificando_conta('117347586')
            sleep(2)
            verificando_data()
            if fatura == True:
                navegador.find_element(By.XPATH, Portal_map['buttons']["download"]["xpath"]).click() #clicando em ok para download
                sleep(7)
                arquivo_recente()
                extração()
                rename_arquivo()
                insert_MySQL()
                upload_drive(f"{pasta_downloads}/{ultimo_arquivo[1]}")
                remover_arquivo()
                sleep(2)
            reinciando()

        elif login == 109700244:
            verificando_conta('116120396')
            sleep(2)
            verificando_data()
            if fatura == True:
                navegador.find_element(By.XPATH, Portal_map['buttons']["download"]["xpath"]).click() #clicando em ok para download
                sleep(7)
                arquivo_recente()
                extração()
                rename_arquivo()
                insert_MySQL()
                upload_drive(f"{pasta_downloads}/{ultimo_arquivo[1]}")
                remover_arquivo()
                sleep(2)
            reinciando()

        #caso padrao de apenas uma fatura no login
        else:
            verificando_data() #chamando a função para verificar a data das faturas disponiveis
            if fatura == False: #se não estiver nenhuma do mes e ano atual disponivel vai voltar a controlar a aba de login e pular essa conta
                reinciando()
            else: #se tiver uma disponivel ele confirma cliando em ok e depois volta para a aba de login
                try:
                    navegador.find_element(By.XPATH, Portal_map['buttons']["download"]["xpath"]).click() #clicando em ok para download
                    sleep(7)
                    arquivo_recente()
                    extração()
                    rename_arquivo()
                    insert_MySQL()
                    upload_drive(f"{pasta_downloads}/{ultimo_arquivo[1]}")
                    remover_arquivo()
                    reinciando()
                except:
                    reinciando()

navegador.quit() #fechando o navegador depois de verificar todos os logins
db.close() #fechando o banco de dados 