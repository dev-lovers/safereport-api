from typing import Optional
from pydantic import BaseModel


class LocationSchema(BaseModel):
    country: str
    state: str
    city: str
    street: Optional[str] = None
    neighborhood: Optional[str] = None
