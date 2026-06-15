FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Create a non-root user to run the app
RUN useradd -m scraperuser
USER scraperuser

# Set working directory to src so relative imports work correctly
WORKDIR /app/src

# Command to run the orchestrator
CMD ["python", "main.py"]