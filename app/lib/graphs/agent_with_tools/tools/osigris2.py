from app.lib.graphs.agent_with_tools.state import ChatState
import logging
from .osigris import ALL_CHECKS

def check_record_node(state: ChatState) -> ChatState:
    """
    Nodo que ejecuta una lista de comprobaciones sobre el state/record.
    """
    logging.info("Ejecutando comprobaciones de registro...")

    # Asegurarte de que la lista existe / está limpia
    if not hasattr(state, "check_errors") or state.check_errors is None:
        state.check_errors = []

    # 👉 nos aseguramos también de tener la lista de mensajes
    if not hasattr(state, "check_messages") or state.check_messages is None:
        state.check_messages = []

    for check in ALL_CHECKS:
        try:
            result = check(state)  # 👈 AHORA guardamos el resultado

            # Si la función devuelve un texto, lo guardamos
            if isinstance(result, str) and result.strip():
                state.check_messages.append(result)

        except Exception as e:
            logging.exception(f"Error ejecutando check {check.__name__}: {e}")
            state.check_errors.append(f"Error interno en {check.__name__}")

    logging.info(f"Comprobaciones finalizadas. Errores: {state.check_errors}")
    logging.info(f"Resultados de checks: {state.check_messages}")

    # Si quieres, aquí puedes tomar decisiones:
    if state.check_errors:
        state.check_status = "failed"
    else:
        state.check_status = "ok"

    return state
