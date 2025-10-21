from langchain_core.tools import tool
from app.interfaces.airtable import PostgresClient
import logging
import requests

API_URL = "https://qnur3yjwqg.execute-api.eu-west-3.amazonaws.com"  
ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpZCI6IjJkYjg3NWU0NDQ5YjdlN2Y3YWUwYWY5YmE1NjIxMzQzOGJhYWFlMjQiLCJqdGkiOiIyZGI4NzVlNDQ0OWI3ZTdmN2FlMGFmOWJhNTYyMTM0MzhiYWFhZTI0IiwiaXNzIjoiIiwiYXVkIjoib1NJR3JpcyIsInN1YiI6IjgiLCJ1c2VyaWQiOiI4IiwidXNlcm5hbWUiOiJhZG1pbnNlcmdpbyIsImVtYWlsIjoic2NhbWJlaXJvQG9zaWdyaXMuY29tIiwibm9tYnJlIjoiU2VyZ2lvIiwiYXBlbGxpZG8iOiJDYW1iZWlybyIsImV4cCI6MTc2MTA0MzgxMSwiaWF0IjoxNzYxMDQwMjExLCJ0b2tlbl90eXBlIjoiYmVhcmVyIiwic2NvcGUiOiJpbnRlcm5hbF91c2VyIn0.gpUljzkKwPKkNfaUeTHmeYgXUjrc1z6ihWMKZYJ1zzuU2MSaOBSEeakMupJFrofFK8IQvwsgIXezzS6Qz-Uyu5bO6-zcwIfaeP9n1k1GCcJJZGeih9B2-_oWVKObRZqHEuyGD6aWpXFrYd1Dhk2BcFR3fUpThKQBsmXoC6WSIeAd78IdvT0XEpAUiADyT01pU0t5oOFNQxAa5FXfjPtCtCx-9ELbtZvq5BwPOSQ7UMtlYHTcbp-Q52TJbstJseA-Vdmdhmj_OOi2yBPS-oo-s6iGWTxj57byy0pXYVO3KAaj3tnoWO9x-H9GT4aAPlMi1ftwYgteUKxzJhamjTZq2Q"
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