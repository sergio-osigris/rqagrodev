from pydantic import BaseModel,Field
from typing import Annotated, Literal
from langchain_core.messages import BaseMessage
import operator
from typing import List,Dict, Any
from app.models.record2 import RecordBase

class ChatState(BaseModel):
    # We store a pure Python list of dicts:
    #   {"role": <str>, "content": <str>}
    messages: List[Dict[str, Any]] = []
    user_id: str = Field(description="User id from names table")
    name: str = Field(description="Full name of user")
    record_generated: bool = Field(description="Indicates if the current conversation has already been generated a new record.",default=False)
    record: RecordBase = Field(description="")
    check_errors: list[str] = []
    check_status: str | None = None
    check_messages: list[str] = Field(default_factory=list)
    # osigris_token:

    class Config:
        arbitrary_types_allowed = True