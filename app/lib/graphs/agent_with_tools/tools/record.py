from langchain_core.tools import tool
from app.models.record import RecordRequest
from app.models.record2 import RecordBase
from app.interfaces.airtable import PostgresClient
import logging

@tool("CreateRecord", return_direct=True)
def create_record(record : RecordBase) -> RecordBase:
    """
    Crea un nuevo registro de aplicación de fitosanitario en el sistema.

    IMPORTANTE:
    - SOLO debes usar esta herramienta DESPUÉS de que el usuario haya confirmado
      explícitamente que los datos del resumen son correctos respondiendo "Sí"
      o pulsando el botón "Sí".
    - No la uses para hacer borradores ni mientras sigues preguntando datos.
    """
    logging.info(f"Creating new record with data {record}")
    return record