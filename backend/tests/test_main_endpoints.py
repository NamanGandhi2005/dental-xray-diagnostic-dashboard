import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import base64 
import io 
from PIL import Image 

from app.main import app 
from app.models import DiagnosisResponse 

client = TestClient(app)

def create_dummy_dcm_file(filename="test.dcm") -> Path:
    content = b"This is not a real DICOM file but for testing upload."
    test_file_path = Path(filename)
    with open(test_file_path, "wb") as f:
        f.write(content)
    return test_file_path

def create_dummy_png_image_bytes() -> bytes:
    img = Image.new('L', (60, 30), color = 'grey') 
    byte_arr = io.BytesIO()
    img.save(byte_arr, format='PNG')
    return byte_arr.getvalue()


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Dental X-ray Diagnostic Dashboard Backend is running."}

def test_diagnose_image_success(mocker):
    mock_pil_image = Image.new('L', (100,100)) 
    mock_base64_image = base64.b64encode(create_dummy_png_image_bytes()).decode('utf-8')
    mocker.patch(
        "app.main.convert_dicom_to_pil_and_base64",  # <--- CORRECTED TARGET
        return_value=(mock_pil_image, mock_base64_image, None)
    )

    mock_annotations = [
        {"x": 50, "y": 50, "width": 10, "height": 10, "confidence": 0.9, "class": "cavity"}
    ]
    mocker.patch(
        "app.main.detect_objects_roboflow_sdk",  # <--- CORRECTED TARGET
        return_value=(mock_annotations, None) 
    )

    mock_report_text = "Mocked diagnostic report for cavity."
    mocker.patch(
        "app.main.generate_llm_report",  # <--- CORRECTED TARGET
        return_value=mock_report_text
    )

    dummy_file_path = create_dummy_dcm_file("test_success.dcm")
    
    with open(dummy_file_path, "rb") as f:
        files = {"file": (dummy_file_path.name, f, "application/octet-stream")}
        response = client.post("/api/diagnose", files=files)

    assert response.status_code == 200
    data = response.json()
    
    try:
        DiagnosisResponse(**data)
    except Exception as e:
        pytest.fail(f"Response validation failed: {e}\nResponse data: {data}")

    assert data["image_filename"] == "test_success.dcm"
    assert data["converted_image_base64"] == mock_base64_image
    assert len(data["annotations"]) == 1
    assert data["annotations"][0]["class"] == "cavity"
    assert data["annotations"][0]["confidence"] == 0.9
    assert data["diagnostic_report"] == mock_report_text
    assert data["error"] is None

    dummy_file_path.unlink()


def test_diagnose_image_invalid_file_type():
    dummy_txt_path = Path("test.txt")
    with open(dummy_txt_path, "wb") as f:
        f.write(b"this is a text file")
    
    with open(dummy_txt_path, "rb") as f:
        files = {"file": (dummy_txt_path.name, f, "text/plain")}
        response = client.post("/api/diagnose", files=files)
        
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]
    
    dummy_txt_path.unlink()

def test_diagnose_image_dicom_conversion_failure(mocker):
    mocker.patch(
        "app.main.convert_dicom_to_pil_and_base64",  # <--- CORRECTED TARGET
        return_value=(None, None, "Mocked DICOM conversion error")
    )
    
    dummy_file_path = create_dummy_dcm_file("test_conv_fail.dcm")
    with open(dummy_file_path, "rb") as f:
        files = {"file": (dummy_file_path.name, f, "application/octet-stream")}
        response = client.post("/api/diagnose", files=files)
        
    assert response.status_code == 200
    data = response.json()
    assert "Failed to convert DICOM: Mocked DICOM conversion error" in data["error"]
    assert data["converted_image_base64"] == ""
    assert data["diagnostic_report"] == "Could not process DICOM file."
    
    dummy_file_path.unlink()


def test_diagnose_image_roboflow_failure(mocker):
    mock_pil_image = Image.new('L', (100,100))
    mock_base64_image = base64.b64encode(create_dummy_png_image_bytes()).decode('utf-8')
    mocker.patch(
        "app.main.convert_dicom_to_pil_and_base64",   # <--- CORRECTED TARGET
        return_value=(mock_pil_image, mock_base64_image, None)
    )
    mocker.patch(
        "app.main.detect_objects_roboflow_sdk",  # <--- CORRECTED TARGET
        return_value=([], "Mocked Roboflow API error")
    )
    mocker.patch(
        "app.main.generate_llm_report",  # <--- CORRECTED TARGET
        return_value="No pathologies detected by the model, or an error occurred during detection."
    )

    dummy_file_path = create_dummy_dcm_file("test_rf_fail.dcm")
    with open(dummy_file_path, "rb") as f:
        files = {"file": (dummy_file_path.name, f, "application/octet-stream")}
        response = client.post("/api/diagnose", files=files)
        
    assert response.status_code == 200
    data = response.json()
    assert "Roboflow detection failed: Mocked Roboflow API error" in data["error"]
    assert data["converted_image_base64"] == mock_base64_image
    assert len(data["annotations"]) == 0
    assert data["diagnostic_report"] == "No pathologies detected by the model, or an error occurred during detection."

    dummy_file_path.unlink()