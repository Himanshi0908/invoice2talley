from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import os
from app.routes import invoice

app = FastAPI(title="Invoice to Tally API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(invoice.router, prefix="/api", tags=["Invoices"])

# Serve Static Files
# Assuming the 'client' directory is at the same level as 'server' or 'main.py'
# Based on project structure: c:/Users/Himanshi/Desktop/invoice_to_talley/client
client_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "client")
app.mount("/static", StaticFiles(directory=client_path), name="static")

@app.get("/")
async def root():
    return FileResponse(os.path.join(client_path, "index.html"))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
