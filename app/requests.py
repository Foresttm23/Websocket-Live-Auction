from pydantic import BaseModel, Field, computed_field
from models import LotStatus
from datetime import datetime


class BidRequest(BaseModel):
    # lot_id: int = Field(gt=0)  Not used since lot_id is passed in `Path` endpoint
    bidder: str = Field(min_length=1)
    amount: int = Field(gt=0)

    model_config = {
        "json_schema_extra": {
            "example": {
                # "lot_id": "1",
                "bidder": "Maks",
                "amount": "100",
            }
        }
    }


class LotRequest(BaseModel):
    title: str = Field(min_length=3)
    start_price: int = Field(gt=0)
    status: LotStatus = Field(description="Status of the lot")

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Shoes",
                "start_price": "100",
                "status": "running",
            }
        }
    }


class LotResponse(BaseModel):
    id: int
    title: str
    status: str
    start_time: datetime
    end_time: datetime

    @computed_field
    @property
    def time_till_end(self) -> float:
        return max((self.end_time - datetime.utcnow()).total_seconds(), 0)

    class Config:
        from_attributes = True
