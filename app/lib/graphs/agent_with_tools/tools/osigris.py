import logging
import requests
from app.lib.graphs.agent_with_tools.state import ChatState
from difflib import get_close_matches
from typing import Dict, Any
from app.models.record2 import MetadataOsigris
import json
from pydantic import BaseModel
import datetime as dt

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
    
def hacer_peticion_post(url, payload) -> str:
    access_token = obtener_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=5)
        json_resp = resp.json()
        status = resp.status_code
        ctype = resp.headers.get("Content-Type")
        body = resp.text or ""

        logging.info(f"POST {url} -> status={status} content-type={ctype}")
        logging.info(f"Body[:300]: {body[:300]!r}")


        errors = json_resp.get("error") or []
        data = json_resp.get("data") or []

        # 1) Si hay errores, manda error
        if isinstance(errors, list) and len(errors) > 0:
            logging.info(f"⚠️ Error devuelto por la API: {errors}")
            return False, None, errors

        # 2) Si hay data con result ok, válido
        if isinstance(data, list) and any(item.get("result") == "ok" for item in data if isinstance(item, dict)):
            return True, data, None

        # 3) Caso raro: sin errores pero tampoco ok
        return False, data or None, None

    except requests.RequestException as e:
        logging.info(f"Error al conectar con el endpoint: {e}")
        return False, None, [{"message": str(e)}]
    except ValueError as e:  # JSON inválido
        logging.info(f"Respuesta no es JSON válido: {e}")
        return False, None, [{"message": "Respuesta no es JSON válido"}]
 
def validar_explotacion(state: ChatState) -> None:
    """
    Comprueba campaña en Osigris usando Año_campaña y Campaña del state.
    Rellena campos en el state y añade mensajes a check_messages y errores a check_errors.
    """
    año = state.record.Año_campaña
    nombre = state.record.Campaña

    logging.info(f"--Start ComprobarExplotacion tool with arguments: {año}, {nombre}")

    url = (
        f"{API_URL}/osigrisapi/resource/season/list"
        f"?&qg1[and]=year,alias&year[eq]={año}&alias[eq]={nombre}"
    )
    valido, datos = hacer_peticion_get(url)

    # Inicializamos algunos flags
    state.campaign.validated = False
    state.campaign.need_choice = False
    state.campaign.need_fix = False
    state.campaign.id = None
    state.campaign.options = None

    if valido == "si":
        if len(datos) == 1:
            # ---------- CASO 1: UNA SOLA CAMPAÑA ----------
            id_campaña = datos[0]["info"]["id"]

            state.campaign.validated = True
            state.campaign.id = str(id_campaña)

            msg = f"Campaña comprobada. ID de Campaña: {id_campaña}"
            state.check_messages.append(msg)

        elif len(datos) > 1:
            # ---------- CASO 2: VARIAS CAMPAÑAS ----------
            options = []
            for obj in datos:
                info = obj["info"]
                options.append(str(info["id"]))

            state.campaign.validated = False
            state.campaign.need_choice = True
            state.campaign.options = options

            # Mensaje amigable para WhatsApp
            lines = ["He encontrado varias campañas con esos datos:"]
            # Botones: SOLO los IDs
            button_ids = options
            lines.append("")  # línea en blanco antes de los botones
            lines.append(f"[button:{'|'.join(button_ids)}]")
            msg = "\n".join(lines)
            state.check_messages.append(msg)

    else:
        # ---------- CASO 3: NINGUNA CAMPAÑA ----------
        state.campaign.need_fix = True
        state.campaign.validated = False
        # Reiniciar el valor de la variable, puesto que luego tendrá que generarse de nuevo el objeto válido (el registro creado anteriormente no sirve)
        state.record_generated = False

        msg = (
            f"No encuentro ninguna campaña del {año} con el nombre {nombre}. "
            "Por favor, revisa el año y el nombre de la campaña e indícamelo de nuevo."
        )
        state.check_messages.append(msg)

def validar_cultivo(state: ChatState) -> None:
    """Usa esta función para comprobar si existe el cultivo en la campaña en osigris, cogiendo del state el nombre del cultivo y el 
    ID de la campaña
    Rellena campos en el state y añade mensajes a check_messages y errores a check_errors.
    """
    cultivo=state.record.Cultivo
    id_campaña=state.campaign.id
    variedad=state.record.Variedad_Cultivo or ""
    logging.info(f"--Start ComprobarCultivo tool with arguments: {cultivo}, {id_campaña}, {variedad}")
    url = f"{API_URL}/osigrisapi/season/show/{id_campaña}/crop/list?qg1[and]=typecrop,typevariety&typecrop[in]={cultivo}&typevariety[in]={variedad}"

    # Inicializamos algunos flags
    state.crop.validated = False
    state.crop.need_choice = False
    state.crop.need_fix = False
    state.crop.sigpacs_ids = []
    state.crop.selected_label = ""
    state.crop.options = {} 
    
    valido, datos = hacer_peticion_get(url)
    if valido=="si":
        if len(datos) == 1:
            # ---------- CASO 1: UN ÚNICO CULTIVO: Obtenemos correctamente sus sigpacs ---------- 
            state.crop.validated = True
            state.crop.sigpacs_ids=[item["id"] for item in datos[0]["sigpac"]]
            state.crop.surface=datos[0]["dimension"]
            state.phytosanitary_parcel.idcp = [item["id"] for item in datos[0]["sigpac"]]
            if state.record.Superficie:
                state.phytosanitary_parcel.surface = state.record.Superficie
            else:
                state.phytosanitary_parcel.surface = datos[0]["dimension"]
            msg = (
                "Cultivo comprobado correctamente en la campaña.\n"
                f"IDs de SIGPAC obtenidos: {', '.join(map(str, state.crop.sigpacs_ids)) if state.crop.sigpacs_ids else 'ninguno'}"
            )
            state.check_messages.append(msg)
        else:
            # ---------- CASO 2: VARIOS CULTIVOS EN LA CAMPAÑA ----------
            # Mapa label → lista de sigpacs_ids
            opciones: Dict[str, Dict[str, Any]] = {}
            labels: list[str] = []

            for d in datos:
                nombre = d["subtype"]["typecrop"]["name"]
                variedad = d["subtype"]["name"]
                label = f"{nombre}-{variedad}"

                # lista de IDs sigpac asociados a ese cultivo/variedad
                sigpacs_ids = [item["id"] for item in d.get("sigpac", [])]
                surface = d["dimension"]
                opciones[label] = {
                    "sigpacs_ids": sigpacs_ids,
                    "surface": surface,
                }
                labels.append(label)

            state.crop.validated = False
            state.crop.need_choice = True
            state.crop.need_fix = False
            state.crop.options = opciones

            # Mensaje amigable para WhatsApp
            lines = ["He encontrado varios cultivos/variedades en la campaña indicada."]
            lines.append("Elige uno de estos cultivos-variedad:")
            # Botones: los textos visibles serán los labels (e.g. "Tomate-Cherry")
            lines.append("")
            lines.append(f"[button:{'|'.join(labels)}]")
            msg = "\n".join(lines)
            state.check_messages.append(msg)

    else:
        # ---------- CASO 3: NINGÚN CULTIVO ----------
        state.crop.need_fix = True
        state.crop.validated = False
        # Reiniciar el valor de la variable, puesto que luego tendrá que generarse de nuevo el objeto válido (el registro creado anteriormente no sirve)
        state.record_generated = False
        msg = f"No encuentro ningún cultivo en la campaña indicada en oSIGris. Revisa el nombre/variedad."
        state.check_messages.append(msg) 

def validar_infeccion(state: ChatState) -> None:
    """Usa esta función para comprobar si existe la infeccion en la lista oficial de osigris,
    filtrando por la infeccion indicada por el usuario.
    Rellena campos en el state y añade mensajes a check_messages y errores a check_errors.
    """
    plaga=state.record.Plaga
    logging.info(f"--Start ComprobarInfeccion tool with arguments: {plaga}")
    url = f"{API_URL}/osigrisapi/master/infection/list?qg1[or]=name,code&name[in]={plaga}&code[in]={plaga}&simplified"

    # Inicializamos algunos flags
    state.infection_validated = False
    
    valido, datos = hacer_peticion_get(url)
    if valido=="si":
        name_to_item = {item["name"]: item for item in datos if item.get("name")}
        names = list(name_to_item.keys())
        match = get_close_matches(plaga, names, n=1, cutoff=0.75)
        best = match[0] if match else None
        best_item = name_to_item[best] if best else None
        if best:
            state.infection_validated = True
            state.phytosanitary_parcel.info.infection = best_item
            msg = "Infección comprobada correctamente en oSIGris: "+best
        else:
            state.record_generated = False
            msg = f"No encuentro ninguna infección/plaga parecida a la indicada en la lista oficial de oSIGris. Revisa el nombre."
        state.check_messages.append(msg)
    else:
        # ---------- CASO 2: NINGUNA INFECCIÓN ----------
        # Reiniciar el valor de la variable, puesto que luego tendrá que generarse de nuevo el objeto válido (el registro creado anteriormente no sirve)
        state.record_generated = False
        msg = f"No encuentro ninguna infección/plaga parecida a la indicada en la lista oficial de oSIGris. Revisa el nombre."
        state.check_messages.append(msg) 

def validar_measure(state: ChatState) -> None:
    """Usa esta función para comprobar si existe la unidad de medida de dosis en la lista oficial de osigris,
    filtrando por la unidad indicada por el usuario.
    Rellena campos en el state y añade mensajes a check_messages y errores a check_errors.
    """
    measure=state.record.Medida_dosis
    logging.info(f"--Start ComprobarMeasure tool with arguments: {measure}")
    url = f"{API_URL}/osigrisapi/master/measure/list?qg1[and]=typemeasure,symbol&typemeasure[eq]=1&symbol[eq]={measure}"

    # Inicializamos algunos flags
    state.measure_validated = False
    
    valido, datos = hacer_peticion_get(url)
    if valido=="si":
        state.measure_validated = True
        state.phytosanitary_parcel.info.md = datos[0]
        state.phytosanitary_parcel.info.d = state.record.Dosis
        msg = "Medida comprobada correctamente en oSIGris"
        state.check_messages.append(msg)
    else:
        # ---------- CASO 2: NINGUNA MEDIDA ----------
        # Reiniciar el valor de la variable, puesto que luego tendrá que generarse de nuevo el objeto válido (el registro creado anteriormente no sirve)
        state.record_generated = False
        msg = f"No encuentro ninguna unidad de medida de dosis parecida a la indicada en la lista oficial de oSIGris. Revisa el simbolo."
        state.check_messages.append(msg)         

def validar_fitosanitario(state: ChatState) -> None:
    """Usa esta función para comprobar si existe el fitosanitario en la lista oficial de osigris,
    filtrando por el fitosanitario indicado por el usuario.
    Rellena campos en el state y añade mensajes a check_messages y errores a check_errors.
    """
    fitosanitario=state.record.Tratamiento_fitosanitario
    logging.info(f"--Start ComprobarFitosanitario tool with arguments: {fitosanitario}")
    url = f"{API_URL}/osigrisapi/master/typephytosanitary/list?qg1[or]=name,code&name[in]={fitosanitario}&code[in]={fitosanitario}&simplified"

    # Inicializamos algunos flags
    state.phytosanitary_validated = False
    
    valido, datos = hacer_peticion_get(url)
    if valido=="si":
        name_to_item = {item["name"]: item for item in datos if item.get("name")}
        names = list(name_to_item.keys())
        match = get_close_matches(fitosanitario, names, n=1, cutoff=0.75)
        best = match[0] if match else None
        best_item = name_to_item[best] if best else None
        if best:
            state.phytosanitary_validated = True
            state.phytosanitary_parcel.info.subtype=best_item
            msg = "Fitosanitario comprobado correctamente en oSIGris: "+best
        else:
            state.record_generated = False
            msg = f"No encuentro ningún fitosanitario parecido al indicado en la lista oficial de oSIGris. Revisa el nombre."
        state.check_messages.append(msg)
    else:
        # ---------- CASO 2: NINGÚN FITOSANITARIO ----------
        # Reiniciar el valor de la variable, puesto que luego tendrá que generarse de nuevo el objeto válido (el registro creado anteriormente no sirve)
        state.record_generated = False
        msg = f"No encuentro ninguna fitosanitario parecido al indicado en la lista oficial de oSIGris. Revisa el nombre."
        state.check_messages.append(msg) 

def validar_metadatos(state: ChatState) -> None:
    """Usa esta función para comprobar si existe el usuario en la lista oficial de osigris,
    usando el token del usuario.
    Rellena campos en el state y añade mensajes a check_messages y errores a check_errors.
    """
    # token=state.osigris_token
    logging.info(f"--Start ComprobarMetadatos tool with arguments: VALOR DEL TOKEN AQUI")
    url = f"{API_URL}/osigrisapi/oauth/user/show"

    # Inicializamos algunos flags
    state.metadatos_validated = False
    
    valido, datos = hacer_peticion_get(url)
    if valido=="si":
        d = {
            "type": "UserMetadata",
            "id": datos["id"],
        }
        state.phytosanitary_parcel.info.metadata.append(
            MetadataOsigris(user=d)
        )
        state.metadatos_validated = True
        msg = "Usuario comprobado correctamente en oSIGris"
        state.check_messages.append(msg)
    else:
        # ---------- CASO 2: NINGÚN USUARIO ----------
        # Reiniciar el valor de la variable, puesto que luego tendrá que generarse de nuevo el objeto válido (el registro creado anteriormente no sirve)
        state.record_generated = False
        msg = f"En estes momentos no se encuentra registrado en la lista oficial de oSIGris. Revisa el nombre."
        state.check_messages.append(msg) 

def json_default(o):
    if isinstance(o, BaseModel):
        return o.model_dump(by_alias=True)  # (python mode)
    if isinstance(o, dt.datetime):
        return o.strftime("%d-%m-%Y %H:%M:%S")
    if isinstance(o, dt.date):
        return o.strftime("%d-%m-%Y")
    raise TypeError(f"{type(o).__name__} not JSON serializable")

def guardar_fitosanitario(state: ChatState) -> bool:
    """Usa esta función para guardar el registro del fitosanitario en oSIGris.
    Rellena campos en el state y añade mensajes a check_messages y errores a check_errors.
    """
    # token=state.osigris_token
    logging.info(f"--Start GuardarFito tool")
    id_campaña=state.campaign.id
    url = f"{API_URL}/osigrisapi/season/{id_campaña}/phytosanitaryparcel/list/"

    # Inicializamos algunos flags
    # state.metadatos_validated = False

    # 3.1 Normalizar: convertir a dict sí o sí
    if isinstance(state, ChatState):
        response = state.model_dump()
    else:
        # Por si LangGraph ya te devuelve dict
        response = dict(state)

    phytosanitary_parcel_to_save = json.dumps(response["phytosanitary_parcel"], ensure_ascii=False, indent=2, default=json_default)
    payload = {"data": [phytosanitary_parcel_to_save]}
    valido, data, error = hacer_peticion_post(url, payload)
    if error:
        msg = "No se pudo guardar correctamente en oSIGris"
        response.setdefault("check_messages", []).append(msg)
        return False
    elif valido:
        msg = "Tratamiento guardado correctamente en oSIGris"
        response.setdefault("check_messages", []).append(msg)
        return True
    else: 
        msg = "No devuelve OK la API, pero tampoco dió error"
        response.setdefault("check_messages", []).append(msg)
        return False