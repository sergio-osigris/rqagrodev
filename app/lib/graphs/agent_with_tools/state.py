from pydantic import BaseModel,Field
from typing import Annotated, Literal, Optional
from langchain_core.messages import BaseMessage
import operator
from typing import List,Dict, Any
from app.models.record2 import RecordBase, CampaignBase

class ChatState(BaseModel):
    # We store a pure Python list of dicts:
    #   {"role": <str>, "content": <str>}
    messages: List[Dict[str, Any]] = []
    user_id: str = Field(description="User id from names table")
    name: str = Field(description="Full name of user")
    record_generated: bool = Field(description="Indicates if the current conversation has already been generated a new record in recolector phase.",default=False)
    record: RecordBase = Field(description="")
    # osigris_token:

    campaign: CampaignBase = Field(default_factory=CampaignBase)
    
    check_errors: List[str] = Field(default_factory=list)
    check_status: Optional[str | None] = None
    check_messages: list[str] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True