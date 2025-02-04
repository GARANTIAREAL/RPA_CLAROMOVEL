import mysql.connector
from dotenv import load_dotenv
import os

data = str(input('digite a data'))

load_dotenv(override=True)

DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB = os.getenv('DB')

db = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD, 
    database=DB)

cursor = db.cursor()

nome_tabela = 'Mes' +  '_' + str(data)

consulta = f"SELECT * FROM {nome_tabela}" 
cursor.execute(consulta)

for linha in cursor.fetchall():
    # Extrair valores das colunas
    id_lancamento = linha[0]
    conta = linha[1]
    print(conta)
    print(type(conta))
    nome = linha[2]
    valor_total = linha[3]
    juros = linha[4]
    data_vencimento = linha[5]
    referencia = linha[6]
    data_emissao = linha[7]
    id_drive = linha[8]

    cursor.execute(f"SELECT valor FROM Ultimos_Valores WHERE conta = {conta}")
    for linha in cursor.fetchall():
        ultimo_valor = linha[0]
        print(ultimo_valor)