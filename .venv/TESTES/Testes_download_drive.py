import io
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
import os

SCOPES = ["https://www.googleapis.com/auth/drive"] #escopo de permissão que o codigo tem sobre o drive
SERVICE_ACCOUNT_FILE = 'RPA_claro/CHAVES/token.json' #token para acesso drive
SHARED_DRIVE_ID = '1CDjMaelp9XPOYCGrOX96Yn9uz5JorkgT' #ID da pasta no drive para armazenar as NFs PRECISA SER TROCADO A CADA ANO!!!!

pasta_downloads = os.path.join(os.path.expanduser("~"), "Downloads") #declarando automaticamente o caminho até a pasta de downloads de qualquer maquina 


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
    download_file(real_file_id="1kFpbwCW8B1T2YuaMQvYPyzbSZq8E-Dd1")


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


os.rename(f'{save_location}', f'{pasta_downloads}/Claro GR')