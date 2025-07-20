# Use official Python + Playwright image
FROM mcr.microsoft.com/playwright/python:v1.53.0

# Set working directory
WORKDIR /app

# Copy all code
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port FastAPI will run on
EXPOSE 10000

# Run your FastAPI app with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]
