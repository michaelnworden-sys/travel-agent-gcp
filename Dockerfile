# 1. Use a lightweight Python version
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy the shopping list and install ingredients
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the rest of the code
COPY . .

# 5. Tell Google to listen on port 8080
ENV PORT=8080

# 6. The Command to Start the Engine
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]