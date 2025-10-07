from typing import List
from langchain.tools import BaseTool
from app.lib.graphs.agent_with_tools.state import ChatState

class CustomToolNode:
    """
    Nodo encargado de llamar a las herramientas del agente de manera controlada.
    """
    def __init__(self, tools: List[BaseTool]):
        self.tools = {tool.name: tool for tool in tools}

    async def __call__(self, state: ChatState):
        user_msg = state.messages[-1]["content"]

        # 1️⃣ Validar fitosanitario si no se ha validado
        if not state.fitosanitario_validado and "nombre_fitosanitario" in user_msg:
            result = await self.tools["CheckFitosanitario"].run(user_msg)
            state.fitosanitario = result
            state.validar_fitosanitario()
            state.messages.append({"role": "assistant", "content": result})
            return {"messages": state.messages}

        # 2️⃣ Validar campaña y año si fitosanitario ya validado
        elif state.fitosanitario_validado and not state.campaña_validada \
                and "campaña" in user_msg and "año" in user_msg:
            result = await self.tools["ComprobarExplotacion"].run(user_msg)
            if result.lower() == "si":
                state.validar_campaña()
            state.messages.append({"role": "assistant", "content": result})
            return {"messages": state.messages}

        # 3️⃣ Faltan datos
        state.messages.append({"role": "assistant", "content": "Faltan datos necesarios, por favor indica..."})
        return {"messages": state.messages}
