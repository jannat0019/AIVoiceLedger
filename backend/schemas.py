from datetime import date
from typing import Literal

from pydantic import BaseModel, Field

class LineItem(BaseModel):
    name:str
    quantity: float=1
    price:float | None=None

class ExpenseDraft(BaseModel):
    merchant: str | None=None

    expense_date: date| None=None

    currency:str="PKR"

    total:float =Field(gt=0)

    category: Literal[
        "food",
        "transport",
        "groceries",
        "bills",
        "shopping",
        "health",
        "entertainment",
        "other",
    ] = "other"

    payment_method: Literal[
        "cash",
        "card",
        "online",
        "unknown",
    ] = "unknown"

    items: list[LineItem] = []

    uncertain_fields: list[str] = []

class ConfirmedReceipt(BaseModel):
    source:  Literal["receipt", "voice", "manual"] = "receipt"
