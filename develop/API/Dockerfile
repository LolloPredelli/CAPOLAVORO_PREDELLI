FROM python:3.10-slim

# Imposta la directory di lavoro
WORKDIR /app

# Copia i file nel container
COPY requirements.txt .
COPY app.py .
# Se usi un modello spaCy locale, copialo anche:
# COPY ./en_core_web_lg ./en_core_web_lg

# Installa le dipendenze
RUN pip install --upgrade pip \
 && pip install -r requirements.txt

# Scarica il modello spaCy (opzionale)
RUN python -m spacy download en_core_web_lg

# Espone la porta usata da Gradio o FastAPI
EXPOSE 7860

# Avvia l'app (modifica se usi gradio o fastapi)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
