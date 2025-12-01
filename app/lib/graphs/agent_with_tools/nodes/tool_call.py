import json
import re
from langchain_core.tools import BaseTool
import uuid
import logging
from app.lib.graphs.agent_with_tools.state import ChatState
from app.models.record2 import RecordBase
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
        # 1) Grab the last formatted message (a dict)
        logging.info("CALLING TOOLS")
        last_entry = state.messages[-1]
        sender = last_entry.get("role", "")
        text = last_entry.get("content", "")
        incoming_tool_id = last_entry.get("tool_call_id", str(uuid.uuid4()))


        # 2) Only proceed if this was an Assistant→tool-call line
        #    We expect exactly: "Calling FooTool with arguments {...}"
        if sender == "assistant" and text.startswith("Calling ") and " with arguments " in text:
            # 3) Extract the tool name and the JSON args via regex
            #    Regex breakdown:
            #      ^Calling (\w+)   → captures the tool name (letters/numbers/underscore)
            #       with arguments (.*)$ → captures everything after " with arguments "
            m = re.match(r"^Calling (\w+) with arguments (.*)$", text)
            if not m:
                # If it doesn't match exactly, we do nothing
                return state

            tool_name = m.group(1)
            args_json = m.group(2).strip()

            # 4) Load the JSON arguments into a Python dict
            try:
                args = json.loads(args_json)
            except json.JSONDecodeError:
                # If malformed JSON, append an error message and return
                state.messages.append({
                    "role": "assistant",
                    "content": f"Could not parse arguments: {args_json}",
                'tool_call_id' : incoming_tool_id
                })
                return state

            # 5) Look up the correct tool
            tool = self.tools_by_name.get(tool_name)
            if tool is None:
                state.messages.append({
                    "role": "assistant",
                    "content": f"No tool named '{tool_name}' registered.",
                'tool_call_id' : incoming_tool_id
                })
                return state

            # 6) Invoke the tool. Many tools have signature invoke(**kwargs), adjust if yours differ:
            try:
                observation = await tool.ainvoke(input=args,id=incoming_tool_id)
            except Exception as e:
                logging.info(f"Error Procesing tool. Error code: {e}")
                print(e)
                # If the tool itself raises, capture that
                state.messages.append({
                    "role": f"assistant",
                    "content": f" {tool_name} " +f"Error during invocation: {str(e)}",
                'tool_call_id' : incoming_tool_id
                })
                return state

            # 7) Append the tool's response in the same two‐field format
            state.messages.append({
                "role": f"assistant",
                "content": f" {tool_name} " + observation if isinstance(observation, str) else str(observation),
                'tool_call_id' : incoming_tool_id
            })
            if tool_name == "SaveRecord":
                state.record_added = True
            if tool_name == "CreateRecord":
                record = RecordBase(**observation)
                state.record = record
        # If last message wasn’t a “Calling …” line, we do nothing (so no tool is run).
        return state
    
