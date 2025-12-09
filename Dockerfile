FROM python:3.11-slim

WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all your SoundHopper files (agent.py, tools.py, etc)
COPY . .

# Expose the port
EXPOSE 8080
ENV PORT=8080

# Run the server
CMD ["python", "server.py"]