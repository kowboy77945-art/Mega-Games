FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN echo "=== FILES IN /app ===" && ls -la /app/
RUN echo "=== HANDLERS FOLDER ===" && ls -la /app/handlers/ || echo "NO HANDLERS FOLDER!"

CMD ["python", "bot.py"]
