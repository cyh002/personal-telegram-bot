FROM python:3.12-slim

WORKDIR /app

# Copy requirements files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN pip install --no-cache-dir uv && \
    uv pip install --system -e .

# Copy the application
COPY main.py ./
COPY src ./src/

# Create prompts directory
RUN mkdir -p ./prompts

# We'll mount the prompts directory as a volume instead of copying
# This allows updating prompts without rebuilding the image

# Create  .env file to prevent errors if not mounted
RUN touch .env

# Run the bot
CMD ["python", "main.py"]