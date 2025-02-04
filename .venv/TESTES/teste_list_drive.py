from googleapiclient.discovery import build
from google.oauth2 import service_account

SCOPES = ["https://www.googleapis.com/auth/drive"] #escopo de permissão que o codigo tem sobre o drive
SERVICE_ACCOUNT_FILE = 'CHAVES/token.json' #token para acesso drive
SHARED_DRIVE_ID = '1CDjMaelp9XPOYCGrOX96Yn9uz5JorkgT' #ID da pasta no drive para armazenar as NFs PRECISA SER TROCADO A CADA ANO!!!!

def autenticar():  #autenticando as credenciais da API do drive
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return creds

def list_all_files():
    creds = autenticar()
    service = build('drive', 'v3', credentials=creds)

    response = service.files().list(
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
        corpora="drive",
        driveId= f'1j6mXBi6KvynoG1p41Rd-aJGgX00Z0S_v'
    ).execute()

    print(response)
    

def check_file_exists(): #função para checar se a NF já está na pasta do drive
    creds = autenticar()
    service = build('drive', 'v3', credentials=creds)
    page_token = None

    # Busca por arquivos com nome correspondente na pasta pai
    response = service.files().list(
        supportsAllDrives=True, #parametro para incluir drivers compartilhadosq="mimeType='image/jpeg'",
        includeItemsFromAllDrives=True,
        fields="nextPageToken, files(id, name)",
        pageToken=page_token,
        q=f"name = '111976907_Claro_GR_Servico_SP_24-06-2024_ref-6.pdf' and parents = '{SHARED_DRIVE_ID}'"
    ).execute()

    # Verifica se algum arquivo foi encontrado
    if response['files']:
        return True  # O arquivo existe no Drive
    else:
        return False  # O arquivo não existe no Drive
    
    
check_file_exists()