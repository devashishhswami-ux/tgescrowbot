# Main Bot Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all whitelisted files from build context
COPY . .

# Create sessions directory
RUN mkdir -p /app/sessions

# Health check endpoint
EXPOSE 8080

# Run bot
CMD ["python", "bot.py"]
