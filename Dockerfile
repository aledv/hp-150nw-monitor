# Usa un'immagine Python leggera
FROM python:3.11-slim

# Installa curl
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Imposta la directory di lavoro
WORKDIR /app

# Copia i file
COPY main.py requirements.txt ./

# Installa le dipendenze
RUN pip install --no-cache-dir -r requirements.txt

# Espone la porta 5001
EXPOSE 5001

# Avvia l'app FastAPI sulla porta 5001
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5001"]
