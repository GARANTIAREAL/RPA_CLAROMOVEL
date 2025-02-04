from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from time import sleep
import pyautogui
import os
import io
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')

print(TOKEN)

SCOPES = ["https://www.googleapis.com/auth/drive"] #escopo de permissão que o codigo tem sobre o drive
SERVICE_ACCOUNT_FILE = TOKEN #token para acesso drive
SHARED_DRIVE_ID = '1CDjMaelp9XPOYCGrOX96Yn9uz5JorkgT' #ID da pasta no drive para armazenar as NFs PRECISA SER TROCADO A CADA ANO!!!!



#configurando o navegador
#servico = Service(ChromeDriverManager().install()) #instalando o driver atual do chrome de forma automatica
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
chrome_options.add_argument('--ignore-certificate-errors') 
chrome_options.add_argument('--ignore-ssl-errors')  
navegador = webdriver.Chrome(options=chrome_options)

valor_total = '10.100,25'
valor_total = valor_total.replace('.', '')
valor_total = valor_total.replace(',', '.')

juros = '50,55'
juros = juros.replace(',', '.')

mes_nota = 9
ano_nota = int(2025)
dia_nota = str('2')

referencia = '8'

calendario = [(1, "jan"), (2, "fev"), (3, "mar"), (4, "abr"), (5, "mai"), (6, "jun"), (7, "jul"), (8, "ago"), (9, "set"), (10, "out"), (11, "nov"), (12, "dez")]
cores_validas = [("rgba(226, 226, 226, 1)"), ("rgba(255, 136, 136, 1)"), ("rgba(225, 68, 56, 1)")]

pasta_downloads = os.path.join(os.path.expanduser("~"), "Downloads") #declarando automaticamente o caminho até a pasta de downloads de qualquer maquina 



navegador.get("https://sd.grupogr.com.br/HomePage.do?view_type=my_view")

sleep(10)

navegador.find_element(By.XPATH, '//*[@id="username"]').send_keys('Jovem.aprendiz')
navegador.find_element(By.XPATH, '//*[@id="password"]').send_keys('J0v3mapr3nd1z200%')
pyautogui.press('enter')

navegador.find_element(By.XPATH, '//*[@id="dd-searchbox"]').click()
sleep(3)
pyautogui.write('TesteRPA')
sleep(3)
pyautogui.press('enter')
sleep(6)
navegador.find_element(By.XPATH, '//*[@id="request_kanban_div"]/div/div/div[2]/div[1]/span/span/span/a').click()
sleep(3)
iframe = navegador.find_element(By.CSS_SELECTOR, "#wo-details-frame-frame") #alterando para o frame onde estão os campos 
navegador.switch_to.frame(iframe)
sleep(3)

#preenchendo o campo de valor total
navegador.find_element(By.XPATH, '//*[@id="propertyDetailForm"]/div[1]/div[4]/div[1]/div[2]/div[3]/div/p').click()
campo_valor = navegador.find_element(By.XPATH, '//*[@id="udf_decimal_9017_control"]/input')
value_total = campo_valor.get_attribute("value")
if value_total != valor_total:
    for b in range(0, 12):
        pyautogui.press('backspace')
    pyautogui.write(valor_total)
    pyautogui.press('enter')
    
sleep(3)

#preenchendo o campo de juros
navegador.find_element(By.XPATH, '//*[@id="propertyDetailForm"]/div[1]/div[4]/div[1]/div[2]/div[4]/div/p').click()
campo_juros = navegador.find_element(By.XPATH, '//*[@id="udf_decimal_10502_control"]/input')
value_juros = campo_juros.get_attribute("value")
if value_juros != juros:
    for b in range(0, 9):
        pyautogui.press('backspace')
    pyautogui.write(juros)
    pyautogui.press('enter')

#preenchendo o campo de competencia
navegador.find_element(By.XPATH, '//*[@id="propertyDetailForm"]/div[1]/div[4]/div[1]/div[2]/div[8]/div/p').click()
pyautogui.write(referencia)
pyautogui.press('enter')

sleep(4)

#preenchendo o campo de data de emissao
navegador.find_element(By.XPATH, '//*[@id="propertyDetailForm"]/div[1]/div[4]/div[1]/div[2]/div[2]/div/p').click()


campo_mes = str((navegador.find_element(By.CSS_SELECTOR, '#udf_date_11102_IN_calendar_parent > div.zdatetimepicker__monthcontainer.zdatetimepicker__days > div.zdatetimepicker__navbar > div.zdatetimepicker__monthyearnav.zh-cursorpointer > span.zdatetimepicker__monthnav').get_attribute("textContent")).strip(' '))
sleep(2)
for m in calendario:
        if m[0] == mes_nota:
            mes_nota = str(m[1])
            print(mes_nota)
while campo_mes != mes_nota:
            navegador.find_element(By.XPATH, '//*[@id="udf_date_11102_IN_calendar_parent-right-month-0"]').click()
            campo_mes = str((navegador.find_element(By.CSS_SELECTOR, '#udf_date_11102_IN_calendar_parent > div.zdatetimepicker__monthcontainer.zdatetimepicker__days > div.zdatetimepicker__navbar > div.zdatetimepicker__monthyearnav.zh-cursorpointer > span.zdatetimepicker__monthnav').get_attribute("textContent")).strip(' '))
            sleep(1)


campo_ano = str(navegador.find_element(By.CSS_SELECTOR, '#udf_date_11102_IN_calendar_parent > div.zdatetimepicker__monthcontainer.zdatetimepicker__days > div.zdatetimepicker__navbar > div.zdatetimepicker__monthyearnav.zh-cursorpointer > span.zdatetimepicker__yearnav').get_attribute("textContent")).strip(' ')
campo_ano = int(campo_ano)

while campo_ano != ano_nota: 
    if campo_ano < ano_nota:
        navegador.find_element(By.XPATH, '//*[@id="udf_date_11102_IN_calendar_parent-right-year"]').click()
        campo_ano = str(navegador.find_element(By.CSS_SELECTOR, '#udf_date_11102_IN_calendar_parent > div.zdatetimepicker__monthcontainer.zdatetimepicker__days > div.zdatetimepicker__navbar > div.zdatetimepicker__monthyearnav.zh-cursorpointer > span.zdatetimepicker__yearnav').get_attribute("textContent")).strip(' ')
        campo_ano = int(campo_ano)
    else:
        navegador.find_element(By.XPATH, '//*[@id="udf_date_11102_IN_calendar_parent-left-year"]').click()
        campo_ano = str(navegador.find_element(By.CSS_SELECTOR, '#udf_date_11102_IN_calendar_parent > div.zdatetimepicker__monthcontainer.zdatetimepicker__days > div.zdatetimepicker__navbar > div.zdatetimepicker__monthyearnav.zh-cursorpointer > span.zdatetimepicker__yearnav').get_attribute("textContent")).strip(' ')
        campo_ano = int(campo_ano)





dia_selecionado = False

for l in range (1, 7):
    if dia_selecionado == True:
        break
    for c in range (1, 8):
        campo_dia = (navegador.find_element(By.XPATH, f'//*[@id="udf_date_11102_IN_calendar_parent"]/div[1]/div[2]/table/tbody/tr[{l}]/td[{c}]'))
        dia = str(navegador.find_element(By.XPATH, f'//*[@id="udf_date_11102_IN_calendar_parent"]/div[1]/div[2]/table/tbody/tr[{l}]/td[{c}]').get_attribute("textContent").strip(' '))
        color = campo_dia.value_of_css_property("color")
        if dia == dia_nota and color in cores_validas:
            navegador.find_element(By.XPATH, f'//*[@id="udf_date_11102_IN_calendar_parent"]/div[1]/div[2]/table/tbody/tr[{l}]/td[{c}]').click()
            dia_selecionado = True
            navegador.find_element(By.XPATH, '//*[@id="udf_date_11102_IN_calendar_parent"]/div[3]/div[3]/button[2]').click()
            #confirmando os campos
            sleep(3)
            navegador.find_element(By.XPATH, '/html/body/div[4]/div/div[1]/div/div[2]/div[3]/div[1]/div[1]/div[3]/div[2]/div/div/div[1]/div[1]/div[2]/form/div[1]/div[4]/div[1]/div[2]/div[2]/div/div/div[2]/button[1]').click()
            sleep(7)
            break






#preenchendo o campo de data de vencimento 
navegador.find_element(By.XPATH, '//*[@id="propertyDetailForm"]/div[1]/div[4]/div[1]/div[2]/div[7]/div/p').click()

campo_mes = str((navegador.find_element(By.CSS_SELECTOR, '#udf_date_9008_IN_calendar_parent > div.zdatetimepicker__monthcontainer.zdatetimepicker__days > div.zdatetimepicker__navbar > div.zdatetimepicker__monthyearnav.zh-cursorpointer > span.zdatetimepicker__monthnav').get_attribute("textContent")).strip(' '))

while campo_mes != mes_nota:
            navegador.find_element(By.XPATH, '//*[@id="udf_date_9008_IN_calendar_parent-right-month-0"]').click()
            campo_mes = str((navegador.find_element(By.CSS_SELECTOR, '#udf_date_9008_IN_calendar_parent > div.zdatetimepicker__monthcontainer.zdatetimepicker__days > div.zdatetimepicker__navbar > div.zdatetimepicker__monthyearnav.zh-cursorpointer > span.zdatetimepicker__monthnav').get_attribute("textContent")).strip(' '))
            sleep(1)


campo_ano = str(navegador.find_element(By.CSS_SELECTOR, '#udf_date_9008_IN_calendar_parent > div.zdatetimepicker__monthcontainer.zdatetimepicker__days > div.zdatetimepicker__navbar > div.zdatetimepicker__monthyearnav.zh-cursorpointer > span.zdatetimepicker__yearnav').get_attribute("textContent")).strip(' ')
campo_ano = int(campo_ano)

while campo_ano != ano_nota: 
    if campo_ano < ano_nota:
        navegador.find_element(By.XPATH, '//*[@id="udf_date_9008_IN_calendar_parent-right-year"]').click()
        campo_ano = str(navegador.find_element(By.CSS_SELECTOR, '#udf_date_9008_IN_calendar_parent > div.zdatetimepicker__monthcontainer.zdatetimepicker__days > div.zdatetimepicker__navbar > div.zdatetimepicker__monthyearnav.zh-cursorpointer > span.zdatetimepicker__yearnav').get_attribute("textContent")).strip(' ')
        campo_ano = int(campo_ano)
    else:
        navegador.find_element(By.XPATH, '//*[@id="udf_date_9008_IN_calendar_parent-left-year"]').click()
        campo_ano = str(navegador.find_element(By.CSS_SELECTOR, '#udf_date_9008_IN_calendar_parent > div.zdatetimepicker__monthcontainer.zdatetimepicker__days > div.zdatetimepicker__navbar > div.zdatetimepicker__monthyearnav.zh-cursorpointer > span.zdatetimepicker__yearnav').get_attribute("textContent")).strip(' ')
        campo_ano = int(campo_ano)



dia_selecionado = False

for l in range (1, 7):
    if dia_selecionado == True:
        break
    for c in range (1, 8):
        dia = str(navegador.find_element(By.XPATH, f'//*[@id="udf_date_9008_IN_calendar_parent"]/div[1]/div[2]/table/tbody/tr[{l}]/td[{c}]').get_attribute("textContent").strip(' '))
        if dia == dia_nota:
            navegador.find_element(By.XPATH, f'//*[@id="udf_date_9008_IN_calendar_parent"]/div[1]/div[2]/table/tbody/tr[{l}]/td[{c}]').click()
            sleep(2)
            dia_selecionado = True
            navegador.find_element(By.XPATH, '//*[@id="udf_date_9008_IN_calendar_parent"]/div[3]/div[3]/button[2]').click()
            #confirmando os campos
            sleep(3)
            navegador.find_element(By.XPATH, '/html/body/div[4]/div/div[1]/div/div[2]/div[3]/div[1]/div[1]/div[3]/div[2]/div/div/div[1]/div[1]/div[2]/form/div[1]/div[4]/div[1]/div[2]/div[7]/div/div/div[2]/button[1]/span').click()
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

if __name__ == "__main__":
    download_file(real_file_id="16fWmAtTDrcofbdnye9xt6b9ypOIVryrs")


def download_file_os(real_file_id, save_path): 
    if file is not None:
        # Write downloaded content to the specified save path
        with open(save_path, 'wb') as f:
            f.write(file.getvalue())
        print(f"File downloaded successfully and saved to: {save_path}")

# Example usage in the main block
if __name__ == "__main__":
    file_id = "1nxDjn7cvy90v2pnrJ0e10o3t9bhhcwYM"
    save_location = f"{pasta_downloads}/{file}"  # Replace with your desired path
    download_file_os(file_id, save_location)


os.rename(f'{save_location}', f'{pasta_downloads}/Claro GR.pdf')



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

if os.path.exists(pdf):
    os.remove(pdf)