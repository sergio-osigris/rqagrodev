from langchain_core.tools import tool
from app.interfaces.airtable import PostgresClient
import logging
import requests

API_URL = "https://qnur3yjwqg.execute-api.eu-west-3.amazonaws.com"  
ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpZCI6IjViNDJiM2U3ODJlMzEwOGQzMzdkODBmYjk1NWIxMjU5MTg0YmQyMTMiLCJqdGkiOiI1YjQyYjNlNzgyZTMxMDhkMzM3ZDgwZmI5NTViMTI1OTE4NGJkMjEzIiwiaXNzIjoiIiwiYXVkIjoib1NJR3JpcyIsInN1YiI6IjgiLCJ1c2VyaWQiOiI4IiwidXNlcm5hbWUiOiJhZG1pbnNlcmdpbyIsImVtYWlsIjoic2NhbWJlaXJvQG9zaWdyaXMuY29tIiwibm9tYnJlIjoiU2VyZ2lvIiwiYXBlbGxpZG8iOiJDYW1iZWlybyIsImV4cCI6MTc1OTkxNDk3OCwiaWF0IjoxNzU5OTExMzc4LCJ0b2tlbl90eXBlIjoiYmVhcmVyIiwic2NvcGUiOiJpbnRlcm5hbF91c2VyIn0.UrB-gc0TisCvIswQdP4YUF59JoxjbHtEJVo-iESVgEJmHFS993t70_yJqeR4yazeZBUPmxEoKE-hXxvRi6sV7oRIZnPjP9al4OiN_RSyntwUrNWZ7CxPleIAfK8aQ3-XdSEJSjMYcYVOf9is7rcK7aRsSq4pnd-ycYsm29ghUudL2fOXqLTeR3pFA5sZZnCb-ygcqe1nKkk3z1BHc8xRS0ndhKQVekSkI8IcyNNwrnuwgd3qWvzwnZ19jor1PukW2lYcYOA8le4qkRCJAoPMm2s8CojYJ1HF_f7QSgDHK73RwKqu_tEwrXQeXWKbd2pm49T72JDeNUMy7a88NHLHVg"

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
def validar_explotacion(campaña: str, año: str, cultivo: str) -> tuple[bool, str]:
    """Usa esta función para comprobar si existe la campaña en osigris, pasándole el año y el alias de la campaña. 
    Si existe, se comprueba que el cultivo pertenezca a dicha campaña
    Arguments:
    - año: Año de la campaña introducido por el usuario
    - campaña: Alias/nombre de la campaña introducido por el usuario
    - cultivo: Nombre del cultivo introducido por el usuario
    """
    logging.info(f"--Start ComprobarExplotacion tool with arguments: {año}, {campaña}")
    url = f"{API_URL}/osigrisapi/resource/season/list?&qg1[and]=year,alias&year[eq]={año}&alias[eq]={campaña}"
    valido, datos = hacer_peticion_get(url)
    if valido:
        id_campaña = datos[0]["info"]["id"]
        return valido, f"Existe ese año de campaña con el nombre indicado correctamente. {id_campaña}"
    else:
        return valido, "No existe ese año de campaña con el nombre indicado."