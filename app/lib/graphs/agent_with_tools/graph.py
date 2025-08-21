import logging, json, uuid

from langchain.tools import BaseTool
from langgraph.graph import StateGraph, END, START

from app.lib.graphs.agent_with_tools.nodes import actions
from app.lib.graphs.agent_with_tools.state import ChatState
from app.lib.graphs.agent_with_tools.nodes.tool_call import CustomToolNode
class ChatGraph:
    def __init__(self,llm, tools: list[BaseTool]):
        self.tools = tools
        self.chat_message_history = []
        self.llm = llm
        if len(self.tools) > 0:
            self.llm = self.llm.bind_tools(self.tools)

    def graph(self):
        """
        Builds the chat workflow graph.
        """
        workflow = StateGraph(ChatState)

        agent_actions = actions.ChatAgentActions(llm=self.llm, tools=self.tools)

        def should_continue(state: ChatState):
            messages = state.messages
            last_message = messages[-1]
            text = last_message.get("content", "")
            if text.startswith("Calling ") and " with arguments " in text:
                return "continue"
            return END

        workflow.add_node("agent", agent_actions.call_model)
        # workflow.add_node("action", ToolNode(tools=self.tools))
        workflow.add_node("action", CustomToolNode(self.tools))

        workflow.set_entry_point("agent")

        workflow.add_conditional_edges(
            "agent", should_continue, {"continue": "action", END: END}
        )
        workflow.add_edge("action", "agent")
        return workflow.compile()


if __name__ == "__main__":
    import asyncio
    import datetime
    async def main():
        # Example usage
        from langchain_openai import ChatOpenAI
        from langchain.tools import Tool
        from app.lib.graphs.agent_with_tools.tools.fitosanitarios import check_fitosanitarios,available_fitosanitarios
        from app.lib.graphs.agent_with_tools.tools.record import save_record,create_record
        from app.lib.graphs.agent_with_tools.tools.utils import get_current_date
        from dotenv import load_dotenv, find_dotenv
        from app.prompts import AGENT_WITH_TOOLS_NODE
        from app.utils.pydantic_formatters import generar_listado_campos
        from app.models.record import RecordRequest
        import sys
        _: bool = load_dotenv(find_dotenv())    

        llm = ChatOpenAI(model_name="gpt-4o-2024-11-20")
        tools = [check_fitosanitarios,save_record,create_record,get_current_date,available_fitosanitarios]
        
        chat_graph = ChatGraph(llm=llm, tools=tools)
        workflow = chat_graph.graph()
        user_id = str(uuid.uuid4())
        messages = [
            {"role": "system", "content": AGENT_WITH_TOOLS_NODE.format(user_id=user_id,name="Daniel García",size=500,listado_campos=generar_listado_campos(RecordRequest),current_date=datetime.datetime.now().strftime("%Y-%m-%d"))},
        ]
        while True:
            user_input = input("You: ")
            if user_input.strip().lower() == "q":
                print("Exiting.")
                try:
                    for msg in messages:
                        print(msg)
                except Exception as e:
                    print(f"Error saving conversation: {e}")
                break
            messages.append({"role": "user", "content":user_input})
            response = await workflow.ainvoke(ChatState(messages=messages, user_id=user_id,name="Daniel García"))
            print("Assistant:", response['messages'][-1]['content'])
            messages = response['messages']
    asyncio.run(main())