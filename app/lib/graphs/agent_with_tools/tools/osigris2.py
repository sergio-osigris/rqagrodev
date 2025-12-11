from app.lib.graphs.agent_with_tools.state import ChatState
import logging
from .osigris import validar_explotacion, validar_cultivo

def check_record_node(state: ChatState) -> ChatState:
    logging.info("Ejecutando comprobaciones de registro...")

    # reseteamos por si venían de ciclos anteriores
    state.check_messages = []
    state.check_errors = []
    
    # ---------- 1) VALIDAR CAMPAÑA ----------
    if state.campaign.id is None:
        try:
            validar_explotacion(state)
        except Exception as e:
            logging.exception(f"Error ejecutando validar_explotacion: {e}")
            state.check_errors.append("Error interno en validar_explotacion")
            state.check_status = "failed"
            # En un fallo interno, ya no seguimos con más checks
            return state

    # ---------- 2) VALIDAR CULTIVO ----------
    if state.campaign.id:
        try:
            validar_cultivo(state)
        except Exception as e:
            logging.exception(f"Error ejecutando validar_cultivo: {e}")
            state.check_errors.append("Error interno en validar_cultivo")
            state.check_status = "failed"
            # En un fallo interno, ya no seguimos con más checks
            return state
        
    if state.check_errors:
        state.check_status = "failed"
    else:
        state.check_status = "ok"

    logging.info(f"Comprobaciones finalizadas. Errores: {state.check_errors}")
    logging.info(f"Mensajes de comprobación: {state.check_messages}")

    return state

