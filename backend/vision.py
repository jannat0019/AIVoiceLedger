import base64
import json
import os
from pathlib import Path
from dotenv import load_dotenv

from groq import Groq

load_dotenv()

GROQ_API_KEY=os.getenv("GROQ_API_KEY")
VISION_MODEL=os.getenv("VISION_MODEL")

if not GROQ_API_KEY:
    raise RuntimeError("Groq api key is missing")

if not VISION_MODEL:
    raise RuntimeError("Vision model is missing")

client=Groq(api_key=GROQ_API_KEY)

def encode_image(image_bytes:bytes)->str:
    """
    convert image into bytes
    """

    return base64.b64encode(image_bytes).decode("utf-8")

def extract_expense_from_receipt(image_bytes:bytes)->dict:

    """
    send a receipt to the vision model
    and return extracted expense as a python dictionary
    """

    image_base64=encode_image(image_bytes)

    prompt="""
    You are an expense receipt extraction system.

    Analyze the receipt image and extract the following fields:

    - merchant
    - expense_date
    - currency
    - total
    - tax
    - category
    - payment_method
    - items

    Allowed categories:
    food, transport, groceries, bills, shopping,
    health, entertainment, other

    Allowed payment methods:
    cash, card, online, unknown

    Rules:
    1. Return JSON only.
    2. Do not add explanations or markdown.
    3. Do not invent information that is not visible.
    4. If a field cannot be determined, use null where allowed.
    5. total must represent the final amount paid.
    6. category must be one of the allowed categories.
    7. payment_method must be one of the allowed values.
    8. Each item should contain name, quantity, and price.
    9. If you are uncertain about a field, include its field name
    in uncertain_fields.

    Return this exact structure:

    {
    "merchant": null,
    "expense_date": null,
    "currency": "PKR",
    "total": 0,
    "tax":null
    "category": "other",
    "payment_method": "unknown",
    "items": [],
    "uncertain_fields": []
    }
    """

    response=client.chat.completions.create(
        model=VISION_MODEL,
        messages=[
            {
            "role":"user",
            "content":[
                {"type":"text",
                "text":prompt},

                {
                    "type":"image_url",
                    "image_url":{
                        "url":f"data:image/jpeg;base64,{image_base64}"
                    },
                },
            ],
        }
        ],
        temperature=0
    )

    content=response.choices[0].message.content

    if not content:
        raise ValueError("Vision model returned an empty response")


    return json.loads(content)
