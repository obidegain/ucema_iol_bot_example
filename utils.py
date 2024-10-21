import requests
import json
import csv
from datetime import date

class APIError(Exception):
    def __init__(self, status_code, message="Error en la solicitud a la API"):
        self.status_code = status_code
        self.message = message
        super().__init__(f"{message}: {status_code}")


def get_first_token(user, password):
    url = "https://api.invertironline.com/token"

    payload = f'username={user}&password={password}&grant_type=password'
    headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code != 200:
        raise APIError(response.status_code, "Error al obtener el primer token")

    data_dict = response.json()
    access_token = data_dict.get('access_token', None)
    refresh_token = data_dict.get('refresh_token', None)

    if not access_token or not refresh_token:
        raise ValueError("No se pudo obtener el token de acceso o el token de refresco")

    return access_token, refresh_token


def refresh_token(refresh_token):
    url = "https://api.invertironline.com/token"
    payload = f'refresh_token={refresh_token}&grant_type=refresh_token'
    headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    if response.status_code != 200:
        raise APIError(response.status_code, "Error al refrescar el token")


    data_dict = response.json()
    access_token = data_dict.get('access_token')
    new_refresh_token = data_dict.get('refresh_token')

    if not access_token or not new_refresh_token:
        raise ValueError("No se pudo refrescar el token de acceso o el token de refresco")

    return access_token, new_refresh_token


def request_with_token(url, access_token, refresh_token=None):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }

    response = requests.get(url, headers=headers)

    # Si el token ha expirado (suponemos que un 401 indica token expirado)
    if response.status_code == 401 and refresh_token:
        print("Token expirado, refrescando...")
        new_access_token, new_refresh_token = refresh_token(refresh_token)
        headers['Authorization'] = f'Bearer {new_access_token}'
        response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise APIError(response.status_code, "Error al solicitar datos")

    return response.json()


def get_data(access_token, symbol):
    url = f"https://api.invertironline.com/api/v2/Cotizaciones/MEP/{symbol}"
    headers = {
      'Authorization': f'Bearer {access_token}'
    }

    response = requests.request("GET", url, headers=headers)

    return response.text


def get_data_from_symbol(access_token, symbol):
    url = f"https://api.invertironline.com/api/v2/bCBA/Titulos/{symbol}/CotizacionDetalle?api_key={access_token}"

    headers = {
      "Accept": "application/json",
      "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)

    data = response.json()
    return data

def guardar_datos_en_csv(access_token, symbol):
    current_date = date.today().strftime("%Y-%m-%d")

    file_name = f"datos_{symbol}_{current_date}.csv"

    data = get_data_from_symbol(access_token, symbol)

    # Verificar si el archivo existe
    opening_mode = 'a'  # Modo de apertura por defecto: agregar ('a')
    try:
        with open(file_name, 'r') as file:
          # Si el archivo no está vacío, asumimos que tiene cabecera
          if file.read():
            opening_mode = 'a'  # Agregar datos sin cabecera
          else:
            opening_mode = 'w'  # Escribir cabecera y datos
    except FileNotFoundError:
        opening_mode = 'w'  # El archivo no existe, crear y escribir cabecera y datos

    with open(file_name, opening_mode, newline='') as file_csv:
        writer = csv.writer(file_csv)

        if opening_mode == 'w':
          writer.writerow(data.keys())
        writer.writerow(data.values())

    print(f"Los datos del símbolo {symbol} se han guardado en el archivo {file_name}")


def read_bbdd_offline():
    import sqlite3
    import pandas as pd

    conn = sqlite3.connect('market_data.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM market_data")

    column_names = [description[0] for description in cur.description]
    data = cur.fetchall()
    df = pd.DataFrame(data, columns=column_names)

    conn.close()

    return df