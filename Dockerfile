# Use an official lightweight Python image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set workspace directory
WORKDIR /app

# Copy requirements file first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the HuggingFace sentence-transformer model so that the container runs instantly
# and can work without needing to download models during runtime
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy the rest of the application files
COPY . .

# Expose port for FastAPI backend (just in case they want to hit the API directly from outside,
# although main.py calls it on localhost internally within the container)
EXPOSE 8000

# Run main.py as the default entry point
CMD ["python", "main.py"]
