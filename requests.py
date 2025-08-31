from pydantic import BaseModel, Field
from models import LotStatus


class BidRequest(BaseModel):
    lot_id: int = Field(gt=0)
    bidder: str = Field(min_length=1)
    amount: int = Field(gt=0)

    model_config = {
        "json_schema_extra": {
            "example": {
                "lot_id": "1",
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
