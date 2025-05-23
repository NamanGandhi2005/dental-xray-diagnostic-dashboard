# Stage 1: Build dependencies to keep final image smaller
FROM python:3.10-slim as builder

WORKDIR /install

# Copy only requirements to leverage Docker cache
COPY requirements.txt /install/
# Install dependencies into a temporary location
RUN pip install --no-cache-dir --prefix="/install" -r requirements.txt

# Stage 2: Create the final lightweight image
FROM python:3.10-slim

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# --- ADD THIS SECTION TO INSTALL SYSTEM DEPENDENCIES ---
# Install system dependencies required by OpenCV (cv2), which is a dependency of inference_sdk
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
 && rm -rf /var/lib/apt/lists/*
# libglib2.0-0 is another common one sometimes needed by cv2 or its dependencies.
# --no-install-recommends helps keep the image size down.
# rm -rf /var/lib/apt/lists/* cleans up apt cache.
# --- END ADDED SECTION ---

WORKDIR /app

# Copy installed packages from the builder stage
COPY --from=builder /install /usr/local

# Copy the application code
COPY ./app /app/app
COPY .env.example /app/.env.example

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]