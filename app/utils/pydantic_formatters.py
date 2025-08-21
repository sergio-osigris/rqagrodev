def generar_listado_campos(model):
    """
    Recorre los campos de un modelo Pydantic y devuelve
    un texto ya formateado para incluir en el prompt.
    """
    texto_campos = []
    for nombre_atributo, field_info in model.__fields__.items():
        alias = field_info.alias or nombre_atributo
        descripcion = field_info.description or ""
        texto_campos.append(f"- **{alias}**: {descripcion}")
    return "\n".join(texto_campos)