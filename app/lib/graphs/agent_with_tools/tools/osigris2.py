from app.lib.graphs.agent_with_tools.state import ChatState
import logging
from .osigris import validar_explotacion, validar_cultivo, validar_infeccion, validar_measure, validar_fitosanitario, validar_metadatos
from app.models.record2 import CampaignBase, CropBase, RecordBase
from datetime import date

def check_record_node(state: ChatState) -> ChatState:
    logging.info("Ejecutando comprobaciones de registro...")

    # reseteamos por si venían de ciclos anteriores
    state.check_messages = []
    state.check_errors = []
    state.record_to_save = False
    state.check_status = None 
    
    # ---------- 1) VALIDAR CAMPAÑA ----------
    if not state.campaign.validated:
        try:
            validar_explotacion(state)
        except Exception as e:
            logging.exception(f"Error ejecutando validar_explotacion: {e}")
            state.check_errors.append("Error interno en validar_explotacion")
            state.check_status = "failed"
            # En un fallo interno, ya no seguimos con más checks
            return state

    # ---------- 2) VALIDAR CULTIVO ----------
    if state.campaign.validated and not state.campaign.need_choice and not state.campaign.need_fix and not state.crop.validated:
        try:
            validar_cultivo(state)
        except Exception as e:
            logging.exception(f"Error ejecutando validar_cultivo: {e}")
            state.check_errors.append("Error interno en validar_cultivo")
            state.check_status = "failed"
            # En un fallo interno, ya no seguimos con más checks
            return state
        
    # ---------- 3) VALIDAR INFECCIÓN ----------
    if not state.infection_validated:
        try:
            validar_infeccion(state)
        except Exception as e:
            logging.exception(f"Error ejecutando validar_infeccion: {e}")
            state.check_errors.append("Error interno en validar_infeccion")
            state.check_status = "failed"
            # En un fallo interno, ya no seguimos con más checks
            return state

    # ---------- 4) VALIDAR MEASURE ----------
    if not state.measure_validated:
        try:
            validar_measure(state)
        except Exception as e:
            logging.exception(f"Error ejecutando validar_measure: {e}")
            state.check_errors.append("Error interno en validar_measure")
            state.check_status = "failed"
            # En un fallo interno, ya no seguimos con más checks
            return state

    # ---------- 5) VALIDAR FITOSANITARIO ----------
    if not state.phytosanitary_validated:
        try:
            validar_fitosanitario(state)
        except Exception as e:
            logging.exception(f"Error ejecutando validar_fitosanitario: {e}")
            state.check_errors.append("Error interno en validar_fitosanitario")
            state.check_status = "failed"
            # En un fallo interno, ya no seguimos con más checks
            return state
        
    # ---------- 6) VALIDAR METADATOS USER ----------
    if not state.metadatos_validated:
        try:
            validar_metadatos(state)
        except Exception as e:
            logging.exception(f"Error ejecutando validar_metadatos: {e}")
            state.check_errors.append("Error interno en validar_metadatos")
            state.check_status = "failed"
            # En un fallo interno, ya no seguimos con más checks
            return state
          
    # ---------- 7) GUARDAR CULTIVO ----------
    if state.campaign.validated and state.crop.validated and state.infection_validated and state.measure_validated and state.phytosanitary_validated and state.metadatos_validated:
        # Aqui guardo el cultivo
        state.record_to_save=True
        # Aqui vacio las variables
        state.record = RecordBase(Fecha=date.today(),Tratamiento_fitosanitario="",Campaña="",Año_Campaña="",Plaga="",Dosis=0,Medida_dosis="",Cultivo="",Variedad_Cultivo="",Superficie=0)
        state.campaign = CampaignBase(validated= False,id= "",options= [],need_choice= False,need_fix= False)
        state.crop = CropBase(validated= False,sigpacs_id= [],selected_label="",options= {},need_choice= False,need_fix= False)
        state.record_generated = False
        state.phytosanitary_validated = False
        state.measure_validated = False
        state.infection_validated = False
        state.metadatos_validated = False
        state.check_messages.append("PROCESO DE GUARDADO CONTRA OSIGRIS COMPLETADO CORRECTAMENTE")

    if state.check_errors:
        state.check_status = "failed"
    else:
        state.check_status = "ok"

    logging.info(f"Comprobaciones finalizadas. Errores: {state.check_errors}")
    logging.info(f"Mensajes de comprobación: {state.check_messages}")

    return state

