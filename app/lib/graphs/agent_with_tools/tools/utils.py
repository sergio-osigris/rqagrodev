from langchain_core.tools import tool
import time
@tool("current_date")
async def get_current_date():
    """Usa esta función para leer la fecha y hora actuales
    """
    print("Leyendo hora actual")
    current_time = time.localtime()
    formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", current_time)
    return formatted_time
