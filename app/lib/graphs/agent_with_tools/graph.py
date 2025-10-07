import logging
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
            self.llm = self.llm.bind_tools(self.tools)

    def graph(self):
        workflow = StateGraph(ChatState)
        agent_actions = actions.ChatAgentActions(llm=self.llm, tools=self.tools)

        def should_continue(state: ChatState):
            if not state.fitosanitario_validado or not state.campaña_validada:
                return "continue"
            return END

        workflow.add_node("agent", agent_actions.call_model)
        workflow.add_node("action", CustomToolNode(self.tools))
        workflow.set_entry_point("agent")
        workflow.add_conditional_edges(
            "agent", should_continue, {"continue": "action", END: END}
        )
        workflow.add_edge("action", "agent")
        return workflow.compile()
