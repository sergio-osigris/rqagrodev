import logging
import json
import uuid
from typing import List

from langchain.tools import BaseTool
from langgraph.graph import StateGraph, END

from app.lib.graphs.agent_with_tools.nodes import actions
from app.lib.graphs.agent_with_tools.state import ChatState
from app.lib.graphs.agent_with_tools.nodes.tool_call import CustomToolNode

class ChatGraph:
    def __init__(self, llm, tools: List[BaseTool]):
        self.tools = tools
        self.chat_message_history = []
        self.llm = llm
        if len(self.tools) > 0:
            # Bind tools al LLM si se han definido
            self.llm = self.llm.bind_tools(self.tools)

    def graph(self):
        """
        Builds the chat workflow graph.
        """
        workflow = StateGraph(ChatState)

        agent_actions = actions.ChatAgentActions(llm=self.llm, tools=self.tools)

        def should_continue(state: ChatState):
            # Solo continuar si hay herramientas pendientes por usar
            if not state.fitosanitario_validado or not state.campaña_validada:
                return "continue"
            return END

        # Nodo del agente que decide qué acción hacer
        workflow.add_node("agent", agent_actions.call_model)

        # Nodo de ejecución de herramientas
        workflow.add_node("action", CustomToolNode(self.tools))

        # Nodo de entrada del grafo
        workflow.set_entry_point("agent")

        # Conexiones condicionales: si hay herramientas pendientes, ir a 'action'
        workflow.add_conditional_edges(
            "agent", should_continue, {"continue": "action", END: END}
        )

        # Después de ejecutar herramienta, volver al agente
        workflow.add_edge("action", "agent")

        return workflow.compile()
