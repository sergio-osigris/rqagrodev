from pydantic import BaseModel, Field
from typing import Optional,Literal
from datetime import datetime, date
class Record(BaseModel):
    """
    Representa un registro detallado de una incidencia agrícola, incluyendo detalles de la aplicación,
    observaciones y metadatos. Diseñada para ser interpretada por un LLM para almacenamiento
    y recuperación estructurada de datos.
    """
    id: int = Field(..., title="ID del Registro", description="Identificador numérico único y secuencial asignado al registro en la base de datos. Ejemplo: 101.")
    created_at: datetime = Field(default_factory=datetime.utcnow, title="Fecha de Creación", description="Marca de tiempo exacta (fecha y hora UTC) de cuándo se creó el registro en el sistema. Formato: AAAA-MM-DDTHH:MM:SSZ. Ejemplo: '2024-07-15T10:30:00Z'.")
    Nombre: str = Field(..., title="Nombre Asociado al Registro", description="Nombre completo de la persona o entidad principal asociada a este registro (ej. agricultor, técnico). Ejemplo: 'Carlos Sánchez'.")
    Fecha: date = Field(..., title="Fecha de la Incidencia/Aplicación", description="Fecha principal en la que ocurrió la labor, aplicación o se observó la incidencia. Formato: AAAA-MM-DD. Ejemplo: '2024-07-14'.")
    Tipo_de_incidencia: Literal["None","Labor", "Fitosanitario", "Fertilizante"] = Field(..., alias="Tipo de incidencia", description="Categoría principal de la incidencia registrada. Indica si es una 'Labor' (ej. siembra, poda), una aplicación de 'Fitosanitario', un 'Fertilizante', o 'None' si no aplica. Ejemplo: 'Fitosanitario'.")
    Tratamiento_fertilizante_labor: str = Field(..., alias="Tratamiento/ fertilizante / labor", description="Nombre específico del tratamiento, producto fertilizante, o tipo de labor realizada. Ejemplos: 'Azoxystrobin 25%', 'Abonado de fondo NPK 15-15-15', 'Poda de formación', 'Siembra directa'.")
    Campaña: str = Field("", alias="Nombre de la campaña", description="Nombre/alias específico de la campaña. Ejemplos: 'Prueba', 'Explotacion'.")
    Año_campaña: str = Field("", alias="Año de la campaña", description="Año en el que se realiza la campaña. Ejemplos: '2023', '2024', '2022', '2025'.")
    Medida_dosis: Optional[str] = Field("", alias="Medida de la dosis", description="Medida de la dosis aplicada. Ejemplos: 'kg/ha', 'l/ha'.")
    Dimension: Optional[str] = Field("", alias="Dimension", description="Dimension de la parcela. Ejemplos: '100.541', '145'.")
    Problema_en_campo: Optional[str] = Field(..., alias="Problema en campo", description="Descripción detallada del problema o plaga detectada en el campo que motivó la acción. Ejemplos: 'Fuerte ataque de mildiu en hojas basales', 'Clorosis férrica en brotes jóvenes', 'Compactación del suelo post-lluvias'.")
    Dosis: Optional[str] = Field(..., title="Dosis Aplicada", description="Cantidad del producto (fitosanitario o fertilizante) aplicado, especificando las unidades. Ejemplos: '1.5 L/ha', '300 kg/ha', '2 cc/L de agua'.")
    Caldo: Optional[str] = Field(..., title="Tipo de Caldo o Mezcla", description="Descripción del tipo de mezcla o solución utilizada, si aplica, especialmente para fitosanitarios. No la cantidad, sino la naturaleza. Ejemplos: 'Suspensión concentrada (SC)', 'Mojante + Fungicida', 'Solución madre'. Si es una cantidad, usar el campo Dosis o especificar aquí si es volumen total de mezcla. Para aplicaciones en seco, puede ser 'No aplica' o nulo.")
    Cultivo: Optional[str] = Field(..., title="Cultivo Afectado/Tratado", description="Nombre del cultivo específico sobre el cual se realizó la acción o se observó el problema. Incluir variedad si es relevante. Ejemplos: 'Trigo candeal - Variedad Anton', 'Olivo - Picual', 'Tomate para industria'.")
    Superficie: Optional[float] = Field(..., title="Superficie Tratada/Afectada (ha)", description="Área total del terreno, expresada en hectáreas (ha), donde se realizó la aplicación, labor o se detectó el problema. Ejemplo: 25.5.")
    Aplicador: Optional[str] = Field(..., title="Nombre del Aplicador/Realizador", description="Nombre de la persona o empresa que ejecutó la aplicación del producto o realizó la labor en campo. Ejemplo: 'Servicios Agrícolas Paco S.L.', 'Juan Pérez (Nº Carnet: XXXXX)'.")
    archivo_adjunto: Optional[str] = Field(None, alias="archivo adjunto", title="Archivo Adjunto (Ruta o URL)", description="Ruta del sistema de archivos, URL o identificador del archivo adjunto asociado a este registro (ej. foto, análisis, factura). Ejemplo: '/mnt/share/fotos_campo/mildiu_vid_20240714.jpg', 'https://example.com/informe.pdf'.")
    feedback: Optional[str] = Field(None, title="Retroalimentación/Comentarios Adicionales", description="Comentarios, notas, observaciones adicionales o retroalimentación sobre la efectividad del tratamiento, la labor, o cualquier otro aspecto del registro. Ejemplo: 'Tratamiento efectivo, se observó mejora a los 3 días.'")
    telefono_movil: Optional[str] = Field(None, alias="telefono movil", title="Teléfono Móvil de Contacto", description="Número de teléfono móvil de la persona asociada al registro, para contacto rápido. Formato internacional preferido si es posible. Ejemplo: '+34600123456'.")
    user_id: Optional[str] = Field(..., title="ID de Usuario Propietario", description="Identificador único del usuario del sistema que creó o es propietario de este registro. Ejemplo: 'user_carlos_sanchez_789'.")
    parcelas: Optional[str] = Field(None, title="Parcelas/Identificadores de Campo", description="Identificador(es) o nombre(s) de las parcelas, lotes o recintos SIGPAC donde se realizó la acción. Si son múltiples, separar por comas o punto y coma. Ejemplos: 'Parcela El Robledal (Polígono 3, Parcela 45)', 'Lote A-1; Lote B-3'.")

    class Config:
        populate_by_name = True 
        json_schema_extra = {
            "example": {
                "id": 101,
                "created_at": "2024-07-15T10:30:00Z",
                "Nombre": "Carlos Sánchez",
                "Fecha": "2024-07-14",
                "Tipo de incidencia": "Fitosanitario",
                "Tratamiento/ fertilizante / labor": "Fungicida XPLUS",
                "Campaña": "ExploPrueba",
                "Año_campaña": "2025",
                "Problema en campo": "Presencia de oidio en hojas de pepino",
                "Dosis": "0.5 L/ha",
                "Medida_dosis": "L/ha",
                "Dimension": "145.023",
                "Caldo": "Mezcla con adherente YZ",
                "Cultivo": "Pepino Almería - Invernadero Norte",
                "Superficie": 2.5,
                "Aplicador": "Laura Martín (Carnet Aplicador: 98765Z)",
                "archivo adjunto": "https://example.com/fotos/oidio_pepino_20240714.jpg",
                "feedback": "Revisar efectividad en 5 días. Próxima aplicación programada según calendario.",
                "telefono movil": "+34600112233",
                "user_id": "user_carlos_sanchez_789",
                "parcelas": "Invernadero Norte (Ref: INV-N-CS), Parcela Auxiliar (Ref: AUX-CS-01)"
            }
        }




class RecordRequest(BaseModel):
    """
    Clasifica y almacena los detalles de un registro de aplicación o labor agrícola.
    Esta clase está diseñada para ser interpretada por un LLM para la extracción de información
    y el registro estructurado de datos de campo.
    """
    user_id: str = Field(..., title="ID de Usuario", description="Identificador único y persistente del usuario que realiza o está asociado a este registro. Ejemplo: 'user_abc_123'.")
    Tipo_de_incidencia: Literal["None", "Labor", "Fitosanitario", "Fertilizante"] = Field(..., alias="Tipo de incidencia", description="Categoría principal del registro. Indica si la entrada corresponde a una 'Labor' agrícola general, una aplicación de 'Fitosanitario', o el uso de un 'Fertilizante'. Seleccionar 'None' si no aplica.")
    Tratamiento_fertilizante_labor: str = Field("", alias="Nombre del fitosanitario", description="Nombre específico del tratamiento, producto fertilizante, o tipo de labor realizada. Ejemplos: 'Azoxystrobin 25%', 'Abonado de fondo NPK 15-15-15', 'Poda de formación', 'Siembra directa'.")
    Campaña: str = Field("", alias="Nombre de la campaña", description="Nombre/alias específico de la campaña. Ejemplos: 'Prueba', 'Explotacion'.")
    Año_campaña: str = Field("", alias="Año de la campaña", description="Año en el que se realiza la campaña. Ejemplos: '2023', '2024', '2022', '2025'.")
    Problema_en_campo: Optional[str] = Field("", alias="Problema en campo", description="Descripción textual del problema observado en el campo que motivó la acción. Ejemplos: 'Pulgón en tomate', 'Mildiu en vid', 'Necesidad de aporte de nitrógeno', 'Terreno compactado'.")
    Dosis: Optional[str] = Field("", title="Dosis Aplicada", description="Cantidad del producto (fitosanitario o fertilizante) aplicado, incluyendo unidades. Fundamental para el seguimiento y la seguridad. Ejemplo: '50 kg'.")
    Medida_dosis: Optional[str] = Field("", alias="Medida de la dosis", description="Medida de la dosis aplicada. Ejemplos: 'kg/ha', 'l/ha'.")
    Dimension: Optional[str] = Field("", alias="Dimension", description="Dimension de la parcela. Ejemplos: '100.541', '145'.")
    Cultivo: Optional[str] = Field("", title="Cultivo Tratado", description="Nombre del cultivo específico que recibió la aplicación o sobre el cual se realizó la labor. Ejemplos: 'Tomate pera', 'Viñedo Tempranillo', 'Trigo duro', 'Oliveral Picual'.")
    Superficie: Optional[float] = Field(None, title="Superficie (ha)", description="Área total del terreno donde se realizó la aplicación o labor, expresada en hectáreas (ha). Ejemplo: 10.5.")
    Fecha: date = Field(default_factory=date.today, title="Fecha de Aplicación/Labor", description="Fecha en la que se realizó la aplicación del producto o la labor agrícola. Formato esperado: AAAA-MM-DD. Por defecto, se usará la fecha actual.")
    Caldo: Optional[float] = Field(0.0, title="Volumen de Caldo (L)", description="Cantidad total de mezcla líquida (producto + agua) utilizada en la aplicación, expresada en litros (L). Para aplicaciones en seco o si no aplica, usar 0.")
    Aplicador: Optional[str] = Field("", title="Nombre del Aplicador", description="Nombre completo de la persona o empresa responsable que ejecutó la aplicación del tratamiento o la labor en campo. Por defecto el mismo que 'name'")
    parcelas: Optional[str] = Field("", title="Parcelas/Identificadores de Campo", description="Identificador(es) o nombre(s) de las parcelas o recintos SIGPAC donde se realizó la acción. Si son múltiples, separar por comas. Ejemplos: 'Parcela La Loma', 'Polígono 1, Parcela 102, 103'.")
    Nombre: str = Field(..., description="Nombre completo del usuario que crea o a quien pertenece el registro. Utilizado para referencia y visualización. Ejemplo: 'Ana Pérez'.")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "user_id": "user_ana_perez_456",
                "Tipo de incidencia": "Fitosanitario",
                "Tratamiento/ fertilizante / labor": "Metenal",
                "Campaña": "ExploPrueba",
                "Año_campaña": "2025",
                "Problema en campo": "Ataque severo de mildiu en hojas",
                "Dosis": "10kg ",
                "Medida_dosis": "L/ha",
                "Dimension": "145.023",
                "Cultivo": "Viñedo - variedad Albariño",
                "Superficie": 12.5,
                "Fecha": "2024-07-15",
                "Caldo": 600.0,
                "Aplicador": "Ana Pérez",
                "parcelas": "Viña Alta (SIGPAC: 33001A002003200000AB), Viña Baja (SIGPAC: 33001A002003210000AC)",
                "Nombre": "Ana Pérez"
            }
        }