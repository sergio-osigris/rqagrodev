from langchain_core.tools import tool
from app.interfaces.airtable import PostgresClient
from difflib import get_close_matches
import logging
from app.models.fitosanitario import Fitosanitario
from typing import List
@tool("Fitosanitarios_Disponibles")
async def available_fitosanitarios() -> List[Fitosanitario]:
    """Usa esta función para obtener la lista de los fitosanitarios disponibles en la base de datos.
    """
    logging.info("--Start available_fitosanitarios tool")
    db_client = PostgresClient()
    await db_client.initialize()
    fitosanitarios = await db_client.read_fitosanitarios()
    return fitosanitarios

@tool("CheckFitosanitario")
async def check_fitosanitarios(name: str) -> str:
    """
    VALÍDALO SÓLO si el usuario ha dado un nombre de producto
    y quieres comprobar errores tipográficos o existencia en la lista oficial.
    NO llames a esta tool para nada más.
    Arguments:
    - name: Nombre del producto introducido por el usuario
    """
    logging.info(f"--Start check_fitosanitarios tool with argument: {name}")
    db_client = PostgresClient()
    await db_client.initialize()
    fitosanitarios = await db_client.read_fitosanitarios()
    fitos = [f["name"].lower() for f in fitosanitarios]
    # Get the one with highest similarity
    closest = get_close_matches(name, fitos, n=1)
    if closest:
        return f"Fitosanitario comprobado. Nombre final: {closest[0]}"
    else:
        return f"No encuentro ningún fitosanitario similar a {name} en la lista de fitosanitarios disponibles"

