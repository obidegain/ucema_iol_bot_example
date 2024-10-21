import requests
import logging
import os

if not os.path.exists('logs'):
    os.makedirs('logs')

logger = logging.getLogger()

class APIError(Exception):
    def __init__(self, status_code, message="Error en la solicitud a la API"):
        self.status_code = status_code
        self.message = message
        super().__init__(f"{message}: {status_code}")


class InvertirOnlineAPI:
    def __init__(self, user, password):
        self.user = user
        self.access_token = None
        self.refresh_token = None
        self.MARKETS = ["bCBA", "nYSE", "nASDAQ", "aMEX", "bCS", "rOFX"]
        self.COUNTRIES = ["argentina", "estados_Unidos"]
        self.token_url = "https://api.invertironline.com/token"
        self.get_first_token(password)
        logger.info(f"BrokerAPI instanciada para el usuario {user}")

    def get_first_token(self, password):
        payload = f'username={self.user}&password={password}&grant_type=password'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        response = requests.post(self.token_url, headers=headers, data=payload)
        if response.status_code != 200:
            logger.error(f"Error al obtener el primer token: {response.status_code}")
            raise APIError(response.status_code, "Error al obtener el primer token")

        data_dict = response.json()
        self.access_token = data_dict.get('access_token')
        self.refresh_token = data_dict.get('refresh_token')

        if not self.access_token or not self.refresh_token:
            logger.error("No se pudo obtener el token de acceso o el token de refresco")
            raise ValueError("No se pudo obtener el token de acceso o el token de refresco")

        logger.info(f"Token obtenido correctamente para el usuario {self.user}")

    def refresh_token(self):
        payload = f'refresh_token={self.refresh_token}&grant_type=refresh_token'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        response = requests.post(self.token_url, headers=headers, data=payload)
        if response.status_code != 200:
            logger.error("Error al refrescar el token: %s", response.status_code)
            raise APIError(response.status_code, "Error al refrescar el token")

        data_dict = response.json()
        self.access_token = data_dict.get('access_token')
        self.refresh_token = data_dict.get('refresh_token')

        if not self.access_token or not self.refresh_token:
            logger.error("No se pudo refrescar el token de acceso o el token de refresco")
            raise ValueError("No se pudo refrescar el token de acceso o el token de refresco")

        logger.info("Token refrescado correctamente para el usuario %s", self.user)

    def request_with_token(self, url):
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }

        response = requests.get(url, headers=headers)

        # Si el token ha expirado (401 Unauthorized), refrescar el token y reintentar
        if response.status_code == 401:
            logger.warning("Token expirado, intentando refrescar el token...")
            self.refresh_token()
            headers['Authorization'] = f'Bearer {self.access_token}'
            response = requests.get(url, headers=headers)

        if response.status_code != 200:
            logger.error(f"Error en la solicitud a la API: {response.status_code}")
            raise APIError(response.status_code, "Error al solicitar datos")

        logger.info(f"Solicitud a la API completada exitosamente para la URL {url}")
        return response.json()

    def get_data_mep(self, symbol):
        url = f"https://api.invertironline.com/api/v2/Cotizaciones/MEP/{symbol}"
        logger.info(f"Solicitando datos MEP para el símbolo {symbol}")
        return self.request_with_token(url)

    def get_data_bcba(self, symbol):
        url = f"https://api.invertironline.com/api/v2/bCBA/Titulos/{symbol}/CotizacionDetalle"
        logger.info(f"Solicitando datos para el mercado bCBA el símbolo {symbol}")
        return self.request_with_token(url)

    def get_data_with_market_and_symbol(self, market, symbol):
        url = f"https://api.invertironline.com/api/v2/bCBA/Titulos/{symbol}/CotizacionDetalle"
        logger.info(f"Solicitando datos para el mercado {market} el símbolo {symbol}")
        return self.request_with_token(url)


    def get_data_from_country(self, country):
        url = f"https://api.invertironline.com/api/v2/{country}/Titulos/Cotizacion/Instrumentos"
        logger.info(f"Solicitando datos de todos los instrumendos de {country}")
        return self.request_with_token(url)