from langchain_core.tools import tool
from app.interfaces.airtable import PostgresClient
import logging
import requests

API_URL = "https://qnur3yjwqg.execute-api.eu-west-3.amazonaws.com"  
ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpZCI6IjdlOGMxNWJhNGYyOTc2MmI0YmZlZjViOTM1ODVjYWY5NGRkZTExYTQiLCJqdGkiOiI3ZThjMTViYTRmMjk3NjJiNGJmZWY1YjkzNTg1Y2FmOTRkZGUxMWE0IiwiaXNzIjoiIiwiYXVkIjoib1NJR3JpcyIsInN1YiI6IjgiLCJ1c2VyaWQiOiI4IiwidXNlcm5hbWUiOiJhZG1pbnNlcmdpbyIsImVtYWlsIjoic2NhbWJlaXJvQG9zaWdyaXMuY29tIiwibm9tYnJlIjoiU2VyZ2lvIiwiYXBlbGxpZG8iOiJDYW1iZWlybyIsImV4cCI6MTc1OTkyMDA3MiwiaWF0IjoxNzU5OTE2NDcyLCJ0b2tlbl90eXBlIjoiYmVhcmVyIiwic2NvcGUiOiJpbnRlcm5hbF91c2VyIn0.QkIS32DSlk3-XDt6mkplxZ5AhqWXsnuBvTaBaYErqxZgtfZr7bFW4Cp-8r2Z26luylVf-cOzBBnl3Mw7AFcoLZb6PfCG5mmmReu_qOYT2dRM9K47poUq-rG8wp2QKFAhk1Es_2onS6jmTSMo3gllirDJ4tBG9LMhnz7YNpqO-5bAJLQ9D03OH84c5Nk_a8FKHlm_0rmiqMRNO3HW9VFcQM4JC3iexmPxm9tDWaIzYqJIIv7EhVGc9EnVHCF_NVFJMnDNDR5Q-xnvosC6sscT0ILvS_uaPv0tQd187nHXqlWqcRqDQFppFm81pX-IpYU8tPA-G6M-etu9CK8uFSAPdA"

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
                return "si"
            elif "error" in json_resp:
                logging.info("⚠️ Error devuelto por la API:", json_resp["error"])
                return "no"
        return "no"
    except requests.RequestException as e:
        logging.info(f"Error al conectar con el endpoint: {e}")
        return "no"

@tool("ComprobarExplotacion")    
def validar_explotacion(campaña: str, año: str) -> str:
    """Usa esta función para comprobar si existe la campaña en osigris, pasándole el año y el alias de la campaña
    Arguments:
    - año: Año de la campaña introducido por el usuario
    - campaña: Alias/nombre de la campaña introducido por el usuario
    """
    logging.info(f"--Start ComprobarExplotacion tool with arguments: {año}, {campaña}")
    url = f"{API_URL}/osigrisapi/resource/season/list?&qg1[and]=year,alias&year[eq]={año}&alias[eq]={campaña}"
    return hacer_peticion_get(url)

# @tool("ComprobarCultivo")    
# def validar_explotacion(cultivo: str) -> str:
#     """Usa esta función para comprobar si existe el cultivo en la campaña en osigris, pasándole el año y el alias de la campaña
#     Arguments:
#     - año: Año de la campaña introducido por el usuario
#     - campaña: Alias/nombre de la campaña introducido por el usuario
#     """
#     logging.info(f"--Start ComprobarCultivo tool with arguments: {cultivo}, {ID_CAMPAÑA}")
#     url = f"{API_URL}/osigrisapi/season/show/{ID_CAMPAÑA}/crop/list?qg1[and]=typecrop&typecrop[in]={cultivo}"
#     return hacer_peticion_get(url)