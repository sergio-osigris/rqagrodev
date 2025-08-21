from langchain_core.tools import tool
from app.models.record import RecordRequest
from app.interfaces.airtable import PostgresClient
import logging

@tool("CreateRecord", return_direct=True)
def create_record(record : RecordRequest) -> RecordRequest:
    """
    Usa esta herramienta para crear un registro de una incidencia fitosanitaria. 
    Esta herramienta no guarda el registro en la base de datos. SOLO la inicializa.
    """
    logging.info(f"Creating new record with data {record}")
    return record

@tool("SaveRecord")
async def save_record(record: RecordRequest):
    """
    Usa esta herramienta para guardar un registro de una incidencia fitosanitaria.
    Esta herramienta toma un objeto Record y lo guarda en la base de datos.
    Args:
        record (Record): El registro a guardar, que contiene información sobre la incidencia fitosanitaria.
    Returns:
        str: Un mensaje de confirmación indicando que el registro ha sido guardado correctamente.
    """
    logging.debug("GUARDANDO INFO FITOSANITARIA")
    db_client = PostgresClient()
    await db_client.initialize()
    try:
        logging.debug(f"Registro en crudo: {record}")
        
        record_result = await db_client.create_record(
            user_id=record.user_id,
            incident_type=record.Tipo_de_incidencia,
            treatment=record.Tratamiento_fertilizante_labor,
            problem=record.Problema_en_campo or "",
            amount=record.Dosis or "",
            location=record.Cultivo or "",
            size=int(record.Superficie) if record.Superficie is not None else 0,
            date=record.Fecha,
            caldo=str(record.Caldo) if record.Caldo is not None else "0",
            aplicador=record.Aplicador or "",
            name=record.Nombre,
            parcelas=record.parcelas or ""
        )
        logging.info(f"Nuevo registro guardado, respuesta de DB: {record_result}")
        return f"Registro guardado correctamente. Información del registro para que se la reenvies al usuario: {record_result}"
    except Exception as e:
        logging.warning(f"Error guardando registro. Código de error: {e}")
        return f"Parece que hubo un problema al guardar el registro. Código de error: {e}"
