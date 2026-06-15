FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

# Set working directory
WORKDIR /app

# Install dependencies
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (chromium only is sufficient here and saves space, but standard installs all)
RUN playwright install chromium

# Copy source code
COPY src/ ./src/

# We cannot easily drop to a non-root user when running Playwright without complex permission setups
# for the browser binaries and volume mounts, so we run as root inside the container.

# Set working directory to src so relative imports work correctly
WORKDIR /app/src

# Command to run the orchestrator
CMD ["python", "main.py"]