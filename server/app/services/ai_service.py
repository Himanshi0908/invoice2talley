import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import PIL.Image
import easyocr
import numpy as np

# Initialize EasyOCR Reader (will download models on first run)
reader = easyocr.Reader(['en'])

load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

PROMPT = """
You are an expert financial document analyzer. Your task is to extract all relevant information from an invoice as structured data.
You will be provided with:
1. RAW OCR TEXT: Text extracted from the document using OCR.
2. INVOICE IMAGE: The actual document image.

Your goal is to extract every significant field present on the invoice.

EXTRACT THE FOLLOWING DATA STRUCTURE:
1. Extract ALL individual fields (e.g., Invoice Number, Date, Vendor Details, Tax IDs, Subtotal, Taxes, Total, etc.) as top-level key-value pairs in a flat JSON object.
2. Use descriptive, lower_case_with_underscores for keys (e.g., "gst_number", "shipping_address", "invoice_date").
3. Always try to include "invoice_number", "date", "vendor_name", and "total_amount" if they exist, as these are primary fields.
4. "items": Extract the table of products or services as a list of objects. Each item should include all available columns (e.g., description, quantity, unit_price, discount, tax, amount).
5. "category": Categorize the overall expense into one of: [Travel, Food, Office Supplies, Utilities, Software, Others].

STRICT RULES:
- Return ONLY a valid JSON object. No markdown, no preamble.
- Numeric values must be numbers (floats/ints), not strings with currency symbols.
- If a field is not present, do not include it in the JSON.
- If "items" are not present, return an empty list: [].

Example Structure:
{
  "invoice_number": "INV-123",
  "date": "2023-10-27",
  "vendor_name": "Acme Corp",
  "total_amount": 1500.0,
  "gst_number": "27AAAAA0000A1Z5",
  "items": [
    {"description": "Laptop Stand", "quantity": 1, "rate": 1500.0, "amount": 1500.0}
  ],
  "category": "Office Supplies"
}
"""

async def extract_invoice_data(image_path: str):
    if not api_key:
        return {"error": "GEMINI_API_KEY NOT SET"}

    try:
        model = genai.GenerativeModel("gemini-flash-latest")
        
        # 1. Perform Raw OCR with EasyOCR
        print(f"DEBUG: Performing OCR on {image_path}")
        results = reader.readtext(image_path, detail=0)
        raw_text = "\n".join(results)
        print(f"DEBUG: Raw OCR Text: {raw_text[:500]}...") # Print first 500 chars

        # 2. Open image for Gemini
        img = PIL.Image.open(image_path)
        
        # 3. Combine OCR text and Image for Gemini
        content = [
            f"{PROMPT}\n\nRAW OCR TEXT:\n{raw_text}",
            img
        ]
        
        response = model.generate_content(content)
        
        if not response or not response.text:
             return {"error": "Empty response from Gemini"}

        text = response.text.strip()
        print(f"DEBUG AI Response: {text}")
        
        # 1. Try to find JSON in markdown blocks
        import re
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # 2. Try to find raw JSON object
        json_match = re.search(r'(\{.*\})', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # 3. Direct parse attempt
        return json.loads(text)
    except Exception as e:
        print(f"Extraction Error: {e}")
        return {"error": str(e)}
