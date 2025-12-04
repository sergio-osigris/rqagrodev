from fastapi import APIRouter, Request


from app.lib.graphs.agent_with_tools.graph import ChatGraph
from app.lib.graphs.agent_with_tools.state import ChatState
from app.interfaces.llm import ChatLLM
import os        
from app.lib.graphs.agent_with_tools.tools.fitosanitarios import check_fitosanitarios,available_fitosanitarios
from app.lib.graphs.agent_with_tools.tools.osigris import validar_explotacion, validar_cultivo
from app.lib.graphs.agent_with_tools.tools.record import create_record
from app.lib.graphs.agent_with_tools.tools.utils import get_current_date
from app.utils.pydantic_formatters import generar_listado_campos
from app.models.record2 import RecordBase
import datetime
from datetime import date
MODEL_VERSION = os.getenv("MODEL_VERSION")
router = APIRouter()

agent_with_tools_graph = ChatGraph(llm=ChatLLM().get_openai_llm(model_name=MODEL_VERSION), tools=[create_record,get_current_date]).graph()


@router.post("/agent_with_tools")
async def run_graph(state: ChatState):
    from app.prompts import AGENT_WITH_TOOLS_NODE
    messages = [
            {"role": "system", "content": AGENT_WITH_TOOLS_NODE.format(user_id="00",name="Daniel García",size=500,listado_campos=generar_listado_campos(RecordBase),current_date=datetime.datetime.now().strftime("%Y-%m-%d"))}
        ]
    state.messages= messages
    response = await agent_with_tools_graph.ainvoke(state)
    return response

@router.post("/invoke_ai")
async def run_graph(message: str):
    from app.prompts import AGENT_WITH_TOOLS_NODE
    state = ChatState(user_id="00",name="test",record_generated=False,messages=[],record=RecordBase(Fecha=date.today(), Tratamiento_fitosanitario="",Campaña="",Año_Campaña="",Plaga="",Dosis=0, Medida_dosis="", Cultivo="", Superficie=0 ))
    messages = [
            {"role": "system", "content": AGENT_WITH_TOOLS_NODE.format(user_id="00",name="Daniel García",size=500,listado_campos=generar_listado_campos(RecordBase),current_date=datetime.datetime.now().strftime("%Y-%m-%d"))},
            {"role": "user", "content":message}
        ]
    state.messages= messages
    response = await agent_with_tools_graph.ainvoke(state)
    return response