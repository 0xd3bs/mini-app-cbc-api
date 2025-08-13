from typing import Optional
from pydantic import BaseModel

class PredictionResponse(BaseModel):
    prediction: str
    tokenToBuy: Optional[str] = None
    value: Optional[float] = None
