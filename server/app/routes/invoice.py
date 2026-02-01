from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os
import uuid
from typing import List
from app.services import ai_service
from app.utils import tally_xml, db
import datetime

router = APIRouter()

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.post("/upload")
async def upload_invoice(file: UploadFile = File(...)):
    # Validate file type
    if not file.content_type.startswith("image/") and file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type. Only images and PDFs are allowed.")
    
    # Save file
    file_id = str(uuid.uuid4())
    file_ext = os.path.splitext(file.filename)[1]
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}{file_ext}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Trigger AI Extraction
    extraction_result = await ai_service.extract_invoice_data(file_path)
    
    final_data = {}
    if "error" in extraction_result:
        # Fallback to dummy data if API key is missing or error occurs (for demo)
        final_data = {
            "invoice_number": "PENDING",
            "date": datetime.datetime.now().strftime("%Y-%m-%d"),
            "vendor_name": "Unknown Vendor",
            "gstin": "",
            "subtotal": 0.0,
            "tax_amount": 0.0,
            "total_amount": 0.0,
            "items": [],
            "category": "Others"
        }
        response = {
            "id": file_id,
            "filename": file.filename,
            "status": "warning",
            "message": extraction_result["error"],
            "extracted_data": final_data
        }
    else:
        final_data = extraction_result
        response = {
            "id": file_id,
            "filename": file.filename,
            "status": "success",
            "extracted_data": final_data
        }
    
    # Save to history
    db.save_invoice(file_id, file.filename, final_data)
    
    return response

@router.get("/invoices")
async def get_invoices():
    return db.get_all_invoices()

@router.post("/export/tally")
async def export_to_tally(invoice_data: dict):
    xml_content = tally_xml.generate_tally_xml(invoice_data)
    return {"message": "Tally XML generated", "xml": xml_content}
