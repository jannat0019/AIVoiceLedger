from fastapi import FastAPI, File, HTTPException, UploadFile

from schemas import ExpenseDraft
from vision import extract_expense_from_receipt

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
