from langchain_core.tools import tool
from app.interfaces.airtable import PostgresClient
import logging
import requests

API_URL = "https://qnur3yjwqg.execute-api.eu-west-3.amazonaws.com"  
ACCESS_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpZCI6ImVhYWY3NDJjZjQ4MjUwNTgwZmRiZWU1N2Y0YTA5ZTY1NDkyZGNlODEiLCJqdGkiOiJlYWFmNzQyY2Y0ODI1MDU4MGZkYmVlNTdmNGEwOWU2NTQ5MmRjZTgxIiwiaXNzIjoiIiwiYXVkIjoib1NJR3JpcyIsInN1YiI6IjgiLCJ1c2VyaWQiOiI4IiwidXNlcm5hbWUiOiJhZG1pbnNlcmdpbyIsImVtYWlsIjoic2NhbWJlaXJvQG9zaWdyaXMuY29tIiwibm9tYnJlIjoiU2VyZ2lvIiwiYXBlbGxpZG8iOiJDYW1iZWlybyIsImV4cCI6MTc2MTEzMjg2NCwiaWF0IjoxNzYxMTI5MjY0LCJ0b2tlbl90eXBlIjoiYmVhcmVyIiwic2NvcGUiOiJpbnRlcm5hbF91c2VyIn0.OZKdK3maG_3a9nv5aslB3M4Odnpcq4jxZzha_weYPI89m7ddECXCC9adRvo_BTXaegovd7AQ2BJQVoXunp9S8Rs6gnG9PsmY0UI8uVt-OcbBYi7EeYivSVJXMkobI0Q3gys1Wp76TbR05Huy5LejZlQRo03MVNyed6VXnhQgN0Guw-ymqMkNkuMCVRxIwd_Pjo0LbUcNa7naRk5nV5kIqXwZRiQInnHXSF5eGzUcC63FTDXcH1JBY_JF4j2jR2TQR4iRaFR3Ig4VX1spkXi-XKWK1DQNIYxrzUZpcE8TJ7ViymA1S0cHa5Ye2_yOE4wfwSrgUeCIL3SHqgqtEP-gtg"

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
        if len(datos) == 1:
            id_campaña=datos[0]["info"]["id"]
            return f"Campaña comprobada. ID de Campaña: {id_campaña}"
        else:
            id_campaña = [obj["info"]["id"] for obj in datos]
            return f"Existen varias campañas con el {año} y {campaña} indicados. IDs de las campañas: {id_campaña}"   
    else:
        return f"No encuentro ninguna campaña del {año} con el nombre {campaña}"

@tool("ComprobarCultivo")    
def validar_cultivo(cultivo: str, id_campaña: str, variedad: str) -> str:
    """Usa esta función para comprobar si existe el cultivo en la campaña en osigris, pasándole el nombre del cultivo y el 
    ID de la campaña
    Arguments:
    - cultivo: Cultivo introducido por el usuario
    - id_campaña: Alias/nombre de la campaña obtenido en validar_explotacion
    """
    logging.info(f"--Start ComprobarCultivo tool with arguments: {cultivo}, {id_campaña}")
    url = f"{API_URL}/osigrisapi/season/show/{id_campaña}/crop/list?qg1[and]=typecrop,typevariety&typecrop[in]={cultivo}&typevariety[in]={variedad}"
    valido, datos = hacer_peticion_get(url)
    if valido=="si":
        if len(datos) == 1:
            sigpacs_id=[item["id"] for item in datos[0]["sigpac"]]
            return f"Cultivo comprobado correctamente en campaña. IDs de sigpacs obtenidos: {sigpacs_id}"
        else:
            nombres = []
            for d in datos:
                nombre = d["subtype"]["typecrop"]["name"]
                variedad = d["subtype"]["name"]
                nombres.append(f"{nombre}-{variedad}")
                return f"Existen varios cultivos en la campaña indicada. Elige uno de estos cultivos-variedad: {nombres}"   
    else:
        return f"No encuentro ningún cultivo en la campaña indicada"
    return valido