from googleapiclient.discovery import build
from google.oauth2 import service_account
import os

SCOPES = ["https://www.googleapis.com/auth/drive"]
SERVICE_ACCOUNT_FILE = 'token.json'
SHARED_DRIVE_ID = '1CDjMaelp9XPOYCGrOX96Yn9uz5JorkgT'

def autenticar():
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return creds

def check_file_exists(file_name):
    creds = autenticar()
    service = build('drive', 'v3', credentials=creds)

    print(file_name)

    # Busca por arquivos com nome correspondente na pasta pai
    response = service.files().list(
        includeItemsFromAllDrives=True,
        supportsAllDrives=True, #linha para permitir o codigo acessar pastas compartilhadas no drive
        q=f"name = '{file_name}' and parents = '{SHARED_DRIVE_ID}'"
        ).execute()
    
    print(f"name = '{file_name}' and parents = '{SHARED_DRIVE_ID}'")
    print(response)

    # Verifica se algum arquivo foi encontrado
    if response['files']:
        print('o arquivo está no drive')
        return True  # O arquivo existe no Drive
    else:
        print('o arquivo não está no drive')
        return False  # O arquivo não existe no Drive

def upload_drive(file_path):
    creds = autenticar()
    service = build('drive', 'v3', credentials=creds)
    
    global file_name
    file_name = os.path.basename(f'116120396_Claro_GR_Seguranca_ES_25_05_2024.pdf')

    # Verifica se o arquivo já existe no Drive
    if check_file_exists(file_name):
        print(f"O arquivo '{file_name}' já existe no Drive. Pulando envio.")
        return

    file_metadata = {
        'name' : 'NOTA TESTE',
        'parents' : [SHARED_DRIVE_ID]
    }
    
    file = service.files().create(
        supportsAllDrives=True, #linha para permitir o codigo acessar pastas compartilhadas no drive
        body=file_metadata,
        media_body=file_path
    ).execute()

pasta_downloads = os.path.join(os.path.expanduser("~"), "Downloads")
arquivo = "111976907_24-04-2024_4_2024_16.pdf"



upload_drive(f"{pasta_downloads}/{arquivo}")