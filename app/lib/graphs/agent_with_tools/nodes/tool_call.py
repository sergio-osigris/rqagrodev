import json
import re
from langchain.tools.base import BaseTool
from langchain_core.messages import (
    ToolMessage,
)
import uuid
import logging
from app.lib.graphs.agent_with_tools.state import ChatState
from app.models.record2 import RecordBase
from pydantic import BaseModel
class CustomToolNode:
    """
    A Node that:
      - Looks at state.messages[-1], which must be a dict {"sender":..., "message":...}.
      - If message starts with "Calling {tool} with arguments {json}", it:
          • parses out the tool name
          • loads JSON args
          • invokes tool.invoke(**args)
          • appends a new dict {"sender": f"Tool {tool_name}", "message": observation}
      - Otherwise it does nothing.
    """

    def __init__(self, tools: list[BaseTool]):
        # Build a lookup from tool-name → tool instance
        self.tools_by_name = {tool.name: tool for tool in tools}

    async def __call__(self, state: ChatState):
        logging.info("CALLING TOOLS")
        last_entry = state.messages[-1]
        tool_calls = last_entry.get("tool_calls", [])

        if not tool_calls:
            return state

        # Si sólo quieres ejecutar el primer tool_call:
        tc = tool_calls[0]
        func = tc["function"]
        tool_name = func["name"]
        args_json = func["arguments"]
        incoming_tool_id = tc["id"]

        try:
            args = json.loads(args_json)
        except json.JSONDecodeError:
            state.messages.append({
                "role": "assistant",
                "content": f"Could not parse arguments: {args_json}",
            })
            return state

        tool = self.tools_by_name.get(tool_name)
        if tool is None:
            state.messages.append({
                "role": "assistant",
                "content": f"No tool named '{tool_name}' registered.",
            })
            return state

        try:
            observation = await tool.ainvoke(args)
        except Exception as e:
            logging.info(f"Error Procesing tool. Error code: {e}")
            state.messages.append({
                "role": "assistant",
                "content": f"{tool_name} Error during invocation: {str(e)}",
            })
            return state

        #  4) Normalizar observation → string para meter en messages
        if isinstance(observation, BaseModel):
            obs_for_llm = observation.model_dump_json()
        elif isinstance(observation, dict):
            obs_for_llm = json.dumps(observation)
        else:
            obs_for_llm = str(observation)
        # Aquí está el cambio importante:
        # Añadimos un mensaje de rol "tool", no "assistant"
        state.messages.append({
            "role": "tool",
            "tool_call_id": incoming_tool_id,
            "name": tool_name,
            "content": obs_for_llm,
        })

        if tool_name == "SaveRecord":
            state.record_added = True
        if tool_name == "CreateRecord":
            # Aquí quieres guardar el RecordBase en el estado
            if isinstance(observation, RecordBase):
                state.record = observation
            elif isinstance(observation, dict):
                state.record = RecordBase(**observation)
            else:
                # En caso raro, lo dejamos como está para no petar
                logging.info(f"Unexpected type for CreateRecord observation: {type(observation)}")

        return state
    
