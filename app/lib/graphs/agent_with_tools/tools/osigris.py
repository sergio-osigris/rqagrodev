from langchain_core.tools import tool
from app.interfaces.airtable import PostgresClient
import logging
import requests

API_URL = "https://qnur3yjwqg.execute-api.eu-west-3.amazonaws.com"  
ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpZCI6IjliYWFiMzQ1MjdhYzVlMTRhYmJkYmRhNWQwMDc1MjA5NjgyNDc1NDAiLCJqdGkiOiI5YmFhYjM0NTI3YWM1ZTE0YWJiZGJkYTVkMDA3NTIwOTY4MjQ3NTQwIiwiaXNzIjoiIiwiYXVkIjoib1NJR3JpcyIsInN1YiI6IjExNjEyIiwidXNlcmlkIjoiMTE2MTIiLCJ1c2VybmFtZSI6ImFkbWluc2VyZ2lvIiwiZW1haWwiOiJzY2FtYmVpcm9Ab3NpZ3Jpcy5jb20iLCJub21icmUiOiJTZXJnaW8xIiwiYXBlbGxpZG8iOiJDYW1iZWlybyBSaXZlaXJvIiwiZXhwIjoxNzYxMDQzMjc4LCJpYXQiOjE3NjEwMzk2NzgsInRva2VuX3R5cGUiOiJiZWFyZXIiLCJzY29wZSI6ImludGVybmFsX3VzZXIifQ.RMRXlHZ99o-A1pxQOs8fiT7KnALg-6_Ze-BeF8cvW4ouzIWXQNgZA1XIywQBpdPNZ2fx3XDQo_hdNxRXIC8V_2vhPD_iort56v-MdNsHSbsEc6PdEYD7Rd53iiAGNm3V_7cdHGGdRRRbZm_kzUBHheBd57mQrPxaQeSD1vsQeMzZA0bmZBiyQ3SGqrLsAU1WINswUGlC34z0PnHSoiUw4oPO918yeWSNGYZS-Y0e5BadupqZQdqy7kyzH2DIQihU2cmb7dbYsT509QNJYwW-nxI8ywxEcJnfr8roppO4rAtpunZsu4j2BPmWflafToLuAtDLa-YqItCiLqcUXgKPPA"
ID_CAMPAÑA = None
SIGPACS_ID=None

def hacer_peticion_get(url) -> str:
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Accept": "application/json"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            json_resp = resp.json()
            
            # Validar que tenga 'data' y que no haya 'error'
            if "data" in json_resp and json_resp["data"]:
                return "si", json_resp["data"]
            elif "error" in json_resp:
                logging.info("⚠️ Error devuelto por la API:", json_resp["error"])
                return "no", None
        return "no", None
    except requests.RequestException as e:
        logging.info(f"Error al conectar con el endpoint: {e}")
        return "no", None

@tool("ComprobarExplotacion")    
def validar_explotacion(campaña: str, año: str) -> str:
    """Usa esta función para comprobar si existe la campaña en osigris, pasándole el año y el alias de la campaña
    Arguments:
    - año: Año de la campaña introducido por el usuario
    - campaña: Alias/nombre de la campaña introducido por el usuario
    """
    logging.info(f"--Start ComprobarExplotacion tool with arguments: {año}, {campaña}")
    url = f"{API_URL}/osigrisapi/resource/season/list?&qg1[and]=year,alias&year[eq]={año}&alias[eq]={campaña}"
    valido, datos = hacer_peticion_get(url)
    if valido=="si":
        global ID_CAMPAÑA
        ID_CAMPAÑA=datos[0]["info"]["id"]
    return valido

@tool("ComprobarCultivo")    
def validar_cultivo(cultivo: str) -> str:
    """Usa esta función para comprobar si existe el cultivo en la campaña en osigris, pasándole el nombre del cultivo y el 
    ID de la campaña
    Arguments:
    - cultivo: Cultivo introducido por el usuario
    - id_campaña: Alias/nombre de la campaña obtenido en validar_explotacion
    """
    global ID_CAMPAÑA
    logging.info(f"--Start ComprobarCultivo tool with arguments: {cultivo}, {ID_CAMPAÑA}")
    url = f"{API_URL}/osigrisapi/season/show/{ID_CAMPAÑA}/crop/list?qg1[and]=typecrop&typecrop[in]={cultivo}"
    valido, datos = hacer_peticion_get(url)
    if valido=="si":
        global SIGPACS_ID
        SIGPACS_ID=[item["id"] for item in datos[0]["sigpac"]]
    return valido