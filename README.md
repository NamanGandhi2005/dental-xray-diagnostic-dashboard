# 🦷 Dental X-ray Diagnostic Dashboard

## 🎯 Objective


The Dental X-ray Diagnostic Dashboard is a full-stack web application designed to assist dental professionals in analyzing dental X-ray images. Users can upload DICOM (.dcm or .rvg) X-ray images, which are then processed to detect potential pathologies like cavities and periapical lesions using a Roboflow object detection model. The detected pathologies are visualized with bounding boxes on the image, and an AI-generated diagnostic report (using a Large Language Model like Google Gemini or OpenAI GPT) is provided based on these findings.

**Disclaimer:** This application is for demonstration and research purposes only and should not be used for actual clinical diagnosis or decision-making without verification by a qualified dental professional.

---

## ✨ Features

*   **DICOM Upload & Conversion:** Accepts dental X-ray images in DICOM format (.dcm, .rvg).
*   **Image Display:** Converts and displays the uploaded X-ray image.
*   **AI-Powered Pathology Detection:** Sends the image to a Roboflow object detection model (e.g., `adr/6`) to identify common dental pathologies.
*   **Bounding Box Visualization:** Overlays bounding boxes on the image to highlight detected pathologies, along with their class name and confidence score.
*   **Automated Diagnostic Report:** Utilizes Google Gemini (or simulates an LLM response) to generate a concise clinical diagnostic report based on the detected annotations.
*   **User-Friendly Interface:** A two-panel dashboard view for image interaction and report review.
*   **Multi-File Processing:** Supports uploading multiple DICOM files for sequential processing and review.

---

## 🖼️ Screenshots

*(Add your screenshots to an `assets/screenshots/` directory in your repository and update the paths below)*

**1. Main Dashboard View (After Upload and Analysis):**
   ![image](https://github.com/user-attachments/assets/7e2d343b-ce35-432a-b333-3a42e4bd630c)


**2. File Upload and Processing Queue:**
   ![image](https://github.com/user-attachments/assets/9504263e-9020-46f1-ad61-dfb473ecb1ba)


**3. Example of Annotated Image:**
   ![image](https://github.com/user-attachments/assets/938f9112-72b6-4f1f-b488-de02b8922f96)


**4. Example of Generated Diagnostic Report:**
   ![image](https://github.com/user-attachments/assets/5358980e-fd84-4964-8d5a-86b9eff02230)


---

## 🧱 Tech Stack

*   **Frontend:** ReactJS (with Vite), Tailwind CSS
*   **Backend:** FastAPI (Python)
*   **Object Detection:** Roboflow API (`inference_sdk`)
*   **Large Language Model (LLM):** Google Gemini API (simulation fallback)
*   **Image Handling:** `pydicom`, `Pillow`
*   **Containerization:** Docker & Docker Compose
*   **Testing:** Pytest, pytest-mock

---

## ⚙️ Setup and Installation

### Prerequisites

*   [Git](https://git-scm.com/downloads)
*   [Node.js](https://nodejs.org/) (v18+ recommended)
*   [Python](https://www.python.org/downloads/) (v3.10+ recommended)
*   [Docker Desktop](https://www.docker.com/products/docker-desktop/)
*   A **Roboflow API Key**.
*   A **Google Gemini API Key** (optional, for full LLM reports).

### 1. Clone the Repository


git clone https://github.com/NamanGandhi2005/dental-xray-diagnostic-dashboard.git
cd dental-xray-diagnostic-dashboard

## 2. Environment Configuration
1.Backend (backend/.env):
2.Navigate to the backend directory. Copy .env.example to .env:
3.cd backend
4.cp .env.example .env

Edit backend/.env and fill in your details:
ROBOFLOW_API_KEY="YOUR_ACTUAL_ROBOFLOW_API_KEY"
ROBOFLOW_MODEL_ID="adr/6" # Or your specific Roboflow model ID (project_name/version)

GEMINI_API_KEY="YOUR_GEMINI_API_KEY_OR_LEAVE_BLANK_TO_SIMULATE"

## Frontend (Environment variables are typically set for Docker builds):
1.Navigate to the frontend directory.
2.frontend/.env.development should exist for local development:
3.VITE_API_BASE_URL=http://localhost:8000/api

frontend/.env.production is used for Docker builds:
VITE_API_BASE_URL=/api/

## 3. Running the Application
1.Using Docker (Recommended):
2.Ensure Docker Desktop is running.
3.From the project root directory (dental-xray-diagnostic-dashboard/):
4.docker-compose up --build

## Access the application:
Frontend: http://localhost:5173
Backend API Docs: http://localhost:8000/docs
To stop: Ctrl+C in the terminal, then docker-compose down.

## Running Locally:
1.Backend (FastAPI):
2.cd backend
3.Create/activate Python venv: python -m venv venv then source venv/Scripts/activate (or equivalent for your OS).
4.Install dependencies: pip install -r requirements.txt
5.Ensure backend/.env is configured.
6.Start server: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

## Frontend (React):
1.Open a new terminal.
2.cd frontend
3.Install dependencies: npm install
4.Ensure frontend/.env.development is configured.
5.Start server: npm run dev (Usually at http://localhost:5173)

## 4. Using the Application
1.Open the application in your browser.
2. Click "Choose DICOM/RVG File(s)" to select images.
3. Files will be processed automatically.
4.View results and diagnostic reports. Click on filenames in the "Processing History" to switch views if multiple files were uploaded.


## 🛠️ Project Structure
dental-xray-diagnostic-dashboard/
├── backend/
│   ├── app/                # FastAPI application code
│   ├── tests/              # Backend unit tests
│   ├── .env                # Local secrets (Git ignored)
│   ├── .env.example
│   ├── .gitignore
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/                # React application code
│   ├── .env.development
│   ├── .env.production
│   ├── .gitignore
│   ├── Dockerfile
│   ├── nginx.conf          # Nginx config for Docker
│   ├── package.json
│   ├── postcss.config.js
│   └── tailwind.config.js
├── assets/
│   └── screenshots/        # For README screenshots
│       └── (your_screenshots.png)
├── sample_data/            # (Optional) For sample DICOMs
├── .gitignore              # Root .gitignore
├── docker-compose.yml
└── README.md

## 🧪 Running Tests (Backend)
1.cd backend
2.Activate virtual environment.
3.Install test dependencies (if not already via requirements.txt):
4.pip install pytest pytest-mock requests
