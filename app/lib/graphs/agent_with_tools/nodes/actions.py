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
        
        print("ACTIONS: ")
        # print(state)
        return state
    
    