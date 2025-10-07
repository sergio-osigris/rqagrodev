from langchain_core.tools import tool
from app.interfaces.airtable import PostgresClient
import logging
import requests

API_URL = "https://qnur3yjwqg.execute-api.eu-west-3.amazonaws.com"  
ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpZCI6ImQzZjg5MzU0YmExZDNhMDYwMTFjZWFiZTlkMWUzNTkxZDg2ZDMxYTYiLCJqdGkiOiJkM2Y4OTM1NGJhMWQzYTA2MDExY2VhYmU5ZDFlMzU5MWQ4NmQzMWE2IiwiaXNzIjoiIiwiYXVkIjoib1NJR3JpcyIsInN1YiI6IjgiLCJ1c2VyaWQiOiI4IiwidXNlcm5hbWUiOiJhZG1pbnNlcmdpbyIsImVtYWlsIjoic2NhbWJlaXJvQG9zaWdyaXMuY29tIiwibm9tYnJlIjoiU2VyZ2lvIiwiYXBlbGxpZG8iOiJDYW1iZWlybyIsImV4cCI6MTc1OTg1MDg1NiwiaWF0IjoxNzU5ODQ3MjU2LCJ0b2tlbl90eXBlIjoiYmVhcmVyIiwic2NvcGUiOiJpbnRlcm5hbF91c2VyIn0.UsCp55gDnQ1CUAr6jrAntyNL92-Ct2m_RiBnwrkJlyK4dUyPEh8SlH1fXb2wlCEGetlbiCjlufO9w8SWRHbfA7rypLrh-etGK_rTi0DG1LW6HY_npzoav2O7RmCbmJD0o9XgUvuvmEWEGww8-nQwAVRkSGiUkqiZm1-1OJiyxSx6K1l3O6bITrwdSLLuemJTEK_MgKuviCCVoSV7IITzpWPnv5gd2Yr3UzlBArrEwokX-L55oTAYVx4hdDZGCHSPDunkELlU_4qSjrjjfSRcBDm6tZashlZWBKhRSKMgM21N2zbNlZqTfJLhILv-HcQV3BKG1hsW83e2eg0dL268Ng"

def hacer_peticion_get(url):
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
                return json_resp["data"]
            elif "error" in json_resp:
                logging.info("⚠️ Error devuelto por la API:", json_resp["error"])
                return None
        return None
    except requests.RequestException as e:
        logging.info(f"Error al conectar con el endpoint: {e}")
        return None

@tool("Comprobar_explotacion")    
async def validar_explotacion(campaña: str, año: str) -> str:
    """Usa esta función para comprobar si existe la campaña en osigris, pasándole el año y el alias de la campaña
    Arguments:
    - año: Año de la campaña introducido por el usuario
    - campaña: Alias/nombre de la campaña introducido por el usuario
    """
    logging.info(f"--Start comprobar_explotacion tool with arguments: {año}, {campaña}")
    url = f"{API_URL}/osigrisapi/resource/season/list?&qg1[and]=year,alias&year[eq]={año}&alias[eq]={campaña}"
    return hacer_peticion_get(url)