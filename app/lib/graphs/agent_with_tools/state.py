from typing import List, Dict, Any

class ChatState:
    """
    Estado de la conversación del usuario.
    Mantiene los mensajes y el estado de validación de herramientas.
    """

    def __init__(self, messages: List[Dict[str, Any]], user_id: str, name: str):
        self.messages = messages  # Lista de mensajes del chat
        self.user_id = user_id    # ID del usuario
        self.name = name          # Nombre del usuario

        # Estado de validación de herramientas
        self.fitosanitario_validado = False  # True si CheckFitosanitario ya se ejecutó
        self.campaña_validada = False        # True si ComprobarExplotacion ya se ejecutó

        # Datos extraídos
        self.fitosanitario = None
        self.campaña = None
        self.año = None

        # Puedes agregar otros campos si los necesitas en tu flujo
        # ej: dosis, cultivo, aplicador, fecha, etc.
        self.dosis = None
        self.cultivo = None
        self.aplicador = None
        self.fecha = None
