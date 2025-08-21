from pydantic import BaseModel, Field

class Fitosanitario(BaseModel):
    num_registro: str = Field(..., title="Número de Registro", description="Número de registro del producto fitosanitario")
    name : str = Field(..., title="Nombre", description="Nombre del producto fitosanitario")