from fastapi import APIRouter, Request


from app.lib.graphs.agent_with_tools.graph import ChatGraph
from app.lib.graphs.agent_with_tools.state import ChatState
from app.interfaces.llm import ChatLLM
import os        
from app.lib.graphs.agent_with_tools.tools.fitosanitarios import check_fitosanitarios,available_fitosanitarios
from app.lib.graphs.agent_with_tools.tools.osigris import validar_explotacion
from app.lib.graphs.agent_with_tools.tools.record import save_record,create_record
from app.lib.graphs.agent_with_tools.tools.utils import get_current_date

MODEL_VERSION = os.getenv("MODEL_VERSION")
router = APIRouter()

agent_with_tools_graph = ChatGraph(llm=ChatLLM().get_openai_llm(model_name=MODEL_VERSION), tools=[validar_explotacion,check_fitosanitarios,save_record,create_record,get_current_date,available_fitosanitarios]).graph()


@router.post("/agent_with_tools")
async def run_graph(state: ChatState):
    from app.prompts import AGENT_WITH_TOOLS_NODE
    messages = [
            {"role": "system", "content": AGENT_WITH_TOOLS_NODE.format(user_id=state.user_id,name=state.name)}
        ]
    state.messages= messages
    response = await agent_with_tools_graph.ainvoke_graph(state)
    return response