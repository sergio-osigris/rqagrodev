from pydantic import BaseModel,Field
from typing import Annotated, Literal, Optional
from langchain_core.messages import BaseMessage
import operator
from typing import List,Dict, Any
from app.models.record2 import RecordBase, CampaignBase, CropBase

class ChatState(BaseModel):
    # We store a pure Python list of dicts:
    #   {"role": <str>, "content": <str>}
    messages: List[Dict[str, Any]] = []
    user_id: str = Field(description="User id from names table")
    name: str = Field(description="Full name of user")
    record_generated: bool = Field(description="Indicates if the current conversation has already been generated a new record in recolector phase.",default=False)
    record: RecordBase = Field(description="")
    record_to_save: bool = Field(description="Indica si el record se puede guardar ya.",default=False)
    # osigris_token:

    campaign: CampaignBase = Field(default_factory=CampaignBase)
    crop: CropBase = Field(default_factory=CropBase)
    infection_validated: bool = Field(description="Indica si la infeccion ya está validada.",default=False)
    measure_validated: bool = Field(description="Indica si la medida ya está validada.",default=False)
    phytosanitary_validated: bool = Field(description="Indica si el fitosanitario ya está validado.",default=False)
    
    check_errors: List[str] = Field(default_factory=list)
    check_status: Optional[str | None] = None
    check_messages: list[str] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True