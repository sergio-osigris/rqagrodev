import logging, re, json

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain.chat_models.base import BaseChatModel
from langchain_core.tools import BaseTool
from langgraph.prebuilt import ToolInvocation, ToolExecutor
from app.lib.graphs.agent_with_tools.state import ChatState


class ChatAgentActions:
    def __init__(self, llm: BaseChatModel, tools: list[BaseTool]):
        self.llm = llm
        self.tools = tools
        self.tool_executor = ToolExecutor(tools=tools)

    def call_model(self, state: ChatState):
        response: AIMessage = self.llm.invoke(input=state.messages)

        msg_dict = {
            "role": "assistant",
            "content": response.content or "",
        }

        tool_calls = response.additional_kwargs.get("tool_calls")
        if tool_calls:
            msg_dict["tool_calls"] = tool_calls

        state.messages.append(msg_dict)

        state.campaign_validated = False
        state.campaign_need_choice = False
        state.campaign_need_fix = False
        state.campaign_id = None
        state.campaign_options = None
        state.check_errors = []      
        state.check_messages = []    
        state.check_status = None 
        
        print("ACTIONS: ")
        # print(state)
        return state
    
    