from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional

class RoboflowPrediction(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    x: float
    y: float
    width: float
    height: float
    confidence: float
    class_name: str = Field(alias="class")

class DiagnosisResponse(BaseModel):
    
    image_filename: str
    converted_image_base64: str
    annotations: List[RoboflowPrediction]
    diagnostic_report: str
    error: Optional[str] = None