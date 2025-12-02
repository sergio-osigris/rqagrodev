from pydantic import BaseModel,Field
from typing import Annotated, Literal
from langchain_core.messages import BaseMessage
import operator
from typing import List,Dict
from app.models.record2 import RecordBase

class ChatState(BaseModel):
    # We store a pure Python list of dicts:
    #   {"role": <str>, "content": <str>}
    messages: List[Dict[str, str]]
    user_id: str = Field(description="User id from names table")
    name: str = Field(description="Full name of user")
    record_added: bool = Field(description="Indicates if the current conversation has already been saved to a new record.",default=False)
    record: RecordBase = Field(description="")

    class Config:
        arbitrary_types_allowed = True