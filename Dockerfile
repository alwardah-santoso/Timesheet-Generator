FROM python:3.11-slim

# Install Node.js dan npm
RUN apt-get update && apt-get install -y curl nodejs npm && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Salin dan install dependensi Python & Node.js
COPY requirements.txt package*.json ./
RUN pip install --no-cache-dir -r requirements.txt && npm install

# Salin seluruh kode proyek
COPY . .

# Buat folder sementara untuk upload & output
RUN mkdir -p uploads output

# Expose port default 7860 (Standar Hugging Face Spaces & Cloud Container)
EXPOSE 7860

# Jalankan server FastAPI dengan port dinamis atau fallback ke 7860
CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT:-7860}"]
