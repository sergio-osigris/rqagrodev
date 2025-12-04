from pydantic import BaseModel,Field
from typing import Annotated, Literal, Optional
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
    ccheck_errors: List[str] = Field(default_factory=list)
    check_status: Optional[str | None] = None
    check_messages: list[str] = Field(default_factory=list)
    # osigris_token:

    # para campaña
    campaign_validated: Optional[bool] = None
    campaign_id: Optional[str] = None
    campaign_options: Optional[List[Dict[str, Any]]] = None
    campaign_need_choice: bool = False
    campaign_need_fix: bool = False

    class Config:
        arbitrary_types_allowed = True