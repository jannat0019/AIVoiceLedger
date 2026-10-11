from fastapi import FastAPI, File, HTTPException, UploadFile

from schemas import ExpenseDraft,CreateExpenseRequest, ExpenseUpdateRequest,ExpenseResponse
from vision import extract_expense_from_receipt
from database import supabase,create_client

from fastapi import Depends

from auth import AuthenticatedUser, get_current_user
app=FastAPI(title="Voiceledger AI")

@app.get("/auth/me")
def get_me(
    current_user:AuthenticatedUser=Depends(get_current_user),
):
    return{
        "user_Id":current_user.user_id
    }



@app.get("/health")
def health():
    return{"status":"ok"}

@app.post("/extract/receipt", response_model=ExpenseDraft)
async def extract_receipt(file: UploadFile=File(...),current_user: AuthenticatedUser = Depends(get_current_user)):

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
def create_expense(expense: CreateExpenseRequest,
    current_user: AuthenticatedUser = Depends(get_current_user)):

    """
    Save a confirmed expense to DB
    """

    expense_data={
        "user_id":current_user.user_id,
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
        response=(current_user.db.table("expenses")
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
def get_expenses(current_user: AuthenticatedUser = Depends(get_current_user)):

    """
    Return saved expenses
    """
    try:
        response=(
            current_user.db.table("expenses")
            .select("*")
            .order("created_at", desc=True)
            .execute())
        
    except Exception as ex:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch expenses: {str(ex)}",
        )

    return response.data

@app.patch("/expenses/{expense_id}", response_model=ExpenseResponse):
def update_expense(
        expense_id:UUID,
        updates:ExpenseUpdateRequest,
        user:dict=Depends(get_current_user),
):
    update_data=updates.model_dump(
        exclude_unset=True,
        mode="json"
    )

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="Provide at least one field to update.",
        )

    user_supabase = create_client(user["access_token"])

    try:
        response=(
            user_supabase.table("expenses")
             .update(update_data)
            .eq("id", str(expense_id))
            .eq("user_id", user["id"])
            .select("*")
            .execute()
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to update expense.",
        )
    if not response.data:
        raise HTTPException(
            status_code=404,
            detail="Expense not found or you do not have access to it.",
        )

    updated_expense = response.data[0]

    return {
        **updated_expense,
        "uncertain_fields": [],
    }
    



    