FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=7860

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libmagic-dev \
    poppler-utils \
    tesseract-ocr \
    libreoffice \
    pandoc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend code
COPY . .

# Create data directory and set permissions
RUN mkdir -p /app/data && chmod 777 /app/data

# Hugging Face Spaces run on port 7860
EXPOSE 7860

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
