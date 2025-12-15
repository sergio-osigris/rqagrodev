from pydantic import BaseModel, Field
from typing import Optional,Literal, List, Dict, Any
from datetime import datetime, date

class RecordBase(BaseModel):
    """
    Representa un registro de datos detallado de una incidencia agrícola, incluyendo detalles de la aplicación,
    observaciones y metadatos. Diseñada para ser interpretada por un LLM para almacenamiento
    y recuperación estructurada de datos.
    """
    created_at: datetime = Field(default_factory=datetime.utcnow, title="Fecha de Creación", description="Marca de tiempo exacta (fecha y hora UTC) de cuándo se creó el registro en el sistema. Formato: AAAA-MM-DDTHH:MM:SSZ. Ejemplo: '2024-07-15T10:30:00Z'.")
    Fecha: Optional[date] = Field(..., title="Fecha de la Incidencia/Aplicación", description="Fecha principal en la que ocurrió la labor, aplicación o se observó la incidencia. Formato: AAAA-MM-DD. Ejemplo: '2024-07-14'.")
    Tratamiento_fitosanitario: str = Field("", alias="Nombre del fitosanitario", description="Nombre específico del tratamiento/producto fertilizante. Ejemplos: 'Azoxystrobin 25%', 'Metenal'.")
    Campaña: str = Field("", alias="Nombre de la campaña", description="Nombre/alias específico de la campaña. Ejemplos: 'Prueba', 'Explotacion'.")
    Año_campaña: str = Field("", alias="Año de la campaña", description="Año en el que se realiza la campaña. Ejemplos: '2023', '2024', '2022', '2025'.")
    Plaga: str = Field(..., alias="Problema en campo", description="Descripción detallada del problema o plaga detectada en el campo que motivó la acción. Ejemplos: 'Fuerte ataque de mildiu en hojas basales', 'Clorosis férrica en brotes jóvenes', 'Compactación del suelo post-lluvias'.")
    Dosis: float = Field(..., title="Medida de la dosis aplicada", description="Medida de la cantidad del producto (fitosanitario o fertilizante) aplicado. Ejemplos: 'kg/ha', 'l/ha'.")
    Medida_dosis: str = Field(..., title="Dosis Aplicada", description="Cantidad del producto (fitosanitario o fertilizante) aplicado. Ejemplos: '1.5', '300', '2'.")
    Cultivo: str = Field(..., title="Cultivo Afectado/Tratado", description="Nombre del cultivo específico sobre el cual se realizó la acción o se observó el problema. Ejemplos: 'Trigo candeal', 'Olivo', 'Tomate para industria'.")
    Variedad_Cultivo: Optional[str] = Field(..., title="Variedad del Cultivo Afectado/Tratado", description="Variedad del cultivo específico sobre el cual se realizó la acción o se observó el problema. Ejemplos: 'Trigo candeal - *Variedad Anton*', 'Olivo - *Picual*', 'Tomate - *Cherry*'.")
    Superficie: Optional[float] = Field(..., title="Superficie Tratada/Afectada (ha)", description="Área total del terreno, expresada en hectáreas (ha), donde se realizó la aplicación, labor o se detectó el problema. Ejemplo: 25.5.")

    class Config:
        populate_by_name = True 
        json_schema_extra = {
            "example": {
                "created_at": "2024-07-15T10:30:00Z",
                "Fecha": "2024-07-14",
                "Tratamiento_fitosanitario": "Fungicida XPLUS",
                "Campaña": "ExploPrueba",
                "Año_campaña": "2025",
                "Plaga": "Presencia de oidio en hojas de pepino",
                "Dosis": "0.5",
                "Medida_dosis": "L/ha",
                "Cultivo": "Tomate",
                "Variedad_Cultivo": "Cherry",
                "Superficie": 2.5
            }
        }

class CampaignBase(BaseModel):
    # Campos para validar la campaña
    validated: Optional[bool] = None
    id: Optional[str] = None
    options: Optional[List[str]] = None
    need_choice: bool = False
    need_fix: bool = False

class CropBase(BaseModel):
    # Campos para validar el cultivo
    validated: Optional[bool] = None
    # IDs finalmente elegidos para ese cultivo/variedad
    sigpacs_ids: list[str] = []
    # Texto elegido (por ejemplo "Tomate - Cherry")
    selected_label: Optional[str] = None
    # Mapa: label → lista de IDs
    options: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    # superficie finalmente elegida para ese cultivo/variedad
    surface: float = 0.0
    need_choice: bool = False
    need_fix: bool = False

class MetadataOsigris(BaseModel):

    type: str = Field(default="Create")
    date: datetime = Field(default_factory=datetime.utcnow, title="Fecha de Creación", description="Marca de tiempo exacta (fecha y hora UTC) de cuándo se creó el registro en el sistema. Formato: AAAA-MM-DDTHH:MM:SSZ. Ejemplo: '2024-07-15T10:30:00Z'.")
    idorigin: int = Field(default=6)
    user: dict # resultado de hacer peticion GET al servicio osigrisapi/oauth/user/show con token. Revisar si nos sirve este objeto (devuelve User en vez de UserMetadata). Si no, crear objeto básico con type+id (obtenidos de api)

class InfoPhytosanitaryOsigris(BaseModel):

    type: str = Field(default="InfoPhytosanitary")
    id: int = Field(default=-1)
    subtype: dict # resultado de cuando busque "metenal" en osigris. Sería un diccionario? array de campos, json, .. Si no, crear objeto básico con type+id (obtenidos de api)
    inidate: datetime # podemos poner de hora las 09.00 de la mañana. Sería el campo "Fecha" del RecordBarse + la hora (RecordBase es date, no datetime)
    enddate: datetime # podemos poner de hora las 09.00 de la noche. Sería el campo "Fecha" del RecordBarse + la hora (RecordBase es date, no datetime)
    d: float # es la dosis del objeto RecordBase.
    md: dict # resultado de cuando busque el campo medida_dosis del objeto RecordBase en osigris. Sería un diccionario? array de campos, json, .. Si no, crear objeto básico con type+id (obtenidos de api)
    infection: dict # resultado de cuando busque el campo plaga del objeto RecordBase en osigris. Sería un diccionario? array de campos, json, .. Si no, crear objeto básico con type+id (obtenidos de api)
    metadata: list[MetadataOsigris]

class InfoPhytosanitaryParcelOsigris(BaseModel):
    """
    Clasifica y almacena los detalles de un registro de aplicación o labor agrícola.
    Esta clase está diseñada para ser interpretada por un LLM para la extracción de información
    y el registro estructurado de datos de campo.
    """
    type: str = Field(default="InfoPhytosanitaryParcel")
    info: InfoPhytosanitaryOsigris
    surface: float # aqui siempre tengo que mandar. si el usuario indica en RecordBase, poner ese campo, si no recoger el campo devuelto en el endpoint cuando filtro el cultivo en la campaña.
    idcp: List[int] = Field(None, title="Parcelas/Identificadores de Campo", description="Lista de IDs SIGPAC como enteros.")    
    
    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "idcp": "Invernadero Norte (Ref: INV-N-CS), Parcela Auxiliar (Ref: AUX-CS-01)"
            }
        }