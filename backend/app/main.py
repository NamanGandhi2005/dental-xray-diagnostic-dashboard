from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging

from .services import (
    convert_dicom_to_pil_and_base64,
    detect_objects_roboflow_sdk,
    generate_llm_report
)
from .models import DiagnosisResponse 
from .config import settings 
app = FastAPI(title="Dental X-ray Diagnostic Dashboard API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
        
    ]
)
logger = logging.getLogger(__name__)


@app.post("/api/diagnose", response_model=DiagnosisResponse)
async def diagnose_image(file: UploadFile = File(...)):
    logger.info(f"Received file: {file.filename} of type {file.content_type}")

    if not file.filename:
        logger.warning("File upload attempt with no filename.")
        raise HTTPException(status_code=400, detail="No file name provided.")
        
    if not (file.filename.lower().endswith(".dcm") or file.filename.lower().endswith(".rvg")):
        logger.warning(f"Invalid file type received: {file.filename}")
        raise HTTPException(status_code=400, detail="Invalid file type. Only .dcm or .rvg files are accepted.")

    contents = await file.read()
    if not contents:
        logger.warning(f"Empty file received: {file.filename}")
        raise HTTPException(status_code=400, detail="Empty file received.")
    
    
    pil_image, converted_image_base64, error_dicom = convert_dicom_to_pil_and_base64(contents)
    
    if error_dicom or not pil_image or not converted_image_base64:
        logger.error(f"DICOM conversion error for {file.filename}: {error_dicom}")
        return DiagnosisResponse(
            image_filename=file.filename,
            converted_image_base64="", 
            annotations=[],
            diagnostic_report="Could not process DICOM file.",
            error=f"Failed to convert DICOM: {error_dicom}"
        )
    logger.info(f"DICOM file {file.filename} converted to PNG successfully.")

    
    annotations_data, error_roboflow = detect_objects_roboflow_sdk(pil_image)
    
    current_report = "" 

    if error_roboflow:
        logger.error(f"Roboflow detection error for {file.filename}: {error_roboflow}")
       
        current_report = generate_llm_report([])
        
        
        return DiagnosisResponse(
            image_filename=file.filename,
            converted_image_base64=converted_image_base64,
            annotations=[], 
            diagnostic_report=current_report,
            error=f"Roboflow detection failed: {error_roboflow}. Report generated based on no detections."
        )
    logger.info(f"Roboflow detection for {file.filename} successful. Found {len(annotations_data)} annotations.")
    
   
    diagnostic_report = generate_llm_report(annotations_data)
    logger.info(f"Diagnostic report generated for {file.filename}.")

    return DiagnosisResponse(
        image_filename=file.filename,
        converted_image_base64=converted_image_base64,
        annotations=annotations_data,
        diagnostic_report=diagnostic_report
    )

@app.get("/")
def read_root():
    return {"message": "Dental X-ray Diagnostic Dashboard Backend is running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)