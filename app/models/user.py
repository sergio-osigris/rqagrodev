from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class User(BaseModel):
    id: UUID = Field(default_factory=UUID, title="User ID", description="Unique identifier for the user")
    name: str = Field(..., title="Name", description="Full name of the user")
    phone: str = Field(..., title="Phone", description="Phone number of the user")
    email: Optional[str] = Field(..., title="Email", description="Email address of the user")
    dni: Optional[str] = Field(..., title="DNI", description="National ID number of the user")
    created_at: datetime = Field(default_factory=datetime.utcnow, title="Created At", description="Timestamp when the user was created")
    user_id: Optional[UUID] = Field(default_factory=UUID, title="User ID", description="Unique identifier for the user in the system")

