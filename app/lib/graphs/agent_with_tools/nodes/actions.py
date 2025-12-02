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
        """
        1. Turn state.messages (list of dicts) back into proper BaseMessage objects for the LLM.
           For simplicity, we'll assume each dict has `{'sender':"User"/"Assistant", 'message':<content>}`
           so we can reconstruct HumanMessage / AIMessage stubs. In your real code, you might keep
           a parallel list of raw BaseMessages so you don't have to rebuild them here.
        2. Invoke the LLM, get back an AIMessage (with or without tool_calls).
        3. Convert that AIMessage into a two-field dict. If it has tool_calls, we turn it into:
             {"sender":"Assistant", "message": "Calling FooTool with arguments {...}"}.
           Otherwise, it's:
             {"sender":"Assistant", "message": <AIMessage.content>}
        4. Return {"messages":[ new_dict ]}.
        """
        response: AIMessage = self.llm.invoke(input=state.messages)
        # 2) Turn that AIMessage into our two‐field dict (tool‐call vs. normal)
        if "tool_calls" in response.additional_kwargs and response.additional_kwargs["tool_calls"]:
            # Keep only the first tool_call if multiple returned
            func = response.additional_kwargs["tool_calls"][0]["function"]
            tool_id = response.additional_kwargs["tool_calls"][0]["id"]

            tool_name = func["name"]
            tool_args = func["arguments"]
            formatted = {
                "role": "assistant",
                "tool_call_id": tool_id, 
                "content": f"Calling {tool_name} with arguments {tool_args}"
            }
            # Make sure the LLM’s content is blank so that no text is inserted
            response.content = ""
        else:
            formatted = {
                "role": "assistant",
                "content": response.content or ""
            }
        state.messages.append(formatted)
        print(state)
        return state
    
    