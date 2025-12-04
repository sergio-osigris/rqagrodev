from app.lib.graphs.agent_with_tools.state import ChatState
import logging
from .osigris import ALL_CHECKS

def check_record_node(state: ChatState) -> ChatState:
    logging.info("Ejecutando comprobaciones de registro...")

    if not hasattr(state, "check_messages") or state.check_messages is None:
        state.check_messages = []

    if not hasattr(state, "check_errors") or state.check_errors is None:
        state.check_errors = []

    for check in ALL_CHECKS:
        try:
            check(state)   # ya no esperamos return, sólo efectos en state
        except Exception as e:
            logging.exception(f"Error ejecutando check {check.__name__}: {e}")
            state.check_errors.append(f"Error interno en {check.__name__}")

    if state.check_errors:
        state.check_status = "failed"
    else:
        state.check_status = "ok"

    logging.info(f"Comprobaciones finalizadas. Errores: {state.check_errors}")
    logging.info(f"Mensajes de comprobación: {state.check_messages}")

    return state

