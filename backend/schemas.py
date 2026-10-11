from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, model_validator

Category=Literal[
        "food",
        "transport",
        "groceries",
        "bills",
        "shopping",
        "health",
        "entertainment",
        "other",
    ] = "other"
Payment_Method= Literal[
        "cash",
        "card",
        "online",
        "unknown",
    ] = "unknown"

class LineItem(BaseModel):
    name:str
    quantity: float=1
    price:float | None=None

class ExpenseDraft(BaseModel):
    merchant: str | None=None

    expense_date: date| None=None

    currency:str="PKR"

    total:float =Field(gt=0)
    
    tax :float=0

    category: Category="other"

    payment_method: Payment_Method="unknown"

    items: list[LineItem] = []

    uncertain_fields: list[str] = []

class CreateExpenseRequest(ExpenseDraft):
    source: Literal["voice", "receipt", "manual"]


class ExpenseResponse(CreateExpenseRequest):
    id: str


class ExpenseUpdateRequest(BaseModel):
    merchant: str | None = None
    expense_date: date | None = None
    currency: str | None = None
    total: float | None = Field(default=None, gt=0)
    tax: float | None = None
    category: Category | None = None
    payment_method: Payment_Method | None = None
    items: list[LineItem] | None = None

    @model_validator(mode="after")
    def check_non_nullable_fields(self):
        for field_name in (
             "currency",
            "total",
            "category",
            "payment_method",
            "items",
        ):
            if (field_name in self.model_fields_set
            and getattr(self,field_name) is None):
                raise ValueError(f"{field_name} cannot be null.")
        
        return self

    class ExpenseResponse(ExpenseDraft):
        id: str
        user_id: str
        source: Literal["voice", "receipt", "manual"]
                

