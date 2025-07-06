FROM python:3.11-slim

# Встановлюємо робочу директорію
WORKDIR /app

# Копіюємо requirements.txt
COPY requirements.txt .

# Встановлюємо залежності
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо код бота
COPY . .

# Створюємо користувача без root прав
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# Експортуємо порт
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Запускаємо бота
CMD ["python", "bot.py"]
