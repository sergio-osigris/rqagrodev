from langchain_core.tools import tool
from app.interfaces.airtable import PostgresClient
import logging
import requests

API_URL = "https://qnur3yjwqg.execute-api.eu-west-3.amazonaws.com"  
ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpZCI6IjUwNTE4ODQzZTA0N2JkNzM5MzA3MGY2MTJlYzU3N2YyYTM2NWI3YzUiLCJqdGkiOiI1MDUxODg0M2UwNDdiZDczOTMwNzBmNjEyZWM1NzdmMmEzNjViN2M1IiwiaXNzIjoiIiwiYXVkIjoib1NJR3JpcyIsInN1YiI6IjgiLCJ1c2VyaWQiOiI4IiwidXNlcm5hbWUiOiJhZG1pbnNlcmdpbyIsImVtYWlsIjoic2NhbWJlaXJvQG9zaWdyaXMuY29tIiwibm9tYnJlIjoiU2VyZ2lvIiwiYXBlbGxpZG8iOiJDYW1iZWlybyIsImV4cCI6MTc1OTg2MTUyNiwiaWF0IjoxNzU5ODU3OTI2LCJ0b2tlbl90eXBlIjoiYmVhcmVyIiwic2NvcGUiOiJpbnRlcm5hbF91c2VyIn0.N2ly0hUKKaCq59ebCMbQZ4v0hgoZmMQsCz920ev87f06iS450PzYlbjON9aAC9SFOb6sjAN63GTqbc3_pPbGlJT7vzSJNkRJfDo83sYQjx_aW-Ex2a_BtFvGVPsNALfRz2YqCU0WBa3XI4Mj0HKybsbtTAhRcaicLW7doQMqSlCcgxncooq912IMcVrkeVOZm1MWynhklLH8O0Ce8xJ_LGoKCWA_t8VI9HqM2uz30sUOWVfuHFyNm7XKlP7P-t4my8LkGZEsXXTLl_xqGStelLnABUialhcPvdH0JUzQaip4PIubm8JH0yOdSjgn_59tCmEuUP571IlLiA3o0gOUWQ"

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
 
def hacer_peticion_get_test(año, campaña) -> str:
    return "si" if año == "2025" and campaña == "prueba" else "no"

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
    # return hacer_peticion_get(año, campaña)