from pydantic import BaseModel, PrivateAttr
from typing import List, Dict, Any, Optional

class ChatState(BaseModel):
    """
    Estado de la conversación del usuario.
    Compatible con FastAPI como modelo Pydantic.
    """
    messages: List[Dict[str, Any]]
    user_id: str
    name: str

    # Datos extraídos (opcionalmente nulos)
    fitosanitario: Optional[str] = None
    campaña: Optional[str] = None
    año: Optional[int] = None
    dosis: Optional[str] = None
    cultivo: Optional[str] = None
    aplicador: Optional[str] = None
    fecha: Optional[str] = None

    # Atributos privados (no se incluyen en JSON)
    _fitosanitario_validado: bool = PrivateAttr(default=False)
    _campaña_validada: bool = PrivateAttr(default=False)

    # Métodos auxiliares
    def validar_fitosanitario(self):
        self._fitosanitario_validado = True

    def validar_campaña(self):
        self._campaña_validada = True

    @property
    def fitosanitario_validado(self):
        return self._fitosanitario_validado

    @property
    def campaña_validada(self):
        return self._campaña_validada
