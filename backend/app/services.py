import pydicom
from PIL import Image
import numpy as np
import base64
import io
import google.generativeai as genai
from inference_sdk import InferenceHTTPClient, InferenceConfiguration
from typing import List, Tuple, Optional

from .config import settings
from .models import RoboflowPrediction 
import logging

logger = logging.getLogger(__name__)

def convert_dicom_to_pil_and_base64(dicom_file_bytes: bytes) -> Tuple[Optional[Image.Image], Optional[str], Optional[str]]:
    """
    Converts DICOM file bytes to a PIL Image object and a base64 encoded PNG string.
    Returns: (PIL.Image, base64_png_string, error_message)
    """
    try:
        ds = pydicom.dcmread(io.BytesIO(dicom_file_bytes))
        pixel_array = ds.pixel_array
        
        if pixel_array.ndim > 2: 
            if 'NumberOfFrames' in ds and ds.NumberOfFrames > 1:
                 pixel_array = pixel_array[0] 

        window_center = None
        window_width = None

        if 'WindowCenter' in ds:
            wc_val = ds.WindowCenter
            window_center = float(wc_val[0]) if isinstance(wc_val, pydicom.multival.MultiValue) else float(wc_val)
        
        if 'WindowWidth' in ds:
            ww_val = ds.WindowWidth
            window_width = float(ww_val[0]) if isinstance(ww_val, pydicom.multival.MultiValue) else float(ww_val)

        if window_center is not None and window_width is not None:
            lower_bound = window_center - window_width / 2
            upper_bound = window_center + window_width / 2
            
            if window_width == 0:
                normalized_array = np.clip(pixel_array, lower_bound, upper_bound)
                min_val_clipped = np.min(normalized_array)
                max_val_clipped = np.max(normalized_array)
                if max_val_clipped == min_val_clipped:
                    normalized_array = np.zeros_like(normalized_array, dtype=np.uint8)
                else:
                    normalized_array = ((normalized_array - min_val_clipped) / (max_val_clipped - min_val_clipped)) * 255.0
            else:
                pixel_array_processed = np.clip(pixel_array, lower_bound, upper_bound)
                normalized_array = ((pixel_array_processed - lower_bound) / window_width) * 255.0
        else:
            min_val = np.min(pixel_array)
            max_val = np.max(pixel_array)
            if max_val == min_val: 
                normalized_array = np.zeros_like(pixel_array, dtype=np.uint8)
            else:
                normalized_array = ((pixel_array - min_val) / (max_val - min_val)) * 255.0
        
        if normalized_array.size == 0 or not np.all(np.isfinite(normalized_array)):
             logger.error("Normalized array is empty or contains non-finite values after W/L or min-max.")
             min_val = np.min(pixel_array)
             max_val = np.max(pixel_array)
             if max_val == min_val: normalized_array = np.zeros_like(pixel_array, dtype=np.uint8)
             else: normalized_array = ((pixel_array - min_val) / (max_val - min_val)) * 255.0

        image_array_8bit = normalized_array.astype(np.uint8)
        pil_image = Image.fromarray(image_array_8bit)
        
        if 'PhotometricInterpretation' in ds and ds.PhotometricInterpretation == "MONOCHROME1":
            pil_image = Image.eval(pil_image, lambda x: 255 - x)
        
        if pil_image.mode != 'L': 
            pil_image = pil_image.convert('L')

        buffered = io.BytesIO()
        pil_image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        return pil_image, img_base64, None
    except Exception as e:
        logger.error(f"DICOM Conversion Error: {str(e)}", exc_info=True)
        return None, None, f"DICOM Conversion Error: {str(e)}"


def detect_objects_roboflow_sdk(pil_image: Image.Image) -> Tuple[List[RoboflowPrediction], Optional[str]]:
    """Sends PIL image to Roboflow using inference-sdk and parses predictions."""
    if not settings.ROBOFLOW_API_KEY or settings.ROBOFLOW_API_KEY == "YOUR_ROBOFLOW_API_KEY_PLACEHOLDER":
        logger.warning("Roboflow API key not configured. Skipping detection.")
        return [], "Roboflow API Key not configured."
    if not settings.ROBOFLOW_MODEL_ID or settings.ROBOFLOW_MODEL_ID == "your_model_project/version":
        logger.warning("Roboflow Model ID not configured. Skipping detection.")
        return [], "Roboflow Model ID not configured."

    try:
        client = InferenceHTTPClient(
            api_url="https://detect.roboflow.com", 
            api_key=settings.ROBOFLOW_API_KEY
        )

        custom_configuration = InferenceConfiguration(
            confidence_threshold=0.30, 
            iou_threshold=0.50         
        )
        client.configure(custom_configuration)
        
        result = client.infer(
            inference_input=pil_image, 
            model_id=settings.ROBOFLOW_MODEL_ID
        )
        
        logger.info(f"Raw result from Roboflow client.infer(): Type: {type(result)}, Content: {str(result)[:500]}")

        predictions_data = []
        if isinstance(result, dict) and "predictions" in result:
            predictions_data = result["predictions"]
            logger.info(f"Extracted predictions_data (from dict): {str(predictions_data)[:500]}")
        elif isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict) and "predictions" in result[0]:
            predictions_data = result[0]["predictions"]
            logger.info(f"Extracted predictions_data (from list of dicts with 'predictions' key): {str(predictions_data)[:500]}")
        elif isinstance(result, list) and len(result) > 0 and "x" in result[0] and "class" in result[0]: 
            predictions_data = result
            logger.info(f"Using result directly as predictions_data (list of prediction dicts): {str(predictions_data)[:500]}")
        else:
            logger.error(f"Roboflow response format not recognized or 'predictions' key missing. Type: {type(result)}, Content: {str(result)[:500]}")
            return [], "Roboflow response format not recognized."
        
        parsed_predictions = []
        if not predictions_data or not isinstance(predictions_data, list):
            logger.warning(f"predictions_data is empty or not a list after extraction: {predictions_data}")
        else:
            for i, pred_dict in enumerate(predictions_data):
                logger.info(f"Raw prediction dict #{i} before Pydantic: {pred_dict}")
                if not isinstance(pred_dict, dict):
                    logger.warning(f"Item #{i} in predictions_data is not a dict: {pred_dict}")
                    continue 
                try:
                    pydantic_pred = RoboflowPrediction(**pred_dict)
                    parsed_predictions.append(pydantic_pred)
                    logger.info(f"Successfully parsed prediction #{i} into Pydantic model: {pydantic_pred.model_dump_json()}")
                except Exception as e_parse:
                    logger.error(f"Error parsing prediction dict #{i} ({pred_dict}) with Pydantic: {e_parse}", exc_info=True)
        
        if not parsed_predictions and predictions_data:
             logger.warning("predictions_data was present but parsed_predictions is empty. Check Pydantic parsing logs.")
        
        return parsed_predictions, None
        
    except Exception as e:
        logger.error(f"Roboflow SDK General Error: {str(e)}", exc_info=True)
        return [], f"Roboflow SDK GeneralError: {str(e)}"


def generate_llm_report(annotations: List[RoboflowPrediction]) -> str:
    """Generates a diagnostic report using Gemini or simulates it."""
    if not annotations:
        return "No pathologies detected by the model, or an error occurred during detection. Clinical correlation is advised."

    annotation_summary = []
    for ann in annotations:
        class_name_to_report = ann.class_name if ann.class_name else "unidentified finding"
        annotation_summary.append(
            f"- Detected Pathology: {class_name_to_report} (Confidence: {ann.confidence:.2f})"
        )
    prompt_data = "\n".join(annotation_summary)


    llm_prompt_instructions = """You are a dental radiologist. Based on the image annotations provided below, write a concise diagnostic report in clinical language.
The report should be a brief paragraph.
Please highlight the following:
1. Detected pathologies.
2. Location: You may state that specific tooth location cannot be determined from the provided annotations alone.
3. Clinical advice (optional, general advice related to findings is acceptable)."""

    full_prompt = f"""{llm_prompt_instructions}

Image Annotations:
{prompt_data}

Concise Diagnostic Report (brief paragraph):
"""

    if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_OR_LEAVE_BLANK_TO_SIMULATE":
        logger.info("Attempting to generate report with Gemini API using concise prompt...")
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash-latest') 
            
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
            generation_config = genai.types.GenerationConfig(
                temperature=0.5,  
            )

            response = model.generate_content(
                full_prompt,
                generation_config=generation_config,
                safety_settings=safety_settings
                )
            
            report_text = ""
            if hasattr(response, 'text') and response.text:
                 report_text = response.text
            elif hasattr(response, 'parts') and response.parts:
                 report_text = "".join(part.text for part in response.parts if hasattr(part, 'text'))
            elif hasattr(response, 'candidates') and response.candidates and \
                 hasattr(response.candidates[0], 'content') and \
                 hasattr(response.candidates[0].content, 'parts') and \
                 response.candidates[0].content.parts:
                 report_text = "".join(part.text for part in response.candidates[0].content.parts if hasattr(part, 'text'))
            
            if report_text:
                logger.info("Successfully generated concise report using Gemini API.")
                return report_text.strip() 
            else:
                logger.warning(f"Gemini response for concise prompt was empty or structure not as expected. Full response: {response}")
                logger.info("Falling back to concise simulated report after Gemini issue.")


        except Exception as e:
            logger.error(f"Error generating concise report with Gemini: {str(e)}", exc_info=True)
            logger.info("Falling back to concise simulated report after Gemini error.")
           
    else: 
        logger.info("Gemini API key not configured or is placeholder. Using concise simulated report.")
    
    
    pathologies_summary = ", ".join(
        f"{ann.class_name if ann.class_name else 'unidentified finding'} (Confidence: {ann.confidence:.0%})" for ann in annotations
    ) if annotations else "No specific pathologies were clearly identified by the automated system."

    simulated_report = f"""--- SIMULATED DIAGNOSTIC REPORT ---
Automated analysis of the radiographic image suggests the presence of {pathologies_summary}. Specific tooth location cannot be determined from these annotations alone. Clinical correlation is strongly recommended to confirm these automated findings and determine appropriate patient management. This automated report serves as an initial guide and is not a substitute for a comprehensive evaluation by a dental professional.
"""
    
    return simulated_report.strip()