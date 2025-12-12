import logging
import requests
from app.lib.graphs.agent_with_tools.state import ChatState

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
            state.campaign.id = id_campaña

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
            state.crop.sigpacs_ids=[str(item["id"]) for item in datos[0]["sigpac"]]
            msg = (
                "Cultivo comprobado correctamente en la campaña.\n"
                f"IDs de SIGPAC obtenidos: {', '.join(state.crop.sigpacs_ids) if state.crop.sigpacs_ids else 'ninguno'}"
            )
            state.check_messages.append(msg)
        else:
            # ---------- CASO 2: VARIOS CULTIVOS EN LA CAMPAÑA ----------
            # Mapa label → lista de sigpacs_ids
            opciones: dict[str, list[str]] = {}
            labels: list[str] = []

            for d in datos:
                nombre = d["subtype"]["typecrop"]["name"]
                variedad = d["subtype"]["name"]
                label = f"{nombre}-{variedad}"

                # lista de IDs sigpac asociados a ese cultivo/variedad
                sigpacs_ids = [str(item["id"]) for item in d.get("sigpac", [])]

                opciones[label] = sigpacs_ids
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
