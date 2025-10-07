from langchain_core.tools import tool
import logging
import requests

API_URL = "https://qnur3yjwqg.execute-api.eu-west-3.amazonaws.com"  
ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpZCI6ImZiZmVmYWVlMjcyZTQxNWNjMTBlNjgzNmFlNzhhZDllNTc4MWRlNGYiLCJqdGkiOiJmYmZlZmFlZTI3MmU0MTVjYzEwZTY4MzZhZTc4YWQ5ZTU3ODFkZTRmIiwiaXNzIjoiIiwiYXVkIjoib1NJR3JpcyIsInN1YiI6IjgiLCJ1c2VyaWQiOiI4IiwidXNlcm5hbWUiOiJhZG1pbnNlcmdpbyIsImVtYWlsIjoic2NhbWJlaXJvQG9zaWdyaXMuY29tIiwibm9tYnJlIjoiU2VyZ2lvIiwiYXBlbGxpZG8iOiJDYW1iZWlybyIsImV4cCI6MTc1OTg0MTA2OCwiaWF0IjoxNzU5ODM3NDY4LCJ0b2tlbl90eXBlIjoiYmVhcmVyIiwic2NvcGUiOiJpbnRlcm5hbF91c2VyIn0.RaLQQXnImsCLotzrm2UgKYzGx-ciOgpqGFxXq9QT8892TmewoAY1EojduUutLxR2skgJnlgRyMAyD8Hu-MPUgg9-nLVQqHrjtUEqUvR_rlN-RrUtmmIfuI0H2YGGdrWkWHzsR54xbCUOQFMqIvDko6O6hw2XvUQo2UqtN9Pf-rij6rHKm4L7GmzxKM8rdgIFgLCjYUIZP1qpr5zXSsoGuZ788oy4NbYjouZdtCnXcTqfTd-dfLc6E4Lw5tLmRvsrBmqu44vnvSE5Q2cr5Mv2QxoUasmrl6xj20Oio_7C94-_xxV7MFY872Fyp7aY5zfI9gH2Kmvgl5WE_lcZV0WF4g"

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
                print("⚠️ Error devuelto por la API:", json_resp["error"])
                return None
        return None
    except requests.RequestException as e:
        print(f"Error al conectar con el endpoint: {e}")
        return None

@tool("Comprobar_explotacion")    
def validar_explotacion(año: str, campaña: str) -> str:
    """Usa esta función para comprobar si existe la campaña en osigris, pasándole el año y el alias de la campaña
    Arguments:
    - año: Año de la campaña introducido por el usuario
    - campaña: Alias/nombre de la campaña introducido por el usuario
    """
    logging.info(f"--Start comprobar_explotacion tool with arguments: {año}, {campaña}")
    url = f"{API_URL}/osigrisapi/resource/season/list?&qg1[and]=year,alias&year[eq]={año}&alias[eq]={campaña}"
    return hacer_peticion_get(url)