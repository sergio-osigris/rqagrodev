from langchain_core.tools import tool
from app.interfaces.airtable import PostgresClient
import logging
import requests

API_URL = "https://qnur3yjwqg.execute-api.eu-west-3.amazonaws.com"  

def obtener_access_token() -> str:
    url = "https://qnur3yjwqg.execute-api.eu-west-3.amazonaws.com/osigrisapi/oauth2/authentication/"
    
    data = {
        "grant_type": "password",
        "client_id": "oSIGris",
        "client_secret": "UjxBOYDatIElyO9NNPWWv1RMmfKPmZ44ILdzFXwgOaHt3teeaISaqvTLOw2uyUuU",
        "username": "adminsergio",
        "password": "643e145a301b650c019f6ecb75c4dfc90ea93d4fa7662d9da50a42294a3c7824cd9fd4a5cc7069200bea6af9b62ae7069c37abdd74d3eaad0297a4dd3cfeaf85"
    }

    try:
        resp = requests.post(url, data=data, timeout=10)
        resp.raise_for_status()
        json_resp = resp.json()
        access_token = json_resp.get("access_token")
        if access_token:
            return access_token
        else:
            print("⚠️ No se encontró 'access_token' en la respuesta:", json_resp)
            return None
    except requests.RequestException as e:
        print(f"❌ Error al obtener token: {e}")
        return None
    
def hacer_peticion_get(url) -> str:
    access_token = obtener_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
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
    logging.info(f"--Start ComprobarCultivo tool with arguments: {cultivo}, {id_campaña}, {variedad}")
    url = f"{API_URL}/osigrisapi/season/show/{id_campaña}/crop/list?qg1[and]=typecrop,typevariety&typecrop[in]={cultivo}&typevariety[in]={variedad}"
    valido, datos = hacer_peticion_get(url)
    if valido=="si":
        if len(datos) == 1:
            sigpacs_id=[item["id"] for item in datos[0]["sigpac"]]
            dimension = datos[0]["dimension"]
            return f"Cultivo comprobado correctamente en campaña. IDs de sigpacs obtenidos: {sigpacs_id}. Dimension: {dimension}"
        else:
            nombres = []
            datos_cutlvio_variedad = []
            for d in datos:
                nombre = d["subtype"]["typecrop"]["name"]
                variedad = d["subtype"]["name"]
                nombres.append(f"{nombre}-{variedad}")
                sigpacs_id = [item["id"] for item in d["sigpac"]]
                dimension = d["dimension"]
                datos_cutlvio_variedad.append(f"{nombre}-{variedad} Sigpacs:{sigpacs_id} Dimension: {dimension}")
            logging.info(f"Existen varios cultivos en la campaña indicada. Elige uno de estos cultivos-variedad: {nombres}. Datos de los cultivos variedad obtenidos: {datos_cutlvio_variedad}.")
            return f"Existen varios cultivos en la campaña indicada. Elige uno de estos cultivos-variedad: {nombres}. Datos de los cultivos variedad obtenidos: {datos_cutlvio_variedad}."   
    else:
        return f"No encuentro ningún cultivo en la campaña indicada"