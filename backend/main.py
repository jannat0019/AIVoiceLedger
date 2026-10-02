from fastapi import FastAPI, File, HTTPException, UploadFile

from schemas import ExpenseDraft,CreateExpenseRequest
from vision import extract_expense_from_receipt
from database import supabase
app=FastAPI(title="Voiceledger AI")

@app.get("/health")
def health():
    return{"status":"ok"}

@app.post("/extract/receipt", response_model=ExpenseDraft)
async def extract_receipt(file: UploadFile=File(...)):

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Please upload an image file."
        )

    try:
        image_bytes=await file.read()

        if not image_bytes:
            raise HTTPException(
                status_code=400,
                detail="The uploaded image is empty.",
            )

        raw_result=extract_expense_from_receipt(image_bytes)

        expense=ExpenseDraft(**raw_result)

        return expense
    
    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"receipt extraction failed : {str(e)}",
        )

@app.post("/expenses", response_model=ExpenseDraft)
def create_expense(expense: CreateExpenseRequest):

    """
    Save a confirmed expense to DB
    """

    expense_data={
        "merchant":expense.merchant,
        "expense_date": (expense.expense_date.isoformat()
                          if expense.expense_date else None),
        "currency":expense.currency,
        "total": expense.total,
         "tax":expense.tax,
         "category":expense.category,
         "payment_method": expense.payment_method,
         "items":[
             item.model_dump() for item in expense.items
         ],
         "source": expense.source
    }

    try:
        response=(supabase.table("expenses")
                        .insert(expense_data)
                        .execute()
        )
    except Exception as ex:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save expense due to {str(ex)}"
        )

    if not response.data:
        raise HTTPException(
            status_code=500,
            detail="Supabase did not return the created expense.",
        )

    saved_expense=response.data[0]
    print(saved_expense)

    return{
        "id":saved_expense["id"],
        **expense.model_dump()
    }

@app.get("/expenses")
def get_expenses():

    """
    Return saved expenses
    """
    try:
        response=(
            supabase.table("expenses")
            .select("*")
            .order("created_at", desc=True)
            .execute())
        
    except Exception as ex:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch expenses: {str(ex)}",
        )

    return response.data



    